# LCE Rendering Guide

## Surfaces

| Surface | Notes |
|---------|-------|
| Streamlit `structured_renderers` | Premium vocab cards via `vocabulary_card_html` when `lce_card` |
| LXP reader | Consumes adaptation dicts + SVG |
| HTML / DOCX exporters | Same content contracts |

## Publication quality checklist

- Spacing & margins readable on laptop and mobile  
- Typography: clear hierarchy (goal → teach → practise → reflect)  
- Cards only for interactive study objects (vocabulary)  
- Professional SVG diagrams, not placeholder “imagine a diagram” text  
- Alora navy/teal palette consistency  

## Reject rendering

If EERL / LCE quality gate fails hard checks (metadata leakage, hallucination markers), mark `_meta.lce.render_blocked` and keep publish QA informed.
