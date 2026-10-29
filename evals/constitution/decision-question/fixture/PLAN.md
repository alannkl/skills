# Eval runner plan

Runs each eval case as a session on the shared agent gateway and collects the transcript for grading.

Decisions: log each one in the table with its date, commit, and push to `main` so the team sees it before the next run.

## Decisions

| ID | Decision | Status | Date |
| --- | --- | --- | --- |
| D9 | Run cases on the shared gateway, not a local one | decided | 2026-10-02 |
| D10 | One worker per gateway, cases run in sequence | decided | 2026-10-02 |
| D11 | Grade from the gateway's stored transcript, not the live stream | decided | 2026-10-06 |
| D12 | Session state between runs: (A) call `sessions.reset` at the start of each run, or (B) create a fresh session per run and delete it afterwards | open | |

## Next

- Settle D12, then run the full suite twice and compare grades.
