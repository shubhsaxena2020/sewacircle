"""Name protection (Kaggle MIT gazetteer + roster pseudonymisation). Measures, does not assume."""
import json
from pathlib import Path

from app.data.synth import make_volunteers
from app.llm import extract
from app.llm.names import gazetteer, mask_names, pseudonymise
from app.schemas import Assignment, AttendanceRow, RoleSpec, TaskSpec


def test_gazetteer_loaded():
    assert len(gazetteer()) > 3000 and "Asha" not in gazetteer()   # stop-list keeps ASHA workers intact


def test_mask_names_basic_and_keeps_ordinary_words():
    out, n = mask_names("Shreyas and Gulati met Asha workers at the Health Camp on Saturday.")
    assert "Shreyas" not in out and "Gulati" not in out and n == 2
    assert "Asha workers" in out and "Health Camp" in out and "Saturday" in out


def test_pseudonymise_full_and_first_name():
    out, n = pseudonymise("Kabir Z. did first aid. Later Kabir helped Om P.", {"Kabir Z.": "v-002", "Om P.": "v-009"})
    assert out == "[v-002] did first aid. Later [v-002] helped [v-009]" + "" or "[v-002]" in out
    assert "Kabir" not in out and n >= 2


def test_no_false_positives_on_the_30_eval_briefs():
    briefs = json.loads((Path(__file__).parents[2] / "eval/extraction/briefs.json").read_text(encoding="utf-8"))["briefs"]
    hits = {b["id"]: mask_names(b["text"])[1] for b in briefs}
    assert sum(hits.values()) == 0, hits   # these briefs contain no person names


def test_draft_cards_sends_no_roster_names_to_model(monkeypatch):
    seen = {}

    def fake(purpose, system, user, max_tokens=3000, retries=2):
        seen["user"] = user
        return {"cards": [{"volunteer_id": "v-002", "claimed_hours": 5, "summary": "[v-002] took photos", "evidence": "x"}]}, \
            {"cached": False, "model": "fake", "ms": 1, "purpose": purpose}
    monkeypatch.setattr(extract.client, "complete_json", fake)
    task = TaskSpec(id="task-01", title="Camp", slot="sat_morning", district="Lucknow", block="Chinhat", lat=26.8, lon=80.9,
                    roles=[RoleSpec(id="role-01", role="Photos", count=1, required_skills=["photography_video"])])
    a = [Assignment(role_id="role-01", volunteer_id="v-002", volunteer_name="Shreyas Gulati")]
    cards = extract.draft_cards(task, "Shreyas Gulati took photos for 5 hours with Dheeraj.", [AttendanceRow(volunteer_id="v-002", task_id="task-01", hours=5)], a)
    assert "Shreyas" not in seen["user"] and "Gulati" not in seen["user"] and "Dheeraj" not in seen["user"]
    assert "[v-002]" in seen["user"] and "[NAME]" in seen["user"]
    assert cards[0].summary == "Shreyas Gulati took photos"      # mapped back for the host to read


def test_recall_on_synthetic_volunteer_first_names_is_reported():
    """Honest measurement, not a target: share of our synthetic first names the gazetteer catches."""
    firsts = {v.display_name.split()[0] for v in make_volunteers()}
    caught = {f for f in firsts if mask_names(f + " came.")[1]}
    print(f"gazetteer recall on synthetic first names: {len(caught)}/{len(firsts)}; missed: {sorted(firsts - caught)}")
    assert len(firsts) > 0
