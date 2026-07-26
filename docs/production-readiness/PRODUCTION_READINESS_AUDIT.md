# Alora AI Production Readiness Audit

Audit date: 18 July 2026  
Audited local version: 2.17.0 (`20260717-nine-adapt-flowcharts`)  
Public version observed: 2.16.1 (`20260628-colors-fix`)  
Release verdict: **NOT READY**

## Executive summary

Alora has a substantial deterministic STEM foundation, a broad engine catalogue, nine learner adaptations, a capable Streamlit learning workspace, and strong unit-level coverage. The audited local build is materially safer than the deployed build after the bounded fixes in this audit.

It is not production-ready for schools, governments, universities, or multi-tenant commercial deployment. The release is blocked by deployment drift, an incomplete production orchestration path, Class 8 Science-only verified corpus coverage, absent authentication/role/tenant controls, non-durable review/publish semantics, and a failed public automated browser gate.

`ALORA_PRODUCTION_READY_SMOKE_OK` was intentionally not emitted.

## Evidence and scores

- Production readiness: 49/100
- Architecture: 48/100
- Integration: 42/100
- Curriculum accuracy readiness: 45/100
- AI quality readiness: 38/100
- UX: 68/100
- Visual design/LUXE: 64/100
- Accessibility: 73/100
- Performance: 52/100

Scores distinguish audited code and local tested behavior from public-deployment behavior. They do not credit architecture documents as implemented production behavior.

## Blocking release gates

1. **Public/local drift** — the public app exposes v2.16.1 while the audited local build is v2.17.0.
2. **Incomplete engine lifecycle** — `VerifiedLearningOrchestrator.process_lesson(generate_adaptations=True)` runs a reduced set of “light” engines, invokes teaching generation, and synthesizes curriculum/scientific/QA bundles afterward. It does not execute upload → KIE → UCF → CIE → AME as the verified precondition to teaching.
3. **Curriculum coverage** — the substantial verified corpus is CBSE Class 8 Science. Mathematics, English, Social Science, and broader grades/boards cannot satisfy the requested source-grounded production claim.
4. **Identity and authorization** — there is no durable authentication, role authorization, school tenancy, or learner-data isolation. Teacher answers and administrative capabilities cannot be safely scoped.
5. **Public browser gate** — Chromium, Firefox, and WebKit received the public shell but no rendered Alora content within 120 seconds. Direct public extraction worked, proving the deployment exists, but the browser workflow gate failed.
6. **Durability** — JSON files, local Chroma, in-memory events, and Streamlit session state are not a safe enterprise concurrency or disaster-recovery design.
7. **Review/publish semantics** — QA quarantine is now enforced in the local user paths, but teacher review and publication are not durable, authorized state transitions.

## Applied low-risk fixes

- Replaced priority-only engine ordering with stable topological ordering; missing, disabled, and cyclic dependencies fail closed.
- Recorded event-handler failures in a bounded dead-letter queue; orchestration state/stage errors are added to audit output instead of silently ignored.
- Added a shared publication gate and quarantined failed packages from adaptation view, export, audio, and LXP entry points.
- Fixed broken LXP viewer arguments and undefined workspace metadata.
- Prevented CIE and UCF from selecting Class 8 Science concepts/packages for explicitly mismatched subjects and grades.
- Fixed `Social Science` being classified as `Science`.
- Added explicit Chroma-unavailable behavior with warnings and no retrieved evidence.
- Added bounded OpenAI timeout/retry configuration and applied it to lesson, image, and speech clients.
- Bounded the ZIP cache and replaced upload name/size identity with SHA-256.
- Added a strict SVG allow-list sanitizer and stopped rendering model-authored study SVG in preference to deterministic diagrams.
- Added all nine adaptations to the combined print package and made vocabulary matching deterministic.
- Fixed LXP exception leakage and removed public startup tracebacks.
- Added skip navigation, visible focus, reduced motion, forced-colors support, framework ARIA repairs, and uploader contrast corrections.
- Added local Chromium/Firefox/WebKit, responsive, axe, Streamlit smoke, curriculum isolation, publication, export, SVG, recovery, and deterministic exactness gates.
- Added GitHub Actions unit/integration, dependency audit, and three-browser jobs.

## Measured performance

- Local Streamlit server became ready in approximately 9.6 seconds.
- Three deterministic STEM tasks completed in 2.75 seconds; all validated.
- Out-of-scope retrieval failed closed in 35 ms with zero hits.
- Cold Chroma readiness took 21.48 seconds for eight indexed records.
- Traced peak memory during the benchmark was approximately 103 MiB.
- Twenty-five concurrent local health requests all returned HTTP 200 in 3.83 seconds.
- Full live lesson-generation latency/cost was not benchmarked because curriculum and orchestration prerequisite gates failed; spending on model canaries would not establish production correctness.

## Test evidence

- Baseline configured suite passed before audit changes.
- The previously excluded root UX suite passed: 35 tests.
- Production invariant suite passed after fixes.
- Local responsive checks passed at 320, 768, and 1440 px with no document overflow.
- Chromium, Firefox, and WebKit loaded the local v2.17.0 shell.
- Local dashboard axe gate passed with zero critical or serious WCAG 2.2 A/AA findings after repairs.
- Public browser automation failed to render application content in all three engines.

## Manual approval items

- Replace local persistence with a tenant-aware transactional database, managed vector store, migrations, backups, and retention controls.
- Introduce an identity provider, school/organization tenancy, role/permission policy, and audit-log retention.
- Make KIE/UCF/CIE/AME/QA preconditions part of one idempotent production transaction with correlation IDs.
- Add verified, licensed curriculum corpora and official assessment banks for every advertised subject, board, grade, and locale.
- Implement durable teacher-review and publish state transitions with signatures and rollback.
- Add telemetry, error tracking, SLOs, incident response, secret rotation, dependency pinning, and controlled promotion.
- Deploy v2.17.0 and rerun the public release matrix.

## Recommended roadmap

### Gate 1 — deployment and release discipline

Deploy the audited build, lock Python to 3.11 in local/CI/production, enable the production-gates workflow, pin dependencies with hashes, and require public/local version parity.

### Gate 2 — safety and enterprise controls

Implement identity, roles, tenancy, durable storage, review/publish state, security threat modelling, backups, and observability.

### Gate 3 — verified curriculum expansion

Ingest licensed official sources through KIE/UCF for each supported curriculum. Require provenance, hashes, coverage metrics, answer-key validation, and source-bound tutor behavior.

### Gate 4 — complete orchestration

Make every advertised lifecycle stage real, idempotent, dependency-enforced, correlated, recoverable, and blocked by QA before LXP exposure.

### Gate 5 — release validation

Run six-subject fixture and live canaries, full adaptation journeys, authenticated role tests, exports, audio/tutor/offline paths, public cross-browser/axe, load, recovery, and disaster-recovery exercises.

## Smoke decision

The final smoke gate failed. The correct marker is:

`ALORA_PRODUCTION_READY_SMOKE_BLOCKED`
