#!/usr/bin/env python3
"""Exercise Codex lifecycle hooks and hk with positive and negative controls."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "scripts/codex_hook.py"


def invoke(event: dict[str, object], **extra_env: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["HEL_HOOK_TEST_MODE"] = "1"
    env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(HOOK)],
        cwd=ROOT,
        env=env,
        input=json.dumps(event),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def base(event_name: str) -> dict[str, object]:
    return {
        "session_id": "phase0-control",
        "turn_id": "phase0-turn",
        "transcript_path": None,
        "cwd": str(ROOT),
        "model": "control",
        "permission_mode": "default",
        "hook_event_name": event_name,
    }


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def allowed_bash_event() -> dict[str, object]:
    return {
        **base("PreToolUse"),
        "tool_name": "Bash",
        "tool_use_id": "allowed",
        "tool_input": {"command": "set -euo pipefail; git status --short"},
    }


def pre_tool_controls() -> None:
    allowed = allowed_bash_event()
    result = invoke(allowed, HEL_HOOK_TEST_BRANCH="codex/phase-0-bootstrap")
    expect(result.returncode == 0 and result.stdout == "", f"allow control failed: {result.stderr}")

    destructive = {
        **allowed,
        "tool_use_id": "destructive",
        "tool_input": {"command": "git reset --hard HEAD~1"},
    }
    result = invoke(destructive, HEL_HOOK_TEST_BRANCH="codex/phase-0-bootstrap")
    payload = json.loads(result.stdout)
    expect(result.returncode == 0, "destructive control did not produce a policy response")
    expect(
        payload["hookSpecificOutput"]["permissionDecision"] == "deny",
        "destructive Git control was not denied",
    )

    multiline_destructive = {
        **allowed,
        "tool_use_id": "multiline-destructive",
        "tool_input": {"command": "git status --short\ngit reset --hard HEAD~1"},
    }
    result = invoke(multiline_destructive, HEL_HOOK_TEST_BRANCH="codex/phase-0-bootstrap")
    payload = json.loads(result.stdout)
    expect(
        payload["hookSpecificOutput"]["permissionDecision"] == "deny",
        "multiline destructive Git control was not denied",
    )

    default_mutation = {
        **allowed,
        "tool_use_id": "default-branch",
        "tool_input": {"command": "git commit -m blocked"},
    }
    result = invoke(default_mutation, HEL_HOOK_TEST_BRANCH="main")
    payload = json.loads(result.stdout)
    expect(payload["hookSpecificOutput"]["permissionDecision"] == "deny", "main mutation allowed")

    outside = {
        **allowed,
        "tool_name": "apply_patch",
        "tool_use_id": "outside",
        "tool_input": {"command": "*** Begin Patch\n*** Add File: /tmp/outside\n+x\n*** End Patch"},
    }
    result = invoke(outside, HEL_HOOK_TEST_BRANCH="codex/phase-0-bootstrap")
    payload = json.loads(result.stdout)
    expect(payload["hookSpecificOutput"]["permissionDecision"] == "deny", "outside write allowed")

    shell_outside = {
        **allowed,
        "tool_use_id": "shell-outside",
        "tool_input": {"command": "printf x > /tmp/hel-phase0-outside"},
    }
    result = invoke(shell_outside, HEL_HOOK_TEST_BRANCH="codex/phase-0-bootstrap")
    payload = json.loads(result.stdout)
    expect(payload["hookSpecificOutput"]["permissionDecision"] == "deny", "shell outside write allowed")

    null_sink = {
        **allowed,
        "tool_use_id": "null-sink",
        "tool_input": {"command": "mise lock --dry-run > /dev/null"},
    }
    result = invoke(null_sink, HEL_HOOK_TEST_BRANCH="codex/phase-0-bootstrap")
    expect(result.returncode == 0 and result.stdout == "", f"/dev/null control failed: {result.stderr}")

    remote_default = {
        **allowed,
        "tool_use_id": "remote-default",
        "tool_input": {"command": "git push origin HEAD:main"},
    }
    result = invoke(remote_default, HEL_HOOK_TEST_BRANCH="codex/phase-0-bootstrap")
    payload = json.loads(result.stdout)
    expect(payload["hookSpecificOutput"]["permissionDecision"] == "deny", "remote main push allowed")


def malformed_input_control() -> None:
    malformed = subprocess.run(
        [sys.executable, str(HOOK)],
        cwd=ROOT,
        input="[]",
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    expect(malformed.returncode == 2, "non-object hook input did not fail closed")


def post_tool_redaction_control() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        log = Path(temp_dir) / "hooks.jsonl"
        unknown_secret = "phase0-unknown-credential-value"
        response = {
            **base("PostToolUse"),
            "tool_name": "Bash",
            "tool_use_id": "redaction",
            "tool_input": {"command": "provider control"},
            "tool_response": {
                "stdout": f"Bearer phase0-secret-value and {unknown_secret}",
                "exit_code": 0,
            },
        }
        result = invoke(
            response,
            HEL_HOOK_LOG=str(log),
            HEL_TEST_CREDENTIAL=unknown_secret,
        )
        expect(result.returncode == 0, f"post-tool control failed: {result.stderr}")
        contents = log.read_text(encoding="utf-8")
        expect("phase0-secret-value" not in contents, "bearer value reached hook log")
        expect(unknown_secret not in contents, "unknown credential value reached hook log")
        expect("[REDACTED]" in contents, "redaction marker missing from hook log")


def session_lifecycle_controls() -> None:
    result = invoke(
        {**base("SessionStart"), "source": "startup"},
        HEL_HOOK_TEST_BRANCH="codex/phase-0-bootstrap",
    )
    payload = json.loads(result.stdout)
    expect("phase-0 context" in payload["hookSpecificOutput"]["additionalContext"], "start context absent")

    result = invoke(
        {**base("Stop"), "stop_hook_active": False, "last_assistant_message": None},
        HEL_HOOK_SKIP_CHECKS="1",
    )
    expect(result.returncode == 0 and json.loads(result.stdout)["continue"], "Stop allow failed")

    with tempfile.TemporaryDirectory() as temp_dir:
        log = Path(temp_dir) / "hooks.jsonl"
        result = invoke(
            {**base("Stop"), "stop_hook_active": False, "last_assistant_message": None},
            HEL_HOOK_TEST_STOP_FAILURE="1",
            HEL_HOOK_LOG=str(log),
        )
        payload = json.loads(result.stdout)
        expect(payload["decision"] == "block", "Stop failure did not block")
        expect('"exit_code":73' in log.read_text(encoding="utf-8"), "Stop status not retained")

        result = invoke({**base("SessionEnd"), "reason": "other"}, HEL_HOOK_LOG=str(log))
        expect(result.returncode == 0, f"SessionEnd enqueue failed: {result.stderr}")
        expect("session-end-enqueued" in log.read_text(encoding="utf-8"), "end enqueue absent")
        queued = json.loads((Path(temp_dir) / "queue.jsonl").read_text(encoding="utf-8"))
        expect(queued["status"] == "pending", "SessionEnd queue item is not pending")
        expect(queued["kind"] == "phase0-session-end", "SessionEnd queue kind drifted")


def codex_controls() -> None:
    pre_tool_controls()
    malformed_input_control()
    post_tool_redaction_control()
    session_lifecycle_controls()


def hk_controls() -> None:
    validate = subprocess.run(["hk", "validate"], cwd=ROOT, check=False)
    expect(validate.returncode == 0, "hk configuration failed validation")
    positive = subprocess.run(["hk", "run", "pre-commit"], cwd=ROOT, check=False)
    expect(positive.returncode == 0, "hk pre-commit positive control failed")
    push_positive = subprocess.run(["hk", "run", "pre-push"], cwd=ROOT, check=False)
    expect(push_positive.returncode == 0, "hk pre-push positive control failed")
    env = dict(os.environ)
    env["HEL_PHASE0_FORCE_FAIL"] = "1"
    negative = subprocess.run(["hk", "run", "pre-commit"], cwd=ROOT, env=env, check=False)
    expect(negative.returncode != 0, "hk negative control did not preserve failing gate status")
    push_negative = subprocess.run(["hk", "run", "pre-push"], cwd=ROOT, env=env, check=False)
    expect(push_negative.returncode != 0, "hk pre-push negative control did not preserve status")


def main() -> int:
    codex_controls()
    hk_controls()
    print("Codex lifecycle and hk controls passed in both directions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
