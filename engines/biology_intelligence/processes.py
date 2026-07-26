"""Biological process / systems metadata (LXP/VMLE render)."""

from __future__ import annotations

from typing import Any

from engines.biology_intelligence.domains import detect_domains

PROCESS_CATALOGUE: dict[str, list[dict[str, str]]] = {
    "cell_biology": [
        {"process_id": "cell_division_mitosis", "label": "Mitosis"},
        {"process_id": "cell_division_meiosis", "label": "Meiosis"},
        {"process_id": "membrane_transport", "label": "Membrane transport"},
    ],
    "plant_biology": [
        {"process_id": "photosynthesis", "label": "Photosynthesis"},
        {"process_id": "plant_respiration", "label": "Plant respiration"},
        {"process_id": "transpiration", "label": "Transpiration"},
        {"process_id": "life_cycle_plant", "label": "Plant life cycle"},
    ],
    "physiology": [
        {"process_id": "cellular_respiration", "label": "Cellular respiration"},
        {"process_id": "digestion", "label": "Digestion"},
        {"process_id": "gas_exchange", "label": "Gas exchange"},
        {"process_id": "homeostasis", "label": "Homeostasis"},
    ],
    "human_biology": [
        {"process_id": "body_system_integration", "label": "Body system interactions"},
        {"process_id": "life_cycle_human", "label": "Human life cycle"},
    ],
    "genetics": [
        {"process_id": "genetic_inheritance", "label": "Genetic inheritance"},
        {"process_id": "protein_synthesis", "label": "Protein synthesis"},
        {"process_id": "dna_replication", "label": "DNA replication"},
    ],
    "ecology": [
        {"process_id": "food_web_interactions", "label": "Ecological interactions"},
        {"process_id": "energy_flow", "label": "Energy flow"},
        {"process_id": "nutrient_cycles", "label": "Nutrient cycles"},
    ],
    "evolution": [
        {"process_id": "evolutionary_relationships", "label": "Evolutionary relationships"},
        {"process_id": "natural_selection", "label": "Natural selection"},
    ],
}


def build_process_metadata(text: str, domains: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    domains = domains if domains is not None else detect_domains(text)
    processes: list[dict[str, Any]] = []
    seen: set[str] = set()
    blob = (text or "").lower()
    for d in domains:
        for proc in PROCESS_CATALOGUE.get(d["domain"], []):
            pid = proc["process_id"]
            # Prefer processes whose keywords appear, else include top domain defaults
            key_tok = pid.split("_")[0]
            if pid in seen:
                continue
            if key_tok in blob or any(m in blob for m in d.get("markers") or []):
                seen.add(pid)
                processes.append({**proc, "domain": d["domain"], "renderer": "lxp_or_vmle"})
    if not processes and domains:
        for proc in PROCESS_CATALOGUE.get(domains[0]["domain"], [])[:3]:
            processes.append({**proc, "domain": domains[0]["domain"], "renderer": "lxp_or_vmle"})
    return {
        "processes": processes,
        "frameworks": ["systems_thinking", "structure_function", "cause_effect", "concept_mapping"],
        "provenance": "biology_intelligence.processes",
    }
