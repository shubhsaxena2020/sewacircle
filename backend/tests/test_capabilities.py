"""Tests for the demo-role capability menu and its server-side enforcement.

The header is a DEMO switch, not authentication: these tests check that the menu
and the mutating evidence routes read the SAME matrix (one dict), that the
default role stays 'organiser' so existing clients keep working, and that every
other role is refused with 403 on the actions it does not list.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import capabilities, main
from app.llm import extract
from app.llm.client import LLMError

TASK = {"id": "task-01", "title": "Camp", "slot": "sat_morning", "district": "Lucknow", "block": "Chinhat",
        "lat": 26.8, "lon": 80.9,
        "roles": [{"id": "role-01", "role": "First aid", "count": 1, "required_skills": ["first_aid"]}]}

MUTATING_ROUTES = {
    "draft_cards": ("post", "/api/evidence/draft"),
    "confirm_card": ("post", "/api/evidence/{card}/confirm"),
    "correct_card": ("post", "/api/evidence/{card}/correct"),
    "reject_card": ("post", "/api/evidence/{card}/reject"),
    "request_revision": ("post", "/api/evidence/{card}/request_revision"),
    "export_credential": ("get", "/api/export/credential/{card}"),
    "reset_demo": ("post", "/api/demo/reset"),
}


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


def _draft(client, headers=None):
    r = client.post("/api/evidence/draft", json={
        "task": TASK, "host_notes": "Imran worked 5 hours.",
        "attendance_rows": [{"volunteer_id": "v-068", "task_id": "task-01", "hours": 5}],
        "assignments": [{"role_id": "role-01", "volunteer_id": "v-068", "volunteer_name": "Imran B."}],
    }, headers=headers or {})
    return r


@pytest.mark.parametrize("role", capabilities.DEMO_ROLES)
def test_menu_matches_the_matrix_for_each_role(client, role):
    r = client.get("/api/capabilities", params={"role": role})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["role"] == role
    assert body["screens"] == list(capabilities.CAPABILITIES[role]["screens"])
    assert body["actions"] == list(capabilities.CAPABILITIES[role]["actions"])
    assert body["demo_only"] is True
    assert "not authentication" in body["note"]


def test_default_role_is_organiser(client):
    default = client.get("/api/capabilities")
    organiser = client.get("/api/capabilities", params={"role": "organiser"})
    assert default.status_code == 200
    assert default.json()["role"] == "organiser"
    assert default.json() == organiser.json()
    assert capabilities.DEFAULT_ROLE == "organiser"


def test_role_name_is_case_and_space_insensitive(client):
    assert client.get("/api/capabilities", params={"role": "  HOST "}).json()["role"] == "host"


def test_unknown_role_is_422_and_names_the_choices(client):
    r = client.get("/api/capabilities", params={"role": "admin"})
    assert r.status_code == 422
    assert "admin" in r.json()["detail"]
    assert "organiser" in r.json()["detail"]


def test_matrix_invariants():
    """The product story, asserted: host confirms, viewer only reads, organiser runs everything."""
    assert set(capabilities.MUTATING_ACTIONS) == set(MUTATING_ROUTES), \
        "every mutating action in the matrix must have an enforcement test here"
    for action in capabilities.MUTATING_ACTIONS:
        assert capabilities.may("organiser", action) is True
        assert capabilities.may("viewer", action) is False
        assert capabilities.may("volunteer", action) is False
    assert capabilities.may("host", "confirm_card") is True
    assert capabilities.may("host", "request_revision") is True
    assert capabilities.may("host", "draft_cards") is False          # drafting is the organiser/system step
    assert capabilities.may("host", "reset_demo") is False           # only the organiser may wipe the demo
    assert capabilities.may("viewer", "read_eval") is True
    assert capabilities.may("viewer", "read_cards") is False
    for role, entry in capabilities.CAPABILITIES.items():
        assert set(entry["actions"]) <= set(capabilities.CAPABILITIES["organiser"]["actions"]), role
        assert "capabilities" in entry["screens"]


def test_no_header_keeps_the_old_behaviour(client):
    """Default organiser: the routes behave exactly as before for clients that send no header."""
    r = _draft(client)
    assert r.status_code == 200, r.text
    card = r.json()[0]
    assert client.post(f"/api/evidence/{card['id']}/confirm", json={"actor": "host"}).status_code == 200
    assert client.get(f"/api/export/credential/{card['id']}").status_code == 200


@pytest.mark.parametrize("action", sorted(MUTATING_ROUTES))
@pytest.mark.parametrize("role", ["viewer", "volunteer"])
def test_read_only_roles_are_403_on_every_mutating_route(client, role, action):
    card = _draft(client).json()[0]                                  # organiser drafts without a header
    method, path = MUTATING_ROUTES[action]
    body = {"reason": "why", "claimed_hours": 4}
    call = getattr(client, method)
    r = call(path.format(card=card["id"]), json=body, headers={"X-Demo-Role": role}) if method == "post" \
        else call(path.format(card=card["id"]), headers={"X-Demo-Role": role})
    assert r.status_code == 403, r.text
    assert role in r.json()["detail"] and "not authentication" in r.json()["detail"]
    assert client.get("/api/evidence/cards").json()[0]["status"] == "draft"   # nothing moved


def test_host_may_confirm_but_may_not_draft(client):
    card = _draft(client).json()[0]
    r = client.post(f"/api/evidence/{card['id']}/confirm", json={"actor": "host-anita"},
                    headers={"X-Demo-Role": "host"})
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "confirmed"
    assert client.get("/api/ledger").json()[-1]["actor"] == "host-anita"

    r = _draft(client, headers={"X-Demo-Role": "host"})
    assert r.status_code == 403
    assert "draft_cards" in r.json()["detail"]


def test_host_may_export_a_confirmed_card(client):
    card = _draft(client).json()[0]
    assert client.post(f"/api/evidence/{card['id']}/confirm", json={"actor": "host"}).status_code == 200
    r = client.get(f"/api/export/credential/{card['id']}", headers={"X-Demo-Role": "host"})
    assert r.status_code == 200, r.text
    assert r.json()["credentialSubject"]["achievement"]["name"]


def test_only_the_organiser_may_reset_the_demo(client):
    """The destructive route is inside the same matrix as the evidence routes."""
    _draft(client)
    for role in ("host", "viewer", "volunteer"):
        r = client.post("/api/demo/reset", headers={"X-Demo-Role": role})
        assert r.status_code == 403, role
        assert "not authentication" in r.json()["detail"]
    assert client.get("/api/evidence/cards").json()                   # nothing was archived or wiped
    assert client.post("/api/demo/reset").status_code == 200          # default organiser keeps working


def test_unknown_header_role_is_403_and_says_why(client):
    card = _draft(client).json()[0]
    r = client.post(f"/api/evidence/{card['id']}/confirm", json={}, headers={"X-Demo-Role": "root"})
    assert r.status_code == 403
    assert "root" in r.json()["detail"] and "demo role switch" in r.json()["detail"]


def test_header_role_is_case_insensitive(client):
    card = _draft(client).json()[0]
    r = client.post(f"/api/evidence/{card['id']}/confirm", json={}, headers={"X-Demo-Role": " HOST "})
    assert r.status_code == 200
