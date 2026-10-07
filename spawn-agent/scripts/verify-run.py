#!/usr/bin/env python3
"""Checks whether a headless agent run completed its output protocol.

Reads the run's captured stdout, optional stderr and exit code, and applies the
harness's acceptance rules from the skill references: the stream parses, its
lifecycle events arrive in order and end in exactly one terminal event, that
event reports success with a session identifier and a result, and no tool call
was denied permission. Protocol completion says nothing about the task: verify
the artifacts separately.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HARNESSES = ("claude", "codex", "antigravity", "cursor")
DENIAL_PATTERN = re.compile(r"permission denied|approval denied|sandbox denied|not permitted|requires approval|soft-denied", re.I)
SANDBOX_ERROR_PATTERN = re.compile(r"sandbox.*(error|fail|unavailable|unsupported)", re.I)


class Failure(Exception):
    """A protocol failure that affects the caller's next decision."""


def parse_args():
    parser = argparse.ArgumentParser(
        description="Verify that a headless agent run completed its output protocol.",
        epilog="Exits 0 when the protocol completed, 1 when it failed, 2 for unusable input. "
               "Prints one JSON object: status, reason, session_id, result_file, structured_output, "
               "permission_notices, stderr_tail, usage. Writes the final response text to --result.",
    )
    parser.add_argument("--harness", required=True, choices=HARNESSES)
    parser.add_argument("--stdout", required=True, help="File holding the run's captured stdout")
    parser.add_argument("--stderr", help="File holding the run's captured stderr")
    parser.add_argument("--exit-code", type=int, required=True, help="The run's process exit code; 124 means the host timeout killed it")
    parser.add_argument("--format", choices=("json", "stream-json", "text"),
                        help="Output format the run was asked for. json and stream-json are detected when omitted; "
                             "text must be named and only checks the exit code and non-empty output")
    parser.add_argument("--result", help="Where to write the final response text; default <stdout>.result.txt")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        stdout = Path(args.stdout).read_text(encoding="utf-8", errors="replace")
        stderr = Path(args.stderr).read_text(encoding="utf-8", errors="replace") if args.stderr else ""
    except OSError as error:
        return usage_error(f"cannot read input file: {error}")
    report = {
        "status": "completed",
        "harness": args.harness,
        "reason": None,
        "session_id": None,
        "result_file": None,
        "structured_output": None,
        "permission_notices": stderr_notices(stderr),
        "stderr_tail": tail(stderr),
        "usage": None,
    }
    outcome = {}
    try:
        if args.exit_code == 124:
            raise Failure("the host timeout killed the run (exit 124)")
        if args.exit_code != 0:
            raise Failure(f"exit code {args.exit_code}")
        sandbox_errors = [line.strip() for line in stderr.splitlines() if SANDBOX_ERROR_PATTERN.search(line)]
        if args.harness == "cursor" and sandbox_errors:
            raise Failure(f"sandbox startup failed: {sandbox_errors[0][:200]}")
        if args.format == "text":
            outcome = verify_text(stdout)
        else:
            outcome = VERIFIERS[args.harness](stdout, args.format or detect_format(args.harness, stdout))
        denials = outcome.get("denials", [])
        report["permission_notices"] = denials + report["permission_notices"]
        if denials:
            raise Failure(f"{len(denials)} tool call(s) were denied permission; correct the grant and rerun")
    except Failure as error:
        report["status"] = "failed"
        report["reason"] = str(error)
    report["session_id"] = outcome.get("session_id")
    report["structured_output"] = outcome.get("structured_output")
    report["usage"] = outcome.get("usage")
    if report["status"] == "completed" and report["permission_notices"]:
        report["reason"] = "stderr mentions a permission problem; inspect it before trusting the run"
    text = outcome.get("text")
    if text is not None:
        result_file = Path(args.result or f"{args.stdout}.result.txt")
        try:
            result_file.write_text(text, encoding="utf-8")
        except OSError as error:
            return usage_error(f"cannot write the result file: {error}")
        report["result_file"] = str(result_file)
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] == "completed" else 1


def usage_error(message):
    print(json.dumps({"status": "failed", "reason": message}))
    return 2


def tail(text, lines=5):
    kept = [line for line in text.splitlines() if line.strip()]
    return kept[-lines:]


def detect_format(harness, stdout):
    if harness == "codex":
        return "stream-json"
    stripped = stdout.strip()
    if not stripped:
        raise Failure("stdout is empty")
    try:
        json.loads(stripped)
        return "json"
    except ValueError:
        return "stream-json"


def verify_text(stdout):
    if not stdout.strip():
        raise Failure("stdout is empty")
    return {"text": stdout}


def load_object(stdout):
    try:
        data = json.loads(stdout)
    except ValueError as error:
        raise Failure(f"stdout is not one JSON object: {error}")
    if not isinstance(data, dict):
        raise Failure("stdout JSON is not an object")
    return data


def load_events(stdout):
    events = []
    for number, line in enumerate(stdout.splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError as error:
            raise Failure(f"line {number} is not JSON: {error}")
        if not isinstance(event, dict):
            raise Failure(f"line {number} is not a JSON object")
        events.append(event)
    if not events:
        raise Failure("stdout holds no events")
    return events


def single_terminal(events, is_terminal, name):
    """The terminal event must close the stream: exactly one, and last."""
    terminals = [event for event in events if is_terminal(event)]
    if not terminals:
        raise Failure(f"stream ended without a terminal {name} event")
    if len(terminals) > 1:
        raise Failure(f"stream holds {len(terminals)} terminal {name} events")
    if events[-1] is not terminals[0]:
        raise Failure(f"stream continues after its terminal {name} event")
    return terminals[0]


def accept_result_object(result):
    """Claude and Cursor share one result shape: type result, subtype success, is_error false, result text, session_id."""
    if result.get("type") != "result":
        raise Failure(f"final object has type {result.get('type')!r}, expected 'result'")
    if result.get("subtype") != "success" or result.get("is_error") is not False:
        raise Failure(f"result reports subtype {result.get('subtype')!r} with is_error {result.get('is_error')!r}")
    session = result.get("session_id")
    if not isinstance(session, str) or not session:
        raise Failure("result carries no session_id")
    if not isinstance(result.get("result"), str):
        raise Failure("result carries no result text")
    denials = result.get("permission_denials") or []
    return {
        "session_id": session,
        "text": result["result"],
        "structured_output": result.get("structured_output"),
        "usage": result.get("usage"),
        "denials": [describe_denial(item) for item in denials],
    }


def describe_denial(item):
    if isinstance(item, dict):
        name = item.get("tool_name") or item.get("tool") or "tool"
        return f"{name}: {json.dumps(item.get('tool_input', item), ensure_ascii=False)[:200]}"
    return str(item)[:200]


def verify_claude(stdout, fmt):
    if fmt == "json":
        return accept_result_object(load_object(stdout))
    events = load_events(stdout)
    return accept_result_object(single_terminal(events, lambda e: e.get("type") == "result", "result"))


verify_cursor = verify_claude


def verify_codex(stdout, fmt):
    events = load_events(stdout)
    thread = next((e for e in events if e.get("type") == "thread.started"), None)
    session = thread.get("thread_id") if thread else None
    denials = []
    messages = []
    for event in events:
        kind = event.get("type")
        if kind == "turn.failed" or kind == "error":
            raise Failure(f"stream reports {kind}: {json.dumps(event.get('error') or event.get('message') or event, ensure_ascii=False)[:300]}")
        item = event.get("item") if kind in ("item.completed", "item.updated") else None
        if not isinstance(item, dict):
            continue
        if item.get("type") == "agent_message" and kind == "item.completed":
            messages.append(item.get("text") or "")
        error = item.get("error")
        code = error.get("code") if isinstance(error, dict) else None
        if code in ("permission_denied", "approval_denied", "sandbox_denied") or item.get("status") in ("declined", "denied"):
            denials.append(f"{item.get('type')}: {json.dumps(item.get('command') or item.get('title') or item, ensure_ascii=False)[:200]}")
    terminal = single_terminal(events, lambda e: e.get("type") == "turn.completed", "turn.completed")
    if not session:
        raise Failure("stream carries no thread.started event with a thread_id")
    return {
        "session_id": session,
        "text": messages[-1] if messages else "",
        "usage": terminal.get("usage"),
        "denials": denials,
    }


def verify_antigravity(stdout, fmt):
    if fmt == "json":
        data = load_object(stdout)
        status = data.get("status")
        if status != "SUCCESS":
            raise Failure(f"result status is {status!r}, expected 'SUCCESS'")
        session = data.get("conversation_id")
        if not isinstance(session, str) or not session:
            raise Failure("result carries no conversation_id")
        return {
            "session_id": session,
            "text": data.get("response") if isinstance(data.get("response"), str) else "",
            "structured_output": data.get("structured_output"),
            "usage": data.get("usage"),
        }
    events = load_events(stdout)
    inits = [e for e in events if e.get("event") == "init"]
    if len(inits) != 1 or events[0] is not inits[0]:
        raise Failure("stream must open with exactly one init event")
    terminal = single_terminal(events, lambda e: e.get("event") == "result", "result")
    result = terminal.get("result") if isinstance(terminal.get("result"), dict) else {}
    status = result.get("status")
    if status != "SUCCESS":
        raise Failure(f"terminal result status is {status!r}, expected 'SUCCESS'")
    session = result.get("conversation_id") or inits[0].get("conversation_id")
    if not isinstance(session, str) or not session:
        raise Failure("stream carries no conversation_id")
    text = result.get("response")
    if not isinstance(text, str):
        deltas = []
        for event in events:
            update = event.get("step_update") if event.get("event") == "step_update" else None
            if isinstance(update, dict) and update.get("step_type") == "agent_response":
                deltas.append(update.get("text_delta") or "")
        text = "".join(deltas)
    return {
        "session_id": session,
        "text": text,
        "structured_output": result.get("structured_output"),
        "usage": result.get("usage"),
    }


VERIFIERS = {
    "claude": verify_claude,
    "codex": verify_codex,
    "antigravity": verify_antigravity,
    "cursor": verify_cursor,
}


def stderr_notices(stderr):
    return [line.strip()[:200] for line in stderr.splitlines() if DENIAL_PATTERN.search(line)]


if __name__ == "__main__":
    sys.exit(main())
