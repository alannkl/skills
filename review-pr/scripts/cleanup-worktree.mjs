#!/usr/bin/env node

import { access, readFile, realpath } from "node:fs/promises";
import path from "node:path";
import { parseArgs } from "node:util";
import {
  detail,
  fetchRefs,
  git,
  readJson,
  run,
  saveRecord,
} from "./worktree-state.mjs";

const usage = `Usage: node cleanup-worktree.mjs --in <worktree-record.json> [--remove] [--discard-ignored]

Inspects the exact worktree created by prepare-worktree.mjs. Default is inspection
only. --remove attests that the workflow is finished, no agents or checks use the
worktree, and needed evidence is saved elsewhere. Run outside the review worktree.
Dirty files, unpushed commits, attached branches, locks and identity mismatches
block removal. Ignored files also block removal unless --discard-ignored confirms
that ALL remaining ignored content is disposable. No force, push or global prune.
Prints JSON; exits 0 when eligible or removed, 1 when retained or on failure.
The saved record remains after removal. Retry --remove to finish private-ref
cleanup if it failed after the worktree was removed.`;

const { values } = parseArgs({
  options: {
    in: { type: "string" },
    remove: { type: "boolean" },
    "discard-ignored": { type: "boolean" },
    help: { type: "boolean", short: "h" },
  },
});
if (values.help || !values.in) {
  console.error(usage);
  process.exit(values.help ? 0 : 2);
}

let record;
try {
  const recordPath = await realpath(values.in);
  record = await readJson(recordPath);
  if (
    record.version !== 1 ||
    !/^[0-9a-f-]{36}$/.test(record.id) ||
    record.refPrefix !== `refs/review-pr/${record.id}` ||
    recordPath !== path.join(record.commonDir, "review-pr", `${record.id}.json`)
  ) {
    throw new Error("Invalid worktree record identity.");
  }
  const root = record.repository;
  if (
    (await realpath(
      await git(
        root,
        "rev-parse",
        "--path-format=absolute",
        "--git-common-dir",
      ),
    )) !== record.commonDir
  ) {
    throw new Error("Git repository identity changed.");
  }
  if (record.status === "removed") {
    if (values.remove) await removePrivateRefs(record);
    console.log(
      JSON.stringify({
        status: "removed",
        worktree: record.worktree,
        head: record.lastHead,
      }),
    );
    process.exit(0);
  }
  if (record.status !== "ready")
    throw new Error("Setup is incomplete; retain it for inspection.");
  const worktree = await realpath(record.worktree);
  if (worktree !== record.worktree || worktree === (await realpath(root)))
    throw new Error("Worktree path identity changed.");
  if (
    (await realpath(
      await git(
        worktree,
        "rev-parse",
        "--path-format=absolute",
        "--git-common-dir",
      ),
    )) !== record.commonDir ||
    (await realpath(await git(worktree, "rev-parse", "--absolute-git-dir"))) !==
      record.gitDir
  ) {
    throw new Error("Git worktree identity changed.");
  }
  const owner = await readJson(
    path.join(record.gitDir, "review-pr-owner.json"),
  );
  if (owner.id !== record.id || owner.recordPath !== recordPath)
    throw new Error("Worktree ownership does not match the record.");
  const backlink = (
    await readFile(path.join(record.gitDir, "gitdir"), "utf8")
  ).trimEnd();
  if (
    (await realpath(backlink)) !== (await realpath(path.join(worktree, ".git")))
  )
    throw new Error("Worktree registration changed.");
  if (await git(worktree, "branch", "--show-current"))
    throw new Error("Worktree now has an attached branch.");
  const locked = await access(path.join(record.gitDir, "locked")).then(
    () => true,
    (error) => {
      if (error.code !== "ENOENT") throw error;
      return false;
    },
  );
  if (locked) throw new Error("Worktree is locked.");
  const status = await run(
    "git",
    ["status", "--porcelain", "-z", "--untracked-files=all", "--ignored"],
    worktree,
  );
  const changes = status.split("\0").filter(Boolean);
  if (changes.some((item) => !item.startsWith("!! ")))
    throw new Error("Worktree has tracked changes or untracked files.");
  const ignored = changes.map((item) => item.slice(3));
  if (ignored.length && !values["discard-ignored"]) {
    throw new Error(
      `Ignored content requires preservation or --discard-ignored: ${JSON.stringify(ignored)}`,
    );
  }
  const head = await git(worktree, "rev-parse", "HEAD");
  if (head !== record.head) {
    await fetchRefs(record, [
      `+refs/pull/${record.pr.number}/head:${record.refPrefix}/remote-head`,
    ]);
    try {
      await git(
        root,
        "merge-base",
        "--is-ancestor",
        head,
        `${record.refPrefix}/remote-head`,
      );
    } catch {
      throw new Error(
        "Local HEAD is not contained in the freshly fetched PR head; retain unpushed commits.",
      );
    }
  }
  if (!values.remove) {
    console.log(
      JSON.stringify({ status: "eligible", worktree, head, ignored }, null, 2),
    );
    process.exit(0);
  }
  const cwd = await realpath(process.cwd());
  const relative = path.relative(worktree, cwd);
  if (
    !relative ||
    (!relative.startsWith(`..${path.sep}`) &&
      relative !== ".." &&
      !path.isAbsolute(relative))
  ) {
    throw new Error(
      "Return to the starting directory before removing the review worktree.",
    );
  }
  // Git rechecks dirtiness and locks during removal. Never fall back to rm -rf.
  if ((await git(worktree, "rev-parse", "HEAD")) !== head)
    throw new Error("Worktree HEAD changed during cleanup.");
  await git(root, "worktree", "remove", worktree);
  record.status = "removed";
  record.lastHead = head;
  record.removedAt = new Date().toISOString();
  await saveRecord(recordPath, record);
  await removePrivateRefs(record);
  console.log(
    JSON.stringify(
      { status: "removed", worktree, head, record: recordPath },
      null,
      2,
    ),
  );
} catch (error) {
  console.log(
    JSON.stringify(
      {
        status: record?.status === "removed" ? "removed" : "retained",
        worktree: record?.worktree,
        reason: detail(error),
      },
      null,
      2,
    ),
  );
  process.exitCode = 1;
}

async function removePrivateRefs(record) {
  for (const name of ["head", "base", "remote-head"]) {
    await git(
      record.repository,
      "update-ref",
      "-d",
      `${record.refPrefix}/${name}`,
    );
  }
}
