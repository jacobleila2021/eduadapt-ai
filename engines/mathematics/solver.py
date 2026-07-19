"""SymPy mathematics facade — exact answers + step-by-step derivation."""

from __future__ import annotations

import re

from engines.types import EngineResult, TaskKind, ValidationStatus
from engines.safe_math import safe_equation, safe_sympify


def _calculus_result(expression: str) -> EngineResult | None:
    """Handle differentiate / integrate requests. Returns None if not calculus."""
    low = expression.lower().strip()
    kind = None
    body = expression
    if re.match(r"^(differentiate|diff|derivative of)\b", low):
        kind = "diff"
        body = re.sub(r"^(differentiate|diff|derivative of)\s+", "", expression, flags=re.I).strip()
    elif re.match(r"^(integrate|integral of|∫)\b", low) or low.startswith("integrate "):
        kind = "integrate"
        body = re.sub(r"^(integrate|integral of|∫)\s*", "", expression, flags=re.I).strip()
    elif "d/dx" in low or "dy/dx" in low:
        kind = "diff"
        body = re.sub(r".*?d[y]?/dx\s*", "", expression, flags=re.I).strip() or expression
    else:
        return None

    try:
        import sympy as sp

        expr = safe_sympify(body, allow_bare_symbol=True)
        x = next(
            (symbol for symbol in expr.free_symbols if symbol.name == "x"),
            sp.Symbol("x", real=True),
        )
        steps = [f"Parse expression: {sp.sstr(expr)}"]
        if kind == "diff":
            steps.append("Differentiate with respect to x (SymPy diff)")
            result = sp.diff(expr, x)
            steps.append(f"d/dx [{sp.sstr(expr)}] = {sp.sstr(result)}")
            latex = rf"\frac{{d}}{{dx}}\left({sp.latex(expr)}\right) = {sp.latex(result)}"
            common = [
                "Forgetting the chain rule on composite functions",
                "Dropping the constant multiple when differentiating",
            ]
        else:
            steps.append("Integrate with respect to x (SymPy integrate)")
            result = sp.integrate(expr, x)
            steps.append(f"∫ {sp.sstr(expr)} dx = {sp.sstr(result)} + C")
            latex = rf"\int {sp.latex(expr)}\,dx = {sp.latex(result)} + C"
            common = [
                "Forgetting +C for indefinite integrals",
                "Incorrect power rule when exponent is −1",
            ]
        exact = sp.sstr(result)
        return EngineResult(
            engine_id="sympy",
            layer="computation",
            task_kind=TaskKind.SOLVE_MATH,
            payload={
                "input": expression,
                "exact": exact,
                "simplified": exact,
                "operation": kind,
                "steps": steps,
                "common_mistakes": common,
            },
            latex=latex,
            validation=ValidationStatus.PASS,
            validation_detail=f"SymPy {kind} with steps",
            provenance={"library": f"sympy-{getattr(sp, '__version__', 'unknown')}"},
            deterministic=True,
        )
    except Exception:  # noqa: BLE001
        return EngineResult(
            engine_id="sympy",
            layer="computation",
            task_kind=TaskKind.SOLVE_MATH,
            payload={"input": expression, "operation": kind},
            validation=ValidationStatus.FAIL,
            error="The calculus expression could not be parsed safely",
            deterministic=True,
        )


def solve(expression: str) -> EngineResult:
    expression = (expression or "").strip()
    if not expression:
        return EngineResult(
            engine_id="sympy",
            layer="computation",
            task_kind=TaskKind.SOLVE_MATH,
            payload={},
            validation=ValidationStatus.FAIL,
            error="Empty expression",
            deterministic=True,
        )

    calc = _calculus_result(expression)
    if calc is not None:
        return calc

    from engines.mathematics.advanced import try_advanced_math

    advanced = try_advanced_math(expression)
    if advanced is not None:
        return advanced

    try:
        import sympy as sp

        steps: list[str] = []

        if "=" in expression:
            left_e, right_e = safe_equation(expression)
            eq = sp.Eq(left_e, right_e)
            steps.append(f"Write the equation: {sp.sstr(eq)}")
            symbols = sorted(eq.free_symbols, key=lambda s: s.name)
            moved = sp.simplify(left_e - right_e)
            steps.append(f"Bring all terms to one side: {sp.sstr(moved)} = 0")
            if not symbols:
                sols = eq
                exact = str(eq)
            else:
                sols = sp.solve(eq, *symbols)
                steps.append(f"Solve for {', '.join(str(s) for s in symbols)} using SymPy")
                exact = sp.sstr(sols)
                steps.append(f"Exact solution(s): {exact}")
                for sol in sols if isinstance(sols, list) else [sols]:
                    if isinstance(sol, dict):
                        check = eq.subs(sol)
                    elif len(symbols) == 1:
                        check = eq.subs(symbols[0], sol)
                    else:
                        check = None
                    if check is not None:
                        steps.append(f"Verify by substitution: {sp.sstr(check)}")
            latex = sp.latex(eq) + r" \Rightarrow " + sp.latex(sols if symbols else eq)
            payload = {
                "input": expression,
                "exact": exact,
                "solutions": str(sols) if symbols else exact,
                "steps": steps,
                "common_mistakes": [
                    "Forgetting to change sign when moving terms across equals",
                    "Dropping a root of a quadratic equation",
                    "Dividing by a variable that could be zero",
                ],
            }
        else:
            expr = safe_sympify(expression)
            steps.append(f"Parse expression: {sp.sstr(expr)}")
            expanded = sp.expand(expr)
            if expanded != expr:
                steps.append(f"Expand: {sp.sstr(expanded)}")
            factored = sp.factor(expr)
            if factored != expr:
                steps.append(f"Factor: {sp.sstr(factored)}")
            simplified = sp.simplify(expr)
            steps.append(f"Simplify: {sp.sstr(simplified)}")
            exact = sp.sstr(simplified)
            latex = sp.latex(simplified)
            payload = {
                "input": expression,
                "exact": exact,
                "simplified": exact,
                "steps": steps,
                "common_mistakes": [
                    "Cancelling terms that are added, not factors",
                    "Incorrect order of operations",
                ],
            }

        return EngineResult(
            engine_id="sympy",
            layer="computation",
            task_kind=TaskKind.SOLVE_MATH,
            payload=payload,
            latex=latex,
            validation=ValidationStatus.PASS,
            validation_detail="SymPy computed exact result with steps",
            provenance={"library": f"sympy-{getattr(sp, '__version__', 'unknown')}"},
            deterministic=True,
        )
    except ImportError:
        return EngineResult(
            engine_id="sympy",
            layer="computation",
            task_kind=TaskKind.SOLVE_MATH,
            payload={},
            validation=ValidationStatus.FAIL,
            error="SymPy not installed. Add sympy to requirements-engines.txt",
            deterministic=True,
        )
    except Exception:  # noqa: BLE001
        return EngineResult(
            engine_id="sympy",
            layer="computation",
            task_kind=TaskKind.SOLVE_MATH,
            payload={"input": expression},
            validation=ValidationStatus.FAIL,
            error="The mathematical expression could not be parsed safely",
            deterministic=True,
        )
