---
name: standup
description: Drafts standup bullets from yesterday's merges and the pull requests waiting for my review.
disable-model-invocation: true
---

Summarize what I merged yesterday from git log, list the open pull requests I'm reviewing with `gh pr list --search review-requested:@me`, and draft three standup bullets.
