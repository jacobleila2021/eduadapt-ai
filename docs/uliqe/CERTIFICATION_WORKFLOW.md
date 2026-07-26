# ULIQE Certification Workflow

```
validate_uli(uli)
        ↓
overall_score + findings
        ↓
┌─────────────────────────────────────┐
│ critical schema / grounding failure │ → Rejected
│ score ≥ 90 and no errors            │ → Production Ready (auto downstream)
│ score ≥ 80                          │ → Gold (human review recommended)
│ score ≥ 65                          │ → Silver (human review)
│ else                                │ → Needs Review
└─────────────────────────────────────┘
```

**Policy:** Only `Production Ready` sets `downstream_allowed=True` for automatic flow into AME/AIE/ALE/…/Export/Publication.

Gold/Silver may be used manually; they do **not** auto-bypass the gate helper.

Existing Alora generation remains unchanged until callers adopt `gate_for_downstream()`.
