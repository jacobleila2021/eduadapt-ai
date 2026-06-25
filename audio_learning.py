"""
Adaptive Audio Learning — Warm voices, sticky toolbar, resume, cream transcript.
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
    "Warm Female": {
        "openai": "nova",
        "hints": ["female", "zira", "samantha", "susan", "karen", "hazel", "google uk english female"],
    },
    "Warm Male": {
        "openai": "onyx",
        "hints": ["male", "david", "daniel", "mark", "google uk english male", "james"],
    },
}

PLAYBACK_SPEEDS = [0.75, 1.0, 1.25, 1.5, 1.75, 2.0]

OPENAI_VOICE_MAP = {label: meta["openai"] for label, meta in VOICE_OPTIONS.items()}


def extract_speech_text(title: str, content: Any, spec_id: str, max_chars: int = 4096) -> str:
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
    if not text.strip() or not api_key:
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice=voice,
            input=text[:4096],
        )
        return response.content
    except Exception:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text[:4096],
            )
            return response.content
        except Exception:
            return None


def _audio_player_html(
    sentences: list[str],
    voice_label: str,
    speed: float,
    auditory_mode: bool,
    spec_id: str,
    storage_key: str,
) -> str:
    if voice_label not in VOICE_OPTIONS:
        voice_label = "Warm Female"
    voice_hints = VOICE_OPTIONS[voice_label]["hints"]
    payload = json.dumps(sentences)
    mode_class = "auditory-mode" if auditory_mode else ""
    default_font = "1.35rem" if auditory_mode else "1.25rem"

    if not sentences:
        sentences = ["No transcript text is available for this adaptation yet."]

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
    <div class="alora-audio-root {mode_class}" id="alora-audio-root">
      <div class="alora-audio-toolbar" id="alora-audio-toolbar">
        <div class="alora-audio-controls">
          <button type="button" id="btn-play" title="Play">▶ Play</button>
          <button type="button" id="btn-pause" title="Pause">⏸ Pause</button>
          <button type="button" id="btn-resume" title="Resume">⏵ Resume</button>
          <button type="button" id="btn-stop" title="Stop">⏹ Stop</button>
        </div>
        <div class="alora-audio-settings">
          <label>Voice <select id="voice-select">{voice_opts}</select></label>
          <label>Speed <select id="speed-select">{speed_opts}</select></label>
        </div>
      </div>
      <div class="alora-transcript-card" id="speech-text">
        <div class="alora-transcript-label">Audio transcript — follow the highlight</div>
        {sentence_blocks}
      </div>
      <div id="stop-dialog" class="alora-stop-dialog" hidden>
        <p>Resume from previous location?</p>
        <button type="button" id="btn-resume-yes">Yes — Resume</button>
        <button type="button" id="btn-resume-no">No — Start over</button>
      </div>
    </div>
    <style>
      .alora-audio-root {{
        font-family: "Atkinson Hyperlegible", "Comic Sans MS", Verdana, sans-serif;
        color: #334155;
      }}
      .alora-audio-toolbar {{
        position: sticky;
        top: 0;
        z-index: 1000;
        background: linear-gradient(135deg, #334155, #475569);
        border-radius: 14px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 0.85rem;
        color: #fff;
        box-shadow: 0 6px 22px rgba(51, 65, 85, 0.35);
      }}
      .alora-audio-controls, .alora-audio-settings {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        align-items: center;
      }}
      .alora-audio-settings {{
        margin-top: 0.55rem;
        font-size: 0.92rem;
      }}
      .alora-audio-root button {{
        background: #0F766E;
        color: #fff;
        border: none;
        border-radius: 999px;
        padding: 0.5rem 1rem;
        font-weight: 700;
        cursor: pointer;
        font-size: 0.88rem;
      }}
      .alora-audio-root button:hover {{ background: #0d9488; }}
      .alora-audio-root select {{
        background: #fff;
        border: 1px solid #7DD3C7;
        border-radius: 8px;
        padding: 0.35rem 0.5rem;
        margin-left: 0.35rem;
        color: #334155;
      }}
      .alora-transcript-card {{
        background: #F4E9D8;
        border: 2px solid #7DD3C7;
        border-radius: 14px;
        padding: 1.1rem 1.25rem;
        line-height: 1.9;
        font-size: {default_font};
        letter-spacing: 0.04em;
        min-height: 120px;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.5);
      }}
      .alora-transcript-label {{
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #0F766E;
        margin-bottom: 0.65rem;
      }}
      .speech-sentence {{
        margin: 0.55rem 0;
        padding: 0.45rem 0.65rem;
        border-radius: 8px;
        transition: background 0.2s, box-shadow 0.2s;
      }}
      .speech-sentence.active {{
        background: rgba(125, 211, 199, 0.55);
        box-shadow: inset 4px 0 0 #0F766E;
        font-weight: 600;
      }}
      .auditory-mode .speech-sentence {{ font-size: 1.3rem; }}
      .alora-stop-dialog {{
        margin-top: 0.75rem;
        padding: 0.85rem 1rem;
        background: #fff;
        border: 2px solid #F472B6;
        border-radius: 12px;
      }}
      .alora-stop-dialog button {{
        background: #F472B6;
        margin-right: 0.5rem;
      }}
    </style>
    <script>
    (function() {{
      const sentences = {payload};
      const voiceHints = {json.dumps(voice_hints)};
      const storageKey = {json.dumps(storage_key)};
      let idx = 0;
      let speaking = false;
      let paused = false;

      function loadPosition() {{
        try {{
          const raw = localStorage.getItem(storageKey);
          if (!raw) return;
          const data = JSON.parse(raw);
          if (typeof data.idx === "number" && data.idx >= 0 && data.idx < sentences.length) {{
            idx = data.idx;
          }}
          if (data.voice) {{
            const sel = document.getElementById("voice-select");
            if (sel) sel.value = data.voice;
          }}
          if (data.speed) {{
            const spd = document.getElementById("speed-select");
            if (spd) spd.value = data.speed;
          }}
        }} catch (e) {{}}
      }}

      function savePosition() {{
        try {{
          localStorage.setItem(storageKey, JSON.stringify({{
            idx: idx,
            voice: document.getElementById("voice-select").value,
            speed: document.getElementById("speed-select").value,
            spec: {json.dumps(spec_id)}
          }}));
        }} catch (e) {{}}
      }}

      function pickVoice() {{
        const voices = speechSynthesis.getVoices();
        if (!voices.length) return null;
        for (const hint of voiceHints) {{
          const h = hint.toLowerCase();
          const match = voices.find(v => v.name.toLowerCase().includes(h));
          if (match) return match;
        }}
        return voices.find(v => v.lang && v.lang.startsWith("en")) || voices[0];
      }}

      function highlight(i) {{
        document.querySelectorAll(".speech-sentence").forEach(el => el.classList.remove("active"));
        const el = document.querySelector('.speech-sentence[data-idx="' + i + '"]');
        if (el) {{
          el.classList.add("active");
          el.scrollIntoView({{behavior: "smooth", block: "center"}});
        }}
      }}

      function speakCurrent() {{
        if (idx >= sentences.length) {{
          speaking = false;
          paused = false;
          return;
        }}
        speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(sentences[idx]);
        utterance.voice = pickVoice();
        utterance.rate = parseFloat(document.getElementById("speed-select").value) || 1;
        utterance.pitch = 1;
        highlight(idx);
        utterance.onend = function() {{
          if (!speaking || paused) return;
          idx += 1;
          savePosition();
          speakCurrent();
        }};
        utterance.onerror = function() {{ speaking = false; paused = false; }};
        speechSynthesis.speak(utterance);
      }}

      document.getElementById("btn-play").onclick = function() {{
        paused = false;
        speaking = true;
        if (idx >= sentences.length) idx = 0;
        speakCurrent();
        savePosition();
      }};

      document.getElementById("btn-pause").onclick = function() {{
        if (speechSynthesis.speaking && !speechSynthesis.paused) {{
          speechSynthesis.pause();
          paused = true;
          savePosition();
        }}
      }};

      document.getElementById("btn-resume").onclick = function() {{
        if (speechSynthesis.paused) {{
          speechSynthesis.resume();
          paused = false;
          speaking = true;
          savePosition();
        }} else if (!speaking) {{
          speaking = true;
          paused = false;
          speakCurrent();
        }}
      }};

      document.getElementById("btn-stop").onclick = function() {{
        speechSynthesis.cancel();
        speaking = false;
        paused = false;
        savePosition();
        document.getElementById("stop-dialog").hidden = false;
      }};

      document.getElementById("btn-resume-yes").onclick = function() {{
        document.getElementById("stop-dialog").hidden = true;
        speaking = true;
        paused = false;
        speakCurrent();
      }};

      document.getElementById("btn-resume-no").onclick = function() {{
        document.getElementById("stop-dialog").hidden = true;
        idx = 0;
        savePosition();
        document.querySelectorAll(".speech-sentence").forEach(el => el.classList.remove("active"));
      }};

      document.getElementById("voice-select").onchange = savePosition;
      document.getElementById("speed-select").onchange = savePosition;

      loadPosition();
      if (speechSynthesis.onvoiceschanged !== undefined) {{
        speechSynthesis.onvoiceschanged = function() {{ pickVoice(); }};
      }}
      speechSynthesis.getVoices();
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
    """Sticky audio toolbar + cream transcript (all controls at top)."""
    speech_text = extract_speech_text(title, content, spec_id)
    if not speech_text:
        st.caption("No narration text available for this adaptation.")
        return

    voice = st.session_state.get("audio_voice", "Warm Female")
    if voice not in VOICE_OPTIONS:
        voice = "Warm Female"
        st.session_state.audio_voice = voice

    speed = float(st.session_state.get("audio_speed", 1.0))
    sentences = split_sentences(speech_text)
    storage_key = f"alora_audio_{spec_id}"

    st.markdown("#### 🔊 Adaptive Audio Learning")
    if auditory_mode:
        st.caption("Listening mode — controls stay fixed at the top while you read along.")

    components.html(
        _audio_player_html(
            sentences,
            voice,
            speed,
            auditory_mode,
            spec_id,
            storage_key,
        ),
        height=520 if auditory_mode else 460,
        scrolling=True,
    )
