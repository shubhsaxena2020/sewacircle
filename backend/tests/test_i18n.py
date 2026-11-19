"""Contract tests for localized display text (English/Hindi), SYNTHETIC data, no network.

The point of these tests: the Hindi block is a *view*, never a second source of
truth. Ids, counts, the ready verdict and the numbers inside the sentences must be
identical to the canonical English fields; only the words change.
"""
from __future__ import annotations

import re

import pytest
from fastapi.testclient import TestClient

from app import i18n, main
from app.schemas import RoleSpec, TaskSpec

TASK = {"id": "task-01", "title": "Water and hygiene camp", "slot": "sat_morning", "district": "Kanpur Dehat",
        "block": "Akbarpur", "lat": 26.8, "lon": 79.9, "max_travel_km": 25,
        "roles": [{"id": "role-01", "role": "First-aid support", "count": 1, "required_skills": ["first_aid"]},
                  {"id": "role-02", "role": "Team lead", "count": 1, "required_skills": ["team_leadership"]}]}


def _devanagari(text: str) -> bool:
    return any("\u0900" <= ch <= "\u097f" for ch in text)


def _digits(text: str) -> list[str]:
    return re.findall(r"\d+", text)


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DATA_DIR", tmp_path)
    monkeypatch.setattr(main, "CARDS_PATH", tmp_path / "cards.json")
    monkeypatch.delenv("SEWA_LEDGER_PATH", raising=False)
    monkeypatch.setattr(main.S, "share_snapshots", {})
    monkeypatch.setattr(main.S, "cards", None)
    monkeypatch.setattr(main.S, "ledger", None)
    yield TestClient(main.app)
    main.S.cards, main.S.ledger = None, None


def test_task_display_keeps_ids_counts_and_skill_ids(client):
    canonical = {t["id"]: t for t in client.get("/api/tasks").json()}
    for task in client.get("/api/tasks", params={"lang": "hi"}).json():
        base = canonical[task["id"]]
        display = task["display"]
        assert display["lang"] == "hi"
        assert [r["role_id"] for r in display["roles"]] == [r["id"] for r in base["roles"]]
        assert [r["count"] for r in display["roles"]] == [r["count"] for r in base["roles"]]
        assert [[s["id"] for s in r["required_skills"]] for r in display["roles"]] == \
               [r["required_skills"] for r in base["roles"]]
        assert _devanagari(display["title"]) and display["title"] != base["title"]
        assert _devanagari(display["slot"])
        for role in display["roles"]:
            assert _devanagari(role["role"])
            for skill in role["required_skills"]:
                assert _devanagari(skill["label"]) and skill["id"] in base["roles"][0]["required_skills"] + \
                       [s for r in base["roles"] for s in r["required_skills"]]
        # the canonical fields themselves are untouched by the language switch
        assert task["title"] == base["title"] and task["brief_text"] == base["brief_text"]


def test_tasks_default_language_is_english(client):
    for task in client.get("/api/tasks").json():
        assert task["display"]["lang"] == "en"
        assert task["display"]["title"] == task["title"]
        assert task["display"]["slot"] == task["slot"].replace("_", " ")
        assert not _devanagari(task["display"]["title"])


def test_unknown_language_is_422(client):
    assert client.get("/api/tasks", params={"lang": "fr"}).status_code == 422
    assert client.post("/api/roster", json={"task": TASK, "lang": "fr"}).status_code == 422


def _roster(client, lang: str):
    r = client.post("/api/roster", json={"task": TASK, "lang": lang})
    assert r.status_code == 200, r.text
    return r.json()


@pytest.mark.parametrize("method", ["cp_sat", "nearest_skill", "random_feasible", "manual_greedy"])
def test_hindi_roster_display_keeps_verdict_ids_and_numbers(client, method):
    hindi = _roster(client, "hi")[method]
    display = hindi["display"]

    assert display["lang"] == "hi"
    assert display["ready"] == hindi["ready"]                       # the verdict is copied, never re-decided
    assert display["verdict"] == ("तैयार" if hindi["ready"] else "तैयार नहीं")

    assert [q["role_id"] for q in display["recruit"]] == [q["role_id"] for q in hindi["recruit_requests"]]
    assert [q["needed"] for q in display["recruit"]] == [q["needed"] for q in hindi["recruit_requests"]]
    assert [a["volunteer_id"] for a in display["assignments"]] == [a["volunteer_id"] for a in hindi["assignments"]]
    assert [a["role_id"] for a in display["assignments"]] == [a["role_id"] for a in hindi["assignments"]]

    for shown, canonical in zip(display["recruit"], hindi["recruit_requests"]):
        assert _devanagari(shown["text"])
        if shown["role_id"] == canonical["role_id"] and canonical["needed"] > 0:
            assert str(canonical["needed"]) in shown["text"]
        assert f"{canonical['max_travel_km']:.0f}" in shown["text"] or canonical["kind"] != "unfilled"
    for shown in display["assignments"]:
        assert _devanagari(shown["text"])


def test_english_roster_display_mirrors_the_canonical_text(client):
    english = _roster(client, "en")["cp_sat"]
    display = english["display"]
    assert display["lang"] == "en"
    assert display["ready"] == english["ready"]
    assert display["verdict"] == ("READY" if english["ready"] else "NOT READY")
    assert display["explanations"] == english["explanations"]
    assert [q["text"] for q in display["recruit"]] == [q["reason"] for q in english["recruit_requests"]]
    assert all(not _devanagari(t) for t in display["explanations"])


def test_an_unresolved_role_asks_for_a_decision_in_both_languages(client):
    task = {"task": dict(TASK) | {
        "id": "task-99",
        "roles": [{"id": "role-01", "role": "Mystery role", "count": 2, "required_skills": [], "unresolved": True}]}}
    body = {"task": task["task"], "lang": "hi"}
    r = client.post("/api/roster", json=body)
    assert r.status_code == 200, r.text
    result = r.json()["cp_sat"]
    request_row = next(q for q in result["recruit_requests"] if q["kind"] == "unresolved")
    shown = next(q for q in result["display"]["recruit"] if q["role_id"] == request_row["role_id"])
    assert shown["needed"] == request_row["needed"] == 2
    assert "कौशल" in shown["text"] and _devanagari(shown["text"])
    assert str(request_row["role_id"]) not in request_row["reason"].replace(" ", "")  # sanity: ids in display only


def test_hindi_renderings_never_change_the_english_fields(client):
    """Both languages in one response pair: the canonical objects are byte-identical except `display`."""
    hindi = _roster(client, "hi")["cp_sat"]
    english = _roster(client, "en")["cp_sat"]
    assert [(a["volunteer_id"], a["role_id"]) for a in hindi["assignments"]] == \
           [(a["volunteer_id"], a["role_id"]) for a in english["assignments"]]
    assert hindi["ready"] == english["ready"]
    for field in ("role_coverage", "slots_filled", "slots_required", "robustness", "repeat_pick_share",
                  "exposure_gini", "district_spread", "should_coverage", "novices", "mentor_pairs", "solver_status"):
        assert hindi["metrics"][field] == english["metrics"][field], field   # solve_ms is timing, not a decision
    assert [q["role_id"] for q in hindi["recruit_requests"]] == [q["role_id"] for q in english["recruit_requests"]]


def test_hindi_pick_reason_carries_no_number_that_could_disagree(client):
    """The Hindi pick sentence deliberately quotes no distance: Assignment.distance_km is rounded to 1 dp,
    so a kilometre figure there could round differently from the English sentence's raw value."""
    hindi = _roster(client, "hi")["cp_sat"]["display"]["assignments"]
    for shown in hindi:
        assert not _digits(shown["text"]), shown["text"]
        assert _devanagari(shown["text"])


def test_a_robustness_percentage_is_the_same_number_in_both_languages(client):
    english = _roster(client, "en")["cp_sat"]
    hindi = _roster(client, "hi")["cp_sat"]
    english_percent = [n for text in english["explanations"] for n in _digits(text) if "%" in text]
    if english_percent:                                            # only when the English lines quote one
        hindi_text = " ".join(hindi["display"]["explanations"])
        for number in english_percent:
            assert number in _digits(hindi_text)


def test_standby_sentence_uses_the_hindi_role_label():
    role = RoleSpec(id="role-01", role="Health educator", count=1, required_skills=["health_education", "first_aid"])
    text = i18n._recruit_text("standby", role, 1, role.required_skills, True, "sun_morning", "Kashi Vidyapeeth, Varanasi", 25)
    assert i18n.ROLE_LABELS_HI["Health educator"] in text
    assert "Health educator" not in text


def test_unknown_text_is_returned_unchanged_not_machine_translated():
    assert i18n.role_label("Mystery role typed by the organiser", "hi") == "Mystery role typed by the organiser"
    assert i18n.title_label("Some drive", "hi") == "Some drive"
    assert i18n.skill_label("not_a_skill", "hi") == "not_a_skill"
    assert i18n.role_label("Team lead", "hi") == "टीम लीड"
    assert i18n.slot_label("sun_afternoon", "hi") == "रविवार दोपहर"
    assert i18n.skill_label("first_aid", "en") == "First aid / basic medical support"


def test_card_text_is_not_localized(client, monkeypatch):
    """LLM/host-written card text keeps its original language: no display block is attached to cards."""
    from app.llm import extract
    from app.llm.client import LLMError

    def down(*a, **k):
        raise LLMError("offline test")
    monkeypatch.setattr(extract.client, "complete_json", down)
    r = client.post("/api/evidence/draft", json={
        "task": TASK, "host_notes": "Imran worked 5 hours.",
        "attendance_rows": [{"volunteer_id": "v-068", "task_id": "task-01", "hours": 5}],
        "assignments": [{"role_id": "role-01", "volunteer_id": "v-068", "volunteer_name": "Imran B."}]})
    assert r.status_code == 200, r.text
    card = r.json()[0]
    assert "display" not in card
    assert "Imran worked 5 hours." in card["summary"] or "Imran" in card["summary"]
