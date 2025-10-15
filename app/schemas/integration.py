"""Integration schemas."""
from typing import Any

from pydantic import BaseModel


class IntegrationCreate(BaseModel):
    """Create integration request."""

    name: str
    description: str
    hooks: list[str]
    config: dict[str, Any] = {}


class IntegrationResponse(BaseModel):
    """Integration response."""

    id: int
    name: str
    description: str
    hooks: list[str]
    config: dict[str, Any]
    enabled: bool

    class Config:
        from_attributes = True
