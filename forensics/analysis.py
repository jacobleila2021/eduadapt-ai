"""Stage comparison, ECS, blame, disable probes, adaptation audit, historical compare."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

from forensics.learner_metrics import (
    TEACHER_ADVISORY,
    _text_blob,
    adaptation_scores,
    compare_stage_metrics,
    dumps,
    phrase_hits,
    score_lesson_surface,
    structural_similarity,
)
from forensics.pipeline_capture import STAGE_ORDER, capture_pipeline, new_run_dir

# Maps consecutive stage pairs → engine/stage label for ECS
STAGE_ENGINE = {
    ("01_raw_source_profile", "02_after_uli_envelope"): "ULI",
    ("02_after_uli_envelope", "03_after_sif"): "SIF",
    ("03_after_sif", "04_after_uvie"): "UVIE",
    ("04_after_uvie", "05_after_lce_clg_board"): "LCE_CLG_BOARD",
    ("05_after_lce_clg_board", "06_after_adaptations"): "LCE_ADAPTATIONS",
    ("06_after_adaptations", "07_after_vocabulary"): "VOCABULARY",
    ("07_after_vocabulary", "08_after_diagram_integration"): "DIAGRAMS",
    ("08_after_diagram_integration", "09_after_pqle_polish"): "PQLE",
    ("09_after_pqle_polish", "10_after_pmes"): "PMES",
    ("10_after_pmes", "11_after_peec"): "PEEC_EPP_FIDELITY",
    ("11_after_peec", "12_final_html"): "HTML_RENDER",
}


def load_stage(run_dir: Path, stage_id: str) -> dict[str, Any]:
    path = run_dir / "stages" / f"{stage_id}.json"
    if not path.exists():
        matches = sorted((run_dir / "stages").glob(f"{stage_id}*.json"))
        if not matches:
            return {}
        path = matches[0]
    return json.loads(path.read_text(encoding="utf-8"))


def compare_all_stages(run_dir: Path) -> list[dict[str, Any]]:
    rows = []
    for i in range(len(STAGE_ORDER) - 1):
        a_id, b_id = STAGE_ORDER[i], STAGE_ORDER[i + 1]
        before, after = load_stage(run_dir, a_id), load_stage(run_dir, b_id)
        if not before or not after:
            continue
        cmp = compare_stage_metrics(before, after)
        engine = STAGE_ENGINE.get((a_id, b_id), f"{a_id}->{b_id}")
        rows.append(
            {
                "from": a_id,
                "to": b_id,
                "engine": engine,
                **cmp,
                "before_score": (before.get("metrics") or {}).get("learner_quality_score"),
                "after_score": (after.get("metrics") or {}).get("learner_quality_score"),
            }
        )
    return rows


def educational_contribution_scores(comparisons: list[dict[str, Any]]) -> dict[str, int]:
    """Map quality_delta into -100..+100 Educational Contribution Score."""
    scores: dict[str, int] = {}
    for row in comparisons:
        # Scale: ±20 quality points → ±100 ECS (clamped)
        delta = float(row.get("quality_delta") or 0)
        ecs = int(max(-100, min(100, round(delta * 5))))
        # Penalties for harm signals even if score flat
        if row.get("did_ai_phrasing_increase"):
            ecs -= 10
        if row.get("did_repetition_increase"):
            ecs -= 8
        if (row.get("advisory_delta") or 0) > 0:
            ecs -= 12
        if (row.get("clone_failure_delta") or 0) > 0:
            ecs -= 15
        if (row.get("vocab_score_delta") or 0) < -10:
            ecs -= 10
        if (row.get("diagram_score_delta") or 0) < -10:
            ecs -= 10
        scores[row["engine"]] = int(max(-100, min(100, ecs)))
    return scores


def blame_between(before: dict[str, Any], after: dict[str, Any], *, engine: str) -> list[dict[str, Any]]:
    """List learner-visible modifications with inferred impact."""
    findings: list[dict[str, Any]] = []
    ba = before.get("adaptations") or {}
    aa = after.get("adaptations") or {}
    keys = sorted(set(ba) | set(aa))
    for key in keys:
        if str(key).startswith("_"):
            continue
        b, a = ba.get(key), aa.get(key)
        if b == a:
            continue
        bt, at = _text_blob(b), _text_blob(a)
        if bt == at:
            continue
        sim = structural_similarity(b, a)
        inserted = []
        removed = []
        # Rough phrase diffs
        for phrase in phrase_hits(at, tuple(set(phrase_hits(at, TEACHER_ADVISORY + (
            "notice how",
            "in this lesson",
            "furthermore",
            "delve",
            "as an ai",
            "learning objective",
            "in summary,",
            "quick revision",
            "think about it",
        ))))):
            if phrase not in bt.lower():
                inserted.append(phrase)
        for phrase in phrase_hits(bt, ("example", "real life", "try this", "picture")):
            if phrase not in at.lower() and len(at) + 40 < len(bt):
                removed.append(phrase)
        impact = "neutral"
        if sim < 0.5 and len(at) > len(bt) + 200:
            impact = "expanded"
        if inserted:
            impact = "less_natural" if any(p in inserted for p in ("notice how", "furthermore", "as an ai")) else impact
            if any(p in inserted for p in TEACHER_ADVISORY):
                impact = "teacher_advisory_leaked_into_learner_text"
        if removed:
            impact = "reduced_engagement_or_examples"
        # Vocab thinning
        if key == "vocabulary":
            bw = len((b or {}).get("word_wall") or []) if isinstance(b, dict) else 0
            aw = len((a or {}).get("word_wall") or []) if isinstance(a, dict) else 0
            if aw < bw:
                impact = "vocabulary_cards_reduced"
                removed.append(f"cards {bw}->{aw}")
        findings.append(
            {
                "engine": engine,
                "adaptation": key,
                "similarity_to_prior": sim,
                "chars_before": len(bt),
                "chars_after": len(at),
                "inserted_signals": inserted[:12],
                "removed_signals": removed[:12],
                "result": impact,
                "excerpt_after": at[:280].replace("\n", " "),
            }
        )
    return findings


def build_blame_report(run_dir: Path, comparisons: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blame: list[dict[str, Any]] = []
    for row in comparisons:
        before = load_stage(run_dir, row["from"])
        after = load_stage(run_dir, row["to"])
        blame.extend(blame_between(before, after, engine=row["engine"]))
    return blame


def disable_probe(source_text: str, topic: str, run_root: Path) -> list[dict[str, Any]]:
    """Phase 5 — disable engines one by one and measure quality."""
    probes = [
        set(),
        {"sif"},
        {"uvie"},
        {"pqle"},
        {"pmes"},
        {"peec"},
        {"epp"},
        {"content_fidelity"},
        {"diagrams"},
        {"pqle", "pmes", "peec", "epp", "content_fidelity"},
    ]
    results = []
    baseline_score = None
    for disable in probes:
        label = "full_pipeline" if not disable else "disable:" + "+".join(sorted(disable))
        run_dir = run_root / ("probe_" + re.sub(r"[^a-z0-9+]+", "_", label))
        run_dir.mkdir(parents=True, exist_ok=True)
        out = capture_pipeline(
            source_text=source_text, topic=topic, run_dir=run_dir, disable=disable
        )
        score = (out["manifest"] or {}).get("final_score")
        if baseline_score is None:
            baseline_score = score
        delta = None if score is None or baseline_score is None else round(score - baseline_score, 2)
        results.append(
            {
                "label": label,
                "disable": sorted(disable),
                "final_score": score,
                "delta_vs_full": delta,
                "improves_when_disabled": bool(delta is not None and delta > 1.5 and disable),
                "run_dir": str(run_dir),
            }
        )
    return results


def adaptation_audit(adaptations: dict[str, Any]) -> dict[str, Any]:
    """Phase 6 — score each adaptation independently."""
    focus = ["standard", "ell", "visual", "auditory", "teacher", "parent", "ld", "adhd", "autism"]
    by_id = {}
    for key in focus:
        page = adaptations.get(key)
        if not isinstance(page, dict):
            continue
        metrics = score_lesson_surface({key: page, "vocabulary": adaptations.get("vocabulary") or {}})
        text = _text_blob(page)
        age_ok = not phrase_hits(text, ("undergraduate", "doctoral", "thesis"))
        access = True
        if key in {"ld", "visual"} and not (
            str(page.get("flowchart_svg") or "").startswith("<svg")
            or str(page.get("svg_diagram") or "").startswith("<svg")
        ):
            access = False
        by_id[key] = {
            "educational_quality": metrics.get("learner_quality_score"),
            "teaching_effectiveness_proxy": metrics.get("section_count", 0) * 8
            + (0 if metrics.get("thin_sections") else 20),
            "age_appropriateness": age_ok,
            "accessibility_proxy": access,
            "robotic": metrics.get("robotic_phrases"),
            "advisory_leak": metrics.get("teacher_advisory_in_student_tabs") if key not in {"teacher", "parent"} else [],
        }
    clones = adaptation_scores(adaptations)
    # Distinctiveness: inverse of max similarity to standard
    for key, row in by_id.items():
        if key == "standard":
            row["distinctiveness"] = 100
            continue
        sim = structural_similarity(adaptations.get("standard"), adaptations.get(key))
        row["distinctiveness"] = int(round((1 - sim) * 100))
        row["similarity_to_mainstream"] = sim
    return {"by_adaptation": by_id, "clone_failures": clones.get("clone_failures") or [], "pairwise": clones.get("pairwise_similarity") or {}}


def historical_compare(source_text: str, topic: str, run_dir: Path) -> dict[str, Any]:
    """
    Phase 7 — compare current package to golden lesson + quality-era commit snapshots if available.
    Does not rewrite git history; uses golden_lessons + optional git show of composer markers.
    """
    golden_path = Path("golden_lessons") / "biology_water_cycle.json"
    golden = {}
    if golden_path.exists():
        golden = json.loads(golden_path.read_text(encoding="utf-8"))
    current = load_stage(run_dir, "12_final_html")
    cur_adapt = (current.get("adaptations") or {}).get("standard") or {}
    gold_lesson = golden.get("lesson") or {}
    sim = structural_similarity(gold_lesson, cur_adapt)
    gold_roles = {str(s.get("role") or "") for s in (gold_lesson.get("sections") or []) if isinstance(s, dict)}
    cur_roles = {str(s.get("role") or "") for s in (cur_adapt.get("sections") or []) if isinstance(s, dict)}
    commits = []
    for sha in ("3652657", "4f6bf7e", "a7acdcd", "4ed2d3e"):
        try:
            msg = subprocess.check_output(
                ["git", "log", "-1", "--format=%s", sha], text=True, stderr=subprocess.DEVNULL
            ).strip()
            commits.append({"sha": sha, "subject": msg, "reachable": True})
        except Exception:
            commits.append({"sha": sha, "reachable": False})
    return {
        "golden_id": golden.get("id"),
        "similarity_to_golden_standard": sim,
        "golden_roles_missing_now": sorted(gold_roles - cur_roles),
        "current_roles_extra": sorted(cur_roles - gold_roles),
        "golden_section_count": len(gold_lesson.get("sections") or []),
        "current_section_count": len(cur_adapt.get("sections") or []),
        "quality_era_commits": commits,
        "note": (
            "Full byte-identical regen on historical commits requires checking out those trees; "
            "this sprint records golden structural drift and quality-era commit anchors for Phase-fix checkout."
        ),
    }


def write_forensic_report(run_dir: Path, bundle: dict[str, Any]) -> Path:
    comparisons = bundle["comparisons"]
    ecs = bundle["ecs"]
    blame = bundle["blame"]
    probes = bundle["disable_probes"]
    adapt = bundle["adaptation_audit"]
    hist = bundle["historical"]
    manifest = bundle["manifest"]

    lines = [
        "# ALORA AI — Lesson Quality Recovery Forensic Report",
        "",
        f"Run directory: `{run_dir}`",
        f"Topic: **{manifest.get('topic')}**",
        f"Final learner-quality score: **{manifest.get('final_score')}** / 100",
        "",
        "This report is evidence-only. No production engines were rewritten.",
        "",
        "## 1. Stage scores (learner-facing)",
        "",
        "| Stage | Score |",
        "|---|---:|",
    ]
    for row in manifest.get("stages") or []:
        lines.append(f"| `{row.get('stage_id')}` | {row.get('learner_quality_score')} |")

    lines += ["", "## 2. Stage-to-stage comparison", ""]
    for row in comparisons:
        lines += [
            f"### {row['engine']} (`{row['from']}` → `{row['to']}`)",
            "",
            f"- Quality delta: **{row['quality_delta']}** (before {row['before_score']} → after {row['after_score']})",
            f"- Did quality improve? **{row['did_quality_improve']}**",
            f"- Did quality worsen? **{row['did_quality_worsen']}**",
            f"- Robotic phrasing delta: {row['robotic_delta']}",
            f"- Teacher-advisory leak delta (student tabs): {row['advisory_delta']}",
            f"- Repetition increased? {row['did_repetition_increase']}",
            f"- AI phrasing increased? {row['did_ai_phrasing_increase']}",
            f"- Vocab score delta: {row['vocab_score_delta']}",
            f"- Diagram score delta: {row['diagram_score_delta']}",
            f"- Clone-failure delta: {row['clone_failure_delta']}",
            "",
        ]

    lines += ["## 3. Educational Contribution Score (−100…+100)", "", "| Engine / stage | ECS |", "|---|---:|"]
    for name, score in sorted(ecs.items(), key=lambda kv: kv[1]):
        lines.append(f"| {name} | **{score}** |")

    harmful = [k for k, v in ecs.items() if v <= -10]
    helpful = [k for k, v in ecs.items() if v >= 10]
    null = [k for k, v in ecs.items() if -9 <= v <= 9]
    lines += [
        "",
        f"- Improves lessons: {', '.join(helpful) or 'none above +10'}",
        f"- Damages lessons: {', '.join(harmful) or 'none below −10'}",
        f"- Near-zero contribution: {', '.join(null) or 'none'}",
        "",
        "## 4. Blame report (learner-visible modifications)",
        "",
    ]
    if not blame:
        lines.append("_No textual diffs detected between stages._")
    for item in blame[:80]:
        lines += [
            f"- **{item['engine']}** / `{item['adaptation']}` → {item['result']}",
            f"  - similarity={item['similarity_to_prior']}, chars {item['chars_before']}→{item['chars_after']}",
            f"  - inserted: {item['inserted_signals'] or '—'}",
            f"  - removed: {item['removed_signals'] or '—'}",
            f"  - excerpt: {item['excerpt_after'][:200]}",
            "",
        ]

    lines += ["## 5. Disable probes (identical source)", "", "| Probe | Score | Δ vs full | Flag |", "|---|---:|---:|---|"]
    for p in probes:
        flag = "HARMFUL_WHEN_ENABLED" if p.get("improves_when_disabled") else ""
        lines.append(
            f"| `{p['label']}` | {p['final_score']} | {p['delta_vs_full']} | {flag} |"
        )

    lines += ["", "## 6. Adaptation audit", ""]
    for key, row in (adapt.get("by_adaptation") or {}).items():
        lines.append(
            f"- **{key}**: quality={row.get('educational_quality')}, "
            f"distinctiveness={row.get('distinctiveness')}, "
            f"sim_to_mainstream={row.get('similarity_to_mainstream')}, "
            f"access={row.get('accessibility_proxy')}, "
            f"advisory_leak={row.get('advisory_leak')}"
        )
    clones = adapt.get("clone_failures") or []
    lines += ["", f"Clone failures (≥60% identical): **{len(clones)}**"]
    for c in clones:
        lines.append(f"- {c}")

    lines += [
        "",
        "## 7. Historical / golden drift",
        "",
        dumps(hist),
        "",
        "## 8. Verdict — what to rewrite / remove / formatting-only",
        "",
    ]
    rewrite = [k for k, v in ecs.items() if v <= -15]
    remove_or_gate = [p["label"] for p in probes if p.get("improves_when_disabled")]
    formatting_only = [k for k in ("HTML_RENDER", "UVIE", "SIF") if ecs.get(k, 0) <= 5]
    lines += [
        f"1. Engines that improve lessons: {helpful}",
        f"2. Engines that damage lessons: {harmful}",
        f"3. Engines that contribute little: {null}",
        f"4. Stages that should be rewritten (ECS ≤ −15): {rewrite}",
        f"5. Stages that should be removed or hard-gated (disable improved quality): {remove_or_gate}",
        f"6. Stages that should become formatting-only candidates: {formatting_only}",
        "",
        "Do not treat metadata/PQI/PMES approval flags as quality. Scores above are learner-surface only.",
        "",
    ]
    path = run_dir / "FORENSIC_REPORT.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    (run_dir / "forensic_bundle.json").write_text(dumps(bundle), encoding="utf-8")
    return path
