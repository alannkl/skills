# should-we-split-claude-md

**Family:** 2 ("should we X? if you agree, do it"). **Harness:** Claude Code, CLAUDE.md. **Domain:** web app (Django monolith). **Restraint:** likely; the best-grounded answer is "not now", but a justified split is authorized and accepted if it keeps shared rules reachable.

**User:** team lead on a 4-5 person team. The CLAUDE.md has grown over a few months and feels big; they have heard nested CLAUDE.md files exist and wonder whether to use them.

**Why realistic:** "should we split our CLAUDE.md?" comes up as soon as one passes a screenful. The file here is about 70 lines.

**Good result:** a short answer that recognizes nearly every section applies across all three apps (commands, style rules, test rules, migration rules, Celery rules, git rules), so per-app files would either duplicate these or hide them when the agent works in another app, and ~70 lines is not large. The most likely good verdict is "not now; revisit if app-specific guidance accumulates", possibly suggesting trimming or pointing out the stale `Python 3.10+` line (pyproject says >=3.12). Because the user said "if you think it makes sense go for it", a split the agent justifies is also acceptable, provided shared rules stay in the root file (or another always-loaded place) and nothing is lost or duplicated.

**Plausible bad results:** creating `apps/billing/CLAUDE.md` etc. with shared rules moved there (Money and timezone rules apply everywhere; the large-table migration note names billing tables but governs migration work from anywhere), so they no longer load when working in other apps; copying the same rules into several per-app files; a vague "it depends" with no verdict; claiming problems the file does not have.

**Judgment calls:** no verdict is forced; the graders check that the recommendation reads the file's scope correctly, is grounded in it, and that any restructuring keeps every rule reachable where it applies without duplication. `unchanged_except` allows only CLAUDE.md files (root and nested). The accuracy grader sees CLAUDE.md and pyproject.toml and fails only invented problems; it does not require mentioning the Python version.
