# Release Candidate & Production Readiness (RCPR)

**Smoke:** `RELEASE_CANDIDATE_PRODUCTION_READINESS_SMOKE_OK`  
**Tag:** `ALORA-AI-RC1`  
**Not a new intelligence engine** — release engineering over frozen production architecture.

## Architecture freeze

UCF · CEF · CMIF · ULI · ULIQE · SIF · SICS · MIP · PIP · CIP · BIP · ELIP · SSIP · CSIP · CEIP · WLIP · UVIE · LCE · PQLE · PMES · EATS · UEVB · PEEC · POBR

These systems may only receive bug fixes, performance optimisation, integration improvements, rendering improvements, and educational quality improvements. **No redesigns. No new engines or validation frameworks.**

## Campaign

```bash
# Full RC1 matrix (≥100 complete lesson packages)
python -m release --target 100

# Fast smoke (4 packages)
python -m release --smoke
```

The runner:

1. Composes packages via LCE using the UEVB corpus matrix  
2. Classifies defects (Critical / High / Medium / Low)  
3. Auto-resolves Critical/High with existing PMES + PEEC polishers only  
4. Writes Beta Readiness Report under `reports/release/`

## Stop condition

When Critical and High open counts are **zero** and ≥90% of campaign packages publish cleanly:

- Tag build **ALORA-AI-RC1**
- Freeze development for new architecture
- Future work = maintenance, feature requests, educational enhancements

## Defect severity (learner impact)

| Severity | Action |
|----------|--------|
| Critical | Auto-fix when possible; block RC1 |
| High | Auto-fix when possible; block RC1 |
| Medium | Document in RC1 report |
| Low | Document in RC1 report |

## Acceptance gates (existing)

Every lesson must satisfy PMES · PQLE · UEVB · PEEC · publisher · accessibility standards — via the live compose spine, not a new validator.
