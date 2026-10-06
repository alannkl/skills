#!/usr/bin/env node

// Submits one pull-request review from a JSON file. Before posting it checks
// that the reviewed commit is still the PR head, moves inline comments whose
// anchor is not in the PR diff (GitHub would reject the whole review) into the
// review body, and refuses to post a second review of the same kind on the
// same commit by the same viewer, so a retry after an ambiguous failure cannot
// duplicate it.

import { execFile } from "node:child_process";
import { readFile } from "node:fs/promises";
import process from "node:process";
import { parseArgs, promisify } from "node:util";

const execFileAsync = promisify(execFile);
const GH_MAX_BUFFER = 256 * 1024 * 1024;
const PAGE_SIZE = 100;
const EVENTS = {
  REQUEST_CHANGES: "CHANGES_REQUESTED",
  COMMENT: "COMMENTED",
  APPROVE: "APPROVED",
};

const usage = `Usage: node submit-review.mjs <pr-number|pr-url> --in <review.json> [--repo <owner/name>] [--allow-duplicate] [--dry-run]

The JSON file holds the create-review payload: commit_id, event
(REQUEST_CHANGES | COMMENT | APPROVE), body, and comments[] with path, body,
line, side (LEFT | RIGHT), and optionally start_line and start_side. commit_id
must equal the current PR head. Comments anchored outside the PR diff are moved
into the review body. Prints the submitted review as JSON on stdout; with
--dry-run, prints the payload that would be posted instead. Exits 1
when submission fails, 2 for invalid input or an unreadable PR, 3 when the head
moved, and 4 when the same review already exists on that commit. Requires an
authenticated gh CLI.`;

const { values, positionals } = parseArgs({
  options: {
    in: { type: "string" },
    repo: { type: "string" },
    "allow-duplicate": { type: "boolean" },
    "dry-run": { type: "boolean" },
    help: { type: "boolean", short: "h" },
  },
  allowPositionals: true,
});
if (values.help || positionals.length !== 1 || !values.in) {
  console.error(usage);
  process.exit(values.help ? 0 : 2);
}

const review = await readFile(values.in, "utf8")
  .then(JSON.parse)
  .catch((error) => fail(2, `Cannot read the review file: ${error.message}`));
const state = EVENTS[review.event];
if (!state) fail(2, `event must be one of ${Object.keys(EVENTS).join(", ")}`);
if (!/^[0-9a-f]{40}$/i.test(review.commit_id ?? "")) {
  fail(2, "commit_id must be a full commit SHA");
}
const comments = Array.isArray(review.comments) ? review.comments : [];
for (const [index, comment] of comments.entries()) {
  if (!comment.path || !comment.body || !Number.isInteger(comment.line)) {
    fail(2, `comments[${index}] needs path, body, and an integer line`);
  }
  for (const field of ["side", "start_side"]) {
    if (
      comment[field] !== undefined &&
      !["LEFT", "RIGHT"].includes(comment[field])
    ) {
      fail(2, `comments[${index}].${field} must be LEFT or RIGHT`);
    }
  }
}

const prViewArgs = [
  "pr",
  "view",
  positionals[0],
  "--json",
  "number,url,state,headRefOid",
];
if (values.repo) prViewArgs.push("--repo", values.repo);
const prView = await gh(prViewArgs).catch((error) =>
  fail(2, `Cannot read the PR: ${error.stderr?.trim() || error.message}`),
);
const repoMatch = /github\.com\/([^/]+)\/([^/]+)\/pull\/\d+/.exec(prView.url);
if (!repoMatch) {
  fail(2, `Cannot derive the repository from the PR URL: ${prView.url}`);
}
const [, owner, name] = repoMatch;
const pullPath = `repos/${owner}/${name}/pulls/${prView.number}`;

if (prView.state !== "OPEN") fail(2, `PR is ${prView.state}, not OPEN`);
if (prView.headRefOid.toLowerCase() !== review.commit_id.toLowerCase()) {
  fail(
    3,
    `PR head moved: reviewed ${review.commit_id}, current ${prView.headRefOid}. Revalidate the findings against the new head.`,
  );
}

const viewer = await gh(["api", "user", "--jq", ".login"], { raw: true });
const existing = (await collectRest(`${pullPath}/reviews`)).find(
  (item) =>
    item.user?.login === viewer &&
    item.state === state &&
    item.commit_id?.toLowerCase() === review.commit_id.toLowerCase(),
);
if (existing && !values["allow-duplicate"]) {
  fail(
    4,
    `A ${state} review by ${viewer} already exists on ${review.commit_id}: ${existing.html_url}. Pass --allow-duplicate to post another.`,
  );
}

const diffLines = await collectDiffLines();
const anchored = [];
const unanchored = [];
for (const comment of comments) {
  (anchorIsInDiff(comment) ? anchored : unanchored).push(comment);
}

const bodyParts = [review.body?.trim() ?? ""];
if (unanchored.length > 0) {
  bodyParts.push(
    [
      "### Findings outside the diff",
      ...unanchored.map(
        (comment) => `- \`${anchorLabelWithPath(comment)}\` ${comment.body}`,
      ),
    ].join("\n"),
  );
}
const body = bodyParts.filter(Boolean).join("\n\n");
if (!body && review.event !== "APPROVE") {
  fail(2, `${review.event} needs a review body`);
}

const payload = {
  commit_id: review.commit_id,
  event: review.event,
  body,
  comments: anchored.map((comment) => ({
    path: comment.path,
    body: comment.body,
    line: comment.line,
    side: comment.side ?? "RIGHT",
    ...(Number.isInteger(comment.start_line) && {
      start_line: comment.start_line,
      start_side: comment.start_side ?? comment.side ?? "RIGHT",
    }),
  })),
};
if (values["dry-run"]) {
  console.log(
    JSON.stringify(
      {
        dryRun: true,
        payload,
        movedToBody: unanchored.map(anchorLabelWithPath),
      },
      null,
      2,
    ),
  );
  process.exit(0);
}
const submitted = await gh(
  ["api", "--method", "POST", `${pullPath}/reviews`, "--input", "-"],
  { input: JSON.stringify(payload) },
).catch((error) =>
  fail(
    1,
    `Submission failed: ${error.stderr?.trim() || error.message}. Check ${prView.url} for a partially recorded review before retrying.`,
  ),
);

console.log(
  JSON.stringify(
    {
      id: submitted.id,
      url: submitted.html_url,
      state: submitted.state,
      commitId: submitted.commit_id,
      inlineComments: anchored.length,
      movedToBody: unanchored.map(anchorLabelWithPath),
    },
    null,
    2,
  ),
);

function fail(code, message) {
  console.error(message);
  process.exit(code);
}

async function gh(args, { raw = false, input } = {}) {
  const child = execFileAsync("gh", args, { maxBuffer: GH_MAX_BUFFER });
  if (input !== undefined) child.child.stdin.end(input);
  const { stdout } = await child;
  return raw ? stdout.trim() : JSON.parse(stdout);
}

async function collectRest(endpoint) {
  // Page explicitly because older gh releases do not support --slurp.
  const items = [];
  let page;
  do {
    page = await gh([
      "api",
      `${endpoint}?per_page=${PAGE_SIZE}&page=${Math.floor(items.length / PAGE_SIZE) + 1}`,
    ]);
    items.push(...page);
  } while (page.length === PAGE_SIZE);
  return items;
}

// Maps each changed path to the line numbers GitHub accepts as inline anchors:
// every line inside a hunk, on the side where it exists. Files without a patch
// (binary or too large) accept no anchor.
async function collectDiffLines() {
  const lines = new Map();
  for (const file of await collectRest(`${pullPath}/files`)) {
    const sides = { LEFT: new Set(), RIGHT: new Set() };
    lines.set(file.filename, sides);
    if (!file.patch) continue;
    let left = 0;
    let right = 0;
    for (const line of file.patch.split("\n")) {
      const hunk = /^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@/.exec(line);
      if (hunk) {
        left = Number(hunk[1]);
        right = Number(hunk[2]);
        continue;
      }
      // Only prefixed diff records consume lines; a trailing split entry does not.
      if (![" ", "+", "-"].includes(line[0])) continue;
      if (line[0] !== "+") sides.LEFT.add(left++);
      if (line[0] !== "-") sides.RIGHT.add(right++);
    }
  }
  return lines;
}

function anchorIsInDiff(comment) {
  const sides = diffLines.get(comment.path);
  if (!sides) return false;
  const end = sides[comment.side ?? "RIGHT"]?.has(comment.line);
  if (!Number.isInteger(comment.start_line)) return Boolean(end);
  const start = sides[comment.start_side ?? comment.side ?? "RIGHT"]?.has(
    comment.start_line,
  );
  return Boolean(end && start && comment.start_line < comment.line);
}

function anchorLabelWithPath(comment) {
  return `${comment.path}:${anchorLabel(comment)}`;
}

function anchorLabel(comment) {
  return Number.isInteger(comment.start_line)
    ? `${comment.start_line}-${comment.line}`
    : String(comment.line);
}
