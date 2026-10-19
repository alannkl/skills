---
type: llm
---

`docs/releasing.md` cites step 3 of the release-notes skill as the tag check, and the user authorized edits in the workspace. Pass if the final message shows the tag check is still step 3, or that the agent updated `docs/releasing.md` to match the new numbering or to refer to the check by name. Fail if it renumbered the steps and only flagged the doc, or did not mention it.
