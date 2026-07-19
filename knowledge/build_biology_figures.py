"""Create curated Class 8 Science NCERT-style labelled SVG figure pack."""

from __future__ import annotations

import json
from pathlib import Path

FIGURES_DIR = Path(__file__).resolve().parent / "seed" / "figures"


def _svg(title: str, body: str, width: int = 720, height: int = 420) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#FFF9EE"/>
  <text x="24" y="36" font-family="Arial, sans-serif" font-size="20" fill="#041B4D" font-weight="bold">{title}</text>
  <text x="24" y="58" font-family="Arial, sans-serif" font-size="12" fill="#008C95">NCERT Class 8 Science — curated labelled diagram (pilot pack)</text>
  {body}
</svg>
"""


FIGURES = [
    {
        "id": "fig-c8-ch08-plant-cell",
        "chapter": 8,
        "chapter_title": "Cell — Structure and Functions",
        "figure_number": "8.1",
        "title": "Plant cell (labelled)",
        "caption": "Typical plant cell showing cell wall, membrane, nucleus, chloroplast and vacuole.",
        "alt_text": "Diagram of a plant cell with labels for cell wall, cell membrane, nucleus, chloroplast, and large vacuole.",
        "keywords": ["plant cell", "chloroplast", "vacuole", "nucleus"],
        "body": """
  <ellipse cx="360" cy="230" rx="220" ry="140" fill="#E8F7F8" stroke="#008C95" stroke-width="3"/>
  <ellipse cx="360" cy="230" rx="190" ry="115" fill="#FFF9EE" stroke="#041B4D" stroke-width="2"/>
  <circle cx="300" cy="210" r="40" fill="#C0E8EC" stroke="#041B4D" stroke-width="2"/>
  <text x="280" y="215" font-size="12" fill="#041B4D">Nucleus</text>
  <ellipse cx="430" cy="180" rx="28" ry="18" fill="#7BC96F" stroke="#041B4D"/>
  <text x="400" y="155" font-size="12" fill="#041B4D">Chloroplast</text>
  <ellipse cx="420" cy="270" rx="50" ry="35" fill="#DCEEFF" stroke="#041B4D"/>
  <text x="395" y="275" font-size="12" fill="#041B4D">Vacuole</text>
  <text x="120" y="120" font-size="13" fill="#041B4D">Cell wall</text>
  <text x="150" y="250" font-size="13" fill="#041B4D">Cell membrane</text>
""",
    },
    {
        "id": "fig-c8-ch08-animal-cell",
        "chapter": 8,
        "chapter_title": "Cell — Structure and Functions",
        "figure_number": "8.2",
        "title": "Animal cell (labelled)",
        "caption": "Typical animal cell showing membrane, nucleus, cytoplasm and mitochondria.",
        "alt_text": "Diagram of an animal cell with nucleus, cytoplasm, cell membrane and mitochondria labelled.",
        "keywords": ["animal cell", "mitochondria", "nucleus"],
        "body": """
  <ellipse cx="360" cy="230" rx="200" ry="130" fill="#FFF9EE" stroke="#041B4D" stroke-width="3"/>
  <circle cx="340" cy="220" r="45" fill="#C0E8EC" stroke="#041B4D" stroke-width="2"/>
  <text x="315" y="225" font-size="12" fill="#041B4D">Nucleus</text>
  <ellipse cx="430" cy="260" rx="30" ry="16" fill="#F4C27A" stroke="#041B4D"/>
  <text x="405" y="295" font-size="12" fill="#041B4D">Mitochondria</text>
  <text x="140" y="230" font-size="13" fill="#041B4D">Cell membrane</text>
  <text x="300" y="320" font-size="13" fill="#008C95">Cytoplasm</text>
""",
    },
    {
        "id": "fig-c8-ch13-sound-wave",
        "chapter": 13,
        "chapter_title": "Sound",
        "figure_number": "13.1",
        "title": "Sound wave — amplitude and wavelength",
        "caption": "Longitudinal wave representation showing amplitude and wavelength.",
        "alt_text": "Sine wave labelled with amplitude and wavelength for sound.",
        "keywords": ["sound", "amplitude", "wavelength", "frequency"],
        "body": """
  <path d="M40 220 C 80 120, 120 320, 160 220 S 240 120, 280 220 S 360 320, 400 220 S 480 120, 520 220 S 600 320, 660 220"
        fill="none" stroke="#008C95" stroke-width="3"/>
  <line x1="160" y1="220" x2="160" y2="130" stroke="#041B4D" stroke-dasharray="4"/>
  <text x="168" y="150" font-size="13" fill="#041B4D">Amplitude</text>
  <line x1="160" y1="340" x2="400" y2="340" stroke="#041B4D" marker-end="url(#arrow)"/>
  <text x="240" y="365" font-size="13" fill="#041B4D">Wavelength (λ)</text>
""",
    },
    {
        "id": "fig-c8-ch16-reflection",
        "chapter": 16,
        "chapter_title": "Light",
        "figure_number": "16.1",
        "title": "Laws of reflection",
        "caption": "Incident ray, reflected ray and normal at a plane mirror.",
        "alt_text": "Ray diagram showing incident ray, reflected ray and normal on a mirror.",
        "keywords": ["reflection", "mirror", "incident ray", "normal"],
        "body": """
  <line x1="360" y1="80" x2="360" y2="360" stroke="#041B4D" stroke-width="4"/>
  <text x="370" y="100" font-size="13" fill="#041B4D">Mirror</text>
  <line x1="360" y1="220" x2="360" y2="80" stroke="#999" stroke-dasharray="6"/>
  <text x="368" y="150" font-size="12" fill="#666">Normal</text>
  <line x1="120" y1="320" x2="360" y2="220" stroke="#008C95" stroke-width="3"/>
  <line x1="360" y1="220" x2="600" y2="320" stroke="#14D9E5" stroke-width="3"/>
  <text x="140" y="345" font-size="13" fill="#008C95">Incident ray</text>
  <text x="500" y="345" font-size="13" fill="#041B4D">Reflected ray</text>
""",
    },
    {
        "id": "fig-c8-ch11-pressure",
        "chapter": 11,
        "chapter_title": "Force and Pressure",
        "figure_number": "11.1",
        "title": "Pressure = Force / Area",
        "caption": "Same force on small vs large area — pressure is higher on smaller area.",
        "alt_text": "Two blocks showing force on small and large area with pressure labels.",
        "keywords": ["pressure", "force", "area"],
        "body": """
  <rect x="80" y="160" width="80" height="160" fill="#C0E8EC" stroke="#041B4D" stroke-width="2"/>
  <rect x="400" y="200" width="200" height="120" fill="#E8F7F8" stroke="#041B4D" stroke-width="2"/>
  <text x="95" y="140" font-size="13" fill="#041B4D">Small area → high P</text>
  <text x="430" y="180" font-size="13" fill="#041B4D">Large area → low P</text>
  <text x="100" y="250" font-size="14" fill="#008C95">F</text>
  <text x="490" y="270" font-size="14" fill="#008C95">F</text>
  <text x="200" y="380" font-size="16" fill="#041B4D">P = F / A</text>
""",
    },
    {
        "id": "fig-c8-ch06-flame",
        "chapter": 6,
        "chapter_title": "Combustion and Flame",
        "figure_number": "6.1",
        "title": "Zones of a candle flame",
        "caption": "Outer non-luminous (hottest), middle luminous, and inner dark zones.",
        "alt_text": "Candle flame with three zones labelled: outer, middle and inner.",
        "keywords": ["flame", "combustion", "ignition"],
        "body": """
  <ellipse cx="360" cy="250" rx="70" ry="110" fill="#FFE08A" stroke="#041B4D"/>
  <ellipse cx="360" cy="250" rx="45" ry="80" fill="#FFB84D" stroke="#041B4D"/>
  <ellipse cx="360" cy="270" rx="22" ry="40" fill="#4A3728" stroke="#041B4D"/>
  <text x="450" y="180" font-size="13" fill="#041B4D">Outer non-luminous (hottest)</text>
  <text x="450" y="250" font-size="13" fill="#041B4D">Middle luminous zone</text>
  <text x="450" y="310" font-size="13" fill="#041B4D">Inner dark zone</text>
""",
    },
]


def build_figure_pack() -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    index = []
    for fig in FIGURES:
        svg_path = FIGURES_DIR / f"{fig['id']}.svg"
        svg_path.write_text(_svg(fig["title"], fig["body"]), encoding="utf-8")
        index.append(
            {
                "id": fig["id"],
                "chapter": fig["chapter"],
                "chapter_title": fig["chapter_title"],
                "figure_number": fig["figure_number"],
                "title": fig["title"],
                "caption": fig["caption"],
                "alt_text": fig["alt_text"],
                "keywords": fig["keywords"],
                "path": str(svg_path),
                "relative_path": f"figures/{fig['id']}.svg",
            }
        )
    index_path = FIGURES_DIR / "index.json"
    index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
    return index_path


if __name__ == "__main__":
    out = build_figure_pack()
    print(f"Wrote figure pack index → {out}")
