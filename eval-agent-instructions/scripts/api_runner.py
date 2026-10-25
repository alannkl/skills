"""Run tasks straight against a model API, for prompts an app sends without an agent harness.

Each attempt sends the task's system prompt, if it has one, and its instruction as
the user message. It writes a trial folder shaped like Harbor's, so grading treats
both alike: `config.json` naming the task, `result.json`, `agent/api.json` with the
reply, and `verifier/workspace` holding the case's starting workspace, which an API
call cannot change.
"""
import json
import os
import secrets
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from graders import initial_workspace

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def build_request(config: dict, system: str | None, user: str) -> tuple[str, dict, dict]:
    """URL, body and headers for one call; Anthropic and OpenAI models go through the proxy at $ANTHROPIC_BASE_URL."""
    provider, model = config["model"].split("/", 1)
    effort = config.get("effort")
    if provider == "openrouter":
        messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
        body = {"model": model, "messages": messages, "usage": {"include": True}}
        if config.get("openrouter_providers"):
            body["provider"] = {"order": config["openrouter_providers"], "allow_fallbacks": False}
        if "max_tokens" in config:
            body["max_tokens"] = config["max_tokens"]
        if effort:
            body["reasoning"] = {"effort": effort}
        return OPENROUTER_URL, body, {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"}
    base = os.environ["ANTHROPIC_BASE_URL"].rstrip("/")
    headers = {"Authorization": f"Bearer {os.environ['ANTHROPIC_AUTH_TOKEN']}", "anthropic-version": "2023-06-01"}
    if provider == "openai":
        body = {"model": model, "input": user}
        if system:
            body["instructions"] = system
        if effort:
            body["reasoning"] = {"effort": effort}
        return f"{base}/v1/responses", body, headers
    if provider == "anthropic":
        body = {"model": model, "max_tokens": 32000, "messages": [{"role": "user", "content": user}]}
        if system:
            body["system"] = system
        if effort:
            body |= {"thinking": {"type": "adaptive"}, "output_config": {"effort": effort}}
        return f"{base}/v1/messages", body, headers
    raise SystemExit(f"api setups need an anthropic/, openai/ or openrouter/ model, not {config['model']}")


def parse_reply(config: dict, data: dict) -> dict:
    """The reply's text, model, usage, and cost and upstream provider where the API reports them."""
    provider = config["model"].split("/", 1)[0]
    if provider == "openrouter":
        message = (data.get("choices") or [{}])[0].get("message") or {}
        usage = data.get("usage") or {}
        return {"text": message.get("content") or "", "model": data.get("model"), "usage": usage,
                "cost_usd": usage.get("cost"), "provider": data.get("provider")}
    if provider == "openai":
        text = "".join(c.get("text", "") for o in data.get("output", []) if o.get("type") == "message"
                       for c in o.get("content", []))
    else:
        text = "".join(c.get("text", "") for c in data.get("content", []) if c.get("type") == "text")
    return {"text": text, "model": data.get("model"), "usage": data.get("usage"), "cost_usd": None, "provider": None}


def call(config: dict, system: str | None, user: str, attempts: int = 3) -> dict:
    """One completion, retrying throttling and server errors."""
    url, body, headers = build_request(config, system, user)
    request = urllib.request.Request(url, data=json.dumps(body).encode(),
                                     headers=headers | {"content-type": "application/json"})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                return parse_reply(config, json.load(response))
        except urllib.error.HTTPError as exc:
            if not (exc.code == 429 or exc.code >= 500) or attempt + 1 == attempts:
                raise
            time.sleep(10 * (attempt + 1))
    return {}


def run_trial(config: dict, task: Path, out: Path) -> None:
    trial = out / f"{task.name}__{secrets.token_hex(4)}"
    (trial / "agent").mkdir(parents=True)
    (trial / "config.json").write_text(json.dumps({"task": {"path": str(task)}}))
    system_path = task / "prompt" / "system.md"
    system = system_path.read_text() if system_path.is_file() else None
    try:
        reply = call(config, system, (task / "instruction.md").read_text())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        (trial / "result.json").write_text(json.dumps(
            {"exception_info": {"exception_type": "ApiError", "exception_message": str(exc)}}))
        return
    (trial / "agent" / "api.json").write_text(json.dumps(reply, indent=2))
    initial_workspace(task / "environment" / "case", trial / "verifier" / "workspace")
    (trial / "verifier" / "reward.json").write_text('{"snapshot": 1}')
    (trial / "result.json").write_text(json.dumps({"exception_info": None}))


def run_api_job(config: dict, tasks_dir: Path, task_names: list[str], attempts: int, out: Path,
                concurrency: int) -> None:
    """Every task `attempts` times, `concurrency` calls at a time."""
    out.mkdir(parents=True, exist_ok=True)
    jobs = [tasks_dir / name for name in task_names for _ in range(attempts)]
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        list(pool.map(lambda task: run_trial(config, task, out), jobs))
