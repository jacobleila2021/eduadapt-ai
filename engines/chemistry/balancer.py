"""Chemistry equation balancer + atom-count validation."""

from __future__ import annotations

import re
from collections import Counter

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


def _atom_counts(formula: str) -> Counter[str]:
    """Very small formula parser for validation (e.g. H2O, CO2, Ca(OH)2)."""
    formula = formula.replace(" ", "")
    # Strip state symbols
    formula = re.sub(r"\((s|l|g|aq)\)$", "", formula, flags=re.I)

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

    # Try ChemPy if available
    try:
        from chempy import balance_stoichiometry
        from chempy.util.parsing import formula_to_composition

        if not _ARROW.search(raw):
            raise ValueError("No arrow")
        left_s, right_s = _ARROW.split(raw, maxsplit=1)
        reac = [f for _, f in _parse_side(left_s)]
        prod = [f for _, f in _parse_side(right_s)]
        # Validate formulas parse
        for f in reac + prod:
            formula_to_composition(re.sub(r"\((s|l|g|aq)\)$", "", f, flags=re.I))
        reac_bal, prod_bal = balance_stoichiometry(reac, prod)
        left_out = " + ".join(f"{c if c != 1 else ''}{sp}".strip() for sp, c in reac_bal.items())
        right_out = " + ".join(f"{c if c != 1 else ''}{sp}".strip() for sp, c in prod_bal.items())
        balanced = f"{left_out} -> {right_out}"
        ok2, detail2 = atom_balance_ok(balanced)
        if not ok2:
            return EngineResult(
                engine_id="chempy",
                layer="computation",
                task_kind=TaskKind.BALANCE_EQUATION,
                payload={"input": raw, "balanced": balanced},
                validation=ValidationStatus.FAIL,
                validation_detail=detail2,
                error="Balancer output failed atom-count validation",
                deterministic=True,
            )
        return EngineResult(
            engine_id="chempy",
            layer="computation",
            task_kind=TaskKind.BALANCE_EQUATION,
            payload={"input": raw, "balanced": balanced, "reactants": dict(reac_bal), "products": dict(prod_bal)},
            latex=rf"\ce{{{balanced}}}",
            validation=ValidationStatus.PASS,
            validation_detail=detail2,
            provenance={"method": "chempy.balance_stoichiometry"},
            deterministic=True,
        )
    except ImportError:
        return EngineResult(
            engine_id="chemistry_balancer",
            layer="computation",
            task_kind=TaskKind.BALANCE_EQUATION,
            payload={"input": raw},
            validation=ValidationStatus.FAIL,
            validation_detail=detail,
            error=(
                "Equation is unbalanced and ChemPy is not installed. "
                "Install chempy (see requirements-engines.txt). LLM must not balance this."
            ),
            deterministic=True,
        )
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
