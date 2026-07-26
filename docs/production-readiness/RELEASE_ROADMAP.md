# Production Release Roadmap

## Phase 0 — freeze claims

Publish the verified scope as CBSE Class 8 Science only. Remove or qualify unsupported enterprise, offline, role, board, grade, and subject claims.

## Phase 1 — release discipline

- Deploy v2.17.0.
- Require the production-gates workflow.
- Pin Python 3.11 and dependencies with hashes.
- Add staging, immutable build IDs, promotion approvals, rollback, and parity probes.

Exit gate: local, CI, staging, and public build IDs match; three-browser public shell passes.

## Phase 2 — identity and durability

- Add organization/school tenancy and identity provider integration.
- Define student, parent, teacher, special educator, and administrator permissions.
- Move packages, events, reviews, publication, and learner data to durable storage.
- Add backups, encryption, retention, audit-log policy, and security review.

Exit gate: authenticated role and tenant-isolation tests pass.

## Phase 3 — verified curriculum

- Ingest licensed official sources through KIE.
- Produce UCF packages and official assessment banks for each released scope.
- Add source hashes, provenance, coverage, curriculum review, and withdrawal procedures.

Exit gate: 100% of released scopes have official source and answer-key coverage.

## Phase 4 — complete orchestration

- Make KIE/UCF/CIE/deterministic computation/AME/teaching/QA/review/publish one idempotent workflow.
- Add retries, dead-letter handling, checkpoints, cancellation, and observability.

Exit gate: no stage bypass, duplicate processing, orphan output, or uncorrelated event.

## Phase 5 — release validation

Run budgeted live canaries, authenticated E2E, full axe/screen-reader matrix, visual goldens, load/soak, failure injection, recovery, backup restore, mobile, export, audio, tutor, and offline tests.

Exit gate: every blocker in the production audit is closed with current public evidence.
