"""Regression tests for issues found by the REA scenario capture of the live app (2026-11-19, docs/RE-SELF-AUDIT.md)."""
import pytest
from fastapi.testclient import TestClient

from app import main
from app.llm import extract
from app.llm.client import LLMError

TASK = {"id": "task-01", "title": "Camp", "slot": "sat_morning", "district": "Lucknow", "block": "Chinhat", "lat": 26.8,
        "lon": 80.9, "roles": [{"id": "role-01", "role": "First aid", "count": 1, "required_skills": ["first_aid"]},
                               {"id": "role-02", "role": "Poster team", "count": 1, "required_skills": ["graphic_design"]}]}


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DATA_DIR", tmp_path)
    monkeypatch.setattr(main, "CARDS_PATH", tmp_path / "cards.json")
    monkeypatch.delenv("SEWA_LEDGER_PATH", raising=False)
    main.S.cards, main.S.ledger = None, None

    def down(*a, **k):
        raise LLMError("offline test: deterministic fallback parser")
    monkeypatch.setattr(extract.client, "complete_json", down)
    yield TestClient(main.app)
    main.S.cards, main.S.ledger = None, None


def _draft(client, role_id, hours=5):
    a = [{"role_id": role_id, "volunteer_id": "v-068", "volunteer_name": "Imran B."}]
    rows = [{"volunteer_id": "v-068", "task_id": "task-01", "hours": 5}]
    r = client.post("/api/evidence/draft", json={"task": TASK, "host_notes": f"Imran worked {hours} hours.",
                                                 "attendance_rows": rows, "assignments": a})
    assert r.status_code == 200, r.text
    return r.json()


def test_reshuffle_does_not_create_false_duplicate_evidence_flag(client):
    first = _draft(client, "role-01")
    assert [c["role"] for c in first] == ["First aid"]
    second = _draft(client, "role-02")            # dropout moved v-068 to another role
    assert [c["role"] for c in second] == ["Poster team"]
    assert "duplicate_evidence_ref" not in [f["code"] for f in second[0]["flags"]]
    ids = [c["id"] for c in client.get("/api/evidence/cards").json()]
    assert ids == [second[0]["id"]]               # the stale undecided draft is superseded


def test_host_decided_card_survives_redraft(client):
    first = _draft(client, "role-01")
    assert client.post(f"/api/evidence/{first[0]['id']}/confirm", json={"actor": "host"}).status_code == 200
    _draft(client, "role-02")
    statuses = {c["role"]: c["status"] for c in client.get("/api/evidence/cards").json()}
    assert statuses["First aid"] == "confirmed"   # a human decision is never discarded


def test_demo_reset_archives_state_and_starts_clean(client, tmp_path):
    _draft(client, "role-01")
    assert client.get("/api/ledger").json()
    r = client.post("/api/demo/reset").json()
    assert r["ok"] and r["archived"]
    assert client.get("/api/evidence/cards").json() == []
    assert client.get("/api/ledger").json() == []
    assert any(p.name.startswith("archive-") for p in tmp_path.iterdir())  # archived, not deleted
