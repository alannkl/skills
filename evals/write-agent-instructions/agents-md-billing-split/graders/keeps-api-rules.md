---
type: regex
pattern: '/v2/[\s\S]*openapi\.yaml|openapi\.yaml[\s\S]*/v2/'
flags: i
match: contains
target: {source: file, path: AGENTS.md}
---

Both API rules stay in the root file.
