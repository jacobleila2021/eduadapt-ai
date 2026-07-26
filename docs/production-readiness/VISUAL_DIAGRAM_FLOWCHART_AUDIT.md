# Visual, Diagram, and Flowchart Audit

Visual design score: 64/100.

## Current controls

- Lesson concept flowcharts use Alora's deterministic coloured builder.
- Water-cycle and vocabulary visuals use labelled deterministic SVG.
- Model-authored study SVG is no longer selected over built diagrams.
- All SVG reaching the structured renderer is parsed through a strict tag/attribute allow-list.
- External URLs, scripts, event handlers, and unsafe URL references are removed.
- HTML vocabulary export now embeds the deterministic lesson visual.
- Worksheet HTML includes only sanitized SVG.

## Subject coverage

- Mathematics: SymPy exact result and LaTeX paths exist.
- Physics: deterministic pressure/force calculations and selected graph/diagram engines exist.
- Chemistry: ChemPy balancing with atom-count validation exists.
- Biology: selected verified figures and deterministic builders exist.
- Circuits, molecular structures, ray diagrams, anatomy, and advanced graphs do not yet have a complete audited publication-quality catalogue.

## Remaining release gaps

- No approved visual golden set across all subjects and grades.
- No automated semantic-label comparison for every diagram.
- GeoGebra and rich interactive embeds are not validated across browsers/exports.
- Colour-blind simulation, 400% zoom, print/PDF parity, and localization expansion require further testing.
- Generated image providers are disabled by default; enabling one requires provenance, licensing, quality moderation, and alt-text policy.

Deterministic or officially sourced visuals must remain authoritative. Model output may propose presentation metadata only.
