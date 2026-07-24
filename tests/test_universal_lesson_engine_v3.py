from __future__ import annotations

import io
import time
import zipfile
from pathlib import Path

import pytest

from ai_generator import (
    _apply_v3_output_contract,
    _source_fallback_lesson,
)
from adaptation_specs import OUTPUT_KEYS
from engines.claim_extractor import extract_stem_claims
from engines.content_classifier import classify_content
from engines.knowledge_ingestion_engine.universal_ingest import ingest_source_bytes
from engines.qa.pipeline import validate_lesson_package
from engines.safe_math import safe_sympify, validate_math_expression
from engines.universal_lesson.profile import (
    build_universal_lesson_profile,
    detect_curriculum,
)
from engines.verified_learning_engine.compatibility import (
    adaptations_for_legacy_renderer,
    vlp_to_v3,
)
from engines.verified_learning_engine.result_envelope import failed, partial


def _source(text: str = "Plants use light energy during photosynthesis.") -> dict:
    return ingest_source_bytes("lesson.txt", text.encode()).to_dict()


def test_statistics_exact_dict_does_not_quarantine_math_lesson():
    from engines.lesson_pipeline import process_lesson_stem
    from engines.qa.pipeline import validate_lesson_package
    from engines.knowledge_ingestion_engine.universal_ingest import ingest_source_bytes

    text = "Mean of 2, 4, 6, 8\nDifferentiate x**2\nSolve 2*x + 4 = 12"
    stem = process_lesson_stem(text, topic="Mathematics")
    assert any(
        (art.get("payload") or {}).get("exact") not in (None, "", [], {})
        for art in stem.get("artifacts") or []
    )
    source = ingest_source_bytes("math.txt", text.encode()).to_dict()
    ref = source["blocks"][0]["block_id"]
    adaptations = {
        "standard": {
            "big_idea": "Use verified maths results.",
            "source_refs": [ref],
            "sections": [
                {
                    "title": "Results",
                    "body": "The mean is 5 and the derivative of x squared is 2x.",
                    "source_refs": [ref],
                }
            ],
        },
        "_meta": {
            "engine_artifacts": stem.get("artifacts") or [],
            "verified_exact_values": [
                {
                    "field": "exact",
                    "value": (art.get("payload") or {}).get("exact"),
                }
                for art in stem.get("artifacts") or []
                if art.get("ok") and (art.get("payload") or {}).get("exact") not in (
                    None,
                    "",
                    [],
                    {},
                )
            ],
        },
    }
    report = validate_lesson_package(
        artifacts=stem.get("artifacts") or [],
        adaptations=adaptations,
        source_envelope=source,
        grounding_mode="uploaded_source",
    )
    assert report.publish_blocked is False
    exactness = next(
        check for check in report.checks if check["code"] == "deterministic_exactness"
    )
    assert exactness["ok"] is True


def test_canonical_exact_forms_accept_json_and_math_presentation():
    from engines.qa.pipeline import _exact_value_preserved

    stats = {"mean": 5.0, "median": 5.0, "std": 2.58}
    haystack = '{"exact":{"mean":5.0,"median":5.0,"std":2.58}}'
    assert _exact_value_preserved(stats, haystack)
    assert _exact_value_preserved("2*x", "The derivative is 2x.")
    assert _exact_value_preserved("[2, 3]", "roots are [2,3]")


def test_source_references_remain_internal_metadata():
    output = _apply_v3_output_contract(
        {
            "answer": "An acid donates hydrogen ions.\nSource: blk_001, page 2",
            "notes": [
                "Use indicator paper.",
                "Source detail: uploaded source block blk_001",
            ],
        },
        key="standard",
        valid_source_refs=["blk_001"],
    )
    assert output["answer"] == "An acid donates hydrogen ions."
    assert output["notes"] == ["Use indicator paper.", ""]
    assert output["source_refs"] == ["blk_001"]


def test_pdf_extraction_artifacts_are_cleaned_before_adaptation():
    from engines.knowledge_ingestion_engine.universal_ingest import (
        _clean_extracted_block,
    )

    clean = _clean_extracted_block(
        "observations/square6Now repeat. Activity 2.3Activity 2.3 "
        "Figure 2.1Figure 2.1Reaction details."
    )
    assert "/square" not in clean
    assert clean.count("Activity 2.3") == 1
    assert clean.count("Figure 2.1") == 1
    assert "observations. Now" in clean


@pytest.mark.parametrize(
    "filename,body",
    [
        ("lesson.txt", b"Teacher notes about migration and citizenship."),
        ("lesson.md", b"# Fractions\nA fraction represents part of a whole."),
        ("lesson.html", b"<h1>Psychology</h1><p>Memory supports learning.</p><script>bad()</script>"),
    ],
)
def test_text_formats_ingest_without_curriculum_assumptions(filename, body):
    envelope = ingest_source_bytes(filename, body)
    assert envelope.ok
    assert envelope.curriculum_resolution["status"] == "unknown"
    assert "bad()" not in envelope.text


def test_docx_preserves_headings_and_tables():
    docx = pytest.importorskip("docx")
    document = docx.Document()
    document.add_heading("Human Respiration", level=1)
    document.add_paragraph("Cells release energy from food.")
    table = document.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Term"
    table.cell(0, 1).text = "Meaning"
    table.cell(1, 0).text = "Alveoli"
    table.cell(1, 1).text = "Air sacs"
    stream = io.BytesIO()
    document.save(stream)
    envelope = ingest_source_bytes("biology.docx", stream.getvalue())
    assert envelope.ok
    assert any(block.kind == "heading" for block in envelope.blocks)
    assert any(block.kind == "table" for block in envelope.blocks)


def test_docx_embedded_image_provenance(monkeypatch):
    docx = pytest.importorskip("docx")
    image_module = pytest.importorskip("PIL.Image")
    image = image_module.new("RGB", (60, 30), "white")
    image_stream = io.BytesIO()
    image.save(image_stream, format="PNG")
    image_stream.seek(0)
    document = docx.Document()
    document.add_paragraph("Diagram notes")
    document.add_picture(image_stream)
    stream = io.BytesIO()
    document.save(stream)
    monkeypatch.setattr(
        "engines.knowledge_ingestion_engine.universal_ingest._ocr_image",
        lambda *args, **kwargs: ("Labelled cell image", 0.9, "tesseract", []),
    )
    envelope = ingest_source_bytes("mixed-images.docx", stream.getvalue())
    image_blocks = [block for block in envelope.blocks if block.kind == "image_text"]
    assert image_blocks
    assert image_blocks[0].metadata["embedded_asset"].startswith("word/media/")


def test_text_pdf_preserves_full_page_provenance():
    fitz = pytest.importorskip("fitz")
    document = fitz.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "A research paper explains sampling methods, observations, analysis, findings, "
        "limitations, conclusions, and recommendations for future studies.",
    )
    data = document.tobytes()
    document.close()
    envelope = ingest_source_bytes("paper.pdf", data)
    assert envelope.ok
    assert any(block.page == 1 and block.extraction_method == "pypdf" for block in envelope.blocks)


def test_scanned_pdf_uses_ocr_below_native_text_threshold(monkeypatch):
    fitz = pytest.importorskip("fitz")
    document = fitz.open()
    document.new_page()
    data = document.tobytes()
    document.close()
    monkeypatch.setattr(
        "engines.knowledge_ingestion_engine.universal_ingest._ocr_image",
        lambda *args, **kwargs: (
            "Handwritten teacher notes about fractions and equivalent parts.",
            0.82,
            "tesseract",
            [],
        ),
    )
    envelope = ingest_source_bytes("handwritten-scan.pdf", data)
    assert envelope.ok
    assert envelope.ocr_used
    assert envelope.blocks[0].page == 1


def test_pptx_preserves_slide_provenance_and_notes():
    pptx = pytest.importorskip("pptx")
    presentation = pptx.Presentation()
    slide = presentation.slides.add_slide(presentation.slide_layouts[1])
    slide.shapes.title.text = "Supply and Demand"
    slide.placeholders[1].text = "Price changes influence demand."
    stream = io.BytesIO()
    presentation.save(stream)
    envelope = ingest_source_bytes("economics.pptx", stream.getvalue())
    assert envelope.ok
    assert any(block.slide == 1 for block in envelope.blocks)


def test_image_uses_local_first_ocr_contract(monkeypatch):
    pillow = pytest.importorskip("PIL.Image")
    image = pillow.new("RGB", (40, 40), "white")
    stream = io.BytesIO()
    image.save(stream, format="PNG")

    def local_ocr(*args, **kwargs):
        return "A readable OCR lesson about ecosystems.", 0.93, "tesseract", []

    monkeypatch.setattr(
        "engines.knowledge_ingestion_engine.universal_ingest._ocr_image",
        local_ocr,
    )
    envelope = ingest_source_bytes("scan.png", stream.getvalue())
    assert envelope.ok
    assert envelope.ocr_used
    assert envelope.ocr_confidence == 0.93


def test_blank_and_poor_ocr_have_friendly_recovery(monkeypatch):
    blank = ingest_source_bytes("blank.txt", b"")
    assert not blank.ok
    assert blank.errors[0]["stage"] == "validation"
    assert blank.errors[0]["recovery"]

    pillow = pytest.importorskip("PIL.Image")
    image = pillow.new("RGB", (40, 40), "white")
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    monkeypatch.setattr(
        "engines.knowledge_ingestion_engine.universal_ingest._ocr_image",
        lambda *args, **kwargs: (
            "",
            None,
            "none",
            [
                {
                    "stage": "ocr",
                    "code": "low_ocr_confidence",
                    "safe_message": "OCR confidence is too low.",
                    "recovery": "Upload a clearer scan.",
                }
            ],
        ),
    )
    poor = ingest_source_bytes("poor.png", stream.getvalue())
    assert not poor.ok
    assert poor.errors[0]["recovery"]


def test_corrupt_office_and_traversal_archive_are_rejected():
    corrupt = ingest_source_bytes("notes.docx", b"PK-not-a-zip")
    assert not corrupt.ok
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("../outside.xml", "<x/>")
    traversal = ingest_source_bytes("notes.docx", stream.getvalue())
    assert not traversal.ok
    assert traversal.errors[0]["code"] == "unsafe_office_archive"
    polyglot = ingest_source_bytes(
        "mixed.pdf", b"%PDF-1.7\n" + b"PK\x03\x04" + b"x" * 200
    )
    assert not polyglot.ok
    assert polyglot.errors[0]["code"] == "polyglot_file_rejected"


def test_legacy_zip_adapter_rejects_traversal(tmp_path):
    from engines.knowledge_ingestion_engine.adapters.parsers import (
        parse_zip_package,
    )

    archive_path = tmp_path / "lesson.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("../escape.txt", "unsafe")
    with pytest.raises(ValueError, match="unsafe member path"):
        parse_zip_package(archive_path, tmp_path / "extract")


@pytest.mark.parametrize(
    "prose",
    [
        "The force of public opinion shaped the independence movement.",
        "Blood pressure equals the pressure exerted by circulating blood.",
        "In English, the symbol = can show an equivalence in notes.",
        "Differentiate instruction for learners by reading level.",
        "The year 1947 marked a major historical change.",
        "Psychology studies memory, attention, and behaviour.",
    ],
)
def test_non_math_prose_never_reaches_sympy_claims(prose):
    assert classify_content(prose).content_type in {"prose", "question"}
    assert not [
        claim
        for claim in extract_stem_claims(prose)
        if claim.kind in {"math_equation", "plot_expression"}
    ]


@pytest.mark.parametrize(
    "expression,kind",
    [
        ("Solve x^2 - 4 = 0", "math_equation"),
        ("Differentiate x^3 + 2*x", "calculus_expression"),
        ("Plot sin(x)", "plot_expression"),
        ("H2 + O2 -> H2O", "chemical_equation"),
    ],
)
def test_valid_stem_inputs_are_typed(expression, kind):
    assert classify_content(expression).content_type == kind


def test_malformed_stem_is_omitted_with_scoped_warning():
    from engines.lesson_pipeline import process_lesson_stem

    result = process_lesson_stem("Balance H2 + -> water")
    assert not result["artifacts"]
    assert result["routing_warnings"][0]["code"] == "ambiguous_stem_not_routed"
    assert result["qa"]["publish_blocked"] is False


@pytest.mark.parametrize(
    "text",
    [
        "2CHAPTER",
        "2.12.12.1",
        "Chapter 2.12.12.1 Chemical Reactions",
        "Exercise 17 -> review questions",
    ],
)
def test_chemistry_chapter_labels_never_enter_math_or_chemistry_parsers(text):
    classified = classify_content(text)
    assert classified.content_type in {"prose", "metadata"}
    assert not extract_stem_claims(text)


def test_unbalanceable_source_reaction_is_scoped_not_quarantined():
    from engines.lesson_pipeline import process_lesson_stem

    result = process_lesson_stem(
        "Chemical reactions are represented using equations.\nH2 -> H2O"
    )
    assert result["artifacts"] == []
    assert any(
        warning["code"] == "scoped_computation_omitted"
        for warning in result["routing_warnings"]
    )
    assert result["qa"]["publish_blocked"] is False


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os').system('echo bad')",
        "x" * 400,
        "open(secret)",
        "((((((((((((((x+1))))))))))))))",
        "[x for x in range(999999)]",
    ],
)
def test_safe_math_rejects_malicious_or_exhaustive_inputs(expression):
    assert not validate_math_expression(expression).ok
    with pytest.raises(ValueError):
        safe_sympify(expression)


@pytest.mark.parametrize(
    "text,expected_status",
    [
        ("Biology: Cells contain membranes and cytoplasm.", "unknown"),
        ("History: Trade routes connected communities.", "unknown"),
        ("English: Metaphor compares ideas without using like or as.", "unknown"),
        ("French: Les élèves apprennent le vocabulaire de la famille.", "unknown"),
        ("Engineering: A truss distributes structural loads.", "unknown"),
        ("Medicine: Clinical observations inform diagnosis.", "unknown"),
        ("Psychology: Working memory has limited capacity.", "unknown"),
        ("Research notes describe the study method and findings.", "unknown"),
        ("Vocational training explains safe tool handling.", "unknown"),
        (
            "Corporate training describes an incident reporting procedure.",
            "recognized",
        ),
    ],
)
def test_universal_profile_supports_subjects_without_curriculum_leakage(
    text, expected_status
):
    profile = build_universal_lesson_profile(_source(text))
    assert profile.topic
    assert profile.claim_ledger
    assert profile.curriculum_resolution["status"] == expected_status


def test_curriculum_resolution_is_explicit_and_optional():
    assert detect_curriculum("CBSE Class 8 Science")["status"] == "recognized"
    assert detect_curriculum("Teacher-created lesson")["status"] == "unknown"
    assert detect_curriculum("Lesson", {"curriculum": "Custom State Course"})[
        "status"
    ] == "user_declared"


def test_all_nine_outputs_have_versioned_source_contracts():
    source = _source(
        "Water evaporates when heated. Water vapour condenses as it cools. "
        "The cycle continues through precipitation and collection."
    )
    profile = build_universal_lesson_profile(source).to_dict()
    refs = [block["block_id"] for block in source["blocks"]]
    outputs = {}
    for key in OUTPUT_KEYS:
        if key in {"vocabulary", "worksheet"}:
            value = {
                "body": profile["claim_ledger"][0]["text"],
                "source_refs": refs,
            }
        else:
            value = _source_fallback_lesson(key, profile, refs)
        outputs[key] = _apply_v3_output_contract(
            value,
            key=key,
            valid_source_refs=refs,
            fallback_used="source_extractive",
        )
    assert set(OUTPUT_KEYS) <= set(outputs)
    assert all(outputs[key]["_contract"]["schema_version"] == "3.0.0" for key in OUTPUT_KEYS)


def test_missing_optional_enrichment_never_blocks_source_mode():
    source = _source("A habitat provides food, water, shelter, and space.")
    ref = source["blocks"][0]["block_id"]
    adaptations = {
        "standard": {
            "big_idea": "A habitat provides resources.",
            "source_refs": [ref],
            "sections": [
                {"body": "A habitat provides food.", "source_refs": [ref]}
            ],
        }
    }
    report = validate_lesson_package(
        knowledge={
            "subject": "Science",
            "citations": [],
            "external_enrichment": {"status": "no_hits", "required": False},
        },
        adaptations=adaptations,
        source_envelope=source,
        grounding_mode="uploaded_source",
    )
    assert report.publish_blocked is False
    assert any(
        check["detail"] == "No curriculum references available."
        for check in report.checks
    )


def test_official_publish_mode_still_requires_curriculum_citations():
    report = validate_lesson_package(
        knowledge={"citations": [], "rag_hits": []},
        grounding_mode="official_curriculum_publish",
    )
    assert report.publish_blocked
    assert any(
        check["code"] == "source_citations" and not check["ok"]
        for check in report.checks
    )


def test_v3_errors_include_stage_recovery_and_fallback():
    result = failed(
        "source_ingestion",
        "knowledge_ingestion",
        "The source is unreadable.",
        recovery="Upload a clearer scan.",
        fallback_used="local_ocr",
    ).to_dict()
    assert result["stage"] == "source_ingestion"
    assert result["recovery"]
    assert result["fallback_used"] == "local_ocr"
    assert result["errors"] == ["The source is unreadable."]
    assert partial(
        "audio_generation",
        "voice_multimodal",
        "Using browser narration.",
        fallback_used="browser_tts",
    ).ok


def test_legacy_contracts_project_without_curriculum_invention():
    adaptations = adaptations_for_legacy_renderer({"standard": {"sections": []}})
    assert set(OUTPUT_KEYS) <= set(adaptations)
    package = vlp_to_v3(
        {
            "schema_version": "1.0.0",
            "lesson_metadata": {"source_chars": 100},
            "curriculum": {"citations": []},
        }
    )
    assert package["curriculum_resolution"]["status"] == "unknown"
    assert package["schema_version"] == "3.0.0"


def test_large_plain_text_ingestion_budget():
    text = ("Educational source sentence about learning. " * 20_000).encode()
    started = time.perf_counter()
    envelope = ingest_source_bytes("large.txt", text)
    elapsed = time.perf_counter() - started
    assert envelope.ok
    assert elapsed < 2.0


def test_upload_to_vlp_v3_staged_flow(monkeypatch, tmp_path):
    from agents.orchestration import AloraOrchestrator
    from engines.verified_learning_engine.orchestrator import (
        VerifiedLearningOrchestrator,
    )

    source = _source("A seed germinates when water, oxygen, and warmth are available.")
    ref = source["blocks"][0]["block_id"]

    def fake_generation(self, lesson_text, **kwargs):
        profile = kwargs["universal_profile"]
        rows = {}
        for key in OUTPUT_KEYS:
            if key in {"vocabulary", "worksheet"}:
                value = {"body": lesson_text, "source_refs": [ref]}
            else:
                value = _source_fallback_lesson(key, profile, [ref])
            rows[key] = _apply_v3_output_contract(
                value,
                key=key,
                valid_source_refs=[ref],
                fallback_used="source_extractive",
            )
        rows["_meta"] = {
            "publish_qa": {
                "passed": True,
                "publish_blocked": False,
                "checks": [],
                "scorecard": {"source_grounding_coverage": 100.0},
            },
            "stem_qa": {"passed": True},
            "engine_artifacts": [],
            "preferred_visuals": [],
            "knowledge": {
                "external_enrichment": {
                    "status": "no_hits",
                    "required": False,
                },
                "citations": [],
            },
        }
        return rows

    monkeypatch.setattr(AloraOrchestrator, "run_lesson_pipeline", fake_generation)
    orchestrator = VerifiedLearningOrchestrator()
    monkeypatch.setattr(
        orchestrator.registry, "execution_order", lambda only_enabled=True: []
    )
    monkeypatch.setattr(
        orchestrator.packages,
        "persist",
        lambda package: Path(tmp_path) / "fixture-v3.json",
    )
    result = orchestrator.process_lesson(
        source["text"],
        source_envelope=source,
        generate_adaptations=True,
    )
    assert result["pipeline_result"]["status"] == "success"
    assert result["package"]["schema_version"] == "3.0.0"
    assert result["package"]["curriculum_resolution"]["status"] == "unknown"
    assert set(OUTPUT_KEYS) <= set(result["adaptations"])
    assert {stage["stage"] for stage in result["stages"]} >= {
        "source_ingestion",
        "content_classification",
        "universal_profile",
        "adaptation_generation",
        "package",
    }


def test_model_failures_use_scoped_source_fallbacks(monkeypatch):
    import ai_generator
    import engines.lesson_pipeline
    import knowledge.chapter_cache
    import knowledge.service

    source = _source(
        "Evaporation changes liquid water into vapour. Condensation changes "
        "vapour into liquid water. Precipitation returns water to the surface."
    )
    profile = build_universal_lesson_profile(source).to_dict()
    monkeypatch.setattr(ai_generator, "get_effective_api_key", lambda key="": "test-key")
    monkeypatch.setattr(
        ai_generator,
        "_chat",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("provider down")),
    )
    monkeypatch.setattr(
        engines.lesson_pipeline,
        "process_lesson_stem",
        lambda *args, **kwargs: {
            "artifacts": [],
            "qa": {"passed": True},
            "claims_found": 0,
            "preferred_visuals": [],
            "biology_figures": [],
            "prompt_block": "",
        },
    )
    monkeypatch.setattr(
        knowledge.service,
        "prepare_knowledge_for_lesson",
        lambda *args, **kwargs: {
            "external_enrichment": {
                "status": "unavailable",
                "required": False,
                "citation_notice": "No curriculum references available.",
            },
            "citations": [],
            "rag_hits": [],
            "official_mcqs": [],
            "exam_bundle": {},
            "prompt_block": "",
        },
    )
    monkeypatch.setattr(knowledge.chapter_cache, "load_approved_package", lambda *a: None)
    monkeypatch.setattr(knowledge.chapter_cache, "find_approved_for_topic", lambda *a: None)
    result = ai_generator.generate_adaptations(
        source["text"],
        override_api_key="test-key",
        source_envelope=source,
        universal_profile=profile,
    )
    assert set(OUTPUT_KEYS) <= set(result)
    # Chat provider is down: lesson adaptations must use scoped fallbacks.
    # Vocabulary may still be LCE-authored (deterministic) and marked complete.
    chat_keys = [key for key in OUTPUT_KEYS if key != "vocabulary"]
    assert all(
        result[key]["_contract"]["completeness"] == "fallback"
        for key in chat_keys
    )
    assert result["_meta"]["publish_qa"]["publish_blocked"] is False
