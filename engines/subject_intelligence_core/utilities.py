"""Common utilities for Subject Intelligence packs."""

from __future__ import annotations

from typing import Any, Mapping


def envelope_text(uli: Any) -> str:
    try:
        env = uli.source_envelope
        if isinstance(env, Mapping):
            return str(env.get("normalized_text") or env.get("text") or "")
        return str(getattr(env, "normalized_text", "") or getattr(env, "text", "") or "")
    except Exception:  # noqa: BLE001
        return ""


def learning_structure_dict(uli: Any) -> dict[str, Any]:
    try:
        return dict(uli.learning_structure())
    except Exception:  # noqa: BLE001
        return {}


def stem_structure_dict(uli: Any) -> dict[str, Any]:
    try:
        return dict(uli.stem_structure())
    except Exception:  # noqa: BLE001
        return {}


def accessibility_structure_dict(uli: Any) -> dict[str, Any]:
    try:
        return dict(uli.accessibility_structure())
    except Exception:  # noqa: BLE001
        return {}


def extract_uli_text(
    uli: Any,
    *,
    include_objectives: bool = True,
    include_vocabulary: bool = False,
    include_claims: bool = True,
    stem_equation_keys: tuple[str, ...] = (),
) -> str:
    """Concatenate source + learning + optional STEM passthrough into one analysis blob."""
    parts: list[str] = [envelope_text(uli)]
    learn = learning_structure_dict(uli)
    for c in learn.get("key_concepts") or []:
        if isinstance(c, Mapping):
            parts.append(str(c.get("concept") or ""))
    if include_objectives:
        for o in learn.get("learning_objectives") or []:
            if isinstance(o, Mapping):
                parts.append(str(o.get("objective") or ""))
            else:
                parts.append(str(o))
    if include_vocabulary:
        for v in learn.get("vocabulary") or []:
            if isinstance(v, Mapping):
                parts.append(str(v.get("term") or ""))
    if include_claims:
        stem = stem_structure_dict(uli)
        for c in stem.get("claims_found") or []:
            if isinstance(c, Mapping):
                parts.append(str(c.get("raw") or c.get("text") or ""))
        for key in stem_equation_keys:
            for item in stem.get(key) or []:
                if isinstance(item, Mapping):
                    parts.append(str(item.get("raw") or item.get("term") or item.get("text") or ""))
                else:
                    parts.append(str(item))
    return "\n".join(p for p in parts if p)


def reading_band(uli: Any) -> Any:
    a11y = accessibility_structure_dict(uli)
    reading = dict(a11y.get("reading_level") or {})
    return reading.get("band")
