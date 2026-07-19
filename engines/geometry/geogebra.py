"""GeoGebra embed helpers + offline Matplotlib fallback constructions."""

from __future__ import annotations

import tempfile
from pathlib import Path
from urllib.parse import quote

from engines.types import EngineResult, TaskKind, ValidationStatus


def _commands_for(kind: str) -> list[str]:
    k = (kind or "triangle").lower().replace("-", "_").replace(" ", "_")
    catalog = {
        "circle": ["A = (0, 0)", "B = (3, 0)", "c = Circle(A, B)", 'SetCaption(c, "Circle")'],
        "angle": [
            "A = (0, 0)",
            "B = (4, 0)",
            "C = (1, 3)",
            "angleABC = Angle(B, A, C)",
            'SetCaption(angleABC, "∠BAC")',
        ],
        "transform": [
            "A = (0, 0)",
            "B = (3, 0)",
            "C = (1.5, 2.5)",
            "poly = Polygon(A, B, C)",
            "axis = Line((0,0),(1,0))",
            "poly2 = Reflect(poly, axis)",
        ],
        "reflect": [
            "A = (0, 0)",
            "B = (3, 0)",
            "C = (1.5, 2.5)",
            "poly = Polygon(A, B, C)",
            "axis = Line((0,0),(1,0))",
            "poly2 = Reflect(poly, axis)",
        ],
        "coordinate": [
            "A = (1, 2)",
            "B = (4, 5)",
            "seg = Segment(A, B)",
            'SetCaption(A, "A(1,2)")',
            'SetCaption(B, "B(4,5)")',
        ],
        "polygon": [
            "A=(0,0)",
            "B=(4,0)",
            "C=(5,3)",
            "D=(1,4)",
            "p=Polygon(A,B,C,D)",
            'SetCaption(p,"Polygon")',
        ],
        "locus": [
            "A=(0,0)",
            "B=(4,0)",
            "C=(2,3)",
            "c=Circle(A,B)",
            "P=Point(c)",
            'SetCaption(P,"Locus point on circle")',
        ],
        "parabola": ["f(x)=x^2", 'SetCaption(f,"y=x²")'],
        "ellipse": ["e=Ellipse((0,0),(3,0),(0,2))", 'SetCaption(e,"Ellipse")'],
        "hyperbola": ["h=Hyperbola((0,0),(3,0),(4,0))", 'SetCaption(h,"Hyperbola")'],
        "conic": ["e=Ellipse((0,0),(3,0),(0,2))", 'SetCaption(e,"Conic (ellipse)")'],
    }
    if k in catalog:
        return catalog[k]
    for key, cmds in catalog.items():
        if key in k:
            return cmds
    return [
        "A = (0, 0)",
        "B = (4, 0)",
        "C = (1, 3)",
        "poly = Polygon(A, B, C)",
        'SetCaption(poly, "Triangle ABC")',
    ]


def _offline_fallback_png(kind: str) -> str | None:
    """Deterministic Matplotlib sketch when GeoGebra network is unavailable."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        return None

    fig, ax = plt.subplots(figsize=(5.5, 4))
    ax.set_facecolor("#FFF9EE")
    k = (kind or "triangle").lower()
    if "circle" in k:
        circ = plt.Circle((0, 0), 2, fill=False, color="#008C95", lw=2)
        ax.add_patch(circ)
        ax.plot([0], [0], "o", color="#041B4D")
        ax.set_title("Circle (offline fallback)")
    elif "parabola" in k or "conic" in k:
        xs = np.linspace(-3, 3, 200)
        ax.plot(xs, xs**2, color="#008C95", lw=2)
        ax.set_title("y = x² (offline fallback)")
    elif "coordinate" in k:
        ax.plot([1, 4], [2, 5], "o-", color="#008C95")
        ax.annotate("A(1,2)", (1, 2))
        ax.annotate("B(4,5)", (4, 5))
        ax.set_title("Coordinate segment (offline)")
    else:
        ax.plot([0, 4, 1, 0], [0, 0, 3, 0], color="#008C95", lw=2)
        ax.set_title("Triangle ABC (offline fallback)")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color="#041B4D", lw=0.6)
    ax.axvline(0, color="#041B4D", lw=0.6)
    out = Path(tempfile.gettempdir()) / "alora_engines"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"geogebra_fallback_{abs(hash(kind)) % 10**8}.png"
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return str(path)


def parse_geometry_kind(problem: str) -> str:
    low = (problem or "").lower()
    for key in (
        "hyperbola",
        "ellipse",
        "parabola",
        "conic",
        "locus",
        "polygon",
        "coordinate",
        "reflect",
        "transform",
        "circle",
        "angle",
        "triangle",
    ):
        if key in low:
            return key
    return "triangle"


def build_geogebra(kind: str = "triangle") -> EngineResult:
    """
    Build GeoGebra embed + offline PNG fallback.
    Streamlit: prefer iframe; show asset_paths when offline.
    """
    kind = parse_geometry_kind(kind) if " " in (kind or "") else (kind or "triangle")
    commands = _commands_for(kind)
    cmd_joined = ";".join(commands)
    iframe_url = f"https://www.geogebra.org/calculator?command={quote(cmd_joined)}"
    offline = _offline_fallback_png(kind)
    assets = [offline] if offline else []

    return EngineResult(
        engine_id="geogebra",
        layer="computation",
        task_kind=TaskKind.GEOMETRY,
        payload={
            "geometry_kind": kind,
            "commands": commands,
            "iframe_url": iframe_url,
            "offline_fallback": bool(offline),
            "embed_hint": "st.components.v1.iframe(iframe_url, height=480)",
        },
        latex=None,
        asset_paths=assets,
        validation=ValidationStatus.PASS,
        validation_detail=f"GeoGebra construction ready: {kind}",
        provenance={"library": "geogebra-embed+matplotlib-fallback"},
        deterministic=True,
    )
