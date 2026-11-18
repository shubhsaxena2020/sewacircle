"""Baseline tests: determinism, hard constraints, uniqueness, standbys, honest unfilled roles.

Fixtures are SYNTHETIC and hand-built from the schema classes (no synth.py dependency).
Coordinates are near the equator: 0.1 degrees longitude ~= 11.12 km (R=6371.0088 km).
"""
from __future__ import annotations

import pytest

from app.schemas import (RosterMetrics, RosterOptions, RoleSpec, TaskSpec, Volunteer)
from app.solver.baselines import manual_greedy, nearest_skill, random_feasible
from app.solver.metrics import compute_metrics, distance_km, is_eligible

BASE_VOLUNTEERS = [
    # id, skills, self-declared, past, times, lon, extra kwargs
    ("near", {"first_aid": 3}, (), 1, 2, 0.2, {}),
    ("far", {"first_aid": 3}, (), 9, 8, 1.0, {}),
    ("teach", {"teaching_literacy": 2}, (), 4, 1, 0.1, {}),
    ("logistics", {"logistics_supplies": 1}, (), 2, 0, 0.3, {}),
    ("extra_aid", {"first_aid": 2}, (), 7, 6, 0.4, {}),
]


def V(vid, *, skills=None, declared=(), past=0, times=0, lon=0.0, slots=("sat_morning",),
      age=20, consent=None, district="D1", block="B1"):
    """Synthetic volunteer builder local to this test module."""
    return Volunteer(id=vid, display_name=f"Vol {vid}", age=age, district=district, block=block,
                     lat=0.0, lon=lon, skills=dict(skills or {}),
                     self_declared_skills=list(declared), languages=["hi"],
                     available_slots=list(slots), past_drives=past,
                     times_picked_last_90d=times, guardian_consent=consent, synthetic=True)


def vols(specs=BASE_VOLUNTEERS):
    return [V(vid, skills=skills, declared=declared, past=past, times=times, lon=lon, **extra)
            for vid, skills, declared, past, times, lon, extra in specs]


def T(roles, *, max_travel_km=200.0, allow_minors=True):
    return TaskSpec(id="task-1", title="Baseline fixture", district="D1", block="B1", lat=0.0, lon=0.0,
                    slot="sat_morning", max_travel_km=max_travel_km, allow_minors=allow_minors,
                    roles=roles, synthetic=True)


ROLES = [
    RoleSpec(id="r1", role="First aid", count=2, required_skills=["first_aid"], min_level=2,
             priority="must", needs_experienced=True),
    RoleSpec(id="r2", role="Teaching", count=1, required_skills=["teaching_literacy"], min_level=1),
    RoleSpec(id="r3", role="Supplies", count=1, required_skills=["logistics_supplies"], min_level=1,
             priority="should"),
]


def _all_methods(task, volunteers, seed=11, options=None):
    return {
        "nearest_skill": nearest_skill(task, volunteers, options=options),
        "random_feasible": random_feasible(task, volunteers, seed=seed, options=options),
        "manual_greedy": manual_greedy(task, volunteers, options=options),
    }


def _comparable(roster):
    """Drop the wall-clock field: all other metric fields must be identical across runs."""
    return roster.metrics.model_copy(update={"solve_ms": 0})


def _metric_only(metrics):
    """Strip caller-owned timing/status fields before checking the shared metric values."""
    return metrics.model_copy(update={"solve_ms": 0, "solver_status": ""})


def test_baselines_deterministic_and_use_shared_metrics():
    """Two runs with the same seed/options must give identical assignments, standbys, reasons
    and metrics (except solve_ms, which is wall-clock). All metrics must equal a fresh call to
    the shared compute_metrics() on the same roster, which is what makes comparisons fair.
    """
    task, volunteers = T(ROLES), vols()
    options = RosterOptions(seed=11)
    for name, first in _all_methods(task, volunteers, options=options).items():
        second = _all_methods(task, volunteers, options=options)[name]
        assert first.method == name and first.synthetic is True
        assert first.assignments == second.assignments
        assert first.standby == second.standby
        assert first.unfilled_role_ids == second.unfilled_role_ids
        assert _comparable(first) == _comparable(second)
        assert _metric_only(compute_metrics(task, volunteers, first)) == _metric_only(first.metrics)
        assert all(a.reasons and a.volunteer_name for a in first.assignments)


def test_random_feasible_seed_controls_selection():
    """With one slot and four eligible volunteers, at least two different seeds must select a
    different person; every selected person must still satisfy every hard constraint.
    """
    role = RoleSpec(id="r1", role="First aid", count=1, required_skills=["first_aid"], min_level=1)
    task, volunteers = T([role]), vols()
    chosen = set()
    for seed in range(20):
        roster = random_feasible(task, volunteers, seed=seed)
        assert len(roster.assignments) == 1
        a = roster.assignments[0]
        v = next(x for x in volunteers if x.id == a.volunteer_id)
        assert is_eligible(v, role, task)
        chosen.add(a.volunteer_id)
    assert len(chosen) >= 2


def test_nearest_skill_ignores_experience_and_distance_is_real():
    """nearest_skill picks 'near' at 0.2 degrees (~22.239 km) over 'far' at 1.0 degrees
    (~111.195 km) even though far has 9 past drives vs near's 1 and a higher repeat count.
    This is an intentionally naive baseline: distance only, no fairness objective.
    """
    role = RoleSpec(id="r1", role="First aid", count=1, required_skills=["first_aid"], min_level=2)
    task, volunteers = T([role]), vols()
    roster = nearest_skill(task, volunteers)
    assert [a.volunteer_id for a in roster.assignments] == ["near"]
    assert roster.assignments[0].distance_km == pytest.approx(22.239, abs=0.01)
    assert distance_km(task, volunteers[1]) == pytest.approx(111.195, abs=0.01)
    assert "nearest_skill" in " ".join(roster.assignments[0].reasons)


def test_manual_greedy_experience_first_and_one_backup_per_role():
    """Role order r1 (TWO slots), r2, r3; most experienced eligible volunteer per slot:
    r1 candidates far(9 drives), extra_aid(7), near(1) -> far then extra_aid; r2 teach;
    r3 logistics. Next-best unused backup for r1: near (1); r2 and r3 have no unused eligible
    volunteer, so exactly ONE standby is produced, covering r1 only.
    """
    task, volunteers = T(ROLES), vols()
    roster = manual_greedy(task, volunteers)
    assert [(a.role_id, a.volunteer_id) for a in roster.assignments] == [
        ("r1", "far"), ("r1", "extra_aid"), ("r2", "teach"), ("r3", "logistics")]
    assert len(roster.standby) == 1
    s = roster.standby[0]
    assert s.volunteer_id == "near" and s.covers_role_ids == ["r1"]
    assert s.volunteer_id not in {a.volunteer_id for a in roster.assignments}
    assert is_eligible(next(v for v in volunteers if v.id == s.volunteer_id),
                       ROLES[0], task)
    assert "backup" in s.reason.lower()


def test_all_baselines_respect_every_hard_constraint_and_forced_ids():
    """Adversarial volunteer pool: unavailable, 222 km away (limit 200), unqualified, below
    min_level, minor without consent, minor with consent, self-declared-only, forced_out.
    For all three methods: no hard constraint is violated, no volunteer is assigned twice,
    forced_in teaching volunteer is placed, forced_out never appears, and the impossible
    forced_in (minor without consent) is reported rather than silently obeyed.
    """
    extra = [
        V("unavailable", skills={"first_aid": 3}, past=10, slots=("sun_morning",)),
        V("out_of_range", skills={"first_aid": 3}, past=10, lon=2.0),  # 222.39 km > 200
        V("unqualified", skills={"photography_video": 3}, past=10),
        V("low_level", skills={"first_aid": 1}, past=10),
        V("minor_no_consent", skills={"first_aid": 3}, past=10, age=16, consent=False),
        V("minor_consent", skills={"first_aid": 3}, past=10, age=16, consent=True, lon=0.5),
        V("declared", declared=("first_aid",), past=3, times=3, lon=0.05),
        V("forced_out_v", skills={"first_aid": 3}, past=10, lon=0.01),
        V("forced_in_v", skills={"teaching_literacy": 3}, past=8, times=9, lon=0.6),
    ]
    task, volunteers = T(ROLES), vols() + extra
    options = RosterOptions(forced_in=["forced_in_v", "minor_no_consent"],
                            forced_out=["forced_out_v"], seed=13)
    by_id = {v.id: v for v in volunteers}
    roles_by_id = {r.id: r for r in ROLES}
    for name, roster in _all_methods(task, volunteers, seed=13, options=options).items():
        ids = [a.volunteer_id for a in roster.assignments]
        assert len(ids) == len(set(ids)), f"{name} assigned someone twice"
        assert "forced_out_v" not in ids
        assert "forced_in_v" in ids
        assert "minor_no_consent" not in ids
        assert any("minor_no_consent" in line for line in roster.explanations)
        assert roster.method == name and roster.synthetic is True
        for a in roster.assignments:
            v, role = by_id[a.volunteer_id], roles_by_id[a.role_id]
            assert is_eligible(v, role, task), f"{name}: {v.id} violates hard constraints"
            assert a.volunteer_name == v.display_name and a.reasons
            assert a.distance_km <= task.max_travel_km
            if v.is_minor:
                assert task.allow_minors and v.guardian_consent is True
        for s in roster.standby:
            assert is_eligible(by_id[s.volunteer_id], roles_by_id[s.covers_role_ids[0]], task)
            assert s.volunteer_id not in ids
        assert 0.0 <= roster.metrics.role_coverage <= 1.0


def test_minors_blocked_by_consent_and_task_flag():
    """A consenting 16-year-old at 0.05 degrees (~5.56 km) can be assigned when allow_minors=True;
    with allow_minors=False the adult at 0.2 degrees (~22.24 km) is the only eligible first-aider.
    A 16-year-old without consent is never eligible. nearest/manual deterministically take the
    closer/more experienced consenting minor; the seeded random draw may pick either eligible
    person (seed=5 picks 'near'), which is still constraint-respecting.
    """
    role = RoleSpec(id="r1", role="First aid", count=1, required_skills=["first_aid"], min_level=2)
    pool = [V("near", skills={"first_aid": 3}, past=1, lon=0.2),
            V("minor_consent", skills={"first_aid": 3}, past=10, age=16, consent=True, lon=0.05),
            V("minor_no_consent", skills={"first_aid": 3}, past=10, age=16, consent=False, lon=0.01)]
    methods = [("nearest", nearest_skill), ("manual", manual_greedy),
               ("random", lambda t, v: random_feasible(t, v, seed=5))]
    for name, method in methods:
        allowed = method(T([role], allow_minors=True), pool)
        blocked = method(T([role], allow_minors=False), pool)
        assert blocked.assignments[0].volunteer_id == "near", name
        chosen = allowed.assignments[0].volunteer_id
        assert chosen in ({"near"} if name == "random" else {"minor_consent"}), name
        assert "minor_no_consent" not in {a.volunteer_id for a in allowed.assignments + blocked.assignments}
        assert is_eligible(next(v for v in pool if v.id == "minor_consent"), role,
                           T([role], allow_minors=True))


def test_self_declared_skill_allowed_but_flagged():
    """For an ordinary (non safety-critical) role, a volunteer whose only claim is a self-declared skill at
    min_level 2 qualifies (no level is stored for declarations) and the Assignment carries the flag.
    Updated 2026-11-19: first aid is now safety-critical, so this uses teaching (see the safety test below).
    """
    role = RoleSpec(id="r1", role="Teaching", count=1, required_skills=["teaching_literacy"], min_level=2)
    task = T([role])
    volunteer = V("declared", declared=("teaching_literacy",), past=3)
    assert is_eligible(volunteer, role, task)
    for roster in _all_methods(task, [volunteer]).values():
        assert [a.volunteer_id for a in roster.assignments] == ["declared"]
        assert "self_declared_skill" in roster.assignments[0].flags


def test_safety_critical_role_never_accepts_self_declared_skill():
    """Devil's-advocate finding (docs/v3): a self-declared first-aider must never fill a first-aid role."""
    role = RoleSpec(id="r1", role="First aid", count=1, required_skills=["first_aid"])
    assert role.safety_critical is True                      # set automatically from the skill
    task = T([role])
    volunteer = V("declared", declared=("first_aid",), past=3)
    assert not is_eligible(volunteer, role, task)
    for roster in _all_methods(task, [volunteer]).values():
        assert roster.assignments == [] and roster.unfilled_role_ids == ["r1"]


def test_unfilled_roles_are_reported_honestly():
    """r1 requires first_aid level 3 but nobody has above level 2, so r1 stays unfilled for all
    methods. r2 is filled: slots_filled=1, slots_required=2, coverage=0.5, status is partial,
    and the unfilled id appears in unfilled_role_ids and in the plain-English explanations.
    """
    roles = [RoleSpec(id="r1", role="Senior first aider", count=1,
                      required_skills=["first_aid"], min_level=3, priority="must"),
             RoleSpec(id="r2", role="Teaching", count=1,
                      required_skills=["teaching_literacy"], min_level=1)]
    task = T(roles)
    volunteers = [V("aide", skills={"first_aid": 2}), V("teach", skills={"teaching_literacy": 2})]
    for name, roster in _all_methods(task, volunteers).items():
        assert roster.unfilled_role_ids == ["r1"], name
        assert (roster.metrics.slots_filled, roster.metrics.slots_required) == (1, 2), name
        assert roster.metrics.role_coverage == 0.5, name
        assert roster.metrics.solver_status == "baseline_partial", name
        assert any("Unfilled role slots: r1" in line for line in roster.explanations), name
        assert all(a.role_id == "r2" for a in roster.assignments), name


def test_no_slot_placeholder_metric_leaks():
    """RosterMetrics defaults are never returned unfilled: every baseline reports the real
    slots_required, and solve_ms is a non-negative integer measured at runtime.
    """
    task, volunteers = T(ROLES), vols()
    for roster in _all_methods(task, volunteers).values():
        assert roster.metrics.slots_required == 3  # A1: MUST slots only: r1 x2 + r2 (r3 is should)
        assert isinstance(roster.metrics.solve_ms, int) and roster.metrics.solve_ms >= 0
        assert roster.metrics.solver_status in {"baseline_complete", "baseline_partial"}
        assert isinstance(roster.metrics, RosterMetrics)
