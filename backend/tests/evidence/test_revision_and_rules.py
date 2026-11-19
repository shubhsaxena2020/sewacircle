"""B2: revision semantics and the rules re-check on `correct` (SYNTHETIC data, no network).

Two behaviours are pinned here:

* ``correct`` re-runs the deterministic rules on the corrected card and STORES the new flags. A host who
  raises the hours above the recorded sheet must see ``hours_exceed_recorded`` on the card they just
  corrected; if they lower it back, the flag must be gone. The status stays ``corrected`` - the decision is
  the host's, the flags are evidence.
* Empty drafting is non-destructive. If the drafting step returns no card while assignments were sent, the
  route answers HTTP 502 and leaves the card store and the journal byte-identical; with no assignments it
  answers an empty list and still removes nothing. A failed draft must never wipe cards a host is reviewing.
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


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DATA_DIR", tmp_path)
    monkeypatch.setattr(main, "CARDS_PATH", tmp_path / "cards.json")
    monkeypatch.delenv("SEWA_LEDGER_PATH", raising=False)
    main.S.cards, main.S.ledger = None, None
    main.S.attendance_rows = None

    def down(*a, **k):
        raise LLMError("offline test: deterministic fallback parser")
    monkeypatch.setattr(extract.client, "complete_json", down)
    yield TestClient(main.app)
    main.S.cards, main.S.ledger = None, None
    main.S.attendance_rows = None


def _draft(client, claimed=5.0, recorded=5.0, volunteer="v-068", name="Imran B."):
    r = client.post("/api/evidence/draft", json={
        "task": TASK, "host_notes": f"{name} worked {claimed:g} hours.",
        "attendance_rows": [{"volunteer_id": volunteer, "task_id": "task-01", "hours": recorded}],
        "assignments": [{"role_id": "role-01", "volunteer_id": volunteer, "volunteer_name": name}],
    })
    assert r.status_code == 200, r.text
    return r.json()[0]


def _codes(card) -> list[str]:
    return [f["code"] for f in card["flags"]]


# ---------------- correct re-runs the rules ----------------

def test_correct_above_the_recorded_hours_stores_the_warning(client):
    card = _draft(client, claimed=5.0, recorded=5.0)
    assert "hours_exceed_recorded" not in _codes(card)

    r = client.post(f"/api/evidence/{card['id']}/correct", json={"claimed_hours": 9, "actor": "host-anita"})
    assert r.status_code == 200, r.text
    corrected = r.json()
    assert corrected["status"] == "corrected"
    assert corrected["claimed_hours"] == 9
    assert "hours_exceed_recorded" in _codes(corrected)
    assert "9" in next(f["message"] for f in corrected["flags"] if f["code"] == "hours_exceed_recorded")

    stored = client.get("/api/evidence/cards").json()[0]      # the flags are persisted, not just returned
    assert "hours_exceed_recorded" in _codes(stored)
    assert stored["status"] == "corrected"
    assert client.get("/api/ledger/verify").json()["ok"] is True


def test_correct_back_down_clears_the_warning(client):
    card = _draft(client, claimed=9.0, recorded=5.0)
    assert card["status"] == "flagged" and "hours_exceed_recorded" in _codes(card)

    r = client.post(f"/api/evidence/{card['id']}/correct", json={"claimed_hours": 5})
    assert r.status_code == 200, r.text
    assert "hours_exceed_recorded" not in _codes(r.json())    # re-run on the new number, so it is gone
    assert "hours_exceed_recorded" not in _codes(client.get("/api/evidence/cards").json()[0])


def test_correct_to_an_implausible_number_stores_the_block_flag(client):
    card = _draft(client)
    r = client.post(f"/api/evidence/{card['id']}/correct", json={"claimed_hours": 14})
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "corrected"                  # the host may still correct; the flag is the warning
    assert "implausible_hours" in _codes(r.json())
    assert any(f["code"] == "implausible_hours" and f["severity"] == "block" for f in r.json()["flags"])


def test_correct_falls_back_to_the_cards_recorded_hours_after_a_restart(client, tmp_path):
    """The attendance sheet cache is process-local; the persisted recorded_hours on the card is enough."""
    card = _draft(client, claimed=5.0, recorded=5.0)
    main.S.attendance_rows = None                              # simulate a restart: no cached sheet
    r = client.post(f"/api/evidence/{card['id']}/correct", json={"claimed_hours": 8})
    assert r.status_code == 200, r.text
    assert "hours_exceed_recorded" in _codes(r.json())


def test_correct_still_needs_hours(client):
    card = _draft(client)
    assert client.post(f"/api/evidence/{card['id']}/correct", json={}).status_code == 422
    assert client.get("/api/evidence/cards").json()[0]["status"] == "draft"


# ---------------- empty drafting is non-destructive ----------------

def test_an_empty_draft_with_assignments_is_502_and_changes_nothing(client, tmp_path, monkeypatch):
    card = _draft(client)
    assert client.post(f"/api/evidence/{card['id']}/request_revision", json={"reason": "wrong hours"}).status_code == 200
    journal = tmp_path / "ledger.jsonl"
    cards_file = tmp_path / "cards.json"
    journal_before, cards_before = journal.read_bytes(), cards_file.read_bytes()

    monkeypatch.setattr(main.llm_extract, "draft_cards", lambda *a, **k: [])
    failing = TestClient(main.app, raise_server_exceptions=False)
    r = failing.post("/api/evidence/draft", json={
        "task": TASK, "host_notes": "Imran worked 5 hours.",
        "attendance_rows": [{"volunteer_id": "v-068", "task_id": "task-01", "hours": 5}],
        "assignments": [{"role_id": "role-01", "volunteer_id": "v-068", "volunteer_name": "Imran B."}]})

    assert r.status_code == 502, r.text
    assert "nothing was changed" in r.json()["detail"]
    assert journal.read_bytes() == journal_before              # no ledger entry
    assert cards_file.read_bytes() == cards_before             # no card removed, none written
    assert [c["status"] for c in failing.get("/api/evidence/cards").json()] == ["revision_requested"]


def test_an_empty_draft_with_no_assignments_keeps_the_undecided_cards(client, monkeypatch):
    """No assignments and no cards drafted: an empty list, not a silent wipe of the undecided pool."""
    card = _draft(client)
    monkeypatch.setattr(main.llm_extract, "draft_cards", lambda *a, **k: [])
    r = client.post("/api/evidence/draft", json={"task": TASK, "host_notes": "", "assignments": []})
    assert r.status_code == 200, r.text
    assert r.json() == []
    assert [c["id"] for c in client.get("/api/evidence/cards").json()] == [card["id"]]


def test_a_non_empty_draft_still_supersedes_the_stale_card(client):
    """The guard must not disable the real supersede path: a different volunteer replaces the stale card."""
    _draft(client)                                            # v-068
    second = _draft(client, volunteer="v-069", name="Sunita K.")
    assert [c["volunteer_id"] for c in client.get("/api/evidence/cards").json()] == ["v-069"]
    assert second["status"] == "draft"


def test_a_partial_draft_is_502_and_changes_nothing(client, tmp_path, monkeypatch):
    """A draft that silently drops a rostered volunteer would delete that card via the supersede step."""
    stale = _draft(client)                                     # v-068, undecided
    journal_before = (tmp_path / "ledger.jsonl").read_bytes()
    cards_before = (tmp_path / "cards.json").read_bytes()

    import app.llm.extract as extract_mod
    real = extract_mod.draft_cards

    def one_of_two(*args, **kwargs):
        return real(*args, **kwargs)[:1]                       # pretend the model skipped the second volunteer
    monkeypatch.setattr(main.llm_extract, "draft_cards", one_of_two)

    r = client.post("/api/evidence/draft", json={
        "task": TASK, "host_notes": "Imran worked 5 hours. Sunita worked 4 hours.",
        "attendance_rows": [{"volunteer_id": "v-068", "task_id": "task-01", "hours": 5},
                            {"volunteer_id": "v-069", "task_id": "task-01", "hours": 4}],
        "assignments": [{"role_id": "role-01", "volunteer_id": "v-068", "volunteer_name": "Imran B."},
                        {"role_id": "role-01", "volunteer_id": "v-069", "volunteer_name": "Sunita K."}]})
    assert r.status_code == 502, r.text
    assert "nothing was changed" in r.json()["detail"]
    assert (tmp_path / "ledger.jsonl").read_bytes() == journal_before
    assert (tmp_path / "cards.json").read_bytes() == cards_before
    assert [c["id"] for c in client.get("/api/evidence/cards").json()] == [stale["id"]]


def test_correct_keeps_a_block_flag_only_the_sheet_could_prove(client):
    """After a restart the sheet is gone; a block flag that depends on sheet fields must NOT silently vanish."""
    card = _draft(client, claimed=5.0, recorded=5.0)
    # re-draft the same card with an attendance row that records a minor without consent -> block flag
    rows = [{"volunteer_id": "v-068", "task_id": "task-01", "hours": 5, "age": 16}]
    r = client.post("/api/evidence/draft", json={
        "task": TASK, "host_notes": "Imran worked 5 hours.", "attendance_rows": rows,
        "assignments": [{"role_id": "role-01", "volunteer_id": "v-068", "volunteer_name": "Imran B."}]})
    assert r.status_code == 200, r.text
    assert "minor_without_guardian_consent" in _codes(r.json()[0])

    main.S.attendance_rows = None                       # restart: the sheet is no longer in memory
    corrected = client.post(f"/api/evidence/{card['id']}/correct", json={"claimed_hours": 4})
    assert corrected.status_code == 200, corrected.text
    assert "minor_without_guardian_consent" in _codes(corrected.json())     # kept, not dropped
    assert any(f["code"] == "minor_without_guardian_consent" and f["severity"] == "block"
               for f in corrected.json()["flags"])
