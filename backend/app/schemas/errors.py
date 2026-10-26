"""Uniform error shape; handlers/status mapping are connected in route tasks."""
from pydantic import Field, JsonValue

from .common import APIModel


class ErrorBody(APIModel):
    code: str = Field(strict=True, min_length=1, pattern=r'^[A-Z][A-Z0-9_]*$')
    message: str = Field(strict=True, min_length=1)
    details: dict[str, JsonValue] = Field(default_factory=dict)


class ErrorEnvelope(APIModel):
    error: ErrorBody
