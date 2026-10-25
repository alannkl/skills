# tally

Shared expense ledger for households, from the terminal.

## Usage

    tally add 12.50 "groceries" --split alex,sam
    tally sync
    tally balance

If sync misbehaves, `tally sync --verbose` prints every request and response.
