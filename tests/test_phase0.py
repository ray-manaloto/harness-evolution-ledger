from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import json


ROOT = Path(__file__).resolve().parents[1]
PHASE0 = ROOT / "scripts/phase0.py"


class Phase0PolicyTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
