"""
Alora AI — adaptation categories and workspace navigation.
"""

from __future__ import annotations

from adaptation_specs import ADAPTATION_SPECS

# Premium pill tabs shown after generation (maps to underlying adaptation specs)
PILL_CATEGORIES = [
    {"id": "vocabulary", "label": "Vocabulary", "spec_ids": ["vocabulary"]},
    {"id": "mainstream", "label": "Mainstream", "spec_ids": ["standard", "gifted"]},
    {
        "id": "learning_differences",
        "label": "Learning Differences",
        "spec_ids": ["ld", "dyslexia", "dysgraphia", "dyscalculia", "ell"],
    },
    {"id": "visual", "label": "Visual Learner", "spec_ids": ["visual", "multisensory"]},
    {"id": "auditory", "label": "Auditory Learner", "spec_ids": ["auditory"]},
    {"id": "neurodiverse", "label": "Neurodiverse", "spec_ids": ["adhd", "autism", "executive"]},
    {"id": "teacher", "label": "Teacher Version", "spec_ids": ["teacher", "tutor"]},
    {"id": "parent", "label": "Parent Version", "spec_ids": ["parent"]},
    {"id": "worksheet", "label": "Exam Worksheet", "spec_ids": ["worksheet"]},
]


def spec_by_id(spec_id: str) -> dict | None:
    for spec in ADAPTATION_SPECS:
        if spec["id"] == spec_id:
            return spec
    return None


def category_for_spec(spec_id: str) -> dict | None:
    for category in PILL_CATEGORIES:
        if spec_id in category["spec_ids"]:
            return category
    return None


def default_spec_for_category(category_id: str) -> str:
    for category in PILL_CATEGORIES:
        if category["id"] == category_id:
            return category["spec_ids"][0]
    return "vocabulary"


def category_for_id(category_id: str) -> dict | None:
    for category in PILL_CATEGORIES:
        if category["id"] == category_id:
            return category
    return None
