"""Source-linked universal lesson profile; curriculum is optional enrichment."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any

_STOPWORDS = {
    "about", "after", "also", "and", "are", "because", "been", "before",
    "being", "between", "can", "could", "each", "for", "from", "have",
    "into", "its", "lesson", "more", "not", "of", "on", "only", "or",
    "other", "should", "students", "such", "than", "that", "the", "their",
    "them", "then", "there", "these", "they", "this", "through", "to",
    "using", "was", "were", "when", "where", "which", "will", "with", "would",
}
_SKILL_VERBS = {
    "analyse", "analyze", "apply", "calculate", "classify", "compare",
    "construct", "create", "define", "describe", "design", "discuss",
    "evaluate", "explain", "identify", "interpret", "justify", "observe",
    "predict", "read", "solve", "summarise", "summarize", "write",
}
_CURRICULA: list[tuple[str, tuple[str, ...]]] = [
    ("CBSE", ("cbse", "central board of secondary education")),
    ("ICSE", ("icse", "indian certificate of secondary education")),
    ("Cambridge", ("cambridge international", "cambridge lower secondary")),
    ("IB", ("international baccalaureate", "ib myp", "ib dp", "ib pyp")),
    ("IGCSE", ("igcse",)),
    ("GCSE", ("gcse",)),
    ("US Common Core", ("common core", "ccss")),
    ("Australian Curriculum", ("australian curriculum", "acara")),
    ("Singapore Curriculum", ("singapore curriculum", "moe singapore")),
    ("State Board", ("state board", "scert")),
    ("University", ("university", "undergraduate", "postgraduate", "course code")),
    ("Corporate", ("corporate training", "compliance training", "employee training")),
]


@dataclass(frozen=True)
class SourceClaim:
    claim_id: str
    text: str
    source_block_ids: list[str]
    authority: str = "uploaded_source"


@dataclass
class UniversalLessonProfile:
    schema_version: str
    source_id: str
    title: str
    topic: str
    concepts: list[dict[str, Any]]
    skills: list[dict[str, Any]]
    vocabulary: list[dict[str, Any]]
    learning_objectives: list[dict[str, Any]]
    misconceptions: list[dict[str, Any]]
    examples: list[dict[str, Any]]
    assessment_opportunities: list[dict[str, Any]]
    visual_opportunities: list[dict[str, Any]]
    difficulty: dict[str, Any]
    age_estimate: dict[str, Any]
    language: str
    curriculum_resolution: dict[str, Any]
    claim_ledger: list[SourceClaim] = field(default_factory=list)
    grounding_mode: str = "uploaded_source"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def detect_curriculum(
    text: str, user_metadata: dict[str, Any] | None = None
) -> dict[str, Any]:
    metadata = user_metadata or {}
    declared = str(metadata.get("curriculum") or "").strip()
    if declared:
        return {
            "status": "user_declared",
            "curriculum": declared,
            "confidence": 1.0,
            "provenance": "user_metadata",
        }
    sample = str(text or "")[:12000].lower()
    hits = [
        name
        for name, markers in _CURRICULA
        if any(re.search(rf"\b{re.escape(marker)}\b", sample) for marker in markers)
    ]
    if len(hits) == 1:
        return {
            "status": "recognized",
            "curriculum": hits[0],
            "confidence": 0.92,
            "provenance": "source_marker",
        }
    if len(hits) > 1:
        return {
            "status": "ambiguous",
            "curriculum": None,
            "candidates": hits,
            "confidence": 0.45,
            "provenance": "multiple_source_markers",
        }
    return {
        "status": "unknown",
        "curriculum": None,
        "confidence": 0.0,
        "provenance": "no_source_marker",
    }


def _reading_metrics(text: str) -> tuple[dict[str, Any], dict[str, Any]]:
    sentences = max(len(re.findall(r"[.!?]+", text)), 1)
    words = re.findall(r"[A-Za-zÀ-ÿ']+", text)
    word_count = max(len(words), 1)
    average_sentence = word_count / sentences
    average_word = sum(len(word) for word in words) / word_count
    score = average_sentence * 0.45 + average_word * 1.8
    if score < 13:
        band, age = "introductory", "8-11"
    elif score < 18:
        band, age = "intermediate", "11-14"
    elif score < 24:
        band, age = "advanced_secondary", "14-18"
    else:
        band, age = "higher_education_or_professional", "18+"
    return (
        {
            "band": band,
            "score": round(score, 2),
            "average_sentence_words": round(average_sentence, 2),
            "average_word_characters": round(average_word, 2),
        },
        {"band": age, "method": "source_readability_heuristic", "confidence": 0.55},
    )


def _refs(block_id: str) -> list[str]:
    return [block_id] if block_id else []


def build_universal_lesson_profile(
    source_envelope: dict[str, Any],
) -> UniversalLessonProfile:
    blocks = [
        block
        for block in source_envelope.get("blocks") or []
        if isinstance(block, dict) and str(block.get("text") or "").strip()
    ]
    text = str(source_envelope.get("text") or "")
    first_heading = next(
        (
            str(block["text"]).strip()
            for block in blocks
            if block.get("kind") == "heading"
        ),
        "",
    )
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "")
    title = (first_heading or first_line or "Uploaded Lesson")[:160]
    topic = re.split(r"[.:!?]", title, 1)[0][:100].strip() or "Uploaded Lesson"

    word_rows: list[tuple[str, str]] = []
    for block in blocks:
        block_id = str(block.get("block_id") or "")
        for word in re.findall(r"\b[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'-]{3,}\b", str(block["text"])):
            normalized = word.lower()
            if normalized not in _STOPWORDS:
                word_rows.append((normalized, block_id))
    counts = Counter(word for word, _ in word_rows)
    top_words = [word for word, _ in counts.most_common(20)]

    concepts = [
        {
            "concept": word,
            "source_refs": sorted({ref for token, ref in word_rows if token == word})[:8],
            "frequency": counts[word],
        }
        for word in top_words[:12]
    ]
    vocabulary = [
        {
            "term": word,
            "source_refs": sorted({ref for token, ref in word_rows if token == word})[:8],
        }
        for word in top_words[:15]
    ]

    objectives: list[dict[str, Any]] = []
    skills: list[dict[str, Any]] = []
    misconceptions: list[dict[str, Any]] = []
    examples: list[dict[str, Any]] = []
    assessments: list[dict[str, Any]] = []
    visuals: list[dict[str, Any]] = []
    ledger: list[SourceClaim] = []
    claim_index = 0

    for block in blocks:
        block_text = str(block["text"])
        block_id = str(block.get("block_id") or "")
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", block_text):
            sentence = sentence.strip()
            if len(sentence) < 8:
                continue
            claim_index += 1
            ledger.append(
                SourceClaim(
                    claim_id=f"claim_{claim_index:05d}",
                    text=sentence[:1200],
                    source_block_ids=_refs(block_id),
                )
            )
            low = sentence.lower()
            if re.search(r"\b(?:objective|students? will|learners? will|you will learn)\b", low):
                objectives.append({"objective": sentence, "source_refs": _refs(block_id)})
            verbs = sorted(
                verb
                for verb in _SKILL_VERBS
                if re.search(rf"\b{re.escape(verb)}\w*\b", low)
            )
            for verb in verbs:
                skills.append({"skill": verb, "source_refs": _refs(block_id)})
            if "misconception" in low or "common mistake" in low:
                misconceptions.append(
                    {
                        "misconception": sentence,
                        "source_refs": _refs(block_id),
                        "status": "explicit_in_source",
                    }
                )
            if re.search(r"\b(?:example|for instance|case study)\b", low):
                examples.append({"example": sentence, "source_refs": _refs(block_id)})
            if sentence.endswith("?"):
                assessments.append(
                    {"question": sentence, "source_refs": _refs(block_id)}
                )
            if re.search(
                r"\b(?:cycle|process|sequence|timeline|compare|structure|system|flow|map)\b",
                low,
            ):
                visuals.append(
                    {
                        "opportunity": sentence[:240],
                        "source_refs": _refs(block_id),
                    }
                )

    if not objectives:
        for concept in concepts[:5]:
            objectives.append(
                {
                    "objective": f"Explain {concept['concept']} using the uploaded source.",
                    "source_refs": concept["source_refs"],
                    "status": "pedagogically_inferred",
                }
            )

    difficulty, age = _reading_metrics(text)
    curriculum = detect_curriculum(text, source_envelope.get("user_metadata"))
    return UniversalLessonProfile(
        schema_version="3.0.0",
        source_id=str(source_envelope.get("source_id") or ""),
        title=title,
        topic=topic,
        concepts=concepts,
        skills=list({row["skill"]: row for row in skills}.values())[:12],
        vocabulary=vocabulary,
        learning_objectives=objectives[:12],
        misconceptions=misconceptions[:10],
        examples=examples[:12],
        assessment_opportunities=assessments[:20],
        visual_opportunities=visuals[:12],
        difficulty=difficulty,
        age_estimate=age,
        language=str(source_envelope.get("language") or "unknown"),
        curriculum_resolution=curriculum,
        claim_ledger=ledger[:500],
    )


def profile_to_prompt_block(profile: dict[str, Any]) -> str:
    """Compact authoritative prompt representation with source references."""
    lines = [
        "SOURCE_GROUNDING_MODE: uploaded_source",
        "Use only SOURCE_CLAIMS and VERIFIED_ENGINE_ARTIFACTS for factual content.",
        "Do not add uncited general knowledge. Every generated section and answer must include source_refs.",
        f"TOPIC: {profile.get('topic') or 'Uploaded lesson'}",
    ]
    for claim in (profile.get("claim_ledger") or [])[:160]:
        refs = ",".join(claim.get("source_block_ids") or [])
        lines.append(
            f"- {claim.get('claim_id')} [{refs}]: {str(claim.get('text') or '')[:800]}"
        )
    return "\n".join(lines)
