"""
Alora AI — Main Streamlit application.
Dashboard + dedicated adaptation workspace (never stacked on homepage).
"""

from __future__ import annotations

import json
import logging
import hashlib

import streamlit as st

logger = logging.getLogger(__name__)

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

_startup_stage = "application imports"
try:
    _startup_stage = "adaptation specifications"
    from adaptation_specs import ADAPTATION_SPECS
    _startup_stage = "verified learning engine"
    from engines.verified_learning_engine import VerifiedLearningOrchestrator
    _startup_stage = "adaptation generator"
    from ai_generator import quality_report, validate_api_key
    _startup_stage = "analytics"
    from analytics_engine import build_analytics_report
    _startup_stage = "document export"
    from docx_exporter import build_zip_bundle
    _startup_stage = "document ingestion"
    from document_parser import extract_lesson_text, extract_source_document
    _startup_stage = "application configuration"
    from config import APP_NAME
    _startup_stage = "navigation"
    from navigation import category_for_spec, default_spec_for_category
    _startup_stage = "secrets configuration"
    from secrets_helper import is_valid_openai_key, read_api_key_from_env_file
    _startup_stage = "session state"
    from session_state import (
        VIEW_WORKSPACE,
        clear_stale_url_params,
        close_workspace,
        init_navigation_state,
        should_render_workspace,
    )
    _startup_stage = "content rendering"
    from structured_renderers import content_to_export
    _startup_stage = "publication gate"
    from publication_gate import publication_block_reason
    _startup_stage = "visual styles"
    from styles import get_custom_css
    _startup_stage = "version metadata"
    from version import APP_VERSION, BUILD_ID
    _startup_stage = "workspace"
    from workspace_page import render_workspace
    _startup_stage = "interface components"
    from ui_helpers import (
        render_analytics_panel,
        render_dashboard_intro,
        render_pill_navigation,
        render_sidebar,
        render_top_nav,
    )
except Exception as import_error:
    logger.exception("Alora AI startup failed")
    st.error("Alora AI could not start. Please contact your platform administrator.")
    missing_component = getattr(import_error, "name", "") or ""
    reason = (
        f"Required component unavailable: {missing_component}."
        if missing_component
        else f"Component initialization failed ({type(import_error).__name__})."
    )
    st.warning(f"Startup stage: **{_startup_stage}**. {reason}")
    st.info(
        "Recovery: reboot after checking deployment dependencies and private logs. "
        "Fallback used: safe startup screen."
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
if "source_envelope" not in st.session_state:
    st.session_state.source_envelope = None
if "runtime_api_key" not in st.session_state:
    st.session_state.runtime_api_key = ""
if "last_saved_api_key" not in st.session_state:
    st.session_state.last_saved_api_key = ""
if "quality" not in st.session_state:
    st.session_state.quality = None
if "auditory_mode" not in st.session_state:
    st.session_state.auditory_mode = False
if "audio_voice" not in st.session_state:
    st.session_state.audio_voice = "Female"
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


def apply_lesson(name: str, text: str, source_envelope: dict | None = None) -> None:
    st.session_state.lesson_text = text
    st.session_state.upload_name = name
    st.session_state.source_envelope = source_envelope
    st.session_state.adaptations = None
    st.session_state.analytics = build_analytics_report(text)
    close_workspace()


def _upload_fingerprint(name: str, file_bytes: bytes) -> str:
    digest = hashlib.sha256(file_bytes).hexdigest()
    return f"{name}:{len(file_bytes)}:{digest}"


def handle_file_upload(uploaded_file) -> None:
    if uploaded_file is None:
        return
    if int(getattr(uploaded_file, "size", 0) or 0) > 50 * 1024 * 1024:
        st.error("The maximum lesson file size is 50 MB.")
        return
    try:
        file_bytes = uploaded_file.read()
        fingerprint = _upload_fingerprint(uploaded_file.name, file_bytes)
        if st.session_state.get("_processed_upload_key") == fingerprint:
            return
        envelope = extract_source_document(uploaded_file.name, file_bytes)
        if not envelope.ok:
            issue = (envelope.errors or envelope.warnings or [{}])[0]
            st.error(
                f"**{issue.get('stage', 'Extraction').title()}** — "
                f"{issue.get('safe_message') or issue.get('reason') or 'The file is unreadable.'}"
            )
            if issue.get("recovery"):
                st.info(str(issue["recovery"]))
            return
        text = envelope.text
    except ValueError as error:
        st.error(str(error))
        return
    except Exception:
        logger.exception("Lesson extraction failed")
        st.error("The lesson could not be read safely.")
        return
    if not text.strip():
        st.warning("No reliable text was found. Upload a clearer scan or plain text.")
        return
    st.session_state._processed_upload_key = fingerprint
    apply_lesson(uploaded_file.name, text, envelope.to_dict())
    st.success(f"Loaded: **{uploaded_file.name}** ({len(text):,} characters)")


def ensure_sample_lesson_exists() -> bool:
    if SAMPLE_LESSON_PATH.exists():
        return True
    try:
        from create_sample_lesson import main as create_sample

        create_sample()
        return SAMPLE_LESSON_PATH.exists()
    except Exception:
        logger.exception("Sample lesson creation failed")
        st.error("The sample lesson could not be prepared.")
        return False


def load_sample_lesson() -> None:
    if not ensure_sample_lesson_exists():
        return
    try:
        file_bytes = SAMPLE_LESSON_PATH.read_bytes()
        envelope = extract_source_document(SAMPLE_LESSON_PATH.name, file_bytes)
        text = envelope.text
    except Exception:
        logger.exception("Sample lesson extraction failed")
        st.error("The sample lesson could not be loaded.")
        return
    if not text.strip():
        st.warning("Sample lesson file is empty. Try uploading your own file.")
        return
    st.session_state._processed_upload_key = f"{SAMPLE_LESSON_PATH.name}:sample"
    apply_lesson(SAMPLE_LESSON_PATH.name, text, envelope.to_dict())
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
            vlie = VerifiedLearningOrchestrator(on_progress=on_progress)
            vlie_result = vlie.process_lesson(
                st.session_state.lesson_text,
                override_api_key=st.session_state.runtime_api_key,
                generate_adaptations=True,
                source_envelope=st.session_state.get("source_envelope"),
            )
            result_envelope = vlie_result.get("pipeline_result") or {}
            if result_envelope.get("status") in {"failed", "blocked"}:
                st.error(
                    f"**{str(result_envelope.get('stage') or 'Generation').replace('_', ' ').title()}** — "
                    f"{result_envelope.get('message') or 'Generation could not complete.'}"
                )
                if result_envelope.get("recovery"):
                    st.info(f"Recovery: {result_envelope['recovery']}")
                if result_envelope.get("fallback_used") not in {"", "none", None}:
                    st.caption(f"Fallback used: {result_envelope['fallback_used']}")
                return
            st.session_state.adaptations = vlie_result.get("adaptations")
            if isinstance(st.session_state.adaptations, dict):
                st.session_state.adaptations.setdefault("_meta", {})[
                    "pipeline_result"
                ] = result_envelope
            st.session_state.vlie_package = vlie_result.get("package")
            st.session_state.vlie_run_id = vlie_result.get("run_id")
            st.session_state.quality = quality_report(st.session_state.adaptations)
            st.session_state.active_output_id = "vocabulary"
            st.session_state.active_category_id = "vocabulary"
            close_workspace()
        except (ValueError, RuntimeError):
            logger.exception("Lesson generation failed")
            st.error("Lesson generation could not complete safely.")
            st.info("Check the AI service configuration and retry.")
            return
        except Exception:
            logger.exception("Unexpected lesson generation failure")
            st.error("Lesson generation is temporarily unavailable.")
            st.info("Retry shortly or contact your platform administrator.")
            return
        finally:
            progress.empty()
            status.empty()

    q = st.session_state.get("quality") or {}
    routing_warnings = (
        (st.session_state.get("adaptations") or {})
        .get("_meta", {})
        .get("routing_warnings", [])
    )
    if routing_warnings:
        first_warning = routing_warnings[0]
        st.info(
            f"**{str(first_warning.get('stage') or 'Source review').replace('_', ' ').title()}** — "
            f"{first_warning.get('message') or 'Some source notation was omitted from verified computation.'} "
            f"Recovery: {first_warning.get('recovery') or 'Review the source notation.'} "
            "The source-grounded lesson remains available."
        )
    if q.get("publish_blocked"):
        st.error(
            "Publish blocked by hard QA gate"
            + (f": {q.get('publish_blocked_reason')}" if q.get("publish_blocked_reason") else ".")
            + " Review Verified Engines / Visuals before classroom use."
        )
    elif q.get("exam_ready"):
        stem_n = q.get("stem_artifacts", 0)
        viz_n = q.get("verified_visuals", 0)
        stem_msg = f" · {stem_n} verified STEM result(s)" if stem_n else ""
        viz_msg = f" · {viz_n} verified visual(s)" if viz_n else ""
        st.success(
            f"Ready! {q.get('vocab_terms', 0)} vocab terms, "
            f"{q.get('worksheet_short_q', 0)} short + {q.get('worksheet_long_q') or 0} long "
            f"exam questions{stem_msg}{viz_msg} — select a tab below to open."
        )
    elif q.get("adaptations_ready") and not q.get("stem_verified", True):
        st.warning(
            "Adaptations generated but **STEM / publish QA did not pass**. "
            "Review the Verified STEM panel before classroom use."
        )
    else:
        st.info(
            "Generation complete. Full-length lessons are processed in sections automatically — "
            "open an adaptation below."
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


def inject_streamlit_accessibility_repairs() -> None:
    """Repair framework-generated ARIA gaps that application widgets cannot configure."""
    import streamlit.components.v1 as components

    components.html(
        """
        <script>
        (() => {
          const doc = window.parent.document;
          const repair = () => {
            const sidebar = doc.querySelector('section[data-testid="stSidebar"]');
            const toggle = doc.querySelector('button[data-testid="stBaseButton-headerNoPadding"]');
            if (sidebar && sidebar.hasAttribute('aria-expanded')) {
              const expanded = sidebar.getAttribute('aria-expanded');
              sidebar.removeAttribute('aria-expanded');
              if (toggle) toggle.setAttribute('aria-expanded', expanded);
            }
            if (toggle && !(toggle.getAttribute('aria-label') || '').trim()) {
              toggle.setAttribute('aria-label', 'Toggle navigation sidebar');
              toggle.setAttribute('title', 'Toggle navigation sidebar');
            }
            const upload = doc.querySelector('input[data-testid="stFileUploaderDropzoneInput"]');
            if (upload && !(upload.getAttribute('aria-label') || '').trim()) {
              upload.setAttribute('aria-label', 'Upload educational source file');
            }
            doc.querySelectorAll('[data-testid="stFileUploaderDropzoneInstructions"] span')
              .forEach(el => el.style.setProperty('color', '#51545d', 'important'));
          };
          repair();
          new MutationObserver(repair).observe(doc.body, {
            subtree: true, childList: true, attributes: true,
            attributeFilter: ['aria-expanded', 'aria-label']
          });
        })();
        </script>
        """,
        height=0,
    )


def render_api_sidebar() -> None:
    cloud_key = _cloud_api_key_configured()
    active = validate_api_key(st.session_state.runtime_api_key)

    if active:
        st.sidebar.markdown(
            '<div class="sidebar-status-ready">● AI service ready</div>',
            unsafe_allow_html=True,
        )
        from config import IMAGE_PROVIDER

        if IMAGE_PROVIDER == "openai":
            st.sidebar.caption("🖼️ Vocabulary images: OpenAI DALL·E")
        elif IMAGE_PROVIDER not in ("off", "none", "false", "0"):
            st.sidebar.caption("🖼️ Vocabulary images: Pollinations AI (free)")
        else:
            st.sidebar.caption("📊 Visuals: coloured flowcharts")
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
            except Exception:
                logger.exception("Could not save settings locally")
                st.warning("Settings could not be saved locally.")

        if validate_api_key(st.session_state.runtime_api_key):
            st.caption("Configuration saved.")
        else:
            st.caption("Enter a valid API key to enable generation.")


@st.cache_data(show_spinner="Preparing print pack…", ttl=3600, max_entries=8)
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
            "Educational source file",
            type=[
                "pdf",
                "docx",
                "pptx",
                "txt",
                "md",
                "markdown",
                "html",
                "htm",
                "png",
                "jpg",
                "jpeg",
                "webp",
            ],
            help=(
                "PDF, Word, PowerPoint, text, Markdown, HTML, or an image scan. "
                "Content is extracted in memory and curriculum detection is optional."
            ),
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
        block_reason = publication_block_reason(
            st.session_state.adaptations,
            package=st.session_state.get("vlie_package"),
            quality=st.session_state.get("quality"),
        )
        if block_reason:
            st.error(
                "This lesson is quarantined and cannot be opened, exported, narrated, "
                f"or published: {block_reason}"
            )
            return

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
                if q.get("stem_artifacts"):
                    st.caption(
                        f"STEM: {q.get('stem_artifacts')} engine result(s) · "
                        f"{'verified' if q.get('stem_verified') else 'needs review'}"
                    )
                if q.get("rag_citations"):
                    st.caption(
                        f"Knowledge: {q.get('rag_citations')} NCERT citation(s) · "
                        f"{q.get('official_mcqs', 0)} official MCQ(s) · pilot {q.get('knowledge_pilot', '')}"
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

    block_reason = publication_block_reason(
        adaptations,
        package=st.session_state.get("vlie_package"),
        quality=st.session_state.get("quality"),
    )
    if block_reason:
        st.error(
            "This lesson is quarantined and cannot be opened, exported, narrated, "
            f"or published: {block_reason}"
        )
        if st.button("← Back to Dashboard", key="ws_blocked_back", type="primary"):
            close_workspace()
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
    render_sidebar(APP_VERSION, BUILD_ID)
    st.markdown(
        '<a class="alora-skip-link" href="#alora-main-content">Skip to lesson content</a>'
        '<span id="alora-main-content" tabindex="-1"></span>',
        unsafe_allow_html=True,
    )

    # Workspace route — must run before dashboard (dashboard upload must not run first)
    if should_render_workspace():
        render_workspace_page()
        inject_streamlit_accessibility_repairs()
        return

    if st.session_state.get("app_view") == VIEW_WORKSPACE:
        if st.session_state.adaptations:
            render_workspace_page()
            inject_streamlit_accessibility_repairs()
            return
        close_workspace()

    render_dashboard()
    inject_streamlit_accessibility_repairs()


if __name__ == "__main__":
    main()
