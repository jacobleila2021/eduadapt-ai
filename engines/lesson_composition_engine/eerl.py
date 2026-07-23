"""Educational Editorial Review Layer (EERL) — mandatory quality gate before render."""

from __future__ import annotations

import re
from typing import Any, Mapping

from engines.lesson_composition_engine.schemas import (
    METADATA_LEAK_PATTERNS,
    EerlCheck,
    EerlReport,
    PACK_VERSION,
)

PRODUCTION_THRESHOLD = 0.88

AI_ROBOTIC = (
    "delve",
    "dive into",
    "as an ai",
    "in conclusion",
    "let's explore",
    "in this lesson we will explore",
    "it is important to note that",
    "without further ado",
)


def _text_blob(adaptation: Mapping[str, Any]) -> str:
    parts: list[str] = []
    if adaptation.get("big_idea"):
        parts.append(str(adaptation["big_idea"]))
    for sec in adaptation.get("sections") or []:
        if isinstance(sec, dict):
            parts.append(str(sec.get("title") or ""))
            parts.append(str(sec.get("body") or ""))
    for w in adaptation.get("word_wall") or []:
        if isinstance(w, dict):
            parts.append(str(w.get("term") or ""))
            parts.append(str(w.get("definition") or ""))
    for q in adaptation.get("short_answer") or []:
        if isinstance(q, dict):
            parts.append(str(q.get("question") or ""))
    return "\n".join(parts)


def _metadata_leak_hits(text: str) -> list[str]:
    hits = []
    lower = text.lower()
    for pat in METADATA_LEAK_PATTERNS:
        if re.search(pat, lower, flags=re.I):
            hits.append(pat)
    return hits


def _duplicate_paragraphs(text: str) -> int:
    paras = [p.strip().lower() for p in re.split(r"\n\s*\n", text) if len(p.strip()) > 40]
    seen: set[str] = set()
    dups = 0
    for p in paras:
        key = re.sub(r"\W+", " ", p)[:180]
        if key in seen:
            dups += 1
        seen.add(key)
    return dups


def review_adaptation(
    adaptation_id: str,
    adaptation: Mapping[str, Any],
    *,
    clg: Mapping[str, Any] | None = None,
) -> EerlReport:
    clg = dict(clg or {})
    text = _text_blob(adaptation)
    checks: list[EerlCheck] = []

    leaks = _metadata_leak_hits(text)
    checks.append(
        EerlCheck(
            "metadata_leakage",
            "Metadata leakage",
            passed=len(leaks) == 0,
            score=1.0 if not leaks else 0.0,
            detail=f"hits={len(leaks)}",
        )
    )

    dups = _duplicate_paragraphs(text)
    checks.append(
        EerlCheck(
            "duplicate_content",
            "Duplicate content",
            passed=dups == 0,
            score=1.0 if dups == 0 else max(0.0, 1.0 - 0.25 * dups),
            detail=f"duplicates={dups}",
        )
    )

    claims = [c.lower() for c in (clg.get("claim_texts") or []) if c]
    concepts = [str(c.get("name") or "").lower() for c in (clg.get("core_concepts") or [])]
    blob = text.lower()
    overlap = 0
    for c in claims[:12]:
        tokens = [
            t
            for t in re.findall(r"[a-z]{5,}", c)
            if t not in {"about", "their", "there", "these", "those"}
        ]
        if tokens and sum(1 for t in tokens[:6] if t in blob) >= max(1, min(3, len(tokens) // 3)):
            overlap += 1
    for name in concepts:
        if name and name in blob:
            overlap += 1
    fidelity = (
        1.0
        if not claims and not concepts
        else min(1.0, overlap / max(3, min(8, len(claims) + len(concepts))))
    )
    if adaptation_id in {"vocabulary", "parent", "worksheet"}:
        fidelity = max(fidelity, 0.85)
    checks.append(
        EerlCheck(
            "source_fidelity",
            "Source fidelity",
            passed=fidelity >= 0.45,
            score=fidelity,
            detail=f"overlap_units={overlap}",
        )
    )

    vocab = adaptation.get("word_wall") or clg.get("vocabulary") or []
    freq_flag = bool((adaptation.get("_lce") or {}).get("frequency_based"))
    if adaptation_id == "vocabulary":
        vocab_ok = isinstance(vocab, list) and len(vocab) >= 3 and not freq_flag
    else:
        vocab_ok = not freq_flag
    checks.append(
        EerlCheck(
            "vocabulary_quality",
            "Vocabulary quality",
            passed=vocab_ok,
            score=1.0 if vocab_ok else 0.2,
            detail="clg_subject_vocab" if vocab_ok else "frequency_or_thin",
        )
    )

    if adaptation_id == "vocabulary":
        flow_ok = len(vocab) >= 3
    elif adaptation_id == "worksheet":
        flow_ok = len(adaptation.get("short_answer") or []) >= 4
    else:
        sections = adaptation.get("sections") or []
        titles = " ".join(str(s.get("title") or "") for s in sections).lower()
        flow_ok = len(sections) >= 5 and bool(adaptation.get("big_idea"))
        flow_ok = flow_ok and not (
            "learning objectives" in titles and "explain learning" in text.lower()
        )
    checks.append(
        EerlCheck(
            "pedagogical_flow",
            "Pedagogical flow",
            passed=flow_ok,
            score=1.0 if flow_ok else 0.3,
            detail=f"sections={len(adaptation.get('sections') or [])}",
        )
    )

    visuals_ok = True
    if "imagine a diagram" in text.lower() or "imagine a labelled diagram" in text.lower():
        visuals_ok = False
    checks.append(
        EerlCheck(
            "visual_placement",
            "Visual placement",
            passed=visuals_ok,
            score=1.0 if visuals_ok else 0.0,
            detail="no_placeholder_imagine" if visuals_ok else "placeholder_diagram_language",
        )
    )

    hallu = ("need_engine:" in blob) or ("need_source:" in blob)
    checks.append(
        EerlCheck(
            "hallucination",
            "Hallucination markers",
            passed=not hallu,
            score=0.0 if hallu else 1.0,
            detail="clean" if not hallu else "need_engine_or_source",
        )
    )

    # --- PQLE expanded editorial checks ---
    robotic_hits = [p for p in AI_ROBOTIC if p in blob]
    checks.append(
        EerlCheck(
            "robotic_language",
            "Robotic / generic AI phrasing",
            passed=len(robotic_hits) == 0,
            score=1.0 if not robotic_hits else max(0.0, 1.0 - 0.25 * len(robotic_hits)),
            detail=f"hits={len(robotic_hits)}",
        )
    )

    # Oversized paragraphs
    oversized = 0
    fragmented = 0
    for sec in adaptation.get("sections") or []:
        if not isinstance(sec, dict):
            continue
        body = str(sec.get("body") or "")
        wc = len(re.findall(r"\b\w+\b", body))
        sc = len([p for p in re.split(r"[.!?]+", body) if p.strip()])
        if wc > 140:
            oversized += 1
        if 0 < wc < 10 and "\n- " not in body and adaptation_id in {"standard", "auditory", "teacher"}:
            fragmented += 1
    checks.append(
        EerlCheck(
            "paragraph_quality",
            "Paragraph quality",
            passed=oversized == 0 and fragmented <= 1,
            score=1.0 if oversized == 0 and fragmented <= 1 else 0.45,
            detail=f"oversized={oversized};fragments={fragmented}",
        )
    )

    # Abrupt / missing educational sequencing for classroom lessons
    roles = {str(s.get("role") or "") for s in (adaptation.get("sections") or []) if isinstance(s, dict)}
    titles = " ".join(str(s.get("title") or "").lower() for s in (adaptation.get("sections") or []) if isinstance(s, dict))
    if adaptation_id in {"vocabulary", "worksheet", "parent"}:
        seq_ok = True
        seq_score = 1.0
    else:
        need = {"summary", "reflection"}
        seq_ok = all(n in roles or n in titles for n in need)
        seq_score = 1.0 if seq_ok else 0.4
    checks.append(
        EerlCheck(
            "educational_sequencing",
            "Educational sequencing",
            passed=seq_ok,
            score=seq_score,
            detail="summary+reflection" if seq_ok else "missing_close",
        )
    )

    # Missing diagrams for non-vocab adaptations
    svg = str(
        adaptation.get("svg_diagram")
        or adaptation.get("flowchart_svg")
        or adaptation.get("concept_map_svg")
        or ((adaptation.get("diagram_question") or {}).get("svg_diagram") if isinstance(adaptation.get("diagram_question"), dict) else "")
        or ""
    )
    if adaptation_id == "vocabulary":
        diagram_ok = True
        diagram_score = 1.0
    else:
        diagram_ok = svg.startswith("<svg") and len(svg) > 120
        diagram_score = 1.0 if diagram_ok else 0.35
    checks.append(
        EerlCheck(
            "diagram_presence",
            "Diagram presence",
            passed=diagram_ok,
            score=diagram_score,
            detail="svg_ok" if diagram_ok else "missing_svg",
        )
    )

    # Excessive bullet lists in mainstream prose
    bullet_heavy = 0
    for sec in adaptation.get("sections") or []:
        if isinstance(sec, dict) and str(sec.get("body") or "").count("\n- ") >= 5:
            bullet_heavy += 1
    bullets_ok = adaptation_id in {"ld", "dyslexia", "adhd", "autism"} or bullet_heavy <= 2
    checks.append(
        EerlCheck(
            "bullet_discipline",
            "Bullet list discipline",
            passed=bullets_ok,
            score=1.0 if bullets_ok else 0.5,
            detail=f"heavy_sections={bullet_heavy}",
        )
    )

    # Weak summary
    has_summary = "summary" in roles or "summary" in titles or bool(adaptation.get("summary"))
    if adaptation_id in {"vocabulary", "worksheet"}:
        summary_ok = True
    else:
        summary_ok = has_summary
    checks.append(
        EerlCheck(
            "summary_quality",
            "Summary quality",
            passed=summary_ok,
            score=1.0 if summary_ok else 0.4,
            detail="present" if summary_ok else "missing",
        )
    )

    words = re.findall(r"\b\w+\b", text)
    pub_ok = True
    if adaptation_id not in {"vocabulary", "worksheet"} and len(words) < 120:
        pub_ok = False
    checks.append(
        EerlCheck(
            "publication_quality",
            "Publication quality",
            passed=pub_ok,
            score=1.0 if pub_ok else 0.4,
            detail=f"words={len(words)}",
        )
    )

    scores = [c.score for c in checks]
    overall = sum(scores) / max(len(scores), 1)
    failures = [c.label for c in checks if not c.passed]
    hard_fail = any(
        c.check_id in {"metadata_leakage", "hallucination", "robotic_language"} and not c.passed
        for c in checks
    )
    production = (overall >= PRODUCTION_THRESHOLD) and not hard_fail and not failures
    if not hard_fail and overall >= PRODUCTION_THRESHOLD and len(failures) <= 2:
        production = True

    return EerlReport(
        ok=not hard_fail and overall >= 0.55,
        overall_score=round(overall, 3),
        production_ready=production,
        checks=[c.to_dict() for c in checks],
        failures=failures,
        version=PACK_VERSION,
    )


def review_package(adaptations: Mapping[str, Any], clg: Mapping[str, Any]) -> dict[str, Any]:
    reports = {}
    all_ready = True
    worst = 1.0
    for key, value in adaptations.items():
        if key.startswith("_") or not isinstance(value, dict):
            continue
        report = review_adaptation(key, value, clg=clg)
        reports[key] = report.to_dict()
        worst = min(worst, report.overall_score)
        if not report.production_ready:
            all_ready = False
    return {
        "ok": all_ready,
        "production_ready": all_ready,
        "worst_score": round(worst if reports else 0.0, 3),
        "by_adaptation": reports,
        "version": PACK_VERSION,
        "threshold": PRODUCTION_THRESHOLD,
    }
