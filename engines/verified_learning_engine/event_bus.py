"""In-process event bus — publish/subscribe with append-only history."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Callable

from engines.verified_learning_engine.event_registry import EVENT_TYPES, LearningEvent, make_event

Handler = Callable[[LearningEvent], None]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[Handler]] = defaultdict(list)
        self._history: list[LearningEvent] = []
        self._max_history = 5000
        self._dead_letters: list[dict[str, Any]] = []
        self._max_dead_letters = 500

    def subscribe(self, event_type: str, handler: Handler) -> None:
        self._handlers[event_type].append(handler)

    def subscribe_all(self, handler: Handler) -> None:
        self._handlers["*"].append(handler)

    def publish(self, event: LearningEvent) -> LearningEvent:
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]
        for handler in list(self._handlers.get(event.event_type, [])) + list(self._handlers.get("*", [])):
            try:
                handler(event)
            except Exception as exc:  # noqa: BLE001
                self._dead_letters.append(
                    {
                        "event_id": event.event_id,
                        "event_type": event.event_type,
                        "session_id": event.session_id,
                        "handler": getattr(handler, "__qualname__", repr(handler)),
                        "error_type": type(exc).__name__,
                        "error": str(exc)[:500],
                        "ts": datetime.now(timezone.utc).isoformat(),
                    }
                )
                self._dead_letters = self._dead_letters[-self._max_dead_letters :]
        return event

    def emit(
        self,
        event_type: str,
        *,
        session_id: str,
        learner_id: str = "",
        lesson_id: str = "",
        payload: dict[str, Any] | None = None,
        source: str = "vlie",
    ) -> LearningEvent:
        return self.publish(
            make_event(
                event_type,
                session_id=session_id,
                learner_id=learner_id,
                lesson_id=lesson_id,
                payload=payload,
                source=source,
            )
        )

    def history(
        self,
        *,
        session_id: str | None = None,
        event_type: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        rows = self._history
        if session_id:
            rows = [e for e in rows if e.session_id == session_id]
        if event_type:
            rows = [e for e in rows if e.event_type == event_type]
        return [e.to_dict() for e in rows[-limit:]]

    def replay(self, events: list[dict[str, Any]]) -> int:
        """Replay persisted events into history (handlers optional)."""
        count = 0
        for raw in events:
            et = raw.get("event_type") or ""
            if not et:
                continue
            ev = make_event(
                et if et in EVENT_TYPES else et,
                session_id=str(raw.get("session_id") or ""),
                learner_id=str(raw.get("learner_id") or ""),
                lesson_id=str(raw.get("lesson_id") or ""),
                payload=raw.get("payload") or {},
                source=str(raw.get("source") or "replay"),
            )
            # Bypass handlers on replay by default — append only
            object.__setattr__(ev, "event_id", raw.get("event_id") or ev.event_id)  # type: ignore[misc]
            self._history.append(ev)
            count += 1
        return count

    def catalogue(self) -> list[str]:
        return list(EVENT_TYPES)

    def dead_letters(
        self, *, session_id: str | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        rows = self._dead_letters
        if session_id:
            rows = [row for row in rows if row.get("session_id") == session_id]
        return [dict(row) for row in rows[-limit:]]


_BUS: EventBus | None = None


def get_event_bus() -> EventBus:
    global _BUS
    if _BUS is None:
        _BUS = EventBus()
    return _BUS


def reset_event_bus() -> EventBus:
    global _BUS
    _BUS = EventBus()
    return _BUS
