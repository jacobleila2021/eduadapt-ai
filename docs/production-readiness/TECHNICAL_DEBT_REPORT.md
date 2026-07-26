# Technical Debt Report

## Critical

- Streamlit is acting as UI, session store, orchestration host, and deployment boundary.
- No identity provider, authorization model, tenancy, or school data isolation.
- Local JSON/Chroma/in-memory persistence lacks transactional concurrency, backups, and retention policy.
- Advertised lifecycle stages and the production generation branch diverge.
- Verified curriculum coverage is far narrower than the product claim.

## High

- Teacher review and publish are not durable workflow entities.
- Dependencies are range-pinned rather than lockfile/hash pinned.
- Public deployment promotion and version parity are not enforced.
- No centralized traces, metrics, error tracking, SLOs, or incident response.
- PWA/offline implementation is not demonstrated as deployed or conflict-safe.
- Role-specific content, especially answer keys, cannot be authorized.

## Medium

- Chroma cold readiness is slow for the tiny pilot.
- Streamlit framework accessibility requires DOM repairs.
- Visual engines lack comprehensive golden/reference tests.
- Broad exception fallbacks remain in legacy modules.
- Export parity is not tested for every adaptation and complex STEM artifact.

## Debt policy

Do not address critical debt with additional prompts or UI flags. Resolve it with durable platform capabilities, explicit contracts, migration plans, security review, and release gates.
