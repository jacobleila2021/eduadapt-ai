"""Publisher Style Guide — single global visual/writing law for Alora lessons.

Phase Omega 2.0 / PMES. Renderers must consume these tokens; they must not invent
a competing palette or typography.
"""

from __future__ import annotations

from typing import Any

PHASE_OMEGA_2_PMES_SMOKE_OK = True
STYLE_GUIDE_VERSION = "2.0.0"

# Cream textbook canvas + publisher ink (Pearson/Oxford/Cambridge-adjacent)
CREAM = "#FFF9EE"
CREAM_CARD = "#FFFDF6"
NAVY = "#0B2E59"
TEAL = "#008C95"
INK = "#1C2A3A"
MUTED = "#5C6B7A"
SOFT_GOLD = "#C4A35A"
CORAL = "#C45C48"
LEAF = "#2F6B4F"
RULE = "#E2D6C2"

DISPLAY_FONT = "Georgia, 'Palatino Linotype', 'Book Antiqua', Palatino, serif"
BODY_FONT = "Candara, Calibri, 'Segoe UI', sans-serif"
MONO_FONT = "Consolas, 'Courier New', monospace"

MAX_SENTENCE_WORDS = 22
MAX_PARAGRAPH_SENTENCES = 4
MIN_PARAGRAPH_SENTENCES = 2
TARGET_SECTION_WORDS = (55, 140)

VOCAB_TERM_SIZE_PX = 34
VOCAB_CARD_MIN_HEIGHT_PX = 280
PAGE_MARGIN_PX = 28
SECTION_GAP_PX = 22

BANNED_AUTHORING = (
    "notice how",
    "core idea",
    "checkpoint",
    "learning objective",
    "students should",
    "students will",
    "memory tip",
    "scaffold",
    "worth mastering",
    "is a core idea",
    "as an ai",
    "in this section you will",
)

PUBLISHER_PALETTE: dict[str, str] = {
    "cream": CREAM,
    "cream_card": CREAM_CARD,
    "navy": NAVY,
    "teal": TEAL,
    "ink": INK,
    "muted": MUTED,
    "soft_gold": SOFT_GOLD,
    "coral": CORAL,
    "leaf": LEAF,
    "rule": RULE,
}

STYLE_GUIDE: dict[str, Any] = {
    "schema": "alora.publisher_style_guide.v2",
    "version": STYLE_GUIDE_VERSION,
    "writing": {
        "voice": "exceptional classroom teacher — warm, precise, curious",
        "max_sentence_words": MAX_SENTENCE_WORDS,
        "max_paragraph_sentences": MAX_PARAGRAPH_SENTENCES,
        "min_paragraph_sentences": MIN_PARAGRAPH_SENTENCES,
        "paragraph_must": [
            "introduce_curiosity",
            "build_understanding",
            "connect_prior_knowledge",
            "use_analogy_or_example",
            "end_with_natural_transition",
        ],
        "banned_phrases": list(BANNED_AUTHORING),
    },
    "visual": {
        "background": CREAM,
        "card_background": CREAM_CARD,
        "palette": PUBLISHER_PALETTE,
        "display_font": DISPLAY_FONT,
        "body_font": BODY_FONT,
        "page_margin_px": PAGE_MARGIN_PX,
        "section_gap_px": SECTION_GAP_PX,
        "no_dashboard_chrome": True,
        "diagrams_must_teach": True,
        "mermaid_discouraged": True,
    },
    "vocabulary": {
        "term_dominant": True,
        "term_capitalised": True,
        "term_size_px": VOCAB_TERM_SIZE_PX,
        "min_card_height_px": VOCAB_CARD_MIN_HEIGHT_PX,
        "required_fields": (
            "term",
            "pronunciation",
            "definition",
            "example_sentence",
            "memory_tip",
            "picture",
            "color",
        ),
        "layout": "premium_flashcard",
    },
    "diagrams": {
        "require_title": True,
        "require_caption": True,
        "require_explanation": True,
        "require_callouts": True,
        "require_practice_question": True,
        "svg_only_default": True,
        "background": CREAM,
    },
    "adaptations": {
        "author_new_lessons": True,
        "never_clone_wrap": True,
    },
}


def style_guide_css() -> str:
    """CSS tokens every lesson renderer must include. Do not override with grey dashboards."""
    return f"""
:root {{
  --alora-cream: {CREAM};
  --alora-cream-card: {CREAM_CARD};
  --alora-navy: {NAVY};
  --alora-teal: {TEAL};
  --alora-ink: {INK};
  --alora-muted: {MUTED};
  --alora-gold: {SOFT_GOLD};
  --alora-coral: {CORAL};
  --alora-leaf: {LEAF};
  --alora-rule: {RULE};
  --alora-display: {DISPLAY_FONT};
  --alora-body: {BODY_FONT};
  --alora-page-margin: {PAGE_MARGIN_PX}px;
  --alora-section-gap: {SECTION_GAP_PX}px;
  --alora-vocab-term: {VOCAB_TERM_SIZE_PX}px;
}}
.alora-publisher-page, .alora-lesson-shell, .stApp, [data-testid="stAppViewContainer"] {{
  background: var(--alora-cream) !important;
  color: var(--alora-ink);
  font-family: var(--alora-body);
}}
.alora-publisher-page h1, .alora-publisher-page h2, .alora-publisher-page h3,
.lce-vocab-term, .alora-word-wall-term {{
  font-family: var(--alora-display) !important;
  color: var(--alora-navy) !important;
  letter-spacing: 0.02em;
}}
.pmes-flashcard {{
  background: var(--alora-cream-card);
  border: 1px solid var(--alora-rule);
  border-radius: 18px;
  min-height: {VOCAB_CARD_MIN_HEIGHT_PX}px;
  padding: 1.35rem 1.4rem 1.5rem;
  box-shadow: 0 10px 28px rgba(11, 46, 89, 0.06);
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}}
.pmes-flashcard .lce-vocab-term {{
  font-size: var(--alora-vocab-term) !important;
  font-weight: 700 !important;
  text-transform: uppercase;
  line-height: 1.15;
  margin: 0.15rem 0 0.35rem;
}}
.pmes-flashcard .lce-vocab-meta {{
  color: var(--alora-muted);
  font-size: 0.92rem;
  margin: 0;
}}
.pmes-flashcard .lce-vocab-body p {{
  margin: 0.35rem 0;
  line-height: 1.55;
  font-size: 1.02rem;
}}
.pmes-diagram-figure {{
  background: var(--alora-cream-card);
  border: 1px solid var(--alora-rule);
  border-radius: 16px;
  padding: 1rem 1.1rem 1.25rem;
  margin: 1.1rem 0 1.4rem;
}}
.pmes-diagram-figure figcaption {{
  font-family: var(--alora-display);
  color: var(--alora-navy);
  font-size: 1.05rem;
  margin-top: 0.65rem;
}}
.pmes-diagram-explain, .pmes-diagram-practice {{
  color: var(--alora-ink);
  line-height: 1.55;
  margin: 0.45rem 0;
}}
""".strip()
