# Code-review tests

Run from the repository root:

```bash
python3 -m unittest discover -s tests/code-review -v
```

The suite runs `resolve-scope.py` against disposable Git repositories with a local bare remote, covering each rung of the fallback chain, explicit ranges, the empty-scope exit code, file flags, renames and untracked content in the retained patch, and guidance discovery from the base revision rather than the working tree.
