#!/usr/bin/env python3
"""Verify checked-in Codex execpolicy decisions against exact commands."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / ".codex/rules/project.rules"
CONTROLS = (
    (("git", "reset", "--hard"), "forbidden"),
    (("git", "clean", "-fd"), "forbidden"),
    (("git", "clean", "-n"), "allow"),
    (("git", "clean", "--dry-run"), "allow"),
    (("git", "clean", "-d", "-f"), "prompt"),
    (("git", "push", "--force", "origin", "topic"), "forbidden"),
    (("git", "push", "origin", "topic", "--force-with-lease"), "forbidden"),
    (("git", "push", "origin", "topic"), "forbidden"),
    (("git", "push", "origin", "HEAD:main"), "forbidden"),
    (("git", "status", "--short"), "allow"),
    (("git", "merge", "--ff-only"), None),
    (("git", "merge", "--ff-only", "origin/main"), "allow"),
    (("git", "merge", "origin/main"), "prompt"),
    (("git", "merge", "--no-ff", "origin/main"), "prompt"),
    (("git", "rebase", "origin/main"), "prompt"),
    (("git", "cherry-pick", "deadbeef"), "prompt"),
    (("gh", "pr", "merge", "4"), "prompt"),
    (("gh", "pr", "view", "4"), "allow"),
    (("cmake", "--build", "build"), "forbidden"),
    (("clang-format", "-i", "tests/phase0_smoke.cpp"), "forbidden"),
    (("mise", "install"), "forbidden"),
    (("mise", "run", "build"), "allow"),
    (("mise", "run", "ship"), "prompt"),
    (("mise", "run", "land"), "prompt"),
)


def decision(command: tuple[str, ...]) -> str | None:
    result = subprocess.run(
        ["codex", "execpolicy", "check", "--rules", str(RULES), "--", *command],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise RuntimeError(f"execpolicy failed for {command}: {result.stderr.strip()}")
    payload = json.loads(result.stdout)
    value = payload.get("decision")
    return str(value) if value is not None else None


def main() -> int:
    for command, expected in CONTROLS:
        observed = decision(command)
        if observed != expected:
            raise AssertionError(f"{command}: expected {expected}, observed {observed}")
        label = expected or "unmatched"
        print(f"{label:9} {' '.join(command)}")
    print(f"verified {len(CONTROLS)} command-policy controls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
