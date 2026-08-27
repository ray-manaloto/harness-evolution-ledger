# harness-evolution-ledger

Local-first Claude and Codex telemetry replay, evaluation, and autonomous improvement engine

Start with [HANDOFF.md](HANDOFF.md), then complete the environment contract in
[BOOTSTRAP.md](BOOTSTRAP.md). The complete product specification is tracked in
[issue #1](https://github.com/ray-manaloto/harness-evolution-ledger/issues/1).

Phase 0 exposes one public task surface:

```bash
mise run setup
mise run check
mise run hooks:verify
mise run rules:verify
mise run security
mise run sbom
```

Worktree delivery remains repository-owned:

```bash
# Publish the committed worktree branch and fast-forward the clean default checkout.
mise run ship

# Retry only the default-checkout fast-forward after an external publication.
mise run worktree:sync

# Explicit recovery path: preserve dirty default-checkout state in a named Git stash.
mise run worktree:preserve-sync
```

All synchronization paths require the canonical origin and expected branch, reject
divergence, use `git merge --ff-only`, and verify that the default checkout equals
the exact remote SHA. The preserve path never drops dirty state; it reports the
created stash object before synchronizing.

Prototype landing remains explicit and repository-owned:

```bash
mise run land --prototype-bypass-review
```

This mode requires the exact PR head and required `check` result, temporarily sets
the GitHub approval count to zero, restores the original protection in a `finally`
path, performs a squash merge, fast-forwards canonical `main`, and writes the
ignored machine-local delivery receipt used for live post-merge verification.

See [the phase-0 status](docs/receipts/phase-0/status.md) for proven controls and
explicit blockers. Product slice 1 remains closed until the bootstrap acceptance
contract is complete.
