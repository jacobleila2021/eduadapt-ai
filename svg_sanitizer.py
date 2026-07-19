"""Strict SVG allow-list sanitizer for model or imported educational diagrams."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

ET.register_namespace("", "http://www.w3.org/2000/svg")

_ALLOWED_TAGS = {
    "svg",
    "g",
    "defs",
    "title",
    "desc",
    "rect",
    "circle",
    "ellipse",
    "line",
    "polyline",
    "polygon",
    "path",
    "text",
    "tspan",
    "marker",
    "filter",
    "feDropShadow",
    "linearGradient",
    "radialGradient",
    "stop",
}
_ALLOWED_ATTRS = {
    "xmlns",
    "width",
    "height",
    "viewBox",
    "role",
    "aria-label",
    "aria-labelledby",
    "id",
    "class",
    "x",
    "y",
    "x1",
    "x2",
    "y1",
    "y2",
    "cx",
    "cy",
    "r",
    "rx",
    "ry",
    "d",
    "points",
    "transform",
    "fill",
    "fill-opacity",
    "stroke",
    "stroke-width",
    "stroke-linecap",
    "stroke-linejoin",
    "stroke-dasharray",
    "stroke-opacity",
    "opacity",
    "font-family",
    "font-size",
    "font-weight",
    "text-anchor",
    "dominant-baseline",
    "marker-start",
    "marker-mid",
    "marker-end",
    "offset",
    "stop-color",
    "stop-opacity",
    "gradientUnits",
    "gradientTransform",
    "filter",
    "dx",
    "dy",
    "stdDeviation",
    "flood-color",
    "flood-opacity",
    "orient",
    "markerWidth",
    "markerHeight",
    "refX",
    "refY",
}
_SAFE_VALUE = re.compile(r"^(?!.*(?:javascript:|data:text/html|<|>)).*$", re.I | re.S)


def _local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def sanitize_svg(svg: str) -> str:
    """Return safe SVG markup or an empty string when parsing/validation fails."""
    if not isinstance(svg, str) or len(svg) > 500_000:
        return ""
    try:
        root = ET.fromstring(svg.strip())
    except (ET.ParseError, ValueError):
        return ""
    if _local_name(root.tag) != "svg":
        return ""

    def clean(element: ET.Element) -> None:
        for child in list(element):
            if _local_name(child.tag) not in _ALLOWED_TAGS:
                element.remove(child)
            else:
                clean(child)
        clean_attributes: dict[str, str] = {}
        for raw_name, raw_value in element.attrib.items():
            name = _local_name(raw_name)
            value = str(raw_value)
            if name.lower().startswith("on") or name not in _ALLOWED_ATTRS:
                continue
            if not _SAFE_VALUE.match(value):
                continue
            if "url(" in value.lower() and not re.fullmatch(
                r"url\(\s*#[A-Za-z0-9_.:-]+\s*\)", value
            ):
                continue
            clean_attributes[name] = value
        element.attrib.clear()
        element.attrib.update(clean_attributes)

    clean(root)

    root.set("role", root.attrib.get("role") or "img")
    if not root.attrib.get("aria-label") and not root.attrib.get("aria-labelledby"):
        root.set("aria-label", "Educational diagram")
    return ET.tostring(root, encoding="unicode", short_empty_elements=True)
