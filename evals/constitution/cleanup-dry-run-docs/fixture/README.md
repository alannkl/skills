# report-exporter

Exports monthly client-hours reports as CSV files in `exports/`.

## Usage

```sh
npm run export
```

Writes `exports/report-YYYY-MM.csv` for the current month.

```sh
npm run cleanup -- --days 60
```

Deletes files in `exports/` last modified more than `--days` days ago (default 30).
