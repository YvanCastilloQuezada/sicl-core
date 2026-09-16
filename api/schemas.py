from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ProjectCreateRequest(BaseModel):
    project_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
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


class V1Envelope(BaseModel):
    contract_version: str
    status: str
    code: str
    message: str
    project_id: str | None = None
    observed_version: int | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class CanonicalProjectCreateRequest(BaseModel):
    project_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    spatial_scope: dict[str, Any] | None = None
    temporal_scope: dict[str, Any] | None = None
    actor: str = Field(default="api", min_length=1)


class CanonicalCommandRequest(BaseModel):
    command: str = Field(min_length=1)
    actor: str = Field(default="api", min_length=1)


class CanonicalWriteRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    @property
    def payload(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class ProjectResponse(BaseModel):
    project_id: str
    name: str
    stage: str
    version: int
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
