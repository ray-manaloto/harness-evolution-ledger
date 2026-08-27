#!/usr/bin/env python3
"""Strict, dependency-free Codex lifecycle hook for this repository."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Any


MAX_INPUT_BYTES = 1_048_576
MAX_STRING = 2_048
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BRANCHES = {"main", "master"}
SENSITIVE_NAME = re.compile(r"(?i)(api[_-]?key|authorization|bearer|credential|password|secret|token)")
SHELL_BOUNDARY = r"(?:^|[;&|]\s*|\n\s*)"
DESTRUCTIVE_GIT = (
    re.compile(rf"{SHELL_BOUNDARY}git\s+reset\s+--hard(?:\s|$)"),
    re.compile(rf"{SHELL_BOUNDARY}git\s+clean\s+-[^\n;&|]*f"),
    re.compile(rf"{SHELL_BOUNDARY}git\s+(?:checkout|restore)\s+--\s"),
    re.compile(rf"{SHELL_BOUNDARY}git\s+push\b[^\n;&|]*(?:--force(?:-with-lease)?|-f)(?:\s|$)"),
)
DEFAULT_BRANCH_MUTATION = re.compile(
    rf"{SHELL_BOUNDARY}git\s+(?:commit|merge|rebase|cherry-pick|push)(?:\s|$)"
)
REMOTE_DEFAULT_PUSH = re.compile(
    rf"{SHELL_BOUNDARY}git\s+push\b[^\n;&|]*"
    r"(?:(?:HEAD|[^:\s]+):)?(?:refs/heads/)?(?:main|master)(?:\s|$)"
)
BROAD_CREDENTIAL_READ = re.compile(
    rf"{SHELL_BOUNDARY}(?:env|printenv|set)\s*(?=$|[;&|\n])|"
    r"(?:printenv|echo)\s+\$?(?:ANTHROPIC_API_KEY|CLAUDE_CODE_OAUTH_TOKEN|"
    r"DOPPLER_TOKEN|OPENAI_ADMIN_KEY|OPENAI_API_KEY)(?:\s|$)|"
    r"(?:\.aws|\.config/(?:gh|doppler)|Keychains|fnox\.local\.toml)"
)


class HookInputError(ValueError):
    pass


def read_event() -> dict[str, Any]:
    raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise HookInputError("hook input exceeds 1 MiB")
    try:
        event = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HookInputError("hook input is not valid UTF-8 JSON") from exc
    if not isinstance(event, dict):
        raise HookInputError("hook input must be a JSON object")
    for field in ("hook_event_name", "cwd"):
        if not isinstance(event.get(field), str):
            raise HookInputError(f"hook field {field!r} must be a string")
    return event


def git_value(cwd: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def branch(cwd: Path) -> str:
    override = test_override("HEL_HOOK_TEST_BRANCH")
    return override if override is not None else git_value(cwd, "branch", "--show-current")


def test_override(name: str) -> str | None:
    if os.environ.get("HEL_HOOK_TEST_MODE") != "1":
        return None
    return os.environ.get(name)


def command_from(event: dict[str, Any]) -> str:
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        raise HookInputError("tool_input must be an object")
    command = tool_input.get("command")
    if not isinstance(command, str):
        raise HookInputError("tool_input.command must be a string")
    return command


def patch_paths(command: str) -> list[Path]:
    paths: list[Path] = []
    for match in re.finditer(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", command, re.MULTILINE):
        paths.append(Path(match.group(1).strip()))
    return paths


def outside_root(path: Path) -> bool:
    resolved = path.resolve() if path.is_absolute() else (ROOT / path).resolve()
    if resolved == Path("/dev/null"):
        return False
    return resolved != ROOT and ROOT not in resolved.parents


def token_path(token: str, cwd: Path) -> Path | None:
    candidate = token.strip("'\"")
    if candidate.startswith("$HOME/"):
        candidate = str(Path.home() / candidate.removeprefix("$HOME/"))
    elif candidate.startswith("~/"):
        candidate = str(Path.home() / candidate.removeprefix("~/"))
    elif candidate.startswith("$"):
        return Path("/")
    if not candidate or candidate.startswith("-"):
        return None
    return Path(candidate) if Path(candidate).is_absolute() else cwd / candidate


def shell_write_targets(command: str, cwd: Path) -> list[Path]:
    targets: list[Path] = []
    for match in re.finditer(r"(?:>|>>|<>)\s*([^\s;&|]+)", command):
        path = token_path(match.group(1), cwd)
        if path is not None:
            targets.append(path)
    for segment in re.split(r"(?:&&|\|\||[;&|\n])", command):
        try:
            argv = shlex.split(segment)
        except ValueError:
            return [Path("/")]
        if not argv:
            continue
        executable = Path(argv[0]).name
        operands = [item for item in argv[1:] if not item.startswith("-")]
        if executable in {"touch", "mkdir", "rm", "rmdir", "tee", "chmod", "chown"}:
            selected = operands
        elif executable in {"cp", "install", "mv"}:
            selected = operands[-1:]
        else:
            selected = []
        for item in selected:
            path = token_path(item, cwd)
            if path is not None:
                targets.append(path)
    return targets


def deny(reason: str) -> int:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    return 0


def command_denial_reason(command: str, cwd: Path) -> str | None:
    for pattern in DESTRUCTIVE_GIT:
        if pattern.search(command):
            return "Destructive Git operation blocked; use a reviewed repository task."
    if REMOTE_DEFAULT_PUSH.search(command):
        return "Direct push to a remote default branch blocked; use the reviewed land path."
    if branch(cwd) in DEFAULT_BRANCHES and DEFAULT_BRANCH_MUTATION.search(command):
        return "Direct default-branch mutation blocked; use an isolated branch or worktree."
    if BROAD_CREDENTIAL_READ.search(command):
        return "Broad credential or environment exposure blocked; use presence-only doctor checks."
    for sibling in ("/dotfiles/", "/knowledge-base/", "/local-model-eval/"):
        if sibling in command and re.search(r"(?:>|\b(?:rm|mv|cp|git\s+(?:commit|push))\b)", command):
            return "Sibling-repository mutation blocked by project scope."
    return None


def write_denial_reason(event: dict[str, Any], command: str, cwd: Path) -> str | None:
    if event.get("tool_name") == "apply_patch":
        paths = patch_paths(command)
        if not paths:
            return "Patch target could not be resolved safely."
        if any(outside_root(path) for path in paths):
            return "Write outside the authorized repository blocked."
    if event.get("tool_name") == "Bash":
        targets = shell_write_targets(command, cwd)
        if any(outside_root(path) for path in targets):
            return "Shell write outside the authorized repository blocked."
    return None


def pre_tool(event: dict[str, Any]) -> int:
    command = command_from(event)
    cwd = Path(event["cwd"])
    reason = command_denial_reason(command, cwd) or write_denial_reason(event, command, cwd)
    if reason:
        return deny(reason)
    return 0


def redact(value: Any, key: str = "") -> Any:
    if SENSITIVE_NAME.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(k): redact(v, str(k)) for k, v in list(value.items())[:64]}
    if isinstance(value, list):
        return [redact(item) for item in value[:64]]
    if isinstance(value, str):
        text = value[:MAX_STRING]
        for secret_name, secret in os.environ.items():
            if SENSITIVE_NAME.search(secret_name) and len(secret) >= 4:
                text = text.replace(secret, "[REDACTED]")
        text = re.sub(r"(?i)(bearer\s+)[A-Za-z0-9._~+/-]+", r"\1[REDACTED]", text)
        return text
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return f"<{type(value).__name__}>"


def event_log_path(cwd: Path) -> Path:
    override = test_override("HEL_HOOK_LOG")
    if override:
        return Path(override)
    git_dir = git_value(cwd, "rev-parse", "--git-dir")
    base = (cwd / git_dir).resolve() if git_dir else ROOT / ".git"
    return base / "hel" / "hooks.jsonl"


def append_record(event: dict[str, Any], kind: str) -> None:
    path = event_log_path(Path(event["cwd"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "schema": 1,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "kind": kind,
        "event": event.get("hook_event_name"),
        "session_id": event.get("session_id"),
        "turn_id": event.get("turn_id"),
        "tool_name": event.get("tool_name"),
        "tool_use_id": event.get("tool_use_id"),
        "input": redact(event.get("tool_input")),
        "response": redact(event.get("tool_response")),
    }
    encoded = json.dumps(record, sort_keys=True, separators=(",", ":"))
    with path.open("a", encoding="utf-8") as stream:
        stream.write(encoded + "\n")


def session_start(event: dict[str, Any]) -> int:
    cwd = Path(event["cwd"])
    status = git_value(cwd, "status", "--short")
    context = (
        f"HEL phase-0 context: root={ROOT}; branch={branch(cwd) or 'detached'}; "
        f"worktree={'dirty' if status else 'clean'}; read issue #1, HANDOFF.md, and "
        "BOOTSTRAP.md before mutation; run public mise tasks only."
    )
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                }
            }
        )
    )
    return 0


def stop(event: dict[str, Any]) -> int:
    if test_override("HEL_HOOK_SKIP_CHECKS") == "1":
        print(json.dumps({"continue": True}))
        return 0
    argv = ["mise", "run", "check:changed"]
    if test_override("HEL_HOOK_TEST_STOP_FAILURE") == "1":
        argv = [sys.executable, "-c", "raise SystemExit(73)"]
    result = subprocess.run(
        argv,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=25,
    )
    append_record(
        {
            **event,
            "tool_name": "mise run check:changed",
            "tool_response": {"exit_code": result.returncode, "output": result.stdout[-MAX_STRING:]},
        },
        "stop-check",
    )
    if result.returncode:
        print(
            json.dumps(
                {
                    "decision": "block",
                    "reason": "Changed-file checks failed; inspect the retained hook record before stopping.",
                }
            )
        )
    else:
        print(json.dumps({"continue": True}))
    return 0


def session_end(event: dict[str, Any]) -> int:
    append_record(event, "session-end-enqueued")
    path = event_log_path(Path(event["cwd"])).with_name("queue.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    created_at = datetime.now(timezone.utc).isoformat()
    payload = {
        "schema": 1,
        "kind": "phase0-session-end",
        "status": "pending",
        "created_at": created_at,
        "job_id": hashlib.sha256(
            f"{event.get('session_id')}:{created_at}".encode("utf-8")
        ).hexdigest(),
        "session_id": event.get("session_id"),
        "reason": event.get("reason", "other"),
    }
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n")
    return 0


def main() -> int:
    name = ""
    try:
        event = read_event()
        name = event["hook_event_name"]
        if name == "SessionStart":
            return session_start(event)
        if name == "PreToolUse":
            return pre_tool(event)
        if name == "PostToolUse":
            append_record(event, "post-tool")
            return 0
        if name == "Stop":
            return stop(event)
        if name == "SessionEnd":
            return session_end(event)
        raise HookInputError(f"unsupported hook event: {name}")
    except HookInputError as exc:
        print(f"Codex hook rejected malformed input: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # fail closed for policy; observational hooks report failure
        print(f"Codex hook runtime failure: {type(exc).__name__}", file=sys.stderr)
        return 0 if name in {"SessionStart", "PostToolUse", "SessionEnd"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
