# Agent-panel tests

Run from the repository root:

```bash
python3 -m unittest discover -s tests/panel -v
```

The suite uses local fixtures, including disposable Git repositories and subprocesses. It does not call live model services. Tests and their fixtures stay outside the installable `panel/` skill.

`test_continuation.py` covers repeated questions with the same three participants across all presets, shared history, fresh approvals and limits, retained workspaces, stop/reset, failed resumes, crash recovery, version-3 continuation and separate CLI invocations. Chat-message routing and the stop/solo interpretation are host instructions; the offline suite verifies the runner commands they use.

For live testing, use only Claude Sonnet (`sonnet`) and GPT Luna (`gpt-5.6-luna`). Include reasoning effort in the proposed roster before launching. This testing constraint does not restrict models available for normal panel work.

See [validation history](VALIDATION.md) for recorded live checks and limitations.
