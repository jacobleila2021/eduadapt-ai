# Biology Laboratory Metadata Guide

`engines/biology_intelligence/laboratory.py` builds **scaffolds**, not invented lab scripts.

## Slots

Aim, equipment, specimens, microscopy, variables, observation sheets, data recording, conclusions (CER), safety guidance.

## Rules

- Source-bound: do not invent specimens, stains, or dissection steps  
- Always include conservative safety guidance when a lab scaffold is emitted  
- LXP owns interactive labs; BIP owns metadata  
- ULIQE may emit `ULIQE.BIO.BIP.030` when scaffolds are template-only  

## Completeness

`laboratory_completeness_signals()` → `template_only` | `partial` | `n/a` plus `safety_metadata`.
