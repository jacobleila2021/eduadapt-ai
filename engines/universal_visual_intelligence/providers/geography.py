"""Geography map scaffold provider — labels from lesson only; no invented geodata."""

from __future__ import annotations

import html
import re
from typing import Any

from engines.universal_visual_intelligence.schemas import VisualIntent, VisualSpec

_PLACE = re.compile(
    r"\b(India|Asia|Europe|Africa|America|Pacific|Atlantic|Himalaya|Ganga|Nile|"
    r"Amazon|Sahara|Deccan|Indo-Gangetic|British India|Delhi|Mumbai|Chennai|"
    r"Kolkata|latitude|longitude|equator|tropic)\b",
    re.IGNORECASE,
)


def _extract_places(text: str, max_places: int = 10) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    for m in _PLACE.finditer(text or ""):
        place = m.group(0)
        key = place.lower()
        if key in seen:
            continue
        seen.add(key)
        found.append(place)
        if len(found) >= max_places:
            break
    return found


def _map_scaffold_svg(places: list[str], title: str) -> str:
    width = 640
    height = 160 + max(len(places), 1) * 28
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">',
        f"<title>{html.escape(title)}</title>",
        f'<rect x="12" y="12" width="{width - 24}" height="{height - 24}" rx="12" '
        f'fill="#e6f7f8" stroke="#008C95" stroke-width="2"/>',
        f'<text x="28" y="44" font-family="Lexend, Arial, sans-serif" font-size="18" fill="#0B2E59">'
        f"{html.escape(title)}</text>",
        '<text x="28" y="68" font-family="Lexend, Arial, sans-serif" font-size="12" fill="#475569">'
        "Map scaffold — places named in the verified lesson (no invented borders)</text>",
    ]
    for i, place in enumerate(places):
        y = 100 + i * 28
        lines.append(f'<circle cx="40" cy="{y - 4}" r="6" fill="#0B2E59"/>')
        lines.append(
            f'<text x="56" y="{y}" font-family="Lexend, Arial, sans-serif" font-size="14" fill="#0B2E59">'
            f"{html.escape(place)}</text>"
        )
    lines.append("</svg>")
    return "\n".join(lines)


def provide_geography_visuals(
    intents: list[VisualIntent],
    *,
    text: str = "",
    context: dict[str, Any] | None = None,
) -> list[VisualSpec]:
    ctx = dict(context or {})
    want = any(i.family == "geography" or "map" in i.visual_type for i in intents)
    blob = (text or "").lower()
    if not want:
        meta = ctx.get("sif_visuals") or []
        want = any(
            any(k in str(v.get("visual_type") or "").lower() for k in ("map", "geography", "overlay"))
            for v in meta
            if isinstance(v, dict)
        )
    if not want and not any(k in blob for k in ("map", "geography", "latitude", "longitude")):
        return []

    places = _extract_places(text)
    if not places:
        return []

    title = str(ctx.get("topic") or "Geography map scaffold")
    try:
        from svg_sanitizer import sanitize_svg

        svg = sanitize_svg(_map_scaffold_svg(places, title)) or _map_scaffold_svg(places, title)
    except Exception:  # noqa: BLE001
        svg = _map_scaffold_svg(places, title)

    return [
        VisualSpec(
            visual_id="geography:map_scaffold",
            visual_type="clickable_map",
            source="geography_scaffold",
            provenance="universal_visual_intelligence.providers.geography",
            caption=title,
            alt_text="Map scaffold listing places named in the verified lesson; no invented borders or coordinates.",
            svg=svg,
            invents_curriculum=False,
            deterministic=True,
            engine_id="uvie_geography",
            task_kind="geography_scaffold",
            metadata={"place_count": len(places), "invents_geodata": False},
        )
    ]
