"""In-memory UI cache for diagrams/formulae (session-scoped)."""

from __future__ import annotations

from typing import Any

_CACHE: dict[str, Any] = {}
_HITS = 0
_MISSES = 0


def cache_get(key: str) -> Any | None:
    global _HITS, _MISSES
    if key in _CACHE:
        _HITS += 1
        try:
            from engines.learning_experience_platform.phase4_analytics import track_experience

            track_experience("cache_hit", payload={"key_prefix": key[:24]})
        except Exception:  # noqa: BLE001
            pass
        return _CACHE[key]
    _MISSES += 1
    try:
        from engines.learning_experience_platform.phase4_analytics import track_experience

        track_experience("cache_miss", payload={"key_prefix": key[:24]})
    except Exception:  # noqa: BLE001
        pass
    return None


def cache_set(key: str, value: Any, *, max_items: int = 200) -> None:
    if len(_CACHE) >= max_items:
        # drop oldest insertion
        first = next(iter(_CACHE), None)
        if first is not None:
            _CACHE.pop(first, None)
    _CACHE[key] = value


def cache_stats() -> dict[str, Any]:
    return {"ok": True, "size": len(_CACHE), "hits": _HITS, "misses": _MISSES}
