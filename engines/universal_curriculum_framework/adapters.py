"""Thin consume adapters — engines read UCF without board-specific branches."""

from __future__ import annotations

from typing import Any

from engines.universal_curriculum_framework.curriculum_registry import load_package, list_packages
from engines.universal_curriculum_framework.mapping import ucf_package_to_cie_payload
from engines.universal_curriculum_framework.prerequisites import build_dependency_graph


def for_cie(package_id: str = "") -> dict[str, Any]:
    pkg = _resolve(package_id)
    if not pkg:
        return {"ok": False, "concepts": [], "source": "ucf"}
    return {"ok": True, **ucf_package_to_cie_payload(pkg), "source": "ucf"}


def for_ame(package_id: str = "") -> dict[str, Any]:
    pkg = _resolve(package_id)
    if not pkg:
        return {"ok": False, "assessment_items": []}
    items = []
    for q in pkg.get("questions") or []:
        items.append(
            {
                "question_id": q.get("question_id"),
                "official": q.get("official", True),
                "competency_ids": q.get("competency_ids") or [],
                "bloom": q.get("bloom"),
                "dok": q.get("dok"),
                "difficulty": q.get("difficulty"),
            }
        )
    return {"ok": True, "assessment_items": items, "policy": "official_preferred", "source": "ucf"}


def for_ale(package_id: str = "") -> dict[str, Any]:
    pkg = _resolve(package_id)
    if not pkg:
        return {"ok": False, "prerequisite_graph": {}}
    return {"ok": True, "prerequisite_graph": build_dependency_graph(pkg), "source": "ucf"}


def for_aie(package_id: str = "") -> dict[str, Any]:
    pkg = _resolve(package_id)
    if not pkg:
        return {"ok": False, "accessibility": []}
    rows = []
    for t in pkg.get("topics") or []:
        rows.append({"topic_id": t.get("topic_id"), **(t.get("accessibility") or {})})
    return {"ok": True, "accessibility": rows, "source": "ucf"}


def for_atie(package_id: str = "", topic_id: str = "") -> dict[str, Any]:
    pkg = _resolve(package_id)
    if not pkg:
        return {"ok": False, "concepts": []}
    topics = pkg.get("topics") or []
    if topic_id:
        topics = [t for t in topics if t.get("topic_id") == topic_id]
    return {
        "ok": True,
        "verified_concepts": [
            {
                "topic_id": t.get("topic_id"),
                "title": t.get("title"),
                "objectives": t.get("objectives"),
                "misconceptions": (t.get("objectives") or {}).get("misconceptions") or [],
            }
            for t in topics
        ],
        "source": "ucf",
        "policy": "retrieve_verified_only",
    }


def for_vmle(package_id: str = "", topic_id: str = "") -> dict[str, Any]:
    atie = for_atie(package_id, topic_id)
    narration_bits = []
    for c in atie.get("verified_concepts") or []:
        knowledge = ((c.get("objectives") or {}).get("knowledge") or [])
        narration_bits.append({"title": c.get("title"), "text": " ".join(knowledge)})
    return {"ok": True, "narration_objects": narration_bits, "source": "ucf"}


def for_alcis(package_id: str = "") -> dict[str, Any]:
    cie = for_cie(package_id)
    comps = []
    for c in cie.get("competencies") or []:
        if isinstance(c, dict):
            comps.append(c.get("competency_id") or c.get("description"))
    return {"ok": True, "competency_ids": comps, "celebrate_on_mastery": True, "source": "ucf"}


def for_lmas(package_id: str = "") -> dict[str, Any]:
    """Skill-tree nodes from UCF competencies / topics."""
    pkg = _resolve(package_id)
    if not pkg:
        return {"ok": False, "concepts": []}
    concepts = []
    for t in pkg.get("topics") or []:
        source = t.get("source_labels") or {}
        cid = source.get("cie_concept_id") or t.get("topic_id")
        concepts.append(
            {
                "id": cid,
                "title": t.get("title"),
                "prerequisites": (t.get("prerequisites") or {}).get("previous_concepts") or [],
            }
        )
    return {"ok": True, "concepts": concepts, "source": "ucf"}


def for_laie(package_id: str = "") -> dict[str, Any]:
    cie = for_cie(package_id)
    return {
        "ok": True,
        "universal_competencies": cie.get("competencies") or [],
        "concept_count": len(cie.get("concepts") or []),
        "source": "ucf",
    }


def for_kie_emit_hint() -> dict[str, Any]:
    return {"output_target": "ucf", "importer": "kie_package", "wrap_existing_knowledge_package": True}


def _resolve(package_id: str) -> dict[str, Any] | None:
    if package_id:
        return load_package(package_id)
    pkgs = list_packages()
    if not pkgs:
        return None
    return load_package(pkgs[0]["package_id"])
