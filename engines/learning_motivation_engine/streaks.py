"""Healthy streaks — grace days, recovery, never punish missed days."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any


def _today() -> date:
    return datetime.now(timezone.utc).date()


def record_activity(state: dict[str, Any], *, flexible: bool = True) -> dict[str, Any]:
    streaks = dict(state.get("streaks") or {})
    last = streaks.get("last_active_date")
    today = _today().isoformat()
    daily = int(streaks.get("daily") or 0)
    grace = int(streaks.get("grace_days_used") or 0)
    grace_budget = int(streaks.get("grace_budget") or 2)

    if last == today:
        state["streaks"] = streaks
        return {"ok": True, "streaks": streaks, "note": "already_counted_today"}

    if last:
        try:
            last_d = date.fromisoformat(str(last))
            gap = (_today() - last_d).days
        except Exception:  # noqa: BLE001
            gap = 1
        if gap == 1:
            daily += 1
        elif gap == 2 and flexible and grace < grace_budget:
            # grace day — continue streak, no punishment
            daily += 1
            grace += 1
            streaks["recovered"] = True
        elif gap > 1:
            # Reset gently — never shame
            daily = 1
            streaks["message"] = "Fresh start — missing days never reduce your worth as a learner."
            streaks["recovered"] = True
        else:
            daily = max(daily, 1)
    else:
        daily = 1

    streaks["daily"] = daily
    streaks["best_daily"] = max(int(streaks.get("best_daily") or 0), daily)
    streaks["weekly"] = min(7, daily)  # simplified rolling signal
    streaks["monthly"] = min(30, daily)
    streaks["grace_days_used"] = grace
    streaks["grace_budget"] = grace_budget
    streaks["last_active_date"] = today
    streaks["policy"] = "no_punish_missed_days"
    state["streaks"] = streaks
    return {"ok": True, "streaks": streaks, "state": state}
