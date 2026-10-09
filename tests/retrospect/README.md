# Retrospect tests

Run from the repository root:

```bash
python3 -m unittest discover -s tests/retrospect -v
```

Each test builds minimal harness logs in a temporary `$HOME`, shaped after real Claude Code, Codex, Cursor CLI and Antigravity CLI logs, and runs `collect-messages.py` against it. Update the fixtures when a harness changes its log format.
