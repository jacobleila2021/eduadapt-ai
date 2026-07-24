"""UEVB suite runner — compose corpus lessons and validate."""

from __future__ import annotations

from typing import Any

from uevb.constants import UEVB_VERSION
from uevb.corpus import (
    build_sample_sif,
    build_sample_uli,
    build_sample_uvie,
    corpus_size,
    iter_corpus_specs,
)
from uevb.curriculum_consistency import compare_curriculum_packages
from uevb.dashboard import build_dashboard_state
from uevb.release_gate import evaluate_release_gate
from uevb.reports import write_reports
from uevb.validate import validate_composed_package


def _compose_one(spec: dict[str, Any]) -> dict[str, Any]:
    from engines.lesson_composition_engine import compose_lesson_package

    uli = build_sample_uli(
        subject=spec["subject"],
        topic=spec["topic"],
        concept=spec["concept"],
        curriculum=spec["curriculum"],
    )
    sif = build_sample_sif(subject=spec["subject"], topic=spec["topic"], concept=spec["concept"])
    uvie = build_sample_uvie(topic=spec["topic"], concept=spec["concept"])
    return compose_lesson_package(
        uli,
        sif=sif,
        uvie=uvie,
        topic_hint=spec["topic"],
    )


def run_uevb_suite(
    *,
    subjects: tuple[str, ...] | None = None,
    curricula: tuple[str, ...] | None = None,
    max_topics_per_subject: int = 1,
    max_lessons: int | None = 8,
    write: bool = True,
    compose: bool = True,
) -> dict[str, Any]:
    """
    Run Universal Educational Validation & Benchmarking.

    Smoke/CI: keep max_lessons small. Full matrix: max_lessons=None and raise topics.
    """
    specs = iter_corpus_specs(
        subjects=subjects,
        curricula=curricula,
        max_topics_per_subject=max_topics_per_subject,
    )
    if max_lessons is not None:
        specs = specs[: max(1, int(max_lessons))]

    validations: list[dict[str, Any]] = []
    packages_by_concept: dict[str, list[dict[str, Any]]] = {}

    for spec in specs:
        if compose:
            package = _compose_one(spec)
        else:
            package = {
                "adaptations": {},
                "intelligence_board": {
                    "topic": spec["topic"],
                    "subject": spec["subject"],
                    "concepts": [{"name": spec["concept"]}],
                },
                "ok": False,
            }
        validation = validate_composed_package(package, require_pmes=True)
        validation["corpus_id"] = spec["corpus_id"]
        validation["curriculum"] = spec["curriculum"]
        validations.append(validation)
        packages_by_concept.setdefault(spec["concept"], []).append(package)

    consistency_rows = [
        compare_curriculum_packages(pkgs, concept=concept)
        for concept, pkgs in packages_by_concept.items()
        if len(pkgs) >= 2
    ]
    consistency = {
        "ok": all(r.get("ok") for r in consistency_rows) if consistency_rows else True,
        "by_concept": consistency_rows,
    }

    # Load prior dashboard for regression
    prior = {}
    try:
        from pathlib import Path
        import json

        path = Path(__file__).resolve().parents[1] / "reports" / "uevb" / "dashboard_state.json"
        if path.exists():
            prior = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        prior = {}

    release = evaluate_release_gate(validations, prior_dashboard=prior)
    dashboard = build_dashboard_state(
        validations,
        release_gate=release,
        corpus_meta=corpus_size(
            subjects=subjects,
            curricula=curricula,
            max_topics_per_subject=max_topics_per_subject,
        ),
    )
    suite = {
        "schema": "alora.uevb.suite.v1",
        "version": UEVB_VERSION,
        "specs_run": len(specs),
        "validations": validations,
        "curriculum_consistency": consistency,
        "corpus_plan": corpus_size(
            subjects=subjects,
            curricula=curricula,
            max_topics_per_subject=max_topics_per_subject,
        ),
    }
    paths = write_reports(suite_result=suite, release_gate=release, dashboard=dashboard) if write else {}
    return {
        "ok": bool(release.get("release_permitted")),
        "suite": suite,
        "release_gate": release,
        "dashboard": dashboard,
        "report_paths": paths,
    }
