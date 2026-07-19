"""Stable, user-safe result envelope shared across Alora v3 surfaces."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


@dataclass
class PipelineResultEnvelope:
    code: str
    stage: str
    engine: str
    status: Literal["success", "partial", "failed", "blocked"]
    message: str
    severity: Literal["info", "warning", "error"] = "info"
    retryable: bool = False
    recovery: str = ""
    fallback_used: str = "none"
    warnings: list[dict[str, Any]] = field(default_factory=list)
    payload: Any = None
    audit_reference: str = ""
    schema_version: str = "3.0.0"

    @property
    def ok(self) -> bool:
        return self.status in {"success", "partial"}

    @property
    def errors(self) -> list[str]:
        return [] if self.ok else [self.message]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["ok"] = self.ok
        data["errors"] = self.errors
        return data


def success(stage: str, engine: str, payload: Any = None, **kwargs: Any) -> PipelineResultEnvelope:
    return PipelineResultEnvelope(
        code=f"{stage}.success",
        stage=stage,
        engine=engine,
        status="success",
        message=kwargs.pop("message", f"{stage.replace('_', ' ').title()} completed."),
        payload=payload,
        **kwargs,
    )


def partial(stage: str, engine: str, message: str, payload: Any = None, **kwargs: Any) -> PipelineResultEnvelope:
    return PipelineResultEnvelope(
        code=kwargs.pop("code", f"{stage}.partial"),
        stage=stage,
        engine=engine,
        status="partial",
        message=message,
        severity="warning",
        payload=payload,
        **kwargs,
    )


def failed(stage: str, engine: str, message: str, **kwargs: Any) -> PipelineResultEnvelope:
    return PipelineResultEnvelope(
        code=kwargs.pop("code", f"{stage}.failed"),
        stage=stage,
        engine=engine,
        status="failed",
        message=message,
        severity="error",
        **kwargs,
    )
