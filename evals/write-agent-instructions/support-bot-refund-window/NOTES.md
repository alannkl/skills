# support-bot-refund-window

**Family:** 1 (change a behaviour in an existing prompt, with the lesson from a real failure). **Artifact:** system prompt in TypeScript app code. **Domain:** customer-support bot for a meal-kit subscription.

**User:** developer at a small startup who owns the support bot. A customer complaint surfaced that the bot promised a refund outside the monthly window.

**Why realistic:** policy drift between a prompt and the business's real policy is the most common prompt bug in support bots. The fix request is short; the user gives the two numbers.

**Good result:** the refund bullet distinguishes monthly (14 days) from annual (30 days), using the already-interpolated billing interval, or the code computes the window for this customer and states it. Optionally the bot is told what to do outside the window (the policy doc allows opening a request for review), but that is not required. The tool description in `tools.ts` also says "last 30 days" and is read by the model; a careful engineer updates it or at least mentions it. Tests may be extended.

**Plausible bad results:** only changing "30" to "14"; adding both numbers without tying them to the plan interval; rewriting the whole prompt; dropping an interpolation; leaving the tool description contradicting the new rule without a word.

**Judgment calls:** the tools.ts grader accepts either a fix or an accurate flag in the final message, since the user said "the prompt". A fix passes when the description no longer states a flat 30-day window and agrees with 14 monthly / 30 annual; also separating refund eligibility from opening an exception-review request (which the policy allows outside either window) is a welcome extra, not required. All llm graders see `src/bot/**` and the policy doc; edits anywhere under `src/bot/` (e.g. a helper or tests) and to the policy doc are allowed. The 14-day check is semantic, so "fourteen" or a computed value passes.
