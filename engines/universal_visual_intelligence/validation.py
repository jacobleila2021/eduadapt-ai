"""UVIE quality signals for ULIQE — additive INFO only."""

from __future__ import annotations

from typing import Any

from engines.universal_visual_intelligence.schemas import VisualSpec


def _finding_seed(rule_id: str, severity: str, message: str, *, category: str = "diagrams") -> dict[str, Any]:
    try:
        from engines.subject_intelligence_core.validation import finding_seed

        return finding_seed(rule_id, severity, message, category=category)
    except Exception:  # noqa: BLE001
        return {
            "rule_id": rule_id,
            "severity": severity,
            "message": message,
            "category": category,
            "evidence": {},
        }


def collect_uvie_quality_signals(specs: list[VisualSpec] | None = None, *, uli: Any = None) -> dict[str, Any]:
    if specs is None:
        from engines.universal_visual_intelligence.service import render_visuals_for_uli

        rendered = render_visuals_for_uli(uli) if uli is not None else {"visuals": []}
        raw = rendered.get("visuals") or []
        specs = []
        for item in raw:
            if isinstance(item, VisualSpec):
                specs.append(item)
            elif isinstance(item, dict):
                specs.append(
                    VisualSpec(
                        visual_id=str(item.get("visual_id") or ""),
                        visual_type=str(item.get("visual_type") or ""),
                        source=str(item.get("source") or ""),
                        provenance=str(item.get("provenance") or ""),
                        caption=str(item.get("caption") or ""),
                        alt_text=str(item.get("alt_text") or ""),
                        asset_paths=list(item.get("asset_paths") or []),
                        svg=str(item.get("svg") or ""),
                        mermaid=str(item.get("mermaid") or ""),
                        invents_curriculum=bool(item.get("invents_curriculum")),
                        deterministic=bool(item.get("deterministic", True)),
                        placeholder=bool(item.get("placeholder")),
                    )
                )

    teaching = {
        "visual_count": len(specs),
        "deterministic_count": sum(1 for s in specs if s.deterministic and not s.placeholder),
        "placeholder_count": sum(1 for s in specs if s.placeholder),
        "missing_alt": sum(1 for s in specs if not (s.alt_text or "").strip()),
        "invention_flags": sum(1 for s in specs if s.invents_curriculum),
    }

    findings_seed: list[dict[str, Any]] = []
    findings_seed.append(
        _finding_seed(
            "ULIQE.UVIE.000",
            "info",
            f"UVIE signals: {teaching['visual_count']} visual(s).",
            category="diagrams",
        )
    )
    if teaching["deterministic_count"]:
        findings_seed.append(
            _finding_seed(
                "ULIQE.UVIE.DETERMINISTIC",
                "info",
                f"{teaching['deterministic_count']} deterministic visual(s) preferred.",
                category="diagrams",
            )
        )
    findings_seed.append(
        _finding_seed(
            "ULIQE.UVIE.PRIORITY",
            "info",
            "Visualization priority applied (official/deterministic before pedagogy; AI invent disabled).",
            category="diagrams",
        )
    )
    if teaching["missing_alt"] == 0 and teaching["visual_count"]:
        findings_seed.append(
            _finding_seed(
                "ULIQE.UVIE.ALT_TEXT",
                "info",
                "All UVIE visuals include alt text.",
                category="accessibility",
            )
        )
    elif teaching["visual_count"]:
        findings_seed.append(
            _finding_seed(
                "ULIQE.UVIE.ALT_TEXT",
                "info",
                f"{teaching['missing_alt']} visual(s) missing alt text (informational).",
                category="accessibility",
            )
        )

    return {
        "visuals": [s.to_dict() for s in specs],
        "teaching": teaching,
        "findings_seed": findings_seed,
        "provenance": "universal_visual_intelligence.validation",
    }
