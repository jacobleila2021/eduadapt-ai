"""Restricted mathematical parsing boundary for all SymPy-facing engines."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from typing import Any

import sympy as sp

MAX_EXPRESSION_CHARS = 240
MAX_TOKENS = 96
MAX_OPERATIONS = 48
MAX_DEPTH = 12

SAFE_FUNCTIONS: dict[str, Any] = {
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "sqrt": sp.sqrt,
    "log": sp.log,
    "ln": sp.log,
    "exp": sp.exp,
    "Abs": sp.Abs,
    "pi": sp.pi,
    "E": sp.E,
    "I": sp.I,
    "oo": sp.oo,
}
_MATH_CHARS = re.compile(r"^[A-Za-z0-9\s+\-*/^=().,]+$")
_IDENTIFIER = re.compile(r"\b[A-Za-z][A-Za-z0-9]*\b")
_VARIABLE = re.compile(r"^[A-Za-z](?:\d{0,2})?$")


def _ast_is_safe(expression: str) -> bool:
    """Validate Python-compatible math grammar without invoking SymPy."""
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        return False
    allowed = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.UAdd,
        ast.USub,
        ast.Name,
        ast.Load,
        ast.Constant,
        ast.Call,
    )
    for node in ast.walk(tree):
        if not isinstance(node, allowed):
            return False
        if isinstance(node, ast.Constant) and not isinstance(
            node.value, (int, float)
        ):
            return False
        if isinstance(node, ast.Call):
            if (
                not isinstance(node.func, ast.Name)
                or node.func.id not in SAFE_FUNCTIONS
                or node.keywords
            ):
                return False
    return True


@dataclass(frozen=True)
class MathValidation:
    ok: bool
    normalized: str
    code: str = ""
    reason: str = ""


def validate_math_expression(
    expression: str,
    *,
    allow_equation: bool = True,
    allow_bare_symbol: bool = False,
) -> MathValidation:
    raw = re.sub(r"\s+", " ", str(expression or "")).strip()
    normalized = raw.replace("−", "-").replace("×", "*").replace("÷", "/")
    normalized = normalized.replace("^", "**")
    if not normalized:
        return MathValidation(False, "", "empty_expression", "No expression supplied")
    if len(normalized) > MAX_EXPRESSION_CHARS:
        return MathValidation(
            False, normalized, "expression_too_long", "Expression exceeds the safe limit"
        )
    if any(token in normalized for token in ("__", "[", "]", "{", "}", "'", '"', ":", ";", "\\")):
        return MathValidation(
            False, normalized, "unsafe_token", "Expression contains unsupported syntax"
        )
    if not _MATH_CHARS.fullmatch(normalized.replace("**", "^")):
        return MathValidation(
            False, normalized, "invalid_characters", "Expression contains non-mathematical text"
        )
    if normalized.count("=") > (1 if allow_equation else 0):
        return MathValidation(
            False, normalized, "invalid_equation", "Only one equality is supported"
        )
    if not allow_equation and "=" in normalized:
        return MathValidation(
            False, normalized, "equation_not_allowed", "A function expression was expected"
        )
    grammar_parts = normalized.split("=")
    if any(not part.strip() or not _ast_is_safe(part.strip()) for part in grammar_parts):
        return MathValidation(
            False,
            normalized,
            "invalid_expression_grammar",
            "Expression does not match the supported mathematical grammar",
        )
    tokens = re.findall(r"\*\*|[A-Za-z][A-Za-z0-9]*|\d+(?:\.\d+)?|[()+\-*/,=]", normalized)
    if len(tokens) > MAX_TOKENS:
        return MathValidation(
            False, normalized, "too_many_tokens", "Expression is too complex"
        )
    if len(re.findall(r"\*\*|[+\-*/]", normalized)) > MAX_OPERATIONS:
        return MathValidation(
            False, normalized, "too_many_operations", "Expression is too complex"
        )
    depth = current = 0
    for char in normalized:
        if char == "(":
            current += 1
            depth = max(depth, current)
        elif char == ")":
            current -= 1
            if current < 0:
                return MathValidation(
                    False, normalized, "unbalanced_parentheses", "Parentheses are unbalanced"
                )
    if current or depth > MAX_DEPTH:
        return MathValidation(
            False, normalized, "unsafe_depth", "Expression nesting exceeds the safe limit"
        )
    identifiers = _IDENTIFIER.findall(normalized)
    for identifier in identifiers:
        if identifier in SAFE_FUNCTIONS or _VARIABLE.fullmatch(identifier):
            continue
        return MathValidation(
            False,
            normalized,
            "prose_or_unknown_identifier",
            f"Unsupported mathematical identifier: {identifier}",
        )
    for function_name in re.findall(r"\b([A-Za-z][A-Za-z0-9]*)\s*\(", normalized):
        if function_name not in SAFE_FUNCTIONS:
            return MathValidation(
                False,
                normalized,
                "unsafe_function",
                f"Unsupported mathematical function: {function_name}",
            )
    if (
        not allow_bare_symbol
        and not re.search(r"\d|[+\-*/=^()]|\b(?:sin|cos|tan|sqrt|log|ln|exp)\b", raw)
    ):
        return MathValidation(
            False, normalized, "not_mathematical", "No mathematical structure was detected"
        )
    return MathValidation(True, normalized)


def safe_sympify(
    expression: str,
    *,
    allow_equation: bool = False,
    allow_bare_symbol: bool = False,
) -> sp.Expr:
    validation = validate_math_expression(
        expression,
        allow_equation=allow_equation,
        allow_bare_symbol=allow_bare_symbol,
    )
    if not validation.ok:
        raise ValueError(validation.reason)
    if "=" in validation.normalized:
        raise ValueError("Use safe_equation for equalities")
    local_dict = dict(SAFE_FUNCTIONS)
    for identifier in _IDENTIFIER.findall(validation.normalized):
        if _VARIABLE.fullmatch(identifier):
            local_dict.setdefault(identifier, sp.Symbol(identifier, real=True))
    return sp.sympify(validation.normalized, locals=local_dict, evaluate=True)


def safe_equation(expression: str) -> tuple[sp.Expr, sp.Expr]:
    validation = validate_math_expression(expression, allow_equation=True)
    if not validation.ok or validation.normalized.count("=") != 1:
        raise ValueError(validation.reason or "A single mathematical equality is required")
    left, right = validation.normalized.split("=", 1)
    return safe_sympify(left), safe_sympify(right)
