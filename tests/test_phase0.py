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

    def test_forged_delivery_receipt_does_not_unlock_gate(self) -> None:
        marker = ROOT / "docs/receipts/phase-0/merged.json"
        self.assertFalse(marker.exists(), "test requires no genuine merged receipt")
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
            marker.unlink(missing_ok=True)
        self.assertEqual(2, result.returncode)
        self.assertIn("schema is invalid", result.stderr)


if __name__ == "__main__":
    unittest.main()
