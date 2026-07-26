# Shared Pedagogy Guide

Canonical catalogue: `engines.subject_intelligence_core.pedagogy.SHARED_STRATEGY_CATALOGUE`.

## Supported strategies

Inquiry · Direct / Explicit Instruction · Guided Discovery · Socratic · CRA · Worked Examples · Retrieval · Spaced Learning/Practice · Reflection · PBL · Project-Based · Collaborative · POE · CER · Gradual Release · Productive Struggle · Interleaving · Multiple Representations · Conceptual Change · Experimental / Scientific Investigation · Visual Learning · Concept Mapping · Systems Thinking · Structure–Function · Cause–Effect

## Pack usage

```python
from engines.subject_intelligence_core.pedagogy import build_teaching_strategies

strategies = build_teaching_strategies(
    MY_FRAMEWORKS,  # pack subset
    domains,
    provenance="my_pack.teaching",
    default_domain="general",
    application_template="Apply {name} while teaching {primary} from the verified lesson.",
)
```

Packs keep their own framework subset and application wording for backward compatibility.
