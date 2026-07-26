"""Chemistry equation balancer + atom-count validation."""

from __future__ import annotations

import math
import re
from collections import Counter
from functools import reduce

from engines.types import EngineResult, TaskKind, ValidationStatus


_ARROW = re.compile(r"(?:->|→|⟶|<=>|⇌|=)")


def _parse_side(side: str) -> list[tuple[int, str]]:
    """Return list of (coeff, formula) for a reaction side."""
    parts = [p.strip() for p in side.split("+") if p.strip()]
    out: list[tuple[int, str]] = []
    for part in parts:
        m = re.match(r"^(\d+)\s*(.+)$", part)
        if m:
            out.append((int(m.group(1)), m.group(2).strip()))
        else:
            out.append((1, part))
    return out


def _strip_state(formula: str) -> str:
    return re.sub(r"\((s|l|g|aq)\)$", "", formula.replace(" ", ""), flags=re.I)


def _atom_counts(formula: str) -> Counter[str]:
    """Very small formula parser for validation (e.g. H2O, CO2, Ca(OH)2)."""
    formula = _strip_state(formula)

    def parse(frag: str) -> Counter[str]:
        counts: Counter[str] = Counter()
        i = 0
        while i < len(frag):
            if frag[i] == "(":
                depth = 1
                j = i + 1
                while j < len(frag) and depth:
                    if frag[j] == "(":
                        depth += 1
                    elif frag[j] == ")":
                        depth -= 1
                    j += 1
                inner = frag[i + 1 : j - 1]
                mult_m = re.match(r"(\d+)", frag[j:])
                mult = int(mult_m.group(1)) if mult_m else 1
                if mult_m:
                    j += len(mult_m.group(1))
                sub = parse(inner)
                for k, v in sub.items():
                    counts[k] += v * mult
                i = j
                continue
            m = re.match(r"([A-Z][a-z]?)(\d*)", frag[i:])
            if not m:
                raise ValueError(f"Cannot parse formula near: {frag[i:]}")
            el, num = m.group(1), m.group(2)
            counts[el] += int(num) if num else 1
            i += m.end()
        return counts

    return parse(formula)


def atom_balance_ok(equation: str) -> tuple[bool, str]:
    if not _ARROW.search(equation):
        return False, "No reaction arrow found"
    left_s, right_s = _ARROW.split(equation, maxsplit=1)
    left = _parse_side(left_s)
    right = _parse_side(right_s)
    left_atoms: Counter[str] = Counter()
    right_atoms: Counter[str] = Counter()
    try:
        for c, f in left:
            for el, n in _atom_counts(f).items():
                left_atoms[el] += c * n
        for c, f in right:
            for el, n in _atom_counts(f).items():
                right_atoms[el] += c * n
    except ValueError as exc:
        return False, str(exc)
    if left_atoms != right_atoms:
        return False, f"Atom mismatch LHS={dict(left_atoms)} RHS={dict(right_atoms)}"
    return True, "Atom counts match"


def _format_side(species: list[str], coeffs: list[int]) -> str:
    parts: list[str] = []
    for sp, c in zip(species, coeffs):
        parts.append(f"{c if c != 1 else ''}{sp}".strip())
    return " + ".join(parts)


def _balance_with_sympy(reac: list[str], prod: list[str]) -> tuple[dict[str, int], dict[str, int]]:
    """Integer stoichiometry via SymPy nullspace (Cloud-safe; no ChemPy/Jupyter)."""
    from sympy import Matrix, Integer, lcm as sympy_lcm

    species = reac + prod
    comps = [_atom_counts(f) for f in species]
    elements = sorted({el for c in comps for el in c})
    if not elements:
        raise ValueError("No elements parsed from formulas")

    rows: list[list[int]] = []
    for el in elements:
        row: list[int] = []
        for i, comp in enumerate(comps):
            sign = 1 if i < len(reac) else -1
            row.append(sign * int(comp.get(el, 0)))
        rows.append(row)

    nullspace = Matrix(rows).nullspace()
    if not nullspace:
        raise ValueError("No stoichiometry solution")

    vec = nullspace[0]
    dens = [Integer(term.q) for term in vec]
    scale = dens[0]
    for d in dens[1:]:
        scale = sympy_lcm(scale, d)
    coeffs = [int(term * scale) for term in vec]
    if any(c < 0 for c in coeffs):
        coeffs = [-c for c in coeffs]
    if any(c <= 0 for c in coeffs):
        raise ValueError("Non-positive stoichiometry coefficients")
    g = reduce(math.gcd, coeffs)
    coeffs = [c // g for c in coeffs]

    reac_bal = {sp: coeffs[i] for i, sp in enumerate(reac)}
    prod_bal = {sp: coeffs[len(reac) + i] for i, sp in enumerate(prod)}
    return reac_bal, prod_bal


def _balance_with_chempy(reac: list[str], prod: list[str]) -> tuple[dict[str, int], dict[str, int]]:
    from chempy import balance_stoichiometry
    from chempy.util.parsing import formula_to_composition

    for f in reac + prod:
        formula_to_composition(_strip_state(f))
    reac_bal, prod_bal = balance_stoichiometry(reac, prod)
    return dict(reac_bal), dict(prod_bal)


def balance_equation(raw: str) -> EngineResult:
    raw = (raw or "").strip()
    if not raw:
        return EngineResult(
            engine_id="chemistry_balancer",
            layer="computation",
            task_kind=TaskKind.BALANCE_EQUATION,
            payload={},
            validation=ValidationStatus.FAIL,
            error="Empty equation",
            deterministic=True,
        )

    # If already balanced, validate and return
    ok, detail = atom_balance_ok(raw)
    if ok:
        return EngineResult(
            engine_id="chemistry_balancer",
            layer="computation",
            task_kind=TaskKind.BALANCE_EQUATION,
            payload={"input": raw, "balanced": raw, "already_balanced": True},
            latex=rf"\ce{{{raw}}}",
            validation=ValidationStatus.PASS,
            validation_detail=detail,
            provenance={"method": "atom_count_validate"},
            deterministic=True,
        )

    if not _ARROW.search(raw):
        return EngineResult(
            engine_id="chemistry_balancer",
            layer="computation",
            task_kind=TaskKind.BALANCE_EQUATION,
            payload={"input": raw},
            validation=ValidationStatus.FAIL,
            validation_detail=detail,
            error="No reaction arrow found",
            deterministic=True,
        )

    left_s, right_s = _ARROW.split(raw, maxsplit=1)
    reac = [f for _, f in _parse_side(left_s)]
    prod = [f for _, f in _parse_side(right_s)]

    balanced = ""
    engine_id = "chemistry_balancer"
    method = ""
    reac_bal: dict[str, int] = {}
    prod_bal: dict[str, int] = {}

    # Prefer ChemPy when installed (local/engines); else SymPy (Streamlit Cloud).
    try:
        reac_bal, prod_bal = _balance_with_chempy(reac, prod)
        engine_id = "chempy"
        method = "chempy.balance_stoichiometry"
    except ImportError:
        try:
            reac_bal, prod_bal = _balance_with_sympy(reac, prod)
            engine_id = "chemistry_balancer"
            method = "sympy.nullspace_stoichiometry"
        except Exception:  # noqa: BLE001
            return EngineResult(
                engine_id="chemistry_balancer",
                layer="computation",
                task_kind=TaskKind.BALANCE_EQUATION,
                payload={"input": raw},
                validation=ValidationStatus.FAIL,
                validation_detail=detail,
                error="The reaction could not be balanced from the supplied notation",
                deterministic=True,
            )
    except Exception:  # noqa: BLE001
        try:
            reac_bal, prod_bal = _balance_with_sympy(reac, prod)
            engine_id = "chemistry_balancer"
            method = "sympy.nullspace_stoichiometry"
        except Exception:  # noqa: BLE001
            return EngineResult(
                engine_id="chemistry_balancer",
                layer="computation",
                task_kind=TaskKind.BALANCE_EQUATION,
                payload={"input": raw},
                validation=ValidationStatus.FAIL,
                validation_detail=detail,
                error="The reaction could not be balanced from the supplied notation",
                deterministic=True,
            )

    balanced = f"{_format_side(reac, [reac_bal[s] for s in reac])} -> {_format_side(prod, [prod_bal[s] for s in prod])}"
    ok2, detail2 = atom_balance_ok(balanced)
    if not ok2:
        return EngineResult(
            engine_id=engine_id,
            layer="computation",
            task_kind=TaskKind.BALANCE_EQUATION,
            payload={"input": raw, "balanced": balanced},
            validation=ValidationStatus.FAIL,
            validation_detail=detail2,
            error="Balancer output failed atom-count validation",
            deterministic=True,
        )
    return EngineResult(
        engine_id=engine_id,
        layer="computation",
        task_kind=TaskKind.BALANCE_EQUATION,
        payload={
            "input": raw,
            "balanced": balanced,
            "reactants": reac_bal,
            "products": prod_bal,
        },
        latex=rf"\ce{{{balanced}}}",
        validation=ValidationStatus.PASS,
        validation_detail=detail2,
        provenance={"method": method},
        deterministic=True,
    )
