"""Generation Recovery regression report — human-first HEQ + side-by-side.

Run: python -m engines.lesson_composition_engine.recovery_report
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engines.lesson_composition_engine import compose_lesson_package
from engines.lesson_composition_engine.human_quality import PUBLICATION_HEQ_THRESHOLD
from engines.lesson_composition_engine.recovery import (
    GENERATION_RECOVERY_SMOKE_OK,
    adaptation_similarity_report,
    educational_quality_score,
)

REGRESSION_TOPICS = [
    ("physics", "Force and Pressure", "A force can change the shape or motion of an object. Pressure is force on a unit area. A sharp tip has high pressure."),
    ("biology", "The Water Cycle", "Evaporation turns liquid water into vapour. Condensation forms clouds. Precipitation returns water as rain. Collection gathers water in oceans."),
    ("mathematics", "Fractions", "A fraction shows parts of a whole. The numerator is the count of parts. The denominator is the total equal parts."),
    ("biology", "Photosynthesis", "Green plants make food using sunlight. Chlorophyll traps light. Carbon dioxide and water become glucose and oxygen."),
    ("biology", "Digestive System", "Digestion breaks food into nutrients. The stomach mixes food with acid. The small intestine absorbs nutrients."),
    ("physics", "Light", "Light travels in straight lines. Reflection bounces light. Refraction bends light when it enters a new medium."),
    ("geography", "Volcanoes", "Magma rises through cracks in the crust. Lava is magma that reaches the surface. Ash and gases can erupt violently."),
    ("history", "Trade Routes", "Trade routes connected cities across land and sea. Merchants carried goods, ideas, and culture along the routes."),
    ("mathematics", "Percentages", "A percentage is a number out of one hundred. 50 percent means half. Percentages compare parts of a whole."),
    ("environmental_science", "Waste Management", "Reduce means use less. Reuse means use again. Recycle means make new materials from used ones."),
]


def _uli(subject: str, topic: str, text: str) -> dict[str, Any]:
    claims = [{"text": s.strip()} for s in text.replace(". ", ".|").split("|") if s.strip()]
    concepts = []
    for claim in claims:
        for word in claim["text"].replace(",", " ").split():
            token = word.strip(".:;()[]\"'")
            if len(token) >= 5 and token[0].isupper():
                concepts.append({"name": token, "explanation": claim["text"]})
                break
    if not concepts:
        concepts = [{"name": topic, "explanation": text[:120]}]
    return {
        "universal_profile": {
            "topic": topic,
            "subject": subject,
            "concepts": concepts,
            "claim_ledger": claims,
            "key_concepts": concepts,
        },
        "claim_ledger": claims,
    }


def run_recovery_regression() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for subject, topic, text in REGRESSION_TOPICS:
        pkg = compose_lesson_package(_uli(subject, topic, text), topic_hint=topic)
        adaptations = pkg.get("adaptations") or {}
        heq = pkg.get("heq") or pkg.get("eqs") or educational_quality_score(
            adaptations, subject=subject, topic=topic
        )
        sim = pkg.get("adaptation_similarity") or adaptation_similarity_report(adaptations)
        std = adaptations.get("standard") or {}
        blob = (
            str(std.get("big_idea") or "")
            + " "
            + " ".join(str(s.get("body") or "") for s in (std.get("sections") or []) if isinstance(s, dict))
        ).lower()
        banned = [
            p
            for p in (
                "notice how",
                "this section",
                "teacher note",
                "editorial",
                "why opening matters",
                "today you will master",
                "helps you explain the topic clearly",
            )
            if p in blob
        ]
        rows.append(
            {
                "topic": topic,
                "subject": subject,
                "heq": heq.get("overall"),
                "heq_components": heq.get("components"),
                "human_verdict": heq.get("human_verdict"),
                "similarity_ok": sim.get("ok"),
                "similarity_failures": sim.get("failures") or [],
                "adaptation_advantages": pkg.get("adaptation_advantages") or heq.get("adaptation_advantages"),
                "golden_gate": pkg.get("golden_gate") or {},
                "side_by_side": pkg.get("side_by_side") or {},
                "publication_ready": bool((pkg.get("pqle") or {}).get("publication_ready")),
                "reject_reasons": pkg.get("reject_reasons") or [],
                "contribution_log": pkg.get("contribution_log") or [],
                "banned_leaks": banned,
                "no_opening_pollution": "why opening matters" not in blob,
                "excerpt": (std.get("big_idea") or "")[:240],
            }
        )
    all_clean = all(r["no_opening_pollution"] and not r["banned_leaks"] for r in rows)
    publishable = all(r["publication_ready"] for r in rows)
    classroom = all(bool((r.get("human_verdict") or {}).get("classroom_ready")) for r in rows)
    return {
        "schema": "alora.generation_recovery_report.v2_human_first",
        "smoke_ok": GENERATION_RECOVERY_SMOKE_OK,
        "heq_threshold": PUBLICATION_HEQ_THRESHOLD,
        "generated_at": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "topics": rows,
        "suite_ok": all_clean,
        "all_publication_ready": publishable,
        "all_classroom_ready": classroom,
        "recovery_complete": publishable and classroom and all_clean,
        "summary": {
            "count": len(rows),
            "heq_floor_pass": all((r["heq"] or 0) >= PUBLICATION_HEQ_THRESHOLD for r in rows),
            "similarity_pass_count": sum(1 for r in rows if r["similarity_ok"]),
            "publication_ready_count": sum(1 for r in rows if r["publication_ready"]),
            "classroom_ready_count": sum(
                1 for r in rows if (r.get("human_verdict") or {}).get("classroom_ready")
            ),
        },
    }


def write_report(out_dir: Path | None = None) -> Path:
    report = run_recovery_regression()
    root = out_dir or Path("forensics") / "runs" / f"recovery_{report['generated_at']}"
    root.mkdir(parents=True, exist_ok=True)
    (root / "RECOVERY_REPORT.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Generation Recovery Report (Human-First HEQ)",
        "",
        f"Generated: {report['generated_at']}",
        f"HEQ threshold: {report['heq_threshold']}",
        f"Suite clean (no template leaks): {report['suite_ok']}",
        f"All classroom ready: {report['all_classroom_ready']}",
        f"All publication ready: {report['all_publication_ready']}",
        f"Recovery complete: {report['recovery_complete']}",
        "",
        "| Topic | HEQ | Classroom | Pub | Failures |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in report["topics"]:
        classroom = bool((r.get("human_verdict") or {}).get("classroom_ready"))
        lines.append(
            f"| {r['topic']} | {r['heq']} | {classroom} | {r['publication_ready']} | "
            f"{'; '.join(r['reject_reasons']) or '—'} |"
        )
    lines.append("")
    lines.append("## Side-by-side (first topic)")
    sbs = (report["topics"][0].get("side_by_side") or {}) if report["topics"] else {}
    for stage in sbs.get("stages") or []:
        lines.append(f"### {stage.get('stage')} — HEQ {stage.get('heq')}")
        lines.append("")
        lines.append(f"Big idea: {stage.get('big_idea')}")
        lines.append("")
        lines.append((stage.get("excerpt") or "")[:500])
        lines.append("")
    for change in sbs.get("changes") or []:
        lines.append(
            f"- {change.get('from')} → {change.get('to')}: {change.get('verdict')} "
            f"(ΔHEQ {change.get('heq_delta')}) — {change.get('what_changed')}"
        )
    lines.append("")
    lines.append("## Contribution (sample first topic)")
    if report["topics"]:
        for c in report["topics"][0].get("contribution_log") or []:
            lines.append(
                f"- {c.get('engine')}: delta={c.get('delta')} bypassed={c.get('bypassed')} — {c.get('log')}"
            )
    (root / "RECOVERY_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return root


def main() -> None:
    path = write_report()
    print(f"RECOVERY_REPORT_WRITTEN:{path}")


if __name__ == "__main__":
    main()
