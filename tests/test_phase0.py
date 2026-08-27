from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import json
import importlib.util
from contextlib import contextmanager


ROOT = Path(__file__).resolve().parents[1]
PHASE0 = ROOT / "scripts/phase0.py"
PHASE0_SPEC = importlib.util.spec_from_file_location("phase0", PHASE0)
assert PHASE0_SPEC is not None and PHASE0_SPEC.loader is not None
phase0 = importlib.util.module_from_spec(PHASE0_SPEC)
PHASE0_SPEC.loader.exec_module(phase0)


@contextmanager
def isolated_git_environment():
    context_keys = (
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_COMMON_DIR",
        "GIT_INDEX_FILE",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_PREFIX",
    )
    saved = {key: os.environ.pop(key) for key in context_keys if key in os.environ}
    try:
        yield
    finally:
        os.environ.update(saved)


class Phase0PolicyTests(unittest.TestCase):
    def create_worktree_fixture(self, temp_dir: str) -> tuple[Path, Path, Path]:
        root = Path(temp_dir)
        remote = root / "remote.git"
        canonical = root / "canonical"
        linked = root / "linked"
        subprocess.run(
            ["git", "init", "--bare", "--initial-branch=main", str(remote)],
            check=True,
        )
        subprocess.run(["git", "clone", str(remote), str(canonical)], check=True)
        for key, value in (("user.name", "Phase Zero"), ("user.email", "phase0@example.test")):
            subprocess.run(
                ["git", "-C", str(canonical), "config", key, value], check=True
            )
        tracked = canonical / "tracked.txt"
        tracked.write_text("baseline\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(canonical), "add", "tracked.txt"], check=True)
        subprocess.run(
            ["git", "-C", str(canonical), "commit", "-m", "baseline"], check=True
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(canonical),
                "switch",
                "-c",
                phase0.SHIP_TARGET_BRANCH,
            ],
            check=True,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(canonical),
                "push",
                "--set-upstream",
                "origin",
                phase0.SHIP_TARGET_BRANCH,
            ],
            check=True,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(canonical),
                "worktree",
                "add",
                "-b",
                phase0.SHIP_SOURCE_BRANCH,
                str(linked),
            ],
            check=True,
        )
        return remote, canonical, linked

    def publish_linked_change(self, linked: Path) -> str:
        subprocess.run(
            ["git", "-C", str(linked), "config", "user.name", "Phase Zero"],
            check=True,
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(linked),
                "config",
                "user.email",
                "phase0@example.test",
            ],
            check=True,
        )
        (linked / "tracked.txt").write_text("candidate\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(linked), "add", "tracked.txt"], check=True)
        subprocess.run(
            ["git", "-C", str(linked), "commit", "-m", "candidate"], check=True
        )
        subprocess.run(
            [
                "git",
                "-C",
                str(linked),
                "push",
                "origin",
                f"HEAD:{phase0.SHIP_TARGET_BRANCH}",
            ],
            check=True,
        )
        return subprocess.run(
            ["git", "-C", str(linked), "rev-parse", "HEAD"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()

    def test_project_config_rejects_machine_owned_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = Path(temp_dir) / "config.toml"
            config.write_text('model = "machine-owned"\n', encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(PHASE0), "config-policy", str(config)],
                cwd=ROOT,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        self.assertEqual(2, result.returncode)
        self.assertIn("machine-owned", result.stderr)

    def test_poisoned_provider_environment_is_removed(self) -> None:
        env = dict(os.environ)
        env["ANTHROPIC_API_KEY"] = "must-not-survive"
        env["OPENAI_API_KEY"] = "must-not-survive"
        result = subprocess.run(
            [sys.executable, str(PHASE0), "secrets-control"],
            cwd=ROOT,
            env=env,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn("must-not-survive", result.stdout)

    def test_deliberate_failure_preserves_nonzero_status(self) -> None:
        result = subprocess.run(
            [sys.executable, str(PHASE0), "deliberate-failure"],
            cwd=ROOT,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(42, result.returncode)
        self.assertIn("intentional phase-0 delivery failure control", result.stderr)

    def test_ship_rejects_an_unsafe_checkout(self) -> None:
        marker = ROOT / ".phase0-ship-test-marker"
        marker.write_text("negative control\n", encoding="utf-8")
        try:
            result = subprocess.run(
                [sys.executable, str(PHASE0), "ship"],
                cwd=ROOT,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        finally:
            marker.unlink(missing_ok=True)
        self.assertEqual(2, result.returncode)
        self.assertIn("ship blocked:", result.stderr)

    def test_worktree_sync_rejects_dirty_canonical_checkout(self) -> None:
        with isolated_git_environment(), tempfile.TemporaryDirectory() as temp_dir:
            remote, canonical, linked = self.create_worktree_fixture(temp_dir)
            original_head = subprocess.run(
                ["git", "-C", str(canonical), "rev-parse", "HEAD"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
            self.publish_linked_change(linked)
            (canonical / "tracked.txt").write_text("protected evidence\n", encoding="utf-8")
            result = phase0.sync_canonical_checkout(
                repository=linked,
                expected_origin=str(remote),
            )
            observed_head = subprocess.run(
                ["git", "-C", str(canonical), "rev-parse", "HEAD"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
        self.assertEqual(2, result)
        self.assertEqual(original_head, observed_head)

    def test_worktree_sync_preserves_then_fast_forwards(self) -> None:
        with isolated_git_environment(), tempfile.TemporaryDirectory() as temp_dir:
            remote, canonical, linked = self.create_worktree_fixture(temp_dir)
            expected_head = self.publish_linked_change(linked)
            (canonical / "tracked.txt").write_text("candidate\n", encoding="utf-8")
            result = phase0.sync_canonical_checkout(
                preserve_dirty=True,
                repository=linked,
                expected_origin=str(remote),
            )
            observed_head = subprocess.run(
                ["git", "-C", str(canonical), "rev-parse", "HEAD"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
            status = subprocess.run(
                ["git", "-C", str(canonical), "status", "--porcelain"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout
            stash = subprocess.run(
                ["git", "-C", str(canonical), "rev-parse", "refs/stash"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout.strip()
        self.assertEqual(0, result)
        self.assertEqual(expected_head, observed_head)
        self.assertEqual("", status)
        self.assertEqual(40, len(stash))

    def test_forged_delivery_receipt_does_not_unlock_gate(self) -> None:
        marker = ROOT / "docs/receipts/phase-0/merged.json"
        original = marker.read_bytes() if marker.exists() else None
        marker.write_text(json.dumps({"pr": 1, "remote_sha": "forged", "review": {}, "checks": {}}))
        try:
            result = subprocess.run(
                [sys.executable, str(PHASE0), "delivery-gate", "ship"],
                cwd=ROOT,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        finally:
            if original is None:
                marker.unlink(missing_ok=True)
            else:
                marker.write_bytes(original)
        self.assertEqual(2, result.returncode)
        self.assertIn("schema is invalid", result.stderr)

    def test_prototype_review_bypass_is_explicit_and_opt_in(self) -> None:
        marker = ROOT / "docs/receipts/phase-0/merged.json"
        original = marker.read_bytes() if marker.exists() else None
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
        receipt = {
            "schema": 1,
            "pr": 4,
            "remote_sha": head,
            "review": {
                "decision": "PROTOTYPE_BYPASS",
                "authorization": "--prototype-bypass-review",
            },
            "checks": {"check": "SUCCESS"},
        }
        marker.write_text(json.dumps(receipt), encoding="utf-8")
        try:
            default_result = subprocess.run(
                [sys.executable, str(PHASE0), "delivery-gate", "land"],
                cwd=ROOT,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            bypass_result = subprocess.run(
                [
                    sys.executable,
                    str(PHASE0),
                    "delivery-gate",
                    "land",
                    "--prototype-bypass-review",
                ],
                cwd=ROOT,
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        finally:
            if original is None:
                marker.unlink(missing_ok=True)
            else:
                marker.write_bytes(original)
        self.assertEqual(2, default_result.returncode)
        self.assertIn("schema is invalid", default_result.stderr)
        self.assertEqual(2, bypass_result.returncode)
        self.assertNotIn("schema is invalid", bypass_result.stderr)
        self.assertIn("explicit prototype review bypass is active", bypass_result.stderr)
        self.assertIn("origin/main does not equal receipt SHA", bypass_result.stderr)

    def test_only_declared_required_checks_gate_delivery(self) -> None:
        live = {
            "statusCheckRollup": [
                {"name": "check", "conclusion": "SUCCESS"},
                {"name": "optional-health", "conclusion": "FAILURE"},
            ]
        }
        self.assertTrue(phase0.live_checks_match(live, {"check": "SUCCESS"}))
        self.assertFalse(phase0.live_checks_match(live, {"missing": "SUCCESS"}))


if __name__ == "__main__":
    unittest.main()
