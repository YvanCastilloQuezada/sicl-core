from __future__ import annotations

import sqlite3
import pytest

from sicl.copilot_session_repository import CopilotSessionRepository


def make_repo(tmp_path):
    repo = CopilotSessionRepository(tmp_path / "copilot.sqlite")
    repo.create_session(session_id="s-1", project_id="p-1", actor_id="architect-1", channel="FIELD")
    return repo


def append(repo, **overrides):
    args = dict(message_id="m-1", session_id="s-1", role="architect", content="nota de campo",
                attachments=["asset-1"], metadata={"surface": "FIELD"}, idempotency_key="idem-1")
    args.update(overrides)
    return repo.append_message(**args)


def test_session_is_shared_by_channel_and_actor_scope(tmp_path):
    repo = make_repo(tmp_path)
    repo.create_session(session_id="s-2", project_id="p-1", actor_id="architect-2", channel="OFFICE")
    assert [s["session_id"] for s in repo.list_sessions(project_id="p-1", actor_id="architect-1")] == ["s-1"]
    assert repo.get_session("s-1")["channel"] == "FIELD"
    repo.close()


def test_append_order_and_attachment_only_messages(tmp_path):
    repo = make_repo(tmp_path)
    first = append(repo)
    second = append(repo, message_id="m-2", idempotency_key="idem-2", content="", attachments=["photo-2"])
    assert first["sequence"] == 1
    assert second["sequence"] == 2
    assert second["content"] == ""
    assert repo.list_messages(session_id="s-1") == [first, second]
    repo.close()


def test_duplicate_retry_returns_original_without_second_message(tmp_path):
    repo = make_repo(tmp_path)
    first = append(repo)
    retry = append(repo)
    assert retry["code"] == "DUPLICATE"
    assert retry["sequence"] == first["sequence"]
    assert len(repo.list_messages(session_id="s-1")) == 1
    repo.close()


def test_reused_idempotency_key_with_changed_payload_conflicts(tmp_path):
    repo = make_repo(tmp_path)
    append(repo)
    with pytest.raises(ValueError, match="IDEMPOTENCY_CONFLICT"):
        append(repo, message_id="m-2", content="different")
    assert len(repo.list_messages(session_id="s-1")) == 1
    repo.close()


def test_unknown_session_rejected(tmp_path):
    repo = CopilotSessionRepository(tmp_path / "empty.sqlite")
    with pytest.raises(KeyError, match="SESSION_NOT_FOUND"):
        repo.append_message(message_id="m", session_id="missing", role="architect",
                           content="x", idempotency_key="i")
    repo.close()


def test_message_limits_and_validation(tmp_path):
    repo = make_repo(tmp_path)
    with pytest.raises(ValueError, match="size limit"):
        append(repo, content="x" * 70000)
    with pytest.raises(ValueError, match="unsupported message role"):
        append(repo, role="assistant")
    repo.close()


def test_append_only_guards(tmp_path):
    repo = make_repo(tmp_path)
    append(repo)
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        repo.conn.execute("UPDATE copilot_messages SET content='tampered' WHERE message_id='m-1'")
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        repo.conn.execute("DELETE FROM copilot_messages WHERE message_id='m-1'")
    repo.close()


def test_closed_session_rejects_new_messages(tmp_path):
    repo = make_repo(tmp_path)
    assert repo.close_session("s-1")
    with pytest.raises(ValueError, match="SESSION_CLOSED"):
        append(repo, message_id="m-2", idempotency_key="idem-2")
    repo.close()
