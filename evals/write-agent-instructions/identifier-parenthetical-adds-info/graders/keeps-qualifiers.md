---
type: llm
focus: {source: file, path: skills/ship/SKILL.md}
---

Judge the edited `skills/ship/SKILL.md`. Each parenthetical in the original carried information its identifier does not say, so none is a duplicate. Pass only if every fact survives with its meaning: steps run in order; build with `make release`, which needs Docker running and takes about 10 minutes; `deploy.sh` is for production only and staging uses `deploy-staging.sh`; release notes go out with `post_notes` to `#releases`, never `#general`; on any failure, stop and report the failing command and its output. Rewording and dropping pure emphasis are fine. Fail if any fact is lost, weakened, or changed.
