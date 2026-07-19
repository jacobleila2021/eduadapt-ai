"""Matplotlib graph engine — functions + statistical chart types."""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

from engines.types import EngineResult, TaskKind, ValidationStatus
from engines.safe_math import safe_sympify


def _out_path(tag: str) -> Path:
    out_dir = Path(tempfile.gettempdir()) / "alora_engines"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^\w.\-]+", "_", tag)[:60]
    return out_dir / f"{safe}_{abs(hash(tag)) % 10**10}.png"


def plot_function(expr: str, x_range: tuple[float, float] = (-10.0, 10.0)) -> EngineResult:
    expr = (expr or "x").strip()
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
        import sympy as sp
    except ImportError as exc:
        return EngineResult(
            engine_id="matplotlib",
            layer="computation",
            task_kind=TaskKind.PLOT_GRAPH,
            payload={},
            validation=ValidationStatus.FAIL,
            error=f"Missing dependency: {exc}",
            deterministic=True,
        )

    try:
        sym = safe_sympify(expr, allow_bare_symbol=True)
        x = next(
            (symbol for symbol in sym.free_symbols if symbol.name == "x"),
            sp.Symbol("x", real=True),
        )
        f = sp.lambdify(x, sym, modules=["numpy"])
        xs = np.linspace(x_range[0], x_range[1], 400)
        ys = f(xs)
        ys = np.asarray(ys, dtype=float)
        if ys.ndim == 0:
            ys = np.full_like(xs, float(ys))
        elif ys.shape != xs.shape:
            ys = np.broadcast_to(ys, xs.shape).astype(float).copy()

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(xs, ys, color="#008C95", linewidth=2)
        ax.axhline(0, color="#041B4D", linewidth=0.8)
        ax.axvline(0, color="#041B4D", linewidth=0.8)
        ax.set_title(f"y = {expr}", color="#041B4D")
        ax.set_facecolor("#FFF9EE")
        fig.patch.set_facecolor("#FFFFFF")
        ax.grid(True, alpha=0.3)

        path = _out_path(f"fn_{expr}")
        fig.savefig(path, dpi=120, bbox_inches="tight")
        plt.close(fig)

        return EngineResult(
            engine_id="matplotlib",
            layer="computation",
            task_kind=TaskKind.PLOT_GRAPH,
            payload={"expression": expr, "x_range": list(x_range), "chart_type": "function"},
            asset_paths=[str(path)],
            latex=rf"y = {sp.latex(sym)}",
            validation=ValidationStatus.PASS,
            provenance={"library": "matplotlib+sympy+numpy"},
            deterministic=True,
        )
    except Exception:  # noqa: BLE001
        return EngineResult(
            engine_id="matplotlib",
            layer="computation",
            task_kind=TaskKind.PLOT_GRAPH,
            payload={"expression": expr},
            validation=ValidationStatus.FAIL,
            error="The graph expression could not be parsed or plotted safely",
            deterministic=True,
        )


def plot_chart(chart_type: str, raw: str = "") -> EngineResult:
    """
    chart_type: line | bar | pie | histogram | scatter
    Uses demo curriculum-safe sample data when no numbers provided.
    """
    ctype = (chart_type or "bar").lower().strip()
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError as exc:
        return EngineResult(
            engine_id="matplotlib",
            layer="computation",
            task_kind=TaskKind.PLOT_GRAPH,
            payload={"chart_type": ctype},
            validation=ValidationStatus.FAIL,
            error=str(exc),
            deterministic=True,
        )

    # Optional inline numbers: "bar 2,4,6,8"
    nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", raw or "")]
    labels = ["A", "B", "C", "D", "E", "F"]

    try:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.set_facecolor("#FFF9EE")
        fig.patch.set_facecolor("#FFFFFF")

        if ctype == "pie":
            data = nums[:4] or [30, 25, 25, 20]
            ax.pie(data, labels=labels[: len(data)], colors=["#008C95", "#14D9E5", "#041B4D", "#7BC96F"])
            ax.set_title("Pie chart", color="#041B4D")
        elif ctype == "histogram":
            data = nums or list(np.random.default_rng(42).normal(50, 10, 80))
            ax.hist(data, bins=8, color="#008C95", edgecolor="#041B4D")
            ax.set_title("Histogram", color="#041B4D")
        elif ctype == "scatter":
            if len(nums) >= 4:
                xs, ys = nums[0::2], nums[1::2]
                n = min(len(xs), len(ys))
                xs, ys = xs[:n], ys[:n]
            else:
                xs = list(range(1, 9))
                ys = [2, 3, 5, 7, 8, 8, 9, 10]
            ax.scatter(xs, ys, color="#008C95", s=60)
            ax.set_title("Scatter plot", color="#041B4D")
            ax.grid(True, alpha=0.3)
        elif ctype == "line":
            data = nums or [1, 3, 2, 5, 4, 6]
            ax.plot(range(1, len(data) + 1), data, color="#008C95", lw=2, marker="o")
            ax.set_title("Line graph", color="#041B4D")
            ax.grid(True, alpha=0.3)
        else:  # bar
            data = nums[:6] or [4, 7, 3, 8, 5]
            ax.bar(labels[: len(data)], data, color="#008C95")
            ax.set_title("Bar graph", color="#041B4D")

        path = _out_path(f"chart_{ctype}_{raw}")
        fig.savefig(path, dpi=120, bbox_inches="tight")
        plt.close(fig)

        return EngineResult(
            engine_id="matplotlib",
            layer="computation",
            task_kind=TaskKind.PLOT_GRAPH,
            payload={"chart_type": ctype, "input": raw, "values": nums[:12]},
            asset_paths=[str(path)],
            validation=ValidationStatus.PASS,
            provenance={"library": "matplotlib"},
            deterministic=True,
        )
    except Exception as exc:  # noqa: BLE001
        return EngineResult(
            engine_id="matplotlib",
            layer="computation",
            task_kind=TaskKind.PLOT_GRAPH,
            payload={"chart_type": ctype},
            validation=ValidationStatus.FAIL,
            error=str(exc),
            deterministic=True,
        )
