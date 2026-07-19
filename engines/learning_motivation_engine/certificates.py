"""Certificates — metadata, QR verification payload, issue history (auditable)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any
import uuid


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sign(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def issue_certificate(
    state: dict[str, Any],
    *,
    kind: str,
    title: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    kind: course_completion|competency|mastery|milestone
    Digital signature is a deterministic hash (pilot); production may use PKI.
    """
    cert_id = f"cert_{uuid.uuid4().hex[:12]}"
    body = {
        "certificate_id": cert_id,
        "kind": kind,
        "title": title,
        "learner_id": state.get("learner_id"),
        "issued_at": _now(),
        "metadata": metadata or {},
        "xp_at_issue": state.get("xp_total"),
        "level_at_issue": state.get("level_id"),
    }
    signature = _sign(body)
    qr_payload = f"alora://verify/{cert_id}?sig={signature[:16]}"
    cert = {
        **body,
        "digital_signature": signature,
        "qr_verification": qr_payload,
        "verify_hint": "Hash-based pilot verification — replace with PKI in production",
    }
    certs = list(state.get("certificates") or [])
    certs.append(cert)
    state["certificates"] = certs
    return {"ok": True, "certificate": cert, "state": state}


def verify_certificate(cert: dict[str, Any]) -> dict[str, Any]:
    sig = cert.get("digital_signature")
    body = {k: cert[k] for k in ("certificate_id", "kind", "title", "learner_id", "issued_at", "metadata", "xp_at_issue", "level_at_issue") if k in cert}
    expected = _sign(body)
    return {"ok": sig == expected, "certificate_id": cert.get("certificate_id"), "method": "sha256_pilot"}
