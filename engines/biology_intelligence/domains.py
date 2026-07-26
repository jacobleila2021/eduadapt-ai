"""Biology domain detection and prerequisite hints (curriculum-agnostic)."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.taxonomy import (
    concept_graph_from_uli as _concept_graph,
    detect_domains as _detect_domains,
    prerequisite_hints as _prerequisite_hints,
)

DOMAIN_MARKERS: dict[str, tuple[str, ...]] = {
    "cell_biology": (
        "cell",
        "organelle",
        "mitochondri",
        "chloroplast",
        "nucleus",
        "membrane",
        "mitosis",
        "meiosis",
        "cytoplasm",
    ),
    "human_biology": (
        "human",
        "digestive",
        "circulatory",
        "respiratory system",
        "nervous system",
        "excretory",
        "skeletal",
        "muscular",
    ),
    "plant_biology": (
        "photosynthesis",
        "plant",
        "xylem",
        "phloem",
        "stomata",
        "chlorophyll",
        "transpiration",
        "root",
        "leaf",
    ),
    "genetics": (
        "gene",
        "allele",
        "dna",
        "rna",
        "chromosome",
        "heredity",
        "inheritance",
        "protein synthesis",
        "genotype",
        "phenotype",
    ),
    "evolution": (
        "evolution",
        "natural selection",
        "adaptation",
        "speciation",
        "fossil",
        "darwin",
    ),
    "ecology": (
        "ecosystem",
        "ecology",
        "food chain",
        "food web",
        "biodiversity",
        "habitat",
        "producer",
        "consumer",
        "decomposer",
        "biome",
    ),
    "microbiology": (
        "bacteria",
        "virus",
        "microbe",
        "fungi",
        "pathogen",
        "antibiotic",
        "microbiology",
    ),
    "anatomy": (
        "anatomy",
        "organ",
        "tissue",
        "structure",
        "labelled diagram",
    ),
    "physiology": (
        "physiology",
        "homeostasis",
        "respiration",
        "digestion",
        "circulation",
        "enzyme",
        "hormone",
    ),
    "taxonomy": (
        "taxonomy",
        "classification",
        "kingdom",
        "phylum",
        "species",
        "binomial",
        "genus",
    ),
    "laboratory": (
        "microscope",
        "specimen",
        "dissection",
        "laboratory",
        "slide",
        "staining",
        "investigation",
        "apparatus",
    ),
    "biotechnology": (
        "biotechnology",
        "genetic engineering",
        "fermentation",
        "cloning",
        "pcr",
        "recombinant",
    ),
}

PREREQ_EDGES: tuple[tuple[str, str], ...] = (
    ("cell_biology", "anatomy"),
    ("cell_biology", "physiology"),
    ("cell_biology", "genetics"),
    ("anatomy", "human_biology"),
    ("physiology", "human_biology"),
    ("cell_biology", "plant_biology"),
    ("genetics", "evolution"),
    ("ecology", "evolution"),
    ("cell_biology", "microbiology"),
    ("genetics", "biotechnology"),
    ("taxonomy", "ecology"),
    ("laboratory", "cell_biology"),
    ("laboratory", "microbiology"),
)


def detect_domains(text: str) -> list[dict[str, Any]]:
    return _detect_domains(text, DOMAIN_MARKERS)


def prerequisite_hints(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _prerequisite_hints(
        domains,
        PREREQ_EDGES,
        provenance="biology_intelligence.domain_prereqs",
    )


def concept_graph_from_uli(uli: Any, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _concept_graph(
        uli,
        domains,
        PREREQ_EDGES,
        domain_node_type="biology_domain",
        provenance="biology_intelligence",
    )
