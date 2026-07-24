# Product Optimisation & Beta Readiness (POBR)

**Smoke:** `PRODUCT_OPTIMISATION_BETA_READINESS_SMOKE_OK`  
**Not an intelligence engine** — optimisation, workflow polish, and commercial readiness only.

## Mission

Prepare Alora AI for public beta with teachers, schools, parents, and students — without engineering support on every click.

## Deliverables (`reports/pobr/`)

- Product Optimisation Report
- UX Audit
- Performance Audit
- Accessibility Audit
- Rendering Audit
- Export Audit
- Beta Readiness Report
- Final Remediation Plan

## Beta product fixes included

- **PDF export** (`pdf_exporter.py`) — Word/HTML/Print plus PDF
- **Save Lesson Pack** (`lesson_pack.py`) — JSON archive for teachers
- **Share instructions** — how to print / Save as PDF
- Cream **print + HTML** backgrounds
- Student-safe vocab export labels (`Draw this` not `Picture`)
- Clearer ZIP soft-fail captions

## CLI

```bash
python -m pobr
```

## Release rule

Beta readiness requires workflows, exports, and rendering audits green, with overall score ≥ 85.
