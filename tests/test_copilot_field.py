import pytest

from sicl.copilot_field import CaptureKind, CaptureState, FieldCapture, transition_capture


def photo():
    return FieldCapture(capture_id="c1", kind=CaptureKind.PHOTO, created_at="2026-11-26T10:00:00Z",
                       filename="site.jpg", mime_type="image/jpeg", byte_size=1200)


def test_capture_upload_attach_and_process_lifecycle():
    c=photo()
    c=transition_capture(c,CaptureState.UPLOADING)
    c=transition_capture(c,CaptureState.UPLOADED,remote_asset_id="asset-1")
    c=transition_capture(c,CaptureState.ATTACHED_TO_MESSAGE,message_id="msg-1")
    c=transition_capture(c,CaptureState.PROCESSING)
    c=transition_capture(c,CaptureState.COMPLETED)
    assert c.state is CaptureState.COMPLETED
    assert c.remote_asset_id=="asset-1"


def test_invalid_transition_cannot_claim_server_processing():
    with pytest.raises(ValueError,match="invalid capture transition"):
        transition_capture(photo(),CaptureState.PROCESSING)


def test_upload_ack_required_for_uploaded_state():
    with pytest.raises(ValueError,match="remote_asset_id"):
        FieldCapture(capture_id="c",kind=CaptureKind.PHOTO,created_at="2026-11-26T10:00:00Z",
                    state=CaptureState.UPLOADED)


def test_location_capture_requires_consent_and_valid_coordinates():
    with pytest.raises(ValueError,match="consent"):
        FieldCapture(capture_id="loc",kind=CaptureKind.LOCATION,created_at="2026-11-26T10:00:00Z",
                    latitude=-8.38,longitude=-74.53)
    valid=FieldCapture(capture_id="loc",kind=CaptureKind.LOCATION,created_at="2026-11-26T10:00:00Z",
                       latitude=-8.38,longitude=-74.53,location_consent=True)
    assert valid.latitude==-8.38


def test_retry_after_upload_failure_returns_to_draft():
    c=transition_capture(photo(),CaptureState.UPLOADING)
    c=transition_capture(c,CaptureState.FAILED)
    c=transition_capture(c,CaptureState.LOCAL_DRAFT)
    assert c.state is CaptureState.LOCAL_DRAFT


def test_completed_capture_is_terminal():
    c=photo()
    c=transition_capture(c,CaptureState.UPLOADING)
    c=transition_capture(c,CaptureState.UPLOADED,remote_asset_id="a")
    c=transition_capture(c,CaptureState.ATTACHED_TO_MESSAGE,message_id="m")
    c=transition_capture(c,CaptureState.COMPLETED)
    with pytest.raises(ValueError,match="invalid capture transition"):
        transition_capture(c,CaptureState.UPLOADING)
