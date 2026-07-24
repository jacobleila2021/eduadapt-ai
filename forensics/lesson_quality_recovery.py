"""CLI: python -m forensics.lesson_quality_recovery"""

from __future__ import annotations

from pathlib import Path

from forensics.analysis import (
    adaptation_audit,
    build_blame_report,
    compare_all_stages,
    disable_probe,
    educational_contribution_scores,
    historical_compare,
    write_forensic_report,
)
from forensics.pipeline_capture import capture_pipeline, new_run_dir

WATER_CYCLE_SOURCE = """
The Water Cycle

Water moves through the environment in a continuous cycle.
Evaporation changes liquid water into water vapour when the sun heats oceans, lakes, and rivers.
Condensation cools water vapour into tiny droplets that form clouds.
Precipitation returns water to Earth as rain, snow, or hail.
Collection gathers water in oceans, rivers, lakes, and soil so the cycle can continue.
Transpiration releases water vapour from plants into the air.
The sun supplies the energy that drives the water cycle.
The amount of water on Earth stays roughly in balance as water changes form.
""".strip()


def run_sprint(*, topic: str = "The Water Cycle", source_text: str = WATER_CYCLE_SOURCE) -> Path:
    root = new_run_dir(Path("forensics") / "runs")
    primary = root / "primary"
    primary.mkdir(parents=True, exist_ok=True)

    print(f"[forensics] primary capture -> {primary}")
    out = capture_pipeline(source_text=source_text, topic=topic, run_dir=primary)
    comparisons = compare_all_stages(primary)
    ecs = educational_contribution_scores(comparisons)
    blame = build_blame_report(primary, comparisons)

    print("[forensics] disable probes (this takes longer)...")
    probes = disable_probe(source_text, topic, root / "disable_probes")

    adapt = adaptation_audit(out.get("adaptations") or {})
    hist = historical_compare(source_text, topic, primary)

    bundle = {
        "manifest": out.get("manifest") or {},
        "comparisons": comparisons,
        "ecs": ecs,
        "blame": blame,
        "disable_probes": probes,
        "adaptation_audit": adapt,
        "historical": hist,
    }
    report = write_forensic_report(root, bundle)
    print(f"[forensics] REPORT -> {report}")
    print(f"[forensics] ECS -> {ecs}")
    return report


if __name__ == "__main__":
    run_sprint()
