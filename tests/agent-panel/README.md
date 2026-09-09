# Agent-panel tests

Run from the repository root:

```bash
python3 -m unittest discover -s tests/agent-panel -v
```

The suite uses local fixtures, including disposable Git repositories and subprocesses. It does not call live model services. Tests and their fixtures stay outside the installable `agent-panel/` skill.

See [validation history](VALIDATION.md) for recorded live checks and limitations.
