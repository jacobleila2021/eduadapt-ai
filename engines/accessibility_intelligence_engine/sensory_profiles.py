"""Sensory / learner profile catalog — UDL-aligned functional descriptors."""

from __future__ import annotations

from typing import Any

from engines.accessibility_intelligence_engine.schemas import SUPPORTED_PROFILES

PROFILE_CATALOG: dict[str, dict[str, Any]] = {
    "neurotypical": {
        "label": "Neurotypical / Mainstream",
        "modalities": ["visual", "text"],
        "presentation": "standard",
        "notes": "Standard UDL sequence",
    },
    "dyslexia": {
        "label": "Dyslexia-friendly reading",
        "modalities": ["audio", "visual"],
        "presentation": "dyslexia",
        "supports": ["opendyslexic", "ruler", "chunked_text", "tts"],
    },
    "dysgraphia": {
        "label": "Dysgraphia-friendly output",
        "modalities": ["oral", "typed"],
        "presentation": "dysgraphia",
        "supports": ["oral_response", "speech_to_text", "scaffolded_writing"],
    },
    "dyscalculia": {
        "label": "Dyscalculia-friendly math",
        "modalities": ["concrete", "visual"],
        "presentation": "dyscalculia",
        "supports": ["concrete_before_abstract", "formula_cards", "no_timed_drills"],
    },
    "adhd": {
        "label": "ADHD / attention support",
        "modalities": ["chunked", "interactive"],
        "presentation": "adhd",
        "supports": ["chunk_2min", "checkpoints", "focus_mode", "timers"],
    },
    "autism": {
        "label": "Autism-friendly structure",
        "modalities": ["predictable", "literal"],
        "presentation": "autism",
        "supports": ["literal_language", "predictable_structure", "sensory_calm"],
    },
    "executive_function": {
        "label": "Executive function support",
        "modalities": ["checklist", "step"],
        "presentation": "executive",
        "supports": ["checklists", "task_chunking", "planning_templates"],
    },
    "processing_speed": {
        "label": "Processing speed support",
        "modalities": ["paced"],
        "presentation": "standard",
        "supports": ["extra_time", "reduced_density", "pause_points"],
    },
    "working_memory": {
        "label": "Working memory support",
        "modalities": ["external_memory"],
        "presentation": "executive",
        "supports": ["visible_steps", "reference_cards", "chunked_instructions"],
    },
    "sld": {
        "label": "Specific learning disorder supports",
        "modalities": ["multisensory"],
        "presentation": "ld",
        "supports": ["multisensory", "scaffolds"],
    },
    "ell": {
        "label": "English language learner",
        "modalities": ["glossary", "visual"],
        "presentation": "ell",
        "supports": ["glossary", "sentence_frames", "dual_language"],
    },
    "gifted": {
        "label": "Gifted / extension",
        "modalities": ["extension"],
        "presentation": "gifted",
        "supports": ["extension_pathways", "depth"],
    },
    "twice_exceptional": {
        "label": "Twice-exceptional",
        "modalities": ["challenge_plus_support"],
        "presentation": "gifted",
        "supports": ["extension_plus_scaffolds"],
    },
    "low_vision": {
        "label": "Low vision",
        "modalities": ["large_text", "audio"],
        "presentation": "visual",
        "supports": ["large_font", "high_contrast", "tts", "zoom"],
    },
    "blind": {
        "label": "Blind / screen-reader primary",
        "modalities": ["audio", "braille"],
        "presentation": "auditory",
        "supports": ["screen_reader", "alt_text", "transcripts", "braille_ready"],
    },
    "colour_vision_deficiency": {
        "label": "Colour vision deficiency",
        "modalities": ["pattern"],
        "presentation": "standard",
        "supports": ["patterns_not_colour_alone", "high_contrast"],
    },
    "deaf": {
        "label": "Deaf",
        "modalities": ["visual", "caption"],
        "presentation": "visual",
        "supports": ["captions", "transcripts", "visual_alerts"],
    },
    "hard_of_hearing": {
        "label": "Hard of hearing",
        "modalities": ["caption", "visual"],
        "presentation": "visual",
        "supports": ["captions", "volume_independent_text"],
    },
    "motor": {
        "label": "Motor accessibility",
        "modalities": ["keyboard", "switch"],
        "presentation": "standard",
        "supports": ["keyboard_only", "large_targets", "switch_access"],
    },
    "adult": {
        "label": "Adult learner",
        "modalities": ["self_paced"],
        "presentation": "university",
        "supports": ["self_paced", "goal_oriented"],
    },
    "professional": {
        "label": "Professional learning",
        "modalities": ["concise"],
        "presentation": "professional",
        "supports": ["concise", "just_in_time"],
    },
    "visual": {
        "label": "Visual preference",
        "modalities": ["diagram"],
        "presentation": "visual",
        "supports": ["diagrams_first", "concept_maps"],
    },
    "auditory": {
        "label": "Auditory preference",
        "modalities": ["audio"],
        "presentation": "auditory",
        "supports": ["tts", "discussion"],
    },
    "ld": {
        "label": "Learning differences (general)",
        "modalities": ["multisensory"],
        "presentation": "ld",
        "supports": ["scaffolds", "multisensory"],
    },
    "multisensory": {
        "label": "Multisensory",
        "modalities": ["see_hear_do"],
        "presentation": "multisensory",
        "supports": ["see_hear_do"],
    },
}


def catalog() -> dict[str, dict[str, Any]]:
    return {k: PROFILE_CATALOG[k] for k in SUPPORTED_PROFILES if k in PROFILE_CATALOG}


def normalize_profile_key(raw: str) -> str:
    key = (raw or "").strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "executive": "executive_function",
        "ef": "executive_function",
        "cvd": "colour_vision_deficiency",
        "color_blind": "colour_vision_deficiency",
        "colour_blind": "colour_vision_deficiency",
        "hoh": "hard_of_hearing",
        "2e": "twice_exceptional",
    }
    return aliases.get(key, key)
