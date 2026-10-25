Earlier in this chat:

> user: half the team uses claude code now and it doesnt read AGENTS.md. should we add a CLAUDE.md?
>
> you: Yes, but don't copy AGENTS.md into it; two copies will drift. Plan:
> 1. Add a `CLAUDE.md` that just imports the existing file with `@AGENTS.md`, so both tools read the same instructions.
> 2. Since Claude Code will start following AGENTS.md too, fix its stale Setup commands: the repo uses uv (there's a `uv.lock` and no `requirements.txt`), so `pip install -r requirements.txt` should become `uv sync` and the server command `uv run uvicorn app.main:app --reload`.
>
> The Testing section also repeats itself a bit, but that's a separate cleanup.

Now: ok go ahead
