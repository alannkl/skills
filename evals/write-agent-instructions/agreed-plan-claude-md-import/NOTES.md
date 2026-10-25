# agreed-plan-claude-md-import

**Family:** 2, second turn ("should we X?" answered with a plan, then "ok go ahead"). **Harness:** both: AGENTS.md (Codex users) plus a new CLAUDE.md. **Domain:** Python/FastAPI backend.

**User:** tech lead whose team is split between Codex and Claude Code. The earlier turns are quoted in the instruction; the agent is now the one that proposed the plan.

**Why realistic:** "should we...?" followed by "ok do it" is how many instruction changes actually land. The test is whether the agent executes exactly the agreed plan.

**Good result:** new `CLAUDE.md` containing `@AGENTS.md` (optionally a heading or one-line note); AGENTS.md Setup becomes `uv sync` + `uv run uvicorn app.main:app --reload`; nothing else changes. The Testing section's repetition was explicitly deferred and stays.

**Plausible bad results:** copying AGENTS.md content into CLAUDE.md; also "cleaning up" the Testing section; adding Claude-specific rules; creating a symlink instead of the import (not the agreed plan; fails the regex since the file content would be AGENTS.md's, and fails `claude-md-no-copied-content`); adding a requirements.txt.

**Fixture notes:** the earlier turns are supplied history quoted in `instruction.md`, not a real multi-turn session. `uv.lock` is a stand-in, not a full lock for the declared dependencies; if the agent runs `uv sync` and the lock or `.venv` changes, `only-planned-files-changed` allows it.

**Judgment calls:** the import regex accepts `@AGENTS.md` anywhere not preceded by a word character or slash, so an inline import passes. A symlink deviates from the agreed plan, so failing it is intended.
