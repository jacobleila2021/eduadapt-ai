"""Broader physics educational diagrams (Matplotlib)."""

from __future__ import annotations

import tempfile
from pathlib import Path

from engines.types import EngineResult, TaskKind, ValidationStatus


def _save(fig, name: str) -> str:
    import matplotlib.pyplot as plt

    out_dir = Path(tempfile.gettempdir()) / "alora_engines"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{name}_{abs(hash(name)) % 10**8}.png"
    fig.savefig(path, dpi=120, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(path)


def draw_physics_diagram(diagram_type: str = "free_body") -> EngineResult:
    """
    Supported: free_body, ray, vector, projectile, motion_graph, simple_machine
    """
    dtype = (diagram_type or "free_body").lower().replace("-", "_").replace(" ", "_")
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError as exc:
        return EngineResult(
            engine_id="physics_diagram",
            layer="computation",
            task_kind=TaskKind.PHYSICS_DIAGRAM,
            payload={"diagram_type": dtype},
            validation=ValidationStatus.FAIL,
            error=str(exc),
            deterministic=True,
        )

    try:
        fig, ax = plt.subplots(figsize=(6.5, 4.5))
        ax.set_facecolor("#FFF9EE")
        fig.patch.set_facecolor("#FFFFFF")

        if dtype in ("free_body", "fbd", "force_diagram"):
            ax.set_xlim(-2, 2)
            ax.set_ylim(-2, 2)
            ax.set_aspect("equal")
            ax.scatter([0], [0], s=400, c="#008C95", zorder=3)
            ax.annotate("Weight (mg)", xy=(0, 0), xytext=(0, -1.4),
                        arrowprops=dict(arrowstyle="->", color="#041B4D", lw=2),
                        ha="center", color="#041B4D")
            ax.annotate("Normal (N)", xy=(0, 0), xytext=(0, 1.4),
                        arrowprops=dict(arrowstyle="->", color="#008C95", lw=2),
                        ha="center", color="#008C95")
            ax.annotate("Friction (f)", xy=(0, 0), xytext=(-1.5, 0),
                        arrowprops=dict(arrowstyle="->", color="#14D9E5", lw=2),
                        ha="right", color="#041B4D")
            ax.set_title("Free-body diagram", color="#041B4D")
            ax.axis("off")
            caption = "Free-body diagram"

        elif dtype in ("ray", "ray_diagram", "light"):
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 6)
            ax.axvline(5, color="#041B4D", lw=2)
            ax.text(5.1, 5.5, "Mirror", color="#041B4D")
            ax.annotate("", xy=(5, 3), xytext=(1, 1),
                        arrowprops=dict(arrowstyle="->", color="#008C95", lw=2))
            ax.annotate("", xy=(9, 1), xytext=(5, 3),
                        arrowprops=dict(arrowstyle="->", color="#14D9E5", lw=2))
            ax.plot([5, 5], [3, 5.2], "--", color="#999999")
            ax.text(2, 1.3, "Incident ray", color="#008C95")
            ax.text(6.5, 1.3, "Reflected ray", color="#14D9E5")
            ax.set_title("Ray diagram (reflection)", color="#041B4D")
            ax.axis("off")
            caption = "Ray diagram"

        elif dtype in ("vector", "vectors"):
            ax.set_xlim(-1, 5)
            ax.set_ylim(-1, 4)
            ax.annotate("", xy=(3, 0), xytext=(0, 0),
                        arrowprops=dict(arrowstyle="->", color="#008C95", lw=2))
            ax.annotate("", xy=(3, 2), xytext=(3, 0),
                        arrowprops=dict(arrowstyle="->", color="#14D9E5", lw=2))
            ax.annotate("", xy=(3, 2), xytext=(0, 0),
                        arrowprops=dict(arrowstyle="->", color="#041B4D", lw=2.5))
            ax.text(1.4, -0.4, "A", color="#008C95")
            ax.text(3.2, 1, "B", color="#14D9E5")
            ax.text(1.2, 1.3, "A+B", color="#041B4D")
            ax.set_title("Vector addition", color="#041B4D")
            ax.grid(True, alpha=0.25)
            caption = "Vector diagram"

        elif dtype in ("projectile", "projectile_motion"):
            t = np.linspace(0, 2.2, 80)
            x = 8 * t
            y = 12 * t - 4.9 * t**2
            ax.plot(x, y, color="#008C95", lw=2)
            ax.scatter([x[0], x[-1]], [y[0], max(y[-1], 0)], c="#041B4D", zorder=3)
            ax.set_xlabel("Range (m)", color="#041B4D")
            ax.set_ylabel("Height (m)", color="#041B4D")
            ax.set_title("Projectile motion", color="#041B4D")
            ax.grid(True, alpha=0.3)
            caption = "Projectile motion"

        elif dtype in ("motion_graph", "motion"):
            t = np.linspace(0, 5, 50)
            v = np.piecewise(t, [t < 2, (t >= 2) & (t < 4), t >= 4], [lambda t: 3 * t, 6, lambda t: 6 - 2 * (t - 4)])
            ax.plot(t, v, color="#008C95", lw=2)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Velocity (m/s)")
            ax.set_title("Motion graph (v–t)", color="#041B4D")
            ax.grid(True, alpha=0.3)
            caption = "Motion graph"

        else:  # simple_machine lever
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 6)
            ax.plot([1, 9], [3, 3], color="#041B4D", lw=4)
            ax.plot([5, 5], [1.5, 3], color="#008C95", lw=6)
            ax.text(5, 1.1, "Fulcrum", ha="center", color="#008C95")
            ax.text(1.5, 3.4, "Load", color="#041B4D")
            ax.text(8, 3.4, "Effort", color="#041B4D")
            ax.set_title("Simple machine — lever", color="#041B4D")
            ax.axis("off")
            caption = "Simple machine (lever)"
            dtype = "simple_machine"

        path = _save(fig, f"physics_{dtype}")
        return EngineResult(
            engine_id="physics_diagram",
            layer="computation",
            task_kind=TaskKind.PHYSICS_DIAGRAM,
            payload={"diagram_type": dtype, "caption": caption},
            asset_paths=[path],
            validation=ValidationStatus.PASS,
            validation_detail=f"Drawn {caption}",
            provenance={"library": "matplotlib"},
            deterministic=True,
        )
    except Exception as exc:  # noqa: BLE001
        return EngineResult(
            engine_id="physics_diagram",
            layer="computation",
            task_kind=TaskKind.PHYSICS_DIAGRAM,
            payload={"diagram_type": dtype},
            validation=ValidationStatus.FAIL,
            error=str(exc),
            deterministic=True,
        )
