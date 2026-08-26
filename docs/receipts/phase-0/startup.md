# Phase-0 startup receipt

Captured 2026-08-25 in America/Chicago before repository mutation.

## Repository

- Path: `/Users/rmanaloto/dev/github/ray-manaloto/harness-evolution-ledger`
- Origin: `git@github.com:ray-manaloto/harness-evolution-ledger.git`
- Starting branch: `main`
- Starting HEAD: `e97e00a5916235389685b5b3baab26b409b01dd7`
- Upstream: `origin/main`
- Starting status: clean; local `main` equaled `origin/main`
- Work branch: `codex/phase-0-bootstrap`, created from that clean commit
- First planned mutation: add the phase-0 root instructions, trusted project
  settings, exact tool contract, and public gates before any product code.
- Selected first externally testable behavior after phase 0: a smallest vertical
  tracer that ingests a deterministic non-secret fixture, records exact
  hash/provenance in an append-only ledger, emits versioned `hel` JSON, and rejects
  malformed, truncated, and duplicate input. That slice has not begun.

## Product authority

- Issue #1: **Build harness-evolution-ledger: C++26 Claude/Codex telemetry replay
  and autonomous improvement engine**
- State: open
- Labels: `ready-for-agent`
- Relevant comment: `BOOTSTRAP.md` was merged through PR #3 and phase 0 must be
  completed before slice 1.
- Complete reads confirmed:
  - `HANDOFF.md`, 243 lines, execution handoff;
  - `BOOTSTRAP.md`, 305 lines, mandatory phase-0 contract;
  - issue #1 body, 186 lines, plus its single comment, product authority.

## Codex and instruction chain

- Codex: `codex-cli 0.149.1`
- `CODEX_HOME`: `/Users/rmanaloto/.codex` (environment variable unset; default
  location effective)
- Loaded before the target root existed: system/developer instructions, the
  Codex Desktop project context for `local-model-eval`, and that repository's
  `AGENTS.md` supplied by the host.
- Target repository instruction state at startup: no root `AGENTS.md` and no
  trusted `.codex` project layer.
- The target repository was not present in the Codex Desktop saved-project list;
  therefore the inherited `local-model-eval` repository instructions were not
  treated as target-project authority.

## Task-start capability catalog

- Direct local capabilities: repository shell execution, patch application,
  process polling/input, local image inspection, workspace dependency discovery,
  Codex task/project management, automation management, and web access.
- Collaboration capabilities: spawn, message, follow up, interrupt, list, and wait
  for subagents. No subagent was started during initial phase-0 setup.
- Connected callable MCP at task start: Context7 library resolution and official
  documentation query.
- Configured MCP status at task start: Docker MCP, computer history, event stream,
  messages, node REPL, Context7, Exa, and OpenAI developer docs. Configuration
  status was not accepted as callability evidence.
- Required visible skills: `openai-docs`, `mise:mise`, Matt Pocock engineering
  skills, Context7, Codex Security, Firecrawl, Exa, and Last30Days.
- Execution-evidence skill: `continuity-handoff`, used only for its receipt and
  fail-closed handoff discipline because its commands target another repository.

## Startup warnings and drift

- Target repository was not bound as a saved Codex Desktop local project.
- Origin uses the required SSH URL, but `git fetch origin` could not authenticate
  because no SSH identity was loaded. A temporary agent plus Keychain lookup still
  required an unavailable passphrase. Read-only GitHub API checks confirmed the
  starting `origin/main` SHA and issue state; the origin URL was not rewritten.
- One diagnostic shell appended a reporting command after the failed fetch and
  therefore returned the reporter's zero status. The fetch stderr was retained and
  the command was not accepted as a successful fetch control.
- Two required plugins were cached but not account-installed: OpenAI Developers
  and Codex Security. They were installed and enabled, then tested in a fresh
  Codex CLI thread.
- The first fresh-session command placed `--ask-for-approval` after `exec` and
  failed with exit 2. The corrected global-option placement succeeded.
- Fresh thread `01a03b65-dfea-76d2-a897-88dfe80cced3` reported:
  - `chronicle` is under development;
  - a plugin SessionEnd timeout was clamped to Codex's three-second maximum;
  - Exa OAuth was required and its MCP connection failed;
  - skill descriptions were shortened to fit the skill context budget.
- Context7's configuration label said `Not logged in`, but a real resolve/query
  call succeeded. The label was stale relative to observed behavior.
- Firecrawl's plugin shim had no mise version. A bounded public control used
  exact `firecrawl-cli@1.23.1`; its optional feedback step unexpectedly prompted
  for authentication and submission could not be confirmed.
- Last30Days rewrote the supplied two-query plan to one external-planner query,
  then Reddit, Hacker News, and jobs failed TLS certificate validation. Its empty
  result is retained as a failed retrieval control, not evidence of no discussion.
- Exa remained installed but not callable because OAuth was unavailable.
- `DOPPLER_TOKEN` was absent from the task environment. No credential value was
  requested, printed, or persisted.
- Mise resolved 111 exact lock entries and explicitly skipped 22 unsupported
  tool/platform combinations. The skipped combinations remain typed lock gaps,
  not successful platform controls.
- The immutable devcontainer index selected an arm64 image whose embedded OCI
  revision label `2108ebf345acd2c3275da46a1adc048b9b39cecc` did not equal
  inspected producer commit `362f3ed8dbff92c75428c532d7ddf8c2bb48ca63`.
  Both identities are retained; neither was silently substituted.
- The image's `/opt/gcc-latest` reports GCC 15.2, not the requested GCC 16.2.
  Release-authority GCC validation remains unavailable.
- The container has an isolated Codex home and reports account plugins missing.
  Host account capability and container repository-tool controls are kept separate.
- The initial CMake smoke build exposed a missing versioned
  `clang-scan-deps-22` shim. Disabling module scanning for the non-module smoke
  target removed that hidden dependency and the opposing build rerun passed.
