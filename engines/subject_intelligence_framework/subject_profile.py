"""Subject profile helpers — detect subject from ULI / UCF metadata (curriculum-agnostic)."""

from __future__ import annotations

import re
from typing import Any, Mapping

from engines.subject_intelligence_framework.schemas import SubjectDetection

# Keyword → subject_key (order matters: more specific first)
_SUBJECT_MARKERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("chemistry", ("chemistry", "chemical", "mole", "reaction", "acid", "base", "organic")),
    ("physics", ("physics", "force", "motion", "velocity", "optics", "electricity", "magnet")),
    ("biology", ("biology", "cell", "photosynthesis", "organism", "tissue", "enzyme", "ecology")),
    ("mathematics", ("mathematics", "maths", "algebra", "geometry", "calculus", "equation", "trigonometry")),
    ("computer_science", ("computer science", "programming", "python", "algorithm", "coding", "software")),
    ("english", ("english", "grammar", "comprehension", "literature", "essay writing", "poetry")),
    ("history", ("history", "civilisation", "civilization", "empire", "revolution", "ancient")),
    ("geography", ("geography", "climate", "map", "latitude", "longitude", "rainfall")),
    ("civics", ("civics", "constitution", "democracy", "citizenship", "parliament")),
    ("economics", ("economics", "gdp", "inflation", "market", "demand", "supply")),
    ("commerce", ("commerce", "trade", "business studies", "accountancy", "accounting")),
    ("business_studies", ("business studies", "entrepreneur", "management", "marketing")),
    ("environmental_science", ("environmental science", "environment", "pollution", "sustainability")),
    ("social_science", ("social science", "social studies")),
    ("languages", ("language", "hindi", "french", "spanish", "sanskrit", "tamil", "malayalam")),
)

_ALIAS = {
    "math": "mathematics",
    "maths": "mathematics",
    "science": "biology",  # weak default; STEM classifier may override
    "bio": "biology",
    "chem": "chemistry",
    "phy": "physics",
    "cs": "computer_science",
    "ict": "computer_science",
    "evs": "environmental_science",
    "sst": "social_science",
}


def detect_subject_from_uli(uli: Any) -> SubjectDetection:
    """
    Detect subject from ULI educational structure / envelope metadata / text markers.
    Does not invent curriculum alignment — detection only.
    """
    edu: Mapping[str, Any] = {}
    text_bits: list[str] = []
    try:
        edu = dict(uli.educational_structure())
    except Exception:  # noqa: BLE001
        edu = {}

    # Prefer explicit Subject: header from source envelope text
    try:
        envelope_text = str(uli.source_envelope.get("text") or "")[:800]
        m = re.search(r"\bsubject\s*:\s*([^\n|]+)", envelope_text, re.I)
        if m:
            declared_from_text = m.group(1).strip().lower()
            key = _ALIAS.get(declared_from_text, declared_from_text.replace(" ", "_"))
            for subject_key, _markers in _SUBJECT_MARKERS:
                if (
                    key == subject_key
                    or declared_from_text in subject_key
                    or subject_key.replace("_", " ") in declared_from_text
                ):
                    return SubjectDetection(
                        subject_key=subject_key,
                        confidence=0.94,
                        provenance="source_subject_header",
                        evidence={"declared": declared_from_text},
                    )
    except Exception:  # noqa: BLE001
        pass

    declared = str(edu.get("subject") or edu.get("discipline") or "").strip().lower()
    if declared:
        key = _ALIAS.get(declared, declared.replace(" ", "_"))
        for subject_key, _markers in _SUBJECT_MARKERS:
            if key == subject_key or declared in subject_key or subject_key.replace("_", " ") in declared:
                return SubjectDetection(
                    subject_key=subject_key,
                    confidence=0.92,
                    provenance="uli_declared_subject",
                    evidence={"declared": declared},
                )
        # Unknown declared subject — keep as languages/general fallback key
        if declared:
            return SubjectDetection(
                subject_key=_ALIAS.get(declared, "general"),
                confidence=0.7,
                provenance="uli_declared_unmapped",
                evidence={"declared": declared},
            )

    try:
        text_bits.append(str(edu.get("topic") or ""))
        text_bits.append(str(edu.get("title") or ""))
        profile = dict(uli.universal_profile)
        text_bits.append(str(profile.get("topic") or ""))
        for claim in list(uli.claim_ledger)[:40]:
            if isinstance(claim, Mapping):
                text_bits.append(str(claim.get("text") or "")[:200])
        stem = dict(uli.stem_structure())
        for c in list(stem.get("claims_found") or [])[:20]:
            if isinstance(c, Mapping):
                text_bits.append(str(c.get("kind") or ""))
                text_bits.append(str(c.get("raw") or "")[:80])
    except Exception:  # noqa: BLE001
        pass

    blob = " ".join(text_bits).lower()
    scores: dict[str, int] = {}
    for subject_key, markers in _SUBJECT_MARKERS:
        hit = sum(1 for m in markers if re.search(rf"\b{re.escape(m)}\b", blob))
        if hit:
            scores[subject_key] = hit

    # STEM kind boosts
    try:
        kinds = {
            str((c or {}).get("kind") or "")
            for c in (uli.stem_structure().get("claims_found") or [])
            if isinstance(c, Mapping)
        }
        if any(k.startswith("math") for k in kinds):
            scores["mathematics"] = scores.get("mathematics", 0) + 3
        if "chemistry_equation" in kinds or "molecule" in kinds:
            scores["chemistry"] = scores.get("chemistry", 0) + 3
        if "force_problem" in kinds or "physics_diagram" in kinds:
            scores["physics"] = scores.get("physics", 0) + 3
    except Exception:  # noqa: BLE001
        pass

    if not scores:
        return SubjectDetection(
            subject_key="general",
            confidence=0.2,
            provenance="no_marker",
            candidates=[],
        )

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    best_key, best_score = ranked[0]
    confidence = min(0.95, 0.4 + 0.1 * best_score)
    return SubjectDetection(
        subject_key=best_key,
        confidence=confidence,
        provenance="uli_keyword_stem",
        candidates=[k for k, _ in ranked[:5]],
        evidence={"scores": dict(ranked[:8])},
    )
