---
type: regex
pattern: '## Release <version>[\s\S]*### Added[\s\S]*### Fixed[\s\S]*### Breaking'
flags: i
match: contains
target: {source: file, path: release-notes/SKILL.md}
---

The consumer-required heading format survives in order.
