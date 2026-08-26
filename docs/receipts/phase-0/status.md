# Phase-0 acceptance status

Product slice 1 remains closed while any row is blocked or pending.

| # | Acceptance item | Status | Evidence or blocker |
| --- | --- | --- | --- |
| 1 | Correct clean local Codex project | **Blocked** | Git checkout/branch are correct, but Codex Desktop has no saved project bound to this folder |
| 2 | Required capability inventory and controls | **Blocked** | Complete sanitized 60-plugin inventory plus required manifest prepared; Exa OAuth and Last30Days TLS positive controls remain unresolved |
| 3 | Root instructions load without truncation | Proven in CLI; Desktop blocked | Fresh root and nested CLI sessions reported the complete 33-line root instruction chain; saved-project control remains blocked |
| 4 | Trusted project Codex settings only | Static proven; runtime blocked | Strict fresh CLI start and positive/negative TOML controls pass; repository hook runtime load remains unproven without a saved trusted project |
| 5 | Codex and Git hooks both directions | Proven locally | `mise run hooks:verify` exercised lifecycle allow/deny/redaction/malformed/queue controls and both hk hook directions |
| 6 | Command rules controls | Proven locally | `mise run rules:verify` discriminated 17 controls; cleanup inventory is allowed while apply paths are forbidden or prompted |
| 7 | Clean host clone and immutable devcontainer | Container proven; clone pending | Immutable multi-arch index, fresh automated post-create, verified locked install, and semantic P2996 reflection gate pass; clean committed clone remains |
| 8 | Scoped Keychain/Doppler/fnox route | **Blocked** | Poisoned child control passes, but `DOPPLER_TOKEN` is absent so live provider usability is unproven |
| 9 | Shared CI and blocking failure control | Local proven; remote pending | Runs `32918067811` and `32918389481` exposed ambient-compiler and analyzer-prefix bugs; neither counts as the deliberate control. Green and labeled-failure runs remain |
| 10 | Reviewed PR merged to remote `main` | Draft PR open | PR #4 is deliberately draft while blockers remain; independent review, exact-SHA green checks, failure control, receipt, and merge remain |

No `hel` slice-1 tracer files or behavior have been added.
