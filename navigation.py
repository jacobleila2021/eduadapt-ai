"""
Alora AI — adaptation categories and workspace navigation.
"""

from __future__ import annotations

from adaptation_specs import ADAPTATION_SPECS

# Exactly 9 version tabs — one spec each, no sub-classification pills.
PILL_CATEGORIES = [
    {"id": "vocabulary", "label": "Vocabulary Support", "spec_ids": ["vocabulary"]},
    {"id": "mainstream", "label": "Mainstream Support", "spec_ids": ["standard"]},
    {"id": "neurodiversity", "label": "Neurodiversity Support", "spec_ids": ["ld"]},
    {"id": "ell", "label": "English Language Support", "spec_ids": ["ell"]},
    {"id": "visual", "label": "Visual Learner Support", "spec_ids": ["visual"]},
    {"id": "auditory", "label": "Auditory Learner Support", "spec_ids": ["auditory"]},
    {"id": "teacher", "label": "Teacher Version", "spec_ids": ["teacher"]},
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
