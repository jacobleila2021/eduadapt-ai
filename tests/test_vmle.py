"""Voice & Multimodal Learning Experience — unit, integration, smoke tests."""

from __future__ import annotations

from engines.verified_learning_engine import reset_registry, get_registry
from engines.voice_multimodal_learning import VoiceMultimodalEngine
from engines.voice_multimodal_learning.conversation import parse_voice_command
from engines.voice_multimodal_learning.highlighting import build_highlight_timeline
from engines.voice_multimodal_learning.narration import plan_narration
from engines.voice_multimodal_learning.offline import cache_lesson_bundle, synchronize, list_cached
from engines.voice_multimodal_learning.pronunciation import coach, syllable_breakdown
from engines.voice_multimodal_learning.read_along import create_read_along_state, pause, resume
from engines.voice_multimodal_learning.service import (
    api_interactive_content,
    api_multilingual_settings,
    api_pronunciation_feedback,
    api_read_along_state,
    api_speech_to_text,
    api_start_voice_session,
    api_end_voice_session,
    api_text_to_speech,
    api_usage_analytics,
    api_voice_command,
)
from engines.voice_multimodal_learning.speech_to_text import transcribe
from engines.voice_multimodal_learning.accessibility import apply_aie
from engines.voice_multimodal_learning.text_to_speech import synthesize_speech


def test_registry_includes_voice_multimodal():
    reg = reset_registry()
    ids = {e["engine_id"] for e in reg.list_engines()}
    assert "voice_multimodal" in ids
    eng = reg.get("voice_multimodal")
    assert eng is not None
    assert eng.engine_id == "voice_multimodal"


def test_engine_process_plan():
    eng = VoiceMultimodalEngine()
    result = eng.process(
        {
            "lesson_text": "A plant cell has a chloroplast for photosynthesis.",
            "topic": "cell structure",
            "engine_outputs": {
                "accessibility": {
                    "ok": True,
                    "payload": {
                        "presentation": {"primary_mode": "auditory"},
                        "learner_profile": {"active_profiles": ["dyslexia"]},
                    },
                },
                "scientific_accuracy": {"ok": True, "payload": {"artifacts": [{"kind": "biology", "payload": {"svg": "x"}}]}},
            },
        }
    )
    assert result.ok
    assert result.payload["narration"]["text"]
    assert result.payload["accessibility"]["dyslexia_friendly_reading"]
    assert result.payload["policy"]["atie_is_teaching_intelligence"]


def test_narration_and_highlighting():
    plan = plan_narration("Cells make up tissues. Tissues make organs.", spec_id="original")
    assert plan.sentences
    tl = build_highlight_timeline(plan.sentences, plan.paragraphs, plan.text, mode="sentence")
    assert tl and tl[0]["start_ms"] == 0
    state = create_read_along_state(plan)
    assert state["total_units"] >= 1
    assert resume(pause(state))["playing"] is True


def test_voice_commands():
    assert parse_voice_command("Please slow down")["command"] == "slow_down"
    assert parse_voice_command("Ask my tutor about cells")["command"] == "ask_my_tutor"
    assert api_voice_command("Show the diagram")["command"] == "show_the_diagram"


def test_stt_and_tts_headless():
    stt = transcribe(transcript_hint="What is a chloroplast")
    assert stt["ok"] and stt["confidence"] > 0
    tts = synthesize_speech("Chloroplasts capture light energy.", voice_style="Female")
    assert tts["ok"]
    assert tts["provider"] in ("openai", "browser_tts")
    api_tts = api_text_to_speech("Hello lesson.", include_audio_bytes=False)
    assert api_tts["ok"]


def test_pronunciation_coaching():
    syllables = syllable_breakdown("photosynthesis")
    assert len(syllables) >= 3
    attempt = coach("chloroplast", heard="chloroplast")
    assert attempt.accuracy == 1.0
    fb = api_pronunciation_feedback("mitochondria", heard="mito")
    assert fb["ok"] and fb["card"]["actions"] == ["listen", "repeat", "compare"]


def test_offline_sync():
    cached = cache_lesson_bundle(learner_id="u1", lesson_id="ch8", lesson_text="Cell wall protects the cell.")
    assert cached["ok"]
    assert any(c["cache_id"] == cached["cache_id"] for c in list_cached("u1"))
    synced = synchronize(cached["cache_id"])
    assert synced["ok"] and synced["synced"] is True


def test_accessibility_and_multilingual():
    a11y = apply_aie(
        {
            "engine_outputs": {
                "accessibility": {"payload": {"learner_profile": {"active_profiles": ["adhd", "dyslexia"]}}}
            }
        }
    )
    assert a11y["adhd_focus_mode"] and a11y["policy"].startswith("accessibility")
    lang = api_multilingual_settings(language="hi", dual_language=True)
    assert lang["ok"] and lang["dual_language_mode"] is True


def test_interactive_content_policy():
    out = api_interactive_content(topic="electricity circuit", engine_outputs={})
    assert out["ok"]
    assert out["content"]["policy"] == "deterministic_engines_only"
    assert "circuit_simulations" in out["content"]["physics"]["capabilities"]


def test_session_apis_and_analytics():
    started = api_start_voice_session("learner_vmle", lesson_id="L1")
    assert started["ok"]
    sid = started["session"]["session_id"]
    assert api_speech_to_text(transcript_hint="Explain photosynthesis")["ok"]
    assert api_read_along_state(lesson_text="Sunlight helps plants make food.")["ok"]
    assert api_usage_analytics(sid)["ok"]
    assert api_end_voice_session(sid)["ok"]


def test_legacy_engines_still_registered():
    """Regression — VMLE registration must not drop core engines."""
    reg = get_registry()
    ids = {e["engine_id"] for e in reg.list_engines()}
    for required in ("curriculum", "assessment", "accessibility", "adaptive_learning", "ai_tutor", "learning_analytics"):
        assert required in ids


def test_vmle_smoke(capsys):
    """VMLE_SMOKE_OK via standard pytest."""
    reg = reset_registry()
    assert reg.get("voice_multimodal")
    health = reg.get("voice_multimodal").health_check()
    assert health.ok

    eng = VoiceMultimodalEngine()
    bundle = eng.process({"lesson_text": "H2O is water. Force is a push or pull.", "topic": "force"})
    assert bundle.ok
    assert bundle.payload["narration"]["source"] == "verified_lesson"

    session = api_start_voice_session("smoke", lesson_id="smoke")
    sid = session["session"]["session_id"]
    assert parse_voice_command("Start quiz")["command"] == "start_quiz"
    assert coach("force", heard="force").accuracy == 1.0
    cache = cache_lesson_bundle(learner_id="smoke", lesson_id="smoke", lesson_text="Force")
    assert synchronize(cache["cache_id"])["ok"]
    api_end_voice_session(sid)

    with capsys.disabled():
        print("VMLE_SMOKE_OK")
