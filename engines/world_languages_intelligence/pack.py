"""World Languages Intelligence Pack — SubjectIntelligencePack implementation."""

from __future__ import annotations

from typing import Any, Mapping

from engines.subject_intelligence_core.utilities import extract_uli_text
from engines.subject_intelligence_framework.interfaces import SubjectIntelligencePack
from engines.subject_intelligence_framework.schemas import (
    SubjectAnalysisResult,
    SubjectCapability,
    SubjectId,
)
from engines.world_languages_intelligence.accessibility import world_languages_accessibility_for_uli
from engines.world_languages_intelligence.analytics import analytics_metadata
from engines.world_languages_intelligence.assessment import world_languages_assessment_hints
from engines.world_languages_intelligence.competencies import competency_metadata
from engines.world_languages_intelligence.culture import culture_metadata
from engines.world_languages_intelligence.domains import (
    concept_graph_from_uli,
    detect_domains,
    prerequisite_hints,
)
from engines.world_languages_intelligence.grammar import grammar_metadata
from engines.world_languages_intelligence.language_plugins import detect_languages, list_language_plugins
from engines.world_languages_intelligence.listening import listening_metadata
from engines.world_languages_intelligence.metadata import build_pack_metadata
from engines.world_languages_intelligence.misconceptions import detect_world_languages_misconceptions
from engines.world_languages_intelligence.pedagogy import (
    companion_metadata,
    lxp_hints,
    recommend_visuals,
    revision_summary,
    teaching_strategies,
    tutor_guidance,
)
from engines.world_languages_intelligence.phonetics import phonetics_metadata
from engines.world_languages_intelligence.pronunciation import pronunciation_metadata
from engines.world_languages_intelligence.reading import reading_metadata
from engines.world_languages_intelligence.speaking import speaking_metadata
from engines.world_languages_intelligence.translation import translation_metadata
from engines.world_languages_intelligence.validation import collect_world_languages_quality_signals
from engines.world_languages_intelligence.vocabulary import vocabulary_metadata
from engines.world_languages_intelligence.writing import writing_metadata

PACK_VERSION = "1.0.0"


class WorldLanguagesIntelligencePack(SubjectIntelligencePack):
    """
    Authoritative multilingual teaching layer for Alora AI.

    Provides instructional metadata across world languages via a plugin catalogue.
    English subject ownership remains with ELIP (integration-only here).
    """

    def __init__(self) -> None:
        self.subject = SubjectId("languages", "Languages", "languages")
        self.version = PACK_VERSION

    def capabilities(self) -> list[SubjectCapability]:
        return [
            SubjectCapability("wl.pronunciation", "IPA / stress / minimal pairs (VMLE)", "teaching", True),
            SubjectCapability("wl.grammar", "Grammar / morphology / syntax metadata", "teaching", True),
            SubjectCapability("wl.vocabulary", "Vocab relationships (lesson-bound)", "teaching", True),
            SubjectCapability("wl.skills", "Reading / writing / speaking / listening", "teaching", True),
            SubjectCapability("wl.culture", "Culture / literature / translation notes", "teaching", True),
            SubjectCapability("wl.plugins", "Extensible language plugin catalogue", "teaching", True),
            SubjectCapability("wl.assessment", "Vocab/grammar/skills assessment hints", "assessment", True),
            SubjectCapability("wl.accessibility", "Dyslexia / script / audio a11y", "accessibility", True),
            SubjectCapability("wl.tutor", "Conversation & strategy coaching for ATIE", "tutor", True),
            SubjectCapability("wl.lxp", "IPA / recorder / popups / translation drawer", "lxp", True),
        ]

    def analyse_lesson(self, uli: Any, context: Mapping[str, Any] | None = None) -> SubjectAnalysisResult:
        ctx = dict(context or {})
        exam_mode = bool(ctx.get("exam_mode") or ctx.get("protected_assessment"))
        text = extract_uli_text(uli, include_vocabulary=True)
        domains = detect_domains(text)
        languages = detect_languages(text)
        misconceptions = detect_world_languages_misconceptions(text)
        graph = concept_graph_from_uli(uli, domains)
        prereq = prerequisite_hints(domains)
        graph["prerequisites"] = prereq

        phonetics = phonetics_metadata(text, domains, languages)
        pronunciation = pronunciation_metadata(text, domains, languages)
        grammar = grammar_metadata(text, domains, languages)
        vocabulary = vocabulary_metadata(text, domains, uli)
        reading = reading_metadata(text, domains)
        writing = writing_metadata(text, domains, exam_mode=exam_mode)
        speaking = speaking_metadata(text, domains)
        listening = listening_metadata(text, domains)
        culture = culture_metadata(text, domains)
        translation = translation_metadata(text, domains)

        visuals = recommend_visuals(text, domains)
        teach = teaching_strategies(domains)
        assess = world_languages_assessment_hints(uli, domains)
        revision = revision_summary(domains, misconceptions)
        a11y = world_languages_accessibility_for_uli(uli)
        tutor = tutor_guidance(misconceptions)
        companion = companion_metadata(domains)
        analytics = analytics_metadata(domains, misconceptions, languages)
        competencies = competency_metadata(domains, prereq)
        quality = collect_world_languages_quality_signals(uli)
        lxp = lxp_hints(visuals)
        interactions = [
            {"interaction_id": h.get("hook_id"), "meta": h}
            for h in lxp
            if h.get("hook_id") and not str(h.get("hook_id")).startswith("recommended_")
        ]

        warnings: list[str] = []
        if not domains and not languages:
            warnings.append("No world-language domain or language markers detected; enrichment is minimal.")
        if any(lang.get("integration_only") for lang in languages):
            warnings.append(
                "English detected as integration-only; ELIP remains authoritative for subject key `english`."
            )
        if exam_mode:
            warnings.append("Exam/protected mode: do not reveal writing or oral assessment answers.")

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
                    "languages": [
                        {
                            "id": lang.get("id"),
                            "code": lang.get("code"),
                            "name": lang.get("name"),
                            "scripts": lang.get("scripts"),
                            "direction": lang.get("direction"),
                            "integration_only": bool(lang.get("integration_only")),
                        }
                        for lang in languages
                    ],
                    "language_catalogue_size": len(list_language_plugins()),
                    "phonetics": phonetics,
                    "pronunciation": pronunciation,
                    "grammar": grammar,
                    "vocabulary": vocabulary,
                    "reading": reading,
                    "writing": writing,
                    "speaking": speaking,
                    "listening": listening,
                    "culture": culture,
                    "translation": translation,
                    "companion": companion,
                    "analytics": analytics,
                    "competencies": competencies,
                    "quality_signals": quality.get("teaching"),
                    "english_subject_owner": "english_language_intelligence",
                    "context_keys": list(ctx.keys()),
                },
            ),
        )
