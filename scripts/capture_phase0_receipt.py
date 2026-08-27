#!/usr/bin/env python3
"""Run host phase-0 controls and retain exact, separated process evidence."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/receipts/phase-0/host-controls.json"
CONTROLS = (
    (["mise", "run", "doctor"], 0),
    (["mise", "run", "check"], 0),
    (["mise", "run", "hooks:verify"], 0),
    (["mise", "run", "rules:verify"], 0),
    (["mise", "run", "security"], 0),
    (["mise", "run", "sbom"], 0),
    (["mise", "run", "control:fail"], 42),
)


def candidate_tree_digest() -> str:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    excluded = OUTPUT.relative_to(ROOT).as_posix()
    paths = sorted(item.decode("utf-8") for item in result.stdout.split(b"\0") if item)
    digest = hashlib.sha256()
    for relative in paths:
        if relative == excluded:
            continue
        path = ROOT / relative
        digest.update(relative.encode("utf-8") + b"\0")
        if not path.is_file():
            digest.update(b"missing\0")
            continue
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def captured(argv: list[str], expected: int) -> dict[str, object]:
    started = datetime.now(timezone.utc)
    result = subprocess.run(
        argv,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    ended = datetime.now(timezone.utc)
    return {
        "argv": argv,
        "started_at": started.isoformat(),
        "ended_at": ended.isoformat(),
        "exit_status": result.returncode,
        "expected_exit_status": expected,
        "passed": result.returncode == expected,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main() -> int:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, text=True, stdout=subprocess.PIPE
    ).stdout.strip()
    controls = [captured(argv, expected) for argv, expected in CONTROLS]
    payload = {
        "schema": 1,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "head_before_commit": head,
        "candidate_tree_sha256_excluding_this_receipt": candidate_tree_digest(),
        "credential_values_retained": False,
        "controls": controls,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    failures = [item for item in controls if not item["passed"]]
    print(f"retained {len(controls)} command receipts at {OUTPUT.relative_to(ROOT)}")
    if failures:
        for item in failures:
            print(f"unexpected status {item['exit_status']}: {' '.join(item['argv'])}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
