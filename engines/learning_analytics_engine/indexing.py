"""LAIE Chroma — metrics catalogue indexing (structured state remains JSON)."""

from __future__ import annotations

from typing import Any

from knowledge.paths import CHROMA_DIR

from engines.learning_analytics_engine.schemas import ALERT_TYPES, ROLES

LAIE_COLLECTIONS = {
    "metrics_catalog": "laie_metrics_catalog",
    "alert_types": "laie_alert_types",
    "roles": "laie_roles",
}

METRICS_CATALOG = [
    ("mastery_growth", "AME mastery band changes over time"),
    ("curriculum_coverage", "CIE concept/outcome coverage"),
    ("exam_readiness", "AME readiness score"),
    ("accessibility_adoption", "AIE profile and support usage"),
    ("engagement_consistency", "Completion rate and streaks"),
    ("intervention_success", "Pre/post mastery after interventions"),
    ("risk_of_falling_behind", "ALE/LAIE predictive risk"),
    ("reading_complexity", "analytics_engine complexity score"),
]


def rebuild_laie_index() -> dict[str, Any]:
    status: dict[str, Any] = {"ok": True, "collections": {}}
    try:
        import chromadb

        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "warning": str(exc), "collections": {}}

    def upsert(name: str, ids: list[str], docs: list[str], metas: list[dict]) -> dict[str, Any]:
        try:
            col = client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})
            clean = [
                {k: (v if isinstance(v, (str, int, float, bool)) else str(v)) for k, v in m.items()}
                for m in metas
            ]
            col.upsert(ids=ids, documents=docs, metadatas=clean)
            return {"collection": name, "count": len(ids), "ok": True}
        except Exception as exc:  # noqa: BLE001
            return {"collection": name, "ok": False, "error": str(exc)}

    ids = [m[0] for m in METRICS_CATALOG]
    docs = [f"{m[0]}: {m[1]}" for m in METRICS_CATALOG]
    metas = [{"metric": m[0]} for m in METRICS_CATALOG]
    status["collections"]["metrics_catalog"] = upsert(LAIE_COLLECTIONS["metrics_catalog"], ids, docs, metas)
    status["collections"]["alert_types"] = upsert(
        LAIE_COLLECTIONS["alert_types"],
        list(ALERT_TYPES),
        [f"Alert: {a}" for a in ALERT_TYPES],
        [{"alert_type": a} for a in ALERT_TYPES],
    )
    status["collections"]["roles"] = upsert(
        LAIE_COLLECTIONS["roles"],
        list(ROLES),
        [f"Dashboard role: {r}" for r in ROLES],
        [{"role": r} for r in ROLES],
    )
    return status
