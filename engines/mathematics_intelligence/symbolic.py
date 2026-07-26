"""Symbolic consistency helpers — reuse safe_math / STEM claims; never invent solutions."""

from __future__ import annotations

from typing import Any, Mapping


def _stem_claims(uli: Any) -> list[dict[str, Any]]:
    try:
        stem = dict(uli.stem_structure())
        rows = list(stem.get("claims_found") or [])
        return [dict(r) for r in rows if isinstance(r, Mapping)]
    except Exception:  # noqa: BLE001
        return []


def _artifacts(uli: Any) -> list[dict[str, Any]]:
    try:
        stem = dict(uli.stem_structure())
        return [dict(a) for a in (stem.get("artifacts") or []) if isinstance(a, Mapping)]
    except Exception:  # noqa: BLE001
        return []


def inspect_symbolic_consistency(uli: Any) -> dict[str, Any]:
    """
    Report symbol/formula integrity signals from existing STEM pipeline outputs.
    Does not solve new problems beyond what Computation Layer already produced.
    """
    claims = _stem_claims(uli)
    artifacts = _artifacts(uli)
    math_claims = [
        c
        for c in claims
        if str(c.get("kind") or "").startswith("math")
        or str(c.get("kind") or "") in {"plot_expression", "geometry", "statistics"}
    ]
    failed = [
        a
        for a in artifacts
        if a.get("ok") is False
        or str(a.get("validation") or "").lower() in {"fail", "failed"}
    ]
    ok_arts = [a for a in artifacts if a.get("ok") is not False]

    parse_checks: list[dict[str, Any]] = []
    try:
        from engines.safe_math import validate_math_expression
    except Exception:  # noqa: BLE001
        validate_math_expression = None  # type: ignore

    if validate_math_expression:
        for claim in math_claims[:12]:
            raw = str(claim.get("raw") or "")
            if not raw or len(raw) > 200:
                continue
            try:
                result = validate_math_expression(raw)
                parse_checks.append(
                    {
                        "expression": raw[:120],
                        "ok": bool(getattr(result, "ok", result)),
                        "detail": str(
                            getattr(result, "reason", None)
                            or getattr(result, "code", "")
                            or ""
                        )[:200],
                    }
                )
            except Exception as exc:  # noqa: BLE001
                parse_checks.append({"expression": raw[:120], "ok": False, "detail": str(exc)[:200]})

    return {
        "math_claim_count": len(math_claims),
        "artifact_ok_count": len(ok_arts),
        "artifact_failed_count": len(failed),
        "parse_checks": parse_checks,
        "symbol_consistency": "pass"
        if not failed and all(p.get("ok", True) for p in parse_checks)
        else ("warn" if parse_checks or failed else "n/a"),
        "provenance": "mathematics_intelligence.symbolic",
    }
