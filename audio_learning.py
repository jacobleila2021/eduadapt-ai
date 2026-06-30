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
    "Female": {
        "openai": "shimmer",
        "instructions": (
            "You are a warm, professional female teacher with a clear, neutral urban Indian "
            "English accent (well-spoken Mumbai or Bengaluru English). Read the lesson aloud "
            "to children with natural pacing, warm teacher-style delivery, clear pronunciation, "
            "and a child-friendly tone."
        ),
        "hints": ["heera", "kalpana", "swara", "priya", "veena", "raveena", "en-in", "english (india)", "hindi"],
        "avoid": ["male"],
    },
    "Male": {
        "openai": "echo",
        "instructions": (
            "You are a warm, professional male teacher with a clear, neutral urban Indian "
            "English accent (well-spoken Mumbai or Bengaluru English). Read the lesson aloud "
            "to children with natural pacing, warm teacher-style delivery, clear pronunciation, "
            "and a child-friendly tone."
        ),
        "hints": ["ravi", "hemant", "prabhat", "madhur", "en-in", "english (india)"],
        "avoid": ["female", "heera", "kalpana"],
    },
}

from lesson_design import get_audio_passage_css

DEFAULT_VOICE = "Female"

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


def generate_openai_speech(
    text: str, voice: str, api_key: str, instructions: str = ""
) -> bytes | None:
    """Generate expressive neural speech. Tries gpt-4o-mini-tts (accent/tone steerable),
    then falls back to tts-1-hd and tts-1."""
    if not text.strip() or not api_key:
        return None
    try:
        from openai import OpenAI
    except Exception:
        return None

    client = OpenAI(api_key=api_key)
    attempts = [
        ("gpt-4o-mini-tts", True),
        ("tts-1-hd", False),
        ("tts-1", False),
    ]
    for model, supports_instructions in attempts:
        try:
            kwargs: dict[str, Any] = {
                "model": model,
                "voice": voice,
                "input": text[:4096],
            }
            if supports_instructions and instructions:
                kwargs["instructions"] = instructions
            response = client.audio.speech.create(**kwargs)
            return response.content
        except Exception:
            continue
    return None


def _audio_player_styles(font_px: int = 24) -> str:
    return f"<style>{get_audio_passage_css(font_px)}</style>"


def _transcript_html(sentences: list[str], font_px: int = 24) -> str:
    """Reading passage only — playback controls live in Streamlit (st.audio / sticky toolbar)."""
    if not sentences:
        sentences = ["No transcript text is available for this adaptation yet."]
    blocks = "".join(
        f'<p class="speech-sentence">{html.escape(s)}</p>' for s in sentences
    )
    return f"""
    <div class="alora-audio-root">
      <div class="alora-transcript-card">{blocks}</div>
    </div>
    {_audio_player_styles(font_px)}
    """


def _openai_controls_html(
    audio_b64: str,
    sentences: list[str],
    speed: float,
    storage_key: str,
    font_px: int = 24,
) -> str:
    """Sticky toolbar + hidden audio element (transcript rendered separately)."""
    speed_opts = "".join(
        f'<option value="{s}"{" selected" if s == speed else ""}>{s}x</option>'
        for s in PLAYBACK_SPEEDS
    )
    lengths = [max(len(s), 1) for s in sentences]

    return f"""
    <div class="alora-audio-root" id="alora-audio-root">
      <audio id="alora-audio" preload="auto" src="data:audio/mpeg;base64,{audio_b64}"></audio>
      <div class="alora-audio-toolbar">
        <div class="alora-audio-controls">
          <button type="button" id="btn-play">▶ Play</button>
          <button type="button" id="btn-pause">⏸ Pause</button>
          <button type="button" id="btn-resume">⏵ Resume</button>
          <button type="button" id="btn-stop">⏹ Stop</button>
        </div>
        <div class="alora-audio-settings">
          <label>Speed <select id="speed-select">{speed_opts}</select></label>
        </div>
      </div>
    </div>
    {_audio_player_styles(font_px)}
    <script>
    (function() {{
      const audio = document.getElementById("alora-audio");
      const lengths = {json.dumps(lengths)};
      const storageKey = {json.dumps(storage_key)};
      function applySpeed() {{
        audio.playbackRate = parseFloat(document.getElementById("speed-select").value) || 1;
      }}
      audio.addEventListener("loadedmetadata", function() {{
        try {{ const p = parseFloat(localStorage.getItem(storageKey)); if (p > 0 && p < audio.duration) audio.currentTime = p; }} catch (e) {{}}
      }});
      audio.addEventListener("timeupdate", function() {{
        try {{ localStorage.setItem(storageKey, audio.currentTime); }} catch (e) {{}}
      }});
      audio.addEventListener("ended", function() {{
        try {{ localStorage.setItem(storageKey, 0); }} catch (e) {{}}
      }});
      document.getElementById("speed-select").onchange = applySpeed;
      document.getElementById("btn-play").onclick = function() {{ applySpeed(); audio.play(); }};
      document.getElementById("btn-pause").onclick = function() {{ audio.pause(); }};
      document.getElementById("btn-resume").onclick = function() {{ applySpeed(); audio.play(); }};
      document.getElementById("btn-stop").onclick = function() {{
        audio.pause(); audio.currentTime = 0;
        try {{ localStorage.setItem(storageKey, 0); }} catch (e) {{}}
      }};
      applySpeed();
    }})();
    </script>
    """


def _openai_audio_player_html(
    audio_b64: str,
    sentences: list[str],
    speed: float,
    spec_id: str,
    storage_key: str,
    default_font: str,
    font_px: int = 21,
) -> str:
    """Native <audio> player (premium neural voice) with timed transcript highlight."""
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
    lengths = [max(len(s), 1) for s in sentences]

    return f"""
    <div class="alora-audio-root" id="alora-audio-root">
      <audio id="alora-audio" preload="auto" src="data:audio/mpeg;base64,{audio_b64}"></audio>
      <div class="alora-audio-toolbar">
        <div class="alora-audio-controls">
          <button type="button" id="btn-play">▶ Play</button>
          <button type="button" id="btn-pause">⏸ Pause</button>
          <button type="button" id="btn-resume">⏵ Resume</button>
          <button type="button" id="btn-stop">⏹ Stop</button>
        </div>
        <div class="alora-audio-settings">
          <label>Speed <select id="speed-select">{speed_opts}</select></label>
        </div>
      </div>
      <div class="alora-transcript-card" id="speech-text">
        {sentence_blocks}
      </div>
    </div>
    {_audio_player_styles(font_px)}
    <script>
    (function() {{
      const audio = document.getElementById("alora-audio");
      const lengths = {json.dumps(lengths)};
      const storageKey = {json.dumps(storage_key)};
      let bounds = [];
      function computeBounds() {{
        const total = lengths.reduce((a, b) => a + b, 0) || 1;
        let acc = 0;
        bounds = lengths.map(l => {{ acc += l; return acc / total; }});
      }}
      function scrollActiveSentence(el) {{
        if (!el) return;
        el.scrollIntoView({{behavior: "smooth", block: "center"}});
        try {{
          let childWin = window;
          while (childWin && childWin !== childWin.parent) {{
            const parentWin = childWin.parent;
            const frame = childWin.frameElement;
            if (frame && parentWin) {{
              const rect = el.getBoundingClientRect();
              const frameRect = frame.getBoundingClientRect();
              const target = parentWin.scrollY + frameRect.top + rect.top
                - (parentWin.innerHeight / 2) + (rect.height / 2);
              parentWin.scrollTo({{top: Math.max(0, target), behavior: "smooth"}});
            }}
            childWin = parentWin;
          }}
        }} catch (e) {{}}
      }}
      function highlight() {{
        if (!audio.duration || !isFinite(audio.duration)) return;
        const frac = audio.currentTime / audio.duration;
        let i = bounds.findIndex(b => frac <= b);
        if (i < 0) i = lengths.length - 1;
        document.querySelectorAll(".speech-sentence").forEach(el => el.classList.remove("active"));
        const el = document.querySelector('.speech-sentence[data-idx="' + i + '"]');
        if (el) {{ el.classList.add("active"); scrollActiveSentence(el); }}
      }}
      function applySpeed() {{
        audio.playbackRate = parseFloat(document.getElementById("speed-select").value) || 1;
      }}
      computeBounds();
      audio.addEventListener("loadedmetadata", function() {{
        computeBounds();
        try {{ const p = parseFloat(localStorage.getItem(storageKey)); if (p > 0 && p < audio.duration) audio.currentTime = p; }} catch (e) {{}}
      }});
      audio.addEventListener("timeupdate", function() {{
        highlight();
        try {{ localStorage.setItem(storageKey, audio.currentTime); }} catch (e) {{}}
      }});
      audio.addEventListener("ended", function() {{
        document.querySelectorAll(".speech-sentence").forEach(el => el.classList.remove("active"));
        try {{ localStorage.setItem(storageKey, 0); }} catch (e) {{}}
      }});
      document.getElementById("speed-select").onchange = applySpeed;
      document.getElementById("btn-play").onclick = function() {{ applySpeed(); audio.play(); }};
      document.getElementById("btn-pause").onclick = function() {{ audio.pause(); }};
      document.getElementById("btn-resume").onclick = function() {{ applySpeed(); audio.play(); }};
      document.getElementById("btn-stop").onclick = function() {{
        audio.pause(); audio.currentTime = 0;
        document.querySelectorAll(".speech-sentence").forEach(el => el.classList.remove("active"));
        try {{ localStorage.setItem(storageKey, 0); }} catch (e) {{}}
      }};
      applySpeed();
    }})();
    </script>
    """


def _audio_player_html(
    sentences: list[str],
    voice_label: str,
    speed: float,
    auditory_mode: bool,
    spec_id: str,
    storage_key: str,
) -> str:
    if voice_label not in VOICE_OPTIONS:
        voice_label = DEFAULT_VOICE
    voice_hints = VOICE_OPTIONS[voice_label]["hints"]
    voice_avoid = VOICE_OPTIONS[voice_label].get("avoid", [])
    payload = json.dumps(sentences)
    mode_class = "auditory-mode" if auditory_mode else ""
    font_px = 26 if auditory_mode else 24

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
        {sentence_blocks}
      </div>
      <div id="stop-dialog" class="alora-stop-dialog" hidden>
        <p>Resume from previous location?</p>
        <button type="button" id="btn-resume-yes">Yes — Resume</button>
        <button type="button" id="btn-resume-no">No — Start over</button>
      </div>
    </div>
    {_audio_player_styles(font_px)}
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

      function scrollActiveSentence(el) {{
        if (!el) return;
        el.scrollIntoView({{behavior: "smooth", block: "center"}});
        try {{
          let childWin = window;
          while (childWin && childWin !== childWin.parent) {{
            const parentWin = childWin.parent;
            const frame = childWin.frameElement;
            if (frame && parentWin) {{
              const rect = el.getBoundingClientRect();
              const frameRect = frame.getBoundingClientRect();
              const target = parentWin.scrollY + frameRect.top + rect.top
                - (parentWin.innerHeight / 2) + (rect.height / 2);
              parentWin.scrollTo({{top: Math.max(0, target), behavior: "smooth"}});
            }}
            childWin = parentWin;
          }}
        }} catch (e) {{}}
      }}

      function highlight(i) {{
        document.querySelectorAll(".speech-sentence").forEach(el => el.classList.remove("active"));
        const el = document.querySelector('.speech-sentence[data-idx="' + i + '"]');
        if (el) {{
          el.classList.add("active");
          scrollActiveSentence(el);
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
    *,
    show_heading: bool = True,
) -> None:
    """Premium neural audio (OpenAI) with reliable Play/Pause/Resume/Stop/Speed and a
    Streamlit-controlled voice selector. Falls back to browser TTS when no API key."""
    import base64

    speech_text = extract_speech_text(title, content, spec_id)
    if not speech_text:
        st.caption("No narration text available for this adaptation.")
        return

    voice = st.session_state.get("audio_voice", DEFAULT_VOICE)
    if voice not in VOICE_OPTIONS:
        voice = DEFAULT_VOICE
        st.session_state.audio_voice = voice

    speed = float(st.session_state.get("audio_speed", 1.0))
    sentences = split_sentences(speech_text)
    storage_key = f"alora_audio_{spec_id}_{voice}"
    font_px = 26 if auditory_mode else 24

    st.markdown(
        '<div class="alora-audio-sticky-start" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="alora-audio-stick" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    if show_heading:
        st.markdown("#### 🔊 Adaptive Audio Learning")

    voice_labels = list(VOICE_OPTIONS.keys())
    ctrl1, ctrl2 = st.columns(2)
    with ctrl1:
        selected = st.selectbox(
            "Voice",
            voice_labels,
            index=voice_labels.index(voice),
            key=f"voice_select_{spec_id}",
        )
    with ctrl2:
        speed = st.selectbox(
            "Speed",
            PLAYBACK_SPEEDS,
            index=PLAYBACK_SPEEDS.index(speed) if speed in PLAYBACK_SPEEDS else 1,
            format_func=lambda s: f"{s}x",
            key=f"audio_speed_select_{spec_id}",
        )
        st.session_state.audio_speed = speed

    if selected != voice:
        st.session_state.audio_voice = selected
        voice = selected
        storage_key = f"alora_audio_{spec_id}_{voice}"

    meta = VOICE_OPTIONS[voice]

    audio_bytes: bytes | None = None
    if api_key:
        cache_key = f"_audio_cache_{spec_id}"
        signature = f"{voice}|{hash(speech_text)}"
        cached = st.session_state.get(cache_key)
        if isinstance(cached, dict) and cached.get("sig") == signature:
            audio_bytes = cached.get("bytes")
        else:
            with st.spinner(f"Preparing {voice} narration…"):
                audio_bytes = generate_openai_speech(
                    speech_text, meta["openai"], api_key, meta.get("instructions", "")
                )
            if audio_bytes:
                st.session_state[cache_key] = {"sig": signature, "bytes": audio_bytes}

    if audio_bytes:
        b64 = base64.b64encode(audio_bytes).decode("ascii")
        st.markdown(
            '<div class="alora-audio-stick" aria-hidden="true"></div>',
            unsafe_allow_html=True,
        )
        components.html(
            _openai_audio_player_html(
                b64, sentences, speed, spec_id, storage_key, f"{font_px}px", font_px
            ),
            height=620 if auditory_mode else 560,
            scrolling=True,
        )
        return

    if api_key:
        st.caption(
            "Premium neural narration is temporarily unavailable — using your browser voice."
        )
    st.markdown(
        '<div class="alora-audio-stick" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )
    components.html(
        _audio_player_html(
            sentences,
            voice,
            speed,
            auditory_mode,
            spec_id,
            storage_key,
        ),
        height=560 if auditory_mode else 500,
        scrolling=True,
    )
