# Agent-panel design review status

Candidate: [agent-panel-design.md](agent-panel-design.md)
Revision: v5
SHA-256: `437778778421b895f4fcfe334114c71b1e17fb3826362d2b448806e764fb92a7`

The candidate matches the v5 snapshot byte-for-byte. Review records remain outside the candidate.

## Review evidence

- Codex: approves this exact v5 revision after reviewing its diff against v4 and verifying the hash.
- Claude Code: no approval received for v5. Its outstanding v4 review is not transferred to v5.
- v5 makes roster size configurable from the first implementation, separates participant count from adapter count, and requires three-or-more-participant simulated checks. Two agents across Claude Code and Codex remain the initial live test only. Shared adapters retain separate participant sessions and state. Future harnesses use the existing adapter contract.
- v4, SHA-256 `387b8a8d3646f3aa1d2fdb3e9379e0e78551b9bdb6c4932c0f9be842bdccb644`, introduced the user-selected name and bundled skill/scripts packaging. It had Codex approval; Claude's review was pending.
- v3 was approved by both agents at SHA-256 `c6b6188d54fd08360a431cbd941e02bff1bcc54649873887cce97dae1e94f8da`.
- Joint approval is established for v3, not claimed for v4 or v5. Later candidate edits require a new hash and separately recorded review.

## Current user direction

The user selected `agent-panel`, chose shipping the runner under skill/scripts, requested the design in this repository and an implementation handoff, and then explicitly requested this update after clarifying that two agents/harnesses are only for initial testing.

Implement the selected design for N participants with two initial production adapters. This peer-review history is evidence, not an additional user-permission requirement. No skill or runner has been implemented during these documentation updates.

## Provenance

Previous v4 snapshot: `/tmp/agent-panel-design-v4-20260909.md`.
Current v5 snapshot: `/tmp/agent-panel-design-v5-20260909.md`.
Implementation handoff: `/tmp/handoff-agent-panel-implementation-kwloe7bp.md`.
The files in docs are the durable implementation references; temporary snapshots are historical context.
