"""Extract STEM claims from lesson text for deterministic engine routing."""

from __future__ import annotations

import re
from dataclasses import dataclass

_ARROWS = ("<=>", "⇌", "->", "→", "⟶", "=")
_RE_ELEMENT = re.compile(r"[A-Z][a-z]?\d*")

_RE_MATH = re.compile(
    r"(?<![\d/])((?:[a-zA-Z0-9\(][a-zA-Z0-9\^*\.\(\)\-\s+\*/]{0,50})\s*=\s*[a-zA-Z0-9\^+\-*/\(\)\.\s]{1,60})(?![\d/])",
)

_RE_PLOT = re.compile(
    r"(?:graph|plot)\s+(?:of\s+|the\s+(?:graph\s+of\s+|function\s+)?)?(?:y\s*=\s*)?([a-zA-Z0-9\^+\-*/\(\)\.\s]{1,40})",
    re.IGNORECASE,
)

_RE_FORCE = re.compile(
    r"(?:force|pressure|F\s*=\s*ma).{0,120}",
    re.IGNORECASE,
)

_RE_PHYSICS_DIAG = re.compile(
    r"free[\s-]?body|force\s+diagram|ray\s+diagram|projectile|vector\s+diagram|motion\s+graph|simple\s+machine|lever\b",
    re.IGNORECASE,
)

_RE_CHART = re.compile(
    r"\b(bar\s+graph|pie\s+chart|histogram|scatter\s+plot|line\s+graph)\b",
    re.IGNORECASE,
)

_RE_STATS = re.compile(
    r"\b(mean|median|mode|standard\s+deviation|variance|statistics)\b",
    re.IGNORECASE,
)

_RE_CALCULUS = re.compile(
    r"\b(differentiate|derivative|integrate|integral|d/dx|dy/dx)\b",
    re.IGNORECASE,
)

_RE_CIRCUIT = re.compile(
    r"(?:draw|make|show).{0,40}(?:series|parallel)?.{0,20}circuit|circuit\s+(?:diagram|with)",
    re.IGNORECASE,
)

_RE_GEOMETRY = re.compile(
    r"(?:construct|draw|show).{0,40}(?:triangle|circle|angle)|geogebra|geometry\s+construction",
    re.IGNORECASE,
)

_RE_SMILES = re.compile(
    r"smiles\s*[:=]\s*([A-Za-z0-9\(\)\[\]=#\\\+\-]+)",
    re.IGNORECASE,
)

_RE_MOLECULE = re.compile(
    r"(?:structure\s+of|draw\s+(?:the\s+)?molecule)\s+(ethanol|methane|ethene|ethyne|benzene|acetic\s+acid)",
    re.IGNORECASE,
)

_CURATED_SMILES = {
    "ethanol": "CCO",
    "methane": "C",
    "ethene": "C=C",
    "ethyne": "C#C",
    "benzene": "c1ccccc1",
    "acetic acid": "CC(=O)O",
}


@dataclass
class StemClaim:
    kind: str
    raw: str
    line_no: int | None = None
    extra: dict | None = None


def _normalize_chem(eq: str) -> str:
    eq = re.sub(r"\s+", " ", eq.strip())
    for arrow in ("→", "⟶", "⇌", "<=>"):
        eq = eq.replace(arrow, "->")
    if "->" not in eq and "=" in eq:
        eq = eq.replace("=", "->", 1)
    return eq


def _line_looks_chemical(side: str) -> bool:
    return bool(_RE_ELEMENT.search(side)) and not re.fullmatch(r"\d+", side.strip())


def _extract_chem_from_line(line: str) -> str | None:
    from engines.content_classifier import classify_content

    classified = classify_content(line)
    if classified.content_type != "chemical_equation":
        return None
    return _normalize_chem(classified.normalized)


def extract_stem_claims(text: str, max_claims: int = 16) -> list[StemClaim]:
    """Find chemistry, math, plots, force, circuits, geometry, molecules."""
    if not (text or "").strip():
        return []

    claims: list[StemClaim] = []
    seen: set[str] = set()

    def add(kind: str, raw: str, line_no: int | None = None, extra: dict | None = None) -> None:
        key = f"{kind}:{raw.lower()}"
        if key in seen or len(claims) >= max_claims:
            return
        seen.add(key)
        claims.append(StemClaim(kind=kind, raw=raw, line_no=line_no, extra=extra))

    for i, line in enumerate(text.splitlines(), start=1):
        from engines.content_classifier import classify_content

        classified = classify_content(line, line_no=i)
        if classified.content_type == "chemical_equation":
            add("chemistry_equation", classified.normalized, i)
        elif classified.content_type in {"math_equation", "math_expression"}:
            add("math_equation", classified.normalized, i)
        elif classified.content_type == "calculus_expression":
            add("math_equation", line.strip(), i, {"validated_expression": classified.normalized})
        elif classified.content_type == "plot_expression":
            add("plot_expression", classified.normalized, i)

        if classified.content_type == "physics_problem":
            add("force_problem", line.strip(), i)

        if _RE_PHYSICS_DIAG.search(line):
            low = line.lower()
            dtype = "free_body"
            if "ray" in low:
                dtype = "ray"
            elif "projectile" in low:
                dtype = "projectile"
            elif "vector" in low:
                dtype = "vector"
            elif "motion" in low:
                dtype = "motion_graph"
            elif "machine" in low or "lever" in low:
                dtype = "simple_machine"
            add("physics_diagram", dtype, i, {"diagram_type": dtype})

        if classified.content_type == "chart_request":
            m = _RE_CHART.search(line)
            label = m.group(1).lower() if m else "bar graph"
            ctype = "bar"
            if "pie" in label:
                ctype = "pie"
            elif "hist" in label:
                ctype = "histogram"
            elif "scatter" in label:
                ctype = "scatter"
            elif "line" in label:
                ctype = "line"
            add("chart", ctype, i, {"chart_type": ctype, "raw": line.strip()})

        if classified.content_type == "statistics_data":
            add("statistics", line.strip(), i, {"raw": line.strip()})

        if classified.content_type == "circuit_request":
            ctype = "parallel" if "parallel" in line.lower() else "series"
            add("circuit", ctype, i, {"description": ctype})

        if classified.content_type == "geometry_request":
            gkind = "triangle"
            if "circle" in line.lower():
                gkind = "circle"
            elif "angle" in line.lower():
                gkind = "angle"
            add("geometry", gkind, i, {"kind": gkind})

        if classified.content_type == "molecule_request":
            for m in _RE_SMILES.finditer(line):
                add("molecule", m.group(1), i, {"smiles": m.group(1)})

        for m in _RE_MOLECULE.finditer(line):
            name = m.group(1).lower()
            smi = _CURATED_SMILES.get(name) or _CURATED_SMILES.get(name.replace("  ", " "))
            if smi:
                add("molecule", smi, i, {"smiles": smi, "name": name})

    return claims
