#!/usr/bin/env python3
"""Resolves the review scope and inventories its surface in one call.

Applies the skill's fallback chain when no scope is given (staged; unstaged and
untracked; commits ahead of the upstream; the branch against its merge base
with the default branch), writes the retained diff to a file, and prints one
JSON object with the winning rung, commit identities, every changed file with
its status and flags, the files excluded by the chosen rung, guidance files
present at the base revision along the changed paths, and the diff stat.
Interpreting guidance files and reading the diff stay with the agent.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

LOCKFILES = {
    "package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml", "bun.lockb", "bun.lock",
    "Cargo.lock", "poetry.lock", "uv.lock", "Pipfile.lock", "Gemfile.lock", "composer.lock", "go.sum",
    "flake.lock", "packages.lock.json", "mix.lock", "pubspec.lock", "Podfile.lock", "gradle.lockfile",
}
CONFIG_SUFFIXES = {".yml", ".yaml", ".toml", ".ini", ".cfg", ".conf", ".env", ".properties"}
GUIDANCE_ANYWHERE = ("AGENTS.md", "AGENTS.override.md", "CLAUDE.md", "REVIEW.md", "CODING_STANDARDS.md", "CONTRIBUTING.md", ".cursor/BUGBOT.md")
GUIDANCE_ROOT = (".github/copilot-instructions.md",)
LARGE_CHANGE_LINES = 500
ISSUE_REF = re.compile(r"(?:\b[\w.-]+/[\w.-]+)?#\d+\b")


class ScopeError(Exception):
    """A bad ref, an unusable repository, or a scope the agent must pick by hand."""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Resolve a review scope and inventory its surface.",
        epilog="Exits 0 when the scope has changes, 1 when it is empty (the JSON still prints), "
               "2 for a bad ref, multiple merge bases, an unusable repository, or an unwritable output directory.",
    )
    parser.add_argument("--scope", help="staged | worktree | upstream | branch | <base>...<head> | <base>..<head> | <commit>; "
                                        "default: the first non-empty rung of staged, worktree, upstream, branch")
    parser.add_argument("--repo", default=".", help="A directory inside the repository; default: the current directory")
    parser.add_argument("--default-branch", help="Override the default branch, such as origin/main")
    parser.add_argument("--out", help="Directory for diff.patch and scope.json, overwritten if present; "
                                      "default: a new directory under ~/.tmp/code-review")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        repo = Repo(args.repo)
        result = resolve(repo, args.scope, args.default_branch)
        if args.out:
            out = Path(args.out)
            out.mkdir(parents=True, exist_ok=True)
        else:
            base = Path.home() / ".tmp" / "code-review"
            base.mkdir(parents=True, exist_ok=True)
            out = Path(tempfile.mkdtemp(prefix="scope-", dir=base))
        diff_file = out / "diff.patch"
        diff_file.write_bytes(result.pop("patch"))
        result["diff"] = str(diff_file)
        result["repository"] = repo.root
        (out / "scope.json").write_text(json.dumps(result, indent=2) + "\n")
    except ScopeError as error:
        print(json.dumps({"error": str(error)}))
        return 2
    except OSError as error:
        print(json.dumps({"error": f"cannot write the output: {error}"}))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["files"] else 1


class Repo:
    def __init__(self, directory):
        try:
            self.root = self.git("-C", directory, "rev-parse", "--show-toplevel")
        except ScopeError as error:
            raise ScopeError(f"{directory} is not inside a usable Git repository: {error}")

    def run(self, *args, check=True):
        completed = subprocess.run(["git", *args], cwd=getattr(self, "root", None), capture_output=True,
                                   env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
        if check and completed.returncode != 0:
            raise ScopeError(completed.stderr.decode("utf-8", "replace").strip() or f"git {' '.join(args)} failed")
        return completed

    def git(self, *args):
        return self.run(*args).stdout.decode("utf-8", "replace").rstrip("\n")

    def rev(self, ref):
        try:
            return self.git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
        except ScopeError:
            raise ScopeError(f"ref {ref!r} does not resolve to a commit")

    def has_ref(self, ref):
        return self.run("rev-parse", "--verify", "--quiet", ref, check=False).returncode == 0

    def head(self):
        """The HEAD commit, or None before the first commit."""
        return self.rev("HEAD") if self.has_ref("HEAD") else None

    def name_status(self, *diff_args):
        fields = self.git("diff", "--name-status", "-z", "-M", *diff_args).split("\0")
        files = []
        index = 0
        while index < len(fields) and fields[index]:
            status = fields[index][0]
            if status in "RC":
                files.append({"path": fields[index + 2], "status": status, "old_path": fields[index + 1]})
                index += 3
            else:
                files.append({"path": fields[index + 1], "status": status})
                index += 2
        return files

    def untracked(self):
        return [path for path in self.git("ls-files", "--others", "--exclude-standard", "-z").split("\0") if path]

    def numstat(self, *diff_args):
        """Line counts per path; None for binary. With -z a rename record is `added\\tdeleted\\t` then old and new path fields."""
        fields = self.git("diff", "--numstat", "-z", "-M", *diff_args).split("\0")
        stat = {}
        index = 0
        while index < len(fields) and fields[index]:
            added, deleted, name = fields[index].split("\t", 2)
            if name:
                index += 1
            else:
                name = fields[index + 2]
                index += 3
            stat[name] = None if added == "-" else (int(added), int(deleted))
        return stat

    def attributes(self, paths):
        if not paths:
            return {}
        fields = self.git("check-attr", "-z", "linguist-generated", "binary", "--", *paths).split("\0")
        attrs = {}
        for index in range(0, len(fields) - 2, 3):
            attrs.setdefault(fields[index], {})[fields[index + 1]] = fields[index + 2]
        return attrs


def resolve(repo, scope, default_branch):
    head = repo.head()
    if scope in (None, "staged"):
        result = staged(repo, head)
        if scope or result["files"]:
            return result
    if scope in (None, "worktree"):
        result = worktree(repo, head)
        if scope or result["files"]:
            return result
    if scope in (None, "upstream"):
        result = upstream(repo, head)
        if scope or result["files"]:
            return result
    if scope in (None, "branch"):
        return branch(repo, head, default_branch)
    return explicit(repo, scope)


def staged(repo, head):
    files = repo.name_status("--cached")
    unstaged = {item["path"] for item in repo.name_status()}
    excluded = [{"path": item["path"], "reason": "also has unstaged edits"} for item in files if item["path"] in unstaged]
    excluded += [{"path": path, "reason": "unstaged edit"} for path in sorted(unstaged - {item["path"] for item in files})]
    excluded += [{"path": path, "reason": "untracked"} for path in repo.untracked()]
    return inventory(repo, "staged", "staged changes", head, "index", files, excluded, ("--cached",), [])


def worktree(repo, head):
    files = repo.name_status()
    untracked = repo.untracked()
    files += [{"path": path, "status": "A", "untracked": True} for path in untracked]
    return inventory(repo, "worktree", "unstaged and untracked changes", head, "worktree", files, [], (), untracked)


def upstream(repo, head):
    if head is None:
        return empty("upstream", "commits ahead of the upstream", None, "the repository has no commits")
    if not repo.has_ref("@{upstream}"):
        return empty("upstream", "commits ahead of the upstream", head, "no upstream is configured")
    name = repo.git("rev-parse", "--abbrev-ref", "@{upstream}")
    return commits(repo, "upstream", f"commits ahead of {name} (@{{upstream}}..HEAD)", repo.rev("@{upstream}"), head, name)


def branch(repo, head, override):
    if head is None:
        return empty("branch", "the current branch against the default branch", None, "the repository has no commits")
    name = override or default_branch(repo)
    if not name:
        raise ScopeError("no default branch found; pass --default-branch")
    base = repo.rev(name)
    current = repo.git("branch", "--show-current") or "detached HEAD"
    result = commits(repo, "branch", f"branch {current} against its merge base with {name}", base, head, name)
    result["default_branch"] = name
    return result


def default_branch(repo):
    try:
        return repo.git("symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    except ScopeError:
        pass
    for candidate in ("origin/main", "origin/master", "main", "master"):
        if repo.has_ref(candidate):
            return candidate
    return None


def commits(repo, rung, scope, base, head, base_name):
    merge_bases = repo.git("merge-base", "--all", base, head).split()
    if len(merge_bases) > 1:
        raise ScopeError(f"{base_name} and HEAD have {len(merge_bases)} merge bases; pick the scope by hand")
    if not merge_bases:
        raise ScopeError(f"{base_name} and HEAD share no history")
    merge_base = merge_bases[0]
    result = inventory(repo, rung, scope, merge_base, head, repo.name_status(merge_base, head), [], (merge_base, head), [])
    result["behind_base"] = int(repo.git("rev-list", "--count", f"{head}..{base}"))
    result["commits"] = commit_list(repo, merge_base, head)
    return result


def explicit(repo, spec):
    if "..." in spec:
        left, right = spec.split("...", 1)
        base, head = repo.rev(left), repo.rev(right)
        merge_bases = repo.git("merge-base", "--all", base, head).split()
        if len(merge_bases) != 1:
            raise ScopeError(f"{left} and {right} have {len(merge_bases)} merge bases; use <base>..<head> to compare the commits directly")
        base = merge_bases[0]
    elif ".." in spec:
        left, right = spec.split("..", 1)
        base, head = repo.rev(left), repo.rev(right)
    else:
        head = repo.rev(spec)
        parents = repo.git("rev-list", "--parents", "-n", "1", head).split()[1:]
        if len(parents) > 1:
            raise ScopeError(f"{spec} is a merge commit; give an explicit <base>..<head> range")
        base = parents[0] if parents else repo.git("hash-object", "-t", "tree", os.devnull)
    result = inventory(repo, "explicit", spec, base, head, repo.name_status(base, head), [], (base, head), [])
    result["commits"] = commit_list(repo, base, head) if repo.has_ref(f"{base}^{{commit}}") else []
    return result


def commit_list(repo, base, head):
    commits = []
    for entry in repo.git("log", "--format=%H%x00%s%x00%b%x1e", f"{base}..{head}").split("\x1e"):
        if not entry.strip():
            continue
        sha, subject, body = (entry.strip("\n").split("\0", 2) + ["", ""])[:3]
        commits.append({"sha": sha, "subject": subject, "refs": sorted(set(ISSUE_REF.findall(subject + "\n" + body)))})
    return commits


def empty(rung, scope, head, warning):
    return {"rung": rung, "scope": scope, "base": None, "head": head, "behind_base": None, "default_branch": None,
            "commits": [], "files": [], "excluded": [], "guidance": [],
            "stat": {"files": 0, "insertions": 0, "deletions": 0}, "patch": b"", "warnings": [warning]}


def inventory(repo, rung, scope, base, head, files, excluded, diff_args, untracked):
    tracked_stat = repo.numstat(*diff_args)
    attrs = repo.attributes([item["path"] for item in files])
    insertions = deletions = 0
    for item in files:
        counts = untracked_counts(repo, item["path"]) if item.get("untracked") else tracked_stat.get(item["path"])
        item["flags"] = flags(item, counts, attrs.get(item["path"], {}))
        if counts:
            insertions += counts[0]
            deletions += counts[1]
    # git diff never shows untracked files; add each one as a diff against nothing.
    patch = repo.run("diff", "-M", *diff_args).stdout + b"".join(untracked_patch(repo, path) for path in untracked)
    return {
        "rung": rung,
        "scope": scope,
        "base": base,
        "head": head,
        "behind_base": None,
        "default_branch": None,
        "commits": [],
        "files": files,
        "excluded": excluded,
        "guidance": guidance_files(repo, base, files),
        "stat": {"files": len(files), "insertions": insertions, "deletions": deletions},
        "patch": patch,
        "warnings": [],
    }


def no_index_diff(repo, path, *options):
    """Diff an untracked file against nothing. Exit 1 means differences; anything else with no output is a read failure."""
    completed = repo.run("diff", "--no-index", *options, "--", os.devnull, path, check=False)
    if completed.returncode not in (0, 1) or (completed.returncode == 1 and not completed.stdout):
        raise ScopeError(f"cannot read untracked file {path}: {completed.stderr.decode('utf-8', 'replace').strip()}")
    return completed.stdout


def untracked_counts(repo, path):
    line = no_index_diff(repo, path, "--numstat").decode("utf-8", "replace").split("\n")[0]
    if not line:
        return (0, 0)
    added, deleted = line.split("\t")[:2]
    return None if added == "-" else (int(added), int(deleted))


def untracked_patch(repo, path):
    return no_index_diff(repo, path)


def flags(item, counts, attrs):
    path = Path(item["path"])
    found = []
    if attrs.get("linguist-generated") in ("set", "true") or re.search(r"(^|/)(generated|__generated__|__snapshots__|dist|build)/|\.(min\.(js|css)|pb\.go|g\.dart|generated\.(ts|js|go|py))$", item["path"]):
        found.append("generated")
    if path.name in LOCKFILES:
        found.append("lockfile")
    if re.search(r"(^|/)(migrations?|migrate|alembic)/", item["path"]):
        found.append("migration")
    if path.suffix in CONFIG_SUFFIXES or path.name.startswith(".env") or item["path"].startswith(".github/workflows/"):
        found.append("config")
    if counts is None or attrs.get("binary") in ("set", "true"):
        found.append("binary")
    elif counts[0] + counts[1] > LARGE_CHANGE_LINES:
        found.append("large")
    if item.pop("untracked", False):
        found.append("untracked")
    return found


def guidance_files(repo, base, files):
    """Guidance at the base revision: the change's own edits to guidance and any unreviewed disk state must not decide which rules apply."""
    if base is None:
        return []
    # Lists the whole base tree; fine until a repository's file count makes one ls-tree call slow.
    tree = {path for path in repo.git("ls-tree", "-r", "--name-only", "-z", base).split("\0") if path}
    directories = {Path(".")}
    for item in files:
        for path in (item["path"], item.get("old_path")):
            if path:
                directories.update(Path(path).parents)
    wanted = {(directory / name).as_posix() for directory in directories for name in GUIDANCE_ANYWHERE} | set(GUIDANCE_ROOT)
    rules = {(directory / ".cursor" / "rules").as_posix() for directory in directories}
    return sorted(
        path for path in tree
        if path in wanted
        or Path(path).parent.as_posix() in rules
        or (path.startswith(".github/instructions/") and path.endswith(".instructions.md"))
    )


if __name__ == "__main__":
    sys.exit(main())
