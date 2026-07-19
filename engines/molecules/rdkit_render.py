"""RDKit molecular structure renderer (optional) with deterministic fallback."""

from __future__ import annotations

import tempfile
from pathlib import Path

from engines.types import EngineResult, TaskKind, ValidationStatus

_KNOWN = {
    "C": "Methane (CH4)",
    "CCO": "Ethanol (C2H5OH)",
    "C=C": "Ethene (C2H4)",
    "C#C": "Ethyne (C2H2)",
    "c1ccccc1": "Benzene (C6H6)",
    "CC(=O)O": "Acetic acid (CH3COOH)",
}


def _fallback_card(smiles: str) -> EngineResult:
    """Deterministic labelled card when RDKit is unavailable."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return EngineResult(
            engine_id="rdkit",
            layer="computation",
            task_kind=TaskKind.MOLECULE_SMILES,
            payload={"smiles": smiles, "name": _KNOWN.get(smiles, smiles)},
            validation=ValidationStatus.WARN,
            validation_detail="RDKit unavailable — structure name only",
            error=None,
            deterministic=True,
        )

    name = _KNOWN.get(smiles, f"SMILES: {smiles}")
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_facecolor("#FFF9EE")
    fig.patch.set_facecolor("#FFFFFF")
    ax.add_patch(plt.Rectangle((0.5, 0.5), 9, 5, fill=False, edgecolor="#008C95", linewidth=2))
    ax.text(5, 4, "Molecular structure", ha="center", fontsize=12, color="#041B4D", fontweight="bold")
    ax.text(5, 2.8, name, ha="center", fontsize=14, color="#008C95")
    ax.text(5, 1.5, f"SMILES: {smiles}", ha="center", fontsize=10, color="#333333")
    ax.text(5, 0.8, "Install RDKit for 2D bond diagram", ha="center", fontsize=8, color="#666666")

    out_dir = Path(tempfile.gettempdir()) / "alora_engines"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"mol_fallback_{abs(hash(smiles)) % 10**10}.png"
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)

    return EngineResult(
        engine_id="molecule_fallback",
        layer="computation",
        task_kind=TaskKind.MOLECULE_SMILES,
        payload={"smiles": smiles, "name": name, "fallback": True},
        asset_paths=[str(path)],
        validation=ValidationStatus.PASS,
        validation_detail="Deterministic structure card (RDKit not installed)",
        provenance={"library": "matplotlib-fallback"},
        deterministic=True,
    )


def smiles_to_png(smiles: str) -> EngineResult:
    smiles = (smiles or "").strip()
    if not smiles:
        return EngineResult(
            engine_id="rdkit",
            layer="computation",
            task_kind=TaskKind.MOLECULE_SMILES,
            payload={},
            validation=ValidationStatus.FAIL,
            error="Empty SMILES",
            deterministic=True,
        )
    try:
        from rdkit import Chem
        from rdkit.Chem import Draw
    except ImportError:
        return _fallback_card(smiles)

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return EngineResult(
            engine_id="rdkit",
            layer="computation",
            task_kind=TaskKind.MOLECULE_SMILES,
            payload={"smiles": smiles},
            validation=ValidationStatus.FAIL,
            error="Invalid SMILES",
            deterministic=True,
        )

    out_dir = Path(tempfile.gettempdir()) / "alora_engines"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"mol_{abs(hash(smiles)) % 10**10}.png"
    Draw.MolToFile(mol, str(path), size=(480, 360))

    return EngineResult(
        engine_id="rdkit",
        layer="computation",
        task_kind=TaskKind.MOLECULE_SMILES,
        payload={"smiles": smiles, "name": _KNOWN.get(smiles)},
        asset_paths=[str(path)],
        validation=ValidationStatus.PASS,
        provenance={"library": "rdkit"},
        deterministic=True,
    )
