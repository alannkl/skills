---
type: regex
pattern: '^\#\ Release\ checklist\n\n\#\#\ Before\ tagging\n\n\-\ Update\ `CHANGELOG\.md`\ with\ every\ merged\ pull\ request\ since\ the\ last\ tag\.\n\-\ Bump\ the\ version\ in\ `package\.json`\.\n\n\#\#\ Rollback\n\n1\.\ Run\ `deploy\.sh\ production\ \-\-version\ <previous\ tag>`\.\n2\.\ Confirm\ the\ health\ check\ at\ `/healthz`\ returns\ 200\.\n3\.\ Open\ an\ incident\ issue\ labelled\ `release\-rollback`\.\n$'
flags: ''
match: contains
target: {source: file, path: skills/release/references/checklist.md}
---

The checklist reference is byte-for-byte unchanged.
