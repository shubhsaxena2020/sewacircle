"""API tests for the contribution-card state machine and its revision back-edge.

All cards, names and hours here are invented for the test; no network is used
(the drafting step is forced onto its deterministic local parser).
"""
from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from app import main
from app.llm import extract
from app.llm.client import LLMError

TASK = {"id": "task-01", "title": "Camp", "slot": "sat_morning", "district": "Lucknow", "block": "Chinhat",
        "lat": 26.8, "lon": 80.9,
        "roles": [{"id": "role-01", "role": "First aid", "count": 1, "required_skills": ["first_aid"]}]}

TERMINAL_SETUP = {
    "confirmed": ("confirm", {}),
    "corrected": ("correct", {"claimed_hours": 4}),
    "rejected": ("reject", {}),
}
HOST_ACTIONS = ("confirm", "correct", "reject", "request_revision")


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


def _draft(client, claimed=5.0, recorded=5.0, role_id="role-01"):
    """Draft one card. claimed == recorded it stays 'draft'; claimed > recorded the rules flag it."""
    r = client.post("/api/evidence/draft", json={
        "task": TASK,
        "host_notes": f"Imran worked {claimed:g} hours.",
        "attendance_rows": [{"volunteer_id": "v-068", "task_id": "task-01", "hours": recorded}],
        "assignments": [{"role_id": role_id, "volunteer_id": "v-068", "volunteer_name": "Imran B."}],
    })
    assert r.status_code == 200, r.text
    return r.json()


def _payload(action, **extra):
    body = dict(extra)
    if action == "request_revision":
        body.setdefault("reason", "the hours do not match the attendance sheet")
    if action == "correct":
        body.setdefault("claimed_hours", 4)
    return body


def test_request_revision_moves_card_and_records_actor_reason_time(client):
    card = _draft(client)[0]
    assert card["status"] == "draft"

    r = client.post(f"/api/evidence/{card['id']}/request_revision",
                    json={"actor": "host-anita", "reason": "hours do not match the sheet"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "revision_requested"
    assert body["revision_reason"] == "hours do not match the sheet"

    entry = client.get("/api/ledger").json()[-1]
    assert entry["action"] == "request_revision"
    assert entry["actor"] == "host-anita"
    assert entry["reason"] == "hours do not match the sheet"
    assert entry["ts"]                                          # ISO-8601 timestamp, recorded by the ledger
    assert client.get("/api/ledger/verify").json()["ok"] is True


def test_redraft_of_that_volunteer_returns_the_card_to_draft(client):
    card = _draft(client, claimed=9.0)[0]                       # 9 h claimed vs 5 h recorded -> flagged
    assert card["status"] == "flagged"
    assert client.post(f"/api/evidence/{card['id']}/request_revision",
                       json={"reason": "please re-check the attendance sheet"}).status_code == 200

    again = _draft(client, claimed=5.0)[0]                      # re-draft of the same volunteer's card
    assert again["id"] == card["id"]
    assert again["status"] == "draft"
    assert again["revision_reason"] is None

    ledger = client.get("/api/ledger").json()
    assert ledger[-1]["action"] == "draft"
    assert "revision" in ledger[-1]["reason"]
    assert [e["action"] for e in ledger] == ["flag", "request_revision", "draft"]
    assert client.get("/api/ledger/verify").json()["ok"] is True


def test_confirmed_card_cannot_be_sent_back(client):
    """The back-edge only exists from the undecided pool; a decision stays final."""
    card = _draft(client)[0]
    assert client.post(f"/api/evidence/{card['id']}/confirm", json={"actor": "host"}).status_code == 200
    r = client.post(f"/api/evidence/{card['id']}/request_revision", json={"reason": "second thoughts"})
    assert r.status_code == 409
    assert "confirmed" in r.json()["detail"]


@pytest.mark.parametrize("blank", [{}, {"reason": ""}, {"reason": "   "}])
def test_request_revision_needs_a_non_blank_reason(client, blank):
    card = _draft(client)[0]
    r = client.post(f"/api/evidence/{card['id']}/request_revision", json=blank)
    assert r.status_code == 422
    assert "reason" in r.json()["detail"]
    assert client.get("/api/evidence/cards").json()[0]["status"] == "draft"   # nothing moved


@pytest.mark.parametrize("claimed,initial", [(5.0, "draft"), (9.0, "flagged")])
@pytest.mark.parametrize("action,target", [("confirm", "confirmed"), ("correct", "corrected"),
                                           ("reject", "rejected"), ("request_revision", "revision_requested")])
def test_legal_host_edges_from_both_undecided_states(client, claimed, initial, action, target):
    card = _draft(client, claimed=claimed)[0]
    assert card["status"] == initial
    r = client.post(f"/api/evidence/{card['id']}/{action}", json=_payload(action))
    assert r.status_code == 200, r.text
    assert r.json()["status"] == target
    assert client.get("/api/ledger").json()[-1]["action"] == action


@pytest.mark.parametrize("state", sorted(TERMINAL_SETUP))
@pytest.mark.parametrize("action", HOST_ACTIONS)
def test_every_action_from_a_final_state_is_409(client, state, action):
    setup_action, setup_body = TERMINAL_SETUP[state]
    card = _draft(client)[0]
    assert client.post(f"/api/evidence/{card['id']}/{setup_action}", json=setup_body).status_code == 200

    r = client.post(f"/api/evidence/{card['id']}/{action}", json=_payload(action))
    assert r.status_code == 409
    detail = r.json()["detail"]
    assert "illegal transition" in detail and state in detail and "legal actions" in detail
    assert client.get("/api/evidence/cards").json()[0]["status"] == state   # state untouched


@pytest.mark.parametrize("action", HOST_ACTIONS)
def test_revision_requested_refuses_any_host_action_but_redraft(client, action):
    card = _draft(client)[0]
    assert client.post(f"/api/evidence/{card['id']}/request_revision",
                       json={"reason": "fix the role wording"}).status_code == 200
    r = client.post(f"/api/evidence/{card['id']}/{action}", json=_payload(action))
    assert r.status_code == 409
    assert "revision_requested" in r.json()["detail"]


def test_unknown_card_is_404_not_409(client):
    r = client.post("/api/evidence/card-does-not-exist/request_revision", json={"reason": "x"})
    assert r.status_code == 404


def test_reason_is_inside_the_hash_chain(client, tmp_path):
    """An edited reason must break verify(): the reason is a hashed chain field, not a loose note."""
    card = _draft(client)[0]
    assert client.post(f"/api/evidence/{card['id']}/request_revision",
                       json={"reason": "original reason"}).status_code == 200
    journal = tmp_path / "ledger.jsonl"
    lines = [json.loads(line) for line in journal.read_text(encoding="utf-8").splitlines() if line.strip()]
    lines[-1]["reason"] = "rewritten reason"
    journal.write_text("\n".join(json.dumps(r, sort_keys=True) for r in lines) + "\n", encoding="utf-8")

    result = client.get("/api/ledger/verify").json()
    assert result["ok"] is False
    assert result["first_bad_index"] == len(lines) - 1
