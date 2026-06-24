"""
Adaptive Audio Learning — TTS extraction, OpenAI speech, browser playback UI.
"""

from __future__ import annotations

import html
import json
import re
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from structured_renderers import content_to_export

VOICE_OPTIONS = {
    "Female Professional": {"openai": "nova", "browser": "Google UK English Female"},
    "Male Professional": {"openai": "onyx", "browser": "Google UK English Male"},
    "Female Educator": {"openai": "shimmer", "browser": "Microsoft Zira Desktop"},
    "Male Educator": {"openai": "echo", "browser": "Microsoft David Desktop"},
    "Child-Friendly Voice": {"openai": "alloy", "browser": "Google US English"},
}

PLAYBACK_SPEEDS = [0.75, 1.0, 1.25, 1.5, 1.75, 2.0]

OPENAI_VOICE_MAP = {label: meta["openai"] for label, meta in VOICE_OPTIONS.items()}


def extract_speech_text(title: str, content: Any, spec_id: str, max_chars: int = 4096) -> str:
    """Plain text suitable for narration."""
    raw = content_to_export(title, content, spec_id)
    text = re.sub(r"[#*_`>\[\]|]", " ", raw)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_chars:
        text = text[: max_chars - 3].rsplit(" ", 1)[0] + "..."
    return text


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def generate_openai_speech(text: str, voice: str, api_key: str) -> bytes | None:
    """Generate MP3 via OpenAI TTS when API key is available."""
    if not text.strip() or not api_key:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
        )
        return response.content
    except Exception:
        return None


def _audio_player_html(
    sentences: list[str],
    voice_label: str,
    speed: float,
    auditory_mode: bool,
    cyan: str = "#14D9E5",
    navy: str = "#041B4D",
) -> str:
    browser_voice = VOICE_OPTIONS.get(voice_label, VOICE_OPTIONS["Female Professional"])["browser"]
    payload = json.dumps(sentences)
    mode_class = "auditory-mode" if auditory_mode else ""
    sentence_blocks = "".join(
        f'<p class="speech-sentence" data-idx="{i}">{html.escape(s)}</p>'
        for i, s in enumerate(sentences)
    )
    speed_opts = "".join(
        f'<option value="{s}"{" selected" if s == speed else ""}>{s}x</option>'
        for s in PLAYBACK_SPEEDS
    )
    voice_opts = "".join(
        f'<option value="{html.escape(v)}"{" selected" if v == voice_label else ""}>'
        f"{html.escape(v)}</option>"
        for v in VOICE_OPTIONS
    )

    return f"""
    <div class="alora-audio-panel {mode_class}" style="font-family:Inter,Arial,sans-serif;">
      <div class="audio-toolbar" style="background:linear-gradient(135deg,{navy},{navy}ee);
           border-radius:14px;padding:1rem 1.25rem;margin-bottom:1rem;color:#fff;">
        <div style="display:flex;flex-wrap:wrap;gap:0.5rem;align-items:center;margin-bottom:0.75rem;">
          <button type="button" id="btn-play" title="Play">▶ Play</button>
          <button type="button" id="btn-pause" title="Pause">⏸ Pause</button>
          <button type="button" id="btn-stop" title="Stop">⏹ Stop</button>
          <button type="button" id="btn-restart" title="Restart">↺ Restart</button>
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:1rem;align-items:center;font-size:0.9rem;">
          <label>Voice <select id="voice-select">{voice_opts}</select></label>
          <label>Speed <select id="speed-select">{speed_opts}</select></label>
        </div>
      </div>
      <div id="speech-text" style="line-height:1.85;font-size:{'1.15rem' if auditory_mode else '1rem'};">
        {sentence_blocks}
      </div>
    </div>
    <style>
      .alora-audio-panel button {{
        background:{cyan}; color:{navy}; border:none; border-radius:999px;
        padding:0.55rem 1.1rem; font-weight:600; cursor:pointer; font-size:0.9rem;
      }}
      .alora-audio-panel button:hover {{ filter:brightness(1.08); }}
      .alora-audio-panel select {{
        background:#fff; border:1px solid #ccc; border-radius:8px; padding:0.35rem 0.5rem;
        margin-left:0.35rem;
      }}
      .speech-sentence {{ margin:0.65rem 0; padding:0.35rem 0.5rem; border-radius:6px;
        transition:background 0.2s; }}
      .speech-sentence.active {{
        background:rgba(20,217,229,0.35); box-shadow:inset 3px 0 0 {cyan};
      }}
      .auditory-mode .speech-sentence {{ font-size:1.12rem; }}
    </style>
    <script>
    (function() {{
      const sentences = {payload};
      const preferredVoice = {json.dumps(browser_voice)};
      let idx = 0;
      let utterance = null;
      let speaking = false;

      function pickVoice(nameHint) {{
        const voices = speechSynthesis.getVoices();
        if (!voices.length) return null;
        const hint = (nameHint || "").toLowerCase();
        return voices.find(v => v.name.toLowerCase().includes(hint.split(" ")[0].toLowerCase()))
            || voices.find(v => v.lang.startsWith("en"))
            || voices[0];
      }}

      function highlight(i) {{
        document.querySelectorAll(".speech-sentence").forEach(el => el.classList.remove("active"));
        const el = document.querySelector('.speech-sentence[data-idx="' + i + '"]');
        if (el) {{ el.classList.add("active"); el.scrollIntoView({{behavior:"smooth", block:"center"}}); }}
      }}

      function speakCurrent() {{
        if (idx >= sentences.length) {{ speaking = false; return; }}
        utterance = new SpeechSynthesisUtterance(sentences[idx]);
        const voiceLabel = document.getElementById("voice-select").value;
        utterance.voice = pickVoice(preferredVoice);
        utterance.rate = parseFloat(document.getElementById("speed-select").value) || 1;
        highlight(idx);
        utterance.onend = function() {{ idx += 1; if (speaking) speakCurrent(); }};
        utterance.onerror = function() {{ speaking = false; }};
        speechSynthesis.speak(utterance);
      }}

      document.getElementById("btn-play").onclick = function() {{
        if (speechSynthesis.paused) {{ speechSynthesis.resume(); speaking = true; return; }}
        if (!speaking) {{ speaking = true; if (idx >= sentences.length) idx = 0; speakCurrent(); }}
      }};
      document.getElementById("btn-pause").onclick = function() {{ speechSynthesis.pause(); }};
      document.getElementById("btn-stop").onclick = function() {{
        speaking = false; speechSynthesis.cancel(); idx = 0;
        document.querySelectorAll(".speech-sentence").forEach(el => el.classList.remove("active"));
      }};
      document.getElementById("btn-restart").onclick = function() {{
        speechSynthesis.cancel(); idx = 0; speaking = true; speakCurrent();
      }};
      if (speechSynthesis.onvoiceschanged !== undefined) {{
        speechSynthesis.onvoiceschanged = function() {{ pickVoice(preferredVoice); }};
      }}
    }})();
    </script>
    """


def render_audio_learning_panel(
    title: str,
    content: Any,
    spec_id: str,
    api_key: str,
    auditory_mode: bool = False,
) -> None:
    """Audio controls + synchronized sentence highlighting (browser TTS)."""
    speech_text = extract_speech_text(title, content, spec_id)
    if not speech_text:
        st.caption("No narration text available for this adaptation.")
        return

    voice = st.session_state.get("audio_voice", "Female Professional")
    speed = float(st.session_state.get("audio_speed", 1.0))

    st.markdown("#### 🔊 Adaptive Audio Learning")
    if auditory_mode:
        st.caption("Listening-focused layout — follow the cyan highlight as narration plays.")

    sentences = split_sentences(speech_text)
    components.html(
        _audio_player_html(sentences, voice, speed, auditory_mode),
        height=420 if auditory_mode else 340,
        scrolling=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        voice = st.selectbox(
            "Voice selection",
            list(VOICE_OPTIONS.keys()),
            index=list(VOICE_OPTIONS.keys()).index(voice),
            key=f"audio_voice_sel_{spec_id}",
        )
        st.session_state.audio_voice = voice
    with col2:
        speed = st.selectbox(
            "Playback speed",
            PLAYBACK_SPEEDS,
            index=PLAYBACK_SPEEDS.index(speed) if speed in PLAYBACK_SPEEDS else 1,
            format_func=lambda x: f"{x}x",
            key=f"audio_speed_sel_{spec_id}",
        )
        st.session_state.audio_speed = speed
    with col3:
        openai_voice = OPENAI_VOICE_MAP.get(voice, "nova")
        mp3 = generate_openai_speech(speech_text, openai_voice, api_key)
        if mp3:
            st.download_button(
                "Download MP3",
                data=mp3,
                file_name=f"{spec_id}_narration.mp3",
                mime="audio/mpeg",
                use_container_width=True,
                key=f"dl_mp3_{spec_id}",
            )
        else:
            st.caption("MP3 via OpenAI TTS when API key is configured.")
