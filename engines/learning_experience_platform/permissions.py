"""LXP Phase 3 RBAC — secure collaboration permissions."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform.phase3_schemas import ROLE_PERMISSIONS, ROLES


def normalize_role(role: str | None) -> str:
    r = (role or "student").strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "learner": "student",
        "educator": "teacher",
        "sped": "special_educator",
        "specialeducator": "special_educator",
        "admin": "administrator",
    }
    r = aliases.get(r, r)
    return r if r in ROLES else "student"


def can(role: str, action: str) -> bool:
    role = normalize_role(role)
    perms = ROLE_PERMISSIONS.get(role) or frozenset()
    if "*" in perms:
        return True
    return action in perms


def require(role: str, action: str) -> dict[str, Any]:
    ok = can(role, action)
    return {
        "ok": ok,
        "role": normalize_role(role),
        "action": action,
        "denied": None if ok else f"Role '{normalize_role(role)}' cannot '{action}'",
    }


def parents_cannot_alter_curriculum(role: str) -> bool:
    """Parents and similar viewers never mutate verified curriculum."""
    return normalize_role(role) in ("parent",)


def filter_visible_comments(
    comments: list[dict[str, Any]],
    *,
    viewer_id: str,
    viewer_role: str,
) -> list[dict[str, Any]]:
    role = normalize_role(viewer_role)
    out: list[dict[str, Any]] = []
    for c in comments:
        audience = str(c.get("audience") or "class")
        audience_ids = list(c.get("audience_ids") or [])
        author_role = normalize_role(str(c.get("author_role") or ""))
        if role == "administrator":
            out.append(c)
            continue
        if c.get("author_id") == viewer_id:
            out.append(c)
            continue
        if audience == "class" and role in ("student", "teacher", "administrator"):
            out.append(c)
        elif audience == "parents" and role in ("parent", "teacher", "administrator"):
            out.append(c)
        elif audience == "special_educators" and role in ("special_educator", "teacher", "administrator"):
            out.append(c)
        elif audience == "selected_students" and (viewer_id in audience_ids or role in ("teacher", "administrator")):
            out.append(c)
        elif author_role == "teacher" and role == "parent" and audience in ("class", "parents"):
            out.append(c)
    return out
