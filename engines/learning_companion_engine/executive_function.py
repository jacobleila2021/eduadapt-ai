"""Executive function coaching — planning, initiation, breaks (presentation coaching)."""

from __future__ import annotations

from typing import Any

from engines.learning_companion_engine.personality import apply_style
from engines.learning_companion_engine.schemas import CompanionMessage


def coach_ef(
    *,
    need: str,
    companion_id: str = "focus_fox",
    style: str = "calm_mentor",
    task: str = "",
) -> dict[str, Any]:
    """
    need: initiation|planning|organization|time_management|goal_setting|self_monitoring|reflection
    """
    steps_map = {
        "initiation": ["Open the lesson", "Read the first paragraph only", "Write one question you have"],
        "planning": ["Name the goal", "List 3 steps", "Estimate minutes per step", "Start step 1"],
        "organization": ["Gather materials", "Clear workspace", "Open one tab/lesson", "Bookmark where you stop"],
        "time_management": ["Set a 15-minute timer", "Work until the bell", "Take a 3-minute break", "Review what you finished"],
        "goal_setting": ["Pick one measurable goal", "Define done", "Schedule when", "Check progress tomorrow"],
        "self_monitoring": ["Pause mid-task", "Ask: Am I on step X?", "Adjust if needed"],
        "reflection": ["What worked?", "What was hard?", "What will I try next time?"],
    }
    need = need if need in steps_map else "planning"
    steps = steps_map[need]
    if task:
        intro = f"For “{task}”: break it down."
    else:
        intro = f"Let's use a {need.replace('_', ' ')} plan."
    styled = apply_style(f"{intro} " + " → ".join(steps), style)
    msg = CompanionMessage(
        text=styled["text"],
        kind="ef_coach",
        companion_id=companion_id,
        evidence=[{"need": need, "steps": steps}],
        speakable=True,
    )
    return {"ok": True, "message": msg.to_dict(), "steps": steps, "need": need, "suggest_break_after_minutes": 25}
