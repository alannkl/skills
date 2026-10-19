import json


def parse_reply(text: str) -> dict:
    data = json.loads(text)
    return {
        "summary": data["summary"],
        "actions": [(a["owner"], a["task"]) for a in data["actions"]],
        "confidence": float(data["confidence"]),
    }
