# Spawn-agent tests

Run from the repository root:

```bash
python3 -m unittest discover -s tests/spawn-agent -v
```

`fixtures/` holds real headless output captured from each supported CLI answering "Reply with exactly the word OK", trimmed to the fields the verifier reads. Failure cases are built in the tests by editing those samples. Recapture a fixture when a harness changes its output protocol.
