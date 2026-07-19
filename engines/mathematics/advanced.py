"""Extended SymPy domains — limits, matrices, vectors, complex, coord geometry."""

from __future__ import annotations

import re
import ast

from engines.types import EngineResult, TaskKind, ValidationStatus
from engines.safe_math import safe_sympify


def try_advanced_math(expression: str) -> EngineResult | None:
    """Return EngineResult if expression matches an advanced domain; else None."""
    expr_in = (expression or "").strip()
    if not expr_in:
        return None
    low = expr_in.lower()

    try:
        import sympy as sp
    except ImportError:
        return None

    try:
        # Limits: limit x->0 of sin(x)/x  OR  lim(sin(x)/x, x, 0)
        if re.search(r"\blim(it)?\b", low) or "→" in expr_in or "->" in expr_in:
            m = re.search(
                r"(?:limit|lim)\s*(?:as\s+)?([a-z])\s*(?:->|→|=)\s*([^\s]+)\s*(?:of\s+)?(.+)",
                expr_in,
                re.I,
            )
            if m:
                var_s, to_s, body = m.group(1), m.group(2), m.group(3)
            else:
                m2 = re.search(r"lim\s*\((.+),\s*([a-z])\s*,\s*(.+)\)", expr_in, re.I)
                if not m2:
                    return None
                body, var_s, to_s = m2.group(1), m2.group(2), m2.group(3)
            body_e = safe_sympify(body, allow_bare_symbol=True)
            var = next(
                (symbol for symbol in body_e.free_symbols if symbol.name == var_s),
                sp.Symbol(var_s, real=True),
            )
            to_e = sp.oo if to_s.strip() in ("oo", "inf", "∞") else safe_sympify(to_s)
            result = sp.limit(body_e, var, to_e)
            steps = [
                f"Identify limit: lim_{{{var_s}→{to_s}}} ({sp.sstr(body_e)})",
                "Apply SymPy limit",
                f"Result: {sp.sstr(result)}",
            ]
            return _ok(
                expr_in,
                sp.sstr(result),
                rf"\lim_{{{var_s}\to {sp.latex(to_e)}}} {sp.latex(body_e)} = {sp.latex(result)}",
                steps,
                "limit",
                ["Confusing left/right limits", "Substituting without checking indeterminate form"],
            )

        # Matrix: matrix [[1,2],[3,4]] det / inverse / eigenvalues
        if "matrix" in low or "[[" in expr_in:
            m = re.search(r"\[\[.+\]\]", expr_in)
            if m:
                values = ast.literal_eval(m.group(0))
                if (
                    not isinstance(values, list)
                    or not values
                    or len(values) > 10
                    or any(
                        not isinstance(row, list)
                        or len(row) > 10
                        or any(not isinstance(value, (int, float)) for value in row)
                        for row in values
                    )
                ):
                    raise ValueError("Matrix must be a numeric array up to 10 by 10")
                mat = sp.Matrix(values)
                steps = [f"Parse matrix: {mat}"]
                if "det" in low or "determinant" in low:
                    det = mat.det()
                    steps.append(f"Determinant = {det}")
                    return _ok(expr_in, str(det), sp.latex(det), steps, "matrix_det", ["Sign errors in cofactor expansion"])
                if "inverse" in low:
                    inv = mat.inv()
                    steps.append(f"Inverse = {inv}")
                    return _ok(expr_in, sp.sstr(inv), sp.latex(inv), steps, "matrix_inv", ["Matrix not invertible when det=0"])
                if "eigen" in low:
                    ev = mat.eigenvals()
                    steps.append(f"Eigenvalues = {ev}")
                    return _ok(expr_in, str(ev), sp.latex(list(ev.keys())), steps, "matrix_eigen", [])
                steps.append("Matrix parsed (request det/inverse/eigen for computation)")
                return _ok(expr_in, sp.sstr(mat), sp.latex(mat), steps, "matrix", [])

        # Vector: vector <1,2,3> magnitude / dot / cross
        if "vector" in low or re.search(r"<[^>]+>", expr_in):
            nums = re.findall(r"-?\d+(?:\.\d+)?", expr_in)
            if len(nums) >= 2:
                comps = [sp.Float(n) for n in nums[:3]]
                v = sp.Matrix(comps)
                if "magnitude" in low or "modulus" in low or "|" in expr_in:
                    mag = sp.sqrt(sum(c**2 for c in comps))
                    steps = [f"Components: {comps}", f"|v| = √(Σ c²) = {mag}"]
                    return _ok(expr_in, sp.sstr(mag), sp.latex(mag), steps, "vector_mag", [])
                if "dot" in low and len(nums) >= 4:
                    a = sp.Matrix([sp.Float(n) for n in nums[: len(nums) // 2]])
                    b = sp.Matrix([sp.Float(n) for n in nums[len(nums) // 2 :]])
                    d = a.dot(b)
                    steps = [f"a·b = {d}"]
                    return _ok(expr_in, sp.sstr(d), sp.latex(d), steps, "vector_dot", [])
                steps = [f"Vector {comps}"]
                return _ok(expr_in, sp.sstr(v), sp.latex(v), steps, "vector", [])

        # Complex: complex 3+4i  OR  |3+4i|
        if "complex" in low or "i" in low and re.search(r"\d\s*[+\-]\s*\d+\s*\*?i", low):
            body = re.sub(r"^(complex|modulus of|magnitude of)\s+", "", expr_in, flags=re.I)
            body = body.replace("i", "I").replace("^", "**")
            z = safe_sympify(body, allow_bare_symbol=True)
            if "modulus" in low or "magnitude" in low or "|" in expr_in:
                mag = sp.Abs(z)
                steps = [f"z = {z}", f"|z| = {mag}"]
                return _ok(expr_in, sp.sstr(mag), sp.latex(mag), steps, "complex_mod", ["Forgetting a²+b² under the root"])
            steps = [f"z = {z}", f"Re={sp.re(z)}, Im={sp.im(z)}"]
            return _ok(expr_in, sp.sstr(z), sp.latex(z), steps, "complex", [])

        # Distance / midpoint coordinate geometry
        if "distance" in low or "midpoint" in low:
            nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", expr_in)]
            if len(nums) >= 4:
                x1, y1, x2, y2 = nums[:4]
                if "midpoint" in low:
                    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                    steps = [f"Midpoint = (({x1}+{x2})/2, ({y1}+{y2})/2) = ({mx}, {my})"]
                    return _ok(expr_in, f"({mx}, {my})", rf"({mx}, {my})", steps, "midpoint", [])
                import math

                d = math.hypot(x2 - x1, y2 - y1)
                steps = [f"d = √[({x2}-{x1})²+({y2}-{y1})²] = {d}"]
                return _ok(expr_in, str(d), rf"{d}", steps, "distance", ["Forgetting to square both differences"])

        # Tangent / normal to y=f(x) at x=a
        if "tangent" in low or "normal" in low:
            m = re.search(r"(?:to\s+)?y\s*=\s*([^\s,]+)(?:\s+at\s+x\s*=\s*([-\d.]+))?", expr_in, re.I)
            if m:
                fx = safe_sympify(m.group(1), allow_bare_symbol=True)
                x = next(
                    (symbol for symbol in fx.free_symbols if symbol.name == "x"),
                    sp.Symbol("x", real=True),
                )
                a = float(m.group(2) or 0)
                dy = sp.diff(fx, x)
                slope = float(dy.subs(x, a))
                y0 = float(fx.subs(x, a))
                if "normal" in low:
                    ns = -1 / slope if slope != 0 else sp.oo
                    steps = [f"f'(x)={dy}", f"Normal slope at x={a}: {ns}"]
                    return _ok(expr_in, str(ns), rf"m_n={sp.latex(ns)}", steps, "normal", [])
                steps = [f"f'(x)={dy}", f"Tangent slope at x={a}: {slope}", f"Point ({a}, {y0})"]
                return _ok(expr_in, str(slope), rf"m={slope}", steps, "tangent", ["Using f instead of f' for slope"])

    except Exception:  # noqa: BLE001
        return EngineResult(
            engine_id="sympy",
            layer="computation",
            task_kind=TaskKind.SOLVE_MATH,
            payload={"input": expr_in},
            validation=ValidationStatus.FAIL,
            error="The advanced mathematical expression could not be parsed safely",
            deterministic=True,
        )
    return None


def _ok(inp, exact, latex, steps, op, mistakes):
    return EngineResult(
        engine_id="sympy",
        layer="computation",
        task_kind=TaskKind.SOLVE_MATH,
        payload={
            "input": inp,
            "exact": exact,
            "simplified": exact,
            "operation": op,
            "steps": steps,
            "common_mistakes": mistakes,
        },
        latex=latex,
        validation=ValidationStatus.PASS,
        validation_detail=f"SymPy {op}",
        provenance={"library": "sympy"},
        deterministic=True,
    )
