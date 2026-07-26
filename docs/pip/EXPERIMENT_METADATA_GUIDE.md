# Physics Experiment Metadata Guide

`engines/physics_intelligence/experiments.py` builds **scaffolds**, not invented lab scripts.

## Slot schema

| Field | Purpose |
|-------|---------|
| `aim` / `aim_prompt` | Aim from source if extractable; else prompt |
| `equipment` / `equipment_prompt` | Apparatus named in the lesson only |
| `variables` | IV / DV / controlled prompts |
| `method_steps` | Source-bound step prompts |
| `observations_prompt` | No invented data |
| `data_table_hint` | Column suggestions for LXP |
| `graph_hint` | Axes guidance |
| `conclusion_prompt` | CER-linked conclusion |
| `safety_notes` | Conservative safety reminders |

## Rules

- Never invent hazardous procedures beyond the verified lesson  
- Leave empty slots when source is silent — do not fabricate equipment lists  
- LXP owns interactive experiment UIs; PIP supplies metadata only  
- ULIQE may emit `ULIQE.PHYS.PIP.030` when scaffolds are template-only  

## Completeness signal

`experiment_completeness_signals()` returns `template_only` | `partial` | `n/a` for additive quality reporting.
