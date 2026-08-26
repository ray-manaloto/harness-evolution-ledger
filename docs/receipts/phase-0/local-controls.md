# Phase-0 local control receipt

Observed 2026-08-25 on macOS arm64. Commands ran from the repository root unless
an explicit container command is shown. No credential values were printed.

## Host gates

| Command | Exit | Exact control result |
| --- | ---: | --- |
| `mise run setup` | 0 | Locked tools installed; local pre-commit and pre-push hooks installed; doctor completed |
| `mise run check` | 0 | Format, lint, clang-tidy, CMake build, CTest, Python controls, config policy, and poisoned environment passed |
| `mise run hooks:verify` | 0 | Codex lifecycle harness plus hk pre-commit/pre-push passed; both forced hk failures were preserved |
| `mise run rules:verify` | 0 | Fourteen allow, prompt, and forbidden command controls discriminated correctly |
| `mise run security` | 0 | `scanned ~1901779 bytes`; `no leaks found` |
| `mise run sbom` | 0 | SPDX JSON generated as `build/phase0.spdx.json` |
| `mise run control:fail` | 42 | stderr: `intentional phase-0 delivery failure control`; mise reported `ERROR task failed` |

The first SBOM run exited 0 but warned that no explicit source name/version was
provided. The task now supplies `harness-evolution-ledger` and `git rev-parse HEAD`;
the rerun exited 0 without that warning.

`mise run tools:lock` resolved 111 exact platform entries and reported 22 skipped
tool/platform combinations. The versioned lockfile preserves the resolved entries;
the skipped combinations are not claimed as tested. Exact host stdout, stderr,
timestamps, and statuses for the seven final controls are retained in
`docs/receipts/phase-0/host-controls.json`.

Host doctor identities:

```text
mise 2026.8.13 macos-arm64 (2026-08-25)
cmake 4.4.3
ninja 1.13.2
Homebrew clang 22.1.8
Homebrew LLVM clang-tidy 22.1.8
hk 1.56.1
fnox 1.34.0
Doppler CLI 3.76.5
codex-cli 0.149.1
```

`DOPPLER_TOKEN`, `ANTHROPIC_API_KEY`, and `OPENAI_API_KEY` were absent. The
poisoned child-process control removed common Anthropic and OpenAI key variables.

## Fresh Codex CLI controls

Root session `01a03b84-b7b1-76c3-b59b-4e4d364e43b1` exited 0 and reported the
repository root plus the complete root `AGENTS.md` from `# Harness Evolution
Ledger` through `## Gates`.

Nested session `01a03b85-1d7d-74b2-b5e3-12756fd24e6c` started in `tests/`, exited
0, resolved the repository root, reported the same complete instruction chain, and
parsed `.codex/config.toml` with Boolean `features.hooks = true`.

Both sessions warned that hook trust was bypassed for the audited automation,
`chronicle` is under development, a plugin SessionEnd timeout was clamped to three
seconds, Exa required OAuth, and skill descriptions were shortened. The read-only
nested shell also emitted macOS sandbox warnings because `git` could not create an
`xcrun` cache file under `/tmp`; the Git command still returned the correct root.

Project lifecycle behavior is proven by `mise run hooks:verify`, but these CLI
sessions did not create the project hook's expected `.git/hel/hooks.jsonl` record.
Actual trusted-project hook loading therefore remains blocked on saving and opening
this repository as its own Codex Desktop local project.

## Devcontainer controls

Immutable image index:

```text
ghcr.io/ray-manaloto/dotfiles-devcontainer@sha256:d57c2b5dbddb8e08571dee86bbb9f239957691454de85a1401239da9396d0012
```

The exact index pull exited 0 and Docker selected the immutable arm64 manifest.
The initial `devcontainer up` exited 1 because
`remoteUser=devcontainer` named no passwd entry. Image inspection showed root as the
default user and `ubuntu` as the development account; the corrected control uses
`ubuntu`.

The next post-create exited 1 because image mise 2026.8.5 was below the then-declared
minimum 2026.8.13. After setting the compatibility floor to the image version, the
locked install exited 1 again because image system settings disabled verification
required by lockfile GitHub attestations for fnox, Doppler CLI, and rumdl.

The repository now creates a user-local mise 2026.8.13 and explicitly enables
`github_attestations=true` and `slsa=true`. The opposing rerun printed each of:

```text
fnox 1.34.0: GitHub artifact attestations verified
Doppler CLI 3.76.5: GitHub artifact attestations verified
rumdl 0.2.60: GitHub artifact attestations verified
```

The first shared container check exited 1 because it encountered the host CMake
cache. Separate `host-debug` and `container-debug` paths corrected that boundary.
The first container configure then selected GNU 15.2.0; this was rejected as a
P2996 control. A fresh configure selected:

```text
Clang 21.0.0
/opt/clang-p2996/bin/clang++
https://github.com/bloomberg/clang-p2996.git
7220baffd57ea5b0f8cf59bee494dd5b7cc2b748
```

The subsequent in-container `mise run check` exited 0. Its P2996 control compiled
`^^int`, checked `std::meta::is_type`, and linked with `-freflection-latest`;
both CTest cases passed. clang-tidy used `build/container-debug`, and the same
config and secret controls passed.

Finally, `devcontainer up --workspace-folder . --remove-existing-container` ran the
checked-in post-create handler without manual intervention and exited 0. It returned
container `bf5ed19b4ba90b7c8abb3528048a7f71afc91a79515a1b8323dcf92a56b5d483`,
remote user `ubuntu`, and workspace `/workspaces/harness-evolution-ledger`. The bind
mount still contained the earlier `build/container-debug` output, so an independent
clean committed clone remains a distinct acceptance control.

The container has an intentionally isolated Codex home. Its doctor reported the
eight account plugins missing; account-plugin exercise belongs to the host, while
the container proves repository tools, compilation, tests, hooks, rules, and secret
environment separation.
