"""Single Water Cycle run through ai_generator.generate_adaptations (Streamlit path)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from engines.lesson_composition_engine.authoring_benchmark import BENCHMARK_LESSONS, _uli
from engines.lesson_composition_engine.content_fidelity import (
    content_fidelity_block_reason,
    content_fidelity_issues,
)
from publication_gate import publication_block_reason
from ai_generator import generate_adaptations


def main() -> None:
    subject, topic, _grade, text = next(
        x for x in BENCHMARK_LESSONS if x[1] == "The Water Cycle"
    )
    uli = _uli(subject, topic, text)
    profile = uli["universal_profile"]
    envelope = {
        "blocks": [
            {"block_id": "b1", "text": text, "kind": "paragraph"},
        ],
        "metadata": {"topic": topic, "subject": subject, "filename": "water_cycle.txt"},
    }

    def on_progress(msg: str, frac: float) -> None:
        print(f"PROGRESS:{frac:.2f}:{msg}")

    merged = generate_adaptations(
        text,
        on_progress=on_progress,
        source_envelope=envelope,
        universal_profile=profile,
        grounding_mode="uploaded_source",
    )
    lce = (merged.get("_meta") or {}).get("lce") or {}
    issues = content_fidelity_issues(merged)
    block = publication_block_reason(merged) or content_fidelity_block_reason(merged)
    out = {
        "topic": topic,
        "lce_ok": bool(lce.get("ok")),
        "lce_author": lce.get("author"),
        "lce_error": lce.get("error"),
        "quarantine": bool(block),
        "publication_block": block,
        "fidelity_issues": issues,
        "classroom_keys": {
            k: bool(
                isinstance(merged.get(k), dict)
                and ((merged.get(k) or {}).get("sections") or (merged.get(k) or {}).get("big_idea"))
            )
            for k in ("standard", "ld", "adhd", "autism", "ell", "visual")
        },
        "fallback_used": {
            k: ((merged.get(k) or {}).get("_contract") or {}).get("fallback_used")
            for k in ("standard", "ld", "autism")
            if isinstance(merged.get(k), dict)
        },
    }
    root = Path("forensics/runs") / (
        "streamlit_full_water_cycle_"
        + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    )
    root.mkdir(parents=True, exist_ok=True)
    (root / "FULL_STREAMLIT_WATER_CYCLE.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    print("RESULT:" + json.dumps(out))
    print("REPORT:" + root.as_posix())


if __name__ == "__main__":
    main()
