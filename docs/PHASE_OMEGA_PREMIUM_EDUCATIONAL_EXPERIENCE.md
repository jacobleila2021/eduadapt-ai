# Phase Omega — Premium Educational Experience

**Status:** Active product law  
**Rule:** `.cursor/rules/phase-omega-premium-experience.mdc`

## Mandate

Freeze new intelligence engines. All engineering effort goes to:

- Integration of existing engines into learner-facing content
- Educational authoring (LCE as Educational Composer)
- Premium UX and publisher-grade rendering
- Pedagogically unique adaptations
- Golden lesson library and editorial acceptance

Metadata, scores, and engine execution have **zero** educational value unless they change what the learner reads, sees, hears, or practices.

## Golden principle

For every engine contribution ask:

> How does this improve what the learner reads?

If there is no visible improvement, the integration is incomplete.

## Authoring spine

1. Build a **Lesson Intelligence Board** (`engines/lesson_composition_engine/intelligence_board.py`) before any paragraph is written.
2. Author each adaptation from the board (`board_adaptations.py`) — never deep-copy + wrap.
3. Polish with PQLE + **Publisher Editorial Board** (`editorial_board.py`).
4. Render cream textbook UX; diagrams must be referenced, explained, used, and assessed.

## Smoke marker

```text
PHASE_OMEGA_PREMIUM_EDUCATIONAL_EXPERIENCE_SMOKE_OK
```

Import:

```python
from engines.lesson_composition_engine import (
    PHASE_OMEGA_PREMIUM_EDUCATIONAL_EXPERIENCE_SMOKE_OK,
    build_lesson_intelligence_board,
    review_package_editorial,
)
```

## Success

The learner cannot tell that dozens of engines created the lesson. They experience clear teaching, meaningful visuals, purposeful adaptations, and premium design. The technology disappears; the learning remains.
