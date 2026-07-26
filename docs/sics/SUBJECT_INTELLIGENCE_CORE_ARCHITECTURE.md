# Subject Intelligence Core Architecture

**Layer:** Subject Intelligence Core Services (SICS)  
**Version:** 1.0.0  
**Smoke:** `SUBJECT_INTELLIGENCE_CORE_SMOKE_OK`

## Role

SICS is shared **infrastructure** for Subject Intelligence Packs. It does not teach subjects, invent curriculum, or replace ATIE, AIE, AME, LAIE, LXP, VMLE, or ULIQE.

It consolidates duplicated STEM-pack patterns into reusable builders so future packs (English, Social Science, CS, Commerce, Languages) inherit the same foundation.

## Position in the stack

```
ULI → SIF (detect + analyse) → Subject Pack (MIP/PIP/CIP/BIP/…)
                                    ↑
                                   SICS (shared builders / models)
Downstream: ATIE · AIE · AME · LAIE · LXP/VMLE · ULIQE (additive seeds)
```

## Modules

| Module | Responsibility |
|--------|----------------|
| `pedagogy` | Shared strategy catalogue + teaching strategy builder |
| `misconceptions` | Catalogue-driven pattern detection framework |
| `taxonomy` | Domain detection, prerequisites, concept graphs |
| `competencies` | Competency graph helpers (UCF remains authority) |
| `diagrams` / `visualization` | Visual recommendation / hook metadata |
| `assessment` / `learning_objectives` | Bloom/DOK / revision metadata (AME owns items) |
| `accessibility` | Recommendation row normalization (AIE owns UX) |
| `tutor_metadata` | Socratic / hints / fading / diagnosis blocks (ATIE owns chat) |
| `analytics` | LAIE-oriented event templates |
| `validation` | Metadata validators + finding-seed helpers |
| `metadata` / `shared_models` / `utilities` | Common envelopes and ULI text extraction |

## Guarantees

- No curriculum generation  
- No engine behaviour changes outside subject-pack internal refactors  
- Pack public APIs unchanged  
- ULIQE certification thresholds unchanged  

## Consumers

MIP, PIP, CIP, BIP already call SICS for domain graphs, misconception detection, teaching strategies, and visual recommendations.
