"""Tests for opaque drive share keys (SYNTHETIC data, no network).

Covers the key derivation itself and the public read-only route: an unknown key
is 404, a key never reveals the task id, sequential task ids are never accepted,
and the body contains no volunteer name or id.
"""
from __future__ import annotations

import base64
import hashlib
import hmac

import pytest
from fastapi.testclient import TestClient

from app import main, share
from app.schemas import RoleSpec, TaskSpec

SECRET = "test-only-share-secret-value"


def _task(task_id: str, title: str = "Clean-up drive") -> TaskSpec:
    return TaskSpec(id=task_id, title=title, slot="sat_morning", district="Lucknow", block="Chinhat",
                    lat=26.8, lon=80.9,
                    roles=[RoleSpec(id="role-01", role="First aid", count=2, required_skills=["first_aid"]),
                           RoleSpec(id="role-02", role="Poster team", count=1, required_skills=["graphic_design"])])


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SEWA_SHARE_SECRET", SECRET)
    monkeypatch.setattr(main, "DATA_DIR", tmp_path)
    monkeypatch.setattr(main, "CARDS_PATH", tmp_path / "cards.json")
    monkeypatch.setattr(main.S, "tasks", [_task("task-01"), _task("task-02", "Plantation drive")])
    monkeypatch.setattr(main.S, "roster_ready", {})
    share.reset_secret()
    yield TestClient(main.app)
    share.reset_secret()


def test_key_is_sixteen_base32_characters_and_stable(client):
    key = share.share_key_for("task-01")
    assert len(key) == share.KEY_LENGTH == 16
    assert all(ch in share.ALPHABET for ch in key)
    assert share.share_key_for("task-01") == key                    # deterministic per secret
    assert share.share_key_for("task-02") != key


def test_key_is_the_truncated_hmac_not_the_task_id(client):
    """Recompute the key from the secret the way the docstring says, and prove it is one-way."""
    key = share.share_key_for("task-01")
    digest = hmac.new(SECRET.encode("utf-8"), b"task-01", hashlib.sha256).digest()
    assert key == base64.b32encode(digest).decode("ascii")[:16]
    assert base64.b32decode(key) == digest[:10]                     # 16 base32 chars = 80 bits


def test_key_does_not_reveal_the_task_id(client):
    key = share.share_key_for("task-01")
    assert "task-01" not in key and "task-01" not in key.lower()
    assert key.lower() not in "task-01" and key not in "task-01"
    for fragment in ("task", "01", "TASK"):
        assert fragment not in key


def test_resolver_only_knows_keys_for_tasks_it_was_given(client):
    assert share.task_id_for_share_key(share.share_key_for("task-01"), ["task-01", "task-02"]) == "task-01"
    assert share.task_id_for_share_key(share.share_key_for("task-99"), ["task-01", "task-02"]) is None
    assert share.task_id_for_share_key("task-01", ["task-01"]) is None        # an id is not a key
    assert share.task_id_for_share_key("not-a-key", ["task-01"]) is None


def test_public_summary_shape(client):
    key = share.share_key_for("task-01")
    r = client.get(f"/api/drive/{key}")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["title"] == "Clean-up drive"
    assert body["district"] == "Lucknow" and body["block"] == "Chinhat" and body["slot"] == "sat_morning"
    assert body["roles"] == [
        {"role": "First aid", "count": 2, "required_skills": ["first_aid"], "safety_critical": True},
        {"role": "Poster team", "count": 1, "required_skills": ["graphic_design"], "safety_critical": False},
    ]
    assert body["ready"] is None                                    # no roster computed in this process yet
    assert body["synthetic"] is True and "synthetic" in body["notice"]
    assert set(body) == {"title", "district", "block", "slot", "roles", "ready", "notice", "synthetic"}


def test_summary_contains_no_volunteer_id_or_name(client):
    key = share.share_key_for("task-01")
    text = client.get(f"/api/drive/{key}").text
    for volunteer in main.volunteers():
        assert volunteer.id not in text
        assert volunteer.display_name not in text
    assert "task-01" not in text                                    # the id is never echoed back
    assert "volunteer_id" not in text and "volunteer_name" not in text


@pytest.mark.parametrize("bad", ["A" * 16, "ZZZZZZZZZZZZZZZZ", "AAAAAAAAAAAAAAA", "task-01", "1", "%20"])
def test_unknown_or_malformed_key_is_404(client, bad):
    assert client.get(f"/api/drive/{bad}").status_code == 404


@pytest.mark.parametrize("task_id", ["task-01", "task-02", "task-1", "01", "TASK-01"])
def test_sequential_task_ids_are_never_accepted(client, task_id):
    """Walking the id space must never reach the public route."""
    r = client.get(f"/api/drive/{task_id}")
    assert r.status_code == 404
    assert "volunteer" not in r.text.lower()


def test_rotating_the_secret_invalidates_old_links(client, monkeypatch):
    old_key = share.share_key_for("task-01")
    assert client.get(f"/api/drive/{old_key}").status_code == 200
    monkeypatch.setenv("SEWA_SHARE_SECRET", "a-different-secret")
    share.reset_secret()
    assert client.get(f"/api/drive/{old_key}").status_code == 404


def test_ready_verdict_only_appears_after_a_roster_was_computed(client):
    key = share.share_key_for("task-01")
    assert client.get(f"/api/drive/{key}").json()["ready"] is None

    r = client.post("/api/roster", json={"task": _task("task-01").model_dump(mode="json")})
    assert r.status_code == 200, r.text
    ready = client.get(f"/api/drive/{key}").json()["ready"]
    assert isinstance(ready, bool)


def test_secret_is_read_from_env_or_generated_in_memory(client, monkeypatch):
    assert share.server_secret() == SECRET.encode("utf-8")

    monkeypatch.delenv("SEWA_SHARE_SECRET", raising=False)
    share.reset_secret()
    generated = share.server_secret()
    assert len(generated) == 32 and generated != SECRET.encode("utf-8")
    assert share.server_secret() is generated                       # cached for the process, not per call
    share.reset_secret()
    assert share.server_secret() != generated


def test_summary_is_idempotent_for_the_same_key(client):
    key = share.share_key_for("task-01")
    assert client.get(f"/api/drive/{key}").json() == client.get(f"/api/drive/{key}").json()
