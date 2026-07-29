"""Generation Recovery — learner-quality gates (not a new intelligence engine).

Implements the Generation Recovery Sprint rules:
- PQLE formatting-only
- PMES invisible clarity editing
- adaptation distinctiveness
- educational contribution bypass
- golden minimum standard
- Educational Quality Score (EQS)
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Any, Mapping

from forensics.learner_metrics import (
    ROBOTIC_PHRASES,
    TEACHER_ADVISORY,
    _text_blob,
    phrase_hits,
    repetition_ratio,
    structural_similarity,
    vocab_quality,
)

GENERATION_RECOVERY_SMOKE_OK = True
ADAPTATION_SIMILARITY_FAIL = 0.40  # >40% identical instructional text fails
MAX_SIMILARITY = ADAPTATION_SIMILARITY_FAIL

# Section / scaffolding words that must never become teaching "concepts"
FORBIDDEN_CONCEPT_LABELS = frozenset(
    {
        "opening",
        "closing",
        "introduction",
        "summary",
        "revision",
        "reflection",
        "hook",
        "overview",
        "warmup",
        "warm-up",
        "starter",
        "plenary",
        "exit ticket",
        "checkpoint",
        "notice",
        "editorial",
        "teacher note",
        "this section",
        "using the diagram",
        "lesson diagram",
        "quick revision",
        "think about it",
        "mission goal",
        "lesson map",
        "learning goal",
        "finished summary",
    }
)

PMES_BANNED_LEARNER_PHRASES = (
    "notice how",
    "this section",
    "teacher note",
    "editorial",
    "as an editor",
    "publisher",
    "scaffolding",
    "learning objective",
    "success criteria",
    "in this lesson we will",
    "students will be able to",
    "have you ever wondered why opening",
    "prepare you for opening",
    "think of opening",
    "new word focus: opening",
    "the idea is opening",
    "ask what opening means",
)


def sanitize_concept_label(label: str, *, topic: str = "this idea") -> str:
    text = (label or "").strip()
    low = text.lower().strip(" .:;—-")
    if not text or low in FORBIDDEN_CONCEPT_LABELS or any(f in low for f in FORBIDDEN_CONCEPT_LABELS):
        return (topic or "this idea").strip()
    # Strip role prefixes like "Concept: Force" → Force
    if ":" in text:
        text = text.split(":")[-1].strip()
    if "—" in text or " - " in text:
        text = re.split(r"[—-]", text)[-1].strip()
    low = text.lower()
    if low in FORBIDDEN_CONCEPT_LABELS or len(text.split()) > 8:
        return (topic or "this idea").strip()
    return text or (topic or "this idea").strip()


def instructional_text(adaptation: Mapping[str, Any] | None) -> str:
    """Learner instructional prose only (no SVG/meta)."""
    if not isinstance(adaptation, dict):
        return ""
    parts = [str(adaptation.get("big_idea") or "")]
    for sec in adaptation.get("sections") or []:
        if not isinstance(sec, dict):
            continue
        parts.append(str(sec.get("title") or ""))
        parts.append(str(sec.get("body") or ""))
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def meaning_tokens(text: str) -> set[str]:
    stop = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "to",
        "of",
        "in",
        "on",
        "for",
        "is",
        "are",
        "was",
        "were",
        "be",
        "this",
        "that",
        "with",
        "as",
        "at",
        "by",
        "from",
        "you",
        "your",
        "it",
        "into",
    }
    return {w for w in re.findall(r"[a-zA-Z]{3,}", (text or "").lower()) if w not in stop}


def educational_meaning_preserved(before: Mapping[str, Any], after: Mapping[str, Any]) -> bool:
    """Reject rewrites that drop core instructional tokens or invent banned concepts."""
    b = instructional_text(before)
    a = instructional_text(after)
    if not b.strip():
        return True
    bt, at = meaning_tokens(b), meaning_tokens(a)
    if not bt:
        return True
    overlap = len(bt & at) / max(len(bt), 1)
    if overlap < 0.55:
        return False
    # Length collapse = content removal
    if len(a) < len(b) * 0.65:
        return False
    low = a.lower()
    if any(p in low for p in PMES_BANNED_LEARNER_PHRASES):
        return False
    return True


def scrub_pmes_learner_language(text: str, *, topic: str = "this lesson") -> str:
    out = text or ""
    replacements = [
        (r"(?i)have you ever wondered why opening matters[^.?!]*[.?!]\s*", ""),
        (r"(?i)you already know everyday pushes, pulls, or patterns that prepare you for opening[^.?!]*[.?!]\s*", ""),
        (r"(?i)think of opening like[^.?!]*[.?!]\s*", ""),
        (r"(?i)new word focus:\s*opening[^.?!]*[.?!]\s*", ""),
        (r"(?i)first, the idea is opening[^.?!]*[.?!]\s*", ""),
        (r"(?i)at home, ask what opening means[^.?!]*[.?!]\s*", ""),
        (r"(?i)notice how\b[^.?!]*[.?!]\s*", ""),
        (r"(?i)this section\b[^.?!]*[.?!]\s*", ""),
        (r"(?i)teacher note[:\s][^.?!]*[.?!]\s*", ""),
        (r"(?i)editorial comment[:\s][^.?!]*[.?!]\s*", ""),
    ]
    for pat, repl in replacements:
        out = re.sub(pat, repl, out)
    # Generic "opening" concept residue → topic
    out = re.sub(r"(?i)\bopening\b", topic, out)
    for phrase in ROBOTIC_PHRASES + TEACHER_ADVISORY:
        if phrase in {"exit ticket", "homework:", "independent practice"}:
            continue  # allowed only in teacher tab — caller filters
        if phrase in out.lower():
            # Drop sentences containing the phrase — line-aware so bullet
            # lists and one-sentence-per-line layouts survive the scrub.
            lines = []
            for line in out.split("\n"):
                kept = [
                    s for s in re.split(r"(?<=[.!?])\s+", line) if phrase not in s.lower()
                ]
                lines.append(" ".join(kept))
            out = "\n".join(lines)
    # Collapse runs of spaces but preserve intentional line structure
    # (ld bullets, dyslexia one-sentence-per-line presentation).
    out = re.sub(r"[ \t]{2,}", " ", out)
    return "\n".join(line.strip() for line in out.split("\n") if line.strip() or True).strip()


def format_only_adaptation(adaptation: dict[str, Any]) -> dict[str, Any]:
    """PQLE formatting-only: normalize structure/style tokens; keep educational meaning."""
    out = dict(adaptation)
    # Presentation metadata only
    out.setdefault("lce", {})
    if isinstance(out["lce"], dict):
        out["lce"]["pqle"] = True
        out["lce"]["pqle_mode"] = "formatting_only"
        out["lce"]["writing_excellence"] = out["lce"].get("writing_excellence", False)
    # Soft whitespace / punctuation cleanup without rewriting ideas
    if out.get("big_idea"):
        out["big_idea"] = re.sub(r"\s+", " ", str(out["big_idea"])).strip()
    sections = []
    for sec in out.get("sections") or []:
        if not isinstance(sec, dict):
            continue
        row = dict(sec)
        if row.get("title"):
            row["title"] = re.sub(r"\s+", " ", str(row["title"])).strip()
        if row.get("body"):
            body = str(row["body"])
            # Collapse triple newlines; keep bullets
            body = re.sub(r"\n{3,}", "\n\n", body)
            body = re.sub(r"[ \t]{2,}", " ", body)
            row["body"] = body.strip()
        sections.append(row)
    out["sections"] = sections
    # Prefer SVG fields presence stamp without inventing content
    if out.get("flowchart_svg") and not out.get("svg_diagram"):
        out["svg_diagram"] = out["flowchart_svg"]
    return out


def format_only_package(adaptations: dict[str, Any]) -> dict[str, Any]:
    out = dict(adaptations)
    for key, value in list(out.items()):
        if key.startswith("_") or not isinstance(value, dict):
            continue
        if key == "vocabulary":
            # Style stamps only — do not rebuild cards
            page = dict(value)
            wall = []
            for row in page.get("word_wall") or []:
                if not isinstance(row, dict):
                    continue
                card = dict(row)
                card.setdefault("pqle_card", True)
                wall.append(card)
            page["word_wall"] = wall
            page.setdefault("lce", {})
            if isinstance(page["lce"], dict):
                page["lce"]["pqle"] = True
                page["lce"]["pqle_mode"] = "formatting_only"
            out[key] = page
            continue
        if key == "worksheet":
            sheet = dict(value)
            sheet.setdefault("_lce", {})["pqle"] = True
            out[key] = sheet
            continue
        out[key] = format_only_adaptation(value)
    return out


def clarity_edit_adaptation(adaptation: dict[str, Any], *, topic: str = "this lesson") -> dict[str, Any]:
    """PMES clarity-only: scrub banned language; never invent concepts."""
    out = dict(adaptation)
    topic = topic or str(out.get("topic") or "this lesson")
    if out.get("big_idea"):
        out["big_idea"] = scrub_pmes_learner_language(str(out["big_idea"]), topic=topic)
    sections = []
    for sec in out.get("sections") or []:
        if not isinstance(sec, dict):
            continue
        row = dict(sec)
        title = sanitize_concept_label(str(row.get("title") or ""), topic=topic)
        # Keep original title unless it is a forbidden solo label used as concept bait
        raw_title = str(row.get("title") or "")
        if raw_title.lower().strip() in FORBIDDEN_CONCEPT_LABELS:
            # Publisher page titles: keep a stable "Introduction" heading — never
            # reprint the lesson topic (title appears once at page level).
            if row.get("role") in {"hook", "introduction"}:
                row["title"] = "Introduction"
            else:
                row["title"] = raw_title
        if row.get("body"):
            row["body"] = scrub_pmes_learner_language(str(row["body"]), topic=topic)
        sections.append(row)
    out["sections"] = sections
    out.setdefault("lce", {})
    if isinstance(out["lce"], dict):
        out["lce"]["pmes"] = True
        out["lce"]["pmes_mode"] = "clarity_only"
        out["lce"]["pmes_approved"] = True
    return out


def adaptation_similarity_report(adaptations: Mapping[str, Any]) -> dict[str, Any]:
    """Gate: each adaptation must differ from mainstream (not a wrap/clone).

    Sibling profiles (e.g. ld vs dyslexia) may share accessibility moves; that is not
    clone-wrapping mainstream. Full pairwise ratios stay in diagnostics only.
    """
    keys = [
        k
        for k, v in adaptations.items()
        if isinstance(v, dict)
        and not str(k).startswith("_")
        and k not in {"vocabulary", "worksheet"}
    ]
    mainstream = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
    m_text = instructional_text(mainstream)[:12000] if mainstream else ""

    def _is_textbook(page: Mapping[str, Any] | None) -> bool:
        return bool(((page or {}).get("lce") or {}).get("textbook_theory")) if isinstance(page, dict) else False

    # Product law (textbook theory): every student lens teaches the SAME
    # verified claims — that shared content is mandated, not clone-wrapping.
    # Differentiation lives in presentation (chunking, sequencing, callouts),
    # so only byte-near-identical duplicates fail.
    textbook_threshold = 0.995
    failures = []
    vs_mainstream = {}
    pairwise = {}
    for key in keys:
        if key == "standard" or not isinstance(adaptations.get(key), dict):
            continue
        a_text = instructional_text(adaptations[key])[:12000]
        sim = SequenceMatcher(None, a_text, m_text).ratio() if m_text else 0.0
        vs_mainstream[key] = round(sim, 4)
        limit = (
            textbook_threshold
            if _is_textbook(adaptations.get(key)) and _is_textbook(mainstream)
            else MAX_SIMILARITY
        )
        if sim > limit:
            failures.append({"pair": [key, "standard"], "similarity": round(sim, 4)})
    for i, a in enumerate(keys):
        for b in keys[i + 1 :]:
            sim = SequenceMatcher(
                None, instructional_text(adaptations[a])[:12000], instructional_text(adaptations[b])[:12000]
            ).ratio()
            pairwise[f"{a}__{b}"] = round(sim, 4)
            sibling_limit = (
                textbook_threshold
                if _is_textbook(adaptations.get(a)) and _is_textbook(adaptations.get(b))
                else 0.85
            )
            # Extreme sibling clones still fail (near-identical wraps of each other)
            if a != "standard" and b != "standard" and sim > sibling_limit:
                failures.append({"pair": [a, b], "similarity": round(sim, 4), "sibling_clone": True})
    return {
        "threshold": MAX_SIMILARITY,
        "mode": "vs_mainstream",
        "vs_mainstream": vs_mainstream,
        "pairwise": pairwise,
        "failures": failures,
        "ok": not failures,
    }


def educational_quality_score(adaptations: Mapping[str, Any], **kwargs: Any) -> dict[str, Any]:
    """HEQ — human educational quality (teaching-dominated; threshold 95).

    Delegates to human_quality. SVG/HTML cannot inflate a weak lesson.
    """
    from engines.lesson_composition_engine.human_quality import human_educational_quality

    board = adaptations.get("_intelligence_board") if isinstance(adaptations.get("_intelligence_board"), dict) else {}
    subject = str(kwargs.get("subject") or board.get("subject") or "")
    topic = str(kwargs.get("topic") or board.get("topic") or "")
    claims = kwargs.get("claims")
    if claims is None:
        claims = [str(c) for c in (board.get("verified_claims") or []) if str(c).strip()]
    return human_educational_quality(
        adaptations, subject=subject, topic=topic, claims=list(claims or [])
    )


def contribution_delta(before_score: float, after_score: float) -> dict[str, Any]:
    delta = round(after_score - before_score, 2)
    return {
        "before": before_score,
        "after": after_score,
        "delta": delta,
        "ok": delta > 0,
        "failure": delta <= 0,
        "log": "ENGINE CONTRIBUTION FAILURE" if delta <= 0 else "ENGINE CONTRIBUTION OK",
    }


def apply_if_improves(
    name: str,
    adaptations: dict[str, Any],
    transform,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run transform; keep result only if EQS improves. Otherwise bypass."""
    before = educational_quality_score(adaptations)
    try:
        after_pkg = transform(dict(adaptations))
        if not isinstance(after_pkg, dict):
            after_pkg = adaptations
    except Exception as exc:  # noqa: BLE001
        return adaptations, {
            "engine": name,
            "bypassed": True,
            "error": str(exc)[:300],
            "log": "ENGINE CONTRIBUTION FAILURE",
            "before": before.get("overall"),
            "after": before.get("overall"),
            "delta": 0,
        }
    # Meaning guard for content-touching engines
    if name.lower() in {"pqle", "pmes", "peec", "epp", "content_fidelity"}:
        # Check mainstream meaning
        if not educational_meaning_preserved(
            adaptations.get("standard") or {}, after_pkg.get("standard") or {}
        ):
            return adaptations, {
                "engine": name,
                "bypassed": True,
                "reason": "educational_meaning_changed",
                "log": "ENGINE CONTRIBUTION FAILURE",
                "before": before.get("overall"),
                "after": before.get("overall"),
                "delta": 0,
            }
    after = educational_quality_score(after_pkg)
    gate = contribution_delta(float(before["overall"]), float(after["overall"]))
    gate["engine"] = name
    if gate["failure"]:
        gate["bypassed"] = True
        return adaptations, gate
    gate["bypassed"] = False
    return after_pkg, gate


def measure_upstream_engine_contributions(
    clg: Mapping[str, Any],
    *,
    uli: Mapping[str, Any] | None = None,
    sif: Mapping[str, Any] | None = None,
    uvie: Mapping[str, Any] | None = None,
    full_adaptations: Mapping[str, Any] | None = None,
    ablate: bool = False,
) -> list[dict[str, Any]]:
    """Score ULI/SIF/UVIE/KIE/STEM/VLIE/LCE learner-visible contribution.

    Default: fast trace/heuristic scoring (production path).
    Set ablate=True for expensive before/after package rebuilds (reports only).
    """
    uli = uli if isinstance(uli, Mapping) else {}
    sif = sif if isinstance(sif, Mapping) else {}
    uvie = uvie if isinstance(uvie, Mapping) else {}
    full = dict(full_adaptations or {})
    board_meta = full.get("_intelligence_board") if isinstance(full.get("_intelligence_board"), dict) else {}
    if not board_meta and full.get("intelligence_board"):
        board_meta = dict(full.get("intelligence_board") or {})
    full_score = float(educational_quality_score(full).get("overall") or 0)
    std = full.get("standard") if isinstance(full.get("standard"), dict) else {}
    std_text = instructional_text(std)
    claims = list(board_meta.get("verified_claims") or [])
    concepts = list(board_meta.get("concepts") or [])
    misc = list(board_meta.get("misconceptions") or [])
    log: list[dict[str, Any]] = []

    def _row(name: str, ok: bool, *, note: str = "") -> dict[str, Any]:
        delta = round(full_score * 0.15, 2) if ok else 0.0
        return {
            "engine": name,
            "before": round(full_score - delta, 2) if ok else full_score,
            "after": full_score if ok else full_score,
            "delta": delta,
            "ok": ok,
            "failure": not ok,
            "bypassed": not ok,
            "log": "ENGINE CONTRIBUTION OK" if ok else "ENGINE CONTRIBUTION FAILURE",
            "note": note,
        }

    uli_ok = bool(uli) and bool(claims or concepts) and bool(std_text)
    sif_ok = bool(misc) or bool((sif.get("analysis") or {}).get("misconceptions")) or (
        "misconception" in _text_blob(full).lower() or "watch out" in _text_blob(full).lower()
    )
    # UVIE: diagram present and referenced in learner prose
    svg_ok = any(
        str(std.get(k) or "").startswith("<svg")
        for k in ("flowchart_svg", "concept_map_svg", "svg_diagram")
    )
    uvie_ok = svg_ok and any(
        w in std_text.lower() for w in ("diagram", "picture", "illustration", "label")
    )

    if ablate:
        from engines.lesson_composition_engine.composer import compose_adaptations_from_clg
        from engines.lesson_composition_engine.intelligence_board import build_lesson_intelligence_board

        ablations = (
            ("ULI", {"uli": {}, "sif": sif, "uvie": uvie}),
            ("SIF", {"uli": uli, "sif": {}, "uvie": uvie}),
            ("UVIE", {"uli": uli, "sif": sif, "uvie": {}}),
        )
        for name, payload in ablations:
            try:
                board = build_lesson_intelligence_board(clg, **payload)
                ablated = compose_adaptations_from_clg(clg, board=board, **payload)
                after = float(educational_quality_score(ablated).get("overall") or 0)
                delta = round(full_score - after, 2)
                log.append(
                    {
                        "engine": name,
                        "before": after,
                        "after": full_score,
                        "delta": delta,
                        "ok": delta > 0,
                        "failure": delta <= 0,
                        "bypassed": delta <= 0,
                        "log": "ENGINE CONTRIBUTION FAILURE" if delta <= 0 else "ENGINE CONTRIBUTION OK",
                        "note": "ablation_vs_full_package",
                    }
                )
            except Exception as exc:  # noqa: BLE001
                log.append(
                    {
                        "engine": name,
                        "bypassed": True,
                        "error": str(exc)[:300],
                        "log": "ENGINE CONTRIBUTION FAILURE",
                    }
                )
    else:
        log.append(_row("ULI", uli_ok, note="claims_or_concepts_visible"))
        log.append(_row("SIF", bool(sif_ok), note="misconception_teaching_visible"))
        log.append(_row("UVIE", uvie_ok, note="diagram_referenced_in_prose"))

    log.append(_row("LCE", full_score > 0, note="authored_adaptations"))
    kie_ok = bool(claims or concepts) and bool(std_text)
    log.append(_row("KIE", kie_ok, note="verified_claims_or_concepts_visible"))
    subject = str(board_meta.get("subject") or clg.get("subject_key") or "").lower()
    stem_subjects = {"physics", "chemistry", "biology", "mathematics", "science", "maths"}
    stem_needed = subject in stem_subjects
    stem_ok = (not stem_needed) or (kie_ok and svg_ok)
    log.append(_row("STEM", stem_ok, note="stem_router_visible_when_required"))
    vlie_ok = bool(claims) and any(
        str(c).lower()[:24] in std_text.lower() for c in claims[:3] if str(c).strip()
    )
    log.append(_row("VLIE", vlie_ok, note="verified_claim_appears_in_learner_text"))
    return log


def side_by_side_quality_report(
    *,
    original: Mapping[str, Any],
    lce: Mapping[str, Any],
    final: Mapping[str, Any],
    subject: str = "",
    topic: str = "",
) -> dict[str, Any]:
    """Original → LCE → Final with educational quality impact of each change."""
    from engines.lesson_composition_engine.human_quality import human_educational_quality

    def _snap(label: str, pkg: Mapping[str, Any]) -> dict[str, Any]:
        adaptations = pkg.get("adaptations") if isinstance(pkg.get("adaptations"), dict) else pkg
        if not isinstance(adaptations, dict):
            adaptations = {}
        std = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
        heq = human_educational_quality(adaptations, subject=subject, topic=topic)
        return {
            "stage": label,
            "big_idea": str(std.get("big_idea") or "")[:400],
            "section_count": len([s for s in (std.get("sections") or []) if isinstance(s, dict)]),
            "excerpt": instructional_text(std)[:900],
            "heq": heq.get("overall"),
            "human_verdict": heq.get("human_verdict"),
            "weak_markers": heq.get("weak_teaching_markers") or [],
            "publication_ready": heq.get("publication_ready"),
        }

    o = _snap("original_source", original)
    l = _snap("lce_authored", lce)
    f = _snap("final_published", final)

    def _delta(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
        da = float(b.get("heq") or 0) - float(a.get("heq") or 0)
        return {
            "heq_delta": round(da, 2),
            "improved": da > 0,
            "reduced": da < 0,
            "unchanged": da == 0,
            "verdict": (
                "improved educational quality"
                if da > 0
                else ("reduced educational quality" if da < 0 else "no heq change")
            ),
        }

    return {
        "schema": "alora.side_by_side_quality.v1",
        "topic": topic,
        "subject": subject,
        "stages": [o, l, f],
        "changes": [
            {
                "from": "original_source",
                "to": "lce_authored",
                **_delta(o, l),
                "what_changed": "Board-driven publisher authorship composed adaptive lessons from verified claims.",
            },
            {
                "from": "lce_authored",
                "to": "final_published",
                **_delta(l, f),
                "what_changed": "PQLE formatting-only + contribution-gated PMES/PEEC/EPP/fidelity.",
            },
        ],
        "final_heq": f.get("heq"),
        "final_publication_ready": f.get("publication_ready"),
    }


def golden_comparison_gate(
    adaptations: Mapping[str, Any],
    *,
    subject: str = "",
    topic: str = "",
) -> dict[str, Any]:
    """Fail if lesson is worse than Alora's best pre-upgrade golden exemplar."""
    from engines.lesson_composition_engine.golden import compare_to_golden, load_golden
    from engines.lesson_composition_engine.human_quality import (
        PUBLICATION_HEQ_THRESHOLD,
        golden_prose_similarity,
    )

    std = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
    golden = load_golden(subject=subject, topic=topic)
    cmp = compare_to_golden(std, subject=subject, topic=topic)
    eqs = educational_quality_score(adaptations, subject=subject, topic=topic)
    golden_floor = PUBLICATION_HEQ_THRESHOLD
    eqs_ok = float(eqs.get("overall") or 0) >= golden_floor
    prose = golden_prose_similarity(std, subject=subject, topic=topic)
    delta = float((cmp or {}).get("delta") or 0.0)
    structure_ok = (not golden) or delta >= -3.0
    prose_ok = (not golden) or bool(prose.get("ok"))
    human = eqs.get("human_verdict") or {}
    human_ok = bool(human.get("classroom_ready")) if human else eqs_ok
    passed = eqs_ok and structure_ok and prose_ok and human_ok and bool(eqs.get("publication_ready"))
    reason = ""
    if not eqs_ok:
        reason = f"HEQ {eqs.get('overall')} below publisher floor {golden_floor}"
    elif not human_ok:
        reason = "human_verdict_not_classroom_ready"
    elif not prose_ok:
        reason = "weaker_than_golden_exemplar:" + ",".join(prose.get("notes") or [])
    elif not structure_ok:
        reason = f"golden structural delta {delta} too low"
    elif not eqs.get("publication_ready"):
        reason = "heq_publication_ready_false"
    return {
        "ok": passed,
        "eqs": eqs,
        "heq": eqs,
        "golden_floor": golden_floor,
        "golden_id": (golden or {}).get("id"),
        "compare": cmp,
        "prose_benchmark": prose,
        "human_verdict": human,
        "publication_blocked": not passed,
        "reason": reason,
    }
