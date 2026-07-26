"""Central misconception detection framework — catalogues stay pack-owned."""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

from engines.subject_intelligence_core.shared_models import MisconceptionHit


def detect_from_catalogue(
    catalogue: Sequence[Mapping[str, Any]],
    text: str,
    *,
    provenance: str,
    limit: int = 12,
    min_chars: int = 8,
) -> list[dict[str, Any]]:
    """
    Pattern-match learner/lesson text against a pack misconception catalogue.

    Output shape matches historical STEM packs (lean dict, no empty extras).
    """
    blob = (text or "").lower()
    if len(blob) < min_chars:
        return []
    hits: list[dict[str, Any]] = []
    for row in catalogue:
        patterns = list(row.get("patterns") or [])
        matched = [p for p in patterns if re.search(p, blob, re.I)]
        if not matched:
            continue
        hit = MisconceptionHit(
            misconception_id=str(row["misconception_id"]),
            label=str(row["label"]),
            domain=str(row.get("domain") or "general"),
            matched_patterns=matched[:3],
            correction_strategy=str(row.get("correction") or row.get("correction_strategy") or ""),
            related_concepts=list(row.get("related_concepts") or []),
            provenance=provenance,
            confidence=min(0.9, 0.5 + 0.15 * len(matched)),
            severity=str(row.get("severity") or "medium"),
            remediation=dict(row.get("remediation") or {}),
            intervention=dict(row.get("intervention") or {}),
            evidence_links=list(row.get("evidence_links") or []),
        )
        hits.append(hit.to_dict())
        if len(hits) >= limit:
            break
    return hits
