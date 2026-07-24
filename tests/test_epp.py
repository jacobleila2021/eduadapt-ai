"""EPP — Educational Product Perfection tests."""

from __future__ import annotations

from epp import ALORA_EDUCATIONAL_PRODUCT_PERFECTION_SMOKE_OK, apply_epp


def test_epp_smoke_marker():
    assert ALORA_EDUCATIONAL_PRODUCT_PERFECTION_SMOKE_OK is True


def test_epp_surfaces_board_and_clears_scaffold():
    adaptations = {
        "standard": {
            "big_idea": "Notice how force works. It is worth mastering.",
            "sections": [
                {"title": "Concept", "role": "concept", "body": "Force is a push or a pull on an object."},
            ],
            "flowchart_svg": "<svg xmlns='http://www.w3.org/2000/svg'></svg>",
        },
        "adhd": {
            "sections": [
                {"title": "Chunk", "role": "concept", "body": "Force is a push or a pull."},
            ],
        },
        "vocabulary": {"word_wall": []},
    }
    board = {
        "topic": "Force and Pressure",
        "examples": [{"text": "Opening a classroom door uses force."}],
        "misconceptions": [
            {
                "label": "force is the same as energy",
                "correction": "Force is a push or pull; energy is different.",
            }
        ],
        "verified_claims": [{"text": "Force is a push or a pull."}],
        "learning_goals": [{"text": "Explain force with one real-life example."}],
        "vocabulary": [{"term": "Pressure", "definition": "Force on an area."}],
        "visual_opportunities": [{"caption": "Force arrows organiser"}],
    }
    result = apply_epp(adaptations, board=board)
    assert result["ok"] is True
    assert result["smoke_ok"] is True
    std = result["adaptations"]["standard"]
    blob = " ".join(str(s.get("body") or "") for s in std["sections"]).lower()
    assert "notice how" not in blob
    assert "worth mastering" not in (std.get("big_idea") or "").lower()
    assert "opening a classroom door" in blob
    assert any(str(s.get("role")) == "misconception" for s in std["sections"])
    assert result["adaptations"]["adhd"].get("persona_intent")
    wall = result["adaptations"]["vocabulary"]["word_wall"]
    assert any(str(r.get("term") or "").upper() == "PRESSURE" for r in wall if isinstance(r, dict))
    assert std.get("style_guide", {}).get("background") == "#FFF9EE"


def test_epp_vocab_avoids_picture_scaffold():
    result = apply_epp(
        {
            "vocabulary": {
                "word_wall": [
                    {"term": "Force", "definition": "A push or a pull.", "memory_tip": "Picture force."},
                ]
            }
        },
        board={"topic": "Force"},
    )
    tip = result["adaptations"]["vocabulary"]["word_wall"][0]["memory_tip"].lower()
    assert "picture" not in tip
    assert "draw" in tip
