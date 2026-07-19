"""Deterministic adaptation rules — profile → supports (presentation only)."""

from __future__ import annotations

from typing import Any

from engines.accessibility_intelligence_engine.schemas import AccessibilityRecommendation
from engines.accessibility_intelligence_engine.sensory_profiles import PROFILE_CATALOG, normalize_profile_key

# Map AIE profiles → adaptation_specs ids (when they exist)
# Map AIE profiles → generated adaptation_specs ids (nine-product set).
# Extra Section B profiles fall back to the closest generated tab (ld / standard / etc.).
PROFILE_TO_SPEC: dict[str, str] = {
    "dyslexia": "ld",
    "dysgraphia": "ld",
    "dyscalculia": "standard",
    "adhd": "ld",
    "autism": "ld",
    "executive_function": "ld",
    "ell": "ell",
    "gifted": "standard",
    "twice_exceptional": "standard",
    "visual": "visual",
    "auditory": "auditory",
    "ld": "ld",
    "sld": "ld",
    "multisensory": "visual",
    "neurotypical": "standard",
    "adult": "standard",
    "professional": "standard",
    "low_vision": "visual",
    "blind": "auditory",
    "deaf": "visual",
    "hard_of_hearing": "visual",
    "colour_vision_deficiency": "standard",
    "motor": "standard",
    "processing_speed": "ld",
    "working_memory": "ld",
}


RULES: list[dict[str, Any]] = [
    {
        "when_any": ["dyslexia", "ld"],
        "category": "reading",
        "support_id": "dyslexia_font_spacing",
        "title": "Dyslexia-friendly typography",
        "reason": "Reduce visual crowding and letter confusion",
        "evidence": "WCAG 1.4.12 + dyslexia design heuristics",
        "priority": 10,
        "impact": "high",
        "confidence": 0.9,
    },
    {
        "when_any": ["dyslexia", "blind", "low_vision", "auditory"],
        "category": "audio",
        "support_id": "tts_enabled",
        "title": "Text-to-speech",
        "reason": "Provide auditory access to lesson text",
        "evidence": "UDL multiple means of representation",
        "priority": 15,
        "impact": "high",
        "confidence": 0.92,
    },
    {
        "when_any": ["adhd", "executive_function", "working_memory", "processing_speed"],
        "category": "ef",
        "support_id": "task_chunking",
        "title": "Task chunking + checkpoints",
        "reason": "Reduce cognitive load and support planning",
        "evidence": "Executive function scaffolds",
        "priority": 12,
        "impact": "high",
        "confidence": 0.88,
    },
    {
        "when_any": ["adhd"],
        "category": "sensory",
        "support_id": "focus_mode",
        "title": "Focus mode / reduced distraction",
        "reason": "Limit competing stimuli during reading",
        "evidence": "Attention support best practice",
        "priority": 18,
        "impact": "medium",
        "confidence": 0.85,
    },
    {
        "when_any": ["autism"],
        "category": "interaction",
        "support_id": "predictable_structure",
        "title": "Predictable lesson structure",
        "reason": "Literal language and consistent sequence",
        "evidence": "Autism-friendly instructional design",
        "priority": 14,
        "impact": "high",
        "confidence": 0.87,
    },
    {
        "when_any": ["ell"],
        "category": "language",
        "support_id": "glossary_frames",
        "title": "Glossary + sentence frames",
        "reason": "Scaffold academic language without changing facts",
        "evidence": "ELL scaffolding research",
        "priority": 16,
        "impact": "high",
        "confidence": 0.9,
    },
    {
        "when_any": ["dyscalculia"],
        "category": "visual",
        "support_id": "concrete_math",
        "title": "Concrete before abstract + formula cards",
        "reason": "Support number sense without changing STEM results",
        "evidence": "Dyscalculia pedagogy",
        "priority": 11,
        "impact": "high",
        "confidence": 0.86,
    },
    {
        "when_any": ["dysgraphia"],
        "category": "interaction",
        "support_id": "alt_response",
        "title": "Oral/typed response options",
        "reason": "Reduce handwriting barrier",
        "evidence": "UDL action & expression",
        "priority": 17,
        "impact": "high",
        "confidence": 0.84,
    },
    {
        "when_any": ["low_vision", "blind"],
        "category": "visual",
        "support_id": "screen_reader_alt",
        "title": "Screen reader + alt text",
        "reason": "Non-visual access to figures and UI",
        "evidence": "WCAG 1.1.1, 1.3.1",
        "priority": 5,
        "impact": "critical",
        "confidence": 0.95,
    },
    {
        "when_any": ["deaf", "hard_of_hearing"],
        "category": "audio",
        "support_id": "captions_transcripts",
        "title": "Captions and transcripts",
        "reason": "Audio-independent access",
        "evidence": "WCAG 1.2.2",
        "priority": 8,
        "impact": "critical",
        "confidence": 0.94,
    },
    {
        "when_any": ["colour_vision_deficiency"],
        "category": "visual",
        "support_id": "non_colour_cues",
        "title": "Patterns/labels — not colour alone",
        "evidence": "WCAG 1.4.1",
        "reason": "Information must not rely on colour only",
        "priority": 20,
        "impact": "medium",
        "confidence": 0.9,
    },
    {
        "when_any": ["motor"],
        "category": "navigation",
        "support_id": "keyboard_large_targets",
        "title": "Keyboard-only + large touch targets",
        "reason": "Pointer-independent operation",
        "evidence": "WCAG 2.1.1, 2.5.5",
        "priority": 9,
        "impact": "high",
        "confidence": 0.93,
    },
    {
        "when_any": ["gifted", "twice_exceptional"],
        "category": "assessment",
        "support_id": "extension_pathways",
        "title": "Extension / depth options",
        "reason": "Challenge without removing scaffolds for 2e",
        "evidence": "Gifted pedagogy + UDL",
        "priority": 40,
        "impact": "medium",
        "confidence": 0.8,
    },
    {
        "when_any": ["twice_exceptional"],
        "category": "ef",
        "support_id": "challenge_plus_scaffold",
        "title": "Challenge with accessibility scaffolds",
        "reason": "2e learners need both stretch and support",
        "evidence": "Twice-exceptional best practice",
        "priority": 13,
        "impact": "high",
        "confidence": 0.82,
    },
]


def apply_rules(active_profiles: list[str]) -> list[AccessibilityRecommendation]:
    profiles = {normalize_profile_key(p) for p in active_profiles}
    out: list[AccessibilityRecommendation] = []
    seen: set[str] = set()
    for rule in RULES:
        if not profiles.intersection(rule["when_any"]):
            continue
        sid = rule["support_id"]
        if sid in seen:
            continue
        seen.add(sid)
        out.append(
            AccessibilityRecommendation(
                support_id=sid,
                category=rule["category"],
                title=rule["title"],
                reason=rule["reason"],
                evidence=rule["evidence"],
                priority=int(rule["priority"]),
                expected_impact=rule.get("impact") or "medium",
                confidence=float(rule.get("confidence") or 0.8),
                presentation_only=True,
            )
        )
    out.sort(key=lambda r: r.priority)
    return out


def specs_for_profiles(active_profiles: list[str]) -> list[str]:
    """Return adaptation_specs ids to prioritize for this learner."""
    specs = []
    for p in active_profiles:
        key = normalize_profile_key(p)
        spec = PROFILE_TO_SPEC.get(key)
        if spec and spec not in specs:
            specs.append(spec)
    if not specs:
        specs = ["standard"]
    return specs


def catalog_supports(active_profiles: list[str]) -> list[str]:
    supports: list[str] = []
    for p in active_profiles:
        key = normalize_profile_key(p)
        row = PROFILE_CATALOG.get(key) or {}
        for s in row.get("supports") or []:
            if s not in supports:
                supports.append(s)
    return supports
