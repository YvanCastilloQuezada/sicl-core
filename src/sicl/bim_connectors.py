from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .bim import BIMFormat, BIMModelSnapshot


@dataclass(frozen=True)
class NativeAdapterResult:
    adapter: str
    format: BIMFormat
    status: str
    read_only: bool
    message: str
    payload: dict[str, Any]


class NativeBIMAdapter:
    format: BIMFormat
    adapter_name: str

    def inspect(self, source: str) -> NativeAdapterResult:
        raise NotImplementedError

    def export_preview(self, snapshot: BIMModelSnapshot, output_path: str) -> NativeAdapterResult:
        return NativeAdapterResult(self.adapter_name, self.format, "PREVIEW_ONLY", True, "Native export requires HumanReview and the host application SDK", {"output_path": output_path, "applied": False})


class RevitAdapter(NativeBIMAdapter):
    format = BIMFormat.REVIT
    adapter_name = "Revit .NET API adapter contract"

    def inspect(self, source: str) -> NativeAdapterResult:
        return NativeAdapterResult(self.adapter_name, self.format, "HOST_REQUIRED", True, "Run inside Revit with the approved .NET add-in; external .rvt parsing is intentionally not attempted", {"source": source})


class ArchicadAdapter(NativeBIMAdapter):
    format = BIMFormat.ARCHICAD
    adapter_name = "Archicad API adapter contract"

    def inspect(self, source: str) -> NativeAdapterResult:
        return NativeAdapterResult(self.adapter_name, self.format, "HOST_REQUIRED", True, "Run inside Archicad with the approved API add-on or export IFC; native .pln parsing is intentionally not attempted", {"source": source})
