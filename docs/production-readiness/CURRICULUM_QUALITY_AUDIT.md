# Curriculum Quality Audit

Curriculum readiness score: 45/100.

## Evidence

- The verified pilot is CBSE Class 8 Science.
- Official question matching now fails closed below a deterministic relevance threshold.
- Fixed-pilot retrieval is blocked for mismatched grades and subjects.
- `Social Science` is no longer treated as `Science`.
- CIE returns no concepts, competencies, or progression for explicitly out-of-scope English and Social Science lessons.
- UCF no longer chooses the first package when the requested scope has no exact package.
- Mathematics, Physics, and Chemistry adversarial fixtures produced exact deterministic results.
- Cross-subject terms such as pressure, current, force, and reflection are included in isolation tests.

## Six-subject conclusion

- Mathematics: deterministic computation available; verified curriculum corpus incomplete.
- Physics: selected deterministic tools and Class 8 Science overlap available.
- Chemistry: balancing is verified; broader official curriculum corpus incomplete.
- Biology: strongest non-computation support within the Class 8 Science pilot.
- English: no substantial verified production corpus.
- Social Science: no substantial verified production corpus.

Audit-authored fixtures validate routing and isolation; they are not official curriculum sources. Live model canaries cannot replace missing licensed knowledge.

## Release requirement

Each advertised board/grade/subject needs KIE ingestion records, source licenses, UCF packages, hashes, coverage metrics, official answer keys, retrieval tests, and human curriculum sign-off.
