# SICS API Documentation

```python
from engines.subject_intelligence_core import SUBJECT_INTELLIGENCE_CORE_SMOKE_OK, core_health
from engines.subject_intelligence_core.misconceptions import detect_from_catalogue
from engines.subject_intelligence_core.taxonomy import detect_domains, concept_graph_from_uli
from engines.subject_intelligence_core.pedagogy import build_teaching_strategies, resolve_strategies
from engines.subject_intelligence_core.diagrams import recommend_visuals_from_catalogue
from engines.subject_intelligence_core.assessment import build_assessment_hints, build_revision_summary
from engines.subject_intelligence_core.tutor_metadata import socratic_block, graduated_hints_block
from engines.subject_intelligence_core.analytics import from_analysis
from engines.subject_intelligence_core.validation import finding_seed, validate_misconception_rows

assert SUBJECT_INTELLIGENCE_CORE_SMOKE_OK is True
print(core_health())
```

Optional engine: `SubjectIntelligenceCoreEngine` (diagnostic only; not VLIE-registered).
