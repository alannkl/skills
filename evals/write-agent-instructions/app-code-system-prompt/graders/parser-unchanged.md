---
type: regex
pattern: '^import\ json\n\n\ndef\ parse_reply\(text:\ str\)\ \->\ dict:\n\ \ \ \ data\ =\ json\.loads\(text\)\n\ \ \ \ return\ \{\n\ \ \ \ \ \ \ \ "summary":\ data\["summary"\],\n\ \ \ \ \ \ \ \ "actions":\ \[\(a\["owner"\],\ a\["task"\]\)\ for\ a\ in\ data\["actions"\]\],\n\ \ \ \ \ \ \ \ "confidence":\ float\(data\["confidence"\]\),\n\ \ \ \ \}\n$'
flags: ''
match: contains
target: {source: file, path: app/parse.py}
---

The parser is byte-for-byte unchanged.
