# Chemistry Laboratory Metadata Guide

`engines/chemistry_intelligence/laboratory.py` builds **scaffolds**, not invented lab scripts.

## Slots

Aim, equipment, experimental setup, variables, observation tables, safety precautions, hazard warnings, chemical handling, waste disposal, conclusions (CER).

## Rules

- Source-bound: do not invent apparatus, reagents, or hazardous procedures  
- Always include conservative safety / hazard reminders when a lab scaffold is emitted  
- LXP owns simulations; CIP owns metadata  
- ULIQE may emit `ULIQE.CHEM.CIP.030` (template-only) or `.035` (missing safety) as INFO/WARNING  

## Completeness

`laboratory_completeness_signals()` → `template_only` | `partial` | `n/a` plus `safety_metadata` / `hazard_metadata`.
