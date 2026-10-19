---
type: regex
pattern: '^from\ app\.parse\ import\ parse_reply\n\n\ndef\ test_parse_reply\(\):\n\ \ \ \ reply\ =\ ''\{"summary":\ "Agreed\ the\ launch\ date\.",\ "actions":\ \[\{"owner":\ null,\ "task":\ "Book\ the\ room"\}\],\ "confidence":\ 0\.8\}''\n\ \ \ \ assert\ parse_reply\(reply\)\["actions"\]\ ==\ \[\(None,\ "Book\ the\ room"\)\]\n$'
flags: ''
match: contains
target: {source: file, path: tests/test_parse.py}
---

The test is byte-for-byte unchanged.
