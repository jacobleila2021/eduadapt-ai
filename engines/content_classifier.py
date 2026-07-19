"""Deterministic block classification before domain parser invocation."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Literal

from engines.safe_math import validate_math_expression

ContentType = Literal[
    "prose",
    "math_expression",
    "math_equation",
    "calculus_expression",
    "plot_expression",
    "chemical_equation",
    "physics_problem",
    "statistics_data",
    "chart_request",
    "circuit_request",
    "geometry_request",
    "molecule_request",
    "question",
    "code",
    "metadata",
    "unknown",
]


@dataclass(frozen=True)
class ClassifiedContent:
    content_type: ContentType
    raw: str
    normalized: str
    confidence: float
    evidence: list[str]
    line_no: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


_FORMULA = r"(?:\d+\s*)?(?:(?:[A-Z][a-z]?\d*)|(?:\([A-Za-z0-9]+\)\d*))+(?:\((?:s|l|g|aq)\))?"
_CHEMICAL = re.compile(
    rf"{_FORMULA}(?:\s*\+\s*{_FORMULA})*"
    rf"\s*(?:->|→|⟶|⇌|<=>)\s*"
    rf"{_FORMULA}(?:\s*\+\s*{_FORMULA})*"
)
_ELEMENTS = {
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg",
    "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca", "Sc", "Ti", "V", "Cr",
    "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br",
    "Kr", "Rb", "Sr", "Y", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd",
    "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe", "Cs", "Ba", "La",
    "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er",
    "Tm", "Yb", "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au",
    "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th",
    "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm", "Md",
    "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn",
    "Nh", "Fl", "Mc", "Lv", "Ts", "Og",
}
_CODE = re.compile(
    r"^\s*(?:def |class |import |from \w+ import |function |const |let |var |SELECT |INSERT |#include)",
    re.I,
)
_METADATA = re.compile(
    r"^\s*(?:subject|grade|class|board|curriculum|chapter|author|date|title)\s*:",
    re.I,
)


def _valid_formula(formula: str) -> bool:
    value = re.sub(r"^\d+\s*", "", formula.strip())
    value = re.sub(r"\((?:s|l|g|aq)\)$", "", value, flags=re.I)
    if not value or not re.search(r"[A-Z]", value):
        return False
    tokens = re.findall(r"[A-Z][a-z]?|\d+|\(|\)", value)
    if "".join(tokens) != value:
        return False
    if any(token[0].isalpha() and token not in _ELEMENTS for token in tokens):
        return False
    depth = 0
    for token in tokens:
        if token == "(":
            depth += 1
        elif token == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def _valid_chemical_equation(equation: str) -> bool:
    sides = re.split(r"(?:->|→|⟶|⇌|<=>)", equation, maxsplit=1)
    if len(sides) != 2:
        return False
    for side in sides:
        components = [part.strip() for part in side.split("+")]
        if not components or any(not _valid_formula(part) for part in components):
            return False
    return True


def _extract_candidate(line: str) -> str:
    text = line.strip()
    text = re.sub(
        r"^\s*(?:q(?:uestion)?\s*\d*[\s:.)-]*)?",
        "",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"^\s*(?:solve|find|evaluate|simplify|calculate)\s+(?:for\s+)?",
        "",
        text,
        flags=re.I,
    )
    return text.rstrip(" ?.").strip()


def classify_content(raw: str, *, line_no: int | None = None) -> ClassifiedContent:
    line = str(raw or "").strip()
    low = line.lower()
    if not line:
        return ClassifiedContent("unknown", line, "", 0.0, ["empty"], line_no)
    if _CODE.search(line) or "```" in line:
        return ClassifiedContent("code", line, line, 0.98, ["code grammar"], line_no)
    if _METADATA.search(line):
        return ClassifiedContent(
            "metadata", line, line, 0.98, ["metadata label"], line_no
        )
    chemical = _CHEMICAL.search(line)
    if chemical and _valid_chemical_equation(chemical.group(0)):
        normalized = chemical.group(0).replace("→", "->").replace("⟶", "->")
        return ClassifiedContent(
            "chemical_equation",
            line,
            normalized,
            0.99,
            ["chemical formula grammar", "reaction arrow"],
            line_no,
        )
    if re.search(
        r"\bsmiles\s*[:=]|\b(?:structure\s+of|draw\s+(?:the\s+)?molecule)\b",
        line,
        re.I,
    ):
        return ClassifiedContent(
            "molecule_request", line, line, 0.98, ["SMILES label"], line_no
        )
    if re.search(r"\b(?:draw|show|make).{0,50}\bcircuit\b|\bcircuit diagram\b", line, re.I):
        return ClassifiedContent(
            "circuit_request", line, line, 0.94, ["circuit request grammar"], line_no
        )
    if re.search(r"\b(?:construct|draw).{0,50}\b(?:triangle|circle|angle)\b|\bgeogebra\b", line, re.I):
        return ClassifiedContent(
            "geometry_request", line, line, 0.92, ["geometry request grammar"], line_no
        )
    if re.search(r"\b(?:bar graph|pie chart|histogram|scatter plot|line graph)\b", line, re.I):
        return ClassifiedContent(
            "chart_request", line, line, 0.95, ["chart type"], line_no
        )
    if re.search(r"\b(?:mean|median|mode|standard deviation|variance)\b", low) and re.search(r"\d", line):
        return ClassifiedContent(
            "statistics_data", line, line, 0.9, ["statistic term", "numeric data"], line_no
        )
    if re.search(r"\b(?:force|pressure)\b", low) and len(re.findall(r"\d+(?:\.\d+)?", line)) >= 2:
        return ClassifiedContent(
            "physics_problem", line, line, 0.88, ["physics term", "numeric quantities"], line_no
        )

    calculus = re.match(
        r"^\s*(?:differentiate|derive|integrate|evaluate\s+the\s+integral)\s+(.+?)(?:\s+with\s+respect\s+to\s+[A-Za-z])?[?.]?$",
        line,
        re.I,
    )
    if calculus:
        candidate = calculus.group(1).strip()
        validation = validate_math_expression(
            candidate, allow_equation=False, allow_bare_symbol=True
        )
        if validation.ok:
            return ClassifiedContent(
                "calculus_expression",
                line,
                validation.normalized,
                0.96,
                ["calculus command", "safe expression grammar"],
                line_no,
            )

    plot = re.match(
        r"^\s*(?:plot|graph)\s+(?:the\s+)?(?:graph\s+of\s+|function\s+|of\s+)?(?:y\s*=\s*)?(.+?)[?.]?$",
        line,
        re.I,
    )
    if plot:
        candidate = plot.group(1).strip()
        validation = validate_math_expression(
            candidate, allow_equation=False, allow_bare_symbol=True
        )
        if validation.ok:
            return ClassifiedContent(
                "plot_expression",
                line,
                validation.normalized,
                0.96,
                ["plot command", "safe function grammar"],
                line_no,
            )

    candidate = _extract_candidate(line)
    validation = validate_math_expression(candidate, allow_equation=True)
    if validation.ok:
        kind: ContentType = (
            "math_equation" if "=" in validation.normalized else "math_expression"
        )
        confidence = 0.97 if re.match(r"^(?:solve|find|evaluate|simplify|calculate)\b", line, re.I) else 0.9
        return ClassifiedContent(
            kind,
            line,
            validation.normalized,
            confidence,
            ["safe mathematical grammar"],
            line_no,
        )

    if line.endswith("?") or re.match(r"^\s*(?:q(?:uestion)?\s*\d*[\s:.)-])", line, re.I):
        return ClassifiedContent(
            "question", line, line, 0.86, ["question punctuation"], line_no
        )
    return ClassifiedContent(
        "prose", line, line, 0.99, ["no domain parser grammar matched"], line_no
    )


def classify_text(text: str) -> list[ClassifiedContent]:
    return [
        classify_content(line, line_no=index)
        for index, line in enumerate(str(text or "").splitlines(), 1)
        if line.strip()
    ]


def classify_source_blocks(source_envelope: dict) -> list[dict]:
    """Classify every immutable source block while retaining provenance."""
    rows: list[dict] = []
    for block in source_envelope.get("blocks") or []:
        if not isinstance(block, dict):
            continue
        for classified in classify_text(str(block.get("text") or "")):
            row = classified.to_dict()
            row.update(
                {
                    "source_block_id": block.get("block_id"),
                    "page": block.get("page"),
                    "slide": block.get("slide"),
                    "extraction_method": block.get("extraction_method"),
                }
            )
            rows.append(row)
    return rows
