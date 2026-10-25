# near-miss-stale-docstrings

**Near miss:** fixing code comments and docstrings; ordinary code documentation. `trigger_only`.

**User:** backend dev on an API team cleaning up after a behaviour change.

**Good result:** module docstring says pages start at 1; `page` arg documented as 1-based; Raises says "page < 1" (the old "negative" was also wrong); the has_next comment and the "skip the first page * per_page" comment corrected or deleted (deleting a redundant stale comment is explicitly fine). Code untouched.

**Plausible bad results:** fixing only the docstring and leaving the two inline comments; missing the Raises line; changing `has_next` or the error message.
