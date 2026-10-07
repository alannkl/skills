#!/usr/bin/env node

import { realpath } from "node:fs/promises";
import { parseArgs } from "node:util";
import {
  detail,
  fetchRefs,
  git,
  githubRepo,
  readJson,
  run,
} from "./worktree-state.mjs";

const usage = `Usage: node push-fixes.mjs --in <worktree-record.json> [--pr <read-pr.json>] [--dry-run]

Pushes the review worktree's commits to the PR's source branch without force.
Resolves the source repository from the PR's head repository metadata (forks
included), selects a remote whose every push URL points at it, confirms the
worktree is clean and detached, fetches the PR's current head and requires it
to lie between the reviewed head and the local HEAD, then pushes
HEAD:refs/heads/<headRefName> with no tags or submodules.
--pr supplies fresh metadata for the same PR from read-pr.mjs when the record's
copy is incomplete. --dry-run prints the repository, remote, branch and commits
without pushing. Prints JSON. Exits 0 when pushed (or the dry run is ready),
1 when the push failed with Git's reason, 2 for invalid input, missing metadata,
no matching remote or a dirty worktree, 3 when the PR head moved past the local
HEAD or back before the reviewed head, 4 when there is nothing to push. Never
rebases, merges or forces.
Requires an authenticated gh CLI.`;

try {
  const { values } = parseArgs({
    options: {
      in: { type: "string" },
      pr: { type: "string" },
      "dry-run": { type: "boolean" },
      help: { type: "boolean", short: "h" },
    },
  });
  if (values.help || !values.in) {
    console.error(usage);
    process.exit(values.help ? 0 : 2);
  }
  const record = await readJson(await realpath(values.in));
  if (record.version !== 1 || record.status !== "ready" || !record.worktree)
    throw fail(2, "Input must be a ready worktree record from prepare-worktree.mjs.");
  let { pr } = record;
  if (values.pr) {
    const fresh = (await readJson(values.pr)).pr;
    if (!fresh || fresh.number !== pr.number || fresh.url !== pr.url || fresh.repo !== pr.repo)
      throw fail(2, "--pr must be a read-pr.mjs file for the same PR as the record.");
    pr = { ...pr, ...fresh };
  }
  const owner = pr.headRepositoryOwner?.login;
  const name = pr.headRepository?.name;
  const branch = pr.headRefName;
  if (!owner || !name || typeof branch !== "string" || !branch)
    throw fail(2, "PR source metadata (headRepositoryOwner, headRepository, headRefName) is missing; pass --pr with a fresh read-pr.mjs file.");
  const source = `${owner}/${name}`;
  if (!pr.isCrossRepository && source.toLowerCase() !== pr.repo.toLowerCase())
    throw fail(2, `PR is not cross-repository but its head repository ${source} differs from ${pr.repo}.`);
  await git(record.repository, "check-ref-format", `refs/heads/${branch}`);
  const worktree = await realpath(record.worktree);
  if (await git(worktree, "branch", "--show-current"))
    throw fail(2, "Review worktree has an attached branch; expected detached HEAD.");
  const dirty = (
    await run("git", ["status", "--porcelain", "-z", "--untracked-files=all"], worktree)
  )
    .split("\0")
    .filter(Boolean);
  if (dirty.length)
    throw fail(2, `Review worktree has uncommitted changes: ${JSON.stringify(dirty)}`);
  // A remote may carry several push URLs and Git pushes to all of them, so
  // every one must point at the source repository.
  const matches = [];
  for (const remote of (await git(worktree, "remote")).split("\n").filter(Boolean)) {
    const urls = (await git(worktree, "remote", "get-url", "--push", "--all", remote))
      .split("\n")
      .filter(Boolean);
    if (urls.length && urls.every((url) => githubRepo(url) === source.toLowerCase()))
      matches.push(remote);
  }
  const remote = matches.includes("origin") ? "origin" : matches[0];
  if (!remote)
    throw fail(2, `No remote has every push URL pointing at github.com/${source}; add one before pushing.`);
  const current = JSON.parse(
    await run("gh", ["pr", "view", pr.url, "--json", "state,headRefOid,headRefName"], worktree),
  );
  if (current.state !== "OPEN") throw fail(2, `PR is ${current.state}; only OPEN PRs accept fixes.`);
  if (current.headRefName !== branch)
    throw fail(2, `PR source branch changed from ${branch} to ${current.headRefName}; pass --pr with a fresh read-pr.mjs file.`);
  await fetchRefs(record, [`+refs/pull/${pr.number}/head:${record.refPrefix}/remote-head`]);
  const remoteHead = await git(record.repository, "rev-parse", `${record.refPrefix}/remote-head^{commit}`);
  if (remoteHead !== current.headRefOid)
    throw fail(3, "PR head moved during the check; rerun.");
  const head = await git(worktree, "rev-parse", "HEAD");
  const isAncestor = (ancestor, descendant) =>
    git(record.repository, "merge-base", "--is-ancestor", ancestor, descendant).then(() => true, () => false);
  if (!(await isAncestor(remoteHead, head)))
    throw fail(3, `PR head ${remoteHead} is not an ancestor of the local HEAD ${head}; the author or another reviewer pushed. Revalidate before pushing.`);
  // A fast-forward alone would restore commits the author removed; the remote
  // head may only be the reviewed head or a fix commit pushed from here.
  const reviewed = record.pr.headRefOid;
  if (!(await isAncestor(reviewed, remoteHead)))
    throw fail(3, `PR head ${remoteHead} no longer contains the reviewed head ${reviewed}; the author rewrote the branch. Revalidate before pushing.`);
  const commits = (await git(worktree, "log", "--format=%H %s", `${remoteHead}..${head}`))
    .split("\n")
    .filter(Boolean)
    .map((line) => ({ sha: line.slice(0, 40), subject: line.slice(41) }));
  if (!commits.length) throw fail(4, "Nothing to push: the local HEAD is the PR head.");
  const summary = { repository: source, remote, branch, head, refspec: `HEAD:refs/heads/${branch}`, commits };
  if (values["dry-run"]) {
    console.log(JSON.stringify({ status: "ready", ...summary }, null, 2));
    process.exit(0);
  }
  try {
    // Explicit flags override push.followTags and push.recurseSubmodules, which
    // would otherwise publish tags or submodule commits beyond the approved branch.
    await run("git", ["push", "--no-follow-tags", "--recurse-submodules=no", remote, `HEAD:refs/heads/${branch}`], worktree);
  } catch (error) {
    throw fail(1, `Push failed: ${detail(error)}`);
  }
  console.log(JSON.stringify({ status: "pushed", ...summary }, null, 2));
} catch (error) {
  console.log(JSON.stringify({ status: "failed", reason: detail(error) }, null, 2));
  process.exitCode = error.exitCode ?? 2;
}

function fail(exitCode, message) {
  return Object.assign(new Error(message), { exitCode });
}
