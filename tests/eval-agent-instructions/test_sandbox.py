"""The bubblewrap sandbox exposes only system files, the toolchain and the caller's binds, and its identity
tracks everything a run depends on."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[2] / "eval-agent-instructions" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import sandbox  # noqa: E402
import tasks  # noqa: E402
from eval_instructions import choose_slots, mean_agent_seconds, parse_concurrency, split_slots  # noqa: E402

# The Dockerfile every stored Docker baseline was built from; a change to its text invalidates them all.
FROZEN_DOCKERFILE = """FROM b
COPY skills/ /skills/
COPY case/ /tmp/case/
WORKDIR /app
RUN if [ -f /tmp/case/scaffold.sh ]; then bash /tmp/case/scaffold.sh; \\
    elif [ -d /tmp/case/fixture ]; then cp -a /tmp/case/fixture/. /app/; fi \\
    && rm -rf /tmp/case
"""


def mounts(args: list[str]) -> list[tuple[str, str, str]]:
    """(option, source, target) for each bind or tmpfs, in order."""
    found, i = [], 0
    while i < len(args):
        if args[i] in ("--bind", "--ro-bind", "--ro-bind-try"):
            found.append((args[i], args[i + 1], args[i + 2]))
            i += 3
        elif args[i] == "--tmpfs":
            found.append((args[i], "", args[i + 1]))
            i += 2
        else:
            i += 1
    return found


class Sandbox(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.tmp = Path(self._tmp.name)

    def test_only_system_files_and_the_given_binds_come_from_the_host(self):
        toolchain = self.tmp / "toolchain"
        given = [(self.tmp / "app", "/app", False)] + sandbox.toolchain_binds(toolchain)
        found = mounts(sandbox.bwrap_args(given, "/app"))
        given_sources = {str(source) for source, _, _ in given}
        for option, source, target in found:
            if option == "--tmpfs" or source in given_sources:
                continue
            self.assertTrue(source == "/usr" or source.startswith("/etc/"), source)
            self.assertNotEqual(option, "--bind", f"{source} is writable")
        targets = [target for _, _, target in found]
        # The toolchain replaces the host's /usr/local, never the other way round.
        self.assertLess(targets.index("/usr/local"), targets.index("/usr/local/bin"))

    def test_binds_apply_parents_first(self):
        given = [(self.tmp / "nvm", "/root/.nvm", True), (self.tmp / "root", "/root", False)]
        targets = [t for _, _, t in mounts(sandbox.bwrap_args(given, "/"))]
        self.assertLess(targets.index("/root"), targets.index("/root/.nvm"))

    def test_the_sandbox_gets_no_host_environment(self):
        with mock.patch.dict(os.environ, {"OPENROUTER_API_KEY": "k"}):
            self.assertEqual(set(sandbox.sandbox_env()), {"PATH", "HOME", "NVM_DIR"})
        self.assertEqual(sandbox.sandbox_env({"X": "1"})["X"], "1")

    def test_environment_id_follows_the_built_toolchain_and_sandbox_code(self):
        code = self.tmp / "code"
        code.mkdir()
        for name in ("sandbox.py", "bwrap_env.py"):
            shutil.copy(SCRIPTS / name, code / name)
        toolchain = self.tmp / "toolchain-x"
        toolchain.mkdir()
        (toolchain / "versions.txt").write_text("v24.1.0\n")
        with mock.patch.object(sandbox, "HERE", code):
            first = sandbox.environment_id(toolchain)
            (toolchain / "versions.txt").write_text("v24.2.0\n")
            second = sandbox.environment_id(toolchain)
            with (code / "bwrap_env.py").open("a") as f:
                f.write("\n")
            third = sandbox.environment_id(toolchain)
        self.assertEqual(len({first, second, third}), 3)

    def test_scratch_of_a_dead_run_is_removed(self):
        dead = subprocess.Popen(["true"])
        dead.wait()
        for name, pid in (("alive", os.getpid()), ("dead", dead.pid)):
            (self.tmp / name / "tmp").mkdir(parents=True)
            (self.tmp / name / "owner.pid").write_text(str(pid))
        (self.tmp / "unowned").mkdir()
        with mock.patch.object(sandbox, "SCRATCH", self.tmp):
            sandbox.sweep_scratch()
        self.assertEqual(sorted(p.name for p in self.tmp.iterdir()), ["alive"])

    def test_task_dockerfile_text_is_unchanged(self):
        self.assertEqual(tasks.DOCKERFILE.format(base_image="b"), FROZEN_DOCKERFILE)

    def test_slots_follow_each_setups_expected_agent_time(self):
        trials = {"slow": 100, "fast": 100, "new": 100}
        seconds = {"slow": 60.0, "fast": 20.0, "new": None}
        # "new" has no history, so it counts at the others' mean of 40 s.
        self.assertEqual(split_slots(12, trials, seconds, {}), {"slow": 6, "fast": 2, "new": 4})
        self.assertEqual(split_slots(12, trials, seconds, {"new": 2}), {"new": 2, "slow": 8, "fast": 2})
        self.assertEqual(split_slots(2, trials, seconds, {}), {"slow": 1, "fast": 1, "new": 1})

    def test_default_slots_fit_in_free_memory_and_a_given_number_runs_as_given(self):
        trials, seconds = {"claw": 100, "codex": 100}, {"claw": 60.0, "codex": 20.0}
        gb = {"claw": 1.0, "codex": 0.5}
        self.assertEqual(choose_slots(None, trials, seconds, {}, gb, 100.0), {"claw": 12, "codex": 4})
        fitted = choose_slots(None, trials, seconds, {}, gb, 8.0)
        self.assertLessEqual(sum(n * gb[name] for name, n in fitted.items()), 8.0)
        self.assertEqual(sum(fitted.values()), 9)
        self.assertEqual(choose_slots(24, trials, seconds, {}, gb, 8.0), {"claw": 18, "codex": 6})
        # Each setup keeps one session even when memory holds none.
        self.assertEqual(choose_slots(None, trials, seconds, {}, gb, 0.0), {"claw": 1, "codex": 1})

    def test_agent_time_comes_from_earlier_runs_without_probes(self):
        for run, trial, end in (("r1", "case--with__a", "10:01:00"), ("r2", "case--without__b", "10:00:30"),
                                ("r2", "probe--with__c", "10:00:02")):
            path = self.tmp / "results" / run / "jobs" / "slow" / "main" / trial
            path.mkdir(parents=True)
            (path / "result.json").write_text('{"agent_execution": {"started_at": "2026-10-25T10:00:00Z", '
                                              f'"finished_at": "2026-10-25T{end}Z"}}}}')
        self.assertEqual(mean_agent_seconds(self.tmp / "results", "slow"), 45.0)
        os.utime(self.tmp / "results" / "r2" / "jobs" / "slow", (0, 0))  # r1 is now the newest run
        self.assertEqual(mean_agent_seconds(self.tmp / "results", "slow", sample=1), 60.0)
        self.assertIsNone(mean_agent_seconds(self.tmp / "results", "other"))

    def test_concurrency_values(self):
        self.assertEqual(parse_concurrency(["a=4", "16"]), (16, {"a": 4}))
        self.assertEqual(parse_concurrency([]), (None, {}))
        with self.assertRaises(ValueError):
            parse_concurrency(["a=x"])

if __name__ == "__main__":
    unittest.main()
