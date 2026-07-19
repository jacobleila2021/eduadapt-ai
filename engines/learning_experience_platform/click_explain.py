"""Click-to-explain drawer — CIE / ATIE / KIE / UCF retrieval only."""

from __future__ import annotations

from typing import Any


def explain_target(
    target: str,
    *,
    target_type: str = "concept",  # concept|word|formula|diagram|learning_objective|competency
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = context or {}
    engines = context.get("engine_outputs") or {}
    pieces: list[dict[str, Any]] = []

    # UCF / CIE
    try:
        from engines.universal_curriculum_framework.adapters import for_atie
        from engines.universal_curriculum_framework.curriculum_registry import list_packages

        pid = ""
        pkgs = list_packages()
        if pkgs:
            pid = pkgs[0]["package_id"]
        ucf = for_atie(pid)
        for c in ucf.get("verified_concepts") or []:
            if target.lower() in str(c.get("title") or "").lower():
                pieces.append({"source": "ucf", "payload": c})
    except Exception:  # noqa: BLE001
        pass

    cie = (engines.get("curriculum") or {}).get("payload") or {}
    for c in cie.get("concepts") or []:
        title = c.get("title") if isinstance(c, dict) else str(c)
        if target.lower() in str(title).lower():
            pieces.append({"source": "cie", "payload": c})

    # ATIE explanation
    try:
        from engines.ai_tutor_intelligence_engine.service import api_generate_explanation

        atie = api_generate_explanation(question=f"Explain {target_type}: {target}", topic=target)
        pieces.append({"source": "atie", "payload": atie})
    except Exception as exc:  # noqa: BLE001
        pieces.append({"source": "atie", "error": str(exc), "requires_grounding": True})

    return {
        "ok": True,
        "target": target,
        "target_type": target_type,
        "drawer": {
            "title": target,
            "sources": [p.get("source") for p in pieces],
            "content": pieces,
        },
        "policy": "never_hallucinate_retrieve_only",
    }
