"""Intervention recommendation engine."""

from __future__ import annotations

from typing import Any

from engines.assessment_mastery_engine.misconceptions import load_misconception_bank
from engines.assessment_mastery_engine.schemas import InterventionRec, MisconceptionHit


def _intervention_index() -> dict[str, dict[str, Any]]:
    bank = load_misconception_bank()
    return {i["intervention_id"]: i for i in (bank.get("interventions") or [])}


def resolve_interventions(
    hits: list[MisconceptionHit] | list[dict[str, Any]],
    *,
    accessibility_profiles: list[str] | None = None,
    limit: int = 8,
) -> list[InterventionRec]:
    idx = _intervention_index()
    profiles = {p.lower().replace(" ", "_") for p in (accessibility_profiles or [])}
    seen: set[str] = set()
    out: list[InterventionRec] = []

    for h in hits:
        ids = h.intervention_ids if hasattr(h, "intervention_ids") else (h.get("intervention_ids") or [])
        for iid in ids:
            if iid in seen or iid not in idx:
                continue
            raw = idx[iid]
            ap = [a.lower() for a in (raw.get("accessibility_profiles") or [])]
            # prefer interventions matching accessibility needs
            priority = int(raw.get("priority") or 50)
            if profiles and ap and profiles.intersection(ap):
                priority -= 15
            seen.add(iid)
            out.append(
                InterventionRec(
                    intervention_id=iid,
                    kind=raw.get("kind") or "additional_practice",
                    title=raw.get("title") or iid,
                    description=raw.get("description") or "",
                    concept_id=raw.get("concept_id") or "",
                    priority=priority,
                    accessibility_profiles=list(raw.get("accessibility_profiles") or []),
                )
            )

    # Always allow generic EF / teacher hooks when profiles warrant
    if profiles.intersection({"adhd", "executive_function", "autism"}):
        raw = idx.get("int.ef_checklist")
        if raw and "int.ef_checklist" not in seen:
            out.append(
                InterventionRec(
                    intervention_id="int.ef_checklist",
                    kind=raw["kind"],
                    title=raw["title"],
                    description=raw.get("description") or "",
                    priority=int(raw.get("priority") or 35),
                    accessibility_profiles=list(raw.get("accessibility_profiles") or []),
                )
            )

    out.sort(key=lambda r: r.priority)
    return out[:limit]


def interventions_for_weak_concepts(
    concept_ids: list[str],
    *,
    accessibility_profiles: list[str] | None = None,
) -> list[dict[str, Any]]:
    idx = _intervention_index()
    rows = []
    for iid, raw in idx.items():
        cid = raw.get("concept_id") or ""
        if cid and cid in concept_ids:
            rows.append(InterventionRec(
                intervention_id=iid,
                kind=raw.get("kind") or "",
                title=raw.get("title") or iid,
                description=raw.get("description") or "",
                concept_id=cid,
                priority=int(raw.get("priority") or 50),
                accessibility_profiles=list(raw.get("accessibility_profiles") or []),
            ).to_dict())
    # misconception-driven extras
    from engines.assessment_mastery_engine.misconceptions import list_misconceptions

    fake_hits = []
    for cid in concept_ids:
        for m in list_misconceptions(cid):
            fake_hits.append(
                MisconceptionHit(
                    misconception_id=m["misconception_id"],
                    label=m["label"],
                    concept_id=cid,
                    confidence=0.5,
                    intervention_ids=list(m.get("intervention_ids") or []),
                )
            )
    for rec in resolve_interventions(fake_hits, accessibility_profiles=accessibility_profiles):
        if rec.intervention_id not in {r["intervention_id"] for r in rows}:
            rows.append(rec.to_dict())
    rows.sort(key=lambda r: r.get("priority", 50))
    return rows[:12]
