# near-miss-rename-flag-docs

**Near miss:** a small code change plus contributor/user docs; the repo has an AGENTS.md but nothing in the request touches it. `trigger_only`.

**User:** maintainer of a small Go CLI.

**Good result:** `BoolVarP(&verbose, "debug", "v", false, ...)` (variable rename optional), README line uses `--debug`, CONTRIBUTING says `tally sync -v` (or `--debug`). AGENTS.md untouched.

**Plausible bad results:** forgetting CONTRIBUTING's parenthetical `--verbose`; dropping the `-v` shorthand; editing AGENTS.md.

**Judgment calls:** a rename note mentioning `--verbose` passes; only instructing users to use it fails. `syncer.Options{Verbose: ...}` lives in `internal/` (not in the fixture); renaming that field is allowed but not required, so `internal/**` is in the allow list. `go build` can't run here because `internal/syncer` is not in the fixture; graders judge the source.
