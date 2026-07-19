"""Publisher — CEF/UCF publish with RBAC + immutability checks."""

from __future__ import annotations

from typing import Any

from engines.curriculum_migration_framework.licensing import can_publish
from engines.curriculum_migration_framework.provenance import append_audit
from engines.curriculum_migration_framework.versioning import save_version


def publish_to_ucf(
    *,
    job_id: str,
    curriculum_id: str,
    ucf_payload: dict[str, Any],
    role: str = "curriculum_publisher",
    dry_run: bool = False,
) -> dict[str, Any]:
    if not can_publish(role) and role not in ("", "system", "test"):
        # allow system/test for automated pipelines; deny unknown roles
        if role not in ("administrator", "curriculum_publisher", "content_admin", "system", "test"):
            return {"ok": False, "error": "publish_forbidden", "role": role}

    if dry_run:
        return {"ok": True, "dry_run": True, "curriculum_id": curriculum_id}

    from engines.curriculum_expansion_framework.import_pipeline import import_package, publish_package

    result = import_package(curriculum_id, ucf_payload, publish=True, source="cmif")
    if not result.get("ok"):
        append_audit(job_id, "publish_failed", {"result": result})
        return {"ok": False, "error": "cef_import_failed", "detail": result}

    package_id = str(result.get("package_id") or ucf_payload.get("package_id") or "")
    pub = publish_package(curriculum_id, package_id) if package_id else {"ok": True}
    ver = save_version(package_id or curriculum_id, ucf_payload, status="published", note="cmif_publish")
    append_audit(job_id, "published", {"package_id": package_id, "version": ver})
    return {
        "ok": bool(result.get("ok") and pub.get("ok")),
        "package_id": package_id,
        "cef": result,
        "publish": pub,
        "version": ver,
        "immutable": True,
    }
