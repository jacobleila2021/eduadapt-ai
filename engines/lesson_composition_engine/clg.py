"""Canonical Lesson Graph (CLG) — single educational truth before any prose is written."""

from __future__ import annotations

import re
from typing import Any, Mapping

from engines.lesson_composition_engine.schemas import CanonicalLessonGraph, ClgEdge, ClgNode

_STOP = frozenset(
    {
        "this",
        "that",
        "with",
        "from",
        "have",
        "will",
        "were",
        "been",
        "they",
        "them",
        "their",
        "about",
        "which",
        "while",
        "where",
        "when",
        "what",
        "into",
        "also",
        "than",
        "then",
        "only",
        "over",
        "such",
        "some",
        "more",
        "most",
        "other",
        "each",
        "make",
        "like",
        "just",
        "very",
        "subject",
        "grade",
        "level",
        "objective",
        "objectives",
        "students",
        "student",
        "lesson",
        "chapter",
        "learning",
    }
)


def _uli_dict(uli: Any) -> dict[str, Any]:
    if uli is None:
        return {}
    if isinstance(uli, dict):
        return uli
    if hasattr(uli, "to_dict"):
        try:
            return dict(uli.to_dict() or {})
        except Exception:  # noqa: BLE001
            pass
    profile = getattr(uli, "universal_profile", None) or {}
    if isinstance(profile, dict):
        return {
            "universal_profile": profile,
            "claim_ledger": getattr(uli, "claim_ledger", []) or [],
        }
    return {}


def _claims(uli: Any, profile: Mapping[str, Any]) -> list[dict[str, Any]]:
    ledger = []
    if hasattr(uli, "claim_ledger"):
        ledger = list(getattr(uli, "claim_ledger") or [])
    elif isinstance(uli, dict):
        ledger = list(uli.get("claim_ledger") or [])
    if not ledger:
        ledger = list(profile.get("claim_ledger") or [])
    out: list[dict[str, Any]] = []
    for row in ledger:
        if isinstance(row, dict) and row.get("text"):
            out.append(row)
        elif isinstance(row, str) and row.strip():
            out.append(
                {
                    "text": row.strip(),
                    "claim_id": f"claim_{len(out)+1:05d}",
                    "source_block_ids": [],
                }
            )
    return out[:120]


def _student_goal(topic: str, concepts: list[str], claims: list[str]) -> str:
    if concepts:
        joined = ", ".join(concepts[:4])
        return (
            f"Students will understand how {joined} work together in {topic}, "
            f"using accurate lesson terms and everyday examples."
        )
    if claims:
        snippet = claims[0][:160].rstrip(".")
        return f"Students will understand {snippet}."
    return f"Students will understand the main ideas in {topic}."


def _concept_entries(
    profile: Mapping[str, Any], sif: Mapping[str, Any], claims: list[dict]
) -> list[dict[str, Any]]:
    concepts: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(name: str, explanation: str = "", refs: list[str] | None = None) -> None:
        key = re.sub(r"\W+", "", name).lower()
        if not name or key in seen or key in _STOP or len(name) < 3:
            return
        seen.add(key)
        concepts.append(
            {
                "concept_id": f"concept_{len(concepts)+1:03d}",
                "name": name.strip()[:80],
                "explanation": (explanation or "").strip()[:500],
                "source_refs": list(refs or [])[:8],
            }
        )

    for row in profile.get("concepts") or profile.get("key_concepts") or []:
        if isinstance(row, dict):
            add(
                str(row.get("concept") or row.get("name") or ""),
                str(row.get("explanation") or ""),
                row.get("source_refs") or [],
            )
        elif isinstance(row, str):
            add(row)

    analysis = sif.get("analysis") if isinstance(sif.get("analysis"), dict) else sif
    graph = (analysis or {}).get("concept_graph") or {}
    for node in graph.get("nodes") or []:
        if isinstance(node, dict):
            add(
                str(node.get("label") or node.get("id") or ""),
                str(node.get("text") or node.get("description") or ""),
            )

    if len(concepts) < 2:
        for claim in claims[:6]:
            text = str(claim.get("text") or "")
            words = re.findall(r"\b[A-Z][a-zA-Z]{3,}\b", text)
            for w in words[:2]:
                add(w, text[:240], claim.get("source_block_ids") or [claim.get("claim_id", "")])

    return concepts[:12]


def _vocabulary_from_sif_and_concepts(
    sif: Mapping[str, Any],
    concepts: list[dict[str, Any]],
    claims: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Subject/CLG vocabulary — never frequency word lists."""
    vocab: list[dict[str, Any]] = []
    seen: set[str] = set()

    def add(
        term: str,
        definition: str = "",
        example: str = "",
        refs: list[str] | None = None,
        **extra: Any,
    ) -> None:
        clean = re.sub(r"\s+", " ", (term or "").strip())
        key = clean.lower()
        if not clean or key in seen or key in _STOP or len(clean) < 3:
            return
        if clean.lower() in {"subject", "grade", "chapter", "objective"}:
            return
        seen.add(key)
        entry = {
            "term": clean[:1].upper() + clean[1:],
            "definition": (definition or f"A key idea from this lesson about {clean}.").strip()[:300],
            "simple_explanation": (
                definition or f"{clean} is an important idea in this lesson."
            ).strip()[:220],
            "example": (example or "").strip()[:220],
            "part_of_speech": extra.get("part_of_speech") or "noun",
            "pronunciation": extra.get("pronunciation") or "",
            "synonyms": list(extra.get("synonyms") or [])[:4],
            "antonyms": list(extra.get("antonyms") or [])[:4],
            "related_concepts": list(extra.get("related_concepts") or [])[:4],
            "difficulty": extra.get("difficulty") or "core",
            "reading_level": extra.get("reading_level") or "lesson",
            "source_refs": list(refs or [])[:8],
            "provenance": extra.get("provenance") or "clg_sif",
        }
        vocab.append(entry)

    analysis = sif.get("analysis") if isinstance(sif.get("analysis"), dict) else {}
    meta = (analysis or {}).get("metadata") or sif.get("metadata") or {}
    for row in meta.get("vocabulary") or meta.get("entries") or []:
        if isinstance(row, dict):
            add(
                str(row.get("term") or row.get("word") or ""),
                str(row.get("definition") or row.get("gloss") or ""),
                str(row.get("example") or ""),
                provenance="sif_pack",
                part_of_speech=row.get("part_of_speech") or "noun",
                synonyms=row.get("synonyms") or [],
                antonyms=row.get("antonyms") or [],
                related_concepts=row.get("related_concepts") or [],
            )
        elif isinstance(row, str):
            add(row, provenance="sif_pack")

    nested = meta.get("vocabulary") if isinstance(meta.get("vocabulary"), dict) else {}
    for row in (nested or {}).get("entries") or []:
        if isinstance(row, dict):
            add(str(row.get("term") or ""), str(row.get("definition") or ""), provenance="sif_pack")

    for c in concepts:
        name = str(c.get("name") or "")
        expl = str(c.get("explanation") or "")
        example = ""
        for claim in claims:
            text = str(claim.get("text") or "")
            if name and name.lower() in text.lower():
                example = text[:180]
                break
        add(
            name,
            expl or f"{name} is a core concept in this lesson.",
            example,
            c.get("source_refs"),
            related_concepts=[name],
            provenance="clg_concept",
        )

    return vocab[:16]


def _misconceptions(sif: Mapping[str, Any], profile: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    analysis = sif.get("analysis") if isinstance(sif.get("analysis"), dict) else {}
    for m in (analysis or {}).get("misconceptions") or sif.get("misconceptions") or []:
        if isinstance(m, dict):
            rows.append(
                {
                    "label": str(m.get("label") or m.get("misconception") or "Common misconception"),
                    "correction": str(
                        m.get("correction_strategy")
                        or m.get("remediation")
                        or m.get("correction")
                        or "Check the lesson evidence and use accurate terms."
                    ),
                    "related_concepts": list(m.get("related_concepts") or [])[:6],
                    "provenance": str(m.get("provenance") or "sif"),
                }
            )
    for m in profile.get("misconceptions") or []:
        if isinstance(m, dict):
            rows.append(
                {
                    "label": str(m.get("misconception") or m.get("label") or ""),
                    "correction": "Use the uploaded lesson evidence to correct this idea.",
                    "related_concepts": [],
                    "provenance": "uli_profile",
                }
            )
    return rows[:10]


def build_canonical_lesson_graph(
    uli: Any = None,
    *,
    sif: Mapping[str, Any] | None = None,
    uvie: Mapping[str, Any] | None = None,
    topic_hint: str = "",
) -> CanonicalLessonGraph:
    """Transform ULI + SIF + UVIE into one Canonical Lesson Graph (no frequency vocab)."""
    sif = dict(sif or {})
    uvie = dict(uvie or {})
    payload = _uli_dict(uli)
    profile = payload.get("universal_profile") or payload.get("profile") or {}
    if not isinstance(profile, dict):
        profile = {}
    if hasattr(uli, "universal_profile") and isinstance(uli.universal_profile, dict):
        profile = {**profile, **uli.universal_profile}

    topic = (
        topic_hint
        or str(profile.get("topic") or profile.get("title") or "")
        or "this lesson"
    ).strip()
    subject_key = str(
        sif.get("subject_key")
        or (sif.get("analysis") or {}).get("subject_key")
        or profile.get("subject")
        or "general"
    )

    claims = _claims(uli, profile)
    claim_texts = [str(c.get("text") or "").strip() for c in claims if c.get("text")]
    concepts = _concept_entries(profile, sif, claims)
    concept_names = [c["name"] for c in concepts]
    vocab = _vocabulary_from_sif_and_concepts(sif, concepts, claims)
    misconceptions = _misconceptions(sif, profile)

    facts = []
    for i, text in enumerate(claim_texts[:24]):
        facts.append(
            {
                "fact_id": f"fact_{i+1:03d}",
                "text": text,
                "source_refs": claims[i].get("source_block_ids") or [claims[i].get("claim_id", "")],
            }
        )

    examples = []
    for i, text in enumerate(claim_texts[1:9]):
        examples.append({"example_id": f"ex_{i+1:03d}", "text": text, "kind": "source_example"})

    visual_refs = []
    for i, vis in enumerate((uvie.get("visuals") or uvie.get("preferred_visuals") or [])[:8]):
        if not isinstance(vis, dict):
            continue
        visual_refs.append(
            {
                "visual_id": str(vis.get("visual_id") or vis.get("id") or f"vis_{i+1}"),
                "caption": str(vis.get("caption") or vis.get("label") or "Lesson diagram"),
                "visual_type": str(vis.get("visual_type") or vis.get("type") or "diagram"),
                "has_svg": bool(vis.get("svg") or vis.get("svg_diagram")),
                "has_asset": bool(vis.get("asset_paths")),
            }
        )

    analysis = sif.get("analysis") if isinstance(sif.get("analysis"), dict) else {}
    assessments = []
    for i, hint in enumerate(((analysis or {}).get("assessment_hints") or [])[:8]):
        if isinstance(hint, dict):
            assessments.append(
                {
                    "outcome_id": f"assess_{i+1:03d}",
                    "prompt": str(hint.get("prompt") or hint.get("question") or hint.get("label") or ""),
                    "bloom": str(hint.get("bloom") or ""),
                }
            )
    if not assessments and concept_names:
        for i, name in enumerate(concept_names[:4]):
            assessments.append(
                {
                    "outcome_id": f"assess_{i+1:03d}",
                    "prompt": f"Explain {name} using evidence from the lesson.",
                    "bloom": "understand",
                }
            )

    a11y = []
    for row in (analysis or {}).get("accessibility_guidance") or []:
        if isinstance(row, dict):
            a11y.append({"note": str(row.get("guidance") or row.get("note") or row), "provenance": "sif"})
        elif isinstance(row, str):
            a11y.append({"note": row, "provenance": "sif"})

    goal_text = _student_goal(topic, concept_names, claim_texts)
    learning_goals = [
        {
            "goal_id": "goal_001",
            "text": goal_text,
            "source_refs": (claims[0].get("source_block_ids") if claims else []) or [],
        }
    ]

    relationships = []
    for i in range(len(concepts) - 1):
        relationships.append(
            {
                "edge_id": f"rel_{i+1:03d}",
                "source": concepts[i]["concept_id"],
                "target": concepts[i + 1]["concept_id"],
                "relation": "teaches",
                "label": f"{concepts[i]['name']} leads to {concepts[i+1]['name']}",
            }
        )
    if len(concepts) >= 3 and "cycle" in topic.lower():
        relationships.append(
            {
                "edge_id": f"rel_{len(relationships)+1:03d}",
                "source": concepts[-1]["concept_id"],
                "target": concepts[0]["concept_id"],
                "relation": "teaches",
                "label": f"{concepts[-1]['name']} returns to {concepts[0]['name']}",
            }
        )

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    nodes.append(ClgNode("goal_001", "goal", "Learning Goal", goal_text).to_dict())
    for c in concepts:
        nodes.append(
            ClgNode(
                c["concept_id"],
                "concept",
                c["name"],
                c.get("explanation") or "",
                c.get("source_refs") or [],
            ).to_dict()
        )
    for v in vocab:
        nid = f"vocab_{len([n for n in nodes if n['kind']=='vocabulary'])+1:03d}"
        nodes.append(
            ClgNode(
                nid,
                "vocabulary",
                v["term"],
                v.get("definition") or "",
                v.get("source_refs") or [],
                {"card": v},
            ).to_dict()
        )
    for rel in relationships:
        edges.append(ClgEdge(rel["edge_id"], rel["source"], rel["target"], rel["relation"]).to_dict())
    for i, vis in enumerate(visual_refs):
        vid = vis["visual_id"]
        nodes.append(ClgNode(vid, "visual", vis["caption"], vis["visual_type"]).to_dict())
        if concepts:
            edges.append(
                ClgEdge(
                    f"vis_e_{i+1:03d}",
                    concepts[min(i, len(concepts) - 1)]["concept_id"],
                    vid,
                    "visualized_by",
                ).to_dict()
            )

    return CanonicalLessonGraph(
        topic=topic,
        subject_key=subject_key,
        learning_goals=learning_goals,
        core_concepts=concepts,
        facts=facts,
        relationships=relationships,
        vocabulary=vocab,
        misconceptions=misconceptions,
        examples=examples,
        visual_refs=visual_refs,
        assessment_outcomes=assessments,
        accessibility_notes=a11y,
        claim_texts=claim_texts,
        nodes=nodes,
        edges=edges,
        provenance={
            "uli": bool(uli),
            "sif": bool(sif),
            "uvie": bool(uvie),
            "frequency_vocab_used": False,
            "mutates_curriculum": False,
        },
    )
