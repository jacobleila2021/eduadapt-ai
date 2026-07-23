# LCE Visual Placement Guide

## Law

Use **UVIE / verified STEM** visuals only. LCE decides **where** they appear — never invents scientific diagrams.

## Placement rule

Each visual appears **immediately after** the explanation it supports.

Matching order:

1. Concept / caption overlap with section title  
2. Sequential teach sections (`simple_explanation`, `visual`, `concept`, `diagram`, …)

## Diagram standards

- Professional SVG with rounded corners, consistent spacing, premium typography  
- Flowcharts: vertical educational pathways  
- Concept maps: hierarchical hub + orbit nodes + legend  
- Mermaid: **off by default**; enable only when explicitly requested (`allow_mermaid=True`)

## Builders

- `build_educational_flowchart_svg`  
- `build_concept_map_svg`  
- `build_subject_flowchart`  
- `build_vocabulary_concept_map_svg`  
