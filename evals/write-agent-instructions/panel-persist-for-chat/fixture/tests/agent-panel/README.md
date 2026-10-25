# Agent-panel tests

Run from the repository root:

```bash
python3 -m unittest discover -s tests/agent-panel -v
```

The suite uses local fixtures, including disposable Git repositories and subprocesses. It does not call live model services. Tests and their fixtures stay outside the installable `agent-panel/` skill.

For live testing, use only Claude Sonnet (`sonnet`) and GPT Luna (`gpt-5.6-luna`). Include reasoning effort in the proposed roster before launching. This testing constraint does not restrict models available for normal panel work.

See [validation history](VALIDATION.md) for recorded live checks and limitations.
