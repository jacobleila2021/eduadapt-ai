"""Unified premium settings panel."""

from __future__ import annotations

from typing import Any

import streamlit as st

from engines.learning_experience_platform.phase4_schemas import SUPPORTED_UI_LOCALES
from engines.learning_experience_platform.phase4_settings import load_premium_settings, save_premium_settings
from ui.learning_experience_platform.premium.multilingual import t


def render_settings_panel(learner_id: str) -> dict[str, Any]:
    s = load_premium_settings(learner_id)
    st.subheader(t("settings", s.get("language") or "en"))
    c1, c2, c3 = st.columns(3)
    with c1:
        theme = st.selectbox("Theme", ["light", "dark", "sepia", "high_contrast"], index=["light", "dark", "sepia", "high_contrast"].index(s.get("theme") or "light") if (s.get("theme") or "light") in ["light", "dark", "sepia", "high_contrast"] else 0)
        language = st.selectbox("Language (UI)", list(SUPPORTED_UI_LOCALES), index=list(SUPPORTED_UI_LOCALES).index(s.get("language") or "en") if (s.get("language") or "en") in SUPPORTED_UI_LOCALES else 0)
    with c2:
        font = st.text_input("Font", s.get("font_family") or "Lexend")
        size = st.slider("Font size", 14, 32, int(s.get("font_size_px") or 18))
        reduce_motion = st.toggle(t("reduce_motion", s.get("language") or "en"), value=bool(s.get("reduce_motion")))
    with c3:
        audio = st.toggle("Audio", value=bool(s.get("audio_enabled", True)))
        companion = st.toggle("Companion", value=bool(s.get("companion_enabled", True)))
        notifications = st.toggle(t("notifications", s.get("language") or "en"), value=bool(s.get("notifications_enabled", True)))
        sync_auto = st.toggle("Auto sync", value=bool(s.get("sync_auto", True)))
        privacy = st.toggle("Anonymous UX analytics", value=bool(s.get("privacy_analytics", True)))
    offline_mb = st.slider("Offline storage (MB)", 64, 1024, int(s.get("offline_storage_mb") or 256))
    st.caption(t("curriculum_locked", language))
    if st.button("Save settings", key=f"lxp4_save_{learner_id}"):
        out = save_premium_settings(
            learner_id,
            {
                "theme": theme,
                "language": language,
                "font_family": font,
                "font_size_px": size,
                "reduce_motion": reduce_motion,
                "high_contrast": theme == "high_contrast",
                "audio_enabled": audio,
                "companion_enabled": companion,
                "notifications_enabled": notifications,
                "sync_auto": sync_auto,
                "privacy_analytics": privacy,
                "offline_storage_mb": offline_mb,
            },
        )
        st.toast("Settings saved · sync across devices when online")
        return out
    return {"ok": True, "settings": s}
