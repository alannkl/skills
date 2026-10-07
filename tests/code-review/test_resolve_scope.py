"""resolve-scope.py picks the review scope by the skill's fallback chain and inventories it."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "code-review" / "scripts" / "resolve-scope.py"


class Repo:
    def __init__(self, root, env):
        self.root = root
        self.env = env

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, env=self.env, check=True, capture_output=True, text=True).stdout.strip()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def commit(self, message, **files):
        for name, text in files.items():
            self.write(name, text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")


class ResolveScope(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(os.path.realpath(self._tmp.name))
        (self.tmp / "gitconfig").write_text("")
        self.env = {
            **os.environ,
            "GIT_CONFIG_GLOBAL": str(self.tmp / "gitconfig"),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.com",
        }
        remote = self.tmp / "remote.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], env=self.env, check=True)
        seed = Repo(self.tmp / "seed", self.env)
        seed.root.mkdir()
        seed.git("init", "-q", "-b", "main")
        seed.commit("base", **{"a.txt": "one\n", "AGENTS.md": "rules\n"})
        seed.git("push", "-q", str(remote), "main")
        subprocess.run(["git", "clone", "-q", str(remote), str(self.tmp / "work")], env=self.env, check=True)
        self.repo = Repo(self.tmp / "work", self.env)
        self.repo.git("remote", "set-head", "origin", "main")

    def resolve(self, *flags):
        out = self.tmp / "out"
        completed = subprocess.run([sys.executable, str(SCRIPT), "--out", str(out), *flags], cwd=self.repo.root, env=self.env, capture_output=True, text=True)
        return completed.returncode, json.loads(completed.stdout)

    def paths(self, result):
        return [item["path"] for item in result["files"]]

    def test_staged_wins_and_names_excluded_edits(self):
        """Given staged, unstaged and untracked changes, when resolved without a scope, then the staged rung wins and the others are listed as excluded."""
        self.repo.write("a.txt", "one\ntwo\n")
        self.repo.git("add", "a.txt")
        self.repo.write("a.txt", "one\ntwo\nthree\n")
        self.repo.write("b.txt", "unstaged? no, untracked\n")
        code, result = self.resolve()
        self.assertEqual(code, 0)
        self.assertEqual(result["rung"], "staged")
        self.assertEqual(self.paths(result), ["a.txt"])
        self.assertEqual(result["excluded"], [{"path": "a.txt", "reason": "also has unstaged edits"}, {"path": "b.txt", "reason": "untracked"}])
        self.assertIn("+two", Path(result["diff"]).read_text())
        self.assertNotIn("three", Path(result["diff"]).read_text())

    def test_worktree_rung_includes_untracked_contents(self):
        """Given only an unstaged edit and an untracked file, when resolved, then the worktree rung wins and the patch carries the untracked file's content."""
        self.repo.write("a.txt", "one\ntwo\n")
        self.repo.write("new/b.txt", "brand new\n")
        code, result = self.resolve()
        self.assertEqual(code, 0)
        self.assertEqual(result["rung"], "worktree")
        self.assertEqual(self.paths(result), ["a.txt", "new/b.txt"])
        self.assertIn("untracked", result["files"][1]["flags"])
        self.assertIn("+brand new", Path(result["diff"]).read_text())
        self.assertEqual(result["stat"], {"files": 2, "insertions": 2, "deletions": 0})

    def test_upstream_rung_lists_commits_with_issue_refs(self):
        """Given a clean tree one commit ahead of its upstream, when resolved, then the upstream rung wins with the commit and its issue reference."""
        self.repo.commit("fix: handle empty input\n\nCloses #45", **{"a.txt": "one\ntwo\n"})
        code, result = self.resolve()
        self.assertEqual(code, 0)
        self.assertEqual(result["rung"], "upstream")
        self.assertEqual(result["commits"][0]["refs"], ["#45"])
        self.assertEqual(result["behind_base"], 0)
        self.assertEqual(self.paths(result), ["a.txt"])

    def test_branch_rung_uses_default_branch_and_counts_behind(self):
        """Given a feature branch without upstream whose base moved on, when resolved, then the branch rung compares against the merge base and reports behind_base."""
        self.repo.git("checkout", "-q", "-b", "feature")
        self.repo.commit("feature", **{"src/f.py": "print(1)\n"})
        self.repo.git("checkout", "-q", "main")
        self.repo.commit("advance", **{"c.txt": "c\n"})
        self.repo.git("push", "-q", "origin", "main")
        self.repo.git("checkout", "-q", "feature")
        code, result = self.resolve()
        self.assertEqual(code, 0)
        self.assertEqual(result["rung"], "branch")
        self.assertEqual(result["default_branch"], "origin/main")
        self.assertEqual(self.paths(result), ["src/f.py"])
        self.assertEqual(result["behind_base"], 1)
        self.assertEqual(result["guidance"], ["AGENTS.md"])

    def test_clean_default_branch_is_empty_with_exit_one(self):
        """Given a clean checkout of the default branch, when resolved, then every rung is empty, the JSON still prints, and the exit code is 1."""
        code, result = self.resolve()
        self.assertEqual(code, 1)
        self.assertEqual(result["rung"], "branch")
        self.assertEqual(result["files"], [])

    def test_explicit_range_and_single_commit(self):
        """Given an explicit base...head range or a single commit, when resolved, then exactly those changes are reported."""
        first = self.repo.commit("one", **{"x.txt": "x\n"})
        second = self.repo.commit("two", **{"y.txt": "y\n"})
        code, result = self.resolve("--scope", f"{first}...{second}")
        self.assertEqual((code, self.paths(result)), (0, ["y.txt"]))
        code, result = self.resolve("--scope", first)
        self.assertEqual((code, self.paths(result)), (0, ["x.txt"]))

    def test_bad_ref_exits_two(self):
        """Given a scope naming a ref that does not exist, when resolved, then it exits 2 with the ref in the error."""
        completed = subprocess.run([sys.executable, str(SCRIPT), "--scope", "nope...HEAD"], cwd=self.repo.root, env=self.env, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 2)
        self.assertIn("nope", json.loads(completed.stdout)["error"])

    def test_every_rung_prints_the_same_fields(self):
        """Given a staged change, when resolved, then the JSON carries every documented field even where the rung leaves it empty."""
        self.repo.write("a.txt", "x\n")
        self.repo.git("add", "a.txt")
        code, result = self.resolve()
        self.assertEqual(code, 0)
        for key in ["rung", "scope", "base", "head", "behind_base", "default_branch", "commits", "files", "excluded", "guidance", "stat", "diff", "repository", "warnings"]:
            self.assertIn(key, result)
        self.assertEqual((result["behind_base"], result["commits"]), (None, []))

    def test_brace_in_filename_is_not_a_rename(self):
        """Given a staged file whose name contains braces, when resolved, then it is inventoried with its line counts."""
        self.repo.write("src/{slug}.ts", "export {}\n")
        self.repo.git("add", "-A")
        code, result = self.resolve()
        self.assertEqual(code, 0, result)
        self.assertEqual(self.paths(result), ["src/{slug}.ts"])
        self.assertEqual(result["stat"]["insertions"], 1)

    def test_nested_instructions_and_rename_source_guidance_are_found(self):
        """Given a nested GitHub instructions file and a rename out of a directory with its own CLAUDE.md, when resolved, then both guidance files are listed."""
        self.repo.commit("layout", **{"old/CLAUDE.md": "old rules\n", "old/f.txt": "f\n", ".github/instructions/py/all.instructions.md": "---\napplyTo: '**/*.py'\n---\n"})
        self.repo.git("mv", "old/f.txt", "new.txt")
        code, result = self.resolve()
        self.assertEqual(code, 0, result)
        self.assertEqual(result["guidance"], [".github/instructions/py/all.instructions.md", "AGENTS.md", "old/CLAUDE.md"])

    def test_guidance_deleted_only_on_disk_is_still_found(self):
        """Given a staged edit beside an unstaged deletion of the guidance file governing it, when the staged scope is resolved, then that guidance is listed from the base revision."""
        self.repo.commit("layout", **{"src/AGENTS.md": "src rules\n", "src/a.py": "x = 1\n"})
        self.repo.write("src/a.py", "x = 2\n")
        self.repo.git("add", "src/a.py")
        (self.repo.root / "src" / "AGENTS.md").unlink()
        code, result = self.resolve("--scope", "staged")
        self.assertEqual(code, 0, result)
        self.assertEqual(self.paths(result), ["src/a.py"])
        self.assertEqual(result["guidance"], ["AGENTS.md", "src/AGENTS.md"])

    def test_guidance_comes_from_base_not_the_change(self):
        """Given a staged change that deletes the root AGENTS.md and adds src/CLAUDE.md, when resolved, then guidance lists the deleted base file and not the added one."""
        self.repo.git("rm", "-q", "AGENTS.md")
        self.repo.write("src/CLAUDE.md", "new rules\n")
        self.repo.git("add", "src/CLAUDE.md")
        code, result = self.resolve("--scope", "staged")
        self.assertEqual(code, 0, result)
        self.assertEqual(result["guidance"], ["AGENTS.md"])

    def test_repository_without_commits_reviews_staged_files(self):
        """Given a freshly initialised repository with staged files, when resolved, then the staged rung wins with no head commit."""
        fresh = Repo(self.tmp / "fresh", self.env)
        fresh.root.mkdir()
        fresh.git("init", "-q", "-b", "main")
        fresh.write("first.txt", "hello\n")
        fresh.git("add", "first.txt")
        completed = subprocess.run([sys.executable, str(SCRIPT), "--out", str(self.tmp / "fresh-out")], cwd=fresh.root, env=self.env, capture_output=True, text=True)
        result = json.loads(completed.stdout)
        self.assertEqual((completed.returncode, result["rung"], result["base"], result["head"]), (0, "staged", None, "index"), completed.stderr)
        self.assertEqual(self.paths(result), ["first.txt"])

    def test_default_output_directories_never_collide(self):
        """Given two resolutions in the same second without --out, when resolved, then each gets its own directory and patch."""
        self.repo.write("a.txt", "x\n")
        dirs = set()
        for _ in range(2):
            completed = subprocess.run([sys.executable, str(SCRIPT)], cwd=self.repo.root, env=self.env, capture_output=True, text=True)
            directory = Path(json.loads(completed.stdout)["diff"]).parent
            self.addCleanup(shutil.rmtree, directory, ignore_errors=True)
            dirs.add(directory)
        self.assertEqual(len(dirs), 2)
        self.assertTrue(all(directory.parent == Path.home() / ".tmp" / "code-review" for directory in dirs))

    @unittest.skipIf(os.geteuid() == 0, "root can read unreadable files")
    def test_unreadable_untracked_file_is_an_error(self):
        """Given an untracked file the process cannot read, when resolved, then it exits 2 naming the file instead of silently dropping it from the patch."""
        self.repo.write("secret.txt", "x\n")
        (self.repo.root / "secret.txt").chmod(0)
        self.addCleanup((self.repo.root / "secret.txt").chmod, 0o644)
        completed = subprocess.run([sys.executable, str(SCRIPT), "--out", str(self.tmp / "out")], cwd=self.repo.root, env=self.env, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 2, completed.stdout)
        self.assertIn("secret.txt", json.loads(completed.stdout)["error"])

    def test_flags_mark_lockfiles_migrations_binaries_and_renames(self):
        """Given staged changes touching a lockfile, a migration, a binary and a rename, when resolved, then each file carries the matching flag or old path."""
        self.repo.write("package-lock.json", "{}\n")
        self.repo.write("db/migrations/0001_init.sql", "create table t;\n")
        (self.repo.root / "logo.png").write_bytes(b"\x89PNG\x00\x01\x02")
        self.repo.git("mv", "a.txt", "renamed.txt")
        self.repo.git("add", "-A")
        code, result = self.resolve()
        files = {item["path"]: item for item in result["files"]}
        self.assertIn("lockfile", files["package-lock.json"]["flags"])
        self.assertIn("migration", files["db/migrations/0001_init.sql"]["flags"])
        self.assertIn("binary", files["logo.png"]["flags"])
        self.assertEqual((files["renamed.txt"]["status"], files["renamed.txt"]["old_path"]), ("R", "a.txt"))


if __name__ == "__main__":
    unittest.main()
