"""Chemistry misconception library — pattern detection only; no invented curriculum."""

from __future__ import annotations

from typing import Any

CHEMISTRY_MISCONCEPTIONS: tuple[dict[str, Any], ...] = (
    {
        "misconception_id": "chem.atom_vs_molecule",
        "label": "Atom and molecule treated as identical",
        "domain": "atomic_structure",
        "patterns": [
            r"atom\s*(is\s*)?(the\s*)?same\s*as\s*molecule",
            r"molecules?\s*are\s*atoms",
            r"o2\s*is\s*an?\s*atom",
        ],
        "correction": "Atoms are single elements' particles; molecules are bonded groups of atoms (e.g. O₂).",
        "related_concepts": ["atom", "molecule", "element"],
    },
    {
        "misconception_id": "chem.compound_vs_mixture",
        "label": "Compound and mixture conflated",
        "domain": "inorganic",
        "patterns": [
            r"compound\s*(is\s*)?(the\s*)?same\s*as\s*mixture",
            r"mixtures?\s*have\s*fixed\s*formula",
            r"air\s*is\s*a\s*compound",
        ],
        "correction": "Compounds have fixed composition and chemical bonding; mixtures can vary and are physically separable.",
        "related_concepts": ["compound", "mixture", "pure_substance"],
    },
    {
        "misconception_id": "chem.physical_vs_chemical",
        "label": "Physical and chemical change confused",
        "domain": "reactions",
        "patterns": [
            r"melting\s*is\s*a\s*chemical\s*change",
            r"burning\s*is\s*only\s*physical",
            r"physical\s*change\s*makes\s*new\s*substance",
        ],
        "correction": "Chemical change forms new substances; physical change alters form/state without new substances.",
        "related_concepts": ["physical_change", "chemical_change"],
    },
    {
        "misconception_id": "chem.mass_vs_moles",
        "label": "Mass and moles treated interchangeably",
        "domain": "stoichiometry",
        "patterns": [
            r"moles?\s*(is\s*)?(the\s*)?same\s*as\s*mass",
            r"more\s*grams\s*means\s*more\s*moles\s*always",
            r"ignore\s*molar\s*mass",
        ],
        "correction": "n = m/M; equal masses of different substances are not equal moles.",
        "related_concepts": ["mole", "molar_mass", "stoichiometry"],
    },
    {
        "misconception_id": "chem.ionic_vs_covalent",
        "label": "Ionic and covalent bonding swapped or oversimplified",
        "domain": "chemical_bonding",
        "patterns": [
            r"all\s*compounds?\s*are\s*ionic",
            r"covalent\s*bonds?\s*transfer\s*electrons",
            r"ionic\s*bonds?\s*share\s*electrons",
        ],
        "correction": "Ionic: electron transfer / electrostatic attraction; covalent: shared electron pairs.",
        "related_concepts": ["ionic_bonding", "covalent_bonding"],
    },
    {
        "misconception_id": "chem.concentration_vs_amount",
        "label": "Concentration confused with amount of substance",
        "domain": "stoichiometry",
        "patterns": [
            r"concentration\s*(is\s*)?(the\s*)?same\s*as\s*(amount|moles)",
            r"more\s*concentrated\s*means\s*more\s*volume",
            r"dilute\s*means\s*weak\s*always",
        ],
        "correction": "Concentration is amount per volume (e.g. mol/L); amount is moles — dilute ≠ necessarily weak acid.",
        "related_concepts": ["concentration", "mole", "molarity"],
    },
    {
        "misconception_id": "chem.strong_vs_concentrated",
        "label": "Strong acid equated with concentrated acid",
        "domain": "acids_bases",
        "patterns": [
            r"strong\s+acid\s+(is\s+)?(the\s+)?same\s+as\s+(a\s+)?concentrated",
            r"concentrated\s+means\s+strong",
            r"dilute\s+acid\s+cannot\s+be\s+strong",
        ],
        "correction": "Strength = degree of dissociation; concentration = how much solute per volume.",
        "related_concepts": ["acid_strength", "concentration"],
    },
    {
        "misconception_id": "chem.oxidation_vs_reduction",
        "label": "Oxidation and reduction definitions reversed",
        "domain": "electrochemistry",
        "patterns": [
            r"oxidation\s*(is\s*)?gain\s*of\s*electrons",
            r"reduction\s*(is\s*)?loss\s*of\s*electrons",
            r"oil\s*rig\s*reversed",
        ],
        "correction": "Oxidation is loss of electrons; reduction is gain (OIL RIG).",
        "related_concepts": ["oxidation", "reduction", "redox"],
    },
    {
        "misconception_id": "chem.heat_vs_temperature",
        "label": "Heat and temperature treated as the same",
        "domain": "thermochemistry",
        "patterns": [
            r"heat\s*(is\s*)?(the\s*)?same\s*as\s*temperature",
            r"temperature\s*flows",
            r"hotter\s*always\s*more\s*heat\s*content",
        ],
        "correction": "Temperature is average kinetic energy measure; heat is energy transfer.",
        "related_concepts": ["heat", "temperature", "enthalpy"],
    },
    {
        "misconception_id": "chem.catalyst_consumed",
        "label": "Catalysts thought to be consumed or change ΔH",
        "domain": "kinetics",
        "patterns": [
            r"catalyst\s*(is\s*)?used\s*up",
            r"catalyst\s*changes?\s*(the\s*)?enthalpy",
            r"catalyst\s*makes?\s*reaction\s*more\s*exothermic",
        ],
        "correction": "Catalysts provide an alternative path with lower Ea; they are not consumed and do not change overall ΔH.",
        "related_concepts": ["catalyst", "activation_energy", "kinetics"],
    },
)


def detect_chemistry_misconceptions(text: str, *, limit: int = 12) -> list[dict[str, Any]]:
    from engines.subject_intelligence_core.misconceptions import detect_from_catalogue

    return detect_from_catalogue(
        CHEMISTRY_MISCONCEPTIONS,
        text,
        provenance="chemistry_intelligence.misconceptions",
        limit=limit,
    )
