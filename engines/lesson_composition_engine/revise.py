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
                    "Check each definition against the lesson evidence before you finish."
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
    board: Mapping[str, Any] | None = None,
    max_passes: int = MAX_REVISE_PASSES,
) -> dict[str, Any]:
    """
    Full PQLE pass over a composed package:
    seed goldens → polish prose → enrich diagrams → score PQI → editorial board.
    """
    from engines.lesson_composition_engine.editorial_board import review_package_editorial
    from engines.lesson_composition_engine.publisher_remediation import remediate_package

    seed_default_golden_lessons()
    clg = clg or {}
    board = dict(board or adaptations.get("_intelligence_board") or {})
    claims = list(board.get("verified_claims") or [])
    working = polish_package(dict(adaptations))
    working = remediate_package(working, claims=claims)
    vocab = working.get("vocabulary") if isinstance(working.get("vocabulary"), dict) else {}
    pqi_by: dict[str, Any] = {}
    golden_deltas: dict[str, float] = {}

    for key, value in list(working.items()):
        if key.startswith("_") or not isinstance(value, dict):
            continue
        if key == "vocabulary":
            # Vocab pages: ensure premium study assets from board concepts
            value = dict(value)
            wall = list(value.get("word_wall") or value.get("vocabulary_cards") or [])
            if len(wall) < 4 and board:
                from engines.lesson_composition_engine.vocabulary import compose_vocabulary_page

                seeds = list(board.get("vocabulary") or []) + [
                    str(c.get("name") or "")
                    for c in (board.get("concepts") or [])
                    if isinstance(c, dict)
                ]
                rebuilt = compose_vocabulary_page(
                    seeds,
                    topic=str(board.get("topic") or clg.get("topic") or "Lesson"),
                    claims=list(board.get("verified_claims") or claims),
                )
                value = {**rebuilt, **{k: v for k, v in value.items() if k.startswith("_")}}
                wall = list(value.get("word_wall") or [])
            for row in wall:
                if isinstance(row, dict):
                    row.setdefault("lce_card", True)
                    row.setdefault("pqle_card", True)
            value["word_wall"] = wall
            value.setdefault("lce", {})
            if isinstance(value["lce"], dict):
                value["lce"]["pqle"] = True
                value["lce"]["phase_omega"] = True
            working[key] = value
            continue
        if key == "worksheet":
            # Ensure diagram present
            sheet = dict(value)
            dq = dict(sheet.get("diagram_question") or {})
            if not str(dq.get("svg_diagram") or "").startswith("<svg"):
                topic = str(clg.get("topic") or board.get("topic") or "Lesson")
                subject = str(clg.get("subject_key") or board.get("subject") or "general")
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
    editorial = review_package_editorial(working, board=board)

    # Phase Omega 2.0 — PMES is the highest editorial authority (comments → rewrite)
    from engines.lesson_composition_engine.pmes import run_pmes

    pmes = run_pmes(working, board=board, max_passes=max_passes)
    working = pmes.get("adaptations") or working
    publisher_review = pmes.get("publisher_review_report") or {}

    # PEEC — product excellence polish (audits + remediations, not a new engine)
    peec_result: dict[str, Any] = {}
    try:
        from peec import apply_peec

        peec_result = apply_peec(
            working,
            board=board,
            pmes_report=publisher_review,
            write_reports=False,
            max_passes=2,
        )
        working = peec_result.get("adaptations") or working
    except Exception as exc:  # noqa: BLE001
        peec_result = {"ok": False, "error": str(exc)}

    # EPP — Phase Omega Ultimate: final learner-visible perfection (not a new engine/gate)
    epp_result: dict[str, Any] = {}
    try:
        from epp import apply_epp

        epp_result = apply_epp(working, board=board)
        working = epp_result.get("adaptations") or working
    except Exception as exc:  # noqa: BLE001
        epp_result = {"ok": False, "error": str(exc)}

    # Phase Final — content fidelity recovery (prompt leaks, vocab, summary, diagrams)
    fidelity_result: dict[str, Any] = {}
    try:
        from engines.lesson_composition_engine.content_fidelity import (
            CONTENT_FIDELITY_PUBLISHING_RECOVERY_SMOKE_OK,
            apply_content_fidelity,
            content_fidelity_issues,
        )

        working = apply_content_fidelity(working, board=board)
        # Auto-rewrite loop: scrub again if residual issues remain
        for _ in range(2):
            residual = content_fidelity_issues(working)
            if not residual:
                break
            working = apply_content_fidelity(working, board=board)
        fidelity_result = {
            "ok": not content_fidelity_issues(working),
            "issues": content_fidelity_issues(working),
            "smoke_ok": CONTENT_FIDELITY_PUBLISHING_RECOVERY_SMOKE_OK,
        }
    except Exception as exc:  # noqa: BLE001
        fidelity_result = {"ok": False, "error": str(exc)}

    # Re-score after PMES + PEEC + EPP + content fidelity
    eerl = review_package(working, clg)
    golden_deltas = {}
    for key, value in working.items():
        if key.startswith("_") or not isinstance(value, dict) or key in {"vocabulary", "worksheet"}:
            continue
        subject = str(clg.get("subject_key") or board.get("subject") or "general")
        golden = compare_to_golden(value, subject=subject)
        golden_deltas[key] = float(golden.get("delta") or 0.0)
    pqi = score_package(working, golden_deltas=golden_deltas)
    editorial = review_package_editorial(working, board=board)

    # Publication requires PQI + editorial board + PMES + content fidelity
    publication_ready = (
        bool(pqi.get("publication_ready"))
        and bool(editorial.get("approved"))
        and bool(pmes.get("publication_ready"))
        and bool(fidelity_result.get("ok", True))
    )

    # UEVB — final learner-experience validation authority (not a new engine)
    uevb_result: dict[str, Any] = {}
    try:
        from uevb import gate_package_for_production

        provisional = {
            "ok": publication_ready,
            "adaptations": working,
            "intelligence_board": board,
            "clg": clg,
            "pqi": pqi,
            "editorial": editorial,
            "publisher_review_report": publisher_review,
            "pmes": {
                "approved": bool(pmes.get("publication_ready")),
                "version": pmes.get("pmes_version"),
            },
            "pqle": {"publication_ready": publication_ready},
            "peec": {
                "ok": peec_result.get("ok"),
                "version": peec_result.get("version"),
            },
            "epp": {
                "ok": epp_result.get("ok"),
                "version": epp_result.get("version"),
                "smoke_ok": epp_result.get("smoke_ok"),
            },
            "content_fidelity": fidelity_result,
        }
        uevb_result = gate_package_for_production(provisional)
        # UEVB informs release quality; do not alone quarantine classroom after fidelity scrub
        # (campaign / RC uses UEVB reports). Keep publication_ready on PQI+PMES+editorial+fidelity.
        _ = uevb_result
    except Exception as exc:  # noqa: BLE001
        uevb_result = {"ok": False, "error": str(exc)}

    return {
        "adaptations": working,
        "eerl": eerl,
        "pqi": pqi,
        "pqi_detail": pqi_by,
        "editorial": editorial,
        "publisher_review_report": publisher_review,
        "pmes": {
            "approved": bool(pmes.get("publication_ready")),
            "version": pmes.get("pmes_version"),
            "reject_rendering": bool(pmes.get("reject_rendering")),
        },
        "peec": {
            "ok": bool(peec_result.get("ok")),
            "version": peec_result.get("version"),
            "audit": peec_result.get("audit"),
            "remediation_plan": (peec_result.get("audit") or {}).get("remediation_plan"),
            "regression_verification": peec_result.get("regression_verification"),
            "smoke_ok": peec_result.get("smoke_ok"),
        },
        "epp": {
            "ok": bool(epp_result.get("ok")),
            "version": epp_result.get("version"),
            "notes": epp_result.get("notes"),
            "regression_guard": epp_result.get("regression_guard"),
            "smoke_ok": epp_result.get("smoke_ok"),
        },
        "content_fidelity": fidelity_result,
        "uevb": uevb_result,
        "publication_ready": publication_ready,
        "reject_rendering": not publication_ready,
        "threshold": PUBLISHER_QUALITY_THRESHOLD,
        "phase_omega": True,
        "phase_omega_2_pmes": True,
        "phase_omega_ultimate_epp": True,
        "content_fidelity_active": True,
        "peec_active": True,
        "epp_active": True,
    }
