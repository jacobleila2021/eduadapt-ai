# ULIQE Scoring Methodology

## Category weights (baseline)

| Category | Weight |
|----------|--------|
| Curriculum Accuracy | 25% |
| Completeness | 20% |
| Pedagogy | 15% |
| STEM Accuracy | 10% |
| Accessibility | 10% |
| Assessment Coverage | 10% |
| Semantic Integrity | 10% |

## Adjustments
- If STEM not applicable, STEM weight redistributes to Completeness + Semantic.
- If not `official_curriculum_publish`, Curriculum weight is halved and redistributed (uploaded lessons are curriculum-agnostic by design).

## Penalties (per finding, per category)
| Severity | Penalty |
|----------|---------|
| info | 0 |
| warning | 4 |
| error | 12 |
| critical | 25 |

Category score = `max(0, 100 - sum(penalties))`, with a floor of **55** when a category has only info/warnings (reflects current ULI maturity without inventing fields).

Overall = weighted average of category scores. Confidence decreases with errors/criticals.
