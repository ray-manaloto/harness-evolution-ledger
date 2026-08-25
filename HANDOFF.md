# Harness Evolution Ledger handoff

## Start here

This repository is the standalone home of **Harness Evolution Ledger**, provisionally named
`harness-evolution-ledger`, with the CLI name `hel`.

Use this authority order:

1. [GitHub issue #1](https://github.com/ray-manaloto/harness-evolution-ledger/issues/1) is the complete product specification and decision record.
2. This document defines how the next thread resumes work.
3. [BOOTSTRAP.md](BOOTSTRAP.md) defines the phase-0 Codex project and repository setup contract.
4. Live repository, compiler, dependency, provider-policy, and tool output override stale observations.

Read issue #1, this handoff, and `BOOTSTRAP.md` in full before planning or editing. Completion
criterion: the working plan completes phase 0 before slice 1, maps later steps to the specification's
six delivery slices, and names the first externally testable receipt.

## Current state

- GitHub repository: `ray-manaloto/harness-evolution-ledger`.
- Local checkout: `/Users/rmanaloto/dev/github/ray-manaloto/harness-evolution-ledger`.
- Default branch: `main`.
- Initial remote commit before this handoff: `2477bf8` (`Initial commit`).
- Product specification: open issue #1 with only the `ready-for-agent` label.
- Implementation: not started. The repository contained only its initial README before this handoff.
- License decision: Apache-2.0; the license file still needs to be added during bootstrap.
- Knowledge-base issue #515 was transferred here and became issue #1. Its links back to
  `ray-manaloto/knowledge-base` are fully qualified.

Verify all of the above from the live checkout and GitHub before relying on it. The new thread must
report the observed branch, HEAD, remote, worktree state, and issue state before its first mutation.

## Product boundary

Build a local-first, single-user C++26 engine that:

1. captures or ingests every available Claude Code and Codex command, request, response, tool call,
   result, artifact, diff, process state, Git state, hook event, OpenTelemetry event, and provider
   artifact within a configured project boundary;
2. preserves original bytes in encrypted content-addressed storage plus an append-only manifest;
3. derives replaceable SQLite, PostgreSQL, and DuckDB projections for query and analysis;
4. reconstructs and replays sessions with explicit fidelity, omission, and substitution records;
5. extracts evidence-linked failures, inefficiencies, tasks, and candidate hypotheses;
6. generates independent atomic candidates in isolated worktrees;
7. evaluates them against an exact baseline, sealed fixtures, temporal held-out evidence, adversarial
   cases, and independent real harnesses;
8. canaries one candidate under project policy; and
9. promotes accepted work through auditable Git changes and rolls regressions back with revert
   commits.

The system must distinguish capture, analysis, proposal, local validation, held-out evaluation,
canary, promotion, and durable success. An artifact, green unit test, queued job, or generated
candidate is not evidence that a later state was reached.

## Confirmed constraints

### Platform and toolchain

- C++26 only.
- GCC 16.2 static reflection is the release authority.
- An exact Bloomberg LLVM/Clang P2996 commit is a differential lane only and never publishes release
  artifacts.
- macOS ARM64 and Linux ARM64/x86-64 are supported.
- Windows is outside the current scope.
- Use CMake Presets, Ninja, and a pinned vcpkg manifest with overlay ports where exact variants are
  unavailable.
- Use Glaze for typed JSON/NDJSON and reflection integration; preserve original bytes outside Glaze.
- Use openalgz/ut plus CTest, with separate fuzzing, ASan/UBSan, and TSan lanes.

Compiler availability, flags, dependency versions, upstream commits, package names, and licenses are
drift-prone. Verify them from primary sources before pinning. Record the exact evidence in the pull
request or repository decision record.

### Source of truth and storage

- Immutable encrypted raw blobs plus an append-only manifest are authoritative.
- Database tables and indexes are rebuildable projections.
- Compression precedes authenticated encryption.
- The selected design uses zstd, libsodium secretstream XChaCha20-Poly1305, keyed per-project BLAKE3
  addressing, and per-project wrapped keys.
- SQLite is preferred for local operation if it passes conformance.
- Bake off stock SQLite, sqlite-vec, SQLCipher, and the proposed Boost.SQLite wrapper against the same
  public behavior. Boost.SQLite is preferred but not trusted: isolate it behind a project-owned facade
  and disqualify it on any hard ownership, cancellation, WAL, backup, encryption, extension, hook, or
  replacement-parity failure.
- DuckDB is for analytics and Parquet, never ingestion authority.
- PostgreSQL is an optional asynchronous projection, never a prerequisite for raw capture.
- Full-text search is the baseline; local embeddings require measured need and redaction first.

### Providers and external adapters

- Claude Code and Codex are the only v1 provider claims.
- Antigravity and DeepSeek receive reserved adapter identities and fixtures, not support claims.
- Use local subscription-authenticated vendor tools. Never silently fall back to separately billed API
  credentials.
- Before provider execution, prove login state, executable/version, sanitized environment, and current
  plan/policy eligibility.
- Remove common Anthropic and OpenAI API-key variables from child environments.
- Integrate external tools out of process through exact-pinned, versioned adapters with conformance
  fixtures. Unknown versions quarantine input.
- Planned adapter roles are AgentsView for discovery/search/export, Promptfoo for primary comparative
  evaluation, SkillOpt-Sleep for eligible text assets, direct isolated Claude/Codex generation for code
  and infrastructure, and agent-skill-eval as an independent real-harness evaluator.

Subscription behavior and vendor terms are drift-prone. Reverify them before implementing a provider
path and retain a policy receipt. Do not turn previous research into a permanent support promise.

### Security and authority

- Treat every captured byte as hostile data.
- Captured content cannot change policy, capabilities, adapter allowlists, or approvals.
- Credentials are resolved only into the narrowly scoped process that needs them. The established host
  route is macOS Keychain to `DOPPLER_TOKEN`, Doppler values, fnox declarations, then a sanitized process
  environment.
- Replays use current scoped credentials, never captured credential values.
- Project data classification and provider retention eligibility govern model egress.
- Credentials stay out of model input by default. Redact before embedding.
- Irreversible external actions and capability expansion require a fresh human approval bound to an
  immutable action digest with expiry.
- Dirty worktrees are protected evidence. Build candidates from the exact accepted baseline in
  registered isolated worktrees.
- Rollback creates an auditable revert commit; it does not reset, clean, or erase history.
- Emergency stop disables hooks, schedules, model calls, canaries, promotions, and external actions
  while preserving read-only capture and query.

### Repository-specific pilot policy

`ray-manaloto/knowledge-base` is the first approved pilot and reference producer, but it remains a
separate repository. Its Claude-only corpus invariant is a hard project policy: the engine may parse
and store Codex telemetry locally, but it cannot send knowledge-base corpus content to Codex, OpenAI,
DeepSeek, Gemini, or another non-Claude model.

`ray-manaloto/dotfiles` remains a separate integration consumer and owns the immutable devcontainers,
host credential route, schedules, and downstream release consumption. Work in this repository does not
authorize modifications to either sibling repository. Coordinate changes through explicit contracts
and repository-owned pull requests.

## Public behavior and test seam

The primary test seam is the public `hel` CLI over an isolated real fixture project. Prefer one
end-to-end behavioral path over many implementation-coupled seams:

`capture/ingest → query/replay → task → candidates → evaluate → canary → promote → regression → rollback`

Assert stable JSON, raw evidence, audit/approval records, process outcomes, and Git state. Avoid tests
that bind private classes, reflection layout, SQL table shape, or logging call counts.

Subordinate conformance suites cover adapters, storage engines, compilers, recovery, security, and
authorization. Every claimed guard needs an opposite-direction control arm that demonstrates it can
fail. Mocks may support unit development but cannot certify provider, evaluator, replay, optimizer, or
promotion behavior.

## Delivery sequence

Implement the six specification slices in order:

1. capture, encryption, raw manifest, audit, and query;
2. storage/add-on bakeoff and projections;
3. task extraction, replay, Promptfoo, and agent-skill-eval;
4. SkillOpt and direct candidate generation;
5. isolated-worktree promotion, live canary, automatic adoption, and rollback;
6. external actions and later team controls.

Each slice must retain a real externally inspectable receipt. Later-slice scaffolding does not complete
an earlier slice, and an earlier slice does not imply the later loop works.

## First thread objective

Bootstrap a trustworthy slice-1 foundation; do not attempt the entire issue in one change.

1. Verify repository, issue #1, branch, HEAD, remotes, and clean worktree.
2. Read issue #1, this handoff, and `BOOTSTRAP.md` completely. Treat the issue as authority if wording
   differs and complete the bootstrap document's phase-0 acceptance before product implementation.
3. Create a working branch from current `origin/main`; preserve any unexpected worktree changes and
   stop to classify them before editing.
4. Establish lightweight repository instructions for both Claude and Codex that point to issue #1 and
   this handoff without duplicating them.
5. Add Apache-2.0 licensing, the CMake/vcpkg/preset skeleton, formatting/lint/test tasks, and CI only to
   the extent required to run one red-to-green external contract.
6. Write the smallest vertical tracer for slice 1: ingest a deterministic nonsecret raw fixture,
   preserve and verify its exact hash/provenance in an append-only manifest, and return a versioned
   `hel` JSON result. Include malformed/truncated and duplicate controls.
7. Keep encryption and storage interfaces truthful. A placeholder may be named as a placeholder; it
   cannot emit a success state that implies authenticated encryption or durable recovery occurred.
8. Run focused checks plus the repository-wide checks introduced by the bootstrap. Retain commands,
   versions, exit status, warnings, and artifacts.
9. Review the exact branch diff, publish through a pull request, and report remote SHA and checks. A
   local branch or green test is not delivery evidence.

The first thread is complete when a reviewer can clone the repository, run the documented public
command, observe the exact-hash manifest behavior and its failing controls, and trace every reported
field to the fixture without needing private implementation knowledge.

## Decisions that remain evidence-gated

These are not requests to restart product discovery:

- Which SQLite binding wins the conformance bakeoff.
- Whether full-text retrieval proves sufficient before embeddings.
- Which optional PostgreSQL and DuckDB features earn inclusion.
- Current exact pins for experimental compilers and external adapters.
- Current Claude and Codex subscription eligibility for each execution path.
- Final product/package name after live collision and trademark checks.

Resolve each with a reproducible probe and control arm, then record the decision. Preserve a viable
fallback whenever a preferred experimental component fails a hard gate.

## Existing related work

Issue #1 links the narrower knowledge-base issues for universal logs, structured command events,
session-review self-analysis, skill measurement, telemetry retention, and context amplification. They
are evidence and pilot requirements, not implementation tickets in this repository. Do not close or
rewrite them from this project without explicit cross-repository authority.

The earlier research conversation evaluated native libraries, subscription authentication, AgentsView,
Promptfoo, SkillOpt-Sleep, agent-skill-eval, Glaze, SQLite variants, DuckDB, PostgreSQL, encryption,
schedulers, and canary policy. Its accepted conclusions are incorporated in issue #1. Refresh only the
time-sensitive facts; preserve the confirmed product decisions unless new evidence creates a conflict.

## Startup receipt

At the start of the new thread, report:

- repository path and `origin` URL;
- current branch, HEAD, upstream, and worktree status;
- issue #1 title, state, and labels;
- that this handoff and issue #1 were read completely;
- the selected first externally testable behavior;
- the branch and first planned mutation; and
- every discovered conflict, warning, unavailable dependency, or drifted assumption.

Then begin the first thread objective without another architecture interview.

## Suggested opening prompt

> Work only in the `ray-manaloto/harness-evolution-ledger` repository. Read `HANDOFF.md` and GitHub
> issue #1 plus `BOOTSTRAP.md` completely, then produce the startup receipt they require. Treat issue
> #1 as the product authority. Complete phase 0 and publish its verified repository setup before
> beginning the smallest truthful slice-1 vertical tracer through the public `hel` CLI. Preserve
> unexpected worktree state, verify drift-prone facts from primary sources, retain warnings and
> receipts, and publish completed work through reviewed pull requests. Do not modify `knowledge-base`
> or `dotfiles` without explicit cross-repository authority.
