"""LXP Phases 1–2 tests."""

from __future__ import annotations

import uuid

from engines.learning_experience_platform import LearningExperienceEngine
from engines.learning_experience_platform.layout import build_layout
from engines.learning_experience_platform.navigation import build_toc, navigation_state
from engines.learning_experience_platform.offline import cache_lesson, sync_cache
from engines.learning_experience_platform.schemas import HIGHLIGHT_COLORS, THEMES
from engines.learning_experience_platform.service import (
    api_add_bookmark,
    api_add_highlight,
    api_add_note,
    api_apply_accessibility,
    api_chat,
    api_click_explain,
    api_explain_paragraph,
    api_glossary,
    api_list_notes,
    api_offline_cache,
    api_offline_sync,
    api_open_reader,
    api_read_along,
    api_search,
    api_stem,
    api_summary,
    api_update_progress,
    api_update_preferences,
)
from engines.learning_experience_platform.themes import resolve_theme
from engines.verified_learning_engine import get_registry, reset_registry


def test_themes_and_modes():
    assert set(THEMES) == {"light", "dark", "sepia", "high_contrast"}
    assert "yellow" in HIGHLIGHT_COLORS
    assert resolve_theme("sepia")["theme"] == "sepia"


def test_registry_includes_lxp():
    reg = reset_registry()
    assert "learning_experience" in {e["engine_id"] for e in reg.list_engines()}
    assert reg.get("learning_experience").health_check().ok


def test_navigation_and_layout():
    toc = build_toc({"sections": [{"title": "Intro", "anchor": "sec_0"}, {"title": "Main", "anchor": "sec_1"}]})
    nav = navigation_state(toc, current_index=0)
    assert nav["can_next"] and not nav["can_prev"]
    layout = build_layout({"sections": toc}, prefs={"theme": "light", "split_ai_panel": True}, progress={"reading_pct": 10})
    assert layout["panels"]["right_ai"]["collapsible"]
    assert layout["toolbar"]["sticky"]


def test_notes_highlights_bookmarks_progress():
    learner = f"lxp_{uuid.uuid4().hex[:8]}"
    lesson = "lesson_cells"
    assert api_add_note(learner, lesson_id=lesson, text="Chloroplasts make food", category="science")["ok"]
    assert api_list_notes(learner, lesson)["notes"]
    assert api_add_highlight(learner, lesson_id=lesson, color="green", excerpt="chloroplast", target_type="text")["ok"]
    assert api_add_bookmark(learner, lesson_id=lesson, label="Diagram", target_type="diagram", folder="science")["ok"]
    prog = api_update_progress(learner, lesson, reading_pct=42, lesson_text="A" * 400, delta_seconds=12)
    assert prog["ok"] and prog["progress"]["reading_pct"] == 42
    assert api_search(learner_id=learner, query="chloro", lesson_text="chloroplast in plant cells")["ok"]


def test_offline_sync_conflict_safe():
    learner = f"lxp_off_{uuid.uuid4().hex[:8]}"
    cached = cache_lesson(
        learner_id=learner,
        lesson_id="L1",
        lesson_payload={"title": "Force"},
        progress={"reading_pct": 30, "last_viewed_at": "2026-01-01T00:00:00+00:00"},
    )
    assert cached["ok"]
    synced = sync_cache(cached["cache_id"], server_progress={"reading_pct": 55, "last_viewed_at": "2026-02-01T00:00:00+00:00"})
    assert synced["ok"] and synced["progress"]["reading_pct"] == 55


def test_phase2_intelligence_apis():
    learner = f"lxp_p2_{uuid.uuid4().hex[:8]}"
    paragraph = "A plant cell has a chloroplast that captures light energy."
    assert api_explain_paragraph(paragraph, learner_id=learner)["ok"]
    assert api_chat("What is a chloroplast?", learner_id=learner, paragraph=paragraph)["ok"]
    assert api_click_explain("chloroplast", target_type="concept")["ok"]
    assert api_glossary(context={"lesson": {"word_wall": [{"term": "cell", "definition": "Basic unit of life"}]}})["ok"]
    assert api_read_along(paragraph)["ok"] or api_read_along(paragraph).get("fallback")
    assert api_stem(context={})["ok"]
    assert api_summary(lesson={"big_idea": "Cells are basic units", "sections": [{"body": "Plant cells have walls."}]})["ok"]


def test_engine_process_phases():
    eng = LearningExperienceEngine()
    out = eng.process(
        {
            "learner_id": f"eng_{uuid.uuid4().hex[:6]}",
            "lesson_text": "Force is a push or a pull. Pressure is force per unit area.",
            "topic": "Force and Pressure",
            "engine_outputs": {
                "accessibility": {"payload": {"learner_profile": {"active_profiles": ["dyslexia"]}}},
            },
        }
    )
    assert out.ok
    assert out.payload["system"] == "LXP"
    assert "phase1_core_reader" in out.payload["phases"]
    assert out.payload["policy"]["never_generate_curriculum"] is True
    assert out.payload["layout"]["footer"] is not None


def test_accessibility_prefs():
    learner = f"a11y_{uuid.uuid4().hex[:6]}"
    out = api_apply_accessibility(
        learner,
        context={"engine_outputs": {"accessibility": {"payload": {"learner_profile": {"active_profiles": ["adhd", "dyslexia"]}}}}},
    )
    assert out["preferences"]["font_family"] == "OpenDyslexic"
    assert out["preferences"]["reading_mode"] == "focus"
    assert out["wcag"].startswith("2.2")


def test_legacy_engines_remain():
    ids = {e["engine_id"] for e in get_registry().list_engines()}
    for required in ("curriculum", "ai_tutor", "voice_multimodal", "learning_experience", "learning_companion"):
        assert required in ids


def test_lxp_phase1_phase2_smoke(capsys):
    """LXP_PHASE1_PHASE2_SMOKE_OK via standard pytest."""
    reg = reset_registry()
    assert reg.get("learning_experience")
    learner = f"smoke_lxp_{uuid.uuid4().hex[:8]}"
    session = api_open_reader(
        learner_id=learner,
        lesson_text="The cell is the basic unit of life. Chloroplasts perform photosynthesis.",
        topic="Cell Structure",
        board="CBSE",
        grade="8",
        subject="Science",
    )
    assert session["ok"] is not False and session.get("system") == "LXP"
    api_update_preferences(learner, {"theme": "sepia", "reading_mode": "focus"})
    api_update_progress(learner, session["lesson_id"], reading_pct=25, lesson_text="cell " * 50)
    api_add_note(learner, lesson_id=session["lesson_id"], text="Review chloroplast")
    api_offline_cache(learner_id=learner, lesson_id=session["lesson_id"], lesson_payload={"title": "Cell"})
    assert api_explain_paragraph("Chloroplasts capture light.", learner_id=learner)["ok"]

    with capsys.disabled():
        print("LXP_PHASE1_PHASE2_SMOKE_OK")
