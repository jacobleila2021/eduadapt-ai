"""
Alora AI — adaptation categories and workspace navigation.
Nine classroom adaptations only (matches generate=True in adaptation_specs).
"""

from __future__ import annotations

from adaptation_specs import ADAPTATION_SPECS

# One pill per generated adaptation — decided product set of nine.
PILL_CATEGORIES = [
    {"id": "vocabulary", "label": "Vocabulary Support", "spec_ids": ["vocabulary"]},
    {"id": "mainstream", "label": "Mainstream Support", "spec_ids": ["standard"]},
    {"id": "neurodiversity", "label": "Dyslexia Smart", "spec_ids": ["ld"]},
    {"id": "adhd", "label": "ADHD Support", "spec_ids": ["adhd"]},
    {"id": "autism", "label": "Autism Support", "spec_ids": ["autism"]},
    {"id": "ell", "label": "English Language Support", "spec_ids": ["ell"]},
    {"id": "visual", "label": "Visual Learner Support", "spec_ids": ["visual"]},
    {"id": "auditory", "label": "Auditory Learner Support", "spec_ids": ["auditory"]},
    {"id": "teacher", "label": "Teacher Version", "spec_ids": ["teacher"]},
    {"id": "parent", "label": "Parent Version", "spec_ids": ["parent"]},
    {"id": "assessment", "label": "Exam Worksheet", "spec_ids": ["worksheet"]},
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
