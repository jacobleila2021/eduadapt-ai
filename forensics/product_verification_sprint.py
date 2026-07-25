"""Final product verification sprint — learner-facing readiness.

Uses existing compose, defect classification, HTML export, EATS snapshots,
PEEC/POBR audits, and PDF export. Does not add engines, validators, or scorers.

Run: python -m forensics.product_verification_sprint
"""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _select_specs() -> list[dict[str, Any]]:
    """Multi-subject, multi-curriculum verification corpus."""
    from uevb.corpus import iter_corpus_specs

    # CBSE + Cambridge × up to 4 topics so environmental biology seeds are reachable
    specs = iter_corpus_specs(
        curricula=("cbse", "cambridge", "ib"),
        max_topics_per_subject=4,
    )
    by_subject: dict[str, list[dict[str, Any]]] = {}
    for spec in specs:
        by_subject.setdefault(spec["subject"], []).append(spec)
    selected: list[dict[str, Any]] = []
    for subject, rows in by_subject.items():
        first = next((r for r in rows if r["curriculum"] == "cbse"), rows[0])
        selected.append(first)
        second = next(
            (r for r in rows if r["curriculum"] == "cambridge" and r["topic"] != first["topic"]),
            next((r for r in rows if r is not first), None),
        )
        if second:
            selected.append(second)
    # Explicit environmental-science classroom coverage (biology pack — no new engine)
    env = [
        s
        for s in specs
        if s["subject"] == "biology"
        and s["topic"] in {"Waste Management", "Ecosystems"}
        and s["curriculum"] in {"cbse", "cambridge"}
    ]
    seen = {(s["subject"], s["topic"], s["curriculum"]) for s in selected}
    for row in env:
        key = (row["subject"], row["topic"], row["curriculum"])
        if key not in seen:
            selected.append(row)
            seen.add(key)
    return selected


def _render_product_surfaces(
    adaptations: dict[str, Any],
    *,
    lesson_dir: Path,
    topic: str,
) -> dict[str, Any]:
    """Write learner-facing HTML / print / markdown exports for every adaptation."""
    from eats.screenshots import adaptation_html, capture_adaptation_snapshots
    from html_exporter import export_tab_html
    from pdf_exporter import export_tab_pdf

    html_dir = lesson_dir / "html"
    export_dir = lesson_dir / "exports"
    html_dir.mkdir(parents=True, exist_ok=True)
    export_dir.mkdir(parents=True, exist_ok=True)

    snap = capture_adaptation_snapshots(
        adaptations,
        run_id=lesson_dir.name,
        try_png=False,
    )
    # Mirror EATS pages into lesson folder for the product dossier
    surfaces: dict[str, Any] = {"eats_dir": snap.get("dir"), "pages": [], "pdf_ok": {}, "print_html": {}}

    for key, page in adaptations.items():
        if str(key).startswith("_") or not isinstance(page, dict):
            continue
        eats_page = adaptation_html(key, page)
        (html_dir / f"{key}.html").write_text(eats_page, encoding="utf-8")
        try:
            print_html = export_tab_html(f"{topic} — {key}", page, key)
            (export_dir / f"{key}_print.html").write_text(print_html, encoding="utf-8")
            surfaces["print_html"][key] = str(export_dir / f"{key}_print.html")
        except Exception as exc:  # noqa: BLE001
            surfaces["print_html"][key] = f"ERROR:{exc}"
        try:
            pdf = export_tab_pdf(topic, page, key)
            pdf_path = export_dir / f"{key}.pdf"
            if isinstance(pdf, (bytes, bytearray)) and pdf.startswith(b"%PDF"):
                pdf_path.write_bytes(pdf)
                surfaces["pdf_ok"][key] = True
            else:
                surfaces["pdf_ok"][key] = False
        except Exception:  # noqa: BLE001
            surfaces["pdf_ok"][key] = False
        surfaces["pages"].append({"adaptation": key, "html": str(html_dir / f"{key}.html")})
    return surfaces


def _audit_rendered_html(html_path: Path) -> list[dict[str, str]]:
    """Product-defect scan of rendered HTML — pattern detection only, no new scorer."""
    defects: list[dict[str, str]] = []
    text = html_path.read_text(encoding="utf-8", errors="ignore")
    low = text.lower()
    code = html_path.stem

    def add(kind: str, detail: str, remediation: str) -> None:
        defects.append(
            {
                "adaptation": code,
                "code": kind,
                "detail": detail,
                "html": str(html_path),
                "remediation": remediation,
                "root_cause": "rendered_product",
            }
        )

    if "notice how" in low or "students will" in low or "memory tip" in low:
        add("scaffold_leak", "Authoring scaffold visible in rendered page.", "Rewrite learner prose; strip scaffolds.")
    if re.search(r"<svg[^>]*>\s*</svg>", text, flags=re.I):
        add("broken_diagram", "Empty SVG in rendered page.", "Ensure UVIE/flowchart SVG is non-empty before render.")
    if "pronunciation" in low and ("ipa" in low or "part of speech" in low or "noun" == low.strip()):
        add("grammar_label_leak", "Grammar/pronunciation labels interrupt vocabulary.", "Keep Meaning / Example / Remember / Use / Picture only.")
    # Empty cards
    if 'class="vocab-card"' in text and "<h3 class=\"term\"></h3>" in text:
        add("empty_vocab_card", "Vocabulary card missing term.", "Filter empty word-wall rows before render.")
    if "big-idea" in low and re.search(r'class="big-idea">\s*</div>', text):
        add("empty_big_idea", "Big idea block is empty.", "Compose a claim-grounded big idea.")
    # Cream / brand tokens for print exports
    if html_path.name.endswith("_print.html") or "ld-friendly" in low:
        if "#fff9ee" not in low and "fff9ee" not in low:
            add("colour_regression", "Print page missing cream #FFF9EE background.", "Restore cream textbook background in html_exporter.")
    # Duplicate consecutive paragraphs
    paras = re.findall(r"<p[^>]*>(.*?)</p>", text, flags=re.I | re.S)
    cleaned = [" ".join(re.sub(r"<[^>]+>", "", p).lower().split()) for p in paras]
    cleaned = [p for p in cleaned if len(p) > 40]
    for i in range(1, len(cleaned)):
        if cleaned[i] == cleaned[i - 1]:
            add("duplicate_paragraph", "Adjacent duplicate paragraphs in render.", "Dedupe section bodies before export.")
            break
    return defects


def _adaptation_uniqueness(adaptations: dict[str, Any]) -> dict[str, Any]:
    """Confirm each adaptation earns its place (existing instructional_text + overlap)."""
    from engines.lesson_composition_engine.recovery import instructional_text

    std = adaptations.get("standard") if isinstance(adaptations.get("standard"), dict) else {}
    std_text = instructional_text(std).lower()
    std_tokens = set(re.findall(r"[a-z]{4,}", std_text))
    rows: dict[str, Any] = {}
    for key, page in adaptations.items():
        if str(key).startswith("_") or not isinstance(page, dict):
            continue
        if key == "vocabulary":
            wall = page.get("word_wall") or []
            rows[key] = {
                "cards": len(wall),
                "justified": len(wall) >= 4,
                "reason": "Word Wall teaches terms with Meaning / Example / Remember / Use / Picture.",
            }
            continue
        if key == "worksheet":
            dq = page.get("diagram_question") if isinstance(page.get("diagram_question"), dict) else {}
            has_svg = str(dq.get("svg_diagram") or page.get("svg_diagram") or "").startswith("<svg")
            rows[key] = {
                "justified": has_svg or bool(page.get("questions") or page.get("items")),
                "reason": "Practice worksheet with diagram/questions, not a clone of the lesson.",
            }
            continue
        text = instructional_text(page).lower()
        tokens = set(re.findall(r"[a-z]{4,}", text))
        if not std_tokens or key == "standard":
            overlap = 0.0 if key == "standard" else 1.0
        else:
            overlap = len(tokens & std_tokens) / max(len(tokens | std_tokens), 1)
        distinct = round(100.0 * (1.0 - overlap), 1)
        roles = [str(s.get("role") or "") for s in (page.get("sections") or []) if isinstance(s, dict)]
        rows[key] = {
            "distinctiveness": distinct if key != "standard" else 100.0,
            "justified": key == "standard" or distinct >= 25.0 or roles[:1] != [
                str(s.get("role") or "") for s in (std.get("sections") or [])[:1] if isinstance(s, dict)
            ],
            "opening_role": roles[0] if roles else "",
            "section_count": len(roles),
            "reason": {
                "standard": "Mainstream classroom arc.",
                "visual": "Diagram-first teaching path.",
                "auditory": "Speak-aloud / listen-first path.",
                "ell": "Key-word and sentence-frame path.",
                "adhd": "Short mission chunks.",
                "autism": "Predictable routine steps.",
                "dyslexia": "Calm short-line reading.",
                "ld": "One-step-at-a-time scaffolding.",
                "teacher": "Lesson intent and exit checks.",
                "parent": "Home conversation prompts.",
            }.get(key, "Profile-specific teaching strategy."),
        }
    return rows


def _audio_surface_check(adaptations: dict[str, Any]) -> dict[str, Any]:
    """Verify narration text exists (neural TTS may be offline — text must still be speakable)."""
    from audio_learning import build_narration

    out: dict[str, Any] = {}
    for key, page in adaptations.items():
        if str(key).startswith("_") or not isinstance(page, dict):
            continue
        try:
            narr = build_narration(page, key)
            words = len(str(narr or "").split())
            out[key] = {
                "ok": words >= 40,
                "words": words,
                "preview": str(narr or "")[:160],
            }
        except Exception as exc:  # noqa: BLE001
            out[key] = {"ok": False, "words": 0, "error": str(exc)[:200]}
    return out


def run_sprint(*, limit: int | None = None) -> Path:
    from release.campaign import _compose
    from release.defects import classify_package_defects

    selected = _select_specs()
    if limit:
        selected = selected[: max(1, limit)]

    stamp = _stamp()
    out = ROOT / "forensics" / "runs" / f"product_verification_{stamp}"
    out.mkdir(parents=True, exist_ok=True)
    lessons_dir = out / "lessons"
    lessons_dir.mkdir(exist_ok=True)

    report: dict[str, Any] = {
        "schema": "alora.product_verification.v1",
        "generated_at": stamp,
        "mission": "classroom_readiness_rendered_product",
        "count": len(selected),
        "lessons": [],
        "defect_cards": [],
        "summary": {},
    }

    for spec in selected:
        t0 = time.perf_counter()
        pkg = _compose(spec)
        adaptations = pkg.get("adaptations") if isinstance(pkg.get("adaptations"), dict) else {}
        topic = str(
            (pkg.get("intelligence_board") or {}).get("topic")
            or spec.get("topic")
            or "Lesson"
        )
        lesson_id = f"{spec['subject']}__{spec['topic']}__{spec['curriculum']}".replace(" ", "_")
        lesson_dir = lessons_dir / lesson_id
        lesson_dir.mkdir(parents=True, exist_ok=True)

        defects = classify_package_defects(pkg, corpus_id=spec.get("corpus_id") or lesson_id)
        surfaces = _render_product_surfaces(adaptations, lesson_dir=lesson_dir, topic=topic)
        uniqueness = _adaptation_uniqueness(adaptations)
        audio = _audio_surface_check(adaptations)

        render_defects: list[dict[str, str]] = []
        for page in surfaces.get("pages") or []:
            html_path = Path(page["html"])
            if html_path.exists():
                render_defects.extend(_audit_rendered_html(html_path))
            print_path = surfaces.get("print_html", {}).get(page["adaptation"])
            if print_path and not str(print_path).startswith("ERROR"):
                render_defects.extend(_audit_rendered_html(Path(print_path)))

        heq = pkg.get("heq") or pkg.get("eqs") or {}
        publish = bool(pkg.get("ok")) and float(heq.get("overall") or 0) >= 95.0
        unjustified = [k for k, v in uniqueness.items() if not v.get("justified")]
        audio_fail = [k for k, v in audio.items() if not v.get("ok")]
        pdf_fail = [k for k, ok in (surfaces.get("pdf_ok") or {}).items() if not ok]

        if unjustified:
            defects.append(
                {
                    "severity": "high",
                    "code": "cosmetic_adaptation",
                    "detail": f"Adaptations not educationally unique: {', '.join(unjustified)}",
                    "topic": topic,
                    "corpus_id": lesson_id,
                    "auto_fixable": False,
                }
            )
        if audio_fail:
            defects.append(
                {
                    "severity": "high",
                    "code": "missing_audio_text",
                    "detail": f"Narration text too thin for: {', '.join(audio_fail)}",
                    "topic": topic,
                    "corpus_id": lesson_id,
                    "auto_fixable": True,
                }
            )
        if pdf_fail:
            defects.append(
                {
                    "severity": "critical",
                    "code": "broken_pdf_export",
                    "detail": f"PDF export failed for: {', '.join(pdf_fail[:4])}",
                    "topic": topic,
                    "corpus_id": lesson_id,
                    "auto_fixable": False,
                }
            )

        for rd in render_defects:
            card = {
                **rd,
                "topic": topic,
                "subject": spec["subject"],
                "curriculum": spec["curriculum"],
                "screenshot": rd.get("html"),
                "before": rd.get("detail"),
                "after": rd.get("remediation"),
            }
            report["defect_cards"].append(card)

        row = {
            "id": lesson_id,
            "subject": spec["subject"],
            "topic": topic,
            "curriculum": spec["curriculum"],
            "elapsed_s": round(time.perf_counter() - t0, 2),
            "ok": bool(pkg.get("ok")),
            "heq": heq.get("overall"),
            "classroom_ready": bool((heq.get("human_verdict") or {}).get("classroom_ready")),
            "publish": publish and not unjustified and not pdf_fail and not [
                d for d in defects if d.get("severity") in {"critical", "high"}
            ],
            "adaptation_keys": [k for k in adaptations if not str(k).startswith("_")],
            "adaptation_uniqueness": uniqueness,
            "audio": audio,
            "pdf_ok_count": sum(1 for ok in (surfaces.get("pdf_ok") or {}).values() if ok),
            "defects": defects,
            "render_defects": render_defects,
            "surfaces": {
                "html_dir": str(lesson_dir / "html"),
                "exports_dir": str(lesson_dir / "exports"),
                "eats_dir": surfaces.get("eats_dir"),
            },
        }
        report["lessons"].append(row)
        (lesson_dir / "LESSON_REPORT.json").write_text(json.dumps(row, indent=2), encoding="utf-8")
        print(
            f"[product] {spec['subject']}/{topic}/{spec['curriculum']} "
            f"HEQ={heq.get('overall')} publish={row['publish']} "
            f"defects={len(defects)+len(render_defects)} ({row['elapsed_s']}s)"
        )

    lessons = report["lessons"]
    report["summary"] = {
        "lessons": len(lessons),
        "publishable": sum(1 for r in lessons if r["publish"]),
        "classroom_ready": sum(1 for r in lessons if r["classroom_ready"]),
        "heq_ge_95": sum(1 for r in lessons if (r.get("heq") or 0) >= 95),
        "subjects": sorted({r["subject"] for r in lessons}),
        "curricula": sorted({r["curriculum"] for r in lessons}),
        "critical_defects": sum(
            1
            for r in lessons
            for d in r.get("defects") or []
            if d.get("severity") == "critical"
        ),
        "high_defects": sum(
            1
            for r in lessons
            for d in r.get("defects") or []
            if d.get("severity") == "high"
        ),
        "render_defects": len(report["defect_cards"]),
        "classroom_product_ready": (
            len(lessons) > 0
            and all(r["publish"] for r in lessons)
            and all(r["classroom_ready"] for r in lessons)
        ),
    }

    (out / "PRODUCT_VERIFICATION.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    _write_markdown(out, report)
    return out


def _write_markdown(out: Path, report: dict[str, Any]) -> None:
    s = report["summary"]
    lines = [
        "# Alora AI — Final Product Verification",
        "",
        f"Generated: {report['generated_at']}",
        f"Lessons: {s['lessons']}",
        f"Publishable: {s['publishable']}/{s['lessons']}",
        f"Classroom ready: {s['classroom_ready']}/{s['lessons']}",
        f"HEQ ≥ 95: {s['heq_ge_95']}/{s['lessons']}",
        f"Subjects: {', '.join(s['subjects'])}",
        f"Curricula: {', '.join(s['curricula'])}",
        f"Critical defects: {s['critical_defects']} | High: {s['high_defects']} | Render: {s['render_defects']}",
        f"Classroom product ready: {s['classroom_product_ready']}",
        "",
        "## Lessons",
        "",
        "| Subject | Topic | Curriculum | HEQ | Publish | Defects |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in report["lessons"]:
        n = len(r.get("defects") or []) + len(r.get("render_defects") or [])
        lines.append(
            f"| {r['subject']} | {r['topic']} | {r['curriculum']} | {r.get('heq')} | {r['publish']} | {n} |"
        )
    lines += ["", "## Defect cards", ""]
    if not report["defect_cards"]:
        lines.append("None.")
    for card in report["defect_cards"][:40]:
        lines += [
            f"### {card.get('code')} — {card.get('topic')} / {card.get('adaptation')}",
            f"- Detail: {card.get('detail')}",
            f"- Screenshot/HTML: `{card.get('screenshot')}`",
            f"- Root cause: {card.get('root_cause')}",
            f"- Remediation: {card.get('remediation')}",
            "",
        ]
    (out / "PRODUCT_VERIFICATION.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    import sys

    limit = None
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        limit = int(sys.argv[1])
    path = run_sprint(limit=limit)
    report = json.loads((path / "PRODUCT_VERIFICATION.json").read_text(encoding="utf-8"))
    print(json.dumps({"out": str(path), "summary": report["summary"]}, indent=2))
    raise SystemExit(0 if report["summary"].get("classroom_product_ready") else 1)


if __name__ == "__main__":
    main()
