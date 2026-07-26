# SICS Migration Guide

## Completed (STEM packs)

MIP, PIP, CIP, and BIP now consume SICS for:

- Domain detection / prerequisite / concept graph (`taxonomy`)
- Misconception detection (`misconceptions.detect_from_catalogue`)
- Teaching strategy assembly (`pedagogy.build_teaching_strategies`)
- Visual recommendations (`diagrams.recommend_visuals_from_catalogue`)
- MIP pedagogy/assessment/tutor/accessibility helpers

Public pack APIs, registration, smoke constants, and ULIQE additive rule families are unchanged.

## Future packs

Start from SICS builders; only pack-specific catalogues and wording should live in the pack package.

## Rollback

Subject packs still export the same function names. Removing SICS would require restoring inlined helpers — keep SICS as a hard dependency going forward.
