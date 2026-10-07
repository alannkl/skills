#!/usr/bin/env node

import { readFile, realpath } from "node:fs/promises";
import { parseArgs } from "node:util";
import { detail, readJson, run } from "./worktree-state.mjs";

const usage = `Usage: node check-approved-paths.mjs --in <worktree-record.json> --approved <paths.txt>

Compares every change in the review worktree (staged, unstaged and untracked,
with renames counted under both names) against the approved file list, one
path per line relative to the worktree root. Prints JSON: changed, unexpected
(changed but not approved), approved_unchanged, and outside_pr (approved paths
absent from the PR's changed-file list, which needed approval by name). Decides
nothing about approval itself. Exits 0 when every change is approved, 1 when
unexpected changes exist, 2 for invalid input.`;

try {
  const { values } = parseArgs({
    options: {
      in: { type: "string" },
      approved: { type: "string" },
      help: { type: "boolean", short: "h" },
    },
  });
  if (values.help || !values.in || !values.approved) {
    console.error(usage);
    process.exit(values.help ? 0 : 2);
  }
  const record = await readJson(await realpath(values.in));
  if (record.version !== 1 || record.status !== "ready" || !record.worktree)
    throw new Error("Input must be a ready worktree record from prepare-worktree.mjs.");
  const worktree = await realpath(record.worktree);
  const approved = new Set(
    (await readFile(values.approved, "utf8"))
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean),
  );
  const status = await run(
    "git",
    ["status", "--porcelain=v2", "-z", "--untracked-files=all"],
    worktree,
  );
  // Porcelain v2 puts the path after a fixed number of space-separated fields
  // per entry kind: 8 for ordinary changes, 9 for renames and copies (whose
  // old path follows as its own NUL-terminated field), 10 for unmerged entries.
  const FIELDS = { 1: 8, 2: 9, u: 10 };
  const changed = new Set();
  const entries = status.split("\0");
  for (let index = 0; index < entries.length; index += 1) {
    const entry = entries[index];
    if (!entry) continue;
    const kind = entry[0];
    if (kind === "?") {
      changed.add(entry.slice(2));
    } else if (FIELDS[kind]) {
      changed.add(entry.split(" ").slice(FIELDS[kind]).join(" "));
      if (kind === "2") changed.add(entries[++index]);
    }
  }
  const prFiles = new Set(record.files ?? []);
  const result = {
    changed: [...changed].sort(),
    unexpected: [...changed].filter((path) => !approved.has(path)).sort(),
    approved_unchanged: [...approved].filter((path) => !changed.has(path)).sort(),
    outside_pr: [...approved].filter((path) => !prFiles.has(path)).sort(),
  };
  result.status = result.unexpected.length ? "violations" : "within";
  console.log(JSON.stringify(result, null, 2));
  process.exitCode = result.unexpected.length ? 1 : 0;
} catch (error) {
  console.log(JSON.stringify({ status: "failed", reason: detail(error) }, null, 2));
  process.exitCode = 2;
}
