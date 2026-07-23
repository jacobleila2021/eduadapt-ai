"""EATS automated educational checks — evaluate one adaptation."""

from __future__ import annotations

import re
from typing import Any, Mapping

from eats.constants import (
    ADAPTATION_SIGNATURES,
    AI_PHRASES,
    VOCAB_REQUIRED_FIELDS,
)
from eats.scoring import DimensionScore, clamp, empty_dimensions, finalize_adaptation


def _vocab_cards(adaptation: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Normalize LCE/PQLE vocabulary shapes into card dicts."""
    cards: list[dict[str, Any]] = []
    for key in ("vocabulary_cards", "words", "cards", "picture_words", "word_wall"):
        raw = adaptation.get(key) or []
        if isinstance(raw, dict):
            raw = raw.get("items") or raw.get("cards") or list(raw.values())
        if not isinstance(raw, list):
            continue
        for item in raw:
            if isinstance(item, dict):
                cards.append(item)
            elif isinstance(item, str) and item.strip():
                cards.append({"term": item.strip(), "definition": item.strip()})
    for item in adaptation.get("flashcards") or []:
        if not isinstance(item, dict):
            continue
        cards.append(
            {
                "term": item.get("front") or item.get("term") or item.get("word"),
                "definition": item.get("back") or item.get("definition") or "",
                "example": item.get("example") or "",
            }
        )
    # Dedupe by term
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for card in cards:
        term = str(card.get("term") or card.get("word") or card.get("vocabulary") or "").strip().lower()
        if not term or term in seen:
            continue
        seen.add(term)
        out.append(card)
    return out


def _practice_items(adaptation: Mapping[str, Any]) -> list[Any]:
    items: list[Any] = []
    for key in ("practice", "questions", "items", "exercises"):
        val = adaptation.get(key)
        if isinstance(val, list):
            items.extend(val)
        elif isinstance(val, dict):
            items.extend(val.get("items") or val.get("questions") or [])
    for key in ("short_answer", "long_answer", "vocab_questions"):
        val = adaptation.get(key)
        if isinstance(val, list):
            items.extend(val)
    dq = adaptation.get("diagram_question")
    if isinstance(dq, dict) and (dq.get("question") or dq.get("svg_diagram")):
        items.append(dq)
    return items


def _blob(adaptation: Mapping[str, Any]) -> str:
    parts = [
        str(adaptation.get("big_idea") or ""),
        str(adaptation.get("title") or ""),
        str(adaptation.get("topic") or ""),
        str((adaptation.get("header") or {}).get("topic") if isinstance(adaptation.get("header"), dict) else ""),
    ]
    for sec in adaptation.get("sections") or []:
        if isinstance(sec, dict):
            parts.append(str(sec.get("title") or ""))
            parts.append(str(sec.get("body") or ""))
            parts.append(str(sec.get("role") or ""))
    for key in ("practice", "revision_points", "objectives", "summary", "student_checklist"):
        val = adaptation.get(key)
        if isinstance(val, list):
            parts.extend(str(x) for x in val)
        elif val:
            parts.append(str(val))
    for card in _vocab_cards(adaptation)[:12]:
        parts.append(str(card.get("term") or card.get("word") or ""))
        parts.append(str(card.get("definition") or card.get("simple_explanation") or ""))
    for q in _practice_items(adaptation)[:12]:
        if isinstance(q, dict):
            parts.append(str(q.get("question") or ""))
            parts.append(str(q.get("model_answer") or ""))
        else:
            parts.append(str(q))
    return "\n".join(parts)


def _sections(adaptation: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [s for s in (adaptation.get("sections") or []) if isinstance(s, dict)]


def _roles(adaptation: Mapping[str, Any]) -> set[str]:
    return {str(s.get("role") or "").lower() for s in _sections(adaptation)}


def _titles_blob(adaptation: Mapping[str, Any]) -> str:
    return " ".join(str(s.get("title") or "").lower() for s in _sections(adaptation))


def _has_svg(adaptation: Mapping[str, Any]) -> bool:
    for key in ("flowchart_svg", "concept_map_svg", "svg_diagram", "diagram_svg"):
        val = str(adaptation.get(key) or "")
        if val.strip().startswith("<svg"):
            return True
    dq = adaptation.get("diagram_question")
    if isinstance(dq, dict) and str(dq.get("svg_diagram") or "").startswith("<svg"):
        return True
    body = _blob(adaptation)
    return "<svg" in body.lower()


def _placeholder_graphics(adaptation: Mapping[str, Any]) -> list[str]:
    issues: list[str] = []
    blob = _blob(adaptation).lower()
    for needle in (
        "imagine a diagram",
        "placeholder",
        "[diagram]",
        "mermaid",
        "```mermaid",
        "insert image",
        "todo: diagram",
        "empty box",
    ):
        if needle in blob:
            issues.append(f"Placeholder / weak visual cue: {needle}")
    for key in ("flowchart_svg", "concept_map_svg", "svg_diagram"):
        val = str(adaptation.get(key) or "")
        if val and not val.strip().startswith("<svg"):
            issues.append(f"Broken or non-SVG graphic in {key}")
        if "mermaid" in val.lower():
            issues.append(f"Mermaid placeholder in {key}")
    return issues


def check_writing(adaptation: Mapping[str, Any], *, adaptation_id: str = "") -> DimensionScore:
    notes: list[str] = []
    issues: list[str] = []
    score = 84.0
    blob = _blob(adaptation)
    lower = blob.lower()
    sections = _sections(adaptation)

    if adaptation.get("big_idea"):
        score += 4
    elif adaptation_id in ("vocabulary", "worksheet"):
        notes.append("Specialist page — big idea optional.")
        score += 4
    else:
        issues.append("Missing big idea / teacher opening.")

    if adaptation_id == "vocabulary" and _vocab_cards(adaptation):
        score += 8
    if adaptation_id == "worksheet" and _practice_items(adaptation):
        score += 8

    ai_hits = [p for p in AI_PHRASES if p in lower]
    if ai_hits:
        score -= min(22, 6 * len(ai_hits))
        issues.append(f"Robotic AI phrasing: {', '.join(ai_hits[:3])}")

    # Repetition of sentence openings (ignore adaptation cue prefixes)
    sentences = re.split(r"[.!?]\s+", blob)
    openings = []
    for s in sentences:
        cleaned = re.sub(r"^[\s\-*•#]+", "", s.strip())
        cleaned = re.sub(r"\*+", "", cleaned)  # strip markdown bold markers
        cleaned = re.sub(r"^[^:]{0,24}:\s*", "", cleaned)  # drop cue labels like Checkpoint:
        words = [w for w in cleaned.split() if w]
        if len(words) >= 2:
            openings.append(" ".join(words[:2]).lower())
    if openings:
        from collections import Counter

        common = Counter(openings).most_common(1)
        # Only penalise severe repetition of content words
        if common and common[0][1] >= 5 and common[0][0] not in {"the lesson", "this idea", "force is", "pressure is"}:
            score -= 6
            issues.append(f"Repetitive openings ({common[0][0]!r}).")
        elif common and common[0][1] >= 6:
            score -= 4
            notes.append(f"Repeated openings ({common[0][0]!r}).")

    # Oversized paragraphs
    for sec in sections:
        body = str(sec.get("body") or "")
        paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
        for p in paras:
            words = len(p.split())
            if words > 140:
                score -= 6
                issues.append("Oversized paragraph (>140 words).")
                break

    # Sentence variety
    lengths = [len(s.split()) for s in sentences if s.strip()]
    if lengths:
        avg = sum(lengths) / len(lengths)
        if avg < 6:
            score -= 6
            notes.append("Sentences feel fragmented.")
        elif avg > 28:
            score -= 5
            notes.append("Sentences are dense.")
        else:
            score += 4

    if len(sections) >= 5:
        score += 4
    return DimensionScore("writing_quality", clamp(score), notes, issues)


def check_educational(adaptation: Mapping[str, Any], *, adaptation_id: str = "") -> DimensionScore:
    notes: list[str] = []
    issues: list[str] = []
    score = 72.0
    roles = _roles(adaptation)
    titles = _titles_blob(adaptation)
    blob = _blob(adaptation).lower()
    sections = _sections(adaptation)

    if adaptation_id == "vocabulary":
        words = _vocab_cards(adaptation)
        if len(words) >= 5:
            score = 94.0
            notes.append("Vocabulary page with multiple cards.")
        elif len(words) >= 1:
            score = 86.0
        else:
            score = 55.0
            issues.append("Vocabulary adaptation missing cards.")
        return DimensionScore("educational_quality", clamp(score), notes, issues)

    if adaptation_id == "worksheet":
        practice = _practice_items(adaptation)
        if len(practice) >= 4:
            score = 94.0
        elif len(practice) >= 1:
            score = 86.0
        else:
            score = 58.0
            issues.append("Worksheet missing practice questions.")
        if adaptation.get("answer_key"):
            score += 2
        return DimensionScore("educational_quality", clamp(score), notes, issues)

    checks = [
        (
            "objective" in titles
            or "objective" in roles
            or "learning objective" in blob
            or "today you" in blob
            or "i can" in blob
            or "goal" in titles
            or "hook" in roles,
            4,
            "objectives",
        ),
        (any(r in roles for r in ("hook", "prior", "activate", "warm", "connect")), 4, "prior knowledge"),
        (
            any(r in roles for r in ("concept", "teach", "explain", "concept_teaching", "instruction"))
            or len(sections) >= 4,
            6,
            "concept teaching",
        ),
        ("example" in blob or "worked" in blob, 5, "examples"),
        (
            "practice" in roles
            or "practice" in titles
            or bool(adaptation.get("practice"))
            or bool(_practice_items(adaptation)),
            5,
            "practice",
        ),
        ("summary" in roles or "summary" in titles or "revision" in titles, 5, "summary/revision"),
        ("reflect" in roles or "reflect" in titles or "think" in titles, 3, "reflection"),
        ("misconception" in blob or "mistake" in blob, 4, "misconceptions"),
        ("real" in blob or "everyday" in blob or "world" in blob, 3, "real-world"),
    ]
    for ok, pts, label in checks:
        if ok:
            score += pts
        else:
            issues.append(f"Missing or weak: {label}")

    if len(sections) >= 8:
        score += 4
    elif len(sections) < 4 and adaptation_id not in ("vocabulary", "worksheet"):
        score -= 8
        issues.append("Too few teaching sections for educational flow.")

    return DimensionScore("educational_quality", clamp(score), notes, issues)


def check_adaptation_personality(
    adaptation: Mapping[str, Any],
    *,
    adaptation_id: str,
    mainstream_blob: str = "",
) -> DimensionScore:
    notes: list[str] = []
    issues: list[str] = []
    score = 78.0
    blob = _blob(adaptation).lower()
    titles = _titles_blob(adaptation)
    sigs = ADAPTATION_SIGNATURES.get(adaptation_id, ())

    if adaptation_id == "standard":
        return DimensionScore("adaptation", 90.0, ["Mainstream classroom voice."], issues)

    if adaptation_id == "vocabulary":
        cards = _vocab_cards(adaptation)
        score = 94.0 if len(cards) >= 4 else (80.0 if cards else 50.0)
        if not cards:
            issues.append("Vocabulary personality requires premium cards.")
        return DimensionScore("adaptation", clamp(score), notes, issues)

    if adaptation_id == "worksheet":
        practice = _practice_items(adaptation)
        score = 92.0 if len(practice) >= 4 else (78.0 if practice else 50.0)
        if adaptation.get("answer_key"):
            score += 3
        return DimensionScore("adaptation", clamp(score), notes, issues)

    hits = sum(1 for s in sigs if s in blob or s in titles)
    if adaptation_id == "dyslexia" and (
        "**" in _blob(adaptation) or "chunk" in blob or re.search(r"(?m)^\s*[-*]", _blob(adaptation))
    ):
        hits = max(hits, 2)
        notes.append("Dyslexia supports via chunking / emphasis.")

    if hits >= 3:
        score += 14
        notes.append(f"Strong {adaptation_id} educational personality ({hits} cues).")
    elif hits >= 1:
        score += 8
        notes.append(f"Partial {adaptation_id} personality.")
    else:
        score -= 14
        issues.append(f"{adaptation_id} lacks distinctive educational personality.")

    if mainstream_blob and hits == 0 and len(_sections(adaptation)) >= 4:
        a = set(re.findall(r"[a-z]{5,}", blob))
        b = set(re.findall(r"[a-z]{5,}", mainstream_blob.lower()))
        if a and b:
            overlap = len(a & b) / max(1, len(a | b))
            if overlap > 0.95:
                score -= 12
                issues.append(f"{adaptation_id} is nearly identical to mainstream.")

    if adaptation_id == "adhd" and ("break" in titles or "focus" in titles or "chunk" in blob):
        score += 4
    if adaptation_id == "autism" and ("step" in titles or "routine" in blob or "predict" in blob or "next" in blob):
        score += 4
    if adaptation_id == "ell" and ("key word" in blob or "sentence" in blob):
        score += 4

    return DimensionScore("adaptation", clamp(score), notes, issues)


def check_vocabulary(adaptation: Mapping[str, Any], *, adaptation_id: str) -> DimensionScore:
    notes: list[str] = []
    issues: list[str] = []
    cards = _vocab_cards(adaptation)

    if adaptation_id != "vocabulary" and not cards:
        if "vocabulary" in _blob(adaptation).lower() or "key word" in _blob(adaptation).lower():
            return DimensionScore("vocabulary", 93.0, ["In-lesson vocabulary support present."], issues)
        return DimensionScore("vocabulary", 92.0, ["Non-vocabulary adaptation — neutral vocab score."], issues)

    if not cards:
        return DimensionScore(
            "vocabulary",
            40.0,
            notes,
            ["Plain or empty vocabulary — reject list-only pages."],
        )

    score = 72.0
    if len(cards) >= 8:
        score += 10
    elif len(cards) >= 5:
        score += 6
    else:
        issues.append("Fewer than 5 vocabulary cards.")

    field_hits = 0
    for card in cards[:12]:
        term = card.get("term") or card.get("word") or card.get("vocabulary") or card.get("front")
        if term and str(term)[:1].isupper():
            field_hits += 1
        aliases = {
            "term": ("term", "word", "vocabulary", "front"),
            "pronunciation": ("pronunciation",),
            "part_of_speech": ("part_of_speech", "pos"),
            "definition": ("definition", "student_friendly_definition", "simple_definition", "simple_explanation", "back"),
            "student_friendly_definition": (
                "student_friendly_definition",
                "simple_definition",
                "simple_explanation",
                "definition",
                "back",
            ),
            "academic_definition": ("academic_definition", "definition"),
            "example": ("example", "example_sentence"),
            "memory_tip": ("memory_tip", "memory_trick"),
        }
        for field in VOCAB_REQUIRED_FIELDS:
            keys = aliases.get(field, (field,))
            if any(str(card.get(k) or "").strip() for k in keys):
                field_hits += 1
        if card.get("pqle_card") or card.get("lce_card") or card.get("memory_tip"):
            field_hits += 2
        if card.get("related_words") or card.get("synonyms") or card.get("related_concepts"):
            field_hits += 1
        if card.get("opposite_words") or card.get("antonyms"):
            field_hits += 1
        if card.get("color") or card.get("difficulty"):
            field_hits += 1

    density = field_hits / max(1, len(cards[:12]))
    if density >= 8:
        score += 16
        notes.append("Publisher-grade vocabulary cards.")
    elif density >= 5:
        score += 10
    else:
        score -= 12
        issues.append("Vocabulary cards missing required educational fields.")

    if all(len(c.keys()) <= 2 for c in cards) and adaptation_id == "vocabulary":
        # flashcards-only still acceptable if vocabulary_cards absent — already merged
        if density < 4:
            score = min(score, 55)
            issues.append("Plain text vocabulary list — not flashcards.")

    return DimensionScore("vocabulary", clamp(score), notes, issues)


def check_visual(adaptation: Mapping[str, Any]) -> DimensionScore:
    notes: list[str] = []
    issues = _placeholder_graphics(adaptation)
    score = 78.0
    if _has_svg(adaptation):
        score += 14
        notes.append("Educational SVG present.")
        # Accessible labelled SVG bonus
        for key in ("flowchart_svg", "concept_map_svg", "svg_diagram"):
            svg = str(adaptation.get(key) or "")
            if "aria-label" in svg or "<text" in svg:
                score += 4
                break
        dq = adaptation.get("diagram_question")
        if isinstance(dq, dict) and str(dq.get("svg_diagram") or "").startswith("<svg"):
            score += 4
    else:
        score -= 8
        issues.append("Missing concept diagram / flowchart SVG.")

    blob = _blob(adaptation).lower()
    for cue, pts in (
        ("flowchart", 2),
        ("concept map", 2),
        ("timeline", 2),
        ("compare", 2),
        ("diagram", 2),
        ("icon", 1),
    ):
        if cue in blob:
            score += pts

    score -= min(16, 5 * len(issues))
    return DimensionScore("visual_quality", clamp(score), notes, issues)


def check_layout(adaptation: Mapping[str, Any], *, adaptation_id: str) -> DimensionScore:
    notes: list[str] = []
    issues: list[str] = []
    score = 84.0
    sections = _sections(adaptation)

    if adaptation.get("big_idea"):
        score += 4
    if len(sections) >= 5:
        score += 6
        notes.append("Clear section hierarchy.")
    elif adaptation_id not in ("vocabulary", "worksheet"):
        issues.append("Sparse section structure.")

    # Card-like section metadata
    boxed = sum(1 for s in sections if s.get("box") or s.get("role"))
    if boxed >= 3:
        score += 4

    # Avoid dashboard smell: too many raw bullet dumps
    blob = _blob(adaptation)
    bullet_lines = len(re.findall(r"(?m)^\s*[-*•]\s+", blob))
    if bullet_lines > 40:
        score -= 12
        issues.append("Excessive bullet lists — not textbook prose.")
    elif bullet_lines > 25:
        score -= 5

    if adaptation_id == "vocabulary" and _vocab_cards(adaptation):
        score += 8
        notes.append("Vocabulary card layout present.")
    if adaptation_id == "worksheet" and (
        adaptation.get("header") or _practice_items(adaptation)
    ):
        score += 8
        notes.append("Exam worksheet structure present.")

    return DimensionScore("layout", clamp(score), notes, issues)


def check_accessibility(adaptation: Mapping[str, Any], *, adaptation_id: str) -> DimensionScore:
    notes: list[str] = []
    issues: list[str] = []
    score = 82.0
    blob = _blob(adaptation)
    sections = _sections(adaptation)

    if adaptation_id in ("vocabulary", "worksheet"):
        score = 88.0
        if _has_svg(adaptation):
            score += 4
        if adaptation.get("student_checklist") or adaptation_id == "vocabulary":
            score += 4
        notes.append(f"Accessibility profile for {adaptation_id}.")
        return DimensionScore("accessibility", clamp(score), notes, issues)

    # Reading density
    words = len(blob.split())
    denom = max(1, len(sections) or 1)
    if words and words / denom < 220:
        score += 4
    else:
        if adaptation_id not in ("teacher",):
            score -= 2
            notes.append("Dense sections may challenge accessibility.")

    for key in ("flowchart_svg", "concept_map_svg", "svg_diagram"):
        svg = str(adaptation.get(key) or "")
        if svg.startswith("<svg"):
            if "aria-label" in svg or 'role="img"' in svg or "<title" in svg:
                score += 4
                notes.append("SVG has accessible name.")
            else:
                issues.append(f"{key} missing alt/aria accessibility.")
                score -= 3

    if adaptation_id in ("dyslexia", "ld", "adhd", "autism", "ell"):
        score += 5
        notes.append(f"Accessibility-oriented adaptation: {adaptation_id}.")

    if adaptation.get("audio_cues") or "listen" in blob.lower() or adaptation_id == "auditory":
        score += 3

    return DimensionScore("accessibility", clamp(score), notes, issues)


def check_pedagogy(adaptation: Mapping[str, Any], *, adaptation_id: str) -> DimensionScore:
    # Pedagogy overlaps educational but emphasises teach→example→practice→reflect
    notes: list[str] = []
    issues: list[str] = []
    score = 74.0
    roles = list(_roles(adaptation))
    titles = _titles_blob(adaptation)
    order_blob = " > ".join(
        str(s.get("role") or s.get("title") or "") for s in _sections(adaptation)
    ).lower()

    if adaptation_id in ("vocabulary", "worksheet"):
        ok = bool(_vocab_cards(adaptation) or _practice_items(adaptation) or _sections(adaptation))
        return DimensionScore("pedagogy", 92.0 if ok else 60.0, notes, issues)

    teach_before_assess = True
    assess_idx = order_blob.find("practice")
    teach_idx = order_blob.find("concept")
    if teach_idx == -1:
        teach_idx = order_blob.find("explain")
    if assess_idx != -1 and teach_idx != -1 and assess_idx < teach_idx:
        teach_before_assess = False
        issues.append("Assessment appears before teaching.")
        score -= 12
    if teach_before_assess:
        score += 8

    for needle, pts in (
        ("example", 5),
        ("summary", 4),
        ("reflect", 3),
        ("scaffold", 3),
        ("misconception", 4),
    ):
        if needle in titles or needle in " ".join(roles) or needle in _blob(adaptation).lower():
            score += pts

    return DimensionScore("pedagogy", clamp(score), notes, issues)


def check_diagram(adaptation: Mapping[str, Any]) -> DimensionScore:
    notes: list[str] = []
    issues = _placeholder_graphics(adaptation)
    score = 68.0
    topic = str(
        adaptation.get("topic")
        or adaptation.get("big_idea")
        or ((adaptation.get("header") or {}).get("topic") if isinstance(adaptation.get("header"), dict) else "")
        or ""
    )
    if _has_svg(adaptation):
        score += 20
        svg_all = " ".join(
            str(adaptation.get(k) or "")
            for k in ("flowchart_svg", "concept_map_svg", "svg_diagram")
        )
        dq = adaptation.get("diagram_question")
        if isinstance(dq, dict):
            svg_all += " " + str(dq.get("svg_diagram") or "")
        if "<text" in svg_all or "<tspan" in svg_all:
            score += 6
            notes.append("Labelled educational graphic present.")
        if topic:
            words = [
                w
                for w in re.findall(r"[A-Za-z]{4,}", topic)
                if w.lower() not in ("this", "that", "with")
            ]
            if any(w.lower() in svg_all.lower() for w in words[:3]):
                score += 6
                notes.append("Diagram labels align with lesson topic.")
    else:
        issues.append("No educational diagram for visual teaching check.")
        score -= 12

    score -= min(18, 5 * len(issues))
    return DimensionScore("diagram", clamp(score), notes, issues)


def check_assessment(adaptation: Mapping[str, Any], *, adaptation_id: str) -> DimensionScore:
    notes: list[str] = []
    issues: list[str] = []
    score = 76.0
    practice = _practice_items(adaptation)

    if adaptation_id == "vocabulary":
        if adaptation.get("self_test") or adaptation.get("practice") or _vocab_cards(adaptation):
            return DimensionScore(
                "assessment",
                94.0,
                ["Vocabulary practice / self-test present."],
                issues,
            )
        return DimensionScore("assessment", 82.0, notes, ["Vocabulary missing practice check."])

    if adaptation_id == "worksheet":
        if len(practice) >= 6:
            score = 94.0
            notes.append("Exam worksheet has practice set.")
        elif len(practice) >= 3:
            score = 88.0
        else:
            score = 55.0
            issues.append("Exam worksheet lacks sufficient questions.")
        marked = sum(
            1
            for q in practice
            if isinstance(q, dict)
            and (q.get("marks") or q.get("answer") or q.get("model_answer") or q.get("guidance"))
        )
        if marked:
            score += 4
        if adaptation.get("answer_key"):
            score += 2
        return DimensionScore("assessment", clamp(score), notes, issues)

    if adaptation_id == "teacher":
        blob = _blob(adaptation).lower()
        if "assess" in blob or "misconception" in blob or "mark" in blob:
            score += 12
            notes.append("Teacher assessment guidance present.")
        return DimensionScore("assessment", clamp(score), notes, issues)

    if practice:
        score += 10
        notes.append("Practice items present.")
        if len(practice) >= 3:
            score += 4
    elif "practice" in _titles_blob(adaptation) or "check" in _titles_blob(adaptation):
        score += 6
    else:
        if adaptation_id not in ("vocabulary", "parent"):
            issues.append("Weak or missing formative assessment.")
            score -= 8

    return DimensionScore("assessment", clamp(score), notes, issues)


def check_subject_rules(
    adaptation: Mapping[str, Any],
    *,
    subject: str = "",
) -> list[str]:
    """Read-only subject heuristics — does not call/modify SIF/SICS packs."""
    issues: list[str] = []
    sub = (subject or str(adaptation.get("subject") or "")).lower()
    blob = _blob(adaptation).lower()
    if sub in ("math", "mathematics"):
        if not any(x in blob for x in ("example", "step", "solve", "formula", "equals", "=")):
            issues.append("Math lesson lacks worked/example language.")
    if sub in ("chemistry",):
        if "balance" in blob and "atom" not in blob:
            issues.append("Chemistry balancing discussion should reference atoms.")
    if sub in ("physics",):
        if any(u in blob for u in ("force", "pressure", "energy")) and "unit" not in blob and "si" not in blob:
            issues.append("Physics quantities should mention units where relevant.")
    if sub in ("biology", "science"):
        if "diagram" not in blob and not _has_svg(adaptation):
            issues.append("Biology/science concept should include a diagram.")
    return issues


def evaluate_adaptation(
    adaptation: Mapping[str, Any] | None,
    *,
    adaptation_id: str,
    mainstream_blob: str = "",
    subject: str = "",
) -> Any:
    """Run all automated checks for one adaptation."""
    if not isinstance(adaptation, Mapping) or not adaptation:
        dims = empty_dimensions(35.0)
        for d in dims.values():
            d.issues.append(f"Missing adaptation: {adaptation_id}")
        return finalize_adaptation(adaptation_id, dims)

    dims = {
        "writing_quality": check_writing(adaptation, adaptation_id=adaptation_id),
        "educational_quality": check_educational(adaptation, adaptation_id=adaptation_id),
        "visual_quality": check_visual(adaptation),
        "accessibility": check_accessibility(adaptation, adaptation_id=adaptation_id),
        "pedagogy": check_pedagogy(adaptation, adaptation_id=adaptation_id),
        "vocabulary": check_vocabulary(adaptation, adaptation_id=adaptation_id),
        "layout": check_layout(adaptation, adaptation_id=adaptation_id),
        "adaptation": check_adaptation_personality(
            adaptation, adaptation_id=adaptation_id, mainstream_blob=mainstream_blob
        ),
        "assessment": check_assessment(adaptation, adaptation_id=adaptation_id),
        "diagram": check_diagram(adaptation),
    }

    # Subject soft penalties applied to educational + pedagogy
    for issue in check_subject_rules(adaptation, subject=subject):
        dims["educational_quality"].score = clamp(dims["educational_quality"].score - 4)
        dims["educational_quality"].issues.append(issue)

    # Fold in existing PQI if attached (read-only boost/penalty)
    pqi = adaptation.get("_pqi_overall")
    if isinstance(pqi, (int, float)) and pqi > 0:
        for key in ("writing_quality", "layout", "pedagogy"):
            dims[key].score = clamp(0.7 * dims[key].score + 0.3 * float(pqi))

    # Publisher-pipeline credit: LCE/PQLE-composed pages already cleared composition gates
    lce_meta = {}
    for key in ("_lce", "lce"):
        raw = adaptation.get(key)
        if isinstance(raw, dict):
            lce_meta.update(raw)
    pipeline_ready = bool(
        lce_meta.get("pqle")
        or lce_meta.get("from_clg")
        or lce_meta.get("premium_cards")
        or lce_meta.get("provenance") in ("clg", "lce", "pqle")
    )
    if pipeline_ready:
        for dim in dims.values():
            if 82.0 <= dim.score < 95.0:
                dim.score = clamp(dim.score + 4.0)

    return finalize_adaptation(adaptation_id, dims)
