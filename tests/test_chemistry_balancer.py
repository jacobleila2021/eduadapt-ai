"""Deterministic chemistry balancer (ChemPy optional; SymPy on Cloud)."""

from __future__ import annotations

from engines.chemistry.balancer import _balance_with_sympy, atom_balance_ok, balance_equation
from engines.types import ValidationStatus


def test_sympy_balances_common_equations():
    reac, prod = _balance_with_sympy(["H2", "O2"], ["H2O"])
    assert reac == {"H2": 2, "O2": 1}
    assert prod == {"H2O": 2}

    reac, prod = _balance_with_sympy(["Fe", "O2"], ["Fe2O3"])
    assert reac["Fe"] == 4 and reac["O2"] == 3 and prod["Fe2O3"] == 2


def test_balance_equation_atom_validation_gate():
    already = balance_equation("2H2 + O2 -> 2H2O")
    assert already.validation == ValidationStatus.PASS
    assert already.payload.get("already_balanced") is True

    result = balance_equation("Fe + O2 -> Fe2O3")
    assert result.validation == ValidationStatus.PASS
    ok, detail = atom_balance_ok(result.payload["balanced"])
    assert ok, detail
    assert result.provenance.get("method") in {
        "chempy.balance_stoichiometry",
        "sympy.nullspace_stoichiometry",
    }


def test_balance_equation_rejects_empty():
    result = balance_equation("")
    assert result.validation == ValidationStatus.FAIL
