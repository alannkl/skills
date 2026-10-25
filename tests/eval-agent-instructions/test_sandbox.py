"""The bubblewrap sandbox exposes only system files, the toolchain and the caller's binds, and its identity
tracks everything a run depends on."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from collections import defaultdict
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[2] / "eval-agent-instructions" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import sandbox  # noqa: E402
import tasks  # noqa: E402
from eval_instructions import expected_seconds, parse_concurrency, run_queue, session_budget  # noqa: E402

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

    def test_queue_runs_in_order_within_the_budget_and_each_setups_cap(self):
        lock, running, peak, order = threading.Lock(), defaultdict(int), defaultdict(int), []

        def launch(item):
            with lock:
                order.append(item[1])
                running[item[0]] += 1
                running["all"] += 1
                for key in (item[0], "all"):
                    peak[key] = max(peak[key], running[key])
            time.sleep(0.02)
            with lock:
                running[item[0]] -= 1
                running["all"] -= 1

        items = [("a", f"a{i}") for i in range(6)] + [("b", f"b{i}") for i in range(6)]
        run_queue(items, 4, {"a": 1}, launch)
        self.assertEqual(sorted(order), sorted(i[1] for i in items))
        self.assertEqual((peak["a"], peak["all"]), (1, 4))
        self.assertEqual(order[0], "a0")

    def test_budget_fits_in_free_memory(self):
        self.assertEqual(session_budget(0.3, 100.0), 32)
        self.assertEqual(session_budget(0.3, 6.0), 20)
        self.assertEqual(session_budget(1.0, 0.0), 1)
        self.assertEqual(session_budget(0.0, 0.0), 32)

    def test_expected_time_per_task_comes_from_earlier_runs_without_probes(self):
        for run, task, trial, end in (("r1", "case--with", "case--wi__a", "10:01:00"),
                                      ("r2", "case--with", "case--wi__b", "10:00:30"),
                                      ("r2", "other--with", "other--w__d", "10:00:10"),
                                      ("r2", "probe--with", "probe--with__c", "10:00:02")):
            path = self.tmp / "results" / run / "jobs" / "slow" / "job" / trial
            path.mkdir(parents=True)
            (path / "config.json").write_text(json.dumps({"task": {"path": f"/x/tasks/{task}"}}))
            (path / "result.json").write_text('{"agent_execution": {"started_at": "2026-10-25T10:00:00Z", '
                                              f'"finished_at": "2026-10-25T{end}Z"}}}}')
        self.assertEqual(expected_seconds(self.tmp / "results", "slow"),
                         {"case--with": 45.0, "other--with": 10.0, None: 100 / 3})
        self.assertEqual(expected_seconds(self.tmp / "results", "other"), {})

    def test_concurrency_values(self):
        self.assertEqual(parse_concurrency(["a=4", "16"]), (16, {"a": 4}))
        self.assertEqual(parse_concurrency([]), (None, {}))
        with self.assertRaises(ValueError):
            parse_concurrency(["a=x"])

if __name__ == "__main__":
    unittest.main()
