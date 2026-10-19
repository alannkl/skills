---
type: regex
pattern: '^\-\-\-\nname:\ base\ndescription:\ Working\ rules\ for\ every\ coding\ task\ in\ this\ repository\.\n\-\-\-\n\n\#\ Base\ rules\n\n\-\ Run\ the\ test\ suite\ before\ you\ commit\.\n\-\ Never\ commit\ secrets;\ read\ them\ from\ environment\ variables\.\n\-\ Keep\ each\ commit\ to\ one\ logical\ change\.\n\-\ Ask\ before\ deleting\ files\ you\ did\ not\ create\.\n$'
flags: ''
match: contains
target: {source: file, path: skills/base/SKILL.md}
---

The base skill is byte-for-byte unchanged.
