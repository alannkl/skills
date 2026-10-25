# should-we-move-endpoint-guide-to-skill

**Family:** 2 ("should we X? if you agree, just do it"). **Harness:** Codex, AGENTS.md + `.agents/skills/`. **Domain:** Go REST API. **Outcome:** most likely "yes, mostly" and a change; a grounded "no" or different organization is also accepted.

**User:** Go developer on a small team; AGENTS.md is loaded every session and half of it is a procedure needed only occasionally.

**Why realistic:** moving a long how-to section out of an always-loaded file into an on-demand skill is a common proposal. The repo already has one skill (`db-migration`) showing the format.

**Good result:** a new `.agents/skills/<name>/SKILL.md` (e.g. `add-endpoint`) with a description that triggers on adding an endpoint, carrying all ten steps with their concrete identifiers; AGENTS.md loses the procedure, keeps everything else, and optionally gets a one-line pointer. The careful part: step 4's rules (WriteError not http.Error, DecodeJSON, auth.FromContext) govern every handler edit, not only new endpoints. A careful engineer keeps those in AGENTS.md (e.g. under Conventions) or makes the skill's description cover handler changes too. The fixture shows why it matters: `ListVehicles` already calls `http.Error` directly, a real unrelated defect.

**Plausible bad results:** moving everything verbatim so handler-wide rules vanish from always-loaded context while the description only says "adding a new endpoint"; summarising steps and losing specifics (max page size 100, RequireRole group, the three test cases); deleting the section from AGENTS.md without creating the skill fully; editing `db-migration`; fixing the `http.Error` call in `vehicles.go` unasked (mentioning it is fine).

**Judgment calls:** the recommendation is graded first (`grounded-verdict`), then whether the files match it (`action-matches-verdict`): agreeing requires the move done; a reasoned disagreement with no writes passes. `all-steps-preserved` judges AGENTS.md and every skill file together, so keeping the handler-wide rules in AGENTS.md does not count as losing them. `handler-rules-still-reachable` accepts three designs for a completed restructuring: rules kept in AGENTS.md, a skill description that covers handler edits, or an AGENTS.md pointer that loads the skill for handler edits. A final-message flag alone does not pass; a recommendation against moving with files intact does. `unchanged_except` allows `.agents/skills/**` because the skill name is the agent's choice.
