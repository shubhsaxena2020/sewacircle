import pytest
from fastapi.testclient import TestClient

from app import main
from app.llm.client import LLMError, extract_json
from app.main import app
from app.schemas import AttendanceRow, ExtractedRole, RoleSpec, TaskSpec, Volunteer
from app.taxonomy import SKILLS, SLOTS

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["ok"] is True


def test_meta_has_24_skills():
    assert len(client.get("/api/meta").json()["skills"]) == 24 == len(SKILLS)


def _vol(**kw):
    base = dict(id="v-001", display_name="Vol A", age=20, district="Kanpur Dehat", block="Bilhaur", lat=26.8, lon=80.1,
                skills={"first_aid": 2}, available_slots=["sat_morning"])
    base.update(kw)
    return Volunteer(**base)


def test_volunteer_validation():
    v = _vol()
    assert not v.is_minor and v.is_novice
    for bad in (dict(skills={"nope": 1}), dict(available_slots=["someday"]), dict(lat=95), dict(lon=181), dict(past_drives=-1)):
        with pytest.raises(Exception):
            _vol(**bad)


def test_rolespec_and_slot_validation():
    with pytest.raises(Exception):
        RoleSpec(id="role-01", role="x", count=0)
    with pytest.raises(Exception):
        RoleSpec(id="role-01", role="x", count=1, required_skills=["not_a_skill"])
    with pytest.raises(Exception):
        ExtractedRole(role="x", count=1, required_skills=["not_a_skill"])
    assert RoleSpec(id="role-01", role="open", count=1).required_skills == []  # empty = open to all
    with pytest.raises(Exception):
        TaskSpec(id="task-01", title="t", slot="whenever", district="d", block="b", lat=0, lon=0)
    assert "sat_morning" in SLOTS


def test_attendance_row_is_recorded_hours_and_bounded():
    assert AttendanceRow(volunteer_id="v-001", task_id="task-01", hours=5).hours == 5
    for bad in (-1, 25):
        with pytest.raises(Exception):
            AttendanceRow(volunteer_id="v-001", task_id="task-01", hours=bad)


@pytest.mark.parametrize("path", ["/api/volunteers", "/api/tasks", "/api/ledger", "/api/ledger/verify", "/api/eval", "/api/evidence/cards"])
def test_endpoints_never_500(path):
    """Lane modules may still be unimplemented (501) or implemented (200); an unhandled 500 is always a bug."""
    assert client.get(path).status_code in (200, 501)


def test_llm_error_maps_to_502_with_manual_hint(monkeypatch):
    def boom(*a, **k):
        raise LLMError("gateway down")
    monkeypatch.setattr(main.llm_extract, "extract_roles", boom)
    r = client.post("/api/extract-roles", json={"brief_text": "x"})
    assert r.status_code == 502 and r.json()["code"] == "llm_unavailable"


def test_cors_is_an_allowlist_not_wildcard():
    assert "*" not in main._origins


def test_extract_json_tolerant():
    assert extract_json('```json\n{"a":1}\n```') == {"a": 1}
    assert extract_json('Here you go: {"a":[1,2]} thanks') == {"a": [1, 2]}
    with pytest.raises(LLMError):
        extract_json(None)
    with pytest.raises(LLMError):
        extract_json("no json here")
