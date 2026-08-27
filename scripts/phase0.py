#!/usr/bin/env python3
"""Dependency-free phase-0 task implementations.

The script emits only tool identity and credential presence. It never prints a
credential value and never imports sibling-repository code.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
HOST_LLVM_VERSION = "23.1.0"
HOST_LLVM_RESOURCE_VERSION = HOST_LLVM_VERSION.partition(".")[0]
MACHINE_OWNED_CODEX_KEYS = {
    "model",
    "model_provider",
    "notify",
    "profile",
    "web_search",
}
POISONED_PROVIDER_KEYS = {
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "CLAUDE_CODE_OAUTH_TOKEN",
    "CODEX_API_KEY",
    "OPENAI_ADMIN_KEY",
    "OPENAI_API_KEY",
}
ALLOWED_CHILD_KEYS = {
    "HOME",
    "LANG",
    "LC_ALL",
    "PATH",
    "SHELL",
    "SSH_AUTH_SOCK",
    "TERM",
    "TMPDIR",
    "USER",
}
REQUIRED_PLUGINS = (
    "codex-security@openai-curated",
    "context7@context7-marketplace",
    "exa@exa",
    "firecrawl@claude-plugins-official",
    "last30days@last30days-skill",
    "mattpocock-skills@mattpocock",
    "mise@brentmitchell25",
    "openai-developers@openai-curated",
)
RECEIPT_KEYS = {"schema", "pr", "remote_sha", "review", "checks"}
REQUIRED_COMMANDS = (
    "actionlint",
    "bash",
    "clang++",
    "clang-format",
    "clang-tidy",
    "cmake",
    "cmake-format",
    "codex",
    "cosign",
    "cp",
    "ctest",
    "devcontainer",
    "doppler",
    "fnox",
    "gh",
    "git",
    "gitleaks",
    "hk",
    "mkdir",
    "ninja",
    "node",
    "pkl",
    "python3",
    "rumdl",
    "shellcheck",
    "shfmt",
    "syft",
    "taplo",
)
EXPLICIT_COMMANDS = {
    "clang++": ("conda:clangxx", HOST_LLVM_VERSION, "bin/clang++"),
    "clang-format": ("conda:clang-tools", HOST_LLVM_VERSION, "bin/clang-format"),
    "clang-tidy": ("conda:clang-tools", HOST_LLVM_VERSION, "bin/clang-tidy"),
}
SHIP_REMOTE = "origin"
SHIP_SOURCE_BRANCH = "codex/phase-0-bootstrap-completion"
SHIP_TARGET_BRANCH = "codex/phase-0-bootstrap"
SHIP_ORIGIN_URL = "git@github.com:ray-manaloto/harness-evolution-ledger.git"


def run(argv: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(argv), flush=True)
    return subprocess.run(argv, cwd=ROOT, check=check, text=True)


def capture(argv: list[str]) -> tuple[int, str]:
    result = subprocess.run(
        argv,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.returncode, result.stdout.strip()


def capture_stdout(
    argv: list[str], *, env: dict[str, str] | None = None
) -> tuple[int, str]:
    result = subprocess.run(
        argv,
        cwd=ROOT,
        check=False,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
    )
    return result.returncode, result.stdout.strip()


def version(binary: str, *args: str) -> str:
    path = shutil.which(binary)
    if path is None:
        return "unavailable"
    rc, output = capture([binary, *args])
    first = output.splitlines()[0] if output else "no version output"
    return f"rc={rc} {first}"


def plugin_inventory() -> None:
    rc, output = capture(["codex", "plugin", "list", "--json"])
    if rc != 0:
        print(f"plugins=unavailable rc={rc}")
        return
    try:
        document = json.loads(output)
        installed = document.get("installed", [])
        observed = {
            item["pluginId"]: item
            for item in installed
            if isinstance(item, dict) and isinstance(item.get("pluginId"), str)
        }
    except (json.JSONDecodeError, AttributeError, KeyError, TypeError):
        print("plugins=invalid-json")
        return
    for plugin_id in REQUIRED_PLUGINS:
        item = observed.get(plugin_id)
        if item is None:
            print(f"plugin.{plugin_id}=missing")
            continue
        print(
            f"plugin.{plugin_id}=version:{item.get('version', 'unknown')} "
            f"enabled:{'yes' if item.get('enabled') else 'no'}"
        )


def cmake_preset() -> str:
    return "container-debug" if os.environ.get("DEVCONTAINER") == "true" else "host-debug"


def mise_prefix(tool: str, version_text: str) -> Path:
    rc, output = capture_stdout(["mise", "where", f"{tool}@{version_text}"])
    if rc or not output:
        raise RuntimeError(f"locked mise prefix unavailable: {tool}@{version_text}")
    return Path(output)


def host_compiler() -> Path:
    return mise_prefix("conda:clangxx", HOST_LLVM_VERSION) / "bin/clang++"


def host_clang_tool(binary: str) -> Path:
    return mise_prefix("conda:clang-tools", HOST_LLVM_VERSION) / "bin" / binary


def doctor() -> int:
    print(f"repository={ROOT}")
    print(f"platform={platform.platform()}")
    rc, branch = capture(["git", "branch", "--show-current"])
    print(f"git_branch={branch or 'detached'} rc={rc}")
    rc, head = capture(["git", "rev-parse", "HEAD"])
    print(f"git_head={head} rc={rc}")
    for binary, args in (
        ("mise", ("--version",)),
        ("bash", ("--version",)),
        ("git", ("--version",)),
        ("gh", ("--version",)),
        ("cmake", ("--version",)),
        ("ninja", ("--version",)),
        ("hk", ("--version",)),
        ("fnox", ("--version",)),
        ("doppler", ("--version",)),
        ("codex", ("--version",)),
    ):
        print(f"tool.{binary}={version(binary, *args)}")
    for binary in ("clang++", "clang-format", "clang-tidy"):
        path = host_compiler() if binary == "clang++" else host_clang_tool(binary)
        rc, output = capture([str(path), "--version"])
        first = output.splitlines()[0] if output else "no version output"
        print(f"tool.{binary}=rc={rc} {first} path={path}")
    if os.environ.get("DEVCONTAINER") != "true":
        print(f"compiler.host.selected={host_compiler()}")
    for name in (
        "DOPPLER_TOKEN",
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_AUTH_TOKEN",
        "CODEX_API_KEY",
        "OPENAI_API_KEY",
    ):
        print(f"credential.{name}.present={'yes' if os.environ.get(name) else 'no'}")
    plugin_inventory()
    print(f"codex_hooks={'present' if (ROOT / '.codex/hooks.json').is_file() else 'missing'}")
    print(f"codex_rules={'present' if (ROOT / '.codex/rules/project.rules').is_file() else 'missing'}")
    rc, _ = capture(["hk", "validate"])
    print(f"hk_config={'valid' if rc == 0 else 'invalid'} rc={rc}")
    print("compiler.gcc16.2=unavailable")
    print("compiler.clang-p2996=devcontainer-only")
    print(f"environment.devcontainer={'yes' if os.environ.get('DEVCONTAINER') else 'no'}")
    return 0


def dependency_policy() -> int:
    config_path = ROOT / "mise.toml"
    declared = set(tomllib.loads(config_path.read_text(encoding="utf-8"))["tools"])
    isolated_env = {
        **os.environ,
        "MISE_CONFIG_DIR": str(ROOT / "tests/fixtures/empty-mise-config"),
    }
    rc, output = capture_stdout(
        ["mise", "ls", "--current", "--json"], env=isolated_env
    )
    if rc:
        print("unable to inspect active mise tools", file=sys.stderr)
        return 2
    active = json.loads(output)
    failures: list[str] = []
    for tool in sorted(declared):
        entries = active.get(tool)
        local = [
            item
            for item in entries or []
            if item.get("active")
            and item.get("source", {}).get("path") == str(config_path)
        ]
        if not local:
            failures.append(f"tool is not active from repository mise.toml: {tool}")
    install_root = Path(os.environ.get("MISE_INSTALLS_DIR", Path.home() / ".local/share/mise/installs"))
    for command in REQUIRED_COMMANDS:
        explicit = EXPLICIT_COMMANDS.get(command)
        if explicit:
            tool, version_text, relative_path = explicit
            path = (mise_prefix(tool, version_text) / relative_path).resolve()
            if not path.is_file():
                failures.append(f"command is absent from its declared mise tool: {command} -> {path}")
                continue
        else:
            rc, resolved = capture_stdout(
                ["mise", "which", command], env=isolated_env
            )
            if rc or not resolved:
                failures.append(f"command is not provided by a mise tool: {command}")
                continue
            path = Path(resolved).resolve()
        if not path.is_relative_to(install_root.resolve()):
            failures.append(f"command resolved outside mise installs: {command} -> {path}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 2
    print(
        f"{len(declared)} tools and {len(REQUIRED_COMMANDS)} commands resolve from "
        "repository mise with the user config excluded"
    )
    return 0


def tracked_files(suffixes: tuple[str, ...], names: tuple[str, ...] = ()) -> list[str]:
    rc, output = capture(["git", "ls-files", "--cached", "--others", "--exclude-standard"])
    if rc != 0:
        raise RuntimeError("git ls-files failed")
    return [
        item
        for item in output.splitlines()
        if item.endswith(suffixes) or Path(item).name in names
    ]


def format_files(check_only: bool) -> int:
    cpp = tracked_files((".cpp", ".hpp", ".cc", ".hh"))
    cmake = tracked_files((".cmake",), ("CMakeLists.txt",))
    shell = tracked_files((".sh",))
    if cpp:
        formatter = str(host_clang_tool("clang-format"))
        args = [formatter, "--dry-run", "--Werror"] if check_only else [formatter, "-i"]
        run([*args, *cpp])
    if cmake:
        args = ["cmake-format", "--check"] if check_only else ["cmake-format", "-i"]
        run([*args, *cmake])
    if shell:
        args = ["shfmt", "-d"] if check_only else ["shfmt", "-w"]
        run([*args, *shell])
    run(["rumdl", "fmt", "--check", "."] if check_only else ["rumdl", "fmt", "."])
    if check_only:
        run(["taplo", "format", "--check"])
    else:
        run(["taplo", "format"])
    return 0


def lint() -> int:
    run(["rumdl", "check", "."])
    run(["taplo", "check"])
    run(["actionlint"])
    shell = tracked_files((".sh",))
    if shell:
        run(["shellcheck", *shell])
    py = tracked_files((".py",))
    if py:
        run([sys.executable, "-m", "py_compile", *py])
    run(["cmake-lint", "CMakeLists.txt"])
    if os.environ.get("DEVCONTAINER") == "true":
        tidy = Path("/usr/lib/llvm-22/bin/clang-tidy")
        extra: list[str] = []
    else:
        compiler_prefix = mise_prefix("conda:clangxx", HOST_LLVM_VERSION)
        tidy = host_clang_tool("clang-tidy")
        resource_dir = compiler_prefix / "lib/clang" / HOST_LLVM_RESOURCE_VERSION
        extra = [f"--extra-arg=-resource-dir={resource_dir}"]
    run([str(tidy), *extra, "-p", f"build/{cmake_preset()}", "tests/phase0_smoke.cpp"])
    return 0


def config_policy(path: Path | None = None) -> int:
    config_path = path or ROOT / ".codex/config.toml"
    data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    rejected = sorted(MACHINE_OWNED_CODEX_KEYS.intersection(data))
    if rejected:
        print(f"rejected machine-owned project keys: {', '.join(rejected)}", file=sys.stderr)
        return 2
    permitted = {"features", "shell_environment_policy"}
    unknown = sorted(set(data).difference(permitted))
    if unknown:
        print(f"rejected unreviewed project keys: {', '.join(unknown)}", file=sys.stderr)
        return 2
    print("project Codex config contains only reviewed project-owned keys")
    return 0


def secrets_control() -> int:
    poisoned = dict(os.environ)
    for name in POISONED_PROVIDER_KEYS:
        poisoned[name] = f"poison-{name.lower()}"
    child = {key: value for key, value in poisoned.items() if key in ALLOWED_CHILD_KEYS}
    visible = sorted(POISONED_PROVIDER_KEYS.intersection(child))
    if visible:
        print(f"provider child inherited forbidden keys: {visible}", file=sys.stderr)
        return 2
    probe = subprocess.run(
        [sys.executable, "-c", "import os; print(','.join(sorted(os.environ)))"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        env=child,
    )
    observed = set(filter(None, probe.stdout.strip().split(",")))
    leaked = sorted(POISONED_PROVIDER_KEYS.intersection(observed))
    if leaked:
        print(f"poisoned child leaked keys: {leaked}", file=sys.stderr)
        return 2
    print("poisoned API-key variables absent from scoped provider child")
    print(f"doppler_token_present={'yes' if os.environ.get('DOPPLER_TOKEN') else 'no'}")
    return 0


def consistency() -> int:
    if os.environ.get("HEL_PHASE0_FORCE_FAIL") == "1":
        print("forced negative control reached repository consistency gate", file=sys.stderr)
        return 86
    run(["git", "diff", "--check"])
    for required in (
        "AGENTS.md",
        "BOOTSTRAP.md",
        "HANDOFF.md",
        "mise.lock",
        ".codex/hooks.json",
        ".codex/rules/project.rules",
    ):
        if not (ROOT / required).exists():
            print(f"missing required phase-0 file: {required}", file=sys.stderr)
            return 2
    if (ROOT / "AGENTS.md").stat().st_size >= 12_000:
        print("AGENTS.md exceeds 12,000-byte contract", file=sys.stderr)
        return 2
    return 0


def changed() -> int:
    run(["git", "diff", "--check"])
    run(["rumdl", "check", "AGENTS.md", "BOOTSTRAP.md", "HANDOFF.md", "README.md"])
    return 0


def ship_candidate() -> int:
    """Publish the single reviewed Phase-0 candidate through a fast-forward push."""
    rc, branch_name = capture(["git", "branch", "--show-current"])
    if rc or branch_name != SHIP_SOURCE_BRANCH:
        print(f"ship blocked: current branch must be {SHIP_SOURCE_BRANCH}", file=sys.stderr)
        return 2
    rc, origin_url = capture(["git", "remote", "get-url", SHIP_REMOTE])
    if rc or origin_url != SHIP_ORIGIN_URL:
        print("ship blocked: origin URL is not the canonical repository", file=sys.stderr)
        return 2
    rc, status = capture(["git", "status", "--porcelain"])
    if rc or status:
        print("ship blocked: worktree is not clean", file=sys.stderr)
        return 2

    source_ref = f"refs/heads/{SHIP_SOURCE_BRANCH}"
    target_ref = f"refs/heads/{SHIP_TARGET_BRANCH}"
    tracking_ref = f"refs/remotes/{SHIP_REMOTE}/{SHIP_TARGET_BRANCH}"
    run(["git", "fetch", "--no-tags", SHIP_REMOTE, f"{target_ref}:{tracking_ref}"])
    rc, source_sha = capture(["git", "rev-parse", source_ref])
    if rc:
        print("ship blocked: source branch is unavailable", file=sys.stderr)
        return 2
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", tracking_ref, source_ref],
        cwd=ROOT,
        check=False,
    )
    if ancestry.returncode:
        print("ship blocked: publication would not be a fast-forward", file=sys.stderr)
        return 2

    run(["git", "push", SHIP_REMOTE, f"{source_ref}:{target_ref}"])
    rc, published = capture(["git", "ls-remote", "--heads", SHIP_REMOTE, target_ref])
    fields = published.split()
    if rc or len(fields) != 2 or fields[0] != source_sha or fields[1] != target_ref:
        print("ship failed: remote target does not match the candidate SHA", file=sys.stderr)
        return 2
    print(f"ship published {source_sha} to {SHIP_REMOTE}/{SHIP_TARGET_BRANCH}")
    return 0


def valid_receipt_values(data: dict[str, object]) -> bool:
    if set(data) != RECEIPT_KEYS or data.get("schema") != 1:
        return False
    pr = data.get("pr")
    remote_sha = data.get("remote_sha")
    review = data.get("review")
    checks = data.get("checks")
    if not isinstance(pr, int) or not isinstance(remote_sha, str):
        return False
    if len(remote_sha) != 40 or any(character not in "0123456789abcdef" for character in remote_sha):
        return False
    if not isinstance(review, dict) or review.get("decision") != "APPROVED":
        return False
    reviewer = review.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer:
        return False
    return isinstance(checks, dict) and bool(checks) and all(
        value == "SUCCESS" for value in checks.values()
    )


def live_review_approved(live: dict[str, object], reviewer: str) -> bool:
    author_value = live.get("author")
    author = author_value.get("login") if isinstance(author_value, dict) else None
    reviews = live.get("reviews")
    if not isinstance(reviews, list):
        return False
    return reviewer != author and any(
        isinstance(item, dict)
        and item.get("state") == "APPROVED"
        and isinstance(item.get("author"), dict)
        and item["author"].get("login") == reviewer
        for item in reviews
    )


def live_checks_match(live: dict[str, object], declared: dict[str, object]) -> bool:
    checks = live.get("statusCheckRollup")
    if not isinstance(checks, list) or not checks:
        return False
    if not all(isinstance(item, dict) and item.get("conclusion") == "SUCCESS" for item in checks):
        return False
    successful_names = {item.get("name") or item.get("context") for item in checks}
    return set(declared).issubset(successful_names)


def live_delivery_matches(live: dict[str, object], data: dict[str, object]) -> bool:
    review = data["review"]
    checks = data["checks"]
    merge_commit = live.get("mergeCommit")
    merged_sha = merge_commit.get("oid") if isinstance(merge_commit, dict) else None
    return (
        live.get("state") == "MERGED"
        and merged_sha == data["remote_sha"]
        and live_review_approved(live, review["reviewer"])
        and live_checks_match(live, checks)
    )


def delivery_gate(operation: str) -> int:
    marker = ROOT / "docs/receipts/phase-0/merged.json"
    if not marker.is_file():
        print(f"{operation} blocked: phase-0 merged receipt is absent", file=sys.stderr)
        return 2
    data = json.loads(marker.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not valid_receipt_values(data):
        print(f"{operation} blocked: merged receipt schema is invalid", file=sys.stderr)
        return 2
    pr = data.get("pr")
    remote_sha = data.get("remote_sha")
    rc, local_head = capture(["git", "rev-parse", "HEAD"])
    if rc or local_head != remote_sha:
        print(f"{operation} blocked: local HEAD does not equal receipt SHA", file=sys.stderr)
        return 2
    rc, remote_main = capture(["git", "rev-parse", "origin/main"])
    if rc or remote_main != remote_sha:
        print(f"{operation} blocked: origin/main does not equal receipt SHA", file=sys.stderr)
        return 2
    result = subprocess.run(
        [
            "gh", "pr", "view", str(pr), "--repo", "ray-manaloto/harness-evolution-ledger",
            "--json", "state,mergeCommit,author,reviews,statusCheckRollup",
        ],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        print(f"{operation} blocked: live PR verification unavailable", file=sys.stderr)
        return 2
    live = json.loads(result.stdout)
    if not isinstance(live, dict) or not live_delivery_matches(live, data):
        print(f"{operation} blocked: live PR, review, SHA, or checks do not match", file=sys.stderr)
        return 2
    print(f"{operation} prerequisites verified live at {remote_sha}")
    return 0


def dispatch_simple(command: str, argv: list[str]) -> int | None:
    simple_commands = {
        "doctor": doctor,
        "format": lambda: format_files(False),
        "format-check": lambda: format_files(True),
        "lint": lint,
        "secrets-control": secrets_control,
        "dependency-policy": dependency_policy,
        "consistency": consistency,
        "changed": changed,
    }
    if command in simple_commands and len(argv) == 2:
        return simple_commands[command]()
    return None


def dispatch_build(command: str) -> int | None:
    if command == "configure":
        argv = ["cmake", "--preset", cmake_preset()]
        if os.environ.get("DEVCONTAINER") != "true":
            argv.append(f"-DCMAKE_CXX_COMPILER={host_compiler()}")
        run(argv)
        return 0
    if command == "build":
        run(["cmake", "--build", "--preset", cmake_preset()])
        return 0
    if command == "ctest":
        run(["ctest", "--preset", cmake_preset()])
        return 0
    return None


def dispatch_policy(command: str, argv: list[str]) -> int | None:
    if command == "config-policy":
        path = Path(argv[2]) if len(argv) == 3 else None
        return config_policy(path)
    if command == "deliberate-failure":
        print("intentional phase-0 delivery failure control", file=sys.stderr)
        return 42
    if command == "ship" and len(argv) == 2:
        return ship_candidate()
    if command == "delivery-gate" and len(argv) == 3:
        return delivery_gate(argv[2])
    return None


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: phase0.py COMMAND", file=sys.stderr)
        return 2
    command = sys.argv[1]
    for dispatcher in (dispatch_simple, dispatch_policy):
        result = dispatcher(command, sys.argv)
        if result is not None:
            return result
    result = dispatch_build(command)
    if result is not None:
        return result
    print(f"unknown command: {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
