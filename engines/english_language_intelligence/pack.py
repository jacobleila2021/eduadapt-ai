"""English Language Intelligence Pack — SubjectIntelligencePack implementation."""

from __future__ import annotations

from typing import Any, Mapping

from engines.english_language_intelligence.accessibility import english_accessibility_for_uli
from engines.english_language_intelligence.analytics import analytics_metadata
from engines.english_language_intelligence.assessment import english_assessment_hints
from engines.english_language_intelligence.competencies import competency_metadata
from engines.english_language_intelligence.domains import (
    concept_graph_from_uli,
    detect_domains,
    prerequisite_hints,
)
from engines.english_language_intelligence.grammar import grammar_metadata
from engines.english_language_intelligence.listening import listening_metadata
from engines.english_language_intelligence.literature import literature_metadata
from engines.english_language_intelligence.metadata import build_pack_metadata
from engines.english_language_intelligence.misconceptions import detect_english_misconceptions
from engines.english_language_intelligence.pedagogy import (
    companion_metadata,
    lxp_hints,
    recommend_visuals,
    revision_summary,
    teaching_strategies,
    tutor_guidance,
)
from engines.english_language_intelligence.pronunciation import pronunciation_metadata
from engines.english_language_intelligence.reading import reading_metadata
from engines.english_language_intelligence.speaking import speaking_metadata
from engines.english_language_intelligence.validation import collect_english_quality_signals
from engines.english_language_intelligence.vocabulary import vocabulary_metadata
from engines.english_language_intelligence.writing import writing_metadata
from engines.subject_intelligence_core.utilities import extract_uli_text
from engines.subject_intelligence_framework.interfaces import SubjectIntelligencePack
from engines.subject_intelligence_framework.schemas import (
    SubjectAnalysisResult,
    SubjectCapability,
    SubjectId,
)

PACK_VERSION = "1.0.0"


class EnglishLanguageIntelligencePack(SubjectIntelligencePack):
    """
    Authoritative English language & literacy teaching layer (SIF non-STEM Phase 1).

    Enriches ULI with reading, vocabulary, grammar, writing, literature, and
    oracy metadata. Never invents curriculum or assessment answers.
    """

    def __init__(self) -> None:
        self.subject = SubjectId("english", "English", "languages")
        self.version = PACK_VERSION

    def capabilities(self) -> list[SubjectCapability]:
        return [
            SubjectCapability("english.reading", "Reading fluency & comprehension metadata", "teaching", True),
            SubjectCapability("english.vocabulary", "Tiered vocabulary scaffolds", "teaching", True),
            SubjectCapability("english.grammar", "Grammar foci & editing cues", "teaching", True),
            SubjectCapability("english.writing", "Writing process guidance (no auto answers)", "teaching", True),
            SubjectCapability("english.literature", "Literature lenses & annotations", "teaching", True),
            SubjectCapability("english.speaking_listening", "Oracy / listening metadata", "teaching", True),
            SubjectCapability("english.assessment", "Bloom/DOK/literacy competency hints", "assessment", True),
            SubjectCapability("english.accessibility", "ELL / dyslexia / audio-first guidance", "accessibility", True),
            SubjectCapability("english.tutor", "Reading/writing/vocab coaching for ATIE", "tutor", True),
            SubjectCapability("english.lxp", "Click-to-define / reading mode / cards", "lxp", True),
        ]

    def analyse_lesson(self, uli: Any, context: Mapping[str, Any] | None = None) -> SubjectAnalysisResult:
        ctx = dict(context or {})
        exam_mode = bool(ctx.get("exam_mode") or ctx.get("protected_assessment"))
        text = extract_uli_text(uli, include_vocabulary=True)
        domains = detect_domains(text)
        misconceptions = detect_english_misconceptions(text)
        graph = concept_graph_from_uli(uli, domains)
        prereq = prerequisite_hints(domains)
        graph["prerequisites"] = prereq

        reading = reading_metadata(text, domains)
        vocab = vocabulary_metadata(text, uli)
        grammar = grammar_metadata(text, domains)
        writing = writing_metadata(text, domains, exam_mode=exam_mode)
        literature = literature_metadata(text, domains)
        speaking = speaking_metadata(text, domains)
        listening = listening_metadata(text, domains)
        pronunciation = pronunciation_metadata(text, domains)
        visuals = recommend_visuals(text, domains)
        teach = teaching_strategies(domains)
        assess = english_assessment_hints(uli, domains)
        revision = revision_summary(domains, misconceptions)
        a11y = english_accessibility_for_uli(uli)
        tutor = tutor_guidance(misconceptions)
        companion = companion_metadata(domains)
        analytics = analytics_metadata(domains, vocab, misconceptions)
        competencies = competency_metadata(domains, prereq)
        quality = collect_english_quality_signals(uli)
        lxp = lxp_hints(visuals, vocab)
        interactions = [
            {"interaction_id": h.get("hook_id"), "meta": h}
            for h in lxp
            if h.get("hook_id") and not str(h.get("hook_id")).startswith("recommended_")
        ]

        warnings: list[str] = []
        if not domains:
            warnings.append("No English literacy domain markers detected; enrichment is minimal.")
        if exam_mode:
            warnings.append("Exam/protected mode: writing guidance must not reveal assessment answers.")

        return SubjectAnalysisResult(
            subject_key=self.subject.key,
            ok=True,
            placeholder=False,
            concept_graph=graph,
            misconceptions=misconceptions,
            visuals=visuals,
            interactions=interactions,
            assessment_hints=assess,
            revision_summary=revision,
            accessibility_guidance=a11y,
            teaching_strategies=teach,
            tutor_guidance=tutor,
            lxp_hints=lxp,
            warnings=warnings,
            metadata=build_pack_metadata(
                version=self.version,
                domains=domains,
                exam_mode=exam_mode,
                extra={
                    "reading": reading,
                    "vocabulary": vocab,
                    "grammar": grammar,
                    "writing": writing,
                    "literature": literature,
                    "speaking": speaking,
                    "listening": listening,
                    "pronunciation": pronunciation,
                    "companion": companion,
                    "analytics": analytics,
                    "competencies": competencies,
                    "quality_signals": quality.get("teaching"),
                    "context_keys": list(ctx.keys()),
                },
            ),
        )
