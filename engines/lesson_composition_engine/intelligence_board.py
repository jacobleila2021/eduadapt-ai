"""Lesson Intelligence Board — gather verified teaching intelligence before writing.

Phase Omega: LCE must not author paragraphs until this board exists.
Not a new engine — composition prep inside LCE.
"""

from __future__ import annotations

from typing import Any, Mapping

PHASE_OMEGA_PREMIUM_EDUCATIONAL_EXPERIENCE_SMOKE_OK = True
BOARD_VERSION = "1.0.0"


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _texts(items: list[Any], *keys: str) -> list[str]:
    out: list[str] = []
    for item in items:
        if isinstance(item, dict):
            for key in keys:
                text = str(item.get(key) or "").strip()
                if text:
                    out.append(text)
                    break
        else:
            text = str(item or "").strip()
            if text:
                out.append(text)
    return out


def _dedupe(items: list[str], *, limit: int = 24) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = item.lower().strip()
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(item.strip())
        if len(out) >= limit:
            break
    return out


def build_lesson_intelligence_board(
    clg: Mapping[str, Any] | None = None,
    *,
    uli: Mapping[str, Any] | None = None,
    sif: Mapping[str, Any] | None = None,
    uvie: Mapping[str, Any] | None = None,
    meta: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble the Lesson Intelligence Board from existing pipeline artefacts."""
    from engines.lesson_composition_engine.publisher_remediation import (
        has_teacher_objective_leak,
        studentize_goal,
        template_hits,
    )
    from engines.lesson_composition_engine.vocab_quality import clean_topic, is_junk_term

    clg = dict(clg or {})
    uli = dict(uli or {})
    sif = dict(sif or {})
    uvie = dict(uvie or {})
    meta = dict(meta or {})
    profile = dict(uli.get("universal_profile") or meta.get("universal_profile") or {})

    topic = clean_topic(
        str(clg.get("topic") or profile.get("topic") or meta.get("topic") or "Lesson"),
        fallback="Lesson",
    )
    subject = str(clg.get("subject_key") or sif.get("subject_key") or profile.get("subject") or "general")

    claim_texts = _dedupe(
        _texts(list(clg.get("facts") or []), "text")
        + _texts(list(clg.get("claim_texts") or []))
        + _texts(list(profile.get("claim_ledger") or []), "text", "claim")
    )
    claim_texts = [c for c in claim_texts if not has_teacher_objective_leak(c) and not template_hits(c)]

    concepts_raw = list(clg.get("core_concepts") or profile.get("concepts") or [])
    concepts: list[dict[str, Any]] = []
    for item in concepts_raw:
        if isinstance(item, dict):
            name = str(item.get("name") or item.get("title") or "").strip()
            if name and not is_junk_term(name):
                concepts.append(
                    {
                        "name": name,
                        "explanation": str(item.get("explanation") or item.get("definition") or "").strip(),
                    }
                )
        else:
            name = str(item or "").strip()
            if name and not is_junk_term(name):
                concepts.append({"name": name, "explanation": ""})

    misconceptions: list[dict[str, str]] = []
    for item in list(clg.get("misconceptions") or []) + list(
        (sif.get("analysis") or {}).get("misconceptions") or []
    ):
        if isinstance(item, dict):
            label = str(item.get("label") or item.get("misconception") or "").strip()
            correction = str(item.get("correction") or item.get("remedy") or "").strip()
        else:
            label = str(item or "").strip()
            correction = ""
        if label:
            misconceptions.append({"label": label, "correction": correction})

    goals = _texts(list(clg.get("learning_goals") or []), "text") or _texts(
        list(profile.get("learning_objectives") or [])
    )
    goals = [studentize_goal(g, topic=topic) for g in goals if g]

    vocabulary = _dedupe(
        _texts(list(clg.get("vocabulary") or []), "term", "word")
        + _texts(list(profile.get("vocabulary") or []), "term", "word")
        + [c["name"] for c in concepts]
    )

    examples = _dedupe(
        _texts(list(clg.get("examples") or []), "text", "example")
        + _texts(list(profile.get("examples") or []), "text")
        + claim_texts[1:6]
    )

    assessments = _dedupe(
        _texts(list(clg.get("assessment_outcomes") or []), "prompt", "name", "text")
        + _texts(list((sif.get("analysis") or {}).get("assessment_hints") or []), "prompt", "text")
    )

    visuals = []
    for item in list(clg.get("visual_refs") or []) + list(uvie.get("preferred_visuals") or meta.get("preferred_visuals") or []):
        if isinstance(item, dict):
            visuals.append(
                {
                    "caption": str(item.get("caption") or item.get("title") or "Lesson diagram").strip(),
                    "kind": str(item.get("kind") or item.get("type") or "diagram").strip(),
                    "visual_id": str(item.get("visual_id") or item.get("id") or "").strip(),
                }
            )
        elif item:
            visuals.append({"caption": str(item), "kind": "diagram", "visual_id": ""})

    teaching_sequence = [c["name"] for c in concepts] or vocabulary[:6] or [topic]
    prerequisites = _dedupe(
        _texts(list(profile.get("prerequisites") or []), "text", "name")
        + _texts(list((sif.get("analysis") or {}).get("prerequisites") or []), "text", "name")
    )

    accessibility_profile = {
        "needs_chunking": True,
        "needs_glossary": True,
        "needs_visual_first": True,
        "needs_literal_language": True,
        "needs_listen_cues": True,
    }

    contributions = {
        "kie_ucf": bool(claim_texts or concepts),
        "sif": bool(sif.get("analysis") or misconceptions or assessments),
        "uvie": bool(visuals or uvie),
        "lce": True,
        "visible_targets": [
            "explanation",
            "example",
            "diagram",
            "concept_map",
            "vocabulary",
            "assessment",
            "reflection",
            "practice",
            "teacher_guidance",
            "parent_support",
        ],
    }

    board = {
        "schema": "alora.lesson_intelligence_board.v1",
        "version": BOARD_VERSION,
        "topic": topic,
        "subject": subject,
        "verified_claims": claim_texts,
        "concepts": concepts,
        "concept_hierarchy": teaching_sequence,
        "teaching_sequence": teaching_sequence,
        "prerequisites": prerequisites,
        "misconceptions": misconceptions[:8],
        "vocabulary": vocabulary[:12],
        "examples": examples[:10],
        "worked_example_seeds": claim_texts[:4],
        "assessment_objectives": assessments[:8],
        "visual_opportunities": visuals[:8],
        "experiments": _texts(list(clg.get("experiments") or []), "text", "title")[:4],
        "learning_goals": goals[:4] or [studentize_goal(f"Understand {topic}", topic=topic)],
        "accessibility_profile": accessibility_profile,
        "learner_profiles": (
            "standard",
            "ld",
            "dyslexia",
            "adhd",
            "autism",
            "ell",
            "visual",
            "auditory",
            "teacher",
            "parent",
            "vocabulary",
            "worksheet",
        ),
        "teacher_guidance_seeds": [
            "Keep verified facts unchanged; change presentation and scaffolds only.",
            "Cold-call or exit ticket after the core ideas.",
        ],
        "parent_guidance_seeds": [
            "Ask your child to teach you one idea in two minutes.",
            "Praise clear wording and effort, not only the perfect answer.",
        ],
        "engine_contributions": contributions,
        "ready_to_author": bool(claim_texts or concepts),
    }
    return board


def board_claim_for(board: Mapping[str, Any], needle: str = "") -> str:
    claims = list(board.get("verified_claims") or [])
    needle_l = (needle or "").lower()
    for claim in claims:
        if needle_l and needle_l in claim.lower():
            return claim
    return claims[0] if claims else ""


def integration_failures(board: Mapping[str, Any]) -> list[str]:
    """Flag board gaps that mean engines did not contribute visibly enough to author."""
    failures: list[str] = []
    if not board.get("verified_claims"):
        failures.append("No verified claims on the Intelligence Board.")
    if not board.get("concepts"):
        failures.append("No concepts on the Intelligence Board.")
    if not board.get("misconceptions"):
        failures.append("No misconceptions contributed for teaching.")
    if not board.get("visual_opportunities") and not board.get("concepts"):
        failures.append("No visual opportunities for diagrams/maps.")
    if not board.get("ready_to_author"):
        failures.append("Board not ready — refuse empty template authorship.")
    return failures
