# Skill-eval tests

Run from the repository root:

```bash
python3 -m unittest discover -s tests/eval-agent-instructions -v
```

The suite covers task generation, the host-side graders, grading a trial from its saved files, reuse of earlier trials, the token counts of loaded texts, and the rule map with its minus-one-rule copies and table. No agent, judge or token-counting endpoint is called; each is replaced in the test that needs it.

`fixtures/` holds real logs from one Claude Code, one Codex and one OpenClaw run of a `shorten-it` case, trimmed to the fields the evidence extractors read. Recapture a fixture when a harness changes its log format.
