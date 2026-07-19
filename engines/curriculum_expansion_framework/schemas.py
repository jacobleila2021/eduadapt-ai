"""Curriculum Expansion Framework — multi-board registry schemas."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

# Programme-level curriculum family ids → UCF board_id
CURRICULUM_FAMILIES: dict[str, dict[str, Any]] = {
    # India
    "ncert": {"ucf_board": "ncert", "family": "india", "programme": "NCERT", "country": "IN", "incremental_priority": 1},
    "cbse": {"ucf_board": "cbse", "family": "india", "programme": "CBSE", "country": "IN", "incremental_priority": 1},
    "icse": {"ucf_board": "icse", "family": "india", "programme": "ICSE", "country": "IN", "incremental_priority": 3},
    "isc": {"ucf_board": "isc", "family": "india", "programme": "ISC", "country": "IN", "incremental_priority": 3},
    "nios": {"ucf_board": "nios", "family": "india", "programme": "NIOS", "country": "IN", "incremental_priority": 3},
    "kerala_scert": {"ucf_board": "kerala_scert", "family": "india", "programme": "Kerala State Board", "country": "IN", "region": "Kerala", "incremental_priority": 3},
    # Cambridge
    "cambridge_primary": {"ucf_board": "cambridge", "family": "cambridge", "programme": "Cambridge Primary", "country": "UK", "incremental_priority": 4},
    "cambridge_lower_secondary": {"ucf_board": "cambridge", "family": "cambridge", "programme": "Cambridge Lower Secondary", "country": "UK", "incremental_priority": 4},
    "cambridge_igcse": {"ucf_board": "cambridge", "family": "cambridge", "programme": "Cambridge IGCSE", "country": "UK", "incremental_priority": 4},
    "cambridge_as_a_level": {"ucf_board": "cambridge", "family": "cambridge", "programme": "Cambridge AS & A Level", "country": "UK", "incremental_priority": 4},
    # IB
    "ib_pyp": {"ucf_board": "ib", "family": "ib", "programme": "IB PYP", "country": "CH", "incremental_priority": 4},
    "ib_myp": {"ucf_board": "ib", "family": "ib", "programme": "IB MYP", "country": "CH", "incremental_priority": 4},
    "ib_dp": {"ucf_board": "ib", "family": "ib", "programme": "IB Diploma Programme", "country": "CH", "incremental_priority": 4},
    # Higher ed / professional
    "university": {"ucf_board": "university", "family": "higher_ed", "programme": "University", "incremental_priority": 5},
    "college": {"ucf_board": "university", "family": "higher_ed", "programme": "College", "incremental_priority": 5},
    "foundation": {"ucf_board": "university", "family": "higher_ed", "programme": "Foundation programme", "incremental_priority": 5},
    "professional_cert": {"ucf_board": "professional", "family": "professional", "programme": "Certification provider", "incremental_priority": 5},
    "corporate_learning": {"ucf_board": "corporate", "family": "professional", "programme": "Corporate learning", "incremental_priority": 5},
    "cpd": {"ucf_board": "professional", "family": "professional", "programme": "Continuing Professional Development", "incremental_priority": 5},
}

PUBLICATION_STATUSES = ("draft", "validated", "published", "deprecated", "rejected")
IMPORT_STATUSES = ("not_started", "imported", "mapped", "failed")
VALIDATION_STATUSES = ("pending", "passed", "failed", "warnings")


@dataclass
class CurriculumRegistryEntry:
    curriculum_id: str
    board_name: str
    programme: str
    country: str = ""
    region: str = ""
    academic_year: str = ""
    version: str = "1.0.0"
    subjects: list[str] = field(default_factory=list)
    grade_levels: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    licensing: dict[str, Any] = field(default_factory=dict)
    import_status: str = "not_started"
    validation_status: str = "pending"
    publication_status: str = "draft"
    ucf_board_id: str = ""
    ucf_package_ids: list[str] = field(default_factory=list)
    family_id: str = ""
    provenance: dict[str, Any] = field(default_factory=dict)
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
