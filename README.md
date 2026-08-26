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

See [the phase-0 status](docs/receipts/phase-0/status.md) for proven controls and
explicit blockers. Product slice 1 remains closed until the bootstrap acceptance
contract is complete.
