"""EATS scoring helpers — dimension scores and overall publisher score."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from eats.constants import SCORE_DIMENSIONS, band_for_score, verdict_for_score


@dataclass
class DimensionScore:
    name: str
    score: float
    notes: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AdaptationAcceptance:
    adaptation_id: str
    dimensions: dict[str, DimensionScore]
    overall: float
    band: str
    verdict: str
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "adaptation_id": self.adaptation_id,
            "dimensions": {k: v.to_dict() for k, v in self.dimensions.items()},
            "overall": round(self.overall, 2),
            "band": self.band,
            "verdict": self.verdict,
            "strengths": list(self.strengths),
            "weaknesses": list(self.weaknesses),
        }


@dataclass
class PackageAcceptance:
    overall: float
    band: str
    verdict: str
    by_adaptation: dict[str, AdaptationAcceptance]
    scores: dict[str, float]
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    rejected_adaptations: list[str] = field(default_factory=list)
    revise_adaptations: list[str] = field(default_factory=list)
    attempts: int = 0
    publication_ready: bool = False
    reject_rendering: bool = True
    report_path: str = ""
    screenshot_dir: str = ""
    golden_delta: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall": round(self.overall, 2),
            "band": self.band,
            "verdict": self.verdict,
            "by_adaptation": {k: v.to_dict() for k, v in self.by_adaptation.items()},
            "scores": {k: round(v, 2) for k, v in self.scores.items()},
            "strengths": list(self.strengths),
            "weaknesses": list(self.weaknesses),
            "rejected_adaptations": list(self.rejected_adaptations),
            "revise_adaptations": list(self.revise_adaptations),
            "attempts": self.attempts,
            "publication_ready": self.publication_ready,
            "reject_rendering": self.reject_rendering,
            "report_path": self.report_path,
            "screenshot_dir": self.screenshot_dir,
            "golden_delta": round(self.golden_delta, 2),
            "educational_quality_score": round(self.scores.get("educational_quality", 0), 2),
            "writing_quality_score": round(self.scores.get("writing_quality", 0), 2),
            "visual_quality_score": round(self.scores.get("visual_quality", 0), 2),
            "accessibility_score": round(self.scores.get("accessibility", 0), 2),
            "pedagogy_score": round(self.scores.get("pedagogy", 0), 2),
            "vocabulary_score": round(self.scores.get("vocabulary", 0), 2),
            "layout_score": round(self.scores.get("layout", 0), 2),
            "adaptation_score": round(self.scores.get("adaptation", 0), 2),
            "assessment_score": round(self.scores.get("assessment", 0), 2),
            "diagram_score": round(self.scores.get("diagram", 0), 2),
            "overall_publisher_score": round(self.overall, 2),
        }


def clamp(n: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, n))


def average(values: list[float], default: float = 0.0) -> float:
    nums = [float(v) for v in values if v is not None]
    if not nums:
        return default
    return sum(nums) / len(nums)


def finalize_adaptation(
    adaptation_id: str,
    dimensions: dict[str, DimensionScore],
) -> AdaptationAcceptance:
    scores = [d.score for d in dimensions.values()]
    overall = clamp(average(scores, 0.0))
    strengths: list[str] = []
    weaknesses: list[str] = []
    for name, dim in dimensions.items():
        if dim.score >= 92:
            strengths.append(f"{adaptation_id}:{name} strong ({dim.score:.0f})")
        if dim.score < 85 or dim.issues:
            weaknesses.extend(dim.issues or [f"{adaptation_id}:{name} weak ({dim.score:.0f})"])
    return AdaptationAcceptance(
        adaptation_id=adaptation_id,
        dimensions=dimensions,
        overall=overall,
        band=band_for_score(overall),
        verdict=verdict_for_score(overall),
        strengths=strengths[:8],
        weaknesses=weaknesses[:12],
    )


def finalize_package(
    by_adaptation: dict[str, AdaptationAcceptance],
    *,
    attempts: int = 0,
    golden_delta: float = 0.0,
) -> PackageAcceptance:
    if not by_adaptation:
        return PackageAcceptance(
            overall=0.0,
            band="reject",
            verdict="reject",
            by_adaptation={},
            scores={d: 0.0 for d in SCORE_DIMENSIONS},
            weaknesses=["No adaptations to evaluate."],
            rejected_adaptations=[],
            revise_adaptations=[],
            attempts=attempts,
            publication_ready=False,
            reject_rendering=True,
            golden_delta=golden_delta,
        )

    overalls = [a.overall for a in by_adaptation.values()]
    # Publisher score is the worst adaptation — every learner version must pass
    overall = clamp(min(overalls))
    dim_avgs: dict[str, float] = {}
    for dim in SCORE_DIMENSIONS:
        vals = []
        for acc in by_adaptation.values():
            if dim in acc.dimensions:
                vals.append(acc.dimensions[dim].score)
        dim_avgs[dim] = average(vals, 0.0)

    rejected = [k for k, v in by_adaptation.items() if v.verdict == "reject"]
    revise = [k for k, v in by_adaptation.items() if v.verdict == "revise"]
    strengths: list[str] = []
    weaknesses: list[str] = []
    for acc in by_adaptation.values():
        strengths.extend(acc.strengths)
        weaknesses.extend(acc.weaknesses)

    verdict = verdict_for_score(overall)
    ready = verdict == "pass" and not rejected
    return PackageAcceptance(
        overall=overall,
        band=band_for_score(overall),
        verdict=verdict if ready or verdict == "reject" else "revise",
        by_adaptation=by_adaptation,
        scores=dim_avgs,
        strengths=strengths[:16],
        weaknesses=weaknesses[:24],
        rejected_adaptations=rejected,
        revise_adaptations=revise,
        attempts=attempts,
        publication_ready=ready,
        reject_rendering=not ready,
        golden_delta=golden_delta,
    )


def empty_dimensions(base: float = 70.0) -> dict[str, DimensionScore]:
    return {name: DimensionScore(name=name, score=base) for name in SCORE_DIMENSIONS}
