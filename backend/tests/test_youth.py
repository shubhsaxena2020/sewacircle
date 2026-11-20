"""Youth-side matching: eligibility first, explained percentages, stable ranking."""
from fastapi.testclient import TestClient

from app.main import app, tasks
from app.youth import WEIGHTS, YouthProfile, recommend

KANPUR = dict(lat=26.4499, lon=80.3319, district="Kanpur Nagar")
AKBARPUR = dict(lat=26.43, lon=79.95, district="Kanpur Dehat")


def test_minor_never_sees_adult_only_projects():
    adult_only = {t.id for t in tasks() if not t.allow_minors}
    res = recommend(YouthProfile(age=17, skills=["first_aid"], available_slots=["sat_morning"], **KANPUR), tasks())
    assert adult_only.isdisjoint({m.task_id for m in res.matches})
    assert adult_only <= {e.task_id for e in res.excluded}


def test_under_minimum_age_gets_nothing():
    res = recommend(YouthProfile(age=14, **KANPUR), tasks())
    assert res.matches == [] and len(res.excluded) == len(tasks())


def test_percent_is_sum_of_explained_parts_and_sorted():
    res = recommend(YouthProfile(age=20, skills=["graphic_design", "first_aid"], interests=["health"],
                                 available_slots=["sat_morning", "sun_morning"], **KANPUR), tasks())
    assert res.matches and len(res.matches) <= 10
    for m in res.matches:
        assert m.percent == sum(m.parts.values()) <= sum(WEIGHTS.values())
        assert m.reasons
    assert [m.percent for m in res.matches] == sorted((m.percent for m in res.matches), reverse=True)


def test_safety_role_is_flagged_not_qualified():
    res = recommend(YouthProfile(age=20, skills=["first_aid"], available_slots=["sat_morning"], **KANPUR), tasks())
    flagged = [m for m in res.matches if m.host_check_needed]
    assert flagged and all(m.parts["skills"] < WEIGHTS["skills"] for m in flagged)


def test_endpoint_returns_hindi_reasons():
    body = {"profile": {"age": 19, "skills": ["teaching_literacy"], "available_slots": ["sun_morning"], **KANPUR}, "lang": "hi"}
    r = TestClient(app).post("/api/youth/recommend", json=body)
    assert r.status_code == 200
    assert any("किमी" in reason for m in r.json()["matches"] for reason in m["reasons"])


def test_far_projects_are_excluded_not_ranked():
    res = recommend(YouthProfile(age=20, skills=["teaching_literacy"], available_slots=["sat_afternoon"], **AKBARPUR), tasks())
    by_id = {t.id: t for t in tasks()}
    from app.solver.metrics import haversine_km
    for m in res.matches:
        t = by_id[m.task_id]
        assert haversine_km(AKBARPUR["lat"], AKBARPUR["lon"], t.lat, t.lon) <= 2 * t.max_travel_km
    assert any("travel limit" in e.reason for e in res.excluded)
