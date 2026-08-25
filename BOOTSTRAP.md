# Codex project bootstrap

## Purpose

This is phase 0 for a fresh Codex project. It establishes the trusted repository,
instructions, installed capabilities, hooks, command policy, reproducible tools,
secrets boundary, Git gates, and CI needed before product code is allowed to claim a
verified result.

The bootstrap is a deliverable, not ambient machine state. Record every installed or
reused capability, exact version, source, scope, positive control, negative control,
and remaining gap. A plugin visible in a cache or settings screen is not proven
callable. A tool on `PATH` is not proven reproducible.

## Scope map

| Layer | Scope | Source of truth |
| --- | --- | --- |
| ChatGPT/Codex project | Local project | Folder attached to the new project |
| Product decisions | Repository | GitHub issue #1 |
| Thread resumption | Repository | `HANDOFF.md` |
| Durable agent guidance | Repository | `AGENTS.md` and small context pointers |
| Codex settings | Trusted repository | `.codex/config.toml` |
| Codex lifecycle enforcement | Trusted repository | `.codex/hooks.json` and repo-owned handlers |
| Command escalation policy | Trusted repository | `.codex/rules/*.rules` |
| Reusable project workflows | Repository | `.agents/skills/*/SKILL.md` |
| Toolchain and commands | Repository | `mise.toml`, lockfiles, and `mise run` tasks |
| Git commit hooks | Repository | `hk` configuration installed through `mise` |
| CI | Repository | GitHub Actions invoking the same `mise` tasks |
| Credentials | Host/user | macOS Keychain, Doppler, and fnox references |
| Plugins | Account/environment | Codex plugin directory; effective after a new chat |

Do not put provider authentication, notification settings, or telemetry routing into
project `.codex/config.toml`. Codex treats those as machine-owned settings and ignores
their project-local forms.

## Step 1: bind the project to the correct checkout

Create the Codex local project with this folder:

`/Users/rmanaloto/dev/github/ray-manaloto/harness-evolution-ledger`

Start the new thread from that project. Verify:

- workspace root is the repository root;
- `origin` is `git@github.com:ray-manaloto/harness-evolution-ledger.git`;
- local `main` equals `origin/main` before branching;
- worktree is clean or every unexpected change is classified and preserved;
- GitHub issue #1 is open and labelled `ready-for-agent`.

Completion criterion: the startup receipt in `HANDOFF.md` contains live output for
all five checks.

## Step 2: inventory plugins and skills

Plugin installation is account/environment scoped, not repository scoped. Installed
plugins normally carry into a new project on the same account, but their skills and
tools are captured when a new chat starts. After installing or enabling a plugin,
start a new thread before testing it.

### Required for phase 0

Audit and enable these capabilities when available:

| Capability | Purpose | Acceptance control |
| --- | --- | --- |
| OpenAI Developers / `openai-docs` | Current official Codex and OpenAI guidance | Fetch a current Codex customization fact from the official manual |
| `mise:mise` | Correct project and lockfile conventions | Read `mise --version` and validate the project config |
| Matt Pocock engineering skills | Research, TDD, review, domain design, agent-facing docs | Explicitly invoke one installed skill and show its loaded instructions |
| Context7 | Current primary dependency documentation | Resolve one selected C++ dependency and retrieve its official docs |
| Codex Security | Threat model, attack paths, security review, fix verification | Confirm the relevant security skill is callable without scanning unrelated repos |

### Required before research-dependent pins

| Capability | Purpose | Acceptance control |
| --- | --- | --- |
| Firecrawl | Search, scrape, parse, and monitor web sources | Run one bounded public search and retain source URLs |
| Exa | Independent deep research route | Run one bounded query and distinguish tool callability from cached files |
| Last 30 Days | Recent social, market, and web evidence | Run one time-bounded query with dated sources |

### Deferred until their delivery slice

- plugin-eval and SkillOpt evaluation tooling: before skills are optimized;
- SkillOpt-Sleep: before slice 4 text-candidate generation;
- Fable or another orchestrator: only after ordinary single-thread behavior is
  reproducible;
- Graphify: only after this repository has declared its own source and graph contract;
- unrelated SaaS connectors: only when an approved requirement names their data.

Use the Codex plugin browser or Plugins directory to install missing plugins. Record
plugin name, publisher, version, permissions, connectors, MCP servers, hooks, and
authentication needs. Review bundled hooks before trusting them. Do not treat an
installed plugin as usable until a new thread exposes and positively exercises its
capability.

Completion criterion: commit `docs/tooling/capability-manifest.md` containing the
observed table, controls, gaps, and exact task-start callable catalog. It must contain
no credential values.

## Step 3: establish repository instructions

Create a concise root `AGENTS.md` below 12,000 characters. It should:

- point to issue #1, `HANDOFF.md`, and this bootstrap instead of duplicating them;
- state the C++26, supported-platform, immutable-raw-evidence, and public-CLI test
  boundaries;
- require `mise run` public tasks for setup, build, test, lint, format, check, ship,
  and land operations;
- protect dirty trees and require isolated branches/worktrees for candidates;
- require real isolated inputs, retained exit status, warnings, receipts, and control
  arms;
- keep sibling repositories outside mutation scope;
- identify which checks must pass before commit, pull request, and merge.

Add a small `CLAUDE.md` pointer only if Claude will also work in this repository.
Keep shared meaning in one authoritative document. Verify Codex instruction discovery
from the repository root and a nested directory in a new session.

Completion criterion: Codex reports the expected global and repository instruction
chain without truncation, and the root file passes its configured size/lint gate.

## Step 4: add project Codex configuration

Create `.codex/config.toml` with the smallest trusted-project settings needed for this
repository. Start with:

- hooks explicitly enabled;
- a core or explicitly allowlisted shell environment;
- bounded multi-agent concurrency only when a task genuinely delegates;
- project instruction byte limits only if the verified `AGENTS.md` chain needs them;
- sandbox and approval posture appropriate for local repository work.

Keep models, provider URLs, authentication, profiles, notifications, and telemetry
routing in user-level Codex configuration. Project config must not export Claude
telemetry variables into Codex or inherit all host secrets.

Completion criterion: a fresh Codex session trusts and reports the intended project
layer, and a control demonstrates that a machine-owned key placed in project config
would be ignored or rejected rather than relied upon.

## Step 5: install two distinct hook systems

### Codex lifecycle hooks

Create `.codex/hooks.json` and repo-owned, dependency-light handlers. Resolve handlers
from the Git root because Codex may start in a subdirectory. Begin with:

- `SessionStart`: read-only project/tool/capability doctor and concise additional
  context;
- `PreToolUse`: protect default-branch mutation, destructive Git operations, broad
  credential exposure, and writes outside the authorized project;
- `PostToolUse`: preserve command metadata, stdout/stderr, exit status, warnings, and
  terminal state through a bounded logging seam;
- `Stop`: run or enqueue the bounded changed-file checks and record incomplete work;
- `SessionEnd`: enqueue only; finish within Codex's maximum three-second window.

Hooks receive untrusted structured input. Parse it with strict size/type limits. A
policy hook should fail closed when its own runtime is unavailable; an observational
hook should record its failure without falsely claiming evidence was captured. Keep
hook behavior idempotent and test every deny path with an allowed control.

Do not copy the dotfiles writer-lease hook verbatim: it depends on dotfiles-owned
Python modules and paths. Reuse its proven behavior through a project-owned interface.
Plan to replace bootstrap handlers with `hel` subcommands when the native executable
can dogfood its own telemetry safely.

### Git hooks

Install `hk` through `mise` and define commit/pre-push checks that invoke the same
public tasks used by CI. Initial checks should cover formatting, Markdown, TOML,
secrets, CMake, C++ static analysis, tests, and generated/lockfile consistency.

Completion criterion: hook verification fires each Codex and Git hook with a positive
case and an opposite-direction control, preserves real exit status, and proves the
same gate command runs locally and in CI.

## Step 6: add command rules

Create `.codex/rules/project.rules` for commands that request execution outside the
sandbox. Rules are experimental command-prefix policy, not general prose guidance or
a substitute for hooks.

Use tested `prefix_rule` entries with `match` and `not_match` examples. Start with the
smallest set justified by real risks:

- forbid or prompt for destructive Git commands and force pushes;
- prompt for direct merge, release, and publication commands until repository `ship`
  and `land` tasks own those paths;
- allow bounded read-only Git and GitHub inspection where the active sandbox requires
  an exception;
- route build, test, formatting, and dependency operations through `mise run` tasks.

Test every rule with `codex execpolicy check`. Shell wrappers containing expansion,
redirection, or control flow may be evaluated as one opaque command, so do not assume
a nested command was recognized.

Completion criterion: checked-in rule tests discriminate the intended commands and
the startup receipt records the Codex version because rules are experimental.

## Step 7: create the `mise` project contract

Create root `mise.toml` with exact pins, lockfiles, and a minimum release age where
supported. Verify current versions from primary sources before choosing pins.

The initial tool categories are:

- CMake and Ninja;
- GCC 16.2 release-authority toolchain when live availability is confirmed;
- the exact LLVM/Clang P2996 differential toolchain through a reproducible build or
  immutable devcontainer layer;
- vcpkg at an exact commit/baseline;
- clang-format, clang-tidy, and CMake format/lint tooling;
- `hk`, `rumdl`, TOML validation, secret scanning, and GitHub Actions linting;
- devcontainer CLI and any image/SBOM/provenance tools required by the release plan.

Expose stable tasks rather than memorable shell recipes:

- `mise run bootstrap` — install/sync tools and verify lockfiles;
- `mise run doctor` — report tools, compilers, credentials by presence only, plugins,
  hooks, rules, Git, and platform state;
- `mise run configure`, `build`, and `test`;
- `mise run fmt`, `lint`, and `check`;
- `mise run hooks:verify` and `rules:verify`;
- `mise run security` and `sbom` when their tools land;
- `mise run ship` and `land` once review/receipt behavior is implemented.

Keep host-only tools in root config, devcontainer tools in an immutable image config,
and common exact pins in one shared fragment. Use the dotfiles devcontainer only by
immutable commit and image digest. A new worktree must receive the same tool versions
without copying secret values or depending on an interactive shell profile.

Completion criterion: a clean clone and the devcontainer both pass `mise install
--locked`, `mise doctor`, and the initial `mise run check`, with any host-only
difference explicitly classified.

## Step 8: preserve the secrets boundary

Reuse the existing host chain:

`macOS Keychain → DOPPLER_TOKEN → Doppler values → fnox declarations → scoped process`

Commit declarations and references only. Start child jobs from a clean allowlisted
environment. Never write a persistent `.env`, `doppler.env`, broad container env file,
credential argv, or secret-bearing log. Add secret canaries and poisoned-environment
controls before provider execution.

Completion criterion: `mise run doctor` reports credential presence and auth status
without values; a poisoned control proves common Anthropic and OpenAI API key variables
are removed from subscription-backed provider children.

## Step 9: add CI and delivery controls

Create GitHub Actions that invoke the public `mise` tasks rather than duplicating
commands. Pin actions by immutable SHA. Start with Markdown/config/security checks and
the toolchains currently available; add the GCC release and Clang differential matrix
only after each image/compiler path is reproducible.

Require a reviewed pull request for bootstrap. Record exact remote SHA, check results,
warnings, tool versions, and any skipped platform with a typed reason. Configure branch
protection after CI has a green control and a deliberately failing control.

Completion criterion: a fresh pull request proves checks run from committed state, a
failing control blocks merge, and `main` contains the reviewed bootstrap receipt.

## Phase-0 acceptance

Phase 0 is complete only when all of these are true:

1. The local Codex project is bound to the correct clean repository.
2. Required plugins/skills have versioned inventory and callable controls.
3. `AGENTS.md` loads without truncation and points to authoritative docs.
4. Project Codex config loads only trusted project-owned settings.
5. Codex hooks and Git hooks pass positive and negative controls.
6. Command rules pass `codex execpolicy check` controls.
7. A clean host clone and immutable devcontainer can reproduce locked `mise` tools.
8. Credential presence is usable through scoped fnox/Doppler/Keychain routing without
   values in files, argv, logs, or broad environment inheritance.
9. CI calls the same `mise` gates and has a blocking failure control.
10. The setup is merged to remote `main` through a reviewed pull request with a receipt.

Only then begin the slice-1 raw-evidence tracer described in `HANDOFF.md`.

## Official Codex references

- [Projects and chats](https://learn.chatgpt.com/docs/projects)
- [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [Hooks](https://learn.chatgpt.com/docs/hooks)
- [Rules](https://learn.chatgpt.com/docs/agent-configuration/rules)
- [Plugins](https://learn.chatgpt.com/docs/plugins)
- [Skills and plugins](https://learn.chatgpt.com/docs/skills-and-plugins)

## Prompt for the first new-project thread

> Work only in `ray-manaloto/harness-evolution-ledger`. Read `HANDOFF.md`,
> `BOOTSTRAP.md`, and GitHub issue #1 completely, then produce the required startup
> receipt. Treat issue #1 as product authority and complete phase 0 before product
> implementation. Inventory and positively test account-scoped plugins/skills; create
> concise repository instructions; add trusted project Codex config, audited lifecycle
> hooks, tested command rules, locked `mise` tooling/tasks, scoped secrets routing, Git
> hooks, and CI. Use a clean branch and reviewed pull request. Preserve every warning,
> unavailable dependency, version drift, skipped check, and control result. Do not copy
> dotfiles internals or modify sibling repositories. Do not begin the `hel` slice-1
> tracer until every phase-0 acceptance item is either proven or reported as an explicit
> blocker.
