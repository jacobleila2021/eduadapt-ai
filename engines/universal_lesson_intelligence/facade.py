"""
Read-only Universal Lesson Intelligence facade (Milestones 2.1 + 2.2).

2.1 — wrap envelope / profile / optional STEM passthrough.
2.2 — lazy semantic enrichment from existing extractors (STEM, CIE, AME, AIE, LXP).

Design rules
------------
* No LLM calls. No lesson/adaptation generation.
* Does not mutate caller-owned metadata.
* Missing fields stay empty — never invent educational content.
* Future engines MUST consume this facade, not internal extractors.
"""

from __future__ import annotations

import copy
from types import MappingProxyType
from typing import Any, Mapping

from engines.universal_lesson.profile import (
    UniversalLessonProfile,
    build_universal_lesson_profile,
)

ULI_SCHEMA_VERSION = "3.2.0-semantic"
ULI_MILESTONE_2_2_SMOKE_OK = True

SUPPORTED_SUBJECT_FAMILIES: tuple[str, ...] = (
    "Mathematics",
    "Geometry",
    "Algebra",
    "Arithmetic",
    "Physics",
    "Chemistry",
    "Biology",
    "English",
    "Languages",
    "History",
    "Geography",
    "Economics",
    "Computer Science",
    "Business",
    "Engineering",
    "Medicine",
    "Higher Education",
    "Professional Learning",
    "General / Mixed",
    "Unknown",
)


def _as_profile_dict(
    universal_profile: Mapping[str, Any] | UniversalLessonProfile | dict[str, Any],
) -> dict[str, Any]:
    if isinstance(universal_profile, UniversalLessonProfile):
        return universal_profile.to_dict()
    return dict(universal_profile)


def _freeze_mapping(data: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(dict(data or {}))


def _freeze_list(rows: list[Any] | tuple[Any, ...] | None) -> tuple[Any, ...]:
    return tuple(rows or ())


def _immutable(data: Any) -> Any:
    """
    Return a detached, top-level read-only view.

    Nested values are plain deep-copied dicts/lists (JSON/pickle safe for ULIQE
    evidence). Top-level mappings are wrapped in MappingProxyType.
    """
    cloned = copy.deepcopy(data)
    if isinstance(cloned, dict):
        return MappingProxyType(cloned)
    if isinstance(cloned, list):
        return tuple(cloned)
    return cloned


class UniversalLessonIntelligence:
    """
    Single consumer interface for lesson understanding + semantic enrichment.
    """

    __slots__ = (
        "_envelope",
        "_profile",
        "_stem",
        "_classifications",
        "_enrichment",
        "_auto_enrich",
        "_bundle_cache",
    )

    def __init__(
        self,
        *,
        source_envelope: Mapping[str, Any],
        universal_profile: Mapping[str, Any] | UniversalLessonProfile,
        stem_metadata: Mapping[str, Any] | None = None,
        classifications: list[Any] | None = None,
        enrichment: Mapping[str, Any] | None = None,
        auto_enrich: bool = False,
    ) -> None:
        self._envelope = _freeze_mapping(copy.copy(dict(source_envelope)))
        self._profile = _freeze_mapping(_as_profile_dict(universal_profile))
        self._stem = _freeze_mapping(copy.copy(dict(stem_metadata or {})))
        self._classifications = _freeze_list(
            list(classifications) if classifications is not None else []
        )
        self._enrichment: Mapping[str, Any] | None = (
            _freeze_mapping(copy.deepcopy(dict(enrichment))) if enrichment else None
        )
        self._auto_enrich = bool(auto_enrich)
        self._bundle_cache: Mapping[str, Any] | None = None

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def from_artifacts(
        cls,
        source_envelope: Mapping[str, Any],
        universal_profile: Mapping[str, Any] | UniversalLessonProfile | None = None,
        *,
        stem_metadata: Mapping[str, Any] | None = None,
        classifications: list[Any] | None = None,
        enrich: bool = False,
        enrichment: Mapping[str, Any] | None = None,
    ) -> UniversalLessonIntelligence:
        """
        Build a facade from existing artifacts.

        enrich=False (default): Milestone 2.1 behaviour — no pipeline calls.
        enrich=True: collect verified semantic enrichment (Milestone 2.2).
        """
        envelope = dict(source_envelope)
        profile = (
            _as_profile_dict(universal_profile)
            if universal_profile is not None
            else build_universal_lesson_profile(envelope).to_dict()
        )
        collected = enrichment
        stem = stem_metadata
        classes = classifications
        if enrich and collected is None:
            from engines.universal_lesson_intelligence.enrichment import (
                collect_semantic_enrichment,
            )

            collected = collect_semantic_enrichment(
                envelope,
                profile,
                stem_metadata=stem_metadata,
                classifications=classifications,
            )
            stem = collected.get("stem") or stem_metadata
            classes = list(collected.get("classifications") or classifications or [])
        return cls(
            source_envelope=envelope,
            universal_profile=profile,
            stem_metadata=stem,
            classifications=classes,
            enrichment=collected,
            auto_enrich=False,
        )

    def ensure_enriched(self) -> UniversalLessonIntelligence:
        """
        Lazily attach enrichment. Returns self if already enriched; otherwise a
        new enriched instance (original remains unchanged).
        """
        if self._enrichment is not None:
            return self
        return UniversalLessonIntelligence.from_artifacts(
            dict(self._envelope),
            dict(self._profile),
            stem_metadata=dict(self._stem) or None,
            classifications=list(self._classifications) or None,
            enrich=True,
        )

    def _enrich(self) -> Mapping[str, Any]:
        if self._enrichment is not None:
            return self._enrichment
        if self._auto_enrich:
            enriched = self.ensure_enriched()
            # Copy enrichment onto this instance for subsequent lazy hits
            object.__setattr__(self, "_enrichment", enriched._enrichment)
            object.__setattr__(self, "_stem", enriched._stem)
            object.__setattr__(
                self, "_classifications", enriched._classifications
            )
            return self._enrichment or MappingProxyType({})
        return MappingProxyType({})

    # ------------------------------------------------------------------
    # Raw transitional accessors
    # ------------------------------------------------------------------

    @property
    def schema_version(self) -> str:
        return ULI_SCHEMA_VERSION

    @property
    def enriched(self) -> bool:
        return self._enrichment is not None

    @property
    def source_envelope(self) -> Mapping[str, Any]:
        return self._envelope

    @property
    def universal_profile(self) -> Mapping[str, Any]:
        return self._profile

    @property
    def stem_metadata(self) -> Mapping[str, Any]:
        enrich = self._enrich()
        if enrich.get("stem"):
            return _freeze_mapping(dict(enrich["stem"]))
        return self._stem

    @property
    def classifications(self) -> tuple[Any, ...]:
        enrich = self._enrich()
        if enrich.get("classifications"):
            return _freeze_list(list(enrich["classifications"]))
        return self._classifications

    @property
    def claim_ledger(self) -> tuple[Any, ...]:
        return _freeze_list(list(self._profile.get("claim_ledger") or []))

    @property
    def grounding_mode(self) -> str:
        return str(self._profile.get("grounding_mode") or "uploaded_source")

    @property
    def source_id(self) -> str:
        return str(
            self._profile.get("source_id")
            or self._envelope.get("source_id")
            or ""
        )

    @property
    def enrichment_payload(self) -> Mapping[str, Any]:
        return self._enrich()

    # ------------------------------------------------------------------
    # Educational Semantic Layer
    # ------------------------------------------------------------------

    def educational_structure(self) -> Mapping[str, Any]:
        profile = self._profile
        envelope = self._envelope
        enrich = self._enrich()
        declared = dict(enrich.get("declared") or {})
        curriculum = dict(profile.get("curriculum_resolution") or {})
        subject = declared.get("subject")
        if subject is None and isinstance(envelope.get("user_metadata"), dict):
            subject = envelope["user_metadata"].get("subject")
        age = profile.get("age_estimate") or {}
        grade = declared.get("grade")
        if not grade and isinstance(age, dict):
            grade = age.get("band")
        cie = dict(enrich.get("cie") or {})
        cie_ref = cie.get("curriculum_ref") or cie.get("ref") or {}
        return _immutable(
            {
                "title": profile.get("title"),
                "lesson_title": profile.get("title"),
                "subject": subject or cie_ref.get("subject"),
                "discipline": subject or cie_ref.get("subject"),
                "topic": profile.get("topic"),
                "grade": grade or cie_ref.get("grade"),
                "grade_or_level": grade or (age.get("band") if isinstance(age, dict) else None),
                "board": declared.get("board") or cie_ref.get("board") or curriculum.get("curriculum"),
                "programme": declared.get("programme"),
                "curriculum": curriculum.get("curriculum"),
                "curriculum_resolution": curriculum,
                "language": profile.get("language") or envelope.get("language"),
                "lesson_type": None,
                "estimated_duration": enrich.get("estimated_duration_minutes"),
                "difficulty": dict(profile.get("difficulty") or {}),
                "reading_level": dict(profile.get("difficulty") or {}),
                "teacher_notes": None,
                "learning_mode": None,
                "delivery_type": None,
                "source_metadata": {
                    "source_id": self.source_id,
                    "source_hash": envelope.get("source_hash"),
                    "filename": envelope.get("filename"),
                    "detected_format": envelope.get("detected_format"),
                    "extraction_methods": list(envelope.get("extraction_methods") or []),
                },
                "version": self.schema_version,
                "supported_subject_families": list(SUPPORTED_SUBJECT_FAMILIES),
                "duration_estimate": enrich.get("estimated_duration_minutes"),
            }
        )

    def learning_structure(self) -> Mapping[str, Any]:
        profile = self._profile
        enrich = self._enrich()
        cie = dict(enrich.get("cie") or {})
        ame = list(enrich.get("ame_misconceptions") or [])
        profile_misc = list(profile.get("misconceptions") or [])
        return _immutable(
            {
                "learning_objectives": list(profile.get("learning_objectives") or []),
                "success_criteria": list(cie.get("learning_outcomes") or []),
                "competencies": list(cie.get("competencies") or []),
                "bloom_taxonomy": list(cie.get("bloom_levels") or cie.get("bloom") or []),
                "depth_of_knowledge": list(cie.get("dok") or cie.get("depth_of_knowledge") or []),
                "prerequisites": dict(cie.get("prerequisites") or {}),
                "prior_knowledge": list(
                    (cie.get("prerequisites") or {}).get("required")
                    or (cie.get("learning_gaps") or {}).get("missing")
                    or []
                ),
                "misconceptions": profile_misc + ame,
                "key_concepts": list(profile.get("concepts") or []),
                "concept_hierarchy": list(cie.get("matched_concepts") or cie.get("concepts") or []),
                "lesson_progression": cie.get("progression"),
                "knowledge_dependencies": dict(cie.get("prerequisites") or {}),
                "cross_board_mappings": list(
                    cie.get("cross_curriculum") or cie.get("cross_links") or cie.get("cross_board") or []
                ),
                "vocabulary": list(profile.get("vocabulary") or []),
                "definitions": list(enrich.get("glossary") or []),
                "glossary": list(enrich.get("glossary") or []),
                "skills": list(profile.get("skills") or []),
                "key_ideas": list(profile.get("concepts") or []),
                "examples": list(profile.get("examples") or []),
                "concept_inventory": list(profile.get("concepts") or [])
                + list(cie.get("matched_concepts") or []),
            }
        )

    def stem_structure(self) -> Mapping[str, Any]:
        enrich = self._enrich()
        stem = dict(enrich.get("stem") or self._stem or {})
        claims = list(stem.get("claims_found") or stem.get("claims") or [])
        artifacts = list(stem.get("artifacts") or [])
        formula_inv = list(enrich.get("formula_inventory") or [])
        classifications = list(
            enrich.get("classifications") or self._classifications or []
        )
        return _immutable(
            {
                "formula_inventory": formula_inv,
                "formulae": formula_inv,
                "equations": [
                    c
                    for c in claims
                    if str((c or {}).get("kind") or "")
                    in {"math_equation", "chemistry_equation"}
                ],
                "mathematical_expressions": [
                    c
                    for c in claims
                    if str((c or {}).get("kind") or "").startswith("math")
                ],
                "scientific_calculations": [
                    c
                    for c in claims
                    if str((c or {}).get("kind") or "")
                    in {"force_problem", "physics_diagram", "statistics"}
                ],
                "chemical_equations": [
                    c
                    for c in claims
                    if str((c or {}).get("kind") or "") == "chemistry_equation"
                ],
                "molecules": [
                    c for c in claims if str((c or {}).get("kind") or "") == "molecule"
                ],
                "reactions": [
                    c
                    for c in claims
                    if str((c or {}).get("kind") or "") == "chemistry_equation"
                ],
                "physics_laws": [],
                "biological_terminology": [],
                "constants": [],
                "units": [],
                "symbols": [],
                "graphs": [
                    c
                    for c in claims
                    if str((c or {}).get("kind") or "") in {"chart", "plot_expression"}
                ],
                "tables": [
                    b
                    for b in (self._envelope.get("blocks") or [])
                    if isinstance(b, dict) and b.get("kind") == "table"
                ],
                "interactive_diagram_references": [
                    d
                    for d in (enrich.get("diagrams") or [])
                    if isinstance(d, Mapping) and d.get("interactive_support")
                ],
                "simulation_references": [],
                "claims_found": claims,
                "artifacts": artifacts,
                "preferred_visuals": list(stem.get("preferred_visuals") or []),
                "routing_warnings": list(stem.get("routing_warnings") or []),
                "content_classifications": classifications,
            }
        )

    def diagram_structure(self) -> Mapping[str, Any]:
        enrich = self._enrich()
        return _immutable(
            {
                "diagram_inventory": list(enrich.get("diagrams") or []),
                "figure_references": list(enrich.get("diagrams") or []),
                "captions": [
                    d.get("caption")
                    for d in (enrich.get("diagrams") or [])
                    if isinstance(d, Mapping) and d.get("caption")
                ],
                "alternative_text": [
                    d.get("alt_text")
                    for d in (enrich.get("diagrams") or [])
                    if isinstance(d, Mapping) and d.get("alt_text")
                ],
            }
        )

    def learning_resources(self) -> Mapping[str, Any]:
        blocks = [
            b for b in (self._envelope.get("blocks") or []) if isinstance(b, dict)
        ]
        enrich = self._enrich()
        stem = dict(enrich.get("stem") or self._stem or {})
        return _immutable(
            {
                "diagrams": list(enrich.get("diagrams") or self._profile.get("visual_opportunities") or []),
                "tables": [b for b in blocks if b.get("kind") == "table"],
                "graphs": [
                    c
                    for c in (stem.get("claims_found") or [])
                    if str((c or {}).get("kind") or "") in {"chart", "plot_expression"}
                ],
                "images": [b for b in blocks if b.get("kind") == "image_text"],
                "experiments": [],
                "practical_activities": [],
                "worked_examples": list(self._profile.get("examples") or []),
                "glossary_references": list(enrich.get("glossary") or []),
            }
        )

    def assessment_structure(self) -> Mapping[str, Any]:
        opportunities = list(self._profile.get("assessment_opportunities") or [])
        enrich = self._enrich()
        cie = dict(enrich.get("cie") or {})
        return _immutable(
            {
                "existing_questions": opportunities,
                "assessment_opportunities": opportunities,
                "assessment_objectives": list(cie.get("learning_outcomes") or []),
                "question_mappings": [],
                "competency_mappings": list(cie.get("competencies") or []),
                "official_answer_references": [],
                "mark_scheme_references": [],
                "revision_anchors": [
                    {"anchor_id": a.get("anchor_id"), "kind": "claim"}
                    for a in (enrich.get("section_anchors") or [])[:40]
                ],
                "exam_relevance": cie.get("exam_relevance"),
                "difficulty_progression": cie.get("progression"),
                "misconception_mappings": list(enrich.get("ame_misconceptions") or []),
                "exercises": [],
                "activities": [],
            }
        )

    def accessibility_structure(self) -> Mapping[str, Any]:
        enrich = self._enrich()
        aie = dict(enrich.get("aie_readability") or {})
        return _immutable(
            {
                "reading_level": dict(self._profile.get("difficulty") or {}),
                "age_estimate": dict(self._profile.get("age_estimate") or {}),
                "vocabulary_complexity": aie.get("vocab_complexity") or aie.get("vocabulary_complexity"),
                "sentence_complexity": aie.get("avg_sent_len") or aie.get("average_sentence_length"),
                "language_difficulty": aie.get("reading_level") or aie.get("load"),
                "cognitive_load": aie.get("load") or aie.get("cognitive_load"),
                "accessibility_hints": list(aie.get("recommendations") or []),
                "recommended_presentation_mode": aie.get("chunk_size"),
                "aie_profile_mappings": [],
                "screen_reader_hints": [],
                "audio_availability": False,
                "diagram_descriptions": [
                    d.get("alt_text") or d.get("caption")
                    for d in (enrich.get("diagrams") or [])
                    if isinstance(d, Mapping)
                ],
                "executive_function_demands": [],
                "cognitive_complexity": dict(self._profile.get("difficulty") or {}),
                "accessibility_markers": list(aie.get("recommendations") or []),
                "language": self._profile.get("language") or self._envelope.get("language"),
                "aie_readability_report": aie,
            }
        )

    def tutor_structure(self) -> Mapping[str, Any]:
        """Structured anchors for ATIE — no conversation generation."""
        learn = self.learning_structure()
        assess = self.assessment_structure()
        return _immutable(
            {
                "socratic_prompts": [],
                "hint_anchors": list(learn.get("key_concepts") or [])[:20],
                "worked_example_references": list(learn.get("examples") or []),
                "reflection_prompts": [],
                "misconception_anchors": list(learn.get("misconceptions") or []),
                "guided_discovery_nodes": list(assess.get("assessment_opportunities") or [])[:20],
            }
        )

    def voice_structure(self) -> Mapping[str, Any]:
        enrich = self._enrich()
        return _immutable(
            {
                "pronunciation_metadata": [],
                "narration_segments": list(enrich.get("narration_segments") or []),
                "sentence_timing": [],
                "paragraph_timing": [],
                "read_along_anchors": list(enrich.get("section_anchors") or []),
                "multilingual_references": [],
                "phonetic_guidance": [],
            }
        )

    def companion_structure(self) -> Mapping[str, Any]:
        assess = self.assessment_structure()
        return _immutable(
            {
                "celebration_anchors": list(assess.get("assessment_opportunities") or [])[:10],
                "reflection_opportunities": list(assess.get("revision_anchors") or [])[:10],
                "motivation_checkpoints": list(assess.get("revision_anchors") or [])[10:20],
                "break_recommendations": [],
                "encouragement_opportunities": [],
            }
        )

    def lxp_structure(self) -> Mapping[str, Any]:
        enrich = self._enrich()
        return _immutable(
            {
                "section_anchors": list(enrich.get("section_anchors") or []),
                "paragraph_identifiers": [
                    a.get("anchor_id") for a in (enrich.get("section_anchors") or [])
                ],
                "glossary_references": list(enrich.get("glossary") or []),
                "bookmark_anchors": list(enrich.get("section_anchors") or [])[:50],
                "note_anchors": list(enrich.get("section_anchors") or [])[:50],
                "click_to_explain_targets": list(self.learning_structure().get("key_concepts") or []),
                "highlight_regions": [],
                "interactive_regions": list(
                    self.stem_structure().get("interactive_diagram_references") or []
                ),
                "voice_synchronization_anchors": list(enrich.get("section_anchors") or []),
                "offline_package_metadata": {
                    "source_id": self.source_id,
                    "schema_version": self.schema_version,
                },
            }
        )

    def analytics_structure(self) -> Mapping[str, Any]:
        enrich = self._enrich()
        concepts = list(self.learning_structure().get("key_concepts") or [])
        return _immutable(
            {
                "engagement_events": [],
                "reading_milestones": list(enrich.get("section_anchors") or [])[::10],
                "concept_completion": [
                    {"concept": c.get("concept") if isinstance(c, Mapping) else c, "event": "concept_exposed"}
                    for c in concepts[:30]
                    if c
                ],
                "interaction_points": list(enrich.get("section_anchors") or [])[:40],
                "revision_checkpoints": list(self.assessment_structure().get("revision_anchors") or []),
                "assessment_checkpoints": list(
                    self.assessment_structure().get("assessment_opportunities") or []
                ),
                "learning_events": [],
            }
        )

    def knowledge_graph_structure(self) -> Mapping[str, Any]:
        """Link lesson nodes into existing CIE graph references — do not rebuild."""
        enrich = self._enrich()
        cie = dict(enrich.get("cie") or {})
        learn = self.learning_structure()
        nodes = [
            {"type": "lesson", "id": self.source_id, "label": self._profile.get("title")}
        ]
        for c in learn.get("key_concepts") or []:
            if isinstance(c, Mapping):
                nodes.append(
                    {
                        "type": "concept",
                        "id": c.get("concept") or c.get("concept_id"),
                        "label": c.get("concept") or c.get("name"),
                        "source_refs": c.get("source_refs") or [],
                    }
                )
        for c in learn.get("concept_hierarchy") or []:
            if isinstance(c, Mapping):
                nodes.append(
                    {
                        "type": "cie_concept",
                        "id": c.get("concept_id") or c.get("id"),
                        "label": c.get("name") or c.get("label"),
                        "provenance": "cie",
                    }
                )
        edges = []
        prereq = learn.get("knowledge_dependencies") or {}
        if isinstance(prereq, Mapping):
            for key, vals in prereq.items():
                if isinstance(vals, list):
                    for v in vals:
                        edges.append(
                            {
                                "from": str(v),
                                "to": str(key),
                                "relation": "prerequisite",
                                "provenance": "cie",
                            }
                        )
        return _immutable(
            {
                "nodes": nodes,
                "edges": edges,
                "cie_scope_matched": cie.get("scope_matched"),
                "cie_primary_concept": cie.get("primary_concept_id") or cie.get("primary_id"),
                "graph_extended": False,
                "note": "References CIE runtime graph; does not rebuild ontology.",
            }
        )

    def semantic_bundle(self) -> Mapping[str, Any]:
        if self._bundle_cache is not None:
            return self._bundle_cache
        bundle = _immutable(
            {
                "schema_version": self.schema_version,
                "source_id": self.source_id,
                "grounding_mode": self.grounding_mode,
                "enriched": self.enriched or bool(self._enrich()),
                "educational_structure": dict(self.educational_structure()),
                "learning_structure": dict(self.learning_structure()),
                "stem_structure": dict(self.stem_structure()),
                "diagram_structure": dict(self.diagram_structure()),
                "learning_resources": dict(self.learning_resources()),
                "assessment_structure": dict(self.assessment_structure()),
                "accessibility_structure": dict(self.accessibility_structure()),
                "tutor_structure": dict(self.tutor_structure()),
                "voice_structure": dict(self.voice_structure()),
                "companion_structure": dict(self.companion_structure()),
                "lxp_structure": dict(self.lxp_structure()),
                "analytics_structure": dict(self.analytics_structure()),
                "knowledge_graph_structure": dict(self.knowledge_graph_structure()),
                "enrichment_sources": dict(self._enrich().get("enrichment_sources") or {}),
            }
        )
        object.__setattr__(self, "_bundle_cache", bundle)
        return bundle

    def enriched_profile_view(self) -> Mapping[str, Any]:
        """
        Read-only projection merging profile + enrichment metadata for consumers.
        Does not mutate the underlying universal_profile.
        """
        edu = self.educational_structure()
        learn = self.learning_structure()
        base = dict(self._profile)
        base.update(
            {
                "subject": edu.get("subject"),
                "discipline": edu.get("discipline"),
                "grade": edu.get("grade"),
                "board": edu.get("board"),
                "programme": edu.get("programme"),
                "estimated_duration": edu.get("estimated_duration"),
                "glossary": list(learn.get("glossary") or []),
                "competencies": list(learn.get("competencies") or []),
                "bloom_taxonomy": list(learn.get("bloom_taxonomy") or []),
                "uli_schema_version": self.schema_version,
            }
        )
        return _immutable(base)

    def to_dict(self) -> dict[str, Any]:
        enrich = self._enrich()
        return {
            "uli_schema_version": self.schema_version,
            "source_envelope": copy.deepcopy(dict(self._envelope)),
            "universal_profile": copy.deepcopy(dict(self._profile)),
            "stem_metadata": copy.deepcopy(dict(self.stem_metadata)),
            "classifications": copy.deepcopy(list(self.classifications)),
            "enrichment": copy.deepcopy(dict(enrich)),
            "semantic": dict(self.semantic_bundle()),
        }


def build_universal_lesson_intelligence(
    source_envelope: Mapping[str, Any],
    universal_profile: Mapping[str, Any] | UniversalLessonProfile | None = None,
    *,
    stem_metadata: Mapping[str, Any] | None = None,
    classifications: list[Any] | None = None,
    enrich: bool = False,
) -> UniversalLessonIntelligence:
    """Public factory — set enrich=True for Milestone 2.2 semantic attachment."""
    return UniversalLessonIntelligence.from_artifacts(
        source_envelope,
        universal_profile,
        stem_metadata=stem_metadata,
        classifications=classifications,
        enrich=enrich,
    )


def build_enriched_universal_lesson_intelligence(
    source_envelope: Mapping[str, Any],
    universal_profile: Mapping[str, Any] | UniversalLessonProfile | None = None,
    *,
    stem_metadata: Mapping[str, Any] | None = None,
    classifications: list[Any] | None = None,
) -> UniversalLessonIntelligence:
    """Milestone 2.2 convenience factory (enrich=True)."""
    return build_universal_lesson_intelligence(
        source_envelope,
        universal_profile,
        stem_metadata=stem_metadata,
        classifications=classifications,
        enrich=True,
    )
