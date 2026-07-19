"""LXP Phase 4 — premium experience, performance & polish."""

from __future__ import annotations

import uuid
from pathlib import Path

from engines.learning_experience_platform import LearningExperienceEngine
from engines.learning_experience_platform.phase4_offline import (
    background_sync,
    build_full_package,
    detect_conflict,
    enqueue_delta,
    process_queue,
    resolve_conflict,
    sync_status,
)
from engines.learning_experience_platform.phase4_schemas import ANIMATION_PRESETS, CURRICULUM_TRANSLATION_POLICY
from engines.learning_experience_platform.phase4_settings import load_premium_settings, save_premium_settings
from engines.learning_experience_platform.service import (
    api_background_sync,
    api_enqueue_delta,
    api_experience_analytics,
    api_offline_package,
    api_phase4,
    api_premium_settings,
    api_resolve_sync_conflict,
    api_sync_status,
)
from engines.verified_learning_engine import reset_registry
from ui.learning_experience_platform.premium.accessibility import a11y_audit_checklist, keyboard_shortcuts
from ui.learning_experience_platform.premium.animations import animation_catalog, motion_css
from ui.learning_experience_platform.premium.caching import cache_get, cache_set, cache_stats
from ui.learning_experience_platform.premium.gestures import gesture_map
from ui.learning_experience_platform.premium.multilingual import locale_meta, t
from ui.learning_experience_platform.premium.performance import performance_plan
from ui.learning_experience_platform.premium.pwa import pwa_config
from ui.learning_experience_platform.premium.responsive import layout_for_width
from ui.learning_experience_platform.premium.transitions import transition_plan


def test_motion_respects_reduce_motion():
    css_on = motion_css(reduce_motion=False)
    css_off = motion_css(reduce_motion=True)
    assert "lxpFade" in css_on
    assert "animation: none" in css_off
    assert animation_catalog()["policy"]["never_delay_content"] is True
    assert len(ANIMATION_PRESETS) >= 10


def test_performance_and_cache():
    plan = performance_plan()
    assert plan["lazy_load_diagrams"] and plan["virtual_scroll_threshold"] == 40
    cache_set("diagram:force", {"svg": "<svg/>"})
    assert cache_get("diagram:force")["svg"]
    assert cache_stats()["hits"] >= 1


def test_responsive_and_gestures():
    mobile = layout_for_width(375)
    assert mobile["device"] == "mobile" and mobile["touch_min_px"] == 44
    desk = layout_for_width(1440)
    assert desk["device"] == "desktop" and desk["split_screen"]
    g = gesture_map()
    assert g["keyboard_equivalents"] is True
    assert "swipe_nav" in g


def test_multilingual_no_auto_curriculum_translate():
    assert locale_meta("hi")["curriculum_policy"] == CURRICULUM_TRANSLATION_POLICY
    assert t("settings", "hi")
    assert locale_meta("ur")["dir"] == "rtl"


def test_accessibility_polish():
    audit = a11y_audit_checklist()
    assert audit["wcag"] == "2.2 AA"
    assert "?" in keyboard_shortcuts()


def test_offline_package_delta_conflict():
    learner = f"p4_{uuid.uuid4().hex[:8]}"
    pkg = build_full_package(
        learner_id=learner,
        lesson_id="force",
        lesson_payload={"title": "Force", "verified": True},
        notes=[{"text": "review"}],
        flashcards=[{"front": "F", "back": "force"}],
        preferences={"theme": "sepia"},
        progress={"reading_pct": 20, "updated_at": "2026-01-01T00:00:00+00:00"},
    )
    assert pkg["ok"] and pkg["package_id"]
    q = enqueue_delta(learner, "note", "n1", "upsert", {"text": "offline note"})
    assert q["ok"]
    status = sync_status(learner)
    assert status["pending"] >= 1
    processed = process_queue()
    assert processed["ok"]
    bg = background_sync(learner)
    assert bg["ok"] and bg["background"]

    conflict = detect_conflict(
        {"updated_at": "2026-01-01T00:00:00+00:00", "reading_pct": 40},
        {"updated_at": "2026-02-01T00:00:00+00:00", "reading_pct": 30},
    )
    assert conflict["conflict"]
    resolved = resolve_conflict(
        {"updated_at": "2026-01-01T00:00:00+00:00", "reading_pct": 40},
        {"updated_at": "2026-02-01T00:00:00+00:00", "reading_pct": 30},
    )
    assert resolved["ok"] and float(resolved["resolved"]["reading_pct"]) == 40


def test_settings_and_apis():
    learner = f"set_{uuid.uuid4().hex[:8]}"
    out = save_premium_settings(learner, {"language": "hi", "reduce_motion": True, "theme": "dark"})
    assert out["ok"] and out["settings"]["language"] == "hi"
    assert load_premium_settings(learner)["reduce_motion"] is True
    assert api_premium_settings(learner)["ok"]
    assert api_phase4(learner_id=learner)["ok"]
    assert api_phase4(learner_id=learner)["motion"]["reduce_motion"] is True
    assert api_phase4(learner_id=learner)["policy"]["never_auto_translate_curriculum"]
    assert api_sync_status(learner)["ok"]
    assert api_enqueue_delta(learner_id=learner, entity="bookmark", entity_id="b1", payload={"a": 1})["ok"]
    assert api_background_sync(learner)["ok"]
    assert api_experience_analytics(learner)["privacy"]["no_unnecessary_pii"]
    assert api_resolve_sync_conflict(
        local={"updated_at": "a", "reading_pct": 10},
        remote={"updated_at": "b", "reading_pct": 50},
    )["ok"]
    assert api_offline_package(
        learner_id=learner,
        lesson_id="L1",
        lesson_payload={"title": "Cells"},
    )["ok"]


def test_pwa_assets_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "static" / "lxp" / "manifest.webmanifest").is_file()
    assert (root / "static" / "lxp" / "sw.js").is_file()
    cfg = pwa_config()
    assert cfg["installable"] and cfg["graceful_fallback"]
    assert transition_plan(reduce_motion=True)["lesson_enter"] == "none"


def test_engine_includes_phase4():
    eng = LearningExperienceEngine()
    out = eng.process(
        {
            "learner_id": f"eng4_{uuid.uuid4().hex[:6]}",
            "lesson_text": "Force is a push or a pull.",
            "topic": "Force",
            "include_phase4": True,
        }
    )
    assert out.ok
    assert "phase4_premium_experience" in out.payload["phases"]
    assert out.payload["phase4"]["pwa"]["installable"]
    assert out.payload["policy"]["never_delay_learning_content"]


def test_regression_registry():
    reg = reset_registry()
    detail = reg.get("learning_experience").health_check().detail or ""
    assert "phases=1+2+3+4" in detail


def test_lxp_phase4_premium_experience_smoke(capsys):
    """LXP_PHASE4_PREMIUM_EXPERIENCE_SMOKE_OK"""
    learner = f"smoke_p4_{uuid.uuid4().hex[:8]}"
    save_premium_settings(learner, {"reduce_motion": True, "language": "en"})
    plan = api_phase4(learner_id=learner, device_type="mobile", screen_size=390)
    assert plan["ok"] and plan["motion"]["reduce_motion"]
    assert plan["performance"]["lazy_loading"]
    assert plan["offline"]["delta_sync"]
    assert plan["multilingual"]["curriculum_policy"] == "approved_bundles_only"
    assert plan["accessibility"]["wcag"].startswith("2.2")
    pkg = api_offline_package(learner_id=learner, lesson_id="smoke", lesson_payload={"title": "Smoke"})
    assert pkg["ok"]
    api_enqueue_delta(learner_id=learner, entity="progress", entity_id="p1", payload={"reading_pct": 5})
    assert api_background_sync(learner)["ok"]
    assert LearningExperienceEngine().process({"learner_id": learner, "lesson_text": "Smoke test lesson."}).ok
    assert Path(__file__).resolve().parents[1].joinpath("static/lxp/sw.js").is_file()

    with capsys.disabled():
        print("LXP_PHASE4_PREMIUM_EXPERIENCE_SMOKE_OK")
