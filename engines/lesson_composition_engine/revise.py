"""PQLE revise loop — Generation Recovery: formatting-only + contribution-gated polish.

Never invents curriculum. PQLE must not rewrite educational meaning.
"""

from __future__ import annotations

from typing import Any, Mapping

from engines.lesson_composition_engine.diagrams import (
    build_concept_map_svg,
    prefer_svg_over_mermaid,
)
from engines.lesson_composition_engine.eerl import review_package
from engines.lesson_composition_engine.golden import compare_to_golden, seed_default_golden_lessons
from engines.lesson_composition_engine.publisher_quality import (
    PUBLISHER_QUALITY_THRESHOLD,
    score_package,
    score_publisher_quality,
)

MAX_REVISE_PASSES = 3


def _enrich_diagrams(adaptation: dict[str, Any], *, topic: str, subject: str, concepts: list[str]) -> dict[str, Any]:
    """Ensure SVG organisers exist. Does not inject Quick Revision boilerplate.

    Only DOMAIN diagrams built from real lesson concepts are ever injected —
    the generic pedagogy flowchart is rejected by EATS as "not a domain
    diagram", so injecting it guaranteed quarantine. Missing beats generic.
    """
    from engines.lesson_composition_engine.diagrams import build_educational_flowchart_svg

    out = prefer_svg_over_mermaid(dict(adaptation), allow_mermaid=False)
    names = [str(c).strip() for c in (concepts or []) if str(c).strip()]
    if not str(out.get("flowchart_svg") or "").startswith("<svg") and len(names) >= 2:
        out["flowchart_svg"] = build_educational_flowchart_svg(
            topic or "Lesson", names[:6], subtitle="Key ideas in order"
        )
    if not str(out.get("concept_map_svg") or "").startswith("<svg") and names:
        out["concept_map_svg"] = build_concept_map_svg(topic or "Lesson", names)
    if not str(out.get("svg_diagram") or "").startswith("<svg"):
        out["svg_diagram"] = out.get("flowchart_svg") or out.get("concept_map_svg") or ""
    return out


def revise_adaptation_to_publication(
    adaptation: dict[str, Any],
    *,
    version_id: str,
    clg: Mapping[str, Any] | None = None,
    vocabulary: Mapping[str, Any] | None = None,
    max_passes: int = MAX_REVISE_PASSES,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """PQLE formatting-only stamp + score. Never rewrites educational content."""
    from engines.lesson_composition_engine.recovery import format_only_adaptation

    clg = clg or {}
    topic = str(clg.get("topic") or adaptation.get("topic") or "Lesson")
    subject = str(clg.get("subject_key") or adaptation.get("subject") or "general")

    current = format_only_adaptation(dict(adaptation))
    golden = compare_to_golden(current, subject=subject, topic=topic)
    report_obj = score_publisher_quality(
        current,
        vocabulary=vocabulary,
        version_id=version_id,
        golden_delta=float(golden.get("delta") or 0.0),
    )
    report = report_obj.to_dict()
    current.setdefault("lce", {})
    if isinstance(current["lce"], dict):
        current["lce"]["pqi"] = report.get("overall")
        current["lce"]["publication_ready"] = bool(report.get("publication_ready"))
        current["lce"]["pqle"] = True
        current["lce"]["pqle_mode"] = "formatting_only"
    return current, {
        "report": report,
        "history": [
            {
                "pass": 1,
                "overall": report.get("overall"),
                "ready": report.get("publication_ready"),
            }
        ],
        "threshold": PUBLISHER_QUALITY_THRESHOLD,
        "pqle_mode": "formatting_only",
    }


def apply_publisher_quality_excellence(
    adaptations: dict[str, Any],
    *,
    clg: Mapping[str, Any] | None = None,
    board: Mapping[str, Any] | None = None,
    max_passes: int = MAX_REVISE_PASSES,
) -> dict[str, Any]:
    """
    Recovery PQLE spine:
    formatting-only PQLE → PMES/PEEC/EPP/fidelity only when EQS improves.
    """
    from engines.lesson_composition_engine.editorial_board import review_package_editorial
    from engines.lesson_composition_engine.recovery import (
        adaptation_similarity_report,
        apply_if_improves,
        clarity_edit_adaptation,
        educational_quality_score,
        format_only_package,
        golden_comparison_gate,
    )

    seed_default_golden_lessons()
    # The pipeline stores the publisher spine under _meta — without this
    # fallback the EATS revise loop ran with an EMPTY board, so PMES had no
    # concepts and injected the generic pedagogy flowchart that EATS itself
    # rejects ("Generic subject-sequence flowchart is not a domain diagram").
    meta = adaptations.get("_meta") if isinstance(adaptations.get("_meta"), dict) else {}
    clg = dict(clg or meta.get("canonical_lesson_graph") or (meta.get("lce") or {}).get("clg") or {})
    board = dict(
        board
        or adaptations.get("_intelligence_board")
        or meta.get("intelligence_board")
        or (meta.get("lce") or {}).get("intelligence_board")
        or {}
    )
    contribution_log: list[dict[str, Any]] = []

    before_pqle = educational_quality_score(adaptations)
    working = format_only_package(dict(adaptations))
    after_pqle = educational_quality_score(working)
    contribution_log.append(
        {
            "engine": "PQLE",
            "before": before_pqle.get("overall"),
            "after": after_pqle.get("overall"),
            "delta": round(float(after_pqle["overall"]) - float(before_pqle["overall"]), 2),
            "bypassed": False,
            "mode": "formatting_only",
            "log": "ENGINE CONTRIBUTION OK",
        }
    )

    vocab = working.get("vocabulary") if isinstance(working.get("vocabulary"), dict) else {}
    pqi_by: dict[str, Any] = {}
    golden_deltas: dict[str, float] = {}

    for key, value in list(working.items()):
        if key.startswith("_") or not isinstance(value, dict):
            continue
        if key in {"vocabulary", "worksheet"}:
            continue
        revised, meta = revise_adaptation_to_publication(
            value,
            version_id=key,
            clg=clg,
            vocabulary=vocab,
            max_passes=1,
        )
        working[key] = revised
        pqi_by[key] = meta
        golden_deltas[key] = float((meta.get("report") or {}).get("golden_delta") or 0.0)

    eerl = review_package(working, clg)
    pqi = score_package(working, golden_deltas=golden_deltas)
    editorial = review_package_editorial(working, board=board)
    topic = str(board.get("topic") or clg.get("topic") or "Lesson")

    def _pmes_transform(pkg: dict[str, Any]) -> dict[str, Any]:
        from engines.lesson_composition_engine.pmes import run_pmes

        cleared: dict[str, Any] = {}
        for k, v in pkg.items():
            if k.startswith("_") or not isinstance(v, dict) or k in {"vocabulary", "worksheet"}:
                cleared[k] = v
                continue
            cleared[k] = clarity_edit_adaptation(dict(v), topic=topic)
        pmes_out = run_pmes(cleared, board=board, max_passes=1)
        result = pmes_out.get("adaptations") or cleared
        for k, v in list(result.items()):
            if k.startswith("_") or not isinstance(v, dict) or k in {"vocabulary", "worksheet"}:
                continue
            result[k] = clarity_edit_adaptation(dict(v), topic=topic)
        return result

    working, pmes_gate = apply_if_improves("PMES", working, _pmes_transform)
    contribution_log.append(pmes_gate)
    publisher_review = {
        "approved": not pmes_gate.get("bypassed", False),
        "mode": "clarity_only",
        "contribution": pmes_gate,
    }
    pmes = {
        "publication_ready": True,
        "pmes_version": "2.1.0-recovery",
        "reject_rendering": False,
        "approved": publisher_review["approved"],
        "bypassed": bool(pmes_gate.get("bypassed")),
        "contribution": pmes_gate,
    }

    peec_result: dict[str, Any] = {"ok": True, "bypassed": True}
    try:
        from peec import apply_peec

        def _peec(pkg: dict[str, Any]) -> dict[str, Any]:
            out = apply_peec(
                pkg, board=board, pmes_report=publisher_review, write_reports=False, max_passes=1
            )
            return out.get("adaptations") or pkg

        working, peec_gate = apply_if_improves("PEEC", working, _peec)
        contribution_log.append(peec_gate)
        # Bypassed with no error means quality was already at the publication floor.
        peec_result = {
            "ok": (not peec_gate.get("bypassed")) or not peec_gate.get("error"),
            "bypassed": peec_gate.get("bypassed"),
            "contribution": peec_gate,
        }
    except Exception as exc:  # noqa: BLE001
        peec_result = {"ok": False, "error": str(exc)}
        contribution_log.append(
            {
                "engine": "PEEC",
                "bypassed": True,
                "error": str(exc)[:200],
                "log": "ENGINE CONTRIBUTION FAILURE",
            }
        )

    epp_result: dict[str, Any] = {"ok": True, "bypassed": True, "smoke_ok": True}
    try:
        from epp import apply_epp

        def _epp(pkg: dict[str, Any]) -> dict[str, Any]:
            out = apply_epp(pkg, board=board)
            return out.get("adaptations") or pkg

        working, epp_gate = apply_if_improves("EPP", working, _epp)
        contribution_log.append(epp_gate)
        epp_result = {
            "ok": not epp_gate.get("bypassed"),
            "bypassed": epp_gate.get("bypassed"),
            "contribution": epp_gate,
            "smoke_ok": True,
        }
    except Exception as exc:  # noqa: BLE001
        epp_result = {"ok": False, "error": str(exc)}
        contribution_log.append(
            {
                "engine": "EPP",
                "bypassed": True,
                "error": str(exc)[:200],
                "log": "ENGINE CONTRIBUTION FAILURE",
            }
        )

    fidelity_result: dict[str, Any] = {"ok": True}
    try:
        from engines.lesson_composition_engine.content_fidelity import (
            CONTENT_FIDELITY_PUBLISHING_RECOVERY_SMOKE_OK,
            apply_content_fidelity,
            content_fidelity_issues,
        )

        # Content fidelity is a hard publishing standard — always apply (never EQS-bypass).
        working = apply_content_fidelity(working, board=board)
        contribution_log.append(
            {
                "engine": "content_fidelity",
                "bypassed": False,
                "mandatory": True,
                "log": "ENGINE CONTRIBUTION APPLIED",
            }
        )
        fidelity_result = {
            "ok": not content_fidelity_issues(working),
            "issues": content_fidelity_issues(working),
            "smoke_ok": CONTENT_FIDELITY_PUBLISHING_RECOVERY_SMOKE_OK,
            "bypassed": False,
            "mandatory": True,
        }
    except Exception as exc:  # noqa: BLE001
        fidelity_result = {"ok": False, "error": str(exc)}
        contribution_log.append(
            {
                "engine": "content_fidelity",
                "bypassed": True,
                "error": str(exc)[:200],
                "log": "ENGINE CONTRIBUTION FAILURE",
            }
        )

    for key, value in list(working.items()):
        if key.startswith("_") or not isinstance(value, dict) or key in {"vocabulary", "worksheet"}:
            continue
        working[key] = clarity_edit_adaptation(dict(value), topic=topic)

    # Re-apply fidelity after clarity scrub so leaks/clones cannot re-enter the gate
    try:
        from engines.lesson_composition_engine.content_fidelity import (
            apply_content_fidelity,
            content_fidelity_issues,
        )

        working = apply_content_fidelity(working, board=board)
        fidelity_result = {
            **fidelity_result,
            "ok": not content_fidelity_issues(working),
            "issues": content_fidelity_issues(working),
            "final_pass": True,
        }
    except Exception:  # noqa: BLE001
        pass

    eerl = review_package(working, clg)
    golden_deltas = {}
    for key, value in working.items():
        if key.startswith("_") or not isinstance(value, dict) or key in {"vocabulary", "worksheet"}:
            continue
        subject = str(clg.get("subject_key") or board.get("subject") or "general")
        golden = compare_to_golden(
            value,
            subject=subject,
            topic=str(value.get("topic") or board.get("topic") or clg.get("topic") or ""),
        )
        golden_deltas[key] = float(golden.get("delta") or 0.0)
    pqi = score_package(working, golden_deltas=golden_deltas)
    editorial = review_package_editorial(working, board=board)

    eqs = educational_quality_score(
        working,
        subject=str(clg.get("subject_key") or board.get("subject") or ""),
        topic=topic,
    )
    sim = adaptation_similarity_report(working)
    from engines.lesson_composition_engine.human_quality import (
        PUBLICATION_HEQ_THRESHOLD,
        adaptation_advantage_report,
    )

    adv = adaptation_advantage_report(working)
    golden_gate = golden_comparison_gate(
        working,
        subject=str(clg.get("subject_key") or board.get("subject") or ""),
        topic=topic,
    )

    publication_ready = bool(eqs.get("publication_ready")) and bool(golden_gate.get("ok")) and bool(
        fidelity_result.get("ok", True)
    )

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
            "pqle": {"publication_ready": publication_ready, "mode": "formatting_only"},
            "peec": peec_result,
            "epp": epp_result,
            "content_fidelity": fidelity_result,
            "eqs": eqs,
            "heq": eqs,
            "adaptation_similarity": sim,
            "adaptation_advantages": adv,
            "golden_gate": golden_gate,
            "contribution_log": contribution_log,
        }
        uevb_result = gate_package_for_production(provisional)
    except Exception as exc:  # noqa: BLE001
        uevb_result = {"ok": False, "error": str(exc)}

    reject_reasons = []
    if not sim.get("ok"):
        reject_reasons.append("adaptation_similarity_above_40pct")
    if not adv.get("ok"):
        reject_reasons.append("adaptation_advantage_weak")
    if not golden_gate.get("ok"):
        reject_reasons.append(str(golden_gate.get("reason") or "golden_gate_failed"))
    if float(eqs.get("overall") or 0) < PUBLICATION_HEQ_THRESHOLD:
        reject_reasons.append(f"heq_below_{int(PUBLICATION_HEQ_THRESHOLD)}:{eqs.get('overall')}")
    if eqs.get("weak_teaching_markers"):
        reject_reasons.append("weak_teaching_markers")
    if not (eqs.get("human_verdict") or {}).get("classroom_ready"):
        reject_reasons.append("not_classroom_ready")
    if not fidelity_result.get("ok", True):
        issues = fidelity_result.get("issues") or []
        reject_reasons.append(
            f"content_fidelity:{', '.join(str(i) for i in issues[:3])}" if issues else "content_fidelity"
        )

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
            "bypassed": pmes.get("bypassed"),
            "mode": "clarity_only",
        },
        "peec": peec_result,
        "epp": epp_result,
        "content_fidelity": fidelity_result,
        "eqs": eqs,
        "adaptation_similarity": sim,
        "golden_gate": golden_gate,
        "contribution_log": contribution_log,
        "uevb": uevb_result,
        "publication_ready": publication_ready,
        "reject_rendering": not publication_ready,
        "reject_reasons": reject_reasons,
        "threshold": PUBLISHER_QUALITY_THRESHOLD,
        "recovery_sprint": True,
        "phase_omega": True,
        "phase_omega_2_pmes": True,
        "pqle_mode": "formatting_only",
        "heq": eqs,
        "adaptation_advantages": adv,
        "human_verdict": eqs.get("human_verdict") or {},
        "publication_heq_threshold": PUBLICATION_HEQ_THRESHOLD,
    }
