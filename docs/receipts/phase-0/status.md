# Phase-0 acceptance status

Product slice 1 remains closed while any row is blocked or pending.

| # | Acceptance item | Status | Evidence or blocker |
| --- | --- | --- | --- |
| 1 | Correct clean local Codex project | **Blocked** | Git checkout/branch are correct, but Codex Desktop has no saved project bound to this folder |
| 2 | Required capability inventory and controls | **Blocked** | Complete sanitized 60-plugin inventory plus required manifest prepared; Exa OAuth and Last30Days TLS positive controls remain unresolved |
| 3 | Root instructions load without truncation | Proven in CLI; Desktop blocked | Fresh root and nested CLI sessions reported the complete 33-line root instruction chain; saved-project control remains blocked |
| 4 | Trusted project Codex settings only | Static proven; runtime blocked | Strict fresh CLI start and positive/negative TOML controls pass; repository hook runtime load remains unproven without a saved trusted project |
| 5 | Codex and Git hooks both directions | Proven locally | `mise run hooks:verify` exercised lifecycle allow/deny/redaction/malformed/queue controls and both hk hook directions |
| 6 | Command rules controls | Proven locally | `mise run rules:verify` discriminated 14 allow/prompt/forbidden commands, including cleanup, push, direct-tool, and mise mutation paths |
| 7 | Clean host clone and immutable devcontainer | Container proven; clone pending | Immutable multi-arch index, fresh automated post-create, verified locked install, and semantic P2996 reflection gate pass; clean committed clone remains |
| 8 | Scoped Keychain/Doppler/fnox route | **Blocked** | Poisoned child control passes, but `DOPPLER_TOKEN` is absent so live provider usability is unproven |
| 9 | Shared CI and blocking failure control | Local proven; remote pending | Exact candidate-SHA workflow and local exit-42 failure pass; remote labeled-failure and green rerun remain |
| 10 | Reviewed PR merged to remote `main` | Pending | Requires commit, push, independent review, checks, receipt, and merge authority |

No `hel` slice-1 tracer files or behavior have been added.
