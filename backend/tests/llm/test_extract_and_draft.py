"""Head tests for extraction, drafting and credential export. No network: llm.client.complete_json is monkeypatched."""
import pytest

from app.evidence import badges
from app.llm import extract
from app.llm.client import LLMError
from app.schemas import Assignment, AttendanceRow, ContributionCard, RoleSpec, TaskSpec, Volunteer

BRIEF = "गाँव में शनिवार को शिविर। २ लोग प्राथमिक उपचार के लिए और कोई जो सामान संभाले। संपर्क 9876543210"


def _fake(payload):
    def f(purpose, system, user, max_tokens=3000, retries=2):
        f.calls.append((purpose, system, user))
        return payload, {"cached": False, "model": "fake", "ms": 1, "purpose": purpose}
    f.calls = []
    return f


def test_extract_redacts_before_model_and_validates(monkeypatch):
    fake = _fake({"roles": [
        {"role": "First-aid support", "count": "२", "required_skills": ["first_aid", "not_a_skill"], "evidence_span": "२ लोग प्राथमिक उपचार", "confidence": "high"},
        {"role": "Supplies", "count": 1, "required_skills": ["logistics_supplies"], "evidence_span": "made up span", "confidence": "high"},
    ], "needs_decision": [], "language_detected": "hi"})
    monkeypatch.setattr(extract.client, "complete_json", fake)
    r = extract.extract_roles(BRIEF)
    sent = fake.calls[0][2]
    assert "9876543210" not in sent and r.redactions >= 1          # PII never reaches the model
    assert r.roles[0].count == 2                                    # Devanagari digit parsed
    assert r.roles[0].required_skills == ["first_aid"]              # unknown skill dropped...
    assert any("not_a_skill" in n for n in r.notes)                 # ...and noted
    assert r.roles[1].confidence == "low"                           # span not in text -> low confidence
    assert any("Supplies" in q for q in r.needs_decision)
    specs = extract.to_role_specs(r)
    assert [s.id for s in specs] == ["role-01", "role-02"]


def test_extract_bad_model_output_raises_llm_error(monkeypatch):
    monkeypatch.setattr(extract.client, "complete_json", _fake({"nope": 1}))
    with pytest.raises(LLMError):
        extract.extract_roles("Need two cooks on Sunday.")


def test_extract_empty_brief_needs_no_model(monkeypatch):
    monkeypatch.setattr(extract.client, "complete_json", lambda *a, **k: (_ for _ in ()).throw(AssertionError("called")))
    assert extract.extract_roles("   ").roles == []


TASK = TaskSpec(id="task-01", title="Camp", slot="sat_morning", district="Lucknow", block="Chinhat", lat=26.8, lon=80.9,
                roles=[RoleSpec(id="role-01", role="First aid", count=1, required_skills=["first_aid"]),
                       RoleSpec(id="role-02", role="Photos", count=1, required_skills=["photography_video"])])
ASSIGN = [Assignment(role_id="role-01", volunteer_id="v-001", volunteer_name="Asha K."),
          Assignment(role_id="role-02", volunteer_id="v-002", volunteer_name="Om P.")]
ROWS = [AttendanceRow(volunteer_id="v-001", task_id="task-01", hours=5), AttendanceRow(volunteer_id="v-002", task_id="task-01", hours=5)]


def test_draft_cards_never_confirms_and_uses_recorded_hours(monkeypatch):
    monkeypatch.setattr(extract.client, "complete_json", _fake({"cards": [
        {"volunteer_id": "v-002", "role": "Photos", "claimed_hours": 8, "summary": "Took photos.", "evidence": "Om took photos for 8 hours"},
        {"volunteer_id": "v-999", "role": "Ghost", "claimed_hours": 3, "summary": "x", "evidence": ""}]}))
    cards = extract.draft_cards(TASK, "Om took photos for 8 hours", ROWS, ASSIGN)
    by = {c.volunteer_id: c for c in cards}
    assert set(by) == {"v-001", "v-002"}                            # unknown id dropped; unmentioned rostered person still gets a card
    assert by["v-002"].claimed_hours == 8 and by["v-002"].recorded_hours == 5
    assert by["v-001"].claimed_hours == 0 and "not mentioned" in by["v-001"].summary
    assert all(c.status == "draft" and c.confirmed_by is None for c in cards)
    assert by["v-002"].id == "card-task-01-v-002-photos"            # deterministic id
    assert any(r.startswith("host_note:task-01:v-002:") for r in by["v-002"].evidence_refs)  # specific, not a shared generic ref
    assert extract.draft_cards(TASK, "Om took photos for 8 hours", ROWS, ASSIGN)[0].id in {c.id for c in cards}


def test_draft_cards_fallback_when_llm_down(monkeypatch):
    def down(*a, **k):
        raise LLMError("down")
    monkeypatch.setattr(extract.client, "complete_json", down)
    cards = extract.draft_cards(TASK, "Asha worked 6 hours at the first aid desk.\nOm did photos 4 hours.", ROWS, ASSIGN)
    by = {c.volunteer_id: c for c in cards}
    assert by["v-001"].claimed_hours == 6 and by["v-002"].claimed_hours == 4
    assert all(c.drafted_by == "human" and c.status == "draft" for c in cards)


def _vol():
    return Volunteer(id="v-001", display_name="Asha K.", age=21, district="Lucknow", block="Chinhat", lat=26.8, lon=80.9)


def test_credential_shape_unsigned_and_no_pii():
    card = ContributionCard(id="card-task-01-v-001-first-aid", task_id="task-01", volunteer_id="v-001", role="First aid",
                            claimed_hours=5, recorded_hours=5, status="confirmed", confirmed_by="host")
    doc = badges.to_credential(card, _vol())
    assert badges.missing_required(doc) == {}
    assert doc["@context"][0] == "https://www.w3.org/ns/credentials/v2"
    assert "OpenBadgeCredential" in doc["type"] and "proof" not in doc
    assert "UNSIGNED" in doc["description"]
    assert doc["credentialSubject"]["id"].startswith("urn:uuid:") and "v-001" not in doc["credentialSubject"]["id"]
    assert "Asha" not in str(doc)                                    # display name is not exported
    assert badges.to_credential(card, _vol())["id"] == doc["id"]     # deterministic


def test_credential_refuses_unconfirmed():
    card = ContributionCard(id="c", task_id="t", volunteer_id="v-001", role="x", claimed_hours=1)
    with pytest.raises(ValueError):
        badges.to_credential(card, _vol())


def test_distinct_note_lines_do_not_trigger_duplicate_evidence(monkeypatch):
    from app.evidence.rules import check_card
    monkeypatch.setattr(extract.client, "complete_json", _fake({"cards": [
        {"volunteer_id": "v-001", "role": "First aid", "claimed_hours": 5, "summary": "a", "evidence": "Asha ran first aid 5 hours"},
        {"volunteer_id": "v-002", "role": "Photos", "claimed_hours": 5, "summary": "b", "evidence": "Om took photos 5 hours"}]}))
    notes = "Asha ran first aid 5 hours" + chr(10) + "Om took photos 5 hours"
    cards = extract.draft_cards(TASK, notes, ROWS, ASSIGN)
    for c in cards:
        assert "duplicate_evidence_ref" not in [f.code for f in check_card(c, cards, ROWS)]



def test_unknown_skill_role_becomes_unresolved_not_open(monkeypatch):
    """Devil's-advocate finding: an unmapped requirement must not silently become 'anyone can do it'."""
    monkeypatch.setattr(extract.client, "complete_json", _fake({"roles": [
        {"role": "Snake handler", "count": 1, "required_skills": ["snake_handling"], "evidence_span": "", "confidence": "high"}],
        "needs_decision": []}))
    r = extract.extract_roles("Need a snake handler for the camp.")
    assert r.roles[0].unresolved and r.roles[0].confidence == "low"
    assert extract.to_role_specs(r)[0].unresolved is True
    assert any("Snake handler" in q for q in r.needs_decision)


def test_card_role_comes_from_roster_not_model_text(monkeypatch):
    monkeypatch.setattr(extract.client, "complete_json", _fake({"cards": [
        {"volunteer_id": "v-002", "role": "Chief Executive Volunteer", "claimed_hours": 5, "summary": "x", "evidence": "Om 5 hours"}]}))
    cards = {c.volunteer_id: c for c in extract.draft_cards(TASK, "Om 5 hours", ROWS, ASSIGN)}
    assert cards["v-002"].role == "Photos"
