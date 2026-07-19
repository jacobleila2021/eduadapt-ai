"""Learner model store — evolves after interactions; wraps AME/AIE evidence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

from engines.adaptive_learning_engine.schemas import LearnerModel

ALE_DIR = DATA_DIR / "ale"
MODELS_DIR = ALE_DIR / "learner_models"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(learner_id: str) -> Path:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in learner_id)[:80]
    return MODELS_DIR / f"{safe}.json"


def load_learner_model(learner_id: str) -> LearnerModel:
    path = _path(learner_id)
    if not path.is_file():
        return LearnerModel(learner_id=learner_id, updated_at=_now())
    return LearnerModel.from_dict(json.loads(path.read_text(encoding="utf-8")))


def save_learner_model(model: LearnerModel) -> Path:
    model.updated_at = _now()
    path = _path(model.learner_id)
    path.write_text(json.dumps(model.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def refresh_from_engines(
    learner_id: str,
    *,
    context: dict[str, Any] | None = None,
    cie: dict[str, Any] | None = None,
    ame: dict[str, Any] | None = None,
    aie: dict[str, Any] | None = None,
) -> LearnerModel:
    """
    Continuously update learner model from verified engine outputs.
    Does not invent mastery — reads AME/CIE/AIE.
    """
    context = context or {}
    model = load_learner_model(learner_id)
    model.grade = str(context.get("grade") or model.grade or "")

    # AIE profile
    if aie:
        lp = aie.get("learner_profile") or {}
        model.accessibility_profiles = list(lp.get("active_profiles") or aie.get("profiles_generated") or model.accessibility_profiles)
        model.preferred_modalities = list(lp.get("preferred_modalities") or model.preferred_modalities)
        model.reading_level = str(lp.get("reading_level") or model.reading_level)
        model.working_memory = str(lp.get("working_memory") or model.working_memory)
        model.processing_speed = str(lp.get("processing_speed") or model.processing_speed)
        model.attention = str(lp.get("attention_profile") or model.attention)

    # CIE curriculum binding
    if cie:
        ref = cie.get("curriculum_ref") or {}
        model.curriculum = str(ref.get("board") or ref.get("curriculum_id") or model.curriculum)
        if ref.get("subject"):
            subj = str(ref["subject"])
            if subj not in model.subjects:
                model.subjects.append(subj)

    # AME mastery
    if ame:
        mastery = ame.get("mastery") or {}
        # mastery may be summary with weak/strong or concept map
        weak = mastery.get("weak_concepts") or []
        strong = mastery.get("strong_concepts") or []
        if isinstance(weak, list) and weak and isinstance(weak[0], dict):
            model.concepts_at_risk = [w.get("concept_id") for w in weak if w.get("concept_id")]
            model.concepts_developing = list(model.concepts_at_risk)
        if isinstance(strong, list) and strong and isinstance(strong[0], dict):
            model.concepts_mastered = [s.get("concept_id") for s in strong if s.get("concept_id")]
        # full mastery map if present
        mmap = mastery.get("mastery") if isinstance(mastery.get("mastery"), dict) else None
        if mmap is None and ame.get("assessment_package") is None:
            # try load from AME store
            try:
                from engines.assessment_mastery_engine.store import load_learner

                st = load_learner(learner_id)
                mmap = st.get("mastery") or {}
            except Exception:  # noqa: BLE001
                mmap = {}
        if isinstance(mmap, dict) and mmap:
            mastered, developing, risk = [], [], []
            for cid, row in mmap.items():
                pct = float(row.get("mastery_pct") or 0)
                level = (row.get("level") or "").lower()
                if level in ("proficient", "advanced", "mastered") or pct >= 0.75:
                    mastered.append(cid)
                elif pct < 0.4 or level == "beginning":
                    risk.append(cid)
                else:
                    developing.append(cid)
            model.concepts_mastered = mastered
            model.concepts_developing = developing
            model.concepts_at_risk = risk

        ready = ame.get("exam_readiness") or {}
        if ready.get("confidence_level") is not None:
            model.confidence = float(ready["confidence_level"])
        elif ready.get("readiness_score") is not None:
            model.confidence = float(ready["readiness_score"])

    # Direct context overrides
    if context.get("confidence") is not None:
        model.confidence = float(context["confidence"])
    if context.get("motivation_level") is not None:
        model.motivation_level = float(context["motivation_level"])
    if context.get("teacher_observations"):
        model.teacher_observations = list(context["teacher_observations"])
    if context.get("parent_observations"):
        model.parent_observations = list(context["parent_observations"])

    save_learner_model(model)
    return model


def apply_teacher_override(
    learner_id: str,
    *,
    decision_type: str,
    choice: str,
    reason: str,
    teacher_id: str = "teacher",
) -> LearnerModel:
    model = load_learner_model(learner_id)
    model.teacher_overrides.append(
        {
            "at": _now(),
            "decision_type": decision_type,
            "choice": choice,
            "reason": reason,
            "teacher_id": teacher_id,
        }
    )
    save_learner_model(model)
    return model


def list_learner_ids() -> list[str]:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    return [p.stem for p in MODELS_DIR.glob("*.json")]
