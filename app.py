"""
Alora AI — Main Streamlit application.
Dashboard + dedicated adaptation workspace (never stacked on homepage).
"""

import json
import traceback

import streamlit as st

st.set_page_config(
    page_title="Alora AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SAMPLE_LESSON_PATH = PROJECT_ROOT / "samples" / "sample_lesson.docx"
ALORA_LOGO = PROJECT_ROOT / "assets" / "alora_logo.png"

try:
    from adaptation_specs import ADAPTATION_SPECS
    from ai_generator import generate_adaptations, quality_report, validate_api_key
    from analytics_engine import build_analytics_report
    from docx_exporter import build_zip_bundle
    from document_parser import extract_lesson_text
    from config import APP_NAME
    from navigation import category_for_spec, default_spec_for_category
    from secrets_helper import is_valid_openai_key, read_api_key_from_env_file
    from session_state import (
        VIEW_WORKSPACE,
        clear_stale_url_params,
        close_workspace,
        init_navigation_state,
        should_render_workspace,
    )
    from structured_renderers import content_to_export
    from styles import get_custom_css
    from version import APP_VERSION
    from workspace_page import render_workspace
    from ui_helpers import (
        render_analytics_panel,
        render_dashboard_intro,
        render_pill_navigation,
        render_sidebar,
        render_top_nav,
    )
except Exception as import_error:
    st.error("Alora AI could not start. Details below (share with support if needed):")
    st.code(traceback.format_exc())
    st.info(
        "Common fix: Streamlit **Settings → Secrets** must include "
        "`OPENAI_API_KEY`. Also confirm **Manage app → Logs** shows a successful pip install."
    )
    st.stop()

init_navigation_state()

if "lesson_text" not in st.session_state:
    st.session_state.lesson_text = ""
if "adaptations" not in st.session_state:
    st.session_state.adaptations = None
if "analytics" not in st.session_state:
    st.session_state.analytics = None
if "upload_name" not in st.session_state:
    st.session_state.upload_name = ""
if "runtime_api_key" not in st.session_state:
    st.session_state.runtime_api_key = ""
if "last_saved_api_key" not in st.session_state:
    st.session_state.last_saved_api_key = ""
if "quality" not in st.session_state:
    st.session_state.quality = None
if "auditory_mode" not in st.session_state:
    st.session_state.auditory_mode = False
if "audio_voice" not in st.session_state:
    st.session_state.audio_voice = "Warm Female"
if "audio_speed" not in st.session_state:
    st.session_state.audio_speed = 1.0


def save_api_key_to_env(api_key: str) -> None:
    env_path = PROJECT_ROOT / ".env"
    env_path.write_text(
        f"OPENAI_API_KEY={api_key}\nOPENAI_MODEL=gpt-4o-mini\n",
        encoding="utf-8",
    )


def load_api_key_from_env_file() -> None:
    env_key = read_api_key_from_env_file()
    if env_key:
        st.session_state.runtime_api_key = env_key
        st.session_state.last_saved_api_key = env_key


def apply_lesson(name: str, text: str) -> None:
    st.session_state.lesson_text = text
    st.session_state.upload_name = name
    st.session_state.adaptations = None
    st.session_state.analytics = build_analytics_report(text)
    close_workspace()


def _upload_fingerprint(uploaded_file) -> str:
    return f"{uploaded_file.name}:{uploaded_file.size}"


def handle_file_upload(uploaded_file) -> None:
    if uploaded_file is None:
        return
    fingerprint = _upload_fingerprint(uploaded_file)
    if st.session_state.get("_processed_upload_key") == fingerprint:
        return
    try:
        file_bytes = uploaded_file.read()
        text = extract_lesson_text(uploaded_file.name, file_bytes)
    except ValueError as error:
        st.error(str(error))
        return
    except Exception as error:
        st.error(f"Could not read file: {error}")
        return
    if not text.strip():
        st.warning("No text found in this file. Try a different PDF or DOCX.")
        return
    st.session_state._processed_upload_key = fingerprint
    apply_lesson(uploaded_file.name, text)
    st.success(f"Loaded: **{uploaded_file.name}** ({len(text):,} characters)")


def ensure_sample_lesson_exists() -> bool:
    if SAMPLE_LESSON_PATH.exists():
        return True
    try:
        from create_sample_lesson import main as create_sample

        create_sample()
        return SAMPLE_LESSON_PATH.exists()
    except Exception as error:
        st.error(f"Could not create sample lesson: {error}")
        return False


def load_sample_lesson() -> None:
    if not ensure_sample_lesson_exists():
        return
    try:
        file_bytes = SAMPLE_LESSON_PATH.read_bytes()
        text = extract_lesson_text(SAMPLE_LESSON_PATH.name, file_bytes)
    except Exception as error:
        st.error(f"Could not load sample lesson: {error}")
        return
    if not text.strip():
        st.warning("Sample lesson file is empty. Try uploading your own file.")
        return
    st.session_state._processed_upload_key = f"{SAMPLE_LESSON_PATH.name}:sample"
    apply_lesson(SAMPLE_LESSON_PATH.name, text)
    st.success(f"Loaded: **{SAMPLE_LESSON_PATH.name}** ({len(text):,} characters)")


def run_generation() -> None:
    if not st.session_state.lesson_text.strip():
        st.warning("Upload a lesson first.")
        return
    if not validate_api_key(st.session_state.runtime_api_key):
        st.error(
            "AI service is not configured. Open **Administrator settings** in the sidebar "
            "or contact your platform administrator."
        )
        return

    with st.spinner("Starting…"):
        progress = st.progress(0, text="Preparing…")
        status = st.empty()

        def on_progress(message: str, fraction: float) -> None:
            progress.progress(min(max(fraction, 0.0), 1.0), text=message)
            status.caption(message)

        try:
            st.session_state.adaptations = generate_adaptations(
                st.session_state.lesson_text,
                override_api_key=st.session_state.runtime_api_key,
                on_progress=on_progress,
            )
            st.session_state.quality = quality_report(st.session_state.adaptations)
            st.session_state.active_output_id = "vocabulary"
            st.session_state.active_category_id = "vocabulary"
            close_workspace()
        except (ValueError, RuntimeError) as error:
            st.error(str(error))
            return
        finally:
            progress.empty()
            status.empty()

    q = st.session_state.get("quality") or {}
    if q.get("exam_ready"):
        st.success(
            f"Ready! {q.get('vocab_terms', 0)} vocab terms, "
            f"{q.get('worksheet_short_q', 0)} short + {q.get('worksheet_long_q', 0)} long "
            f"exam questions — select a tab below to open."
        )
    else:
        st.warning(
            "Generation finished but some sections may be thin — try again or use a shorter "
            "lesson extract."
        )


def _content_for_spec(spec: dict, adaptations: dict, lesson: str):
    if not spec["generate"]:
        return lesson
    return adaptations.get(spec["id"], "_No content generated for this section._")


def _cloud_api_key_configured() -> bool:
    try:
        return is_valid_openai_key(str(st.secrets.get("OPENAI_API_KEY", "")))
    except Exception:
        return False


def render_api_sidebar() -> None:
    cloud_key = _cloud_api_key_configured()
    active = validate_api_key(st.session_state.runtime_api_key)

    if active:
        st.sidebar.markdown(
            '<div class="sidebar-status-ready">● AI service ready</div>',
            unsafe_allow_html=True,
        )
    else:
        st.sidebar.markdown(
            '<div class="sidebar-status-warn">○ Setup required</div>',
            unsafe_allow_html=True,
        )

    if cloud_key:
        return

    with st.sidebar.expander("Administrator settings", expanded=False):
        st.caption("Self-hosted only. Keys are stored locally in `.env`.")
        session_key = st.text_input(
            "OpenAI API key",
            value=st.session_state.runtime_api_key,
            type="password",
            placeholder="sk-…",
            label_visibility="collapsed",
        )
        st.session_state.runtime_api_key = session_key.strip()

        if (
            is_valid_openai_key(st.session_state.runtime_api_key)
            and st.session_state.runtime_api_key != st.session_state.last_saved_api_key
        ):
            try:
                save_api_key_to_env(st.session_state.runtime_api_key)
                st.session_state.last_saved_api_key = st.session_state.runtime_api_key
            except Exception as error:
                st.warning(f"Could not save settings locally: {error}")

        if validate_api_key(st.session_state.runtime_api_key):
            st.caption("Configuration saved.")
        else:
            st.caption("Enter a valid API key to enable generation.")


@st.cache_data(show_spinner="Preparing print pack…")
def _cached_zip_bundle(adaptations_json: str, lesson_text: str, base_name: str) -> bytes:
    adaptations = json.loads(adaptations_json)
    return build_zip_bundle(ADAPTATION_SPECS, adaptations, lesson_text, base_name)


def _build_bundle_download() -> str:
    adaptations = st.session_state.adaptations
    lesson = st.session_state.lesson_text
    parts = [f"{APP_NAME} — Lesson Adaptation Package\n" + "=" * 50 + "\n"]
    for spec in ADAPTATION_SPECS:
        body = _content_for_spec(spec, adaptations, lesson)
        if spec["generate"]:
            parts.append("\n\n" + content_to_export(spec["title"], body, spec["id"]))
        else:
            parts.append(f"\n\n{'=' * 50}\n{spec['title'].upper()}\n{'=' * 50}\n\n{body}")
    return "".join(parts)


def _base_name() -> str:
    if st.session_state.upload_name:
        return st.session_state.upload_name.rsplit(".", 1)[0]
    return "lesson"


def _zip_bytes() -> bytes | None:
    if not st.session_state.adaptations:
        return None
    adaptations_json = json.dumps(
        st.session_state.adaptations, sort_keys=True, default=str
    )
    return _cached_zip_bundle(
        adaptations_json, st.session_state.lesson_text, _base_name()
    )


def _resolve_active_spec():
    active_id = st.session_state.active_output_id
    active_spec = next((s for s in ADAPTATION_SPECS if s["id"] == active_id), None)
    if not active_spec:
        active_id = default_spec_for_category(
            st.session_state.get("active_category_id", "vocabulary")
        )
        active_spec = next(s for s in ADAPTATION_SPECS if s["id"] == active_id)
        st.session_state.active_output_id = active_id
    cat = category_for_spec(active_id)
    if cat:
        st.session_state.active_category_id = cat["id"]
    return active_spec


def render_dashboard() -> None:
    """Homepage only — no adaptation outputs."""
    render_dashboard_intro()

    st.markdown('<div class="workspace-card">', unsafe_allow_html=True)
    st.subheader("1. Upload Your Lesson")
    col_upload, col_sample = st.columns([3, 1])
    with col_sample:
        if st.button("Use Sample Lesson", use_container_width=True):
            load_sample_lesson()
    with col_upload:
        uploaded = st.file_uploader(
            "PDF or DOCX (Grades 3–11)",
            type=["pdf", "docx"],
            help="Text is extracted in memory — files are not stored on disk.",
        )
    if uploaded is not None:
        handle_file_upload(uploaded)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.analytics:
        st.markdown('<div class="workspace-card">', unsafe_allow_html=True)
        st.subheader("2. Lesson Insights")
        render_analytics_panel(st.session_state.analytics)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.lesson_text:
        st.markdown('<div class="workspace-card">', unsafe_allow_html=True)
        st.subheader("3. Generate Adaptations")
        col_generate, col_clear = st.columns([2, 1])
        with col_generate:
            can_generate = bool(
                st.session_state.lesson_text
                and validate_api_key(st.session_state.runtime_api_key)
            )
            if st.button(
                "Generate Adaptations",
                type="primary",
                use_container_width=True,
                disabled=not can_generate,
            ):
                run_generation()
        with col_clear:
            if st.button("Clear Session", use_container_width=True):
                st.session_state.lesson_text = ""
                st.session_state.adaptations = None
                st.session_state.analytics = None
                st.session_state.upload_name = ""
                st.session_state.quality = None
                st.session_state.active_output_id = "vocabulary"
                st.session_state.active_category_id = "vocabulary"
                st.session_state._processed_upload_key = ""
                close_workspace()
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.adaptations:
        st.markdown('<div class="workspace-card">', unsafe_allow_html=True)
        st.subheader("4. Choose an Adaptation")
        st.caption(
            "Each version opens in its own workspace — one adaptation at a time, never stacked here."
        )
        render_pill_navigation()
        st.markdown("</div>", unsafe_allow_html=True)

        q = st.session_state.quality or {}
        if q:
            with st.expander("Quality Report", expanded=False):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Analysis sections", q.get("pages_analyzed", 1))
                c2.metric("Objectives", q.get("objectives_found", 0))
                c3.metric("Vocab terms", q.get("vocab_terms", 0))
                c4.metric(
                    "Exam questions",
                    (q.get("worksheet_short_q") or 0) + (q.get("worksheet_long_q") or 0),
                )


def render_workspace_page() -> None:
    """Dedicated workspace — single adaptation, never on homepage."""
    adaptations = st.session_state.adaptations
    if not adaptations:
        st.warning(
            "Adaptations are not available in this session. "
            "Please go back and click **Generate Adaptations** again."
        )
        if st.button("← Back to Dashboard", key="ws_missing_back", type="primary"):
            close_workspace()
            clear_stale_url_params()
            st.rerun()
        return

    active_spec = _resolve_active_spec()
    content = _content_for_spec(active_spec, adaptations, st.session_state.lesson_text)
    base_name = _base_name()
    filename = f"{base_name}_{active_spec['id']}.txt"

    st.session_state._text_bundle_cache = _build_bundle_download()
    zip_bytes = _zip_bytes()

    render_workspace(
        active_spec=active_spec,
        content=content,
        download_filename=filename,
        zip_bytes=zip_bytes,
        base_name=base_name,
        api_key=st.session_state.runtime_api_key,
        adaptations=adaptations,
        lesson_text=st.session_state.lesson_text,
        content_for_spec=_content_for_spec,
    )


def main() -> None:
    load_api_key_from_env_file()
    clear_stale_url_params()

    st.markdown(get_custom_css(), unsafe_allow_html=True)

    logo_path = str(ALORA_LOGO) if ALORA_LOGO.exists() else None
    render_top_nav(logo_path, APP_VERSION)
    render_api_sidebar()
    render_sidebar(APP_VERSION)

    # Workspace route — must run before dashboard (dashboard upload must not run first)
    if should_render_workspace():
        render_workspace_page()
        return

    if st.session_state.get("app_view") == VIEW_WORKSPACE:
        if st.session_state.adaptations:
            render_workspace_page()
            return
        close_workspace()

    render_dashboard()


if __name__ == "__main__":
    main()
