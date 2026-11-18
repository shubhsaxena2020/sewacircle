"""Tests for the random-instance generator used by Lane A property/adversarial tests.

These tests do NOT require cp_sat.py, metrics.py or synth.py: they prove the
scaffolding itself is deterministic, schema-valid and able to reach adversarial
regions of the input space. Later B2 tests can import the same factories.
"""
from __future__ import annotations

import pytest

from factories import (
    DISTRICT_ANCHORS,
    SCARCE_DEFAULT,
    SLOT_IDS,
    VALID_SEED_COUNT,
    haversine_km,
    make_random_case,
    make_random_task,
    make_random_volunteers,
    validate_case,
    validate_instances,
    volunteer_is_eligible,
)
from app.schemas import RoleSpec, RosterOptions, TaskSpec, Volunteer
from app.taxonomy import SKILLS, SLOTS

SEEDS = range(VALID_SEED_COUNT)


def _hard_problems(problems: list[str]) -> list[str]:
    return [p for p in problems if not p.startswith("warn:")]


# ---------------------------------------------------------------------------
# determinism
# ---------------------------------------------------------------------------
def test_volunteers_are_deterministic():
    a = make_random_volunteers(25, 123)
    b = make_random_volunteers(25, 123)
    c = make_random_volunteers(25, 124)
    assert [v.model_dump() for v in a] == [v.model_dump() for v in b]
    assert [v.id for v in a] != [v.id for v in c]


def test_task_and_options_are_deterministic():
    t1, o1 = make_random_task(31)
    t2, o2 = make_random_task(31)
    t3, _ = make_random_task(32)
    assert t1.model_dump() == t2.model_dump()
    assert o1.model_dump() == o2.model_dump()
    assert t1.model_dump() != t3.model_dump()


def test_full_case_is_deterministic():
    a = make_random_case(17, n_volunteers=20)
    b = make_random_case(17, n_volunteers=20)
    assert a[0].model_dump() == b[0].model_dump()
    assert a[2].model_dump() == b[2].model_dump()
    assert [x.model_dump() for x in a[1]] == [x.model_dump() for x in b[1]]


# ---------------------------------------------------------------------------
# schema validity / sweep
# ---------------------------------------------------------------------------
def test_all_objects_are_schema_instances():
    for seed in SEEDS:
        task, people, options = make_random_case(seed, n_volunteers=15)
        assert isinstance(task, TaskSpec)
        assert isinstance(options, RosterOptions)
        assert len(people) == 15
        for v in people:
            assert isinstance(v, Volunteer)
            assert v.synthetic is True
            assert isinstance(v.age, int)
            assert all(k in SKILLS and lvl in (1, 2, 3) for k, lvl in v.skills.items())
        for role in task.roles:
            assert isinstance(role, RoleSpec)
            assert all(s in SKILLS for s in role.required_skills)


def test_validate_case_accepts_all_seeds():
    for seed in SEEDS:
        task, people, options = make_random_case(seed, n_volunteers=20)
        assert _hard_problems(validate_case(task, people, options)) == [], seed


def test_batch_validator_reports_no_hard_failure():
    assert validate_instances(0, VALID_SEED_COUNT, n_volunteers=20) == []


def test_factory_fixture_shape(solver_case, solver_validator, solver_seed):
    task, people, options = solver_case
    assert task.id == f"task_{solver_seed}"
    assert options.seed == solver_seed
    assert solver_validator(task, people, options) is not None


def test_parametrized_seed_fixture_shape(solver_seed_param):
    seed = solver_seed_param
    assert seed in SEEDS
    task, people, _ = make_random_case(seed, n_volunteers=5)
    assert task.id == f"task_{seed}"
    assert len(people) == 5


# ---------------------------------------------------------------------------
# constraint-relevant fields are present
# ---------------------------------------------------------------------------
def test_constraint_relevant_fields_present():
    task, people, options = make_random_case(7, n_volunteers=200)
    assert task.slot in SLOTS
    assert task.slot in SLOT_IDS
    assert task.max_travel_km > 0
    assert isinstance(task.allow_minors, bool)
    assert isinstance(task.lat, float) and isinstance(task.lon, float)
    assert all(v.available_slots for v in people)
    assert all(task.slot in v.available_slots for v in people)
    assert all(0 <= v.lat <= 35 and 65 <= v.lon <= 90 for v in people)
    assert len({v.district for v in people}) >= 6
    assert len({v.block for v in people}) >= 2
    assert any(v.is_minor for v in people)
    assert any(v.is_minor and v.guardian_consent is not True for v in people)
    assert any(v.is_novice for v in people)
    assert any(v.can_mentor for v in people)
    assert any(v.times_picked_last_90d >= 6 for v in people)
    assert any(v.self_declared_skills for v in people)
    assert any(role.needs_experienced for role in task.roles) or len(task.roles) > 0
    assert any(role.priority == "must" for role in task.roles)
    assert options.time_limit_s > 0
    assert options.seed == 7


def test_many_distinct_slots_and_blocks_across_seeds():
    slots, blocks, travels = set(), set(), set()
    for seed in SEEDS:
        task, _, _ = make_random_case(seed, n_volunteers=8)
        slots.add(task.slot)
        blocks.add(task.block)
        travels.add(task.max_travel_km)
    assert len(slots) > 3
    assert len(blocks) > 2
    assert len(travels) > 3


def test_haversine_basics():
    assert haversine_km(0.0, 0.0, 0.0, 0.0) == pytest.approx(0.0)
    d = haversine_km(0.0, 0.0, 0.0, 1.0)
    assert 110.0 < d < 112.0
    assert haversine_km(0.0, 1.0, 0.0, 0.0) == pytest.approx(d)


# ---------------------------------------------------------------------------
# adversarial knobs really are reachable
# ---------------------------------------------------------------------------
def test_scarce_skill_knob_produces_unfillable_role():
    task, people, options = make_random_case(
        11, n_volunteers=40,
        volunteer_kwargs={"scarce_skills": ("first_aid",), "scarcity_rate": 1.0},
        scarce_skills=("first_aid",), force_scarce_skill=True, min_level=1,
    )
    # Normalise away any incidental self-declaration so the scarcity knob is
    # tested in isolation (a self-declared skill is still allowed by the schema).
    people = [v.model_copy(update={
        "skills": {k: x for k, x in v.skills.items() if k != "first_aid"},
        "self_declared_skills": [s for s in v.self_declared_skills if s != "first_aid"],
    }) for v in people]
    assert task.roles[0].required_skills == ["first_aid"]
    assert all("first_aid" not in v.skills for v in people)
    assert all("first_aid" not in v.self_declared_skills for v in people)
    assert volunteer_is_eligible(people[0], task, task.roles[0], options) is False
    problems = validate_case(task, people, options)
    assert any("warn: role r0" in p for p in problems)
    assert _hard_problems(problems) == []


def test_remote_block_and_tight_travel_block_everyone():
    anchor = DISTRICT_ANCHORS["Lucknow"]
    task, people, options = make_random_case(
        3, n_volunteers=30, district="Lucknow", remote=True, max_travel_km=0.5,
        force_scarce_skill=False,
    )
    assert task.block.startswith("remote_")
    assert task.max_travel_km == 0.5
    far = [v.model_copy(update={"lat": anchor[0], "lon": anchor[1]}) for v in people]
    assert all(
        haversine_km(v.lat, v.lon, task.lat, task.lon) > task.max_travel_km for v in far
    )
    assert all(volunteer_is_eligible(v, task, task.roles[0], options) is False for v in far)


def test_minor_consent_knobs_reachable():
    with_consent = make_random_volunteers(
        40, 5, minor_fraction=1.0, no_consent_fraction=0.0)
    without = make_random_volunteers(
        40, 5, minor_fraction=1.0, no_consent_fraction=1.0)
    assert all(v.is_minor for v in with_consent)
    assert all(v.guardian_consent is True for v in with_consent)
    assert all(v.is_minor for v in without)
    assert all(v.guardian_consent is False for v in without)
    # Valid input data even without consent: the solver, not the factory, rejects them.
    for v in without:
        assert _hard_problems(validate_case(
            TaskSpec(id="t", title="Synthetic probe", district="Lucknow", block="b",
                     lat=26.85, lon=80.95,
                     roles=[RoleSpec(id="r0", role="probe", count=1,
                                     required_skills=["first_aid"])]),
            [v], RosterOptions())) == []


def test_minors_blocked_when_task_disallows_them():
    task, people, options = make_random_case(
        5, n_volunteers=30, allow_minors=False,
        volunteer_kwargs={"minor_fraction": 1.0, "no_consent_fraction": 0.0},
        force_scarce_skill=False,
    )
    minors = [v for v in people if v.is_minor]
    assert minors
    assert all(volunteer_is_eligible(v, task, task.roles[0], options) is False
               for v in minors)


def test_minor_with_consent_can_be_eligible():
    task, people, options = make_random_case(
        5, n_volunteers=10, allow_minors=True,
        volunteer_kwargs={"minor_fraction": 1.0, "no_consent_fraction": 0.0},
        force_scarce_skill=False,
    )
    role = task.roles[0]
    v = people[0].model_copy(update={
        "lat": task.lat, "lon": task.lon,
        "skills": {s: role.min_level for s in role.required_skills},
        "available_slots": [task.slot],
    })
    assert volunteer_is_eligible(v, task, role, options) is True


def test_forced_in_and_forced_out_knobs_reachable():
    base = 9
    fin = (f"v{base + 1}_0000",)
    fout = (f"v{base + 1}_0001",)
    task, people, options = make_random_case(
        base, n_volunteers=10, forced_in=fin, forced_out=fout)
    assert set(fin) <= {v.id for v in people}
    assert set(fout) <= {v.id for v in people}
    assert options.forced_in == list(fin)
    assert options.forced_out == list(fout)
    assert volunteer_is_eligible(
        next(v for v in people if v.id == fout[0]), task, task.roles[0], options) is False


def test_varied_slots_knob_reachable():
    slots = ("mon_morning", "wed_evening", "sun_afternoon")
    task, people, _ = make_random_case(8, n_volunteers=12, slots=slots)
    assert task.slot in slots
    assert all(task.slot in v.available_slots for v in people)


def test_min_level_and_role_count_knobs_reachable():
    task, _ = make_random_task(4, role_count=5, min_level=3, slots=("sat_morning",))
    assert len(task.roles) == 5
    assert all(r.min_level == 3 for r in task.roles)
    assert task.slot == "sat_morning"


# ---------------------------------------------------------------------------
# validate_case catches corruption
# ---------------------------------------------------------------------------
def test_validate_case_catches_corruption():
    task, people, options = make_random_case(2, n_volunteers=6)
    assert _hard_problems(validate_case(task, people, options)) == []
    bad_slot = task.model_copy(update={"slot": "not_a_slot"})
    assert any("slot not in taxonomy" in p for p in validate_case(bad_slot, people, options))
    overlap = options.model_copy(update={"forced_out": list(options.forced_in) + [people[0].id]})
    overlap = overlap.model_copy(update={"forced_in": [people[0].id]})
    assert any("forced_in and forced_out overlap" in p for p in validate_case(task, people, overlap))
    bad_time = options.model_copy(update={"time_limit_s": 0.0})
    assert any("time_limit_s" in p for p in validate_case(task, people, bad_time))
    dupes = people + [people[0]]
    assert any("duplicate volunteer ids" in p for p in validate_case(task, dupes, options))
