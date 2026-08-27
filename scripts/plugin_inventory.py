#!/usr/bin/env python3
"""Write a sanitized inventory of every installed account-scoped plugin."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/tooling/account-plugin-inventory.json"


def interface_inventory(source: Path) -> dict[str, object]:
    skills = sorted(
        str(path.relative_to(source).parent)
        for path in source.glob("**/SKILL.md")
        if ".git" not in path.parts
    )
    return {
        "skills": skills,
        "mcp_server_declared": (source / ".mcp.json").is_file(),
        "hooks_declared": any((source / name).is_file() for name in ("hooks/hooks.json", "hooks.json")),
    }


def main() -> int:
    result = subprocess.run(
        ["codex", "plugin", "list", "--json"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise RuntimeError(f"codex plugin inventory failed: {result.stderr.strip()}")
    document = json.loads(result.stdout)
    plugins: list[dict[str, object]] = []
    for raw in sorted(document.get("installed", []), key=lambda item: item["pluginId"]):
        source_data = raw.get("source", {})
        source_path = Path(str(source_data.get("path", "")))
        interfaces = interface_inventory(source_path) if source_path.is_dir() else {
            "skills": [],
            "mcp_server_declared": False,
            "hooks_declared": False,
        }
        plugins.append(
            {
                "plugin_id": raw["pluginId"],
                "version": raw.get("version"),
                "installed": bool(raw.get("installed")),
                "enabled": bool(raw.get("enabled")),
                "permissions": raw.get("installPolicy"),
                "authentication": raw.get("authPolicy"),
                **interfaces,
            }
        )
    payload = {
        "schema": 1,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "source_command": "codex plugin list --json",
        "machine_paths_retained": False,
        "plugin_count": len(plugins),
        "plugins": plugins,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {len(plugins)} sanitized plugin records to {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
