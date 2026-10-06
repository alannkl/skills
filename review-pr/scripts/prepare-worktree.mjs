#!/usr/bin/env node

import { randomUUID } from "node:crypto";
import { mkdir, mkdtemp, realpath, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { parseArgs } from "node:util";
import {
  detail,
  fetchRefs,
  git,
  githubRepo,
  readJson,
  run,
  saveRecord,
} from "./worktree-state.mjs";

const usage = `Usage: node prepare-worktree.mjs --in <read-pr.json> [--remote <name>] [--worktree-root <directory>]

Run from the caller's checkout. Selects a remote matching the PR's base repository,
checks current PR metadata, fetches the PR head and base into private refs, and
creates a fresh detached worktree. Works for same-repository and fork PRs.
Prints a record path containing the starting checkout, worktree identity, exact
commit IDs, diff scope and changed files. The record lives in the shared Git
directory; worktrees default to ~/.tmp/review-pr/worktrees, outside the checkout.
Does not install dependencies. Exits 1 on failure, retaining any partial setup
and reporting its record path. Refresh read-pr.json if the PR moved.`;

const { values } = parseArgs({
  options: {
    in: { type: "string" },
    remote: { type: "string" },
    "worktree-root": { type: "string" },
    help: { type: "boolean", short: "h" },
  },
});
if (values.help || !values.in) {
  console.error(usage);
  process.exit(values.help ? 0 : 2);
}

let record;
let recordPath;
try {
  const input = await realpath(values.in);
  const { pr } = await readJson(input);
  if (
    !pr ||
    pr.state !== "OPEN" ||
    !Number.isSafeInteger(pr.number) ||
    pr.number < 1 ||
    !/^[0-9a-f]{40}$/i.test(pr.headRefOid) ||
    !/^[\w.-]+\/[\w.-]+$/.test(pr.repo) ||
    pr.url !== `https://github.com/${pr.repo}/pull/${pr.number}` ||
    typeof pr.baseRefName !== "string"
  ) {
    throw new Error("Input must be an open PR record from read-pr.mjs.");
  }
  const directory = await realpath(process.cwd());
  const repository = await realpath(
    await git(directory, "rev-parse", "--show-toplevel"),
  );
  const commonDir = await realpath(
    await git(
      repository,
      "rev-parse",
      "--path-format=absolute",
      "--git-common-dir",
    ),
  );
  await git(repository, "check-ref-format", `refs/heads/${pr.baseRefName}`);
  const remotes = (await git(repository, "remote")).split("\n").filter(Boolean);
  const matches = [];
  for (const remote of remotes) {
    if (
      githubRepo(await git(repository, "remote", "get-url", remote)) ===
      pr.repo.toLowerCase()
    ) {
      matches.push(remote);
    }
  }
  const remote =
    values.remote || (matches.includes("origin") ? "origin" : matches[0]);
  if (!remote || !matches.includes(remote)) {
    throw new Error(
      `No selected remote matches github.com/${pr.repo}. Configure one before preparing the review.`,
    );
  }
  const current = JSON.parse(
    await run(
      "gh",
      ["pr", "view", pr.url, "--json", "state,headRefOid,baseRefName"],
      repository,
    ),
  );
  if (
    current.state !== "OPEN" ||
    current.headRefOid !== pr.headRefOid ||
    current.baseRefName !== pr.baseRefName
  ) {
    throw new Error(
      "PR state, head or base changed. Refresh the input with read-pr.mjs.",
    );
  }
  const id = randomUUID();
  recordPath = path.join(commonDir, "review-pr", `${id}.json`);
  await mkdir(path.dirname(recordPath), { recursive: true });
  record = {
    version: 1,
    id,
    status: "preparing",
    createdAt: new Date().toISOString(),
    input,
    repository,
    commonDir,
    remote,
    starting: {
      directory,
      branch: await git(repository, "branch", "--show-current"),
      head: await git(repository, "rev-parse", "HEAD"),
    },
    pr,
    refPrefix: `refs/review-pr/${id}`,
    worktree: null,
  };
  await saveRecord(recordPath, record);
  await fetchRefs(record, [
    `+refs/pull/${pr.number}/head:${record.refPrefix}/head`,
    `+refs/heads/${pr.baseRefName}:${record.refPrefix}/base`,
  ]);
  const head = await git(
    repository,
    "rev-parse",
    `${record.refPrefix}/head^{commit}`,
  );
  if (head !== pr.headRefOid) {
    throw new Error(
      "PR head moved during fetch. Refresh the input with read-pr.mjs.",
    );
  }
  const base = await git(
    repository,
    "rev-parse",
    `${record.refPrefix}/base^{commit}`,
  );
  const mergeBases = (
    await git(repository, "merge-base", "--all", base, head)
  ).split("\n");
  if (mergeBases.length !== 1)
    throw new Error("Multiple merge bases require manual scope selection.");
  const scope = `${base}...${head}`;
  const files = (
    await run(
      "git",
      ["diff", "--name-only", "--no-renames", "-z", scope, "--"],
      repository,
    )
  )
    .split("\0")
    .filter(Boolean);
  Object.assign(record, {
    head,
    base,
    mergeBase: mergeBases[0],
    scope,
    files,
    behindBase: Number(
      await git(repository, "rev-list", "--count", `${head}..${base}`),
    ),
  });
  const worktreeRoot = path.resolve(
    values["worktree-root"] ||
      path.join(os.homedir(), ".tmp", "review-pr", "worktrees"),
  );
  await mkdir(worktreeRoot, { recursive: true });
  record.worktree = await realpath(
    await mkdtemp(
      path.join(worktreeRoot, `pr-${pr.number}-${head.slice(0, 8)}-`),
    ),
  );
  await saveRecord(recordPath, record);
  await git(repository, "worktree", "add", "--detach", record.worktree, head);
  record.gitDir = await realpath(
    await git(record.worktree, "rev-parse", "--absolute-git-dir"),
  );
  await writeFile(
    path.join(record.gitDir, "review-pr-owner.json"),
    JSON.stringify({ id, recordPath }),
    { flag: "wx", mode: 0o600 },
  );
  if ((await git(record.worktree, "rev-parse", "HEAD")) !== head)
    throw new Error("Worktree HEAD differs from the fetched PR head.");
  record.status = "ready";
  await saveRecord(recordPath, record);
  console.log(recordPath);
} catch (error) {
  if (record && recordPath) {
    record.error = detail(error);
    await saveRecord(recordPath, record).catch(() => {});
    console.error(`Partial setup retained. Record: ${recordPath}`);
  }
  console.error(detail(error));
  process.exitCode = 1;
}
