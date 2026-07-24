"""python -m epp — smoke Educational Product Perfection."""

from __future__ import annotations

import json
import sys

from epp import ALORA_EDUCATIONAL_PRODUCT_PERFECTION_SMOKE_OK, EPP_VERSION, apply_epp


def main() -> int:
    sample = {
        "standard": {
            "big_idea": "Notice how force works. It is worth mastering.",
            "sections": [
                {"title": "Concept", "role": "concept", "body": "Force is a push or a pull."},
            ],
        },
        "adhd": {
            "sections": [
                {"title": "Chunk", "role": "concept", "body": "Force is a push or a pull."},
            ],
        },
    }
    board = {
        "topic": "Force and Pressure",
        "examples": [{"text": "Opening a classroom door uses force."}],
        "misconceptions": [
            {"label": "force is the same as energy", "correction": "Force is a push or pull; energy is different."}
        ],
        "verified_claims": [{"text": "Force is a push or a pull."}],
        "learning_goals": [{"text": "Explain force with one real-life example."}],
        "vocabulary": [{"term": "Force", "definition": "A push or a pull."}],
        "visual_opportunities": [{"caption": "Force arrows organiser"}],
    }
    result = apply_epp(sample, board=board)
    std = (result.get("adaptations") or {}).get("standard") or {}
    blob = " ".join(str(s.get("body") or "") for s in (std.get("sections") or []) if isinstance(s, dict)).lower()
    print(
        json.dumps(
            {
                "smoke_ok": ALORA_EDUCATIONAL_PRODUCT_PERFECTION_SMOKE_OK,
                "version": EPP_VERSION,
                "ok": result.get("ok"),
                "notes": len(result.get("notes") or []),
                "scaffold_cleared": "notice how" not in blob and "worth mastering" not in blob,
                "example_surfaced": "opening a classroom door" in blob,
            },
            indent=2,
        )
    )
    return 0 if ALORA_EDUCATIONAL_PRODUCT_PERFECTION_SMOKE_OK and result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
