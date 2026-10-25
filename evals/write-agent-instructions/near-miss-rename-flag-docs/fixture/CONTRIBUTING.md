# Contributing to tally

Thanks for helping out!

## Reporting bugs

Open an issue with your OS, `tally --version`, and what you expected. For sync problems, run `tally sync -v` (or `--verbose`) and paste the output, with any amounts redacted.

## Development

    go build ./...
    go test ./...

Run `gofmt -w .` before pushing. One feature per PR.
