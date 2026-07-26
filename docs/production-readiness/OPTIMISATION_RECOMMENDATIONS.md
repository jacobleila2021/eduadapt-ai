# Optimisation Recommendations

## Immediate

- Deploy the audited build and require public/local version parity.
- Persist and reuse Chroma readiness outside request-time generation.
- Instrument stage durations, model calls, token use, cache hit rate, and export timings.
- Keep out-of-scope detection before all vector and model work.
- Enforce bounded queues and per-tenant quotas before multi-user release.

## Next

- Move orchestration to an idempotent background job with correlation IDs and checkpoint recovery.
- Store source, UCF, package, review, and publish records in a transactional database.
- Use managed, tenant-aware vector storage with immutable source revisions.
- Generate adaptations concurrently only after deterministic prerequisites pass; cap worker count and model budget.
- Pre-render/cache deterministic diagrams by engine-input hash.
- Stream or incrementally package large exports instead of rebuilding all formats on every rerun.

## Avoid

- Do not cache API keys, learner-private data, or unvalidated model output globally.
- Do not use model calls to compensate for absent official corpora.
- Do not enable offline claims until encryption, conflict resolution, revocation, and tenant separation are tested.
- Do not optimize by bypassing QA, deterministic validation, source checks, or teacher review.
