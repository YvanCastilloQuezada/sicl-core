"""UCG Pipeline R1: coordinated identity-to-gate decision flow.

This pipeline performs a permission decision only. It never executes operations.
"""
from dataclasses import dataclass

from .registry import CanonicalRegistry
from .resolver import CanonicalResolver
from .authorization import CanonicalAuthorization
from .execution_gate import CanonicalExecutionGate

PIPELINE_CONTRACT_VERSION = "UCG-PIPELINE-R1"


@dataclass(frozen=True)
class PipelineResult:
    permitted: bool
    code: str
    resolution: object
    authorization: object
    gate: object


class CanonicalPipeline:
    """Orchestrates Registry, Resolver, Authorization and Execution Gate."""

    def __init__(
        self,
        registry=None,
        authorization=None,
        gate=None,
    ):
        self.registry = registry if registry is not None else CanonicalRegistry()
        self.resolver = CanonicalResolver(self.registry)
        self.authorization = (
            authorization if authorization is not None
            else CanonicalAuthorization()
        )
        self.gate = gate if gate is not None else CanonicalExecutionGate()

    def register(self, identity):
        return self.registry.register(identity)

    def grant(self, identity):
        return self.authorization.grant(identity)

    def revoke(self, identity):
        return self.authorization.revoke(identity)

    def evaluate(self, identity):
        resolution = self.resolver.resolve(identity)

        auth_result = self.authorization.authorize(
            identity,
            resolution,
        )

        gate_result = self.gate.evaluate(
            identity,
            resolution,
            auth_result,
        )

        return PipelineResult(
            permitted=gate_result.permitted,
            code=gate_result.code,
            resolution=resolution,
            authorization=auth_result,
            gate=gate_result,
        )
