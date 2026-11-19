"""B1: one card, one decision - the atomicity tests (SYNTHETIC data, no network).

Three properties are asserted here, and each one is a real failure mode this route had before:

1. Two hosts act on the SAME card at the SAME moment (confirm vs reject). Exactly one wins, the loser gets
   HTTP 409 and changes nothing, the ledger gains exactly one decision entry, and the chain still verifies.
2. A failed ledger append leaves the card and the journal exactly as they were: no decided card without an
   entry, no half-written cards.json.
3. The card file is replaced atomically (write temp + os.replace), never rewritten in place, and the decision
   is only committed after the append succeeded.

This is a SINGLE-PROCESS guarantee (one threading.RLock). See the app/main.py module docstring.
"""
from __future__ import annotations

import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from app import main
from app.llm import extract
from app.llm.client import LLMError

TASK = {"id": "task-01", "title": "Camp", "slot": "sat_morning", "district": "Lucknow", "block": "Chinhat",
        "lat": 26.8, "lon": 80.9,
        "roles": [{"id": "role-01", "role": "First aid", "count": 1, "required_skills": ["first_aid"]}]}

DECISION_ACTIONS = ("confirm", "correct", "reject", "request_revision")


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


def _draft(client, volunteer="v-068", name="Imran B.", claimed=5.0, recorded=5.0):
    r = client.post("/api/evidence/draft", json={
        "task": TASK,
        "host_notes": f"{name} worked {claimed:g} hours.",
        "attendance_rows": [{"volunteer_id": volunteer, "task_id": "task-01", "hours": recorded}],
        "assignments": [{"role_id": "role-01", "volunteer_id": volunteer, "volunteer_name": name}],
    })
    assert r.status_code == 200, r.text
    return r.json()[0]


@pytest.mark.parametrize("attempt", [1, 2, 3])
def test_simultaneous_confirm_and_reject_give_one_200_and_one_409(client, attempt):
    """A barrier makes both requests leave at the same instant; the lock makes the outcome deterministic."""
    card = _draft(client, volunteer=f"v-06{attempt}", name=f"Imran {attempt}")
    assert card["status"] == "draft"

    barrier = threading.Barrier(2)

    def act(action: str):
        barrier.wait(timeout=10)
        return action, client.post(f"/api/evidence/{card['id']}/{action}", json={"actor": f"host-{action}"})

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = dict(pool.map(act, ("confirm", "reject")))

    statuses = sorted(r.status_code for r in results.values())
    assert statuses == [200, 409], {a: (r.status_code, r.text) for a, r in results.items()}

    winner = next(a for a, r in results.items() if r.status_code == 200)
    loser = next(a for a, r in results.items() if r.status_code == 409)
    assert "illegal transition" in results[loser].json()["detail"]
    assert results[winner].json()["status"] == {"confirm": "confirmed", "reject": "rejected"}[winner]

    # exactly one decision entry for THIS card, and it is the winner's
    decisions = [e for e in client.get("/api/ledger").json()
                 if e["card_id"] == card["id"] and e["action"] in DECISION_ACTIONS]
    assert len(decisions) == 1
    assert decisions[0]["action"] == winner
    assert decisions[0]["actor"] == f"host-{winner}"

    stored = client.get("/api/evidence/cards").json()
    assert len(stored) == 1 and stored[0]["status"] == results[winner].json()["status"]
    assert client.get("/api/ledger/verify").json()["ok"] is True


def test_a_failed_append_leaves_the_card_and_the_journal_unchanged(client, tmp_path, monkeypatch):
    """If the journal cannot be written, the decision must not be committed anywhere."""
    card = _draft(client)
    journal = tmp_path / "ledger.jsonl"
    cards_file = tmp_path / "cards.json"
    journal_before = journal.read_bytes()
    cards_before = cards_file.read_bytes()

    def boom(self, entry):
        raise OSError("disk full (injected)")
    monkeypatch.setattr(main.ledger_mod.Ledger, "_write_entry", boom)

    failing = TestClient(main.app, raise_server_exceptions=False)
    r = failing.post(f"/api/evidence/{card['id']}/confirm", json={"actor": "host"})
    assert r.status_code == 500, r.text

    assert journal.read_bytes() == journal_before               # no entry was added
    assert cards_file.read_bytes() == cards_before              # no card was decided
    assert main.cards()[card["id"]].status == "draft"           # the in-memory store is untouched too
    assert failing.get("/api/evidence/cards").json()[0]["status"] == "draft"
    assert failing.get("/api/ledger/verify").json()["ok"] is True


def test_the_card_file_is_replaced_atomically_and_only_after_the_append(client, tmp_path, monkeypatch):
    """The commit order is append -> store -> rename, and the rename goes through os.replace on a temp file."""
    card = _draft(client)
    calls: list[tuple[str, str]] = []
    real_replace = os.replace

    def record_replace(src, dst):
        calls.append((str(src), str(dst)))
        return real_replace(src, dst)

    real_append = main.ledger().append

    def record_append(action, c, actor, reason=""):
        calls.append(("append", action))
        return real_append(action, c, actor, reason)

    monkeypatch.setattr(main.os, "replace", record_replace)
    monkeypatch.setattr(main.ledger(), "append", record_append)

    assert client.post(f"/api/evidence/{card['id']}/confirm", json={"actor": "host"}).status_code == 200

    assert ("append", "confirm") in calls
    # os.replace is shared with the ledger's own sidecar, so filter to the card file
    card_replaces = [c for c in calls if c[0] != "append" and c[1] == str(tmp_path / "cards.json")]
    assert len(card_replaces) == 1, calls
    temp_path, target = card_replaces[0]
    assert temp_path != target and temp_path.endswith(".tmp")
    assert calls.index(("append", "confirm")) < calls.index(card_replaces[0])

    # no temp files left behind, and the file on disk is valid JSON with the new status
    assert not list(tmp_path.glob(".cards-*.tmp"))
    stored = json.loads((tmp_path / "cards.json").read_text(encoding="utf-8"))
    assert [c["status"] for c in stored] == ["confirmed"]


def test_an_illegal_second_action_writes_nothing(client, tmp_path):
    """The loser of a race and a plain illegal action are the same path: 409, no entry, no file change."""
    card = _draft(client)
    assert client.post(f"/api/evidence/{card['id']}/confirm", json={}).status_code == 200
    journal_before = (tmp_path / "ledger.jsonl").read_bytes()
    cards_before = (tmp_path / "cards.json").read_bytes()

    r = client.post(f"/api/evidence/{card['id']}/reject", json={})
    assert r.status_code == 409
    assert (tmp_path / "ledger.jsonl").read_bytes() == journal_before
    assert (tmp_path / "cards.json").read_bytes() == cards_before


def test_a_failed_sidecar_write_rolls_the_journal_line_back(client, tmp_path, monkeypatch):
    """A journal line whose sidecar write fails must not survive: otherwise verify() reports tampering and a
    retry appends a SECOND decision entry for one card (the failure mode a reviewer found)."""
    card = _draft(client)
    journal = tmp_path / "ledger.jsonl"
    journal_before = journal.read_bytes()

    def boom(self, count, head_hash):
        raise OSError("sidecar disk full (injected)")
    monkeypatch.setattr(main.ledger_mod.Ledger, "_write_head", boom)

    failing = TestClient(main.app, raise_server_exceptions=False)
    assert failing.post(f"/api/evidence/{card['id']}/confirm", json={"actor": "host"}).status_code == 500
    assert journal.read_bytes() == journal_before                  # the line was rolled back
    assert main.cards()[card["id"]].status == "draft"              # and nothing was committed
    assert failing.get("/api/ledger/verify").json()["ok"] is True   # no phantom entry, no tamper alarm

    monkeypatch.undo()
    retry = client.post(f"/api/evidence/{card['id']}/confirm", json={"actor": "host"})
    assert retry.status_code == 200, retry.text
    decisions = [e for e in client.get("/api/ledger").json()
                 if e["card_id"] == card["id"] and e["action"] in DECISION_ACTIONS]
    assert len(decisions) == 1                                     # exactly one, not one per attempt
    assert client.get("/api/ledger/verify").json()["ok"] is True


def test_demo_reset_cannot_erase_a_decision_that_is_mid_commit(client, tmp_path, monkeypatch):
    """The reset archives the journal, so it must not run between a decision's append and its store commit."""
    card = _draft(client)
    real_save = main._save_cards
    inside = threading.Event()
    release = threading.Event()

    def slow_save():
        inside.set()
        assert release.wait(timeout=10)
        real_save()
    monkeypatch.setattr(main, "_save_cards", slow_save)

    outcomes: dict[str, object] = {}

    def confirm():
        outcomes["confirm"] = client.post(f"/api/evidence/{card['id']}/confirm", json={"actor": "host"})

    def reset():
        outcomes["reset"] = client.post("/api/demo/reset")

    decision = threading.Thread(target=confirm)
    decision.start()
    assert inside.wait(timeout=10), "the decision never reached its file write"

    resetter = threading.Thread(target=reset)
    resetter.start()
    resetter.join(timeout=0.4)
    assert resetter.is_alive(), "demo reset ran while a decision was mid-commit"
    assert not list(tmp_path.glob("archive-*")), "files were archived before the decision finished"

    release.set()
    decision.join(timeout=15)
    resetter.join(timeout=15)

    assert outcomes["confirm"].status_code == 200
    assert outcomes["reset"].status_code == 200
    archived = list(tmp_path.glob("archive-*-ledger.jsonl"))
    assert len(archived) == 1
    actions = [json.loads(line)["action"] for line in archived[0].read_text(encoding="utf-8").splitlines()]
    assert "confirm" in actions                     # the decision exists in the archived history, not lost
    assert client.get("/api/ledger").json() == []    # and the demo is clean afterwards


def test_the_store_is_restored_when_a_draft_fails_mid_commit(client, monkeypatch):
    """A draft that fails after some cards were written leaves the store exactly as it was."""
    first = _draft(client)                                   # one card, committed
    real_append = main.ledger().append
    calls = {"n": 0}

    def fail_second(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] >= 2:
            raise OSError("journal unavailable (injected)")
        return real_append(*args, **kwargs)
    monkeypatch.setattr(main.ledger(), "append", fail_second)

    failing = TestClient(main.app, raise_server_exceptions=False)
    r = failing.post("/api/evidence/draft", json={
        "task": TASK, "host_notes": "Sunita worked 4 hours. Ravi worked 4 hours.",
        "attendance_rows": [{"volunteer_id": "v-069", "task_id": "task-01", "hours": 4},
                            {"volunteer_id": "v-070", "task_id": "task-01", "hours": 4}],
        "assignments": [{"role_id": "role-01", "volunteer_id": "v-069", "volunteer_name": "Sunita K."},
                        {"role_id": "role-01", "volunteer_id": "v-070", "volunteer_name": "Ravi P."}]})
    assert r.status_code == 500
    assert calls["n"] >= 2                                   # the failure happened after a card was written
    assert [c["id"] for c in failing.get("/api/evidence/cards").json()] == [first["id"]]   # nothing replaced
    assert json.loads((main.CARDS_PATH).read_text(encoding="utf-8"))[0]["id"] == first["id"]
