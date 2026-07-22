# Universal Visual Intelligence Architecture

**Engine:** Universal Visual Intelligence Engine (UVIE)  
**Version:** 1.0.0  
**Smoke:** `UNIVERSAL_VISUAL_INTELLIGENCE_SMOKE_OK`

## Role

UVIE turns verified ULI / SIF / UCF / STEM signals into prioritized educational visuals (SVG, Mermaid, PNG, iframe). It is an orchestrator over Knowledge and Computation providers—not a generative image engine.

## Priority

NCERT / curated → GeoGebra → Matplotlib → Schemdraw → RDKit → physics → pedagogy organisers → timeline/map scaffolds → placeholder.  
`ai_illustration` remains last and fail-closed (providers disabled in 1.0).

## Guarantees

- `mutates_curriculum: false`
- `invents_curriculum: false` on produced specs
- Pedagogy never outranks STEM/knowledge when both apply
- Alt text attached via accessibility pass
- LXP owns interactive chrome; UVIE owns VisualSpec assets
