"""CP-SAT roster tests (head). Property tests reuse Lane A's random-instance factories."""
import pytest

from app.data.synth import make_tasks, make_volunteers
from app.schemas import RoleSpec, RosterOptions, TaskSpec, Volunteer
from app.solver import api
from app.solver.metrics import compute_metrics, distance_km, is_eligible
from tests.solver.factories import make_random_case

V = make_volunteers()
T = make_tasks()


def _assert_hard_constraints(task, vols, roster, opts=None):
    by = {v.id: v for v in vols}
    roles = {r.id: r for r in task.roles}
    seen_v, seen_slot = set(), set()
    for a in roster.assignments:
        v, r = by[a.volunteer_id], roles[a.role_id]
        assert is_eligible(v, r, task), (task.id, a)
        assert task.slot in v.available_slots
        assert distance_km(task, v) <= task.max_travel_km + 1e-9
        if v.is_minor:
            assert task.allow_minors and v.guardian_consent is True
        assert a.volunteer_id not in seen_v, "one slot per volunteer"
        assert (a.role_id, a.slot_index) not in seen_slot, "one volunteer per slot"
        assert 0 <= a.slot_index < r.count
        seen_v.add(a.volunteer_id)
        seen_slot.add((a.role_id, a.slot_index))
        if opts:
            assert a.volunteer_id not in opts.forced_out
    for s in roster.standby:
        assert s.volunteer_id not in seen_v, "standby is not also on the roster"


@pytest.mark.parametrize("task", T, ids=[t.id for t in T])
def test_synthetic_tasks_hard_constraints_reasons_and_metrics(task):
    r = api.build_roster(task, V)
    _assert_hard_constraints(task, V, r)
    assert r.metrics.solver_status in ("OPTIMAL", "FEASIBLE")
    assert all(a.reasons for a in r.assignments), "every assignment has a reason"
    fresh = compute_metrics(task, V, r)
    assert fresh.role_coverage == r.metrics.role_coverage and fresh.robustness == r.metrics.robustness


@pytest.mark.parametrize("task", T, ids=[t.id for t in T])
def test_cp_sat_never_worse_than_baselines_on_coverage(task):
    cp = api.build_roster(task, V)
    assert cp.metrics.solver_status == "OPTIMAL"
    for base in (api.baseline_nearest_skill(task, V), api.baseline_manual_greedy(task, V), api.baseline_random_feasible(task, V, 7)):
        assert cp.metrics.role_coverage >= base.metrics.role_coverage - 1e-12, (task.id, base.method)


def test_unfilled_is_reported_not_hidden():
    t4 = next(t for t in T if t.id == "task-04")   # deliberately scarce task
    r = api.build_roster(t4, V)
    assert r.metrics.role_coverage < 1.0
    assert r.unfilled_slots and r.unfilled_role_ids
    assert any("Unfilled" in e for e in r.explanations)


@pytest.mark.parametrize("seed", range(200))
def test_property_random_instances_never_break_hard_constraints(seed):
    task, vols, opts = make_random_case(seed)
    opts = opts.model_copy(update={"seed": seed, "time_limit_s": 5})
    r = api.build_roster(task, vols, opts)
    _assert_hard_constraints(task, vols, r, opts)
    if r.metrics.solver_status == "OPTIMAL":
        assert r.metrics.role_coverage >= api.baseline_nearest_skill(task, vols).metrics.role_coverage - 1e-12


def _v(i, **kw):
    base = dict(id=f"v-{i:03d}", display_name=f"V{i}", age=25, district="Lucknow", block="Chinhat", lat=26.85, lon=80.95,
                available_slots=["sat_morning"], skills={})
    base.update(kw)
    return Volunteer(**base)


def _task(roles, **kw):
    base = dict(id="task-x", title="t", slot="sat_morning", district="Lucknow", block="Chinhat", lat=26.85, lon=80.95,
                max_travel_km=20, roles=roles)
    base.update(kw)
    return TaskSpec(**base)


def test_adversarial_must_coverage_beats_every_secondary_preference():
    """The only person who can fill the MUST role is far, heavily over-picked, and also the best fit for a SHOULD role.
    Sequential tiers must still put them on the MUST role (tier 1 is fixed before quality/fairness are optimised)."""
    must = RoleSpec(id="role-01", role="First aid", count=1, required_skills=["first_aid"], priority="must")
    should = RoleSpec(id="role-02", role="Photos", count=1, required_skills=["photography_video"], priority="should")
    star = _v(1, skills={"first_aid": 1, "photography_video": 3}, times_picked_last_90d=9, past_drives=9, lat=26.95)
    other = _v(2, skills={"photography_video": 1})
    r = api.build_roster(_task([must, should]), [star, other])
    assert {(a.role_id, a.volunteer_id) for a in r.assignments} == {("role-01", "v-001"), ("role-02", "v-002")}
    assert r.metrics.role_coverage == 1.0


def test_minor_without_consent_is_never_assigned_even_if_only_candidate():
    role = RoleSpec(id="role-01", role="Teacher", count=1, required_skills=["teaching_literacy"])
    kid = _v(1, age=16, guardian_consent=False, skills={"teaching_literacy": 3})
    r = api.build_roster(_task([role]), [kid])
    assert r.assignments == [] and r.unfilled_role_ids == ["role-01"]


def test_forced_in_and_out_are_respected():
    role = RoleSpec(id="role-01", role="Helper", count=2, required_skills=[])
    vols = [_v(i) for i in range(1, 6)]
    r = api.build_roster(_task([role]), vols, RosterOptions(forced_in=["v-005"], forced_out=["v-001", "v-002"]))
    ids = {a.volunteer_id for a in r.assignments}
    assert "v-005" in ids and not ids & {"v-001", "v-002"}


def test_fairness_prefers_less_picked_when_equal():
    role = RoleSpec(id="role-01", role="Helper", count=1, required_skills=["logistics_supplies"])
    busy = _v(1, skills={"logistics_supplies": 2}, times_picked_last_90d=6, past_drives=8)
    fresh = _v(2, skills={"logistics_supplies": 2}, times_picked_last_90d=0, past_drives=8)
    on = api.build_roster(_task([role]), [busy, fresh], RosterOptions(fairness=True, resilience=False))
    assert on.assignments[0].volunteer_id == "v-002"


def test_standby_makes_roster_dropout_robust_and_dropout_heals():
    role = RoleSpec(id="role-01", role="First aid", count=1, required_skills=["first_aid"])
    vols = [_v(1, skills={"first_aid": 3}), _v(2, skills={"first_aid": 2})]
    task = _task([role])
    r = api.build_roster(task, vols)
    assert r.metrics.robustness == 1.0 and len(r.standby) == 1
    no_res = api.build_roster(task, vols, RosterOptions(resilience=False))
    assert no_res.metrics.robustness == 0.0
    d = api.simulate_dropout(task, vols, r, r.assignments[0].volunteer_id)
    assert d.healed_with_standby and d.uncovered_role_ids == []
    assert d.roster_after.metrics.role_coverage == 1.0


def test_why_not_explains_blocking_rule_and_real_delta():
    role = RoleSpec(id="role-01", role="Helper", count=1, required_skills=["logistics_supplies"])
    near = _v(1, skills={"logistics_supplies": 3})
    alt = _v(2, skills={"logistics_supplies": 1}, lat=26.9)
    away = _v(3, skills={"logistics_supplies": 3}, available_slots=["sun_morning"])
    task = _task([role])
    r = api.build_roster(task, [near, alt, away], RosterOptions(resilience=False))
    blocked = api.why_not(task, [near, alt, away], r, "v-003")
    assert not blocked.feasible and any("Not available" in b for b in blocked.blocking_reasons)
    cf = api.why_not(task, [near, alt, away], r, "v-002")
    assert cf.feasible and cf.displaced_volunteer_ids == ["v-001"]


def test_deterministic_same_seed():
    a = api.build_roster(T[0], V, RosterOptions(seed=3))
    b = api.build_roster(T[0], V, RosterOptions(seed=3))
    assert [(x.role_id, x.volunteer_id) for x in a.assignments] == [(x.role_id, x.volunteer_id) for x in b.assignments]
    assert [s.volunteer_id for s in a.standby] == [s.volunteer_id for s in b.standby]


# ---------------- Ready Crew (2026-11-19) ----------------
def test_ready_crew_with_standby_is_ready():
    role = RoleSpec(id="role-01", role="First aid", count=1, required_skills=["first_aid"])
    r = api.build_roster(_task([role]), [_v(1, skills={"first_aid": 3}), _v(2, skills={"first_aid": 2})])
    assert r.ready is True and r.recruit_requests == []


def test_single_point_of_failure_gives_exact_recruit_request():
    role = RoleSpec(id="role-01", role="First aid", count=1, required_skills=["first_aid"])
    r = api.build_roster(_task([role]), [_v(1, skills={"first_aid": 3})])
    assert r.ready is False and len(r.recruit_requests) == 1
    req = r.recruit_requests[0]
    assert (req.role_id, req.needed, req.skills, req.checked_skill_required, req.slot) == ("role-01", 1, ["first_aid"], True, "sat_morning")
    assert "Single point of failure" in req.reason


def test_unfilled_role_gives_recruit_request_with_count():
    role = RoleSpec(id="role-01", role="Coach", count=3, required_skills=["sports_coaching"])
    r = api.build_roster(_task([role]), [_v(1, skills={"sports_coaching": 2})])
    assert r.ready is False
    assert [(q.role_id, q.needed) for q in r.recruit_requests] == [("role-01", 2)]


def test_unresolved_role_assigns_nobody_and_asks_organiser():
    role = RoleSpec(id="role-01", role="Snake handler", count=1, required_skills=[], unresolved=True)
    r = api.build_roster(_task([role]), [_v(i) for i in range(1, 5)])
    assert r.assignments == [] and r.ready is False
    assert "could not match" in r.recruit_requests[0].reason


def test_opted_in_only_restricts_every_method_to_volunteers_who_chose_the_drive():
    role = RoleSpec(id="role-01", role="Helper", count=1, required_skills=[])
    vols = [_v(1, opted_in_task_ids=["task-x"]), _v(2), _v(3)]
    opts = RosterOptions(opted_in_only=True)
    for r in (api.build_roster(_task([role]), vols, opts), api.baseline_nearest_skill(_task([role]), vols, opts),
              api.baseline_manual_greedy(_task([role]), vols, opts)):
        assert {a.volunteer_id for a in r.assignments} <= {"v-001"}
