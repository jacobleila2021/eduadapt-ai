"""Administrative dashboards for curriculum expansion."""

from __future__ import annotations

from typing import Any

from engines.curriculum_expansion_framework.registry import import_logs, list_curricula, list_supported_boards
from engines.curriculum_expansion_framework.versioning import version_history
from engines.universal_curriculum_framework.curriculum_registry import list_packages


def admin_dashboard() -> dict[str, Any]:
    curricula = list_curricula()
    by_status: dict[str, int] = {}
    by_family: dict[str, int] = {}
    missing = []
    for c in curricula:
        ps = str(c.get("publication_status") or "draft")
        by_status[ps] = by_status.get(ps, 0) + 1
        fam = str(c.get("family_id") or "unknown")
        by_family[fam] = by_family.get(fam, 0) + 1
        if c.get("import_status") in ("not_started", None) and (c.get("provenance") or {}).get("incremental_priority", 99) <= 2:
            missing.append(c.get("curriculum_id"))

    packages = list_packages(status="") + list_packages(status="active")
    # dedupe by package_id
    seen = set()
    uniq = []
    for p in packages:
        pid = p.get("package_id")
        if pid in seen:
            continue
        seen.add(pid)
        uniq.append(p)

    coverage: dict[str, int] = {}
    for p in uniq:
        bid = str(p.get("board_id") or "unknown")
        coverage[bid] = coverage.get(bid, 0) + 1

    return {
        "ok": True,
        "imported_curricula": curricula,
        "supported_boards": list_supported_boards(),
        "validation_status": by_status,
        "mapping_completeness": {
            "published": by_status.get("published", 0),
            "validated": by_status.get("validated", 0),
            "draft": by_status.get("draft", 0),
            "rejected": by_status.get("rejected", 0),
        },
        "missing_content": missing,
        "version_history_sample": {
            cid: version_history(cid).get("history")[-3:]
            for cid in ("ncert", "cbse")
        },
        "import_logs": import_logs(30),
        "coverage_by_board": coverage,
        "coverage_by_family": by_family,
        "ucf_packages": len(uniq),
        "incremental_order": [
            "1 NCERT+CBSE",
            "2 ICSE/ISC",
            "3 Cambridge",
            "4 IB",
            "5 Kerala State Board",
            "7 Universities",
            "8 Professional learning",
        ],
    }
