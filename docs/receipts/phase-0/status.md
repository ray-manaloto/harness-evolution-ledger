# Phase-0 acceptance status

Product slice 1 remains closed while any row is blocked or pending.

| # | Acceptance item | Status | Evidence or blocker |
| --- | --- | --- | --- |
| 1 | Correct clean local Codex project | Proven locally | Codex Desktop lists saved project `harness-evolution-ledger` at the canonical repository path; completion work is isolated on `codex/phase-0-bootstrap-completion` from exact SHA `703168b3bc413f075bea8c0d712abd16e6d3817d`, and the committed candidate passed from a clean clone |
| 2 | Required capability inventory and controls | **Blocked on Exa** | Sanitized plugin inventory is complete. Last30Days v3.21.1 preflight was safe/read-only and its bounded positive query exited 0 with byte-exact ignored evidence plus a tracked projection. Exa is installed/enabled but exposes no callable tool in this task, so no positive control exists |
| 3 | Root instructions load without truncation | Proven in CLI and current task | Fresh root and nested CLI sessions reported the complete 33-line root instruction chain; the current Codex worktree task also received the root `AGENTS.md` instruction context |
| 4 | Trusted project Codex settings only | Static proven; runtime blocked | Strict fresh CLI start and positive/negative TOML controls pass; a saved project now exists, but a fresh trusted canonical-project session has not produced the repository hook's `.git/hel/hooks.jsonl` runtime record |
| 5 | Codex and Git hooks both directions | Proven locally | `mise run hooks:verify` exercised lifecycle allow/deny/redaction/malformed/queue controls and both hk hook directions |
| 6 | Command rules controls | Proven locally | `mise run rules:verify` discriminated 17 controls; all raw pushes are forbidden, including a force flag after the refspec, while cleanup inventory remains allowed |
| 7 | Clean host clone and immutable devcontainer | Proven locally | Immutable multi-arch index, fresh automated post-create, verified locked install, and semantic P2996 reflection gate pass; committed functional candidate `36f6794ee13cbeac10e435c37a5419919d46d442` passed all seven public host tasks in an independent clean clone |
| 8 | Scoped Keychain/Doppler/fnox route | **Blocked** | Poisoned child control passes, but `DOPPLER_TOKEN` is absent so live provider usability is unproven |
| 9 | Shared CI and blocking failure control | Local proven; remote candidate pending | Exact PR head `703168b3bc413f075bea8c0d712abd16e6d3817d` has two successful `check` runs and one deliberate-control failure (`32918827009`). Because that failure shares the PR check context, PR #4 is genuinely unstable. The local workflow moves the failure control to explicit dispatch on a dedicated control ref; it needs authorized publication and exact-SHA remote proof |
| 10 | Reviewed PR merged to remote `main` | **Blocked** | PR #4 remains draft with no approving review. Repowise fails because health fell 10.0 to 8.5 against a 0.3 budget, with four complexity warnings. The local candidate decomposes the flagged methods, but review, remote checks, delivery receipt, and merge remain |

No `hel` slice-1 tracer files or behavior have been added.

## Completion audit notes

- Public host tasks observed during the 2026-08-27 completion pass: `setup`,
  `doctor`, `check`, `hooks:verify`, and `rules:verify` exited 0. The first
  `check` attempt exited 1 because the external Last30Days renderer's Markdown
  was not repository-formatted; that output was removed as raw evidence, a
  byte-exact ignored recapture was retained, and the normalized projection
  passed the rerun.
- `setup` installed the repository hk hooks into the shared canonical Git
  directory. This is expected Git worktree behavior and did not modify the
  canonical checkout's branch or tracked files.
- `DOPPLER_TOKEN` remains absent. `doctor` proves fnox 1.34.0 and Doppler CLI
  3.76.5 are installed, while the poisoned-child control proves common provider
  keys are removed. It does not prove Keychain-to-fnox-to-Doppler usability.
- The host CMake preset is not a public entry point. `mise run configure`, used
  by the public build/check tasks, injects the exact locked Clang++ 23.1.0
  binary; direct CMake invocation is forbidden by command policy. This accounts
  for the review request to avoid ambient compiler selection without duplicating
  a machine-specific path in `CMakePresets.json`.
- Every portable executable used by public tasks is pinned in the repository
  `mise.toml`; transitive Conda package URLs and checksums are retained in
  `mise.lock`. The mise bootstrap itself is enforced at 2026.8.14 by
  `min_version`, CI, and the devcontainer because mise must start before it can
  load project tools. `mise run dependencies:verify` loads a tracked empty
  `MISE_CONFIG_DIR` and proves 25 tools plus 28 commands resolve from the
  repository. Git, GitHub CLI, Bash, coreutils, and LLVM are therefore not
  inherited from user configuration, Homebrew, or the macOS system. Under that
  isolated config, `mise outdated -b --local -J` exited 0 with `{}`.
- The first independent clone run made `syft dir:.` resolve too broadly through
  macOS's `/var` to `/private/var` path alias. It exited 0 with permission
  warnings, so that SBOM was rejected as proof. The task now passes Syft Git's
  explicit repository root. The clean-clone rerun of functional candidate
  `36f6794ee13cbeac10e435c37a5419919d46d442` passed without those warnings.
