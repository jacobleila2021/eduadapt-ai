# Regression Test Report

## Passing evidence

- Final default suite: 250 passed, 7 opt-in browser cases skipped, exit code 0.
- Final local browser suite: 7 passed across Chromium, Firefox, WebKit, responsive, and axe cases.
- Baseline configured unit/integration suite.
- Previously excluded root UX suite: 35 passing tests.
- Engine dependency topology, missing/disabled dependency, and cycle gates.
- Event dead-letter recovery.
- Publication quarantine sources.
- Six-subject fixture manifest and cross-subject scope isolation.
- Exact SymPy mathematics, deterministic physics, and ChemPy atom-count validation.
- Malicious SVG sanitization.
- Nine-adaptation print completeness and deterministic matching.
- Chroma outage fallback and bounded OpenAI configuration.
- Streamlit dashboard shell smoke.
- Local Chromium, Firefox, and WebKit shell journeys.
- Local responsive overflow at 320, 768, and 1440 px.
- Local Chromium axe gate with zero critical/serious findings after fixes.
- Twenty-five concurrent local health requests.

## Failed/deferred evidence

- Public Chromium, Firefox, and WebKit content render: failed after 120 seconds.
- Public axe/responsive checks: blocked by public content-render failure.
- Live six-subject model canaries: deferred because verified curriculum and complete orchestration prerequisites failed.
- Authenticated teacher/student/parent/special-educator/admin journeys: unavailable because identity and roles are not implemented.
- Full load, rate-limit storm, cancellation, disaster recovery, and offline synchronization: not production-testable on the current architecture.

## Release gate result

The suite supports a non-ready verdict. It does not support emission of `ALORA_PRODUCTION_READY_SMOKE_OK`.
