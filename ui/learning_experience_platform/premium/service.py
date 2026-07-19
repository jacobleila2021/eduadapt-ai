"""Premium experience UI service — injects CSS/PWA/settings into LXP."""

from __future__ import annotations

from typing import Any
import time

import streamlit as st

from engines.learning_experience_platform.phase4 import build_phase4
from engines.learning_experience_platform.phase4_settings import load_premium_settings
from ui.learning_experience_platform.premium.accessibility import a11y_css, keyboard_shortcuts
from ui.learning_experience_platform.premium.animations import motion_css
from ui.learning_experience_platform.premium.gestures import gesture_map
from ui.learning_experience_platform.premium.loading_states import render_skeleton
from ui.learning_experience_platform.premium.multilingual import locale_meta, t
from ui.learning_experience_platform.premium.notifications import render_notification_center
from ui.learning_experience_platform.premium.offline_sync import render_sync_indicator
from ui.learning_experience_platform.premium.performance import mark_page_load, performance_plan
from ui.learning_experience_platform.premium.pwa import pwa_config, render_install_hint
from ui.learning_experience_platform.premium.responsive import layout_for_width
from ui.learning_experience_platform.premium.settings import render_settings_panel
from ui.learning_experience_platform.premium.transitions import transition_plan


def inject_premium_chrome(*, learner_id: str, width_px: int | None = None) -> dict[str, Any]:
    """Apply motion/a11y CSS and return phase4 plan. Never blocks content."""
    started = time.monotonic()
    settings = load_premium_settings(learner_id)
    reduce_motion = bool(settings.get("reduce_motion"))
    high_contrast = bool(settings.get("high_contrast") or settings.get("theme") == "high_contrast")
    st.markdown(motion_css(reduce_motion=reduce_motion), unsafe_allow_html=True)
    st.markdown(a11y_css(high_contrast=high_contrast), unsafe_allow_html=True)
    st.markdown('<div class="lxp-premium" aria-live="polite"></div>', unsafe_allow_html=True)

    plan = build_phase4({"learner_id": learner_id, "reduce_motion": reduce_motion, "screen_size": width_px})
    plan["ui"] = {
        "layout": layout_for_width(width_px),
        "performance": performance_plan(),
        "transitions": transition_plan(reduce_motion=reduce_motion),
        "gestures": gesture_map(),
        "locale": locale_meta(str(settings.get("language") or "en")),
        "pwa": pwa_config(),
        "shortcuts": keyboard_shortcuts(),
    }
    mark_page_load(started, learner_id=learner_id)
    return plan


def render_premium_panel(*, learner_id: str) -> None:
    """Settings / sync / notifications / PWA — secondary panel; content stays primary."""
    settings = load_premium_settings(learner_id)
    lang = str(settings.get("language") or "en")
    tabs = st.tabs([t("settings", lang), t("sync", lang), t("notifications", lang), t("install_app", lang)])
    with tabs[0]:
        render_settings_panel(learner_id)
        with st.expander("Keyboard shortcuts"):
            for k, v in keyboard_shortcuts().items():
                st.caption(f"`{k}` — {v}")
    with tabs[1]:
        render_sync_indicator(learner_id)
    with tabs[2]:
        render_notification_center(learner_id)
    with tabs[3]:
        st.info(render_install_hint())
        st.code(pwa_config()["manifest"])
        st.caption("Service worker registers when static assets are served.")


def render_premium_loading() -> None:
    render_skeleton()
