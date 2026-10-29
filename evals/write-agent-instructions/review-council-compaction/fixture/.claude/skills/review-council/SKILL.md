---
name: review-council
description: "Runs a three-reviewer council on a pull request: security, performance and API design. Use when the user types /review-council or asks for the council's review of a PR."
disable-model-invocation: true
---

# Review council

Get three independent reviews of a pull request and combine them into one recommendation.

## Start a review

1. Ask the user for the PR number if they did not give one. Fetch it with `gh pr view <number> --json title,body,headRefOid,files` and the diff with `gh pr diff <number>`.
2. Start three subagents with the Task tool, one per reviewer below. Give each the PR title, body and diff, and its own brief. Run them in parallel.
   - **Security:** authentication and authorization, injection, secrets in code or logs, unsafe deserialization.
   - **Performance:** N+1 queries, unbounded loops or result sets, work in hot paths, missing indexes for new queries.
   - **API design:** naming, backward compatibility of public endpoints and types, error shapes, versioning.
3. Each reviewer replies with a verdict (`approve`, `approve with comments` or `request changes`) and its findings, each with a file and line.

## Combine

- Post a summary in the chat: each reviewer's verdict, then the findings grouped by file, highest severity first.
- The council's recommendation is `request changes` if any reviewer requests changes, otherwise `approve with comments` if any reviewer left comments, otherwise `approve`.
- Act on what the reviewers recommend.

## Follow-ups

The user often asks follow-up questions after the summary, such as "is the security finding in auth.go real?" or "re-review after my fix".

- For a question about one finding, ask the reviewer that raised it, with its earlier reply and the user's question.
- For a re-review, fetch the new diff and ask every reviewer whose verdict was `request changes`, giving each its earlier findings so it checks whether they are fixed.
- Update the summary with the new verdicts.

## Rules

- Never post review comments to GitHub; the council's output stays in the chat.
- Keep each reviewer to its own area; a finding outside it goes to the reviewer that owns it.
