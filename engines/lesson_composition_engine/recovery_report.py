"""Generation Recovery regression report — Part 7 automatic suite.

Run: python -m engines.lesson_composition_engine.recovery_report
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engines.lesson_composition_engine import compose_lesson_package
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
        eqs = pkg.get("eqs") or educational_quality_score(adaptations)
        sim = pkg.get("adaptation_similarity") or adaptation_similarity_report(adaptations)
        std = adaptations.get("standard") or {}
        blob = (
            str(std.get("big_idea") or "")
            + " "
            + " ".join(str(s.get("body") or "") for s in (std.get("sections") or []) if isinstance(s, dict))
        ).lower()
        banned = [p for p in ("notice how", "this section", "teacher note", "editorial", "why opening matters") if p in blob]
        rows.append(
            {
                "topic": topic,
                "subject": subject,
                "eqs": eqs.get("overall"),
                "eqs_components": eqs.get("components"),
                "similarity_ok": sim.get("ok"),
                "similarity_failures": sim.get("failures") or [],
                "golden_gate": pkg.get("golden_gate") or {},
                "publication_ready": bool((pkg.get("pqle") or {}).get("publication_ready")),
                "reject_reasons": pkg.get("reject_reasons") or [],
                "contribution_log": pkg.get("contribution_log") or [],
                "banned_leaks": banned,
                "no_opening_pollution": "why opening matters" not in blob,
            }
        )
    all_pass = all(
        r["no_opening_pollution"] and not r["banned_leaks"] and (r["eqs"] or 0) >= 55 for r in rows
    )
    publishable = all(r["publication_ready"] for r in rows)
    return {
        "schema": "alora.generation_recovery_report.v1",
        "smoke_ok": GENERATION_RECOVERY_SMOKE_OK,
        "generated_at": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "topics": rows,
        "suite_ok": all_pass,
        "all_publication_ready": publishable,
        "summary": {
            "count": len(rows),
            "eqs_floor_pass": all((r["eqs"] or 0) >= 55 for r in rows),
            "similarity_pass_count": sum(1 for r in rows if r["similarity_ok"]),
            "publication_ready_count": sum(1 for r in rows if r["publication_ready"]),
        },
    }


def write_report(out_dir: Path | None = None) -> Path:
    report = run_recovery_regression()
    root = out_dir or Path("forensics") / "runs" / f"recovery_{report['generated_at']}"
    root.mkdir(parents=True, exist_ok=True)
    (root / "RECOVERY_REPORT.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Generation Recovery Report",
        "",
        f"Generated: {report['generated_at']}",
        f"Suite OK: {report['suite_ok']}",
        f"All publication ready: {report['all_publication_ready']}",
        "",
        "| Topic | EQS | Sim OK | Pub | Failures |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in report["topics"]:
        lines.append(
            f"| {r['topic']} | {r['eqs']} | {r['similarity_ok']} | {r['publication_ready']} | "
            f"{'; '.join(r['reject_reasons']) or '—'} |"
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
