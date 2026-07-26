# Social Science Intelligence Architecture

**Pack:** Social Science Intelligence Pack (SSIP)  
**Version:** 1.0.0  
**Smoke:** `SOCIAL_SCIENCE_INTELLIGENCE_SMOKE_OK`

## Role

SSIP is Alora AI’s humanities Subject Intelligence Pack for History, Geography, Civics / Political Science, school-level Economics, Sociology, and Environmental Studies. Built on **SIF + SICS**. Enriches verified ULI without inventing curriculum.

## Subject family registration

One analysis implementation registers over:

`social_science`, `history`, `geography`, `civics`, `environmental_science`

(School-level economics markers still enrich when the lesson subject is `social_science`. The `economics` subject key is owned by CEIP.)

## Guarantees

- No invented events, borders, or economic “facts” beyond the lesson  
- Timelines/maps are metadata hooks — LXP renders  
- Additive ULIQE `ULIQE.SOC.SSIP.*` only — certification unchanged  
