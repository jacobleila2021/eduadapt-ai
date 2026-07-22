"""Timeline scaffold provider — lesson chronology only; never invents events."""

from __future__ import annotations

import html
import re
from typing import Any

from engines.universal_visual_intelligence.schemas import VisualIntent, VisualSpec

_YEAR = re.compile(r"\b(1[0-9]{3}|20[0-9]{2})\b")
_EVENTISH = re.compile(
    r"(?P<year>1[0-9]{3}|20[0-9]{2})\s*[-–:]\s*(?P<label>[^\n.]{3,80})",
    re.IGNORECASE,
)


def _extract_events(text: str, max_events: int = 8) -> list[dict[str, str]]:
    events: list[dict[str, str]] = []
    seen: set[str] = set()
    for m in _EVENTISH.finditer(text or ""):
        year = m.group("year")
        label = re.sub(r"\s+", " ", m.group("label")).strip(" -–:")
        key = f"{year}:{label.lower()}"
        if key in seen:
            continue
        seen.add(key)
        events.append({"year": year, "label": label[:60]})
        if len(events) >= max_events:
            return events
    for m in _YEAR.finditer(text or ""):
        year = m.group(1)
        start = max(0, m.start() - 40)
        end = min(len(text or ""), m.end() + 40)
        snippet = re.sub(r"\s+", " ", (text or "")[start:end]).strip()
        key = f"{year}:{snippet.lower()[:30]}"
        if key in seen:
            continue
        seen.add(key)
        events.append({"year": year, "label": snippet[:60] or year})
        if len(events) >= max_events:
            break
    return events


def _timeline_svg(events: list[dict[str, str]], title: str) -> str:
    width = 720
    height = 120 + max(len(events), 1) * 36
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">',
        f"<title>{html.escape(title)}</title>",
        f'<text x="24" y="32" font-family="Lexend, Arial, sans-serif" font-size="18" fill="#0B2E59">'
        f"{html.escape(title)}</text>",
        f'<line x1="40" y1="60" x2="40" y2="{height - 24}" stroke="#008C95" stroke-width="4"/>',
    ]
    for i, ev in enumerate(events):
        y = 72 + i * 36
        lines.append(f'<circle cx="40" cy="{y}" r="7" fill="#0B2E59"/>')
        lines.append(
            f'<text x="60" y="{y + 5}" font-family="Lexend, Arial, sans-serif" font-size="14" fill="#0B2E59">'
            f'{html.escape(ev["year"])}: {html.escape(ev["label"])}</text>'
        )
    lines.append("</svg>")
    return "\n".join(lines)


def provide_timeline_visuals(
    intents: list[VisualIntent],
    *,
    text: str = "",
    context: dict[str, Any] | None = None,
) -> list[VisualSpec]:
    ctx = dict(context or {})
    want = any(i.family == "timeline" or "timeline" in i.visual_type for i in intents)
    blob = (text or "").lower()
    if not want and "timeline" not in blob and not _YEAR.search(text or ""):
        meta = ctx.get("sif_visuals") or []
        want = any("timeline" in str(v.get("visual_type") or "").lower() for v in meta if isinstance(v, dict))
    if not want and "timeline" not in blob:
        return []

    events = _extract_events(text)
    if not events:
        return []

    title = str(ctx.get("topic") or "Lesson timeline")
    try:
        from svg_sanitizer import sanitize_svg

        svg = sanitize_svg(_timeline_svg(events, title)) or _timeline_svg(events, title)
    except Exception:  # noqa: BLE001
        svg = _timeline_svg(events, title)

    return [
        VisualSpec(
            visual_id="timeline:lesson",
            visual_type="interactive_timeline",
            source="timeline_scaffold",
            provenance="universal_visual_intelligence.providers.timeline",
            caption=title,
            alt_text="Timeline of dated events extracted from the verified lesson text.",
            svg=svg,
            invents_curriculum=False,
            deterministic=True,
            engine_id="uvie_timeline",
            task_kind="timeline_scaffold",
            metadata={"event_count": len(events), "invents_events": False},
        )
    ]
