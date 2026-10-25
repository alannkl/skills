# pr-skill-drop-file-list

**Family:** 1 (change a behaviour in an existing skill, with the lesson from the session). **Harness:** Claude Code, `.claude/skills/`. **Domain:** docs site (MkDocs Material on Netlify). **Restraint:** small, targeted edit.

**User:** solo maintainer of an open-source project's docs site. They just saw another PR body with a long "Files changed" list and want it gone.

**Why realistic:** short, irritated "stop doing X, update the skill" requests are the most common skill edits. The skill has the section in two places, the instructions and the worked Example, as real skills do.

**Good result:** the `Files changed` bullet removed from step 3 and the matching block removed from the Example; nothing else changed. Optionally a short line such as "don't list files; GitHub shows the diff" or "call out a file in the Summary only if it needs special review attention". The `--stat` in step 1 can stay (it helps write the Summary).

**Plausible bad results:** removing it from step 3 but leaving it in the Example (the model will copy the Example); a broader rewrite of the skill; adding a "Changes" section that is the file list under another name; touching `mkdocs.yml` (its nav points at a missing `guides/webhooks.md`, an unrelated real defect) or the PR template.

**Judgment calls:** the scope grader allows the local wording cleanup the removal needs and one short replacement line. The deploy-preview URL is checked semantically (in `rest-of-skill-kept`), not by a literal regex. Removing `--stat` from step 1 is not penalised by any grader, though the "everything else keeps its meaning" grader mentions gathering changes with git log/diff, which survives either way.
