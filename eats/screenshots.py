"""EATS screenshot / visual capture — HTML snapshots + optional Playwright PNGs."""

from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_ROOT = ROOT / "reports" / "screenshots"

VIEWPORTS = {
    "desktop": {"width": 1280, "height": 800},
    "tablet": {"width": 768, "height": 1024},
    "mobile": {"width": 390, "height": 844},
}


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def adaptation_html(adaptation_id: str, content: Mapping[str, Any]) -> str:
    """Self-contained HTML page for visual acceptance (no Streamlit required)."""
    title = html.escape(str(content.get("title") or content.get("topic") or adaptation_id))
    big = html.escape(str(content.get("big_idea") or ""))
    sections_html: list[str] = []
    for sec in content.get("sections") or []:
        if not isinstance(sec, dict):
            continue
        st = html.escape(str(sec.get("title") or ""))
        body = html.escape(str(sec.get("body") or "")).replace("\n", "<br>")
        role = html.escape(str(sec.get("role") or ""))
        sections_html.append(
            f'<section class="card" data-role="{role}"><h2>{st}</h2><p>{body}</p></section>'
        )

    vocab_html = ""
    words = content.get("words") or content.get("cards") or []
    if words:
        cards = []
        for w in words:
            if not isinstance(w, dict):
                continue
            term = html.escape(str(w.get("term") or w.get("word") or ""))
            definition = html.escape(
                str(w.get("student_friendly_definition") or w.get("definition") or "")
            )
            cards.append(
                f'<article class="vocab-card"><h3 class="term">{term}</h3>'
                f'<p class="def">{definition}</p></article>'
            )
        vocab_html = '<div class="vocab-grid">' + "".join(cards) + "</div>"

    svgs = []
    for key in ("flowchart_svg", "concept_map_svg", "svg_diagram"):
        raw = str(content.get(key) or "")
        if raw.strip().startswith("<svg"):
            svgs.append(f'<div class="diagram">{raw}</div>')

    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — {html.escape(adaptation_id)}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Literata:opsz,wght@7..72,500;7..72,700&family=Source+Sans+3:wght@400;600&display=swap');
  :root {{ --ink:#0B2E59; --teal:#008C95; --paper:#f7fafb; --card:#ffffff; }}
  body {{ margin:0; font-family:'Source Sans 3',Segoe UI,sans-serif; color:var(--ink);
         background:linear-gradient(180deg,#eef6f7 0%, var(--paper) 40%); }}
  main {{ max-width:880px; margin:0 auto; padding:2rem 1.25rem 3rem; }}
  .eyebrow {{ text-transform:uppercase; letter-spacing:.08em; color:var(--teal); font-size:.75rem; }}
  h1 {{ font-family:Literata,Georgia,serif; font-size:2rem; margin:.35rem 0 1rem; }}
  .big-idea {{ background:#e6f7f8; border-left:5px solid var(--teal); padding:1rem 1.2rem;
               border-radius:12px; font-size:1.05rem; margin-bottom:1.5rem; }}
  .card {{ background:var(--card); border-radius:14px; padding:1.1rem 1.25rem; margin:1rem 0;
           box-shadow:0 8px 24px rgba(11,46,89,.06); }}
  .card h2 {{ font-family:Literata,Georgia,serif; font-size:1.2rem; margin:0 0 .5rem; }}
  .vocab-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:1rem; }}
  .vocab-card {{ background:var(--card); border-radius:16px; padding:1.25rem; text-align:center;
                 box-shadow:0 8px 24px rgba(11,46,89,.07); }}
  .term {{ font-family:Literata,Georgia,serif; font-size:1.6rem; margin:0 0 .5rem; color:var(--teal); }}
  .diagram {{ margin:1.25rem 0; overflow:auto; background:#fff; border-radius:12px; padding:1rem; }}
  .diagram svg {{ max-width:100%; height:auto; }}
</style></head><body>
<main>
  <div class="eyebrow">{html.escape(adaptation_id)} adaptation</div>
  <h1>{title}</h1>
  {f'<div class="big-idea">{big}</div>' if big else ''}
  {''.join(svgs)}
  {vocab_html}
  {''.join(sections_html)}
</main></body></html>"""


def capture_adaptation_snapshots(
    adaptations: Mapping[str, Any],
    *,
    run_id: str = "",
    keys: list[str] | None = None,
    try_png: bool = False,
) -> dict[str, Any]:
    """Write HTML (always) and PNG screenshots (when Playwright works).

    Default try_png=False for fast CI; enable for full visual acceptance runs.
    """
    run_id = run_id or _stamp()
    out_dir = SCREENSHOT_ROOT / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    keys = keys or [k for k in adaptations.keys() if not str(k).startswith("_")]
    manifest: dict[str, Any] = {"run_id": run_id, "pages": [], "mosaic": None}

    for key in keys:
        content = adaptations.get(key)
        if not isinstance(content, dict):
            continue
        page = adaptation_html(key, content)
        html_path = out_dir / f"{key}.html"
        html_path.write_text(page, encoding="utf-8")
        entry: dict[str, Any] = {"adaptation": key, "html": str(html_path), "png": {}}
        if try_png:
            entry["png"] = _maybe_png(html_path, out_dir, key)
        manifest["pages"].append(entry)

    mosaic = _write_mosaic_index(out_dir, manifest)
    manifest["mosaic"] = str(mosaic) if mosaic else None
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return {"dir": str(out_dir), "manifest": manifest}


def _maybe_png(html_path: Path, out_dir: Path, key: str) -> dict[str, str]:
    paths: dict[str, str] = {}
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return paths

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for name, vp in VIEWPORTS.items():
                page = browser.new_page(viewport=vp)
                page.goto(html_path.resolve().as_uri(), wait_until="load", timeout=15000)
                png_path = out_dir / f"{key}_{name}.png"
                page.screenshot(path=str(png_path), full_page=True)
                paths[name] = str(png_path)
                page.close()
            browser.close()
    except Exception:
        return paths
    return paths


def _write_mosaic_index(out_dir: Path, manifest: Mapping[str, Any]) -> Path:
    cards = []
    for page in manifest.get("pages") or []:
        aid = html.escape(str(page.get("adaptation") or ""))
        href = html.escape(Path(str(page.get("html") or "")).name)
        pngs = page.get("png") or {}
        img = ""
        if pngs.get("desktop"):
            img = f'<img src="{html.escape(Path(pngs["desktop"]).name)}" alt="{aid} desktop">'
        cards.append(
            f'<a class="tile" href="{href}"><div class="label">{aid}</div>'
            f'{img or "<div class=placeholder>HTML snapshot</div>"}</a>'
        )
    mosaic = out_dir / "comparison_mosaic.html"
    mosaic.write_text(
        f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>EATS Mosaic</title>
<style>
body{{font-family:Segoe UI,sans-serif;background:#0B2E59;color:#fff;padding:1.5rem}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:1rem}}
.tile{{background:#fff;color:#0B2E59;border-radius:12px;padding:.75rem;text-decoration:none}}
.tile img{{width:100%;height:auto;border-radius:8px}}
.label{{font-weight:700;margin-bottom:.5rem}}
.placeholder{{padding:2rem;background:#eef6f7;border-radius:8px;text-align:center}}
</style></head><body>
<h1>Educational Acceptance — Comparison Mosaic</h1>
<div class="grid">{''.join(cards)}</div>
</body></html>""",
        encoding="utf-8",
    )
    return mosaic
