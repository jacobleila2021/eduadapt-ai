"""Immutable stage capture for the lesson composition spine."""

from __future__ import annotations

import copy
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from forensics.learner_metrics import dumps, score_lesson_surface

STAGE_ORDER = [
    "01_raw_source_profile",
    "02_after_uli_envelope",
    "03_after_sif",
    "04_after_uvie",
    "05_after_lce_clg_board",
    "06_after_adaptations",
    "07_after_vocabulary",
    "08_after_diagram_integration",
    "09_after_pqle_polish",
    "10_after_pmes",
    "11_after_peec",
    "12_final_html",
]


def _safe_copy(obj: Any) -> Any:
    try:
        return copy.deepcopy(obj)
    except Exception:
        return json.loads(json.dumps(obj, default=str))


def _write_stage(run_dir: Path, stage_id: str, payload: dict[str, Any]) -> Path:
    path = run_dir / "stages" / f"{stage_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    # Never overwrite: if exists, append timestamp suffix
    if path.exists():
        path = run_dir / "stages" / f"{stage_id}_{int(time.time() * 1000)}.json"
    path.write_text(dumps(payload), encoding="utf-8")
    return path


def _lesson_html(adaptations: dict[str, Any]) -> str:
    std = adaptations.get("standard") or {}
    title = str(std.get("topic") or std.get("title") or "Lesson")
    try:
        from html_exporter import export_lesson_html

        return export_lesson_html(std, title)
    except Exception:
        pass
    sections = std.get("sections") or []
    parts = [f"<h1>{title}</h1>"]
    if std.get("big_idea"):
        parts.append(f"<p><strong>Big idea:</strong> {std.get('big_idea')}</p>")
    for sec in sections:
        if not isinstance(sec, dict):
            continue
        parts.append(f"<h2>{sec.get('title') or ''}</h2>")
        parts.append(f"<p>{sec.get('body') or ''}</p>")
    return "\n".join(parts)


def _export_html_file(run_dir: Path, adaptations: dict[str, Any]) -> Path:
    html = _lesson_html(adaptations)
    path = run_dir / "stages" / "12_final_html.html"
    if path.exists():
        path = run_dir / "stages" / f"12_final_html_{int(time.time() * 1000)}.html"
    path.write_text(html, encoding="utf-8")
    return path


def new_run_dir(root: Path | None = None) -> Path:
    root = root or Path("forensics") / "runs"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = root / stamp
    (run_dir / "stages").mkdir(parents=True, exist_ok=True)
    return run_dir


def capture_pipeline(
    *,
    source_text: str,
    topic: str = "",
    run_dir: Path | None = None,
    disable: set[str] | None = None,
) -> dict[str, Any]:
    """
    Run the real LCE spine step-by-step and save every stage.

    disable: optional set of stage short names to skip:
      sif, uvie, pqle, pmes, peec, epp, content_fidelity, diagrams
    """
    disable = {d.lower() for d in (disable or set())}
    run_dir = run_dir or new_run_dir()
    manifest: dict[str, Any] = {
        "run_dir": str(run_dir),
        "topic": topic,
        "disable": sorted(disable),
        "stages": [],
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

    def snap(stage_id: str, adaptations: dict[str, Any] | None, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        adaptations = adaptations or {}
        metrics = score_lesson_surface(adaptations) if adaptations else {}
        payload = {
            "stage_id": stage_id,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "adaptations": _safe_copy(adaptations),
            "metrics": metrics,
            "extra": extra or {},
        }
        path = _write_stage(run_dir, stage_id, payload)
        manifest["stages"].append(
            {
                "stage_id": stage_id,
                "path": str(path),
                "learner_quality_score": metrics.get("learner_quality_score"),
            }
        )
        return payload

    # --- Stage 1: raw source + profile (no LLM; extractive baseline) ---
    from engines.knowledge_ingestion_engine.universal_ingest import ingest_source_bytes
    from engines.universal_lesson.profile import build_universal_lesson_profile

    envelope = ingest_source_bytes(f"{topic or 'lesson'}.txt", source_text.encode("utf-8")).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    if topic:
        profile["topic"] = topic
    uli_payload = {
        "universal_profile": profile,
        "claim_ledger": profile.get("claim_ledger") or [],
    }
    # Extractive "raw" lesson from claims — baseline before composition engines
    claims = [str(c.get("text") or c) for c in (profile.get("claim_ledger") or []) if c][:8]
    concepts = [
        str(c.get("name") or "")
        for c in (profile.get("key_concepts") or profile.get("concepts") or [])
        if c
    ]
    raw_adaptations = {
        "standard": {
            "topic": profile.get("topic") or topic or "Lesson",
            "big_idea": claims[0] if claims else f"Learn about {topic or 'this topic'}.",
            "sections": [
                {"title": "Source Ideas", "role": "concept", "body": " ".join(claims[:4]) or "No claims extracted."},
                {
                    "title": "Key Terms",
                    "role": "vocabulary",
                    "body": ", ".join(concepts[:8]) or "Terms will be added later.",
                },
            ],
        },
        "vocabulary": {"topic": profile.get("topic") or topic, "word_wall": []},
    }
    snap("01_raw_source_profile", raw_adaptations, {"profile_keys": list(profile.keys()), "claim_count": len(claims)})

    # --- Stage 2: ULI envelope (profile package used by LCE) ---
    snap("02_after_uli_envelope", raw_adaptations, {"uli_payload_topic": uli_payload["universal_profile"].get("topic")})

    # --- Stage 3: SIF (optional / often empty on Streamlit path) ---
    sif: dict[str, Any] = {}
    if "sif" not in disable:
        try:
            from engines.subject_intelligence_framework.semantic_hooks import run_subject_intelligence

            sif = run_subject_intelligence(uli_payload, context={"text": source_text}) or {}
            if not isinstance(sif, dict):
                sif = {"raw": sif}
        except Exception as exc:  # noqa: BLE001
            sif = {"ok": False, "error": str(exc)[:300]}
    snap("03_after_sif", raw_adaptations, {"sif_ok": bool(sif) and not sif.get("error"), "sif_keys": list(sif)[:20]})

    # --- Stage 4: UVIE ---
    uvie: dict[str, Any] = {"preferred_visuals": [], "visuals": []}
    if "uvie" not in disable:
        try:
            from engines.universal_visual_intelligence import render_visuals_for_uli

            uvie_result = render_visuals_for_uli(
                None,
                context={"text": source_text, "topic": profile.get("topic") or topic},
            )
            visuals = list((uvie_result or {}).get("visuals") or [])
            uvie = {
                "preferred_visuals": visuals,
                "visuals": visuals,
                "ok": bool((uvie_result or {}).get("ok")),
            }
        except Exception as exc:  # noqa: BLE001
            uvie = {"ok": False, "error": str(exc)[:300], "preferred_visuals": [], "visuals": []}
    snap(
        "04_after_uvie",
        raw_adaptations,
        {"uvie_ok": uvie.get("ok"), "visual_count": len(uvie.get("preferred_visuals") or [])},
    )

    # --- Stage 5: LCE CLG + Intelligence Board (pre-adaptation authorship) ---
    from engines.lesson_composition_engine.clg import build_canonical_lesson_graph
    from engines.lesson_composition_engine.composer import compose_adaptations_from_clg
    from engines.lesson_composition_engine.intelligence_board import build_lesson_intelligence_board

    clg = build_canonical_lesson_graph(
        uli_payload, sif=sif if isinstance(sif, dict) else {}, uvie=uvie, topic_hint=topic or profile.get("topic") or ""
    )
    clg_dict = clg.to_dict() if hasattr(clg, "to_dict") else dict(clg)
    board = build_lesson_intelligence_board(
        clg_dict,
        uli=uli_payload,
        sif=sif if isinstance(sif, dict) else {},
        uvie=uvie,
    )
    snap(
        "05_after_lce_clg_board",
        raw_adaptations,
        {
            "clg_topic": clg_dict.get("topic"),
            "concept_count": len(clg_dict.get("core_concepts") or []),
            "board_version": board.get("version") if isinstance(board, dict) else None,
        },
    )

    # --- Stage 6: Adaptations authored from board ---
    adaptations = compose_adaptations_from_clg(
        clg_dict,
        board=board,
        uli=uli_payload,
        sif=sif if isinstance(sif, dict) else {},
        uvie=uvie,
    )
    if not isinstance(adaptations, dict):
        adaptations = {}
    snap("06_after_adaptations", adaptations)

    # --- Stage 7: Vocabulary (ensure composed) ---
    if not (adaptations.get("vocabulary") or {}).get("word_wall"):
        try:
            from engines.lesson_composition_engine.vocabulary import compose_vocabulary_page

            seeds = list(board.get("vocabulary") or []) + [
                str(c.get("name") or "") for c in (board.get("concepts") or []) if isinstance(c, dict)
            ]
            adaptations["vocabulary"] = compose_vocabulary_page(
                seeds,
                topic=str(board.get("topic") or clg_dict.get("topic") or topic or "Lesson"),
                claims=list(board.get("verified_claims") or []),
            )
        except Exception as exc:  # noqa: BLE001
            adaptations.setdefault("vocabulary", {"error": str(exc)[:200]})
    snap("07_after_vocabulary", adaptations)

    # --- Stage 8: Diagram integration ---
    if "diagrams" not in disable:
        from engines.lesson_composition_engine.revise import _enrich_diagrams

        topic_s = str(clg_dict.get("topic") or topic or "Lesson")
        subject_s = str(clg_dict.get("subject_key") or "general")
        concepts_s = [str(c.get("name") or "") for c in (clg_dict.get("core_concepts") or []) if c]
        for key, value in list(adaptations.items()):
            if key.startswith("_") or key in {"vocabulary", "worksheet"} or not isinstance(value, dict):
                continue
            adaptations[key] = _enrich_diagrams(value, topic=topic_s, subject=subject_s, concepts=concepts_s)
    snap("08_after_diagram_integration", adaptations)

    # --- Stage 9: PQLE polish/remediate/revise (without PMES/PEEC) ---
    working = dict(adaptations)
    if "pqle" not in disable:
        from engines.lesson_composition_engine.publisher_remediation import remediate_package
        from engines.lesson_composition_engine.writing_excellence import polish_package
        from engines.lesson_composition_engine.revise import revise_adaptation_to_publication

        claims_b = list(board.get("verified_claims") or [])
        working = polish_package(dict(working))
        working = remediate_package(working, claims=claims_b)
        vocab = working.get("vocabulary") if isinstance(working.get("vocabulary"), dict) else {}
        for key, value in list(working.items()):
            if key.startswith("_") or key in {"vocabulary", "worksheet"} or not isinstance(value, dict):
                continue
            revised, _meta = revise_adaptation_to_publication(
                value, version_id=key, clg=clg_dict, vocabulary=vocab, max_passes=2
            )
            working[key] = revised
    snap("09_after_pqle_polish", working)

    # --- Stage 10: PMES ---
    if "pmes" not in disable:
        from engines.lesson_composition_engine.pmes import run_pmes

        pmes = run_pmes(working, board=board, max_passes=2)
        working = pmes.get("adaptations") or working
        snap("10_after_pmes", working, {"pmes_approved": (pmes.get("publisher_review_report") or {}).get("approved")})
    else:
        snap("10_after_pmes", working, {"skipped": True})

    # --- Stage 11: PEEC (+ optional EPP / content fidelity as bundled final polish) ---
    if "peec" not in disable:
        try:
            from peec import apply_peec

            peec_result = apply_peec(working, board=board, write_reports=False, max_passes=2)
            working = peec_result.get("adaptations") or working
        except Exception as exc:  # noqa: BLE001
            snap("11_after_peec", working, {"peec_error": str(exc)[:300]})
            peec_result = {}
        else:
            extra = {"peec_ok": peec_result.get("ok")}
            if "epp" not in disable:
                try:
                    from epp import apply_epp

                    epp_result = apply_epp(working, board=board)
                    working = epp_result.get("adaptations") or working
                    extra["epp"] = True
                except Exception as exc:  # noqa: BLE001
                    extra["epp_error"] = str(exc)[:200]
            if "content_fidelity" not in disable:
                try:
                    from engines.lesson_composition_engine.content_fidelity import apply_content_fidelity

                    cf_out = apply_content_fidelity(working, board=board)
                    if isinstance(cf_out, dict):
                        working = cf_out.get("adaptations") or cf_out
                    extra["content_fidelity"] = True
                except Exception as exc:  # noqa: BLE001
                    extra["content_fidelity_error"] = str(exc)[:200]
            snap("11_after_peec", working, extra)
    else:
        snap("11_after_peec", working, {"skipped": True})

    # --- Stage 12: Final HTML ---
    html_path = _export_html_file(run_dir, working)
    final = snap("12_final_html", working, {"html_path": str(html_path)})

    manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
    manifest["final_score"] = (final.get("metrics") or {}).get("learner_quality_score")
    (run_dir / "manifest.json").write_text(dumps(manifest), encoding="utf-8")
    return {"run_dir": run_dir, "manifest": manifest, "adaptations": working, "board": board, "clg": clg_dict}


# Avoid unused import warning for Callable in type checkers
_: Callable[..., Any] | None = None
