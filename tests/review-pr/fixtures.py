"""Disposable Git repositories, a fake gh CLI and a fake SSH transport for the review-pr scripts."""
import json
import os
import subprocess
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "review-pr" / "scripts"
REPO = "o/r"
PR_URL = f"https://github.com/{REPO}/pull/1"

# Answers `gh pr view`, `gh api` GETs and one POST from a JSON file, and logs
# every call with any stdin it received. A POST answer is
# {"stdout": ..., "stderr": ..., "exit": ...}.
FAKE_GH = """#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
stdin = sys.stdin.read() if "--input" in args else None
with open(os.environ["FAKE_GH_LOG"], "a") as log:
    log.write(json.dumps({"args": args, "stdin": stdin}) + "\\n")
with open(os.environ["FAKE_GH_RESPONSES"]) as source:
    responses = json.load(source)
if args[0] == "api":
    host = os.environ.get("GH_HOST", "github.com")
    if "--hostname" in args:
        index = args.index("--hostname")
        host = args[index + 1]
        del args[index:index + 2]
    if host != "github.com":
        sys.exit(f"fake gh: API routed to {host}, expected github.com")
if args[:2] == ["pr", "view"]:
    print(json.dumps(responses["pr"]))
elif args[:2] == ["api", "user"]:
    print(responses["viewer"] if "--jq" in args else json.dumps({"login": responses["viewer"]}))
elif args[:2] == ["api", "graphql"]:
    with open(os.environ["FAKE_GH_LOG"]) as log:
        page = sum("graphql" in json.loads(line)["args"] for line in log) - 1
    print(json.dumps(responses["graphql"][page]))
elif args[0] == "api" and "--method" not in args:
    endpoint = args[1] if args[1] in responses else args[1].split("?")[0]
    print(json.dumps(responses[endpoint]))
elif args[:3] == ["api", "--method", "POST"]:
    post = responses["post"]
    sys.stdout.write(post.get("stdout", ""))
    sys.stderr.write(post.get("stderr", ""))
    sys.exit(post.get("exit", 0))
else:
    sys.exit(f"fake gh: unexpected call {args}")
"""

# Serves every SSH fetch from the local bare repository.
FAKE_SSH = """#!/bin/sh
exec git upload-pack "$FAKE_REMOTE"
"""


class Sandbox:
    """A temporary directory with isolated Git config and fake gh/ssh on PATH."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(os.path.realpath(self._tmp.name))
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        for name, body in (("gh", FAKE_GH), ("ssh", FAKE_SSH)):
            (bin_dir / name).write_text(body)
            (bin_dir / name).chmod(0o755)
        (self.root / "gitconfig").write_text("")
        self.gh_log = self.root / "gh-calls.jsonl"
        self.gh_responses = self.root / "gh-responses.json"
        self.env = {
            **os.environ,
            "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
            "GIT_CONFIG_GLOBAL": str(self.root / "gitconfig"),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
            "GIT_SSH_COMMAND": str(bin_dir / "ssh"),
            "GIT_SSH_VARIANT": "simple",
            "FAKE_REMOTE": str(self.root / "remote.git"),
            "FAKE_GH_LOG": str(self.gh_log),
            "FAKE_GH_RESPONSES": str(self.gh_responses),
        }

    def close(self):
        self._tmp.cleanup()

    def git(self, cwd, *args):
        return subprocess.run(
            ["git", *args], cwd=cwd, env=self.env, check=True,
            capture_output=True, text=True,
        ).stdout.strip()

    def node(self, script, *args, cwd=None):
        return subprocess.run(
            ["node", str(SCRIPTS / script), *args], cwd=cwd or self.root,
            env=self.env, capture_output=True, text=True,
        )

    def set_gh(self, responses):
        self.gh_responses.write_text(json.dumps(responses))

    def gh_calls(self):
        if not self.gh_log.exists():
            return []
        return [json.loads(line) for line in self.gh_log.read_text().splitlines()]


class PreparedReview(Sandbox):
    """A PR whose base and head live in a bare remote that the checkout reaches as github.com/o/r over SSH, prepared into a review worktree by prepare-worktree.mjs."""

    def __init__(self):
        super().__init__()
        seed = self.root / "seed"
        seed.mkdir()
        self.git(seed, "init", "-q", "-b", "main")
        (seed / ".gitignore").write_text("*.log\n")
        (seed / "a.txt").write_text("one\n")
        self.git(seed, "add", ".")
        self.git(seed, "commit", "-q", "-m", "base")
        base = self.git(seed, "rev-parse", "HEAD")
        (seed / "a.txt").write_text("one\ntwo\n")
        self.git(seed, "commit", "-q", "-am", "pr")
        self.pr_head = self.git(seed, "rev-parse", "HEAD")
        self.remote = self.root / "remote.git"
        self.git(self.root, "init", "-q", "--bare", "-b", "main", str(self.remote))
        self.git(seed, "push", "-q", str(self.remote), f"{base}:refs/heads/main",
                 f"{self.pr_head}:refs/pull/1/head")
        self.checkout = self.root / "checkout"
        self.git(self.root, "clone", "-q", str(self.remote), str(self.checkout))
        self.git(self.checkout, "remote", "set-url", "origin", f"ssh://git@github.com/{REPO}.git")

        pr = {"number": 1, "url": PR_URL, "repo": REPO, "state": "OPEN",
              "headRefOid": self.pr_head, "baseRefName": "main"}
        self.set_gh({"pr": pr})
        read_pr = self.root / "read-pr.json"
        read_pr.write_text(json.dumps({"pr": pr}))
        prepared = self.node("prepare-worktree.mjs", "--in", str(read_pr),
                             "--worktree-root", str(self.root / "worktrees"), cwd=self.checkout)
        if prepared.returncode != 0:
            raise RuntimeError(f"prepare-worktree failed: {prepared.stderr}")
        self.record = prepared.stdout.strip()
        self.worktree = Path(json.loads(Path(self.record).read_text())["worktree"])

    def cleanup(self, *flags):
        result = self.node("cleanup-worktree.mjs", "--in", self.record, *flags, cwd=self.checkout)
        return result.returncode, json.loads(result.stdout)

    def private_refs(self):
        return self.git(self.checkout, "for-each-ref", "--format=%(refname)", "refs/review-pr/")

    def commit_in_worktree(self):
        (self.worktree / "a.txt").write_text("one\ntwo\nthree\n")
        self.git(self.worktree, "commit", "-q", "-am", "fix")
        return self.git(self.worktree, "rev-parse", "HEAD")
