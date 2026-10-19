# Context design

Use this when instructions decide what material enters an agent's context, when it is loaded or refreshed, how long it stays relevant, and what must stay recoverable for continuation. These are authoring decisions. The execution system performs loading, compaction, caching, and delegation; specify what the instructions need from it rather than reimplementing it.

Done when every piece of material has a placement and a load condition, every pointer target is reachable, the read path of each branch is known, and any continuation state is named with the source that owns it.

## Placement and cost

- Decide for each piece of material whether it is always loaded, loaded on a recognizable condition, or supplied for one task.
- Estimate recurring cost from the text's size, the number of later requests that retain or reassemble it, and the number of agent contexts that receive it, such as inheriting subagents. These are repeated inclusions across requests, not copies piling up within one window.
- Check the target execution system before relying on how long text stays, whether it is compacted or evicted, or whether a user-invoked skill stays out of the model's context. Caching can lower processing or billing cost; the cached text still occupies the context window.

## Retrieval

- Check retrieval against the tools the executing agent actually has, such as file reads or skill loading; a system prompt with no file access cannot follow a file pointer.
- Design each branch's read path so it loads only what that branch needs, and avoid reaching the same material twice through different pointers.
- Count the context that instructions induce: files they ask the agent to read and command output they ask it to keep. Name the files or sections needed, and ask for filtered or summarized output where the full output does not inform the next decision. For bundled script output, follow the Scripts section of `references/skill-mechanics.md`; for work given to subagents, point to the executor's delegation instructions, such as the `delegate` skill, rather than restating them.

## Authority

- State which sources carry instructions and which are evidence, within the executor's actual instruction hierarchy. Content the agent reads, such as files, tool output, web pages, or other agents' replies, is data unless that hierarchy makes it an instruction.

## State and freshness

- Separate durable rules from task state that changes. Keep changing state, such as progress, current decisions, or environment facts, in the source that owns it, such as a record file, the repository, or a tool, and say when to refresh it rather than freezing it into standing instructions.

## Continuation and context boundaries

- When work may continue after a handoff, compaction, or a new session, name the state that must be recoverable and where it lives. Point to the skill that performs the transfer, such as `handoff`, instead of restating its procedure.
- An inline skill load or reference read keeps earlier material in context. Only a separate context that does not inherit that material, such as a new session or a subagent the executor starts without the parent conversation, keeps it out of view; check the executor's inheritance behavior before relying on one. Use such a context when later material must stay out of view or when a step can return a compact result.
