"""B3: the public-demo boundary and plan-versioned share snapshots (SYNTHETIC data, no network).

Three groups of assertions:

1. Gate OFF (the local default) changes nothing: no token needed anywhere.
2. Gate ON (``SEWA_PUBLIC_DEMO=1``): every mutating route needs ``X-Operator-Token`` equal to
   ``SEWA_OPERATOR_TOKEN``, the personal-data reads need it too, the public reads do not, and a
   ``X-Demo-Role`` header can never grant what the token does not. A missing configured token fails closed.
3. Share snapshots are plan-versioned: ``plan_version`` + ``computed_at`` are stored, a dropout refreshes the
   snapshot and makes it ``stale``, and ``GET /api/drive/status`` reports the last verdict per task id without
   running the solver or changing any state.
"""
from __future__ import annotations

import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from app import demo_mode, main, share
from app.llm import extract
from app.llm.client import LLMError
from app.schemas import RoleSpec, TaskSpec

TOKEN = "operator-token-for-tests"
SHARE_SECRET = "test-only-share-secret-value"


def _solvable(task_id: str, title: str) -> dict:
    """A task built from a real synthetic volunteer, so the planner really assigns someone.

    The share snapshot is only stored for a task id the server knows, so this body is also what the server
    holds for that id - the plan under test and the plan the server would solve are the same plan.
    """
    for v in main.volunteers():
        if v.is_minor or not v.skills or not v.available_slots:
            continue
        return {"id": task_id, "title": title, "slot": v.available_slots[0], "district": v.district,
                "block": v.block, "lat": v.lat, "lon": v.lon, "max_travel_km": 25,
                "roles": [{"id": "role-01", "role": "First aid", "count": 1,
                           "required_skills": [sorted(v.skills)[0]]}]}
    raise AssertionError("no usable synthetic volunteer")


TASK = _solvable("task-01", "Clean-up drive")
OTHER_TASK = _solvable("task-02", "Plantation drive")

AUTH = {demo_mode.TOKEN_HEADER: TOKEN}

MUTATING_ROUTES = {
    "roster": ("post", "/api/roster", {"task": TASK}),
    "why_not": ("post", "/api/roster/why-not", {"task": TASK, "roster": None, "volunteer_id": "v-068"}),
    "dropout": ("post", "/api/roster/dropout", {"task": TASK, "roster": None, "dropped_volunteer_id": "v-068"}),
    "draft": ("post", "/api/evidence/draft", {"task": TASK, "host_notes": "Imran worked 5 hours.",
                                              "attendance_rows": [{"volunteer_id": "v-068", "task_id": "task-01",
                                                                   "hours": 5}],
                                              "assignments": [{"role_id": "role-01", "volunteer_id": "v-068",
                                                               "volunteer_name": "Imran B."}]}),
    "extract": ("post", "/api/extract-roles", {"brief_text": ""}),
    "confirm": ("post", "/api/evidence/{card}/confirm", {}),
    "correct": ("post", "/api/evidence/{card}/correct", {"claimed_hours": 4}),
    "reject": ("post", "/api/evidence/{card}/reject", {}),
    "request_revision": ("post", "/api/evidence/{card}/request_revision", {"reason": "check the sheet"}),
    "export": ("get", "/api/export/credential/{card}", None),
    "share": ("post", "/api/drive/share", {"task_id": "task-01"}),
    "reset": ("post", "/api/demo/reset", {}),
}

PRIVATE_READS = ("/api/evidence/cards", "/api/ledger", "/api/ledger/verify", "/api/volunteers")
PUBLIC_READS = ("/api/tasks", "/api/eval", "/api/geo/tree", "/api/capabilities", "/api/drive/status")


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DATA_DIR", tmp_path)
    monkeypatch.setattr(main, "CARDS_PATH", tmp_path / "cards.json")
    monkeypatch.delenv("SEWA_LEDGER_PATH", raising=False)
    monkeypatch.setenv("SEWA_SHARE_SECRET", SHARE_SECRET)
    monkeypatch.setattr(main.S, "tasks", [
        TaskSpec(**{**TASK, "roles": [RoleSpec(**r) for r in TASK["roles"]]}),
        TaskSpec(**{**OTHER_TASK, "roles": [RoleSpec(**r) for r in OTHER_TASK["roles"]]}),
    ])
    main.S.cards, main.S.ledger = None, None
    main.S.share_snapshots, main.S.latest_plan, main.S.attendance_rows = {}, {}, None
    share.reset_secret()
    monkeypatch.delenv(demo_mode.PUBLIC_DEMO_ENV, raising=False)
    monkeypatch.delenv(demo_mode.OPERATOR_TOKEN_ENV, raising=False)

    def down(*a, **k):
        raise LLMError("offline test: deterministic fallback parser")
    monkeypatch.setattr(extract.client, "complete_json", down)
    yield TestClient(main.app)
    main.S.cards, main.S.ledger = None, None
    main.S.share_snapshots, main.S.latest_plan = None, None
    share.reset_secret()


@pytest.fixture()
def demo(client, monkeypatch):
    monkeypatch.setenv(demo_mode.PUBLIC_DEMO_ENV, "1")
    monkeypatch.setenv(demo_mode.OPERATOR_TOKEN_ENV, TOKEN)
    return client


def _draft(client, headers=None):
    return client.post("/api/evidence/draft", json=MUTATING_ROUTES["draft"][2], headers=headers or {})


def _call(client, action, card_id="x", headers=None):
    method, path, body = MUTATING_ROUTES[action]
    url = path.format(card=card_id)
    call = getattr(client, method)
    kwargs = {"headers": headers or {}}
    return call(url, json=body, **kwargs) if body is not None else call(url, **kwargs)


# ---------------- 1. gate off: unchanged ----------------


def test_gate_is_off_by_default(client, monkeypatch):
    assert demo_mode.public_demo_enabled() is False
    assert client.get("/api/volunteers").status_code == 200
    assert client.get("/api/ledger").status_code == 200
    assert client.get("/api/evidence/cards").status_code == 200
    assert _draft(client).status_code == 200
    assert client.post("/api/demo/reset").status_code == 200
    assert client.get("/api/health").json()["public_demo"] is False


@pytest.mark.parametrize("value", ["0", "false", "", "no", "off"])
def test_a_falsy_value_keeps_the_gate_off(client, monkeypatch, value):
    monkeypatch.setenv(demo_mode.PUBLIC_DEMO_ENV, value)
    assert demo_mode.public_demo_enabled() is False
    assert client.get("/api/volunteers").status_code == 200


@pytest.mark.parametrize("value", ["1", "true", "YES", " on "])
def test_truthy_values_turn_the_gate_on(client, monkeypatch, value):
    monkeypatch.setenv(demo_mode.PUBLIC_DEMO_ENV, value)
    monkeypatch.setenv(demo_mode.OPERATOR_TOKEN_ENV, TOKEN)
    assert demo_mode.public_demo_enabled() is True
    assert client.get("/api/volunteers").status_code == 403


# ---------------- 2. gate on: 403s, token success, role never grants ----------------


@pytest.mark.parametrize("action", sorted(MUTATING_ROUTES))
def test_every_mutating_route_needs_the_operator_token(demo, action):
    card = _draft(demo, headers=AUTH).json()[0]
    r = _call(demo, action, card_id=card["id"])
    assert r.status_code == 403, (action, r.text)
    assert demo_mode.TOKEN_HEADER in r.json()["detail"]
    assert "simulation" in r.json()["detail"].lower()      # says the role header cannot grant it


@pytest.mark.parametrize("action", sorted(set(MUTATING_ROUTES) - {"reset", "why_not", "dropout"}))
def test_a_wrong_token_is_403_too(demo, action):
    card = _draft(demo, headers=AUTH).json()[0]
    r = _call(demo, action, card_id=card["id"], headers={demo_mode.TOKEN_HEADER: "not-the-token"})
    assert r.status_code == 403


def test_the_full_evidence_flow_works_with_the_token(demo):
    r = _draft(demo, headers=AUTH)
    assert r.status_code == 200, r.text
    card = r.json()[0]
    assert demo.post(f"/api/evidence/{card['id']}/confirm", json={"actor": "host"}, headers=AUTH).status_code == 200
    assert demo.get(f"/api/export/credential/{card['id']}", headers=AUTH).status_code == 200
    assert demo.get("/api/evidence/cards", headers=AUTH).json()[0]["status"] == "confirmed"
    assert demo.get("/api/ledger", headers=AUTH).json()
    assert demo.get("/api/ledger/verify", headers=AUTH).json()["ok"] is True
    assert demo.get("/api/volunteers", headers=AUTH).status_code == 200
    assert demo.post("/api/drive/share", json={"task_id": "task-01"}, headers=AUTH).status_code == 200
    assert demo.post("/api/roster", json={"task": TASK}, headers=AUTH).status_code == 200
    assert demo.post("/api/demo/reset", headers=AUTH).status_code == 200


@pytest.mark.parametrize("path", PRIVATE_READS)
def test_private_reads_are_403_without_the_token(demo, path):
    r = demo.get(path)
    assert r.status_code == 403, (path, r.text)
    assert demo_mode.TOKEN_HEADER in r.json()["detail"]


@pytest.mark.parametrize("path", PUBLIC_READS)
def test_public_reads_stay_public(demo, path):
    r = demo.get(path)
    assert r.status_code == 200, (path, r.text)


def test_the_public_drive_summary_stays_public(demo):
    key = share.share_key_for("task-01")
    r = demo.get(f"/api/drive/{key}")
    assert r.status_code == 200, r.text
    assert "volunteer_name" not in r.text


@pytest.mark.parametrize("role", ["organiser", "host"])
def test_the_demo_role_can_never_grant_what_the_token_does_not(demo, role):
    r = demo.post("/api/evidence/draft", json=MUTATING_ROUTES["draft"][2], headers={"X-Demo-Role": role})
    assert r.status_code == 403
    assert demo_mode.TOKEN_HEADER in r.json()["detail"]
    assert demo.get("/api/volunteers", headers={"X-Demo-Role": "organiser"}).status_code == 403


def test_the_token_does_not_grant_a_role(demo):
    """Both gates apply: a valid token with a read-only demo role is still refused on a mutating route."""
    card = _draft(demo, headers=AUTH).json()[0]
    r = demo.post(f"/api/evidence/{card['id']}/confirm", json={}, headers={**AUTH, "X-Demo-Role": "viewer"})
    assert r.status_code == 403
    assert "viewer" in r.json()["detail"] and "demo role switch" in r.json()["detail"]


def test_a_missing_configured_token_fails_closed(client, monkeypatch):
    """Public-demo mode on, SEWA_OPERATOR_TOKEN unset: refuse everything rather than let anyone in."""
    monkeypatch.setenv(demo_mode.PUBLIC_DEMO_ENV, "1")
    monkeypatch.delenv(demo_mode.OPERATOR_TOKEN_ENV, raising=False)
    r = client.get("/api/volunteers", headers={demo_mode.TOKEN_HEADER: ""})
    assert r.status_code == 403
    assert demo_mode.OPERATOR_TOKEN_ENV in r.json()["detail"]
    assert client.post("/api/demo/reset").status_code == 403
    assert client.get("/api/tasks").status_code == 200          # the public routes still work


def test_token_comparison_is_exact(client, monkeypatch):
    monkeypatch.setenv(demo_mode.OPERATOR_TOKEN_ENV, TOKEN)
    assert demo_mode.token_matches(TOKEN) is True
    assert demo_mode.token_matches(TOKEN + " ") is False
    assert demo_mode.token_matches(TOKEN.upper()) is False
    assert demo_mode.token_matches(None) is False
    assert demo_mode.token_matches("") is False


@pytest.mark.parametrize("value", ["production", "enabled", "2", "1.0", "yes1"])
def test_an_unrecognised_switch_value_fails_closed(client, monkeypatch, value):
    """A typo in SEWA_PUBLIC_DEMO must not publish an open demo (reviewer finding: it failed open)."""
    monkeypatch.setenv(demo_mode.PUBLIC_DEMO_ENV, value)
    monkeypatch.setenv(demo_mode.OPERATOR_TOKEN_ENV, TOKEN)
    assert demo_mode.public_demo_enabled() is True
    assert client.get("/api/volunteers").status_code == 403
    assert client.get("/api/volunteers", headers=AUTH).status_code == 200


def test_duplicate_operator_token_headers_are_refused(demo):
    """Two occurrences of the header are ambiguous (a proxy may validate a different one): refuse them."""
    r = demo.get("/api/ledger", headers=[(demo_mode.TOKEN_HEADER, TOKEN), (demo_mode.TOKEN_HEADER, "nope")])
    assert r.status_code == 403
    assert "duplicate" in r.json()["detail"]
    r = demo.get("/api/ledger", headers=[(demo_mode.TOKEN_HEADER, TOKEN), (demo_mode.TOKEN_HEADER, TOKEN)])
    assert r.status_code == 403


def test_a_configured_token_is_compared_as_written(client, monkeypatch):
    """A token configured with surrounding spaces is used exactly as written, not silently trimmed."""
    spaced = "  spaced-token  "
    monkeypatch.setenv(demo_mode.OPERATOR_TOKEN_ENV, spaced)
    monkeypatch.setenv(demo_mode.PUBLIC_DEMO_ENV, "1")
    assert demo_mode.token_matches(spaced) is True
    assert demo_mode.token_matches(spaced.strip()) is False
    assert client.get("/api/ledger", headers={demo_mode.TOKEN_HEADER: spaced}).status_code == 200


def test_extract_roles_is_gated_even_when_the_gate_fails_closed(client, monkeypatch):
    """Reviewer finding: POST /api/extract-roles was ungated - it spends the model budget and writes a cache."""
    monkeypatch.setenv(demo_mode.PUBLIC_DEMO_ENV, "1")
    monkeypatch.delenv(demo_mode.OPERATOR_TOKEN_ENV, raising=False)
    r = client.post("/api/extract-roles", json={"brief_text": ""})
    assert r.status_code == 403
    assert demo_mode.TOKEN_HEADER in r.json()["detail"]


# ---------------- 3. plan-versioned snapshots + drive status ----------------


def test_roster_run_stores_a_plan_version_and_timestamp(client):
    key = share.share_key_for("task-01")
    assert client.get(f"/api/drive/{key}").json()["plan_version"] == ""

    roster = client.post("/api/roster", json={"task": TASK}).json()["cp_sat"]
    body = client.get(f"/api/drive/{key}").json()
    assert len(body["plan_version"]) == 64                      # a sha256 hex digest
    assert body["computed_at"] and body["ready"] is not None
    assert body["stale"] is False                               # the snapshot IS the latest solved plan
    assert main.latest_plan()["task-01"] == body["plan_version"]

    # the version really is a digest of this plan (roles + crew), so a different crew is a different version
    from app.schemas import RosterOptions, RosterResult
    same = share.plan_version([RoleSpec(**r) for r in TASK["roles"]], RosterOptions(),
                             *share.roster_fingerprint(RosterResult.model_validate(roster)))
    assert same == body["plan_version"]


def test_a_dropout_refreshes_the_snapshot_and_marks_it_stale(client):
    key = share.share_key_for("task-01")
    roster = client.post("/api/roster", json={"task": TASK}).json()["cp_sat"]
    assert roster["assignments"], "this test needs a solved roster"
    before = client.get(f"/api/drive/{key}").json()
    assert before["stale"] is False

    dropped = roster["assignments"][0]["volunteer_id"]
    r = client.post("/api/roster/dropout", json={"task": TASK, "roster": roster, "dropped_volunteer_id": dropped})
    assert r.status_code == 200, r.text

    after = client.get(f"/api/drive/{key}").json()
    assert after["stale"] is True                               # the healed crew is a different plan
    assert after["plan_version"] != before["plan_version"]
    assert after["computed_at"] >= before["computed_at"]        # the snapshot was refreshed, not left behind
    assert after["ready"] == r.json()["roster_after"]["ready"]  # the verdict is the healed roster's verdict
    assert main.latest_plan()["task-01"] == before["plan_version"]   # the organiser's last solved plan


def test_re_solving_the_roster_clears_staleness(client):
    key = share.share_key_for("task-01")
    roster = client.post("/api/roster", json={"task": TASK}).json()["cp_sat"]
    client.post("/api/roster/dropout", json={"task": TASK, "roster": roster,
                                            "dropped_volunteer_id": roster["assignments"][0]["volunteer_id"]})
    assert client.get(f"/api/drive/{key}").json()["stale"] is True

    client.post("/api/roster", json={"task": TASK})
    assert client.get(f"/api/drive/{key}").json()["stale"] is False


def test_drive_status_lists_every_known_task_with_nulls_before_any_plan(client):
    body = client.get("/api/drive/status").json()
    assert [row["task_id"] for row in body["tasks"]] == ["task-01", "task-02"]
    assert all(row["ready"] is None and row["computed_at"] is None for row in body["tasks"])
    assert "never runs the planner" in body["note"].lower()


def test_drive_status_reports_the_last_verdict_and_changes_nothing(client, tmp_path):
    client.post("/api/roster", json={"task": TASK})
    cards_before = (tmp_path / "cards.json").read_bytes() if (tmp_path / "cards.json").exists() else None
    ledger_before = len(client.get("/api/ledger").json())
    snapshots_before = {k: v.model_dump() for k, v in main.share_snapshots().items()}
    plans_before = dict(main.latest_plan())

    first = client.get("/api/drive/status").json()
    second = client.get("/api/drive/status").json()             # idempotent: a read, not a solve
    assert first == second

    row = next(r for r in first["tasks"] if r["task_id"] == "task-01")
    snapshot = main.share_snapshots()["task-01"]
    assert row["ready"] == snapshot.ready
    assert datetime.fromisoformat(row["computed_at"]) == snapshot.computed_at
    assert row["stale"] is False

    # nothing moved: same ledger, same snapshot, same plan registry, no new cards file
    assert len(client.get("/api/ledger").json()) == ledger_before
    assert {k: v.model_dump() for k, v in main.share_snapshots().items()} == snapshots_before
    assert dict(main.latest_plan()) == plans_before
    assert ((tmp_path / "cards.json").read_bytes() if (tmp_path / "cards.json").exists() else None) == cards_before


def test_drive_status_marks_a_task_stale_after_a_dropout(client):
    key = share.share_key_for("task-01")
    roster = client.post("/api/roster", json={"task": TASK}).json()["cp_sat"]
    client.post("/api/roster/dropout", json={"task": TASK, "roster": roster,
                                            "dropped_volunteer_id": roster["assignments"][0]["volunteer_id"]})
    row = next(r for r in client.get("/api/drive/status").json()["tasks"] if r["task_id"] == "task-01")
    assert row["stale"] is True
    assert row["ready"] == client.get(f"/api/drive/{key}").json()["ready"]


def test_plan_version_is_keyed_so_the_public_summary_is_not_a_membership_oracle(client, monkeypatch):
    """The published version must be useless to someone who can only see the public body.

    A bare SHA-256 over roles + crew could be brute-forced from the published roles (sequential volunteer
    ids), telling an outsider who is on the drive. Keyed with the share secret it cannot be recomputed
    without that secret, so the reviewer's oracle attack no longer works - while staleness still compares
    versions minted inside this process.
    """
    from app.schemas import RosterOptions, RosterResult

    key = share.share_key_for("task-01")
    roster = client.post("/api/roster", json={"task": TASK}).json()["cp_sat"]
    published = client.get(f"/api/drive/{key}").json()["plan_version"]

    roles = [RoleSpec(**r) for r in TASK["roles"]]
    crew = share.roster_fingerprint(RosterResult.model_validate(roster))
    assert share.plan_version(roles, RosterOptions(), *crew) == published          # reproducible in-process
    assert share.plan_version(roles, RosterOptions(), *crew, secret=b"guess") != published   # not without it

    monkeypatch.setenv("SEWA_SHARE_SECRET", "a-rotated-secret")
    share.reset_secret()
    assert share.plan_version(roles, RosterOptions(), *crew) != published          # rotation re-keys versions


def test_plan_version_is_deterministic_and_sensitive():
    roles = [RoleSpec(id="role-02", role="Poster", count=1, required_skills=["graphic_design"]),
             RoleSpec(id="role-01", role="First aid", count=2, required_skills=["first_aid"])]
    a = share.plan_version(roles, None, ["role-01:0:v-068"], [])
    b = share.plan_version(list(reversed(roles)), None, ["role-01:0:v-068"], [])
    assert a == b                                               # order of roles does not matter
    assert share.plan_version(roles, None, ["role-01:0:v-069"], []) != a      # a different crew is a new plan
    assert share.plan_version(roles, None, [], ["v-069"]) != a                # standby is part of the plan
    roles[0].count = 2
    assert share.plan_version(roles, None, ["role-01:0:v-068"], []) != a      # a role change is a new plan


def test_the_status_route_never_calls_the_solver(client, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("/api/drive/status must not run the solver")
    monkeypatch.setattr(main.solver, "build_roster", boom)
    monkeypatch.setattr(main.solver, "baseline_nearest_skill", boom)
    monkeypatch.setattr(main.solver, "baseline_random_feasible", boom)
    monkeypatch.setattr(main.solver, "baseline_manual_greedy", boom)
    assert client.get("/api/drive/status").status_code == 200
    failing = TestClient(main.app, raise_server_exceptions=False)
    assert failing.post("/api/roster", json={"task": TASK}).status_code == 500   # the guard proves it would run
