# Phase Omega 2.0 — Publisher Master Editorial System (PMES)

**Authority:** Highest editorial gate before a lesson reaches a learner.  
**Smoke:** `PHASE_OMEGA_2_PMES_SMOKE_OK`

## What PMES is

PMES does **not** score. It:

- critiques with publisher comments
- rewrites master-teacher prose
- packages teaching diagrams (title, caption, explanation, callouts, practice)
- redesigns vocabulary as premium flashcards
- rejects until reviewers approve

It lives inside LCE — **not** a new intelligence engine.

## Modules

| Module | Role |
|--------|------|
| `publisher_style_guide.py` | Global writing + visual law (cream `#FFF9EE`, typography, banned phrases) |
| `master_teacher.py` | Curiosity → understanding → analogy → example → transition |
| `pmes.py` | Comment review → rewrite loop → Publisher Review Report |
| `board_adaptations.py` | Unique lessons per learner profile |

## Pipeline

Intelligence Board → board authorship → PQLE polish → Editorial Board → **PMES** → render

Publication requires PQI readiness **and** editorial approval **and** PMES approval.

## Style guide

Every renderer must respect `style_guide_css()`. No grey dashboard override of the cream textbook canvas.

## Stop condition

Opening any lesson should make an educator believe:

> “This feels like a professionally published digital textbook.”

not

> “This feels AI generated.”
