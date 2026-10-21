---
type: llm
---

The review compares the background refresh thread with a simpler alternative, such as `TTLValue` from `app/cache.py`, which refreshes the cached flags on lookup once they are older than 30 s. It states at least one real cost of each option and recommends one with a reason; recommending to keep the thread passes. It does not describe the alternative as having no disadvantage. A recommendation to adopt `TTLValue` notes that it drops the change's keep-last-known-flags behavior when a refresh fails, or counts the handling needed to keep it as a cost.
