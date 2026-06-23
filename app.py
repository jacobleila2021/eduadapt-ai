"""
Alora AI — Main Streamlit application.
"""

import traceback

import streamlit as st

st.set_page_config(
    page_title="Alora AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

from pathlib import Path

try:
    from adaptation_specs import ADAPTATION_SPECS
    from ai_generator import generate_adaptations, quality_report, validate_api_key
    from analytics_engine import build_analytics_report
    from docx_exporter import build_zip_bundle, export_tab_docx
    from brand_assets import ALORA_LOGO
    from document_parser import extract_lesson_text
    from config import APP_NAME
    from secrets_helper import is_valid_openai_key, read_api_key_from_env_file
    from styles import get_custom_css
    from structured_renderers import content_to_export
    from version import APP_VERSION
    from ui_helpers import (
        render_adaptation_nav,
        render_analytics_panel,
        render_brand_header,
        render_content_tab,
        render_sidebar,
        SPEC_ICONS,
    )
except Exception as import_error:
    st.error("Alora AI could not start. Details below (share with support if needed):")
    st.code(traceback.format_exc())
    st.info(
        "Common fix: Streamlit **Settings → Secrets** must include "
        "`OPENAI_API_KEY`. Also confirm **Manage app → Logs** shows a successful pip install."
    )
    st.stop()

PROJECT_ROOT = Path(__file__).resolve().parent
SAMPLE_LESSON_PATH = PROJECT_ROOT / "samples" / "sample_lesson.docx"

# --- Session state defaults ---
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
if "active_output_id" not in st.session_state:
    st.session_state.active_output_id = "vocabulary"


def save_api_key_to_env(api_key: str) -> None:
    """Persist the OpenAI API key to a clean .env file (two lines only)."""
    env_path = PROJECT_ROOT / ".env"
    env_path.write_text(
        f"OPENAI_API_KEY={api_key}\nOPENAI_MODEL=gpt-4o-mini\n",
        encoding="utf-8",
    )


def load_api_key_from_env_file() -> None:
    """Load API key from .env every run (replaces stale placeholder session keys)."""
    env_key = read_api_key_from_env_file()
    if env_key:
        st.session_state.runtime_api_key = env_key
        st.session_state.last_saved_api_key = env_key


def apply_lesson(name: str, text: str) -> None:
    """Store extracted lesson text and refresh analytics in session state."""
    st.session_state.lesson_text = text
    st.session_state.upload_name = name
    st.session_state.adaptations = None
    st.session_state.analytics = build_analytics_report(text)
    st.success(f"Loaded: **{name}** ({len(text):,} characters)")


def ensure_sample_lesson_exists() -> bool:
    """Create sample_lesson.docx if run.bat has not created it yet."""
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
    """Load the built-in Grade 6 sample lesson for instant testing."""
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

    apply_lesson(SAMPLE_LESSON_PATH.name, text)


def handle_file_upload(uploaded_file) -> None:
    """Process an uploaded PDF or DOCX and store text in session state."""
    if uploaded_file is None:
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

    apply_lesson(uploaded_file.name, text)


def run_generation() -> None:
    """Call OpenAI and store adaptations in session state."""
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
        except (ValueError, RuntimeError) as error:
            st.error(str(error))
            return
        finally:
            progress.empty()
            status.empty()

    q = st.session_state.get("quality") or {}
    if q.get("exam_ready"):
        st.success(
            f"Ready for exam prep! {q.get('vocab_terms', 0)} vocab terms, "
            f"{q.get('worksheet_short_q', 0)} short + {q.get('worksheet_long_q', 0)} long "
            f"exam questions, {q.get('objectives_found', 0)} objectives covered."
        )
    else:
        st.warning(
            "Generation finished but some sections may be thin — try again or use a shorter "
            "lesson extract. Check the Quality Report below."
        )


def _content_for_spec(spec: dict, adaptations: dict, lesson: str) -> str:
    """Return tab body: uploaded original or AI-generated markdown."""
    if not spec["generate"]:
        return lesson
    return adaptations.get(spec["id"], "_No content generated for this section._")


def _cloud_api_key_configured() -> bool:
    """True when Streamlit Cloud secrets include a valid OpenAI key."""
    try:
        return is_valid_openai_key(str(st.secrets.get("OPENAI_API_KEY", "")))
    except Exception:
        return False


def render_api_sidebar() -> None:
    """Professional sidebar status — no exposed key details on the main view."""
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


def render_output_tabs() -> None:
    """Persistent tab grid + one lesson panel (adaptations stay in memory)."""
    adaptations = st.session_state.adaptations
    lesson = st.session_state.lesson_text
    base_name = (
        st.session_state.upload_name.rsplit(".", 1)[0]
        if st.session_state.upload_name
        else "lesson"
    )

    nav_specs = [spec for spec in ADAPTATION_SPECS if spec["id"] != "original"]
    active_id = st.session_state.active_output_id
    if not any(s["id"] == active_id for s in nav_specs):
        active_id = "vocabulary"
        st.session_state.active_output_id = active_id

    render_adaptation_nav(nav_specs, active_id)

    active_spec = next(spec for spec in ADAPTATION_SPECS if spec["id"] == active_id)
    content = _content_for_spec(active_spec, adaptations, lesson)
    filename = f"{base_name}_{active_spec['id']}.txt"
    icon = SPEC_ICONS.get(active_id, "📘")

    st.markdown(f"### {icon} {active_spec['title']}")
    render_content_tab(active_spec["title"], content, filename, spec_id=active_id)

    with st.expander("Original uploaded lesson (download only)", expanded=False):
        st.caption(
            "Your source file is included in the **Download ZIP** section below "
            "(Word + HTML). Use Text here for a quick plain copy."
        )
        st.download_button(
            label="Download original as Text",
            data=content_to_export("Original Lesson Archive", lesson, "original"),
            file_name=f"{base_name}_original.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_txt_original",
        )


@st.cache_data(show_spinner="Preparing print pack…")
def _cached_zip_bundle(adaptations_json: str, lesson_text: str, base_name: str) -> bytes:
    """Build ZIP once per lesson — avoids rebuilding on every adaptation click."""
    import json

    adaptations = json.loads(adaptations_json)
    return build_zip_bundle(ADAPTATION_SPECS, adaptations, lesson_text, base_name)


def _adaptation_workspace_impl() -> None:
    """Adaptation grid + content (runs inside st.fragment when available)."""
    q = st.session_state.quality or {}
    if q:
        with st.expander("Quality Report — exam coverage", expanded=False):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Analysis sections", q.get("pages_analyzed", 1))
            c2.metric("Objectives", q.get("objectives_found", 0))
            c3.metric("Vocab terms", q.get("vocab_terms", 0))
            c4.metric("Exam questions", (q.get("worksheet_short_q") or 0) + (q.get("worksheet_long_q") or 0))
            if q.get("source_chars", 0) > 50000:
                st.info(
                    f"Your lesson is {q.get('source_chars', 0):,} characters — "
                    "analyzed in sections for full exam coverage."
                )
            if q.get("exam_ready"):
                st.success("This pack covers enough depth for exam revision on this topic.")
            else:
                st.warning(
                    "Some sections need more content. Click **Clear Session** and "
                    "**Generate Adaptations** again, or upload a focused chapter."
                )

    st.subheader("4. Lesson Adaptations")
    st.caption("Select a version — all tabs stay visible above. Your generated lessons remain loaded.")
    render_output_tabs()


_adaptation_workspace = (
    st.fragment(_adaptation_workspace_impl)
    if hasattr(st, "fragment")
    else _adaptation_workspace_impl
)


def _render_setup_sections() -> None:
    """Upload, analytics, and generate controls."""
    st.subheader("1. Upload Your Lesson")

    col_upload, col_sample = st.columns([3, 1])
    with col_sample:
        if st.button(
            "Use Sample Lesson",
            use_container_width=True,
            help="Loads samples/sample_lesson.docx (Grade 6 water cycle).",
        ):
            load_sample_lesson()

    with col_upload:
        uploaded = st.file_uploader(
            "PDF or DOCX (Grades 3–11 lesson plans, worksheets, or unit guides)",
            type=["pdf", "docx"],
            help="We extract all text and never store your file on disk.",
        )

    if uploaded is not None:
        handle_file_upload(uploaded)

    if st.session_state.analytics:
        st.markdown("---")
        st.subheader("2. Lesson Insights")
        render_analytics_panel(st.session_state.analytics)

    if st.session_state.lesson_text:
        st.markdown("---")
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
                st.rerun()


def main() -> None:
    """Application entry point."""
    load_api_key_from_env_file()

    st.markdown(get_custom_css(), unsafe_allow_html=True)

    logo_path = str(ALORA_LOGO) if ALORA_LOGO.exists() else None
    render_brand_header(logo_path)

    render_sidebar()
    render_api_sidebar()
    st.sidebar.caption(f"Version **{APP_VERSION}**")

    if st.session_state.adaptations:
        with st.expander("1–3. Upload, insights & generate", expanded=False):
            _render_setup_sections()
    else:
        _render_setup_sections()

    if st.session_state.adaptations:
        st.markdown("---")
        _adaptation_workspace()

        st.markdown("---")
        st.subheader("5. Download — print-friendly packs")
        base_name = (
            st.session_state.upload_name.rsplit(".", 1)[0]
            if st.session_state.upload_name
            else "lesson"
        )
        import json

        adaptations_json = json.dumps(st.session_state.adaptations, sort_keys=True, default=str)
        zip_bytes = _cached_zip_bundle(adaptations_json, st.session_state.lesson_text, base_name)
        col_zip, col_txt = st.columns(2)
        with col_zip:
            st.download_button(
                label="Download ZIP (separate DOCX + HTML per tab — best for printing)",
                data=zip_bytes,
                file_name=f"{base_name}_alora_print_pack.zip",
                mime="application/zip",
                use_container_width=True,
                key="dl_zip_bundle",
            )
        with col_txt:
            bundle = _build_bundle_download()
            st.download_button(
                label="Download plain text bundle",
                data=bundle,
                file_name=f"{base_name}_alora_bundle.txt",
                mime="text/plain",
                use_container_width=True,
                key="dl_txt_bundle",
            )


def _build_bundle_download() -> str:
    """Combine every output into one text file for easy sharing."""
    adaptations = st.session_state.adaptations
    lesson = st.session_state.lesson_text

    parts = [f"{APP_NAME} — Lesson Adaptation Package\n" + "=" * 50 + "\n"]
    for spec in ADAPTATION_SPECS:
        body = _content_for_spec(spec, adaptations, lesson)
        if spec["generate"]:
            parts.append(
                "\n\n"
                + content_to_export(spec["title"], body, spec["id"])
            )
        else:
            parts.append(
                f"\n\n{'=' * 50}\n{spec['title'].upper()}\n{'=' * 50}\n\n{body}"
            )

    return "".join(parts)


if __name__ == "__main__":
    main()
