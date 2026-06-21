"""
EduAdapt AI — Main Streamlit application.

Teachers upload a lesson (PDF/DOCX), review analytics, and generate
AdaptEd AI–aligned differentiated versions (19 tabs: original, vocabulary,
16 learner adaptations, exam worksheet).
"""

import streamlit as st
from pathlib import Path

from adaptation_specs import ADAPTATION_SPECS, OUTPUT_TAB_LABELS
from ai_generator import generate_adaptations, get_effective_api_key, quality_report, validate_api_key
from analytics_engine import build_analytics_report
from docx_exporter import build_zip_bundle, export_tab_docx
from document_parser import extract_lesson_text
from secrets_helper import is_valid_openai_key, read_api_key_from_env_file
from styles import get_custom_css, render_header
from structured_renderers import content_to_export
from ui_helpers import render_analytics_panel, render_content_tab, render_sidebar

PROJECT_ROOT = Path(__file__).resolve().parent
SAMPLE_LESSON_PATH = PROJECT_ROOT / "samples" / "sample_lesson.docx"

# --- Page configuration (must be first Streamlit command) ---
st.set_page_config(
    page_title="EduAdapt AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
            "Missing OpenAI API key. Add it in the sidebar under "
            "**OpenAI Setup** or in `.env` as `OPENAI_API_KEY=...`."
        )
        return

    with st.spinner(
        "Step 1/3: Analyzing full lesson (all pages)… "
        "Step 2/3: Building vocabulary & worksheet… "
        "Step 3/3: Creating 16 adaptations… (~8–12 min for long lessons)"
    ):
        try:
            st.session_state.adaptations = generate_adaptations(
                st.session_state.lesson_text,
                override_api_key=st.session_state.runtime_api_key,
            )
            st.session_state.quality = quality_report(st.session_state.adaptations)
        except (ValueError, RuntimeError) as error:
            st.error(str(error))
            return

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


def render_output_tabs() -> None:
    """Show original lesson, vocabulary, adaptations, and worksheet in separate tabs."""
    adaptations = st.session_state.adaptations
    lesson = st.session_state.lesson_text
    base_name = (
        st.session_state.upload_name.rsplit(".", 1)[0]
        if st.session_state.upload_name
        else "lesson"
    )

    tab_contents = []
    for spec in ADAPTATION_SPECS:
        content = _content_for_spec(spec, adaptations, lesson)
        filename = f"{base_name}_{spec['id']}.txt"
        tab_contents.append((spec["title"], content, filename, spec["id"]))

    tabs = st.tabs(OUTPUT_TAB_LABELS)

    for tab, (title, content, filename, spec_id) in zip(tabs, tab_contents):
        with tab:
            render_content_tab(title, content, filename, spec_id=spec_id)


def main() -> None:
    """Application entry point."""
    load_api_key_from_env_file()

    st.markdown(get_custom_css(), unsafe_allow_html=True)
    st.markdown(render_header(), unsafe_allow_html=True)

    render_sidebar()

    with st.sidebar.expander("OpenAI Setup", expanded=True):
        st.caption("Paste once. EduAdapt auto-saves it to `.env`.")
        session_key = st.text_input(
            "OpenAI API Key",
            value=st.session_state.runtime_api_key,
            type="password",
            placeholder="sk-...",
            help="Stored in .env on your machine; on Streamlit Cloud use Secrets.",
        )
        st.session_state.runtime_api_key = session_key.strip()

        if (
            is_valid_openai_key(st.session_state.runtime_api_key)
            and st.session_state.runtime_api_key != st.session_state.last_saved_api_key
        ):
            try:
                save_api_key_to_env(st.session_state.runtime_api_key)
                st.session_state.last_saved_api_key = st.session_state.runtime_api_key
                st.success("API key auto-saved to .env")
            except Exception as error:
                st.warning(f"Could not save .env locally: {error}")

        active_key = get_effective_api_key(st.session_state.runtime_api_key)
        if active_key:
            st.success("API key detected. Ready to generate.")
            st.caption(f"Using key ending in ...{active_key[-4:]}")
        else:
            st.warning("API key missing. Add key to continue.")

        if st.button("Reload key from .env", use_container_width=True):
            load_api_key_from_env_file()
            st.rerun()

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
                st.rerun()

    if st.session_state.adaptations:
        st.markdown("---")
        q = st.session_state.quality or {}
        if q:
            with st.expander("Quality Report — exam coverage", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Pages analyzed", q.get("pages_analyzed", 1))
                c2.metric("Objectives", q.get("objectives_found", 0))
                c3.metric("Vocab terms", q.get("vocab_terms", 0))
                c4.metric("Exam questions", (q.get("worksheet_short_q") or 0) + (q.get("worksheet_long_q") or 0))
                if q.get("source_chars", 0) > 50000:
                    st.info(
                        f"Your lesson is {q.get('source_chars', 0):,} characters — "
                        "all sections were analyzed in chunks so content is not reduced to one page."
                    )
                if q.get("exam_ready"):
                    st.success("This pack covers enough depth for exam revision on this topic.")
                else:
                    st.warning(
                        "Some sections need more content. Click **Clear Session** and "
                        "**Generate Adaptations** again, or upload a focused chapter."
                    )

        st.subheader(
            "4. Your Differentiated Lessons "
            "(Original → Vocabulary → 16 AdaptEd versions → Exam Worksheet)"
        )
        render_output_tabs()

        st.markdown("---")
        st.subheader("5. Download — print-friendly packs")
        base_name = (
            st.session_state.upload_name.rsplit(".", 1)[0]
            if st.session_state.upload_name
            else "lesson"
        )
        zip_bytes = build_zip_bundle(
            ADAPTATION_SPECS,
            st.session_state.adaptations,
            st.session_state.lesson_text,
            base_name,
        )
        col_zip, col_txt = st.columns(2)
        with col_zip:
            st.download_button(
                label="Download ZIP (separate DOCX + HTML per tab — best for printing)",
                data=zip_bytes,
                file_name=f"{base_name}_eduadapt_print_pack.zip",
                mime="application/zip",
                use_container_width=True,
            )
        with col_txt:
            bundle = _build_bundle_download()
            st.download_button(
                label="Download plain text bundle",
                data=bundle,
                file_name=f"{base_name}_eduadapt_bundle.txt",
                mime="text/plain",
                use_container_width=True,
            )


def _build_bundle_download() -> str:
    """Combine every output into one text file for easy sharing."""
    adaptations = st.session_state.adaptations
    lesson = st.session_state.lesson_text

    parts = ["EduAdapt AI — AdaptEd-Aligned Lesson Package\n" + "=" * 50 + "\n"]
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
