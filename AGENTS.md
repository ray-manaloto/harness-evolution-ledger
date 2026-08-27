# Harness Evolution Ledger

Issue [#1](https://github.com/ray-manaloto/harness-evolution-ledger/issues/1)
is the product authority. Read `HANDOFF.md` completely for execution context and
`BOOTSTRAP.md` completely for the phase-0 contract before changing this repository.

## Boundaries

- Target C++26 on Linux and macOS. A build result is not proof of reflection or
  semantic support; capability claims require an explicit positive control.
- Preserve immutable raw evidence and provenance. Test public `hel` CLI behavior,
  not private implementation details.
- Use public `mise run` tasks for bootstrap, doctor, configure, build, test, fmt,
  lint, check, hooks, rules, security, SBOM, ship, and land operations.
- Treat dirty worktrees as protected evidence. Develop candidates on an isolated
  branch or worktree created from current `origin/main`.
- Use real isolated inputs, preserve exit status, stdout, stderr, warnings,
  receipts, and an opposite-direction control. Never infer success from artifacts.
- Do not modify or depend on sibling `dotfiles` or `knowledge-base` repositories.
  Shared behavior must have a repository-owned interface and recorded provenance.
- Keep credentials out of files, argv, logs, broad environments, and containers.
  Machine-local authentication routes through Keychain, Doppler, and fnox.

## Gates

- Before commit: `mise run check` and `mise run hooks:verify`.
- Before pull request: the commit gates plus `mise run rules:verify`, `security`,
  and `sbom`; retain a receipt for every warning or skip.
- Before merge: a reviewed PR, green required CI at the exact remote SHA, a proven
  blocking failure control, and a delivery receipt. Use `mise run ship` and
  `mise run land` once those tasks report themselves enabled.
- Do not begin product slice 1 until every item in BOOTSTRAP phase-0 acceptance is
  proven or recorded as an explicit blocker.
