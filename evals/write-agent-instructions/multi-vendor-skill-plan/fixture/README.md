# Market agent platform

Runs research agents for retail investors. Each agent session gets the skills in `skills/` and posts a daily brief to the user's feed.

- `src/server.ts`: API and session runner.
- `src/agent/`: prompt assembly and tool wiring.
- `skills/`: one folder per skill; the runner installs every skill into each agent session.

Agents have shell and HTTP access and a `web_search` tool.
