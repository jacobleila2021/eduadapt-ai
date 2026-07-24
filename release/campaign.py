"""RC1 campaign runner — generate lesson packages and harvest defects."""

from __future__ import annotations

import time
from typing import Any

from release.defects import (
    CRITICAL,
    HIGH,
    auto_resolve_critical_high,
    classify_package_defects,
)
from uevb.corpus import (
    build_sample_sif,
    build_sample_uli,
    build_sample_uvie,
    corpus_size,
    iter_corpus_specs,
)


def _compose(spec: dict[str, Any]) -> dict[str, Any]:
    from engines.lesson_composition_engine import compose_lesson_package

    uli = build_sample_uli(
        subject=spec["subject"],
        topic=spec["topic"],
        concept=spec["concept"],
        curriculum=spec["curriculum"],
    )
    pkg = compose_lesson_package(
        uli,
        sif=build_sample_sif(subject=spec["subject"], topic=spec["topic"], concept=spec["concept"]),
        uvie=build_sample_uvie(topic=spec["topic"], concept=spec["concept"]),
        topic_hint=spec["topic"],
    )
    pkg = dict(pkg)
    pkg["corpus_id"] = spec["corpus_id"]
    pkg["curriculum"] = spec["curriculum"]
    pkg["subject"] = spec["subject"]
    return pkg


def run_rc1_campaign(
    *,
    target_packages: int = 100,
    subjects: tuple[str, ...] | None = None,
    curricula: tuple[str, ...] | None = None,
    max_topics_per_subject: int = 1,
    compose: bool = True,
    auto_fix: bool = True,
) -> dict[str, Any]:
    """
    Generate up to `target_packages` complete lesson packages.

    Default matrix (12 subjects × 10 curricula × 1 topic) yields 120 specs —
    enough for the RC1 minimum of 100.
    """
    specs = iter_corpus_specs(
        subjects=subjects,
        curricula=curricula,
        max_topics_per_subject=max_topics_per_subject,
    )
    specs = specs[: max(1, int(target_packages))]

    started = time.perf_counter()
    packages_ok = 0
    all_defects: list[dict[str, Any]] = []
    resolved: list[dict[str, Any]] = []
    remaining: list[dict[str, Any]] = []
    timings: list[float] = []
    subjects_seen: set[str] = set()
    curricula_seen: set[str] = set()

    for spec in specs:
        subjects_seen.add(spec["subject"])
        curricula_seen.add(spec["curriculum"])
        t0 = time.perf_counter()
        if compose:
            package = _compose(spec)
        else:
            package = {
                "ok": False,
                "corpus_id": spec["corpus_id"],
                "adaptations": {},
                "intelligence_board": {"topic": spec["topic"], "subject": spec["subject"]},
            }
        elapsed = time.perf_counter() - t0
        timings.append(elapsed)

        defects = classify_package_defects(package, corpus_id=spec["corpus_id"])
        open_defs: list[dict[str, Any]] = []
        if auto_fix and defects:
            package, fixed, open_defs = auto_resolve_critical_high(package, defects)
            resolved.extend(fixed)
            remaining.extend(open_defs)
            defects = classify_package_defects(package, corpus_id=spec["corpus_id"])
        else:
            open_defs = [{**d, "status": "open"} for d in defects]
            remaining.extend(open_defs)

        package_blocking = [
            d
            for d in open_defs
            if d.get("severity") in {CRITICAL, HIGH}
            and d.get("status") in {None, "open"}
        ]
        all_defects.extend(defects)
        if package.get("ok") and not package_blocking:
            packages_ok += 1

    critical_open = [d for d in remaining if d.get("severity") == CRITICAL and d.get("status") == "open"]
    high_open = [d for d in remaining if d.get("severity") == HIGH and d.get("status") == "open"]
    medium = [d for d in remaining if d.get("severity") == "medium"]
    low = [d for d in remaining if d.get("severity") == "low"]

    total_elapsed = time.perf_counter() - started
    avg = (sum(timings) / len(timings)) if timings else 0.0
    rc_ready = len(critical_open) == 0 and len(high_open) == 0 and packages_ok >= max(1, int(0.9 * len(specs)))

    return {
        "schema": "alora.release.rc1_campaign.v1",
        "tag": "ALORA-AI-RC1",
        "packages_targeted": len(specs),
        "packages_ok": packages_ok,
        "subjects": sorted(subjects_seen),
        "curricula": sorted(curricula_seen),
        "corpus_plan": corpus_size(
            subjects=subjects,
            curricula=curricula,
            max_topics_per_subject=max_topics_per_subject,
        ),
        "performance": {
            "total_seconds": round(total_elapsed, 2),
            "avg_package_seconds": round(avg, 2),
            "max_package_seconds": round(max(timings), 2) if timings else 0.0,
            "min_package_seconds": round(min(timings), 2) if timings else 0.0,
        },
        "defects": {
            "total_detected": len(all_defects),
            "resolved": resolved,
            "remaining": remaining,
            "critical_open": critical_open,
            "high_open": high_open,
            "medium_documented": medium,
            "low_documented": low,
            "resolved_count": len(resolved),
            "critical_open_count": len(critical_open),
            "high_open_count": len(high_open),
        },
        "rc1_ready": rc_ready,
        "architecture_frozen": True,
    }
