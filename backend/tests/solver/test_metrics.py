"""Metric definitions on tiny hand-built cases. All data is SYNTHETIC.

Every expected number below is derived by hand in the test docstring; floats use a tight
pytest.approx tolerance only to absorb binary representation rounding.
"""
from __future__ import annotations

import pytest

from app.schemas import (Assignment, RosterMetrics, RosterResult, RoleSpec, StandbyPick, TaskSpec,
                         Volunteer)
from app.solver.metrics import compute_metrics, haversine_km


def V(vid, *, skills=None, past=0, times=0, district="D1", block="B1", lat=0.0, lon=0.0,
      slots=("sat_morning",), age=20, consent=None, declared=()):
    """Synthetic volunteer builder (test-local; nothing imported from synth.py)."""
    return Volunteer(id=vid, display_name=f"Vol {vid}", age=age, district=district, block=block,
                     lat=lat, lon=lon, skills=dict(skills or {}),
                     self_declared_skills=list(declared), languages=["hi"],
                     available_slots=list(slots), past_drives=past,
                     times_picked_last_90d=times, guardian_consent=consent, synthetic=True)


def T(roles, *, max_travel_km=1000.0, allow_minors=True):
    """Synthetic task centred at (0, 0); distances are therefore just the volunteer offset."""
    return TaskSpec(id="task-1", title="Metric fixture", district="D1", block="B1", lat=0.0, lon=0.0,
                    slot="sat_morning", max_travel_km=max_travel_km, allow_minors=allow_minors,
                    roles=roles, synthetic=True)


def A(role_id, index, vid):
    return Assignment(role_id=role_id, slot_index=index, volunteer_id=vid,
                      volunteer_name=f"Vol {vid}")


def R(task, assignments, standby=()):
    return RosterResult(task_id=task.id, method="nearest_skill", assignments=list(assignments),
                        standby=list(standby), unfilled_role_ids=[], synthetic=True,
                        metrics=RosterMetrics(role_coverage=0.0, slots_filled=0, slots_required=0,
                                              robustness=0.0, repeat_pick_share=0.0,
                                              exposure_gini=0.0, district_spread=0))


def test_haversine_known_distance():
    """One degree of longitude at the equator is 111.195 km with R = 6371.0088 km."""
    assert haversine_km(0.0, 0.0, 0.0, 1.0) == pytest.approx(111.1950802, abs=1e-6)


def test_perfect_coverage_fairness_and_partial_robustness():
    """Derivation: 3 required slots (r1 x2 must, r2 x1 should), all 3 valid -> 1.0 coverage.
    repeat_pick_share = 1/3 (only va has times_picked>=3; values 4,0,1).
    Gini of [4,0,1]: sorted [0,1,4], sum=5, n=3 ->
      2*(1*0+2*1+3*4)/(3*5) - 4/3 = 28/15 - 20/15 = 8/15 = 0.533333...
    district_spread = |{(A,X),(B,Y)}| = 2; novices = 1 (vb, past_drives=2).
    mentor_pairs = 1: r1 needs_experienced, novice vb shares it with mentor va (past 6).
    robustness = 1/3: dropping va leaves only vb qualified for r1's TWO slots (fail);
    dropping vb leaves only va (fail); dropping vc leaves va+vb (both slots match -> pass).
    """
    role_a = RoleSpec(id="r1", role="First aid", count=2, required_skills=["first_aid"],
                      min_level=1, priority="must", needs_experienced=True)
    role_b = RoleSpec(id="r2", role="Teaching", count=1, required_skills=["teaching_literacy"],
                      min_level=2, priority="should")
    task = T([role_a, role_b])
    volunteers = [V("va", skills={"first_aid": 3}, past=6, times=4, district="A", block="X"),
                  V("vb", skills={"first_aid": 2}, past=2, times=0, district="B", block="Y", lon=0.2),
                  V("vc", skills={"teaching_literacy": 3}, past=7, times=1, district="B", block="Y")]
    roster = R(task, [A("r1", 0, "va"), A("r1", 1, "vb"), A("r2", 0, "vc")])

    m = compute_metrics(task, volunteers, roster)
    # A1: coverage counts MUST slots only (r1 x2); r2 is 'should' and is reported in should_coverage.
    assert (m.slots_filled, m.slots_required) == (2, 2)
    assert m.role_coverage == 1.0 and m.should_coverage == 1.0
    assert m.robustness == pytest.approx(1 / 3, abs=1e-12)
    assert m.repeat_pick_share == pytest.approx(1 / 3, abs=1e-12)
    # A1: Gini over the eligible pool (va, vb, vc all eligible) with +1 for this pick: [5,1,2] -> 1/3
    assert m.exposure_gini == pytest.approx(1 / 3, abs=1e-12)
    assert m.district_spread == 2
    assert m.novices == 1
    assert m.mentor_pairs == 1


def test_standby_restores_robustness_but_ineligible_standby_does_not():
    """Same roster as above plus a qualified standby sd.
    Drop va -> vb+sd cover r1's two slots; drop vb -> va+sd; drop vc -> va+vb. All pass: 3/3.
    Replacing sd with an unavailable volunteer (slots=sun_morning only) leaves the original
    1/3: standby is part of the rescue pool ONLY if it satisfies the same hard constraints.
    """
    role_a = RoleSpec(id="r1", role="First aid", count=2, required_skills=["first_aid"],
                      min_level=1, priority="must", needs_experienced=True)
    role_b = RoleSpec(id="r2", role="Teaching", count=1, required_skills=["teaching_literacy"],
                      min_level=1, priority="should")
    task = T([role_a, role_b])
    base = [V("va", skills={"first_aid": 3}, past=6), V("vb", skills={"first_aid": 2}, past=2),
            V("vc", skills={"teaching_literacy": 3}, past=7)]
    assignments = [A("r1", 0, "va"), A("r1", 1, "vb"), A("r2", 0, "vc")]

    good = V("sd", skills={"first_aid": 2}, past=4)
    good_roster = R(task, assignments, [StandbyPick(volunteer_id="sd", volunteer_name="Vol sd",
                                                    covers_role_ids=["r1"])])
    assert compute_metrics(task, base + [good], good_roster).robustness == 1.0

    bad = V("bad", skills={"first_aid": 3}, slots=("sun_morning",))
    bad_roster = R(task, assignments, [StandbyPick(volunteer_id="bad", volunteer_name="Vol bad",
                                                   covers_role_ids=["r1"])])
    assert compute_metrics(task, base + [bad], bad_roster).robustness == pytest.approx(1 / 3)


def test_partial_coverage_ineligible_assignment_and_empty_roster():
    """Two must slots, only va qualified. The assignment of vb (no skills) is NOT a filled slot:
    slots_filled=1, slots_required=2, coverage=0.5. vb still counts as an assigned volunteer for
    fairness denominators (2 distinct assigned), but cannot rescue va's dropout, so robustness=0:
    drop va -> only vb (ineligible); drop vb -> only va (cannot fill TWO distinct slots).
    Empty roster: coverage 0/2=0, robustness 0, all distribution metrics 0.
    """
    role = RoleSpec(id="r1", role="First aid", count=2, required_skills=["first_aid"], min_level=1)
    task = T([role])
    volunteers = [V("va", skills={"first_aid": 3}, past=5, times=3, district="A"),
                  V("vb", skills={}, past=1, times=0, district="B")]
    partial = R(task, [A("r1", 0, "va"), A("r1", 1, "vb")])
    m = compute_metrics(task, volunteers, partial)
    assert (m.slots_filled, m.slots_required) == (1, 2)
    assert m.role_coverage == 0.5
    assert m.robustness == 0.0
    assert m.repeat_pick_share == 0.5
    assert m.district_spread == 2

    empty = R(task, [])
    e = compute_metrics(task, volunteers, empty)
    assert (e.role_coverage, e.slots_filled, e.slots_required, e.robustness) == (0.0, 0, 2, 0.0)
    assert (e.repeat_pick_share, e.exposure_gini, e.district_spread, e.novices, e.mentor_pairs) == (0.0, 0.0, 0, 0, 0)


def test_matching_requires_distinct_volunteers():
    """Three must slots and exactly three qualified volunteers. Dropping any one leaves only two
    eligible people for three distinct slots -> 0/3 scenarios pass, even though the survivor is
    qualified for every individual slot. Adding a qualified standby makes all drops healable:
    two survivors + one standby = three distinct volunteers -> robustness 1.0.
    """
    role = RoleSpec(id="r1", role="First aid", count=3, required_skills=["first_aid"], min_level=1)
    task = T([role])
    base = [V(v, skills={"first_aid": 2}) for v in ("va", "vb", "vc")]
    assignments = [A("r1", i, v) for i, v in enumerate(("va", "vb", "vc"))]
    assert compute_metrics(task, base, R(task, assignments)).robustness == 0.0

    sd = V("sd", skills={"first_aid": 2})
    with_standby = R(task, assignments, [StandbyPick(volunteer_id="sd", volunteer_name="Vol sd",
                                                     covers_role_ids=["r1"])])
    assert compute_metrics(task, base + [sd], with_standby).robustness == 1.0


def test_gini_extremes():
    """Four assigned volunteers, one role with four unconstrained slots.
    Equal exposures [2,2,2,2] -> G=0 (and repeat share 0, all >=3 is false).
    Maximal inequality [0,0,0,9]: sorted sum=9, n=4 ->
      2*(0+0+0+4*9)/(4*9) - 5/4 = 2 - 1.25 = 0.75; repeat share = 1/4.
    All-zero exposures -> G=0 by the documented convention (division by zero avoided).
    """
    role = RoleSpec(id="r1", role="General help", count=4)
    task = T([role])
    assignments = [A("r1", i, f"v{i}") for i in range(4)]

    equal = [V(f"v{i}", times=2) for i in range(4)]
    m = compute_metrics(task, equal, R(task, assignments))
    assert m.exposure_gini == 0.0 and m.repeat_pick_share == 0.0

    skewed = [V("v0", times=0), V("v1", times=0), V("v2", times=0), V("v3", times=9)]
    m = compute_metrics(task, skewed, R(task, assignments))
    # A1: eligible pool with +1 for this pick -> [1,1,1,10]: 2*(1+2+3+40)/(4*13) - 5/4 = 27/52
    assert m.exposure_gini == pytest.approx(27 / 52, abs=1e-12)
    assert m.repeat_pick_share == 0.25

    zero = [V(f"v{i}", times=0) for i in range(4)]
    assert compute_metrics(task, zero, R(task, assignments)).exposure_gini == 0.0


def test_district_spread_novices_and_mentor_pairs():
    """Four valid assignments in three distinct (district, block) pairs:
    (A,X), (A,Y), (B,X), (B,X) -> district_spread = 3 (block matters, not just district).
    Novices (past_drives<3): v2 (1) and v3 (2) -> 2. Mentors (past_drives>=5): v1 (5), v4 (6).
    mentor_pairs = 1: only r1 needs_experienced and has novice v2 alongside mentor v1; r2 is
    not flagged needs_experienced, so v3+v4 there does not count.
    robustness = 2/4 = 0.5: dropping v1 or v2 leaves only one first-aider for r1's two slots;
    dropping v3 or v4 leaves v1+v2 able to cover r1.
    """
    r1 = RoleSpec(id="r1", role="First aid", count=2, required_skills=["first_aid"],
                  priority="must", needs_experienced=True)
    r2 = RoleSpec(id="r2", role="Teaching", count=2, required_skills=["teaching_literacy"],
                  priority="should")
    task = T([r1, r2])
    volunteers = [V("v1", skills={"first_aid": 3}, past=5, district="A", block="X"),
                  V("v2", skills={"first_aid": 1}, past=1, district="A", block="Y"),
                  V("v3", skills={"teaching_literacy": 2}, past=2, district="B", block="X"),
                  V("v4", skills={"teaching_literacy": 2}, past=6, district="B", block="X")]
    roster = R(task, [A("r1", 0, "v1"), A("r1", 1, "v2"), A("r2", 0, "v3"), A("r2", 1, "v4")])
    m = compute_metrics(task, volunteers, roster)
    assert m.district_spread == 3
    assert m.novices == 2
    assert m.mentor_pairs == 1
    assert m.robustness == 0.5
    # A1: MUST slots only (r1 x2); r2 x2 is 'should' -> should_coverage
    assert (m.slots_filled, m.slots_required, m.role_coverage) == (2, 2, 1.0)
    assert m.should_coverage == 1.0
