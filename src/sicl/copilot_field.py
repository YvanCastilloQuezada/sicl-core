"""CP-06 Field capture metadata and safe attachment lifecycle.

No binary upload/storage is implemented here. This model represents capture state
for a mobile client/server protocol and prevents UI from claiming remote processing
when an attachment is only local or upload is uncertain.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class CaptureKind(str, Enum):
    PHOTO = "PHOTO"
    AUDIO = "AUDIO"
    DOCUMENT = "DOCUMENT"
    NOTE = "NOTE"
    LOCATION = "LOCATION"


class CaptureState(str, Enum):
    LOCAL_DRAFT = "LOCAL_DRAFT"
    UPLOADING = "UPLOADING"
    UPLOADED = "UPLOADED"
    ATTACHED_TO_MESSAGE = "ATTACHED_TO_MESSAGE"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


_ALLOWED = {
    CaptureState.LOCAL_DRAFT: {CaptureState.UPLOADING, CaptureState.CANCELLED},
    CaptureState.UPLOADING: {CaptureState.UPLOADED, CaptureState.FAILED, CaptureState.LOCAL_DRAFT, CaptureState.CANCELLED},
    CaptureState.UPLOADED: {CaptureState.ATTACHED_TO_MESSAGE, CaptureState.CANCELLED},
    CaptureState.ATTACHED_TO_MESSAGE: {CaptureState.PROCESSING, CaptureState.COMPLETED, CaptureState.FAILED},
    CaptureState.PROCESSING: {CaptureState.COMPLETED, CaptureState.FAILED},
    CaptureState.FAILED: {CaptureState.LOCAL_DRAFT, CaptureState.UPLOADING, CaptureState.CANCELLED},
    CaptureState.COMPLETED: set(),
    CaptureState.CANCELLED: set(),
}


@dataclass(frozen=True)
class FieldCapture:
    capture_id: str
    kind: CaptureKind
    created_at: str
    state: CaptureState = CaptureState.LOCAL_DRAFT
    filename: str | None = None
    mime_type: str | None = None
    byte_size: int | None = None
    sha256: str | None = None
    remote_asset_id: str | None = None
    message_id: str | None = None
    note: str = ""
    latitude: float | None = None
    longitude: float | None = None
    location_consent: bool = False

    def __post_init__(self) -> None:
        if not self.capture_id.strip():
            raise ValueError("capture_id required")
        try:
            datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("created_at must be ISO-8601") from exc
        if self.byte_size is not None and self.byte_size < 0:
            raise ValueError("byte_size cannot be negative")
        if self.sha256 is not None and (len(self.sha256) != 64 or any(c not in "0123456789abcdefABCDEF" for c in self.sha256)):
            raise ValueError("sha256 must be 64 hexadecimal characters")
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be provided together")
        if self.latitude is not None and not (-90 <= self.latitude <= 90):
            raise ValueError("latitude out of range")
        if self.longitude is not None and not (-180 <= self.longitude <= 180):
            raise ValueError("longitude out of range")
        if self.kind is CaptureKind.LOCATION and not self.location_consent:
            raise ValueError("location capture requires explicit consent")
        if self.state in {CaptureState.UPLOADED, CaptureState.ATTACHED_TO_MESSAGE,
                         CaptureState.PROCESSING, CaptureState.COMPLETED} and not self.remote_asset_id:
            raise ValueError("remote lifecycle states require remote_asset_id")
        if self.state in {CaptureState.ATTACHED_TO_MESSAGE, CaptureState.PROCESSING,
                         CaptureState.COMPLETED} and not self.message_id:
            raise ValueError("message-bound lifecycle states require message_id")


def transition_capture(capture: FieldCapture, next_state: CaptureState, *,
                     remote_asset_id: str | None = None, message_id: str | None = None) -> FieldCapture:
    if next_state not in _ALLOWED.get(capture.state, set()):
        raise ValueError(f"invalid capture transition: {capture.state.value}->{next_state.value}")
    updates = {}
    if remote_asset_id is not None:
        updates["remote_asset_id"] = remote_asset_id
    if message_id is not None:
        updates["message_id"] = message_id
    if next_state in {CaptureState.UPLOADED, CaptureState.ATTACHED_TO_MESSAGE,
                       CaptureState.PROCESSING, CaptureState.COMPLETED}:
        if not (remote_asset_id or capture.remote_asset_id):
            raise ValueError("upload acknowledgement/asset ID required")
    if next_state in {CaptureState.ATTACHED_TO_MESSAGE, CaptureState.PROCESSING, CaptureState.COMPLETED}:
        if not (message_id or capture.message_id):
            raise ValueError("message ID required")
    updates["state"] = next_state
    return FieldCapture(**{**capture.__dict__, **updates})
