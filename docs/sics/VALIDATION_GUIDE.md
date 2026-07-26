# Validation Guide (SICS)

Helpers in `engines.subject_intelligence_core.validation`:

- `finding_seed` — additive ULIQE seed dicts  
- `validate_metadata_shape`  
- `validate_misconception_rows` / `validate_diagram_rows` / `validate_accessibility_rows`  
- `validate_competency_graph`  
- `map_seed_severity_to_uliqe_cap` — caps ERROR/CRITICAL seeds to WARNING for pack signals  

## Ownership

**ULIQE** certifies lessons. SICS only helps packs emit consistent metadata and additive finding seeds. Certification thresholds must not change.
