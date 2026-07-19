"""UI facade for advanced offline sync status."""

from __future__ import annotations

from typing import Any

import streamlit as st

from engines.learning_experience_platform.phase4_offline import (
    background_sync,
    build_full_package,
    enqueue_delta,
    sync_status,
)


def render_sync_indicator(learner_id: str) -> dict[str, Any]:
    status = sync_status(learner_id)
    state = status.get("state") or "idle"
    color = {"synced": "🟢", "syncing": "🟡", "conflict": "🟠", "error": "🔴", "offline": "⚪", "idle": "⚪"}.get(state, "⚪")
    st.caption(f"{color} Sync: **{state}** · pending {status.get('pending', 0)}")
    if st.button("Sync now", key=f"lxp4_sync_{learner_id}"):
        out = background_sync(learner_id)
        st.toast(f"Synced {len((out.get('result') or {}).get('processed') or [])} items")
        return out
    return status


def queue_offline_edit(learner_id: str, entity: str, entity_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return enqueue_delta(learner_id, entity, entity_id, "upsert", payload)


def download_full_package(**kwargs: Any) -> dict[str, Any]:
    return build_full_package(**kwargs)
