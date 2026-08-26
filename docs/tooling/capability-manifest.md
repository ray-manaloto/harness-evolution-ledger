# Capability manifest

Observed 2026-08-25. Installation state, UI state, cached files, and successful
tool calls are recorded separately. No credential values appear here.

## Required capabilities

| Capability | Publisher/version | Interfaces and permissions | Authentication | Positive control | Negative control or gap |
| --- | --- | --- | --- | --- | --- |
| OpenAI Developers / `openai-docs` | OpenAI curated `2f1a8948`; local skill | Official-doc retrieval; network read | Codex account | Fetched current official hooks, rules, and `AGENTS.md` guidance | Was cached but not installed at task start; installed before fresh-thread test |
| `mise:mise` | brentmitchell25 `2.9.0`; skill | Reads project config; task/tool installation writes mise data and lockfiles | GitHub downloads may use machine auth | Loaded complete skill, read `mise 2026.8.13`, generated and installed `mise.lock` | Initial lock emitted expected missing-entry warnings; 15 platform combinations were skipped |
| Matt Pocock engineering | mattpocock `1.2.3`; skills | Repository read/review; no MCP | None | Loaded `code-review` instructions explicitly | Final PR review still pending |
| Context7 | Context7 `1.0.1`; MCP and skill | Remote library lookup and docs read | Configuration reported `Not logged in` | Resolved CLI11 and retrieved official CMake target usage | Status label drifted from successful call |
| Codex Security | OpenAI curated `2f1a8948`; skills | Repository security analysis when invoked | On-use Codex authorization | Fresh thread exposed `security-scan` without scanning sibling repositories | Cached but not installed at task start; installed before control |
| Firecrawl | Anthropic marketplace `1.0.9`; skills, expected MCP/CLI | Public web search; network read | API auth for some paths | Bounded search returned three source URLs, retained as a project receipt | Plugin shim unavailable; exact npx CLI used. Feedback prompt auth was ambiguous |
| Exa | Exa `3.4.1`; MCP and skills | Independent network research | OAuth required | Installation and fresh-thread connection attempt positively exercised | **Blocked:** MCP returned `AuthRequired`; no generic-search substitution |
| Last30Days | mvanhorn `3.21.1`; skill/engine | Recent-source retrieval; local receipt write and network read | Configured source credentials by presence only | Seven-day query ran and retained a dated raw receipt plus web supplements | **Failed positive control:** planner drift and TLS failures yielded zero engine evidence |

## Account inventory relevant to phase 0

The complete, sanitized 60-plugin account inventory is versioned in
`docs/tooling/account-plugin-inventory.json`. It records installed/enabled state,
permission and authentication policies, skill entry points, and declared MCP/hook
interfaces without retaining machine-local paths. Unrelated capabilities were not
exercised or reinstalled. In particular, plugin-eval `0.1.1`,
Fable Orchestrator `1.21.0`, SkillOpt-Sleep `0.1.0`, and Graphify tooling were
deferred to their named delivery phases. No SaaS connector was installed.

Required enabled plugins at the end of inventory:

- `mise@brentmitchell25` `2.9.0`;
- `context7@context7-marketplace` `1.0.1`;
- `firecrawl@claude-plugins-official` `1.0.9`;
- `exa@exa` `3.4.1`;
- `last30days@last30days-skill` `3.21.1`;
- `mattpocock-skills@mattpocock` `1.2.3`;
- `codex-security@openai-curated` `2f1a8948`;
- `openai-developers@openai-curated` `2f1a8948`.

Plugin permissions were `AVAILABLE`; auth policies were either `ON_INSTALL` or
`ON_USE` as reported by `codex plugin list --json`. No required plugin bundled a
trusted project hook. Account and plugin hooks remain additive to the audited
repository hooks.

## Exact task-start callable catalog

Tool namespaces exposed to this task were:

- local execution: `exec_command`, `write_stdin`, `apply_patch`, `view_image`,
  workspace dependency loading, and web search/open/click/find/screenshot;
- Codex Desktop task/project operations: list/read/wait/create/fork/message/handoff,
  archive/pin/rename/share/navigate/open, and automation operations;
- collaboration operations: spawn, send, follow up, interrupt, list, and wait;
- image generation;
- Context7 MCP library resolution and documentation query.

The task-start skill catalog relevant to the authority was:

- official Codex/OpenAI: `openai-docs`, OpenAI Developers, and Codex Security;
- project/tooling: `mise:mise`, `continuity-handoff`, Context7, and Matt Pocock
  engineering skills;
- research: Firecrawl search/scrape/crawl/parse/monitor family, Exa Agent/search,
  and Last30Days;
- deferred but visible: plugin-eval, SkillOpt-Sleep, Fable Orchestrator, and
  Graphify continuation.

Exa and Firecrawl MCP tools were not directly exposed in the root task tool list.
Firecrawl was exercised through its exact CLI; Exa was not substituted.

## Retained public-source controls

- Firecrawl: `docs/receipts/phase-0/firecrawl/phase0-control.json`.
- Last30Days engine and dated supplements:
  `docs/receipts/phase-0/last30days/c-26-static-reflection-raw.md`.
- Context7 result: CLI11's official docs specified `find_package(CLI11 CONFIG
  REQUIRED)` and `target_link_libraries(... PRIVATE CLI11::CLI11)`.

## Current gaps

1. Exa requires OAuth in a user-capable fresh thread.
2. Last30Days requires a repaired CA chain and a rerun whose dated evidence comes
   from the engine rather than web supplements.
3. The target checkout must be added as a saved Codex Desktop local project, then
   opened in a new task to verify root and nested instruction discovery and hook
   trust.
