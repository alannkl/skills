# Skill-eval tests

Run from the repository root:

```bash
python3 -m unittest discover -s tests/skill-eval -v
```

The suite covers task generation, the host-side graders, grading a trial from its saved files, reuse of earlier trials, and the rule map with its minus-one-rule copies and table. No agent or judge is called; the judge is replaced in the test that needs it.

`fixtures/` holds real logs from one Claude Code, one Codex and one OpenClaw run of a `shorten-it` case, trimmed to the fields the evidence extractors read. Recapture a fixture when a harness changes its log format.
