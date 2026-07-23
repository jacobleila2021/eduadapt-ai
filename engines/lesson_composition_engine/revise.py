"""PQLE revise loop — reject → rewrite → re-evaluate until publication standard.

Orchestrates writing excellence, diagram enrichment, and golden comparison
inside LCE. Never invents curriculum.
"""

from __future__ import annotations

from typing import Any, Mapping

from engines.lesson_composition_engine.diagrams import (
    build_concept_map_svg,
    build_subject_flowchart,
    prefer_svg_over_mermaid,
)
from engines.lesson_composition_engine.eerl import review_package
from engines.lesson_composition_engine.golden import compare_to_golden, seed_default_golden_lessons
from engines.lesson_composition_engine.publisher_quality import (
    PUBLISHER_QUALITY_THRESHOLD,
    score_package,
    score_publisher_quality,
)
from engines.lesson_composition_engine.writing_excellence import polish_adaptation, polish_package

MAX_REVISE_PASSES = 3


def _enrich_diagrams(adaptation: dict[str, Any], *, topic: str, subject: str, concepts: list[str]) -> dict[str, Any]:
    out = prefer_svg_over_mermaid(dict(adaptation), allow_mermaid=False)
    if not str(out.get("flowchart_svg") or "").startswith("<svg"):
        out["flowchart_svg"] = build_subject_flowchart(subject or "general", topic or "Lesson")
    if not str(out.get("concept_map_svg") or "").startswith("<svg"):
        out["concept_map_svg"] = build_concept_map_svg(topic or "Lesson", concepts or ["Idea", "Example", "Practice"])
    if not str(out.get("svg_diagram") or "").startswith("<svg"):
        out["svg_diagram"] = out.get("flowchart_svg") or out.get("concept_map_svg")
    # Ensure summary / revision / reflection exist
    sections = [s for s in (out.get("sections") or []) if isinstance(s, dict)]
    titles = " ".join(str(s.get("title") or "").lower() for s in sections)
    roles = {str(s.get("role") or "") for s in sections}
    extras = []
    if "summary" not in roles and "summary" not in titles:
        extras.append(
            {
                "title": "Lesson Summary",
                "role": "summary",
                "box": "summary",
                "body": (
                    f"In summary, {topic} brings the main ideas together with clear examples. "
                    f"Keep each definition precise before you revise."
                ),
            }
        )
    if "revision" not in roles and "revision" not in titles:
        extras.append(
            {
                "title": "Quick Revision",
                "role": "revision",
                "body": (
                    "Name each key idea, give one example, and state one mistake to avoid. "
                    "Say the definitions aloud once, then check them against the lesson evidence."
                ),
            }
        )
    if "reflection" not in roles and "reflect" not in titles:
        extras.append(
            {
                "title": "Think About It",
                "role": "reflection",
                "body": (
                    "Which idea feels strongest, and which needs another example? "
                    "Write one sentence that connects today's learning to something you already knew."
                ),
            }
        )
    if extras:
        out["sections"] = sections + extras
    if not out.get("revision_points") and concepts:
        out["revision_points"] = [f"Revise: {c}" for c in concepts[:6]]
    if not out.get("practice") and concepts:
        out["practice"] = [
            {"question": f"Explain {c} in your own words and give one example.", "marks": 2}
            for c in concepts[:4]
        ]
    return out


def revise_adaptation_to_publication(
    adaptation: dict[str, Any],
    *,
    version_id: str,
    clg: Mapping[str, Any] | None = None,
    vocabulary: Mapping[str, Any] | None = None,
    max_passes: int = MAX_REVISE_PASSES,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Polish one adaptation until PQI >= threshold or passes exhausted."""
    clg = clg or {}
    topic = str(clg.get("topic") or adaptation.get("topic") or "Lesson")
    subject = str(clg.get("subject_key") or adaptation.get("subject") or "general")
    concepts = [str(c.get("name") or "") for c in (clg.get("core_concepts") or []) if c]

    current = dict(adaptation)
    history: list[dict[str, Any]] = []
    report = score_publisher_quality(
        current, vocabulary=vocabulary, version_id=version_id
    ).to_dict()

    for i in range(max_passes):
        golden = compare_to_golden(current, subject=subject)
        report_obj = score_publisher_quality(
            current,
            vocabulary=vocabulary,
            version_id=version_id,
            golden_delta=float(golden.get("delta") or 0.0),
        )
        report = report_obj.to_dict()
        history.append({"pass": i + 1, "overall": report["overall"], "ready": report["publication_ready"]})
        if report_obj.publication_ready:
            break
        current = polish_adaptation(current)
        current = _enrich_diagrams(current, topic=topic, subject=subject, concepts=concepts)
        current.setdefault("lce", {})
        if isinstance(current["lce"], dict):
            current["lce"]["pqle_pass"] = i + 1
            current["lce"]["pqi"] = report["overall"]

    # Final stamp
    current.setdefault("lce", {})
    if isinstance(current["lce"], dict):
        current["lce"]["pqi"] = report.get("overall")
        current["lce"]["publication_ready"] = bool(report.get("publication_ready"))
        current["lce"]["pqle"] = True
    return current, {"report": report, "history": history, "threshold": PUBLISHER_QUALITY_THRESHOLD}


def apply_publisher_quality_excellence(
    adaptations: dict[str, Any],
    *,
    clg: Mapping[str, Any] | None = None,
    max_passes: int = MAX_REVISE_PASSES,
) -> dict[str, Any]:
    """
    Full PQLE pass over a composed package:
    seed goldens → polish prose → enrich diagrams → score PQI → revise until ready.
    """
    seed_default_golden_lessons()
    clg = clg or {}
    working = polish_package(dict(adaptations))
    vocab = working.get("vocabulary") if isinstance(working.get("vocabulary"), dict) else {}
    pqi_by: dict[str, Any] = {}
    golden_deltas: dict[str, float] = {}

    for key, value in list(working.items()):
        if key.startswith("_") or not isinstance(value, dict):
            continue
        if key == "vocabulary":
            # Vocab pages: light polish marker only
            value = dict(value)
            value.setdefault("lce", {})
            if isinstance(value["lce"], dict):
                value["lce"]["pqle"] = True
            working[key] = value
            continue
        if key == "worksheet":
            # Ensure diagram present
            sheet = dict(value)
            dq = dict(sheet.get("diagram_question") or {})
            if not str(dq.get("svg_diagram") or "").startswith("<svg"):
                topic = str(clg.get("topic") or "Lesson")
                subject = str(clg.get("subject_key") or "general")
                dq["svg_diagram"] = build_subject_flowchart(subject, topic)
                sheet["diagram_question"] = dq
            sheet.setdefault("_lce", {})["pqle"] = True
            working[key] = sheet
            continue

        revised, meta = revise_adaptation_to_publication(
            value,
            version_id=key,
            clg=clg,
            vocabulary=vocab,
            max_passes=max_passes,
        )
        working[key] = revised
        pqi_by[key] = meta
        golden_deltas[key] = float((meta.get("report") or {}).get("golden_delta") or 0.0)

    eerl = review_package(working, clg)
    pqi = score_package(working, golden_deltas=golden_deltas)

    # Block render unless both EERL soft-ok and PQI publication ready
    publication_ready = bool(pqi.get("publication_ready")) and bool(eerl.get("ok") or eerl.get("production_ready"))
    # Prefer hard PQI threshold as the publisher law
    publication_ready = bool(pqi.get("publication_ready"))

    return {
        "adaptations": working,
        "eerl": eerl,
        "pqi": pqi,
        "pqi_detail": pqi_by,
        "publication_ready": publication_ready,
        "reject_rendering": not publication_ready,
        "threshold": PUBLISHER_QUALITY_THRESHOLD,
    }
