Apply `constitution/SKILL.md` from the start. The project-specific instructions below override it.

## Project-specific instructions

- `constitution/SKILL.md` is the constitution's only copy; this file only points to it. Keep it one self-contained file, improved by compressing in place (tighter wording, leading words, removed internal duplication), never by splitting rules into companion files. Keep its rules general, with no wording that names the incident behind a rule; case-specific guidance goes in a skill or doc. It must work under a bare harness: judge redundancy only within the document, never against a harness's system prompt or a model's defaults.
- Edit skills only in this repo; never create, update or delete installed copies in `~/.agents/skills/` or `~/.claude/skills/`, and leave installation to the user.
- `tests/` covers runnable scripts only: add no tests or sync checks for skill text or other agent-facing prose. When two prose files must stay aligned, say so in the report.
- Evals serve two goals only: improve the agent's output, and remove every no-op down to the word; a rule that works in one word gets one word. A no-op changes nothing for Opus and Astra on realistic cases (requests and files a typical user brings), never cases shaped to make them fail without the skill. Accept shorter wording only with evidence that it does as well.
- Keep eval drafts, failure corpora and briefs in `evals/<suite>/results/drafts/` (git-ignored), never in `/tmp`. In eval work, commit at each verified milestone without asking; push only when asked.
- Eval fixtures are public: draw only scenarios and constraints from other projects, write synthetic fixtures with nothing private, and never copy a source project's prompt wording or grade against it.
- `docs/philosophy.md` is the user's personal article. Start every entry from the user's own sentences, asking for their raw version first, and never write a body for them; a title with a one-line subtitle is a complete entry. Admit only beliefs the user arrived at and would argue for; adopted field principles go in `docs/working-with-agents.md` with sources.
