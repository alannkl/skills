contract: 1

# How deep-research systems plan, search, stop, grade, and report

## TL;DR

**Question.** How do deep-research products, open-source agents, and published research skills plan, search, decide depth and stopping, grade sources, synthesize, and report?

**Outcome: partial.** Every sub-question is answered across the field, but Perplexity rests on secondary coverage only, OpenAI's ChatGPT surface arrived through relayed quotes, and the report-shape sub-question is thin for Anthropic and Gemini.

**Findings that matter most.**
1. Every system with an orchestrator makes workers return condensed, structured findings and keeps raw material out of the lead's context; two persist evidence to files. The single-agent exception is OpenAI's RL-trained model.
2. Nobody stops on a measured saturation signal alone. Every family pairs a soft judgment ("diminishing returns", "stop when confident") with a hard backstop: tool-call caps, iteration caps, time boxes, or a wall clock. The one numeric quality threshold (source count times average credibility) is in a published skill, not a product.
3. Pre-search user interaction splits by surface, not by vendor. Chat products ask a clarifying question or show a plan; API surfaces default to running immediately; two systems forbid asking the user at all.
4. Source quality is handled by prompt heuristics ("primary over aggregators") in five of seven families. Only one scores credibility numerically, with a hard-coded domain tier list. Separate citation verification exists in two families; the rest cite inline by prompt rule and never check.
5. Summary-first reports are not a consensus. One skill mandates an executive summary; the open-source agent writes paragraph-first with no summary; the products leave shape to the prompt.

**Coverage gaps that limit these findings.** Perplexity is secondary-only (every first-party page returned 403), so its mechanism claims are press and an unsourced teardown. OpenAI's ChatGPT surface arrived through relayed quotes; only the API cookbook was read directly. Anthropic's report-writing guidelines are missing from the published prompt. Gemini publishes behavior, not internals. All performance numbers are vendor self-reported.

## 1. Question and trust

| Field | Value |
| --- | --- |
| shape | field |
| sub-questions | 1 clarification and planning; 2 search strategy and breadth; 3 stop and depth control; 4 source grading and citation; 5 synthesis and report shape; 6 parallelism and delegation; 7 user interaction and delivery |
| date | 2026-10-06 |
| budget | 7 collection units, 1 scout + 7 collectors (Sonnet, Explore), web on |
| selected | anthropic-research (primary), openai-deep-research (primary API, relayed ChatGPT), gemini-deep-research (primary docs/blogs), perplexity-deep-research (secondary only), open-deep-research (primary code), weizhena-skill (primary), biotech-skill (primary) |
| dropped | GPT Researcher (same plan-and-execute family as open_deep_research, weaker clarification); DeerFlow deep-research (methodology only, single agent); ECC, NVIDIA AI-Q, 24601 skills (research method lives in a hosted service); B143KC47 (URL unconfirmed) |
| coverage gaps | SQ5 report shape thin for Anthropic (writing guidelines missing) and Gemini (steerable, no default); SQ7 per-run cost display is a gap in every family except Gemini's pre-run estimates; Perplexity SQ1, SQ3, SQ4 all gaps; dropped families unchecked for counterexamples beyond their scout lines |

Trust by family: Anthropic and open_deep_research are the strongest (published prompts and code, observed implementation). The two skills are primary but prompt-only, so behavior is model-dependent and unmeasured. Gemini and OpenAI API are documented behavior from vendor docs. Perplexity is secondary throughout and its teardown is analyst inference.

## 2. Agreements

Counts are independent families out of seven. Counterexample searches covered all seven records and the dropped candidates' scout lines.

**Decompose the question before searching** (6 of 7; Gemini a gap). Anthropic classifies depth-first, breadth-first, or straightforward and plans 3-5 perspectives [anthropic-research:3]; open_deep_research rewrites the thread into one research brief [open-deep-research:4]; biotech splits 5-10 angles [biotech-skill:6]; Weizhena generates an item and field framework first [weizhena-skill:2]; OpenAI's API "autonomously plans sub-questions" [openai-deep-research:6]; Perplexity "builds a research plan automatically" [perplexity-deep-research:6, secondary]. Counterexample: none.

**Orchestrator with parallel workers returning condensed findings** (5 of 7; OpenAI counterexample; Gemini gap). Anthropic lead spawns 3-5 subagents that return via complete_task, and never delegates the final report [anthropic-research:5, :12]; open_deep_research supervisor runs up to 5 researchers, each compressed before return [open-deep-research:7, :12]; biotech runs 3-5 subagents returning structured evidence objects "to prevent synthesis fatigue" [biotech-skill:7]; Weizhena batches background agents writing one JSON per item [weizhena-skill:6]; Perplexity Computer routes subtasks across models [perplexity-deep-research:5, secondary]. Counterexamples: OpenAI is one RL-trained agent with tools [openai-deep-research:6]; DeerFlow's skill is single-agent (scout line).

**Keep raw material out of the lead's context** (5 of 7). Compression and summarization models [open-deep-research:11, :12], condensed returns [anthropic-research:12], evidence persisted to jsonl because it "must not live only in model context" [biotech-skill:8], per-item files [weizhena-skill:7], filter-in-code before reading [perplexity-deep-research:3, secondary]. Anthropic also recommends subagents write to storage and pass references [anthropic-research:13]. Counterexample: none found; OpenAI and Gemini are gaps.

**Soft stop plus hard backstop** (5 of 7 with a hard cap; Weizhena counterexample; Perplexity gap). Anthropic: "STOP FURTHER RESEARCH" at diminishing returns, under 20 tool calls and about 100 sources per subagent [anthropic-research:7, :8]. open_deep_research: "stop when you can answer confidently" and "last 2 searches returned similar information" in the prompt, 6 supervisor iterations and 10 tool calls in code [open-deep-research:6, :9, :10]. biotech: first-finish thresholds by mode, or a time box [biotech-skill:5]. Gemini: "autonomously determines how much reading and searching is necessary", 60-minute cap [gemini-deep-research:11]. OpenAI: two model tiers and max_tool_calls [openai-deep-research:11, :12 unverified]. Counterexample: Weizhena stops on schema completeness with no caps [weizhena-skill:8].

**Effort scaled to query complexity** (5 of 7). Anthropic's 1 / 2-4 / 10+ subagents [anthropic-research:6]; open_deep_research's "bias towards a single agent", one per comparison element [open-deep-research:8]; biotech's four modes [biotech-skill:4]; Gemini's two tiers [gemini-deep-research:10]; OpenAI's two models [openai-deep-research:11]. Counterexample: Weizhena's effort is set by the user's batch parameters, not inferred.

**Primary sources preferred by prompt heuristic, not score** (5 of 7; biotech counterexample). Anthropic flags aggregators, nameless sources, marketing [anthropic-research:9]; open_deep_research's brief asks for official sites and original papers [open-deep-research:5]; OpenAI's example system message names regulator and peer-reviewed sources [openai-deep-research:9]; Gemini says it was trained to weigh conflicting evidence [gemini-deep-research:13]; Weizhena says "note the credibility" [weizhena-skill:11]. Counterexample: biotech scores 0-100 from hard-coded domain tiers [biotech-skill:9].

**Every claim cited inline** (6 of 7; Weizhena's item JSON has no mandated source field [weizhena-skill:12]). Mechanisms differ; see disagreements.

**Long-form, prose-first report with model-chosen sections** (4 of 7 explicit). open_deep_research: paragraph-first, headings chosen per query type [open-deep-research:14]; biotech: prose at least 80 percent, 4-8 findings [biotech-skill:14]; Gemini and OpenAI: shape steered by prompt [gemini-deep-research:14, openai-deep-research:9]. Anthropic: "the specific format that is best for the user's query" [anthropic-research:17].

**Asynchronous delivery with visible progress** (5 of 7). Gemini background jobs and streamed thought summaries [gemini-deep-research:15]; OpenAI background mode and a steps sidebar [openai-deep-research:10, :13 unverified]; Anthropic checkpoints and resumption [anthropic-research:16]; Weizhena progress display [weizhena-skill:16]; biotech auto-opens files [biotech-skill:15].

## 3. Disagreements

**Ask the user, show a plan, or neither.** ChatGPT clarifies with an intermediate model [openai-deep-research:1, documented behavior]; open_deep_research asks at most one round [open-deep-research:2, :3, observed implementation]; Weizhena confirms at five points [weizhena-skill:5]; Gemini shows a plan for approval in the app and on an opt-in flag in the API [gemini-deep-research:1, :5]. Against: Anthropic's lead prompt says "do not attempt to ask the user questions" [anthropic-research:2]; biotech's autonomy principle says stop only for critical errors [biotech-skill:1]; OpenAI's API "simply starts researching" [openai-deep-research:2]; Gemini's API default is immediate execution. The basis on both sides is observed prompts or documented behavior; neither side cites a measured outcome. The split follows the surface: interactive chat asks, programmatic surfaces do not.

**Where citations are produced.** Anthropic adds them after drafting with a CitationAgent that is rejected if it changes a word [anthropic-research:10]. OpenAI and open_deep_research produce them during generation, as annotations or by prompt rule, with no check [openai-deep-research:8, open-deep-research:15]. biotech checks them afterwards with deterministic scripts [biotech-skill:11, :12]. The Perplexity teardown claims citations are bound before generation [perplexity-deep-research:12, unverified].

**How to stop.** Numeric threshold (biotech) versus similarity saturation (open_deep_research) versus judgment plus cap (Anthropic) versus completeness (Weizhena) versus autonomous plus wall clock (Gemini). Only open_deep_research's "last 2 searches returned similar information" is a saturation test the agent can apply mechanically, and it is a prompt instruction, not code.

**Scoring versus heuristics.** biotech's weighted domain-tier score (observed implementation) against five families' prompt heuristics. Anthropic reports that heuristics fixed a real failure, early agents preferring SEO farms [anthropic-research:9, author-stated].

**Summary-first.** biotech mandates a 200-400 word executive summary [biotech-skill:14]; Weizhena's agent output opens with a 2-3 sentence key-findings summary [weizhena-skill:13]; open_deep_research's prompt has no summary requirement [open-deep-research:14]; the rest are steerable or unknown.

**Lean context: filter before reading or summarize after.** Perplexity's search-as-code filters in a sandbox before the model reads anything [perplexity-deep-research:2, :3, secondary]; open_deep_research reads then summarizes with a cheaper model [open-deep-research:11]. Same goal, opposite order.

## 4. Open questions

- Does any system show the user cost or elapsed time per run? Gemini publishes pre-run estimates; nothing else was found.
- How is a contradiction written up in the final report? Anthropic resolves by recency and consistency; Weizhena skips uncertain values; the others are gaps.
- Current production behavior of claude.ai Research and Perplexity, since the Anthropic post is June 2025 and Perplexity's own pages were unreachable.
- Whether the plan-and-execute family with fixed breadth (GPT Researcher, dropped) performs differently from the adaptive supervisors.

## 5. Per-source detail

One section per collection unit. Each claim line gives sub-question, statement, [location], provenance / basis, and applicability notes.

### anthropic-research

- **identity:** Anthropic multi-agent Research system (claude.ai Research), engineering post Jun 13 2025 (lead Opus 4, subagents Sonnet 4) + anthropic-cookbook patterns/agents/prompts/{research_lead_agent,research_subagent,citations_agent}.md; retrieved 2026-10-06
- **access:** primary (post + example prompts; post calls them "example prompts from our system")
- **limitations:** Jun 2025 description, may differ from 2026 deployment; cookbook prompts are examples not production copies; <writing_guidelines> block missing from lead prompt; metrics self-reported internal; some long lines truncated
- **gaps:** SQ1 partial (no user questions; no plan approval described); SQ4 no numeric scoring; SQ5 thin (writing guidelines missing); SQ7 UI/progress/cost/follow-ups not covered

Claims:

- `anthropic-research:1` SQ1 lead plans, saves plan to Memory (context >200k truncated), then spawns subagents; no clarification or approval step described [post Architecture overview caption] primary / documented behavior
- `anthropic-research:2` SQ1 lead prompt: "No clarifications will be given, therefore use your best judgment and do not attempt to ask the user questions" [research_lead_agent.md final para] primary / observed implementation (example prompt)
- `anthropic-research:3` SQ1 lead classifies query as depth-first / breadth-first / straightforward and plans per type (3-5 perspectives depth-first; non-overlapping boundaries breadth-first) [research_lead_agent.md research_process 2-3] primary / observed implementation
- `anthropic-research:4` SQ2 "start wide, then narrow": short broad queries first; subagent queries under 5 words; web_search then web_fetch on promising URLs [post; research_subagent.md] primary / author-stated rationale
- `anthropic-research:5` SQ2 parallel at two levels: 3-5 subagents in parallel, each 3+ tools in parallel; up to 90% time cut on complex queries; execution synchronous (lead waits per batch) [post Parallel tool calling; Synchronous execution] primary / measured outcome (self-reported)
- `anthropic-research:6` SQ3 effort scaled by complexity: simple fact-finding 1 agent 3-10 calls; comparisons 2-4 subagents 10-15 calls each; complex 10+ subagents [post Scale effort to query complexity] primary / author-stated rationale
- `anthropic-research:7` SQ3 cookbook lead: subagent counts 1 / 2-3 / 3-5 / 5-10, max 20, default 3, at least one; subagent min 5 up to 10 tool calls, hard limit 20 calls / ~100 sources, wrap up ~15 [research_lead_agent.md subagent_count_guidelines; research_subagent.md maximum_tool_call_limit] primary / observed implementation; simple-task budget differs between post and prompt
- `anthropic-research:8` SQ3 stopping judgment-based: STOP at diminishing returns; if time running out write report immediately; no numeric saturation test; early failures: continuing with sufficient results, 50 subagents for simple queries [lead important_guidelines 4; post Think like your agents] primary / observed implementation
- `anthropic-research:9` SQ4 source quality by heuristics not score: flag speculative/future-tense, aggregators, nameless sources, marketing; lead prioritizes primary over aggregators, resolves conflicts by recency and consistency; subagents report unreconciled conflicts; testers found early agents preferred SEO farms [research_subagent.md think_about_source_quality; lead guidelines 2; post Human evaluation] primary / observed implementation
- `anthropic-research:10` SQ4 citations added by separate CitationAgent after research; receives report + sources; may only add citations; rejected if text differs; lead told to include no citations [post caption; citations_agent.md; lead answer_formatting 5] primary / documented behavior
- `anthropic-research:11` SQ4 offline LLM judge 0-1 + pass/fail on factual accuracy, citation accuracy, completeness, source quality, tool efficiency [post LLM-as-judge] primary / author-stated rationale; evaluation not runtime
- `anthropic-research:12` SQ6 lead writes each subagent task with objective, output format, tool/source guidance, boundaries; subagents return condensed findings via complete_task; lead writes final report itself, "NEVER create a subagent to generate the final report"; vague tasks duplicated work [post Teach the orchestrator; lead delegation_instructions, guidelines 5] primary / observed implementation
- `anthropic-research:13` SQ6 tip: subagents write to external storage and pass lightweight references to reduce "game of telephone" [post Appendix] primary / author-stated rationale; whether Research uses it GAP
- `anthropic-research:14` SQ6 lead uses integrations (Drive, Gmail, Slack, Asana) when available; may dedicate one subagent per integration [lead use_available_internal_tools; subagent ALWAYS use internal tools] primary / observed implementation
- `anthropic-research:15` SQ7 agents ~4x chat tokens, multi-agent ~15x; token use explains 80% BrowseComp variance; multi-agent Opus4+Sonnet4 beat single Opus4 by 90.2% internal eval, mainly breadth-first; cost/time display to user not stated [post Benefits] primary / measured outcome (self-reported)
- `anthropic-research:16` SQ7 checkpoints and resumption from error point; tool failures surfaced to agent; rainbow deployments [post Agents are stateful; Deployment] primary / documented behavior
- `anthropic-research:17` SQ5 final report as Markdown via complete_task "in the specific format that is best for the user's query" after reviewing fact list; length/sections/summary-first in missing <writing_guidelines> [lead answer_formatting 1-4] primary / observed implementation; report-shape GAP

### openai-deep-research

- **identity:** OpenAI Deep Research; (A) ChatGPT, launched 2025-02-02 on o3; (B) Deep Research API in Responses, o3-deep-research-2025-06-26 / o4-mini-deep-research-2025-06-26; retrieved 2026-10-06
- **access:** primary for API only (cookbook notebook read in full via raw GitHub); launch post, system card, API guide, help center NOT read (403) -> relayed claims marked unverified
- **limitations:** ChatGPT internals unpublished; cookbook dated to 2025-06-26 snapshots; metrics self-reported
- **gaps:** SQ3 partial (max_tool_calls via paraphrase; no saturation rule); SQ4 no scoring; SQ6 single agentic model, no orchestrator described; SQ2 no counts/parallelism; SQ5 prompt-level only; SQ7 ChatGPT delivery via relay

Claims:

- `openai-deep-research:1` SQ1 ChatGPT "uses an intermediate model (like gpt-4.1) to help clarify your intent" before research [cookbook Clarifying Questions section] primary / documented behavior; ChatGPT mid-2025
- `openai-deep-research:2` SQ1 "the Deep Research API skips this clarification step"; expects fully-formed prompts, will not fill gaps, "simply starts researching" [cookbook same section] primary / documented behavior; API
- `openai-deep-research:3` SQ1 recommended API pattern: gpt-4.1 asks 3-6 clarifying questions ("Prioritize the 3–6 questions that would most reduce ambiguity"), second gpt-4.1 call rewrites answers into researcher instructions ("Do NOT complete the task yourself"), then o4-mini-deep-research [cookbook prompts] primary / documented behavior (example pattern)
- `openai-deep-research:4` SQ1 rewriting prompt: include all user details, no unwarranted assumptions, mark unspecified dimensions open-ended, request tables, explicit output format with headers, match language, name preferred sources [cookbook suggested_rewriting_prompt 1-8] primary / documented behavior
- `openai-deep-research:5` SQ3 vague query makes model cover many scenarios -> "verbosity, higher latency, and increased token usage" [cookbook] primary / author-stated rationale
- `openai-deep-research:6` SQ2 API model "autonomously plans sub-questions, uses tools like web search and code execution, and produces a final structured response"; web_search_preview required; code_interpreter, MCP optional [cookbook Background] primary / documented behavior
- `openai-deep-research:7` SQ2 intermediate steps exposed as typed output items (reasoning summaries, web_search_call with query, code_interpreter_call, mcp_call); reasoning summary via reasoning={"summary":"auto"} [cookbook Inspect Intermediate Steps] primary / documented behavior
- `openai-deep-research:8` SQ4 citations = inline annotations with start_index, end_index, title, url; no automated citation verification mentioned (GAP) [cookbook Access Inline Citations] primary / documented behavior
- `openai-deep-research:9` SQ4,5 source preference and report shape steered by developer system message (peer-reviewed/regulator sources, tables, inline citations, "return all source metadata"; avoid redundant fetch) [cookbook system_message] primary / documented behavior (prompt-level)
- `openai-deep-research:10` SQ7 use background=True for minutes-long tasks [cookbook Getting started] primary / documented behavior
- `openai-deep-research:11` SQ3 o3-deep-research "in-depth synthesis and higher-quality output" vs o4-mini-deep-research "lightweight and faster" [cookbook Background] primary / documented behavior
- `openai-deep-research:12` SQ3 max_tool_calls caps tool usage for cost/latency [Microsoft Foundry docs via summary] unverified / documented behavior (relayed)
- `openai-deep-research:13` SQ7 ChatGPT run 5-30 minutes, sidebar of steps and sources, completion notification [launch post via search quote] unverified / documented behavior
- `openai-deep-research:14` SQ4 outputs "fully documented, with clear citations and a summary of its thinking"; limitations: hallucination at "notably lower rate... according to internal evaluations"; "may struggle with distinguishing authoritative information from rumors"; "weakness in confidence calibration" [launch post via quotes] unverified / author-stated rationale (self-report)
- `openai-deep-research:15` SQ1 ChatGPT Chat: model proposes a research plan user can review and modify; filter websites, add sources; in Work/Codex it asks clarifying questions [help center via summary] unverified / documented behavior (relayed); current help text

### gemini-deep-research

- **identity:** Google Gemini Deep Research; (A) Gemini app, Dec 2024 launch blog; (B) Gemini API Interactions agent deep-research-preview-04-2026 and deep-research-max-preview-04-2026 (Apr 2026 blog + ai.google.dev docs); secondary: philschmid.de Apr 29 2026; retrieved 2026-10-06 via curl
- **access:** primary (docs, two vendor blogs); secondary (Schmid); no code/prompts
- **limitations:** internals unpublished; no planner prompt, query generation, grading rubric, stop rule, or subagent structure; app claims dated Dec 2024; benchmark numbers not extractable; costs self-reported
- **gaps:** SQ2 query generation; SQ3 beyond two tiers + 60-min wall; SQ4 no scoring/citation check; SQ6 structure; SQ1 clarifying questions; SQ5 sections/length

Claims:

- `gemini-deep-research:1` SQ1 app: creates "a multi-step research plan for you to either revise or approve", starts after approval [Dec 2024 blog] primary / documented behavior; app Dec 2024
- `gemini-deep-research:2` SQ2,3 app: iterative browsing, "starting a new search based on what it's learned. It repeats this process multiple times" [Dec 2024 blog] primary / documented behavior; iteration count GAP
- `gemini-deep-research:3` SQ5,7 app: report with links to sources, export to Google Doc, follow-ups; "a few minutes" [Dec 2024 blog] primary / documented behavior
- `gemini-deep-research:4` SQ2,5 app: "agentic system that uses Google's expertise of finding relevant information on the web to direct Gemini's browsing", 1M context [Dec 2024 blog] primary / author-stated rationale
- `gemini-deep-research:5` SQ1 API: agent_config.collaborative_planning=true returns "a proposed research plan instead of executing immediately"; review/modify/approve via multi-turn [docs Collaborative planning] primary / documented behavior; default false, opt-in
- `gemini-deep-research:6` SQ1 API: refine plan via previous_interaction_id with flag kept true; plan returned as text; refinement optional [docs Step 2] primary / documented behavior; no plan schema GAP
- `gemini-deep-research:7` SQ1 API: approve by setting collaborative_planning=False on next turn [docs Step 3] primary / documented behavior
- `gemini-deep-research:8` SQ1 API: approval is flag-driven not conversational: "Simply sending 'go ahead' without flipping the flag will not trigger report generation" [Schmid] secondary / documented behavior
- `gemini-deep-research:9` SQ1 docs recommend collaborative planning for complex queries; blog frames as "granular control over the investigation's scope" [docs Best practices; blog] primary / author-stated rationale; no clarifying-questions mechanism documented (GAP)
- `gemini-deep-research:10` SQ3 two effort tiers: Deep Research (speed, streaming) vs Max ("extended test-time compute to iteratively reason, search and refine", async jobs) [docs Supported versions; blog] primary / documented behavior
- `gemini-deep-research:11` SQ2,3,7 "The agent autonomously determines how much reading and searching is necessary"; vendor estimates ~80 queries/250k in/60k out ($1-3) vs Max ~160 queries/900k in/80k out ($3-7); hard cap 60 min, most <20 min [docs Estimated costs; Limitations] primary / documented behavior (self-reported estimates); no user budget param GAP
- `gemini-deep-research:12` SQ2,6 default tools Google Search, URL Context, Code Execution; restrict/extend with mcp_server, file_search; can turn off web to search private data only; no custom function tools or structured output [docs Supported tools; blog] primary / documented behavior
- `gemini-deep-research:13` SQ4,5 taught "to consult a diverse array of sources and carefully weighing conflicting evidence"; authoritative sources (SEC filings, peer-reviewed); Max "consults significantly more sources"; docs advise reviewing citations and prompting to state unknowns rather than estimate [blog; docs Safety, Best practices] primary / author-stated rationale (self-report; no rubric GAP)
- `gemini-deep-research:14` SQ5 report steerable by prompt (sections, tables, tone); visualization=auto only when prompt asks; outputs "Detailed reports, long-form analysis, comparative tables" [docs Steerability; Visualization] primary / documented behavior; no default template or summary-first GAP
- `gemini-deep-research:15` SQ7 async: background=true + polling, or stream=true with thinking_summaries=auto (thought/text/image deltas), resumable via last_event_id; follow-ups via previous_interaction_id [docs Handling long-running tasks; Streaming; Follow-up] primary / documented behavior; per-run cost display GAP
- `gemini-deep-research:16` SQ7 same infrastructure powers Gemini App, NotebookLM, Search, Finance; Apr 2026 release "replaces our preview release from December" with lower latency/cost [Apr 2026 blog] primary / author-stated rationale

### perplexity-deep-research

- **identity:** Perplexity Deep Research; (A) Feb 2025 feature; (B) "Deep Research, Now in Computer" Jun 2026 on Search as Code + Agentic Search SDK; retrieved 2026-10-06
- **access:** SECONDARY ONLY (all perplexity.ai URLs 403); read: Co-Messi gist (unverified teardown), The Decoder 2026-06-07, arXiv 2506.18096 §4.3, search summaries of MarkTechPost/X/WANDR
- **limitations:** no prompts, code, or docs; gist = analyst inference about legacy pipeline; benchmarks vendor self-reported
- **gaps:** SQ1 plan shown/approved; SQ3 stop rules/caps/modes; SQ4 grading/citation mechanics for B; SQ7 delivery/follow-ups/cost display; SQ6 for A

Claims:

- `perplexity-deep-research:1` SQ2 Computer DR on Agent Search SDK + Search as Code: model writes code assembling the search, "running thousands of retrieval steps, in parallel, tailored to each question" [search summary of Perplexity copy/MarkTechPost] secondary / documented behavior; surface B
- `perplexity-deep-research:2` SQ2 SaC three layers: model decides strategy; sandbox runs generated Python; SDK exposes retrieve/filter/dedupe/rerank functions [The Decoder] secondary / documented behavior
- `perplexity-deep-research:3` SQ2 rationale: conventional query-read-query loop locks filtering in a black box and stuffs context with junk; agent-written filters keep context lean [The Decoder] secondary / author-stated rationale
- `perplexity-deep-research:4` SQ2 CVE example: parallel vendor searches -> self-scan for gaps + targeted follow-ups -> schema-based verification [The Decoder] secondary / observed implementation (single vendor example)
- `perplexity-deep-research:5` SQ6 Computer DR breaks questions into subtasks routed across 20+ frontier models; returns reports, decks, dashboards; reads user files [MarkTechPost 2026-06-11 summary] secondary / documented behavior; merge mechanics GAP
- `perplexity-deep-research:6` SQ1 "builds a research plan automatically... finds primary sources across hundreds of sites and cites every claim" [search summary] secondary / documented behavior (marketing); plan approval GAP
- `perplexity-deep-research:7` SQ3 self-reported: HLE 36.4->50.5, BrowseComp 40.7->83.8; SaC DSQA 0.871 vs Anthropic 0.815 at ~half cost [X thread via summary; The Decoder caveat] secondary / measured outcome (self-reported)
- `perplexity-deep-research:8` SQ7 WANDR benchmark: $5.20/task, 14.9 min median, 3.82M tokens; failure points discovery and complete evidence [MarkTechPost 2026-07-19 summary] secondary / measured outcome (vendor benchmark)
- `perplexity-deep-research:9` SQ2 Feb 2025 DR per survey: decompose into subtasks, successive targeted search rounds adjusted by interim insights, evaluate authoritative sources, structured report [arXiv 2506.18096 §4.3] secondary / documented behavior (paraphrase)
- `perplexity-deep-research:10` SQ2 gist: agentic loop decompose -> per subtopic retrieve/partial synth/scratchpad/gap-find/refine -> cross-source validation -> synthesis [gist §5] unverified / analyst inference
- `perplexity-deep-research:11` SQ3 gist: 3-5 sequential refinement cycles, dozens of searches, hundreds of sources, 2-5 min [gist §5] unverified / analyst inference; contradicts :1 loosely (different surfaces)
- `perplexity-deep-research:12` SQ4 gist: citations bound to retrieved passages before generation; corroborated sources boosted; conflicts presented conditionally with multiple citations [gist §6, §4.5] unverified / analyst inference
- `perplexity-deep-research:13` SQ5 gist: structured report (sections, tables, timelines, uncertainty annotations); standard mode abstains when evidence weak [gist] unverified / analyst inference
- `perplexity-deep-research:14` SQ6 Computer runs subtasks as sub-agents in isolated compute envs (filesystem, browser, tools); Gemini for deep-research sub-agents, Opus 4.6 core (Feb 2026 launch) [Techzine via summary] secondary / documented behavior; may have changed

### open-deep-research

- **identity:** LangChain open_deep_research, main branch (current deep_researcher.py graph; legacy out of scope), README + configuration.py + deep_researcher.py + prompts.py; retrieved 2026-10-06, no SHA pinned
- **access:** primary (code and prompts); LangChain blog not read
- **limitations:** defaults overridable by env/config; prompt "Hard Limits" are soft; utils.py (Tavily, summarization) not read; benchmarks self-reported; legacy variants differ (plan approval, sequential sections)
- **gaps:** SQ4 no credibility scoring or citation verification in files read; SQ5 contradiction handling GAP; SQ7 no per-run cost/time display seen

Claims:

- `open-deep-research:1` SQ1,6 graph: clarify_with_user -> write_research_brief -> research_supervisor -> final_report_generation -> END [deep_researcher.py L708-716] primary / observed implementation
- `open-deep-research:2` SQ1 clarification = one optional structured-output call (need_clarification/question/verification); if true graph ENDs to ask user; else to brief [clarify_with_user L60-116; prompts clarify_with_user_instructions] primary / observed implementation; allow_clarification default True
- `open-deep-research:3` SQ1 clarify prompt: "If you can see... you have already asked a clarifying question, you almost always do not need to ask another one" -> effectively one round [prompts.py] primary / documented behavior
- `open-deep-research:4` SQ1 brief step turns history into a single detailed research question; no plan shown for approval [write_research_brief L118-170; transform_messages prompt] primary / observed implementation; legacy had plan approval per README
- `open-deep-research:5` SQ4 brief prompt pushes source preference at planning: primary/official sites for products, original papers for academic, sources in query language [transform_messages prompt "5. Sources"] primary / observed implementation (prompt)
- `open-deep-research:6` SQ3,6 supervisor loop with tools ConductResearch, ResearchComplete, think_tool; capped at max_researcher_iterations default 6 (1-10); exits on ResearchComplete, cap, or exception [configuration.py; supervisor_tools L247, L334-337] primary / observed implementation
- `open-deep-research:7` SQ2,6 parallel ConductResearch calls via asyncio.gather, capped max_concurrent_research_units default 5 (1-20); overflow gets error ToolMessage to retry with fewer [L291-320] primary / observed implementation
- `open-deep-research:8` SQ3,6 supervisor prompt scaling: bias to single agent; one sub-agent per comparison element; stop when confident; think_tool before/after delegation; no acronyms in delegated questions [lead_researcher_prompt Hard Limits, Scaling Rules] primary / documented behavior (soft)
- `open-deep-research:9` SQ2,3 researcher = ReAct loop, hard cap max_react_tool_calls default 10 (1-30); ends on ResearchComplete or no tool calls, then compress_research [researcher_tools L492, L464, L500] primary / observed implementation
- `open-deep-research:10` SQ2,3 researcher prompt budgets: 2-3 searches simple, up to 5 complex; stop on 3+ relevant sources or "Your last 2 searches returned similar information"; broad then narrow; parallel tool calls within step [research_system_prompt Hard Limits; L479] primary / documented behavior + observed implementation; prompt budget (5) < code cap (10)
- `open-deep-research:11` SQ2,4 raw search results summarized by separate model (gpt-4.1-mini, 8192 out, max_content_length 50000) before researcher sees them; backends Tavily default, OpenAI/Anthropic native, none, + MCP [configuration.py; summarize_webpage_prompt; README] primary / documented behavior
- `open-deep-research:12` SQ5,6,4 compress_research condenses each researcher's messages preserving "all of the relevant statements" with inline citations + Sources list; retries 3 dropping older messages on token limit; returns compressed_research + raw_notes [L511-590; compress prompt Citation Rules] primary / observed implementation
- `open-deep-research:13` SQ6 sub-agents see only their topic; supervisor must give "complete standalone instructions"; compressed findings to supervisor, raw notes aggregated to state [lead prompt Scaling Rules; L296-300] primary / observed implementation
- `open-deep-research:14` SQ5 final_report_generation = one LLM call from brief + history + notes; sections model-chosen (comparison/list/overview examples), paragraph-first, title + ## headings, user's language; no summary-first requirement [final_report_generation_prompt; L607-700] primary / observed implementation
- `open-deep-research:15` SQ4 citations by prompt rule: one number per unique URL, inline, closing "### Sources"; "Citations are extremely important"; no code-level check seen [final_report prompt Citation Rules] primary / observed implementation (prompt)
- `open-deep-research:16` SQ3,5 report generation retries 3 on token limit: truncate findings to model_token_limit*4 chars, then -10% each [L635-682] primary / observed implementation
- `open-deep-research:17` SQ3,6 per-phase models and caps: research/final gpt-4.1 10000; compression gpt-4.1 8192; summarization gpt-4.1-mini 8192; structured-output retries 3 [configuration.py] primary / documented behavior
- `open-deep-research:18` SQ7 delivery via LangGraph Studio/server/Platform/Open Agent Platform; clarification as chat message; report as markdown message; Deep Research Bench 100 tasks ~$20-100, default $45.98 / 58M tokens / RACE 0.4309, "on par with many popular deep research agents" [README] primary / documented behavior; benchmark self-reported; per-query cost display GAP

### weizhena-skill

- **identity:** Weizhena/Deep-Research-skills (Claude Code / OpenCode / Codex prompt skills + web-search subagent), master branch, retrieved 2026-10-06; README cites RhinoInsight arXiv 2511.18743
- **access:** primary (README, skills/research-en/*/SKILL.md, agents/web-search-agent.md, modules, validate_json.py head, codex variant head)
- **limitations:** prompt-only; no benchmarks; Codex variant near-identical
- **gaps:** SQ3 no caps/saturation; SQ4 no scoring, no citation verification; SQ2 no breadth cap beyond 5-10 query variations

Claims:

- `weizhena-skill:1` SQ1 two-phase: outline generation then deep investigation, then report; human-in-the-loop at every stage [README intro] primary / documented behavior
- `weizhena-skill:2` SQ1 /research first generates item list + field framework from model knowledge, no web; AskUserQuestion to confirm items/fields [research/SKILL.md Step 1] primary / observed implementation
- `weizhena-skill:3` SQ1 asks time range and existing field file before web supplement; one background web-search-agent verifies/supplements [research/SKILL.md Step 2-3] primary / observed implementation
- `weizhena-skill:4` SQ1 plan artifact = outline.yaml (items, batch_size, items_per_agent, output_dir) + fields.yaml (categories, fields, detail_level, uncertain list); saved and shown for confirmation [Step 4-5] primary / observed implementation
- `weizhena-skill:5` SQ7 approval points: items/fields, batch params, outline, add-items/add-fields loops, approval before each deep batch, TOC fields at report [multiple SKILL.md] primary / observed implementation
- `weizhena-skill:6` SQ6 /research-deep: resume check skips items with existing JSON; one background agent per items_per_agent in batches of batch_size; verbatim prompt template hard constraint [research-deep/SKILL.md Steps 2-3] primary / observed implementation
- `weizhena-skill:7` SQ3 each item agent writes {item}.json per fields.yaml, marks [uncertain], must run validate_json.py; complete only after validation passes [research-deep prompt template] primary / observed implementation
- `weizhena-skill:8` SQ3 stopping = schema completeness + batch completion; no iteration caps, saturation tests, or budgets; validator "can never pass vacuously" [validate_json.py docstring] primary / analyst inference (absence inferred)
- `weizhena-skill:9` SQ2 search agent: 5-10 query variations; must load a scenario module (github-debug, general-web, academic-papers, chinese-tech, stackoverflow) before any search [agents/web-search-agent.md] primary / observed implementation; Codex agent gpt-5.4 high read-only
- `weizhena-skill:10` SQ2 parallel across items via background agents; README says "one by one" [README vs research-deep] primary / documented behavior
- `weizhena-skill:11` SQ4 qualitative grading: official first; note credibility (official docs vs blog vs maintainer); distinguish official vs community workaround; date-stamp; academic module notes citation counts [web-search-agent QA; modules] primary / documented behavior; no enforcement
- `weizhena-skill:12` SQ4 citations are links: "Sources and References" ALWAYS REQUIRED in agent output; no citation checking [web-search-agent Standard Output] primary / observed implementation
- `weizhena-skill:13` SQ5 contradictions: "note conflicting information and explain differences" in free-form; structured path marks [uncertain] and report SKIPS uncertain values [compilation standards; research-report] primary / observed implementation
- `weizhena-skill:14` SQ5 report = Python script merging item JSONs into report.md with TOC and per-item detail; no LLM narrative synthesis [research-report/SKILL.md Step 3] primary / observed implementation
- `weizhena-skill:15` SQ7 delivery = files (outline.yaml, fields.yaml, results/*.json, report.md) + chat summary (counts, failed/uncertain, dir); follow-ups via /research-add-items, /research-add-fields [research-deep Step 5; README] primary / documented behavior
- `weizhena-skill:16` SQ7 cost/time display not mentioned (GAP); progress display only [research-deep Step 4] primary / analyst inference

### biotech-skill

- **identity:** 199-biotechnologies/claude-deep-research-skill, family: published skill file (Claude Code); main branch, SKILL.md v3.0 evidence-persistence design; retrieved 2026-10-06
- **access:** primary (SKILL.md, reference/methodology.md, quality-gates.md, report-assembly.md, scripts/source_evaluator.py, schemas/*.json)
- **limitations:** prompt-and-script skill; self-reported quality; scripts vs methodology may diverge (research_engine.py not read)
- **gaps:** SQ1 partial (no clarifying questions; plan-for-approval is a GAP); SQ7 partial (follow-ups, cost display GAP); contradiction write-up GAP

Claims:

- `biotech-skill:1` SQ1 autonomy principle: operate independently, infer assumptions, stop only for critical errors; surface high-materiality assumptions in Intro/Methodology [SKILL.md Autonomy Principle] primary / documented behavior
- `biotech-skill:2` SQ1 SCOPE decomposes question, stakeholders, boundaries, success criteria; PLAN builds query strategy + triangulation + quality gates; no plan shown for approval (GAP) [methodology.md Phase 1,2] primary / documented behavior; PLAN skipped in quick mode
- `biotech-skill:3` SQ3 eight phases SCOPE PLAN RETRIEVE TRIANGULATE (4.5 OUTLINE REFINE) SYNTHESIZE CRITIQUE REFINE PACKAGE; phases 3-5 are a per-section evidence loop [SKILL.md Workflow Overview] primary / documented behavior; phase set varies by mode
- `biotech-skill:4` SQ3 four modes: quick 3 phases 2-5 min; standard 6 phases 5-10 min default; deep 8 phases 10-20; ultradeep 20-45 [SKILL.md Decision Tree] primary / documented behavior
- `biotech-skill:5` SQ3 First Finish Search thresholds: quick 10+ sources avg cred>60 or 2 min; standard 15+/>60/5 min; deep 25+/>70/10 min; ultradeep 30+/>75/15 min; remaining searches continue in background [methodology.md FFS] primary / documented behavior; enforcement by script GAP
- `biotech-skill:6` SQ2 decompose into 5-10 independent angles; execute ALL searches in parallel in one message; fetch date first; search-cli preferred, WebSearch fallback [methodology.md Phase 3] primary / documented behavior
- `biotech-skill:7` SQ6 3-5 general-purpose subagents in parallel for paper/doc/repo deep dives (README says 2-3); must return structured evidence objects {claim, evidence_quote, source_url, source_title, confidence} to prevent synthesis fatigue [methodology.md Step 2; README ~48] primary / documented behavior + author-stated rationale
- `biotech-skill:8` SQ4 evidence persistence: sources registered with stable ids; evidence.jsonl spans with evidence_id, locator, quote, evidence_type; "evidence must not live only in model context" [methodology.md Evidence persistence v3.0; schemas/evidence.schema.json] primary / observed implementation
- `biotech-skill:9` SQ4 credibility 0-100 weighted: domain authority .35, expertise .25, recency .20, bias .20; hard-coded domain tiers (arxiv/nature/nih 90; techcrunch/wikipedia/github 70; blogspot/substack 40; unknown 55); labels >=80 high, >=60 moderate, >=40 low, else verify [scripts/source_evaluator.py] primary / observed implementation
- `biotech-skill:10` SQ4 flag <40 for extra verification, prioritize >80 for core claims; 3+ source types; core claims need 3+ independent sources; single-source flagged [methodology.md Quality Standards, TRIANGULATE] primary / documented behavior; primary-vs-secondary grading GAP
- `biotech-skill:11` SQ4 claims.jsonl with claim_type and support_status; verify_claim_support.py deterministic lexical/entity/number/date checks, no LLM; only factual claims hard-fail [schemas/claim.schema.json; verify_claim_support.py] primary / observed implementation
- `biotech-skill:12` SQ4 verify_citations.py (DOI, title/year); validate_report.py 9 checks (summary 200-400 words, sections, [N] cites, bibliography match, 500-10000 words, 10+ sources, links); loop retries up to 3 then reports; web content quoted as data never instructions [quality-gates.md] primary / documented behavior; internal count inconsistencies
- `biotech-skill:13` SQ3 Phase 4.5 revises outline when evidence contradicts scope (<=50% restructure, 2-3 searches, 2-5 min); CRITIQUE with 2-3 personas; critical gap loops back to RETRIEVE with delta queries, 3-5 min; no global iteration cap beyond time boxes (GAP) [methodology.md 4.5, Phase 6] primary / documented behavior
- `biotech-skill:14` SQ5 report: Executive Summary 200-400 words, Introduction (scope, methodology, assumptions), 4-8 findings 600-2000 words each, Synthesis, Limitations, Recommendations, Bibliography, Methodology Appendix; prose-first >=80%; length by mode 2k-20k+ words [SKILL.md Output Contract; report-assembly.md] primary / documented behavior
- `biotech-skill:15` SQ7 delivery by file: ~/Documents/[Topic]_Research_[date]/ markdown + sources/evidence/claims jsonl + run_manifest + HTML + PDF auto-opened [SKILL.md Output files] primary / documented behavior
- `biotech-skill:16` SQ6 sections written one at a time (<=2000 words) for the 32k output limit; >18k words triggers recursive continuation agents with state on disk [report-assembly.md; README ~61] primary / author-stated rationale

## 6. Sources

Every URL read or relayed, per unit. Retrieval date 2026-10-06 throughout.

**anthropic-research** (primary)
- https://www.anthropic.com/engineering/multi-agent-research-system
- https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/patterns/agents/prompts/research_lead_agent.md
- https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/patterns/agents/prompts/research_subagent.md
- https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/patterns/agents/prompts/citations_agent.md

**openai-deep-research** (primary for the API cookbook; the rest relayed through search summaries, not fetched)
- https://raw.githubusercontent.com/openai/openai-cookbook/main/examples/deep_research_api/introduction_to_deep_research_api.ipynb (read)
- https://openai.com/index/introducing-deep-research/ (relayed)
- https://openai.com/index/deep-research-system-card/ (not read)
- https://platform.openai.com/docs/guides/deep-research (relayed)
- https://help.openai.com/en/articles/10500283-deep-research-in-chatgpt (relayed)
- https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/deep-research (relayed, max_tool_calls)

**gemini-deep-research** (primary docs and blogs; one secondary)
- https://ai.google.dev/gemini-api/docs/deep-research
- https://blog.google/innovation-and-ai/models-and-research/gemini-models/next-generation-gemini-deep-research/
- https://blog.google/products/gemini/google-gemini-deep-research/
- https://www.philschmid.de/deep-research-update (secondary)

**perplexity-deep-research** (secondary only; every perplexity.ai URL returned 403)
- https://www.perplexity.ai/hub/products/deep-research (403)
- https://www.perplexity.ai/hub/blog/deep-research-now-in-computer (403)
- https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research (403)
- https://research.perplexity.ai/articles/rethinking-search-as-code-generation (403)
- https://the-decoder.com/perplexitys-search-as-code-lets-ai-models-write-their-own-search-pipelines-instead-of-calling-fixed-apis/ (read)
- https://arxiv.org/html/2506.18096 section 4.3 (read)
- https://gist.github.com/Co-Messi/bfcfb39eede5c6bc2fadd2c04139a136 (read; unverified teardown)
- https://www.marktechpost.com/2026/06/11/perplexity-moves-deep-research-into-computer-routing-research-subtasks-across-20-frontier-models-for-reports-decks-and-dashboards/ (relayed)
- https://www.techzine.eu/news/infrastructure/139169/perplexity-computer-assigns-tasks-to-ai-agents/ (relayed)

**open-deep-research** (primary code, `main` branch, no SHA pinned)
- https://github.com/langchain-ai/open_deep_research
- https://raw.githubusercontent.com/langchain-ai/open_deep_research/main/README.md
- https://raw.githubusercontent.com/langchain-ai/open_deep_research/main/src/open_deep_research/configuration.py
- https://raw.githubusercontent.com/langchain-ai/open_deep_research/main/src/open_deep_research/deep_researcher.py
- https://raw.githubusercontent.com/langchain-ai/open_deep_research/main/src/open_deep_research/prompts.py

**weizhena-skill** (primary, `master` branch)
- https://github.com/Weizhena/Deep-Research-skills
- https://raw.githubusercontent.com/Weizhena/Deep-Research-skills/master/README.md
- https://raw.githubusercontent.com/Weizhena/Deep-Research-skills/master/skills/research-en/ (research, research-deep, research-report, research-add-items, research-add-fields SKILL.md; research/validate_json.py)
- https://raw.githubusercontent.com/Weizhena/Deep-Research-skills/master/agents/web-search-agent.md
- https://raw.githubusercontent.com/Weizhena/Deep-Research-skills/master/agents/web-search-modules/ (general-web.md, academic-papers.md)
- https://raw.githubusercontent.com/Weizhena/Deep-Research-skills/master/agents-codex/web-researcher.toml

**biotech-skill** (primary, `main` branch)
- https://github.com/199-biotechnologies/claude-deep-research-skill
- https://raw.githubusercontent.com/199-biotechnologies/claude-deep-research-skill/main/SKILL.md
- https://raw.githubusercontent.com/199-biotechnologies/claude-deep-research-skill/main/reference/ (methodology.md, quality-gates.md, report-assembly.md)
- https://raw.githubusercontent.com/199-biotechnologies/claude-deep-research-skill/main/scripts/ (source_evaluator.py, verify_claim_support.py)
- https://raw.githubusercontent.com/199-biotechnologies/claude-deep-research-skill/main/schemas/ (evidence.schema.json, claim.schema.json)
