"""Biology misconception library — pattern detection only; no invented curriculum."""

from __future__ import annotations

from typing import Any

BIOLOGY_MISCONCEPTIONS: tuple[dict[str, Any], ...] = (
    {
        "misconception_id": "bio.plant_resp_vs_photo",
        "label": "Plants only photosynthesise; do not respire",
        "domain": "plant_biology",
        "patterns": [
            r"plants?\s*(do\s*not|don't)\s*respir",
            r"photosynthesis\s*(is\s*)?(the\s*)?same\s*as\s*respiration",
            r"plants?\s*only\s*make\s*oxygen",
        ],
        "correction": "Plants photosynthesise and respire; photosynthesis stores energy, respiration releases it.",
        "related_concepts": ["photosynthesis", "respiration"],
    },
    {
        "misconception_id": "bio.mitosis_vs_meiosis",
        "label": "Mitosis and meiosis conflated",
        "domain": "cell_biology",
        "patterns": [
            r"mitosis\s*(is\s*)?(the\s*)?same\s*as\s*meiosis",
            r"meiosis\s*makes?\s*identical\s*body\s*cells",
            r"mitosis\s*halves?\s*chromosome\s*number",
        ],
        "correction": "Mitosis → identical somatic cells; meiosis → gametes with halved chromosome number and variation.",
        "related_concepts": ["mitosis", "meiosis", "cell_division"],
    },
    {
        "misconception_id": "bio.dna_vs_chromosomes",
        "label": "DNA and chromosomes treated as identical",
        "domain": "genetics",
        "patterns": [
            r"dna\s*(is\s*)?(the\s*)?same\s*as\s*chromosome",
            r"chromosomes?\s*are\s*just\s*dna\s*words",
            r"one\s*gene\s*=\s*one\s*chromosome",
        ],
        "correction": "DNA is the molecule; chromosomes are DNA packaged with proteins; genes are segments of DNA.",
        "related_concepts": ["dna", "chromosome", "gene"],
    },
    {
        "misconception_id": "bio.genes_vs_traits",
        "label": "Genes and traits equated one-to-one without nuance",
        "domain": "genetics",
        "patterns": [
            r"one\s*gene\s*(always\s*)?(equals|=)\s*one\s*trait",
            r"traits?\s*(are\s*)?(the\s*)?same\s*as\s*genes",
            r"environment\s*never\s*affects\s*traits",
        ],
        "correction": "Traits arise from genes interacting with each other and the environment; inheritance is not always one-gene-one-trait.",
        "related_concepts": ["gene", "trait", "phenotype"],
    },
    {
        "misconception_id": "bio.cells_vs_tissues",
        "label": "Cells and tissues confused",
        "domain": "anatomy",
        "patterns": [
            r"cell\s*(is\s*)?(the\s*)?same\s*as\s*tissue",
            r"tissues?\s*are\s*single\s*cells",
            r"organs?\s*are\s*made\s*of\s*one\s*cell",
        ],
        "correction": "Cells → tissues (groups of similar cells) → organs → systems.",
        "related_concepts": ["cell", "tissue", "organ"],
    },
    {
        "misconception_id": "bio.adaptation_vs_evolution",
        "label": "Individual adaptation equated with evolution",
        "domain": "evolution",
        "patterns": [
            r"animals?\s*choose\s*to\s*adapt",
            r"adaptation\s*(is\s*)?(the\s*)?same\s*as\s*evolution",
            r"individuals?\s*evolve\s*during\s*(their\s*)?lifetime",
        ],
        "correction": "Individuals do not evolve; populations change over generations via selection on heritable variation.",
        "related_concepts": ["adaptation", "evolution", "natural_selection"],
    },
    {
        "misconception_id": "bio.food_chain_vs_web",
        "label": "Food chain and food web treated as identical",
        "domain": "ecology",
        "patterns": [
            r"food\s*chain\s*(is\s*)?(the\s*)?same\s*as\s*food\s*web",
            r"ecosystems?\s*have\s*only\s*one\s*food\s*chain",
        ],
        "correction": "A food chain is one pathway; a food web is interconnected feeding relationships.",
        "related_concepts": ["food_chain", "food_web", "ecosystem"],
    },
    {
        "misconception_id": "bio.respiration_vs_breathing",
        "label": "Respiration equated with breathing",
        "domain": "physiology",
        "patterns": [
            r"respiration\s*(is\s*)?(the\s*)?same\s*as\s*breathing",
            r"breathing\s*(is\s*)?cellular\s*respiration",
            r"plants?\s*do\s*not\s*respir\s*because\s*they\s*don.?t\s*breathe",
        ],
        "correction": "Breathing/ventilation moves gases; cellular respiration releases energy from food in cells.",
        "related_concepts": ["respiration", "breathing", "gas_exchange"],
    },
    {
        "misconception_id": "bio.osmosis_vs_diffusion",
        "label": "Osmosis and diffusion conflated",
        "domain": "cell_biology",
        "patterns": [
            r"osmosis\s*(is\s*)?(the\s*)?same\s*as\s*diffusion",
            r"diffusion\s*only\s*happens\s*with\s*water",
            r"osmosis\s*moves\s*any\s*solute",
        ],
        "correction": "Diffusion is net movement of particles; osmosis is water movement across a selectively permeable membrane.",
        "related_concepts": ["osmosis", "diffusion", "membrane"],
    },
    {
        "misconception_id": "bio.producers_vs_consumers",
        "label": "Producers and consumers roles confused",
        "domain": "ecology",
        "patterns": [
            r"animals?\s*are\s*producers",
            r"plants?\s*are\s*consumers",
            r"producers?\s*eat\s*consumers",
        ],
        "correction": "Producers make organic matter (usually via photosynthesis); consumers obtain energy by feeding.",
        "related_concepts": ["producer", "consumer", "trophic_level"],
    },
)


def detect_biology_misconceptions(text: str, *, limit: int = 12) -> list[dict[str, Any]]:
    from engines.subject_intelligence_core.misconceptions import detect_from_catalogue

    return detect_from_catalogue(
        BIOLOGY_MISCONCEPTIONS,
        text,
        provenance="biology_intelligence.misconceptions",
        limit=limit,
    )
