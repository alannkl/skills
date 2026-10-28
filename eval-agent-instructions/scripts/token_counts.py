"""Count the tokens of each text a with arm loads, per setup, for the report.

An Anthropic model's count comes from the Messages count_tokens endpoint at
$ANTHROPIC_BASE_URL, less the count of a one-character message, so the figure is
the text's own; any other model gets an estimate with tiktoken's o200k_base. A
text that cannot be counted is recorded with the reason, and a run never stops
over it.
"""
import json
import os
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from tasks import without_frontmatter

ESTIMATE_ENCODING = "o200k_base"
# Count calls in flight at once.
COUNT_WORKERS = 4


def loaded_texts(artifact: dict, source: Path, instruction_file: str | None = None) -> list[tuple[str, str]]:
    """(load path, text) for each text the with arm delivers: an instruction file as delivered under
    `instruction_file`, a prompt as written, or a skill's SKILL.md and every other text file in its folder."""
    if artifact["type"] == "instruction-file":
        return [(instruction_file, without_frontmatter(source.read_bytes().decode()))]
    if artifact["type"] == "prompt":
        return [(f"{artifact['role']} prompt", source.read_text())]
    texts = []
    for path in sorted(p for p in source.rglob("*") if p.is_file() and "evals" not in p.relative_to(source).parts):
        try:
            texts.append((f"{artifact['name']}/{path.relative_to(source).as_posix()}", path.read_bytes().decode()))
        except UnicodeDecodeError:
            continue
    return sorted(texts, key=lambda t: t[0] != f"{artifact['name']}/SKILL.md")


def loaded_tokens(texts: dict[str, list[tuple[str, str]]], models: dict[str, str]) -> dict[str, list[dict]]:
    """Per setup in `texts`, {"path", "tokens", "method"} for each of its texts, or {"path", "tokens": None,
    "not_counted": reason}; `models` maps each setup to its model id, such as `anthropic/claude-opus-5-5`."""
    counters = {model: _counter(model) for model in set(models.values())}
    jobs = sorted({(models[setup], text) for setup, pairs in texts.items() for _, text in pairs})

    def count(job: tuple[str, str]) -> dict:
        tally, method = counters[job[0]]
        if tally is None:
            return {"tokens": None, "not_counted": method}
        try:
            return {"tokens": tally(job[1]), "method": method}
        except Exception as exc:  # a failed count is reported, never raised
            return {"tokens": None, "not_counted": _reason(exc)}
    with ThreadPoolExecutor(COUNT_WORKERS) as pool:
        counted = dict(zip(jobs, pool.map(count, jobs)))
    return {setup: [{"path": path} | counted[(models[setup], text)] for path, text in pairs]
            for setup, pairs in texts.items()}


def _counter(model: str):
    """(count function, method) for a model, or (None, why it cannot count)."""
    provider, _, name = model.partition("/")
    try:
        if provider == "anthropic":
            unset = [v for v in ("ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN") if not os.environ.get(v)]
            if unset:
                return None, f"{' and '.join(unset)} not set"
            overhead = _anthropic_count(name, "x")
            return (lambda text: _anthropic_count(name, text) - overhead if text else 0), "count_tokens endpoint"
        import tiktoken
        encoding = tiktoken.get_encoding(ESTIMATE_ENCODING)
        return (lambda text: len(encoding.encode(text, disallowed_special=()))), \
            f"estimate with tiktoken {ESTIMATE_ENCODING}"
    except Exception as exc:  # no credentials, an endpoint error, or tiktoken missing
        return None, _reason(exc)


def _anthropic_count(model: str, text: str) -> int:
    """Input tokens of one user message holding `text`, from the proxy's count_tokens endpoint."""
    token = os.environ["ANTHROPIC_AUTH_TOKEN"]
    body = {"model": model, "messages": [{"role": "user", "content": text}]}
    request = urllib.request.Request(
        f"{os.environ['ANTHROPIC_BASE_URL'].rstrip('/')}/v1/messages/count_tokens", data=json.dumps(body).encode(),
        headers={"x-api-key": token, "authorization": f"Bearer {token}", "anthropic-version": "2023-06-01",
                 "content-type": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)["input_tokens"]


def _reason(exc: Exception) -> str:
    if isinstance(exc, KeyError):
        return f"no {exc.args[0]} in the reply"
    if isinstance(exc, ImportError):
        return "tiktoken is not installed"
    return f"{type(exc).__name__}: {exc}"
