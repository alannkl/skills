---
type: regex
pattern: '\(`(get_profile|quotes-cli|publish_post)'
flags: ''
match: not_contains
target: {source: file, path: skills/stock-alert/SKILL.md}
---

No tool or command is placed in parentheses after an English label that restates it, such as "Read the profile (`get_profile`)".
