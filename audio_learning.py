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

from structured_renderers import _coerce_dict, content_to_export

VOICE_OPTIONS = {
    "Warm Female": {
        "openai": "nova",
        "hints": ["zira", "samantha", "susan", "karen", "hazel", "fiona", "google uk english female", "female"],
        "avoid": [],
    },
    "Warm Male": {
        "openai": "onyx",
        "hints": ["david", "daniel", "mark", "george", "james", "google uk english male"],
        "avoid": ["female"],
    },
    "Indian Female Professional": {
        "openai": "shimmer",
        "hints": ["heera", "kalpana", "swara", "priya", "veena", "raveena", "en-in", "english (india)", "hindi"],
        "avoid": ["male"],
    },
    "Indian Male Professional": {
        "openai": "onyx",
        "hints": ["ravi", "hemant", "prabhat", "madhur", "en-in", "english (india)"],
        "avoid": ["female", "heera", "kalpana"],
    },
}

PLAYBACK_SPEEDS = [0.75, 1.0, 1.25, 1.5, 1.75, 2.0]

OPENAI_VOICE_MAP = {label: meta["openai"] for label, meta in VOICE_OPTIONS.items()}


_MERMAID_BLOCK = re.compile(r"```mermaid.*?```", re.DOTALL | re.IGNORECASE)
_SVG_BLOCK = re.compile(r"<svg.*?</svg>", re.DOTALL | re.IGNORECASE)
_HTML_TAG = re.compile(r"<[^>]+>")
_MD_SYMBOLS = re.compile(r"[#*_`>\[\]|]")


def _clean_for_speech(text: str) -> str:
    """Strip diagrams, HTML, markdown and entities so only spoken prose remains."""
    if not text:
        return ""
    text = _MERMAID_BLOCK.sub(" ", text)
    text = _SVG_BLOCK.sub(" ", text)
    text = _HTML_TAG.sub(" ", text)
    text = html.unescape(text)
    text = _MD_SYMBOLS.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_narration(content: Any, spec_id: str) -> str:
    """
    Produce ONLY educational lesson content for the audio engine.

    Excludes adaptation names, section/navigation labels, button text,
    "Audio transcript", diagram markup and download hints.
    """
    parsed = _coerce_dict(content) if spec_id != "original" else None

    if spec_id == "vocabulary" and parsed:
        out: list[str] = []
        for word in parsed.get("word_wall") or []:
            term = (word.get("term") or "").strip()
            definition = _clean_for_speech(word.get("definition") or "")
            child = _clean_for_speech(word.get("child_friendly") or "")
            example = _clean_for_speech(word.get("example") or word.get("example_sentence") or "")
            if term and definition:
                out.append(f"{term}. {definition}")
            if child:
                out.append(child)
            if example:
                out.append(example)
        return " ".join(out)

    if spec_id == "worksheet" and parsed:
        out = []
        for item in (parsed.get("short_answer") or []) + (parsed.get("long_answer") or []):
            q = _clean_for_speech(item.get("question") or "")
            if q:
                out.append(q)
        return " ".join(out)

    if parsed:
        out = []
        big_idea = _clean_for_speech(parsed.get("big_idea") or "")
        if big_idea:
            out.append(big_idea)
        for section in parsed.get("sections") or []:
            body = _clean_for_speech(section.get("body") or "")
            if body:
                out.append(body)
        if out:
            return " ".join(out)

    # Plain/unstructured fallback: clean the raw content (never the title).
    return _clean_for_speech(str(content))


def extract_speech_text(title: str, content: Any, spec_id: str, max_chars: int = 4096) -> str:
    text = build_narration(content, spec_id)
    if not text:
        # Last-resort fallback keeps audio working but still excludes the title.
        raw = content_to_export("", content, spec_id)
        text = _clean_for_speech(raw)
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
    voice_avoid = VOICE_OPTIONS[voice_label].get("avoid", [])
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
      const voiceAvoid = {json.dumps(voice_avoid)};
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

      function isAvoided(v) {{
        const name = v.name.toLowerCase();
        return voiceAvoid.some(a => name.includes(a));
      }}

      function voiceMatches(v, hint) {{
        const name = v.name.toLowerCase();
        const lang = (v.lang || "").toLowerCase();
        return name.includes(hint) || lang.includes(hint);
      }}

      function pickVoice() {{
        const voices = speechSynthesis.getVoices();
        if (!voices.length) return null;
        for (const hint of voiceHints) {{
          const h = hint.toLowerCase();
          const match = voices.find(v => voiceMatches(v, h) && !isAvoided(v));
          if (match) return match;
        }}
        return voices.find(v => (v.lang || "").toLowerCase().startsWith("en") && !isAvoided(v))
            || voices.find(v => (v.lang || "").toLowerCase().startsWith("en"))
            || voices[0];
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
