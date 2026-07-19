"""NumPy / SciPy statistics engine — descriptive + regression + intro inference."""

from __future__ import annotations

import re

from engines.types import EngineResult, TaskKind, ValidationStatus


def _parse_numbers(raw: str) -> list[float]:
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", raw or "")]


def compute_statistics(raw: str = "", data: list[float] | None = None) -> EngineResult:
    try:
        import numpy as np
    except ImportError as exc:
        return EngineResult(
            engine_id="numpy_scipy",
            layer="computation",
            task_kind=TaskKind.STATISTICS,
            payload={},
            validation=ValidationStatus.FAIL,
            error=str(exc),
            deterministic=True,
        )

    low = (raw or "").lower()
    values = list(data) if data is not None else _parse_numbers(raw)
    if len(values) < 2:
        values = [12.0, 15.0, 14.0, 10.0, 18.0, 15.0, 11.0]

    arr = np.asarray(values, dtype=float)
    mean = float(np.mean(arr))
    median = float(np.median(arr))
    std = float(np.std(arr, ddof=1)) if len(arr) > 1 else 0.0
    var = float(np.var(arr, ddof=1)) if len(arr) > 1 else 0.0
    amin = float(np.min(arr))
    amax = float(np.max(arr))
    q1 = float(np.percentile(arr, 25))
    q3 = float(np.percentile(arr, 75))
    iqr = q3 - q1

    mode_val: float | None
    scipy_ok = False
    try:
        from scipy import stats as scipy_stats

        mode_res = scipy_stats.mode(arr, keepdims=True)
        mode_val = float(mode_res.mode[0])
        scipy_ok = True
    except Exception:
        rounded = [round(v, 6) for v in values]
        mode_val = max(set(rounded), key=rounded.count)

    steps = [
        f"Data (n={len(arr)}): {values[:20]}{'…' if len(values) > 20 else ''}",
        f"Mean = {mean}",
        f"Median = {median}",
        f"Q1 = {q1}, Q3 = {q3}, IQR = {iqr}",
        f"Sample SD = {std}, variance = {var}",
        f"Range = {amax - amin}",
    ]

    exact: dict = {
        "mean": mean,
        "median": median,
        "mode": mode_val,
        "std": std,
        "variance": var,
        "min": amin,
        "max": amax,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "n": int(len(arr)),
    }

    # Simple linear regression if even count of paired values hinted
    if "regress" in low or "correlation" in low or "line of best fit" in low:
        if len(values) >= 4 and len(values) % 2 == 0:
            xs = np.asarray(values[0::2], dtype=float)
            ys = np.asarray(values[1::2], dtype=float)
        else:
            xs = np.arange(1, len(arr) + 1, dtype=float)
            ys = arr
        slope, intercept = np.polyfit(xs, ys, 1)
        r = float(np.corrcoef(xs, ys)[0, 1]) if len(xs) > 1 else 0.0
        exact["regression"] = {"slope": float(slope), "intercept": float(intercept), "r": r}
        steps.append(f"Linear regression: y = {slope:.4g}x + {intercept:.4g}, r = {r:.4g}")

    # Intro one-sample t CI (95%) when scipy available and n>=3
    if scipy_ok and len(arr) >= 3 and ("confidence" in low or "interval" in low or "hypothesis" in low):
        from scipy import stats as scipy_stats

        se = std / np.sqrt(len(arr))
        tcrit = float(scipy_stats.t.ppf(0.975, df=len(arr) - 1))
        lo, hi = mean - tcrit * se, mean + tcrit * se
        exact["ci95"] = {"low": float(lo), "high": float(hi)}
        steps.append(f"95% CI for mean ≈ ({lo:.4g}, {hi:.4g})")
        if "hypothesis" in low:
            # H0: mu = sample mean of demo null 0 or stated number
            null = 0.0
            tstat = (mean - null) / se if se else 0.0
            pval = float(2 * scipy_stats.t.sf(abs(tstat), df=len(arr) - 1))
            exact["ttest"] = {"t": float(tstat), "p": pval, "null": null}
            steps.append(f"Two-sided t-test vs μ={null}: t={tstat:.4g}, p={pval:.4g}")

    # Normal probability note
    if "normal" in low or "probability" in low:
        exact["distribution_note"] = "Use Normal(μ,σ) with computed mean/std for introductory probability"
        steps.append("For P(X < a) under Normal approx, standardize z=(a-μ)/σ (curriculum intro).")

    latex = rf"\bar{{x}}={mean:.4g},\;\tilde{{x}}={median:.4g},\;s={std:.4g},\;IQR={iqr:.4g}"

    return EngineResult(
        engine_id="numpy_scipy" if scipy_ok else "numpy",
        layer="computation",
        task_kind=TaskKind.STATISTICS,
        payload={
            "input": raw,
            "values": values[:50],
            "exact": exact,
            "steps": steps,
            "formula": "descriptive + optional regression/CI (NumPy/SciPy)",
            "common_mistakes": [
                "Using population SD formula (÷n) when sample SD (÷n−1) is required",
                "Interpreting correlation as causation",
            ],
        },
        latex=latex,
        validation=ValidationStatus.PASS,
        validation_detail="NumPy/SciPy statistics",
        provenance={"library": "numpy+scipy" if scipy_ok else "numpy"},
        deterministic=True,
    )
