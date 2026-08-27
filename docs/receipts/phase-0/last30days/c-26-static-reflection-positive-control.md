# Last30Days positive-control projection

Observed 2026-08-27 with installed Last30Days v3.21.1. This file is a
sanitized, normalized projection; it is not byte-exact raw evidence.

The bounded probe used the checked-in query plan, disabled browser-cookie
access, disabled passive library context, selected native host search, and
restricted all declared writes to the repository. It performed no setup,
onboarding, installation, or account mutation.

## Result

- Exit status: `0`.
- Retrieval: 7 dated items across Reddit and Hacker News.
- Reddit: 6 threads; partial after HTTP 429.
- Hacker News: 1 story.
- Jobs: unreachable due DNS resolution failure.
- Other queried sources returned zero ranked items.
- Freshness warning: only 1 of 7 dated items was from the last 7 days.

This proves the installed capability can execute a bounded query and retain
results. It does not prove complete coverage, and the warnings must not be
interpreted as absence of discussion on failed or silent sources.

## Immutable private evidence

The byte-exact files are intentionally ignored under
`build/receipts/phase-0/last30days-completion/`:

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `stdout.bin` | 11,948 | `1a4e2a3d7251a453cfd7262e16aaee59ced3062c08c5de9585acb222247d5649` |
| `stderr.bin` | 1,792 | `53a55441aa239d694ca6c8f27f600b0bcd610035e987f4e616e71b1f37efb62d` |
| `exit-status.txt` | 2 | `9a271f2a916b0b6ee6cecb2426f0b3206ef074578be55d9bc94f6f3fe3ab86aa` |
| `c-26-static-reflection-raw-byte-exact.md` | 14,250 | `c431e60f42d8194bb001832d1cbded56ab9889703ae04e96c8275b1b8fe06a21` |

The earlier formatted `raw-completion` copy was superseded and removed because
formatting destroyed byte identity. The older tracked
`c-26-static-reflection-raw.md` remains historical evidence from the prior
failed TLS control and is not claimed as this run's raw output.
