from pathlib import Path

from anthropic import Anthropic

SYSTEM_PROMPT = (Path(__file__).parent.parent / "prompts" / "support_agent.md").read_text()
client = Anthropic()


def reply(history: list[dict]) -> str:
    resp = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=history,
    )
    return resp.content[0].text
