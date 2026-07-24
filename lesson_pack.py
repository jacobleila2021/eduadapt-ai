"""Save / share lesson packs — session-safe beta persistence via download."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Mapping


def build_lesson_save_pack(
    *,
    adaptations: Mapping[str, Any],
    meta: Mapping[str, Any] | None = None,
    topic: str = "Lesson",
) -> bytes:
    """JSON lesson pack teachers can re-upload / archive (Save)."""
    payload = {
        "schema": "alora.lesson_save_pack.v1",
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "meta": {
            "version": (meta or {}).get("version"),
            "publication_ready": (meta or {}).get("ok"),
            "pmes": (meta or {}).get("pmes"),
            "peec": (meta or {}).get("peec"),
            "uevb": (meta or {}).get("uevb"),
        },
        "adaptations": {
            k: v
            for k, v in (adaptations or {}).items()
            if not str(k).startswith("_") and isinstance(v, dict)
        },
    }
    return json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")


def build_share_readme(topic: str = "Lesson") -> str:
    return (
        f"Alora AI — Share pack for {topic}\n\n"
        "1. Open the HTML file in any browser.\n"
        "2. Use Ctrl+P / Cmd+P to print or Save as PDF.\n"
        "3. Keep the JSON save pack to restore the lesson later.\n"
        "4. Do not edit verified science facts; only presentation may change.\n"
    )
