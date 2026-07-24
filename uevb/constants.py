"""Universal Educational Validation & Benchmarking — constants.

UEVB is a validation authority, not an intelligence engine.
"""

from __future__ import annotations

UNIVERSAL_EDUCATIONAL_VALIDATION_BENCHMARKING_SMOKE_OK = True
UEVB_VERSION = "1.0.0"
UEVB_SCHEMA = "alora.uevb.v1"

SUBJECTS = (
    "mathematics",
    "physics",
    "chemistry",
    "biology",
    "english",
    "history",
    "geography",
    "civics",
    "economics",
    "business_studies",
    "computer_science",
    "world_languages",
)

CURRICULA = (
    "ncert",
    "cbse",
    "icse",
    "isc",
    "kerala_scert",
    "nios",
    "cambridge",
    "ib",
    "university",
    "professional",
)

ADAPTATIONS = (
    "standard",
    "vocabulary",
    "adhd",
    "autism",
    "dyslexia",
    "ell",
    "visual",
    "auditory",
    "teacher",
    "parent",
    "worksheet",
    "ld",
)

# Engines / packs whose learner-visible contribution must be demonstrated
TRACKED_ENGINES = (
    "KIE",
    "UCF",
    "CEF",
    "CMIF",
    "ULI",
    "SIF",
    "MIP",
    "PIP",
    "CIP",
    "BIP",
    "ELIP",
    "SSIP",
    "CSIP",
    "CEIP",
    "WLIP",
    "UVIE",
    "PQLE",
    "PMES",
    "LCE",
    "ULIQE",
    "EATS",
)

# Visible contribution targets per engine family
ENGINE_VISIBLE_TARGETS: dict[str, tuple[str, ...]] = {
    "KIE": ("verified_claims", "facts", "source"),
    "UCF": ("curriculum", "claim", "objective"),
    "CEF": ("sequence", "concept_hierarchy", "teaching_sequence"),
    "CMIF": ("misconception", "watch out", "correction"),
    "ULI": ("claim_ledger", "universal_profile", "concept"),
    "SIF": ("subject", "assessment", "misconception"),
    "MIP": ("equation", "proof", "mathematics", "solve"),
    "PIP": ("force", "energy", "physics", "diagram"),
    "CIP": ("reaction", "mole", "chemistry", "balance"),
    "BIP": ("cell", "organism", "biology", "process"),
    "ELIP": ("grammar", "reading", "writing", "english"),
    "SSIP": ("history", "geography", "civics", "society"),
    "CSIP": ("algorithm", "code", "computer"),
    "CEIP": ("market", "business", "economics"),
    "WLIP": ("language", "pronunciation", "cognate"),
    "UVIE": ("diagram", "flowchart", "concept_map", "svg", "visual"),
    "PQLE": ("pqle", "publication", "polish"),
    "PMES": ("pmes", "diagram_package", "style_guide", "publisher"),
    "LCE": ("sections", "big_idea", "adaptation", "lce"),
    "ULIQE": ("quality", "uliqe", "gate"),
    "EATS": ("eats", "acceptance", "teachability"),
}

DIFFERENTIATION_MIN = 55.0  # 0–100 Adaptation Differentiation Score
PUBLISHER_MIN = 90.0
VISUAL_MIN = 90.0
GOLDEN_MIN_DELTA = -1.0
RELEASE_PASS_RATE_MIN = 0.95

# Representative topics for the auto-generated benchmark corpus
CORPUS_SEEDS: dict[str, list[dict[str, str]]] = {
    "mathematics": [
        {"topic": "Fractions", "concept": "Equivalent fractions"},
        {"topic": "Linear Equations", "concept": "Solving for x"},
    ],
    "physics": [
        {"topic": "Force and Pressure", "concept": "Pressure"},
        {"topic": "Light", "concept": "Reflection"},
    ],
    "chemistry": [
        {"topic": "Chemical Reactions", "concept": "Balancing equations"},
        {"topic": "Acids and Bases", "concept": "pH"},
    ],
    "biology": [
        {"topic": "The Water Cycle", "concept": "Evaporation"},
        {"topic": "Cell Structure", "concept": "Nucleus"},
    ],
    "english": [
        {"topic": "Active and Passive Voice", "concept": "Voice"},
        {"topic": "Reading Comprehension", "concept": "Inference"},
    ],
    "history": [
        {"topic": "The Freedom Struggle", "concept": "Non-cooperation"},
        {"topic": "Ancient Civilisations", "concept": "Harappa"},
    ],
    "geography": [
        {"topic": "Climate", "concept": "Monsoon"},
        {"topic": "Resources", "concept": "Renewable resources"},
    ],
    "civics": [
        {"topic": "Democracy", "concept": "Fundamental rights"},
        {"topic": "Local Government", "concept": "Panchayat"},
    ],
    "economics": [
        {"topic": "Demand and Supply", "concept": "Equilibrium"},
        {"topic": "Money and Banking", "concept": "Credit"},
    ],
    "business_studies": [
        {"topic": "Forms of Business", "concept": "Partnership"},
        {"topic": "Marketing", "concept": "Product mix"},
    ],
    "computer_science": [
        {"topic": "Algorithms", "concept": "Flowcharts"},
        {"topic": "Python Basics", "concept": "Variables"},
    ],
    "world_languages": [
        {"topic": "Greetings", "concept": "Formal address"},
        {"topic": "Family Vocabulary", "concept": "Cognates"},
    ],
}
