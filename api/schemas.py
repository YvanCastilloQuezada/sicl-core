from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class ProjectCreateRequest(BaseModel):
    project_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    spatial_scope: str | None = None
    temporal_scope: str = "proyecto"
    actor: str = Field(default="api", min_length=1)


class ProjectUpdateRequest(BaseModel):
    stage: str | None = None
    actor: str = Field(default="api", min_length=1)


class CommandRequest(BaseModel):
    command: str = Field(min_length=1)
    actor: str = Field(default="api", min_length=1)


class APIResponse(BaseModel):
    status: str
    code: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class ProjectResponse(BaseModel):
    project_id: str
    name: str
    stage: str
    version: int
    spatial_scope: str | None = None
    temporal_scope: str = "proyecto"
    objectives: dict[str, Any] = Field(default_factory=dict)
    constraints: dict[str, Any] = Field(default_factory=dict)
    roles: dict[str, Any] = Field(default_factory=dict)
    facts: dict[str, Any] = Field(default_factory=dict)
    assumptions: dict[str, Any] = Field(default_factory=dict)
    decisions: dict[str, Any] = Field(default_factory=dict)
    alternatives: dict[str, Any] = Field(default_factory=dict)
    evaluations: dict[str, Any] = Field(default_factory=dict)
    comparisons: dict[str, Any] = Field(default_factory=dict)
    recommendations: dict[str, Any] = Field(default_factory=dict)
