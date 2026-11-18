import pytest
from fastapi.testclient import TestClient

from app.llm.client import LLMError, extract_json
from app.main import app
from app.schemas import RoleSpec, Volunteer
from app.taxonomy import SKILLS

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json()["ok"] is True


def test_meta_has_24_skills():
    assert len(client.get("/api/meta").json()["skills"]) == 24 == len(SKILLS)


def test_volunteer_validation():
    v = Volunteer(id="v1", display_name="Vol A", age=20, district="Kanpur Dehat", block="Bilhaur", lat=26.8, lon=80.1,
                  skills={"first_aid": 2})
    assert not v.is_minor and v.is_novice
    with pytest.raises(Exception):
        Volunteer(id="v2", display_name="X", age=20, district="d", block="b", lat=0, lon=0, skills={"nope": 1})


def test_rolespec_bounds():
    with pytest.raises(Exception):
        RoleSpec(id="r", role="x", count=0)


@pytest.mark.parametrize("path", ["/api/volunteers", "/api/tasks", "/api/ledger", "/api/ledger/verify", "/api/eval"])
def test_unimplemented_is_501_not_500(path):
    assert client.get(path).status_code == 501


def test_extract_json_tolerant():
    assert extract_json('```json\n{"a":1}\n```') == {"a": 1}
    assert extract_json('Here you go: {"a":[1,2]} thanks') == {"a": [1, 2]}
    with pytest.raises(LLMError):
        extract_json(None)
    with pytest.raises(LLMError):
        extract_json("no json here")
