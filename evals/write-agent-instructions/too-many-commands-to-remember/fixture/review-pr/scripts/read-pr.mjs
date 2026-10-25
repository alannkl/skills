#!/usr/bin/env node

// Reads an open PR and the authenticated viewer, then collects its comments.
// Every collection is paginated to the end; page counts and retrieval failures
// stay in the JSON file so incomplete coverage remains visible.

import { execFile } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import { parseArgs, promisify } from "node:util";

const execFileAsync = promisify(execFile);
const GH_MAX_BUFFER = 256 * 1024 * 1024;
const PAGE_SIZE = 100;

const usage = `Usage: node read-pr.mjs <pr-number|pr-url> [--repo <owner/name>] [--out <file>]

Writes one JSON file with PR metadata, the viewer's login, discussion comments,
review summaries, and inline review threads (including replies, resolution,
and outdated status). Collections include page counts and retrieval failures.
Prints the file path on stdout. Open drafts are accepted.
Exits 0 for complete coverage, 1 for incomplete comment coverage, 2 when the PR
or viewer cannot be read, and 3 for a closed or merged PR. Exits 2 and 3 do not
write a file. Requires an authenticated gh CLI.`;

const { values, positionals } = parseArgs({
  options: {
    repo: { type: "string" },
    out: { type: "string" },
    help: { type: "boolean", short: "h" },
  },
  allowPositionals: true,
});
if (values.help || positionals.length !== 1) {
  console.error(usage);
  process.exit(values.help ? 0 : 2);
}

const COMMENT_PAGE_FRAGMENT = `
fragment CommentPage on PullRequestReviewCommentConnection {
  pageInfo { hasNextPage endCursor }
  nodes {
    id url createdAt updatedAt outdated body
    author { login __typename }
    pullRequestReview { state }
  }
}`;
const THREADS_QUERY = `query($owner: String!, $name: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: ${PAGE_SIZE}, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id path line startLine originalLine diffSide isResolved isOutdated
          resolvedBy { login }
          comments(first: ${PAGE_SIZE}) { ...CommentPage }
        }
      }
    }
  }
}${COMMENT_PAGE_FRAGMENT}`;
const THREAD_COMMENTS_QUERY = `query($id: ID!, $cursor: String) {
  node(id: $id) {
    ... on PullRequestReviewThread {
      comments(first: ${PAGE_SIZE}, after: $cursor) { ...CommentPage }
    }
  }
}${COMMENT_PAGE_FRAGMENT}`;

const prViewArgs = [
  "pr",
  "view",
  positionals[0],
  "--json",
  "number,url,title,body,state,isDraft,author,baseRefName,headRefName,headRefOid,headRepositoryOwner,headRepository,isCrossRepository,mergeStateStatus",
];
if (values.repo) prViewArgs.push("--repo", values.repo);
const prView = await gh(prViewArgs).catch((error) => {
  console.error(`Cannot read the PR: ${ghError(error)}`);
  process.exit(2);
});
if (prView.state !== "OPEN") {
  console.error(
    `PR #${prView.number} is ${prView.state}; only OPEN PRs are reviewable.`,
  );
  process.exit(3);
}
const viewer = await gh(["api", "user"])
  .then((user) => {
    if (typeof user.login !== "string" || !user.login.trim()) {
      throw new Error("The authenticated user has no login.");
    }
    return user.login;
  })
  .catch((error) => {
    console.error(
      `Cannot read the viewer: ${ghError(error)}`,
    );
    process.exit(2);
  });
const repoMatch = /github\.com\/([^/]+)\/([^/]+)\/pull\/\d+/.exec(prView.url);
if (!repoMatch) {
  console.error(`Cannot derive the repository from the PR URL: ${prView.url}`);
  process.exit(2);
}
const [, owner, name] = repoMatch;
const prPath = `repos/${owner}/${name}`;
const failures = [];

const discussion = await attempt("discussion", () =>
  collectRest(
    `${prPath}/issues/${prView.number}/comments`,
    normalizeDiscussionComment,
  ),
);
const reviews = await attempt("reviews", () =>
  collectRest(`${prPath}/pulls/${prView.number}/reviews`, normalizeReview),
);
const threads = await attempt("threads", collectThreads);

const outFile = values.out
  ? path.resolve(values.out)
  : path.join(
      os.homedir(),
      ".tmp",
      "review-pr",
      `pr-${prView.number}-${new Date().toISOString().replace(/[:.]/g, "-")}.json`,
    );
await mkdir(path.dirname(outFile), { recursive: true });
await writeFile(
  outFile,
  `${JSON.stringify(
    {
      collectedAt: new Date().toISOString(),
      pr: {
        ...prView,
        repo: `${owner}/${name}`,
      },
      viewer,
      discussion,
      reviews,
      threads: {
        ...threads,
        commentCount: threads.items.reduce(
          (total, thread) => total + thread.comments.length,
          0,
        ),
      },
      failures,
    },
    null,
    2,
  )}\n`,
);

console.error(
  `discussion: ${discussion.count} (${discussion.pages} pages); reviews: ${reviews.count} (${reviews.pages} pages); threads: ${threads.count} (${threads.pages} pages); failures: ${failures.length === 0 ? "none" : failures.join(", ")}`,
);
console.log(outFile);
process.exit(failures.length === 0 ? 0 : 1);

// gh prints HTTP status on stderr but GitHub's reason in the response body on
// stdout; keep both so a permanent failure reads differently from a transient one.
function ghError(error) {
  const status = error.stderr?.trim() || error.message;
  try {
    const { message, errors } = JSON.parse(error.stdout);
    const reasons = (errors ?? []).map((item) =>
      typeof item === "string"
        ? item
        : (item?.message ?? JSON.stringify(item)),
    );
    return [status, ...(reasons.length ? reasons : [message])]
      .filter(Boolean)
      .join(": ");
  } catch {
    return status;
  }
}

async function gh(args) {
  // PR URLs select github.com; API calls must ignore any ambient GH_HOST.
  if (args[0] === "api") args = [...args, "--hostname", "github.com"];
  const { stdout } = await execFileAsync("gh", args, {
    maxBuffer: GH_MAX_BUFFER,
  });
  return JSON.parse(stdout);
}

async function graphql(query, variables) {
  const args = ["api", "graphql", "-f", `query=${query}`];
  for (const [key, value] of Object.entries(variables)) {
    if (value === undefined) continue;
    args.push(typeof value === "number" ? "-F" : "-f", `${key}=${value}`);
  }
  return (await gh(args)).data;
}

// Runs one collection to completion; a failure is recorded in the file and
// leaves the collection empty rather than aborting the other collections.
async function attempt(collection, collect) {
  try {
    const { pages, items } = await collect();
    return { count: items.length, pages, error: null, items };
  } catch (error) {
    failures.push(collection);
    const detail = ghError(error);
    console.error(`${collection}: retrieval failed: ${detail}`);
    return { count: 0, pages: 0, error: detail, items: [] };
  }
}

async function collectRest(endpoint, normalize) {
  // Page explicitly because older gh releases do not support --slurp.
  const items = [];
  let pages = 0;
  let page;
  do {
    page = await gh([
      "api",
      `${endpoint}?per_page=${PAGE_SIZE}&page=${pages + 1}`,
    ]);
    pages += 1;
    items.push(...page.map(normalize));
  } while (page.length === PAGE_SIZE);
  return { pages, items };
}

async function collectThreads() {
  const items = [];
  let pages = 0;
  let cursor;
  do {
    const data = await graphql(THREADS_QUERY, {
      owner,
      name,
      number: prView.number,
      cursor,
    });
    const connection = data.repository.pullRequest.reviewThreads;
    pages += 1;
    for (const thread of connection.nodes) {
      const comments = [...thread.comments.nodes];
      let commentPage = thread.comments.pageInfo;
      while (commentPage.hasNextPage) {
        const more = await graphql(THREAD_COMMENTS_QUERY, {
          id: thread.id,
          cursor: commentPage.endCursor,
        });
        pages += 1;
        comments.push(...more.node.comments.nodes);
        commentPage = more.node.comments.pageInfo;
      }
      items.push(normalizeThread(thread, comments));
    }
    cursor = connection.pageInfo.hasNextPage
      ? connection.pageInfo.endCursor
      : undefined;
  } while (cursor);
  return { pages, items };
}

function normalizeDiscussionComment(comment) {
  return {
    id: comment.id,
    url: comment.html_url,
    author: comment.user?.login ?? null,
    authorType: comment.user?.type ?? null,
    createdAt: comment.created_at,
    updatedAt: comment.updated_at,
    body: comment.body ?? "",
  };
}

function normalizeReview(review) {
  return {
    id: review.id,
    url: review.html_url,
    author: review.user?.login ?? null,
    authorType: review.user?.type ?? null,
    state: review.state,
    submittedAt: review.submitted_at ?? null,
    commitId: review.commit_id ?? null,
    body: review.body ?? "",
  };
}

function normalizeThread(thread, comments) {
  return {
    id: thread.id,
    path: thread.path,
    line: thread.line,
    startLine: thread.startLine,
    originalLine: thread.originalLine,
    diffSide: thread.diffSide,
    isResolved: thread.isResolved,
    isOutdated: thread.isOutdated,
    resolvedBy: thread.resolvedBy?.login ?? null,
    comments: comments.map((comment) => ({
      id: comment.id,
      url: comment.url,
      author: comment.author?.login ?? null,
      authorType: comment.author?.__typename ?? null,
      createdAt: comment.createdAt,
      updatedAt: comment.updatedAt,
      outdated: comment.outdated,
      reviewState: comment.pullRequestReview?.state ?? null,
      body: comment.body ?? "",
    })),
  };
}
