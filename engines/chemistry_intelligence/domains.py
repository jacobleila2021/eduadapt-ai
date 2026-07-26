"""Chemistry domain detection and prerequisite hints (curriculum-agnostic)."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.taxonomy import (
    concept_graph_from_uli as _concept_graph,
    detect_domains as _detect_domains,
    prerequisite_hints as _prerequisite_hints,
)

DOMAIN_MARKERS: dict[str, tuple[str, ...]] = {
    "atomic_structure": ("atomic structure", "electron", "proton", "neutron", "shell", "orbital", "electronic configuration"),
    "periodic_table": ("periodic table", "periodic trend", "group", "period", "atomic number", "electronegativity"),
    "chemical_bonding": ("ionic bond", "covalent", "metallic bond", "lewis", "valence", "hybridization", "molecular geometry"),
    "reactions": ("chemical reaction", "reactant", "product", "precipitation", "displacement", "combustion", "decomposition"),
    "stoichiometry": ("mole", "molar mass", "stoichiometr", "limiting reagent", "avogadro", "empirical formula"),
    "acids_bases": ("acid", "base", "ph", "neutrali", "alkali", "indicator", "bronsted", "arrhenius"),
    "organic": ("organic", "hydrocarbon", "functional group", "alkane", "alkene", "alcohol", "isomer"),
    "inorganic": ("inorganic", "salt", "oxide", "carbonate", "sulphate", "sulfate", "nitrate"),
    "electrochemistry": ("electrolysis", "electrode", "anode", "cathode", "redox", "oxidation", "reduction", "galvanic"),
    "thermochemistry": ("enthalpy", "exothermic", "endothermic", "heat of reaction", "calorimetr"),
    "kinetics": ("rate of reaction", "activation energy", "catalyst", "collision theory", "kinetics"),
    "equilibrium": ("equilibrium", "le chatelier", "kc", "kp", "reversible reaction"),
    "laboratory": ("apparatus", "titration", "bunsen", "pipette", "burette", "safety", "hazard", "lab"),
}

PREREQ_EDGES: tuple[tuple[str, str], ...] = (
    ("atomic_structure", "periodic_table"),
    ("atomic_structure", "chemical_bonding"),
    ("periodic_table", "chemical_bonding"),
    ("chemical_bonding", "reactions"),
    ("reactions", "stoichiometry"),
    ("atomic_structure", "stoichiometry"),
    ("reactions", "acids_bases"),
    ("reactions", "electrochemistry"),
    ("stoichiometry", "thermochemistry"),
    ("reactions", "kinetics"),
    ("reactions", "equilibrium"),
    ("chemical_bonding", "organic"),
    ("reactions", "inorganic"),
    ("laboratory", "acids_bases"),
    ("laboratory", "stoichiometry"),
)


def detect_domains(text: str) -> list[dict[str, Any]]:
    return _detect_domains(text, DOMAIN_MARKERS)


def prerequisite_hints(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _prerequisite_hints(
        domains,
        PREREQ_EDGES,
        provenance="chemistry_intelligence.domain_prereqs",
    )


def concept_graph_from_uli(uli: Any, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _concept_graph(
        uli,
        domains,
        PREREQ_EDGES,
        domain_node_type="chemistry_domain",
        provenance="chemistry_intelligence",
    )
