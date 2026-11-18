"""ONE shared set of roster metrics, used by every method so comparisons are fair.

No haversine helper exists anywhere else in this codebase (searched app/, including api.py and
main.py: only Assignment.distance_km exists as a schema field), so the great-circle distance
helper ``haversine_km`` is implemented here with the Python standard library ``math`` only.
Earth radius R = 6371.0088 km (mean radius). A tolerance of 1e-9 km is applied to the travel
limit to absorb floating point noise; a volunteer exactly at the boundary is eligible.

Eligibility (the SAME predicate used by metrics and by the honest baselines)
--------------------------------------------------------------------------
``is_eligible(volunteer, role, task)`` is True iff ALL of the following hold:
  1. availability: task.slot is in volunteer.available_slots;
  2. travel: haversine_km(volunteer, task) <= task.max_travel_km (+1e-9);
  0. a role marked unresolved (AI could not map it to known skills) accepts nobody until an organiser decides;
  3. qualification: if role.required_skills is empty there is no skill constraint; otherwise
     at least one required skill must be present in volunteer.skills at level >= role.min_level,
     OR be listed in volunteer.self_declared_skills. No level is stored for self-declared skills,
     so they are treated as qualifying at any min_level and the caller must FLAG them. For a role marked
     safety_critical (e.g. first aid, disaster response) self-declared skills NEVER qualify: only host-checked levels count
     (Assignment.flags += 'self_declared_skill');
  4. safety: if volunteer.is_minor (age < 18), task.allow_minors must be True AND
     volunteer.guardian_consent must be exactly True.

Metric definitions (computed from task + the full volunteer list + the returned roster)
----------------------------------------------------------------------------------------
* all slots = for every RoleSpec (BOTH 'must' and 'should', each slot equal weight),
  (role.id, index) for index in range(role.count). must slots = same, restricted to
  role.priority == 'must'.
* slots_filled = number of DISTINCT (role_id, slot_index) pairs in roster.assignments that
  name a known role, a valid index, a known volunteer and pass is_eligible. Duplicates of the
  same slot count once; an assignment of one volunteer to two slots is counted in both slots
  by this descriptive metric (the one-role-per-volunteer hard constraint is the solver's job).
* HEAD AMENDMENT A1: role_coverage, slots_filled and slots_required count MUST slots only;
  should_coverage reports 'should' slots separately (None if there are none). 1.0 if no must slots.
* robustness: for EACH distinct assigned volunteer v, form the rescue pool = all assigned
  volunteers except v, UNION roster.standby volunteers (unknown ids and duplicate ids ignored).
  The scenario passes iff EVERY must slot can be matched to a DISTINCT pool volunteer who is
  eligible for that slot's role, using fresh bipartite matching (Kuhn augmenting paths, stdlib
  only) over must slots. Reassignment across roles is allowed. robustness = passed scenarios /
  number of distinct assigned volunteers; 0.0 if there are no assigned volunteers and must
  slots exist, 1.0 if there are no must slots (vacuously covered).
* repeat_pick_share = share of DISTINCT assigned volunteers with times_picked_last_90d >= 3
  (0.0 if nobody is assigned).
* exposure_gini (HEAD AMENDMENT A1) = Gini of times_picked_last_90d over the task-ELIGIBLE
  candidate pool (eligible for at least one role), where selected people get +1 for this pick,
  so a planner cannot look fair just by picking only newcomers. Formula: sort x ascending, then
  G = 2 * sum((i+1) * x[i]) / (n * sum(x)) - (n+1)/n, i zero-based.
  0.0 if n == 0 or sum(x) == 0 (nobody exposed / nobody recently picked = perfectly fair).
  Lower is fairer; the maximum for n volunteers is (n-1)/n.
* district_spread = number of DISTINCT (district, block) pairs among distinct assigned
  volunteers (not the number of districts alone).
* novices = number of DISTINCT assigned volunteers with is_novice True (past_drives < 3).
* mentor_pairs = number of DISTINCT novice assigned volunteers who are assigned to at least
  one role with needs_experienced True that ALSO has at least one distinct assigned volunteer
  with can_mentor True (past_drives >= 5). Each novice is counted at most once.
* solve_ms and solver_status are timing/status fields owned by the caller; compute_metrics
  leaves them at their schema defaults.
"""
from __future__ import annotations

import math
from collections.abc import Iterable

from ..schemas import Assignment, RoleSpec, RosterMetrics, RosterResult, TaskSpec, Volunteer

EARTH_RADIUS_KM = 6371.0088
TRAVEL_EPS_KM = 1e-9


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two WGS84-style (lat, lon) points in degrees."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_KM * math.asin(math.sqrt(min(1.0, a)))


def distance_km(task: TaskSpec, volunteer: Volunteer) -> float:
    """Distance of a volunteer from the task site, rounded nowhere (raw float)."""
    return haversine_km(task.lat, task.lon, volunteer.lat, volunteer.lon)


def best_skill_level(volunteer: Volunteer, role: RoleSpec) -> int:
    """Highest confirmed level the volunteer holds among the role's required skills.

    Self-declared skills are eligible but have no stored level, so they score 0 here and are
    flagged separately by callers. Returns 0 when the role names no required skills.
    """
    return max((volunteer.skills.get(s, 0) for s in role.required_skills), default=0)


def is_eligible(volunteer: Volunteer, role: RoleSpec, task: TaskSpec) -> bool:
    """The single hard-constraint predicate shared by metrics and all baselines."""
    if task.slot not in volunteer.available_slots:
        return False
    if distance_km(task, volunteer) > task.max_travel_km + TRAVEL_EPS_KM:
        return False
    if role.unresolved:          # the AI could not map this role; an organiser must decide before anyone is assigned
        return False
    if role.required_skills:
        confirmed = any(volunteer.skills.get(s, 0) >= role.min_level for s in role.required_skills)
        declared = (not role.safety_critical) and any(s in volunteer.self_declared_skills for s in role.required_skills)
        if not (confirmed or declared):
            return False
    if volunteer.is_minor and not (task.allow_minors and volunteer.guardian_consent is True):
        return False
    return True


def _slot_list(roles: Iterable[RoleSpec], must_only: bool = False) -> list[tuple[str, int]]:
    return [(r.id, i) for r in roles if (not must_only or r.priority == "must") for i in range(r.count)]


def _rescue_matches(slots: list[tuple[str, int]], pool: list[Volunteer], roles_by_id: dict[str, RoleSpec],
                    task: TaskSpec) -> bool:
    """True iff every slot can be matched to a distinct eligible pool volunteer (Kuhn's algorithm)."""
    if not slots:
        return True
    adjacency: dict[str, list[tuple[str, int]]] = {
        v.id: [s for s in slots if is_eligible(v, roles_by_id[s[0]], task)] for v in pool
    }

    def augment(vid: str, seen: set[tuple[str, int]]) -> bool:
        for slot in adjacency[vid]:
            if slot in seen:
                continue
            seen.add(slot)
            owner = slot_owner.get(slot)
            if owner is None or augment(owner, seen):
                slot_owner[slot] = vid
                return True
        return False

    slot_owner: dict[tuple[str, int], str] = {}
    for vid in sorted(adjacency):
        if len(slot_owner) == len(slots):
            return True
        if adjacency[vid]:
            augment(vid, set())
    return len(slot_owner) == len(slots)


def _gini(values: list[int]) -> float:
    n = len(values)
    total = sum(values)
    if n == 0 or total == 0:
        return 0.0
    ordered = sorted(values)
    return (2.0 * sum((i + 1) * x for i, x in enumerate(ordered))) / (n * total) - (n + 1) / n


def compute_metrics(task: TaskSpec, volunteers: list[Volunteer], roster: RosterResult) -> RosterMetrics:
    """Compute every shared metric for one (task, candidates, roster) triple."""
    by_id = {v.id: v for v in volunteers}
    roles_by_id = {r.id: r for r in task.roles}
    all_slots = _slot_list(task.roles)
    must_slots = _slot_list(task.roles, must_only=True)

    filled_slots: set[tuple[str, int]] = set()
    for a in roster.assignments:
        role = roles_by_id.get(a.role_id)
        v = by_id.get(a.volunteer_id)
        if role is None or v is None or not (0 <= a.slot_index < role.count):
            continue
        if is_eligible(v, role, task):
            filled_slots.add((a.role_id, a.slot_index))

    assigned_ids: list[str] = []
    seen_ids: set[str] = set()
    for a in roster.assignments:
        if a.volunteer_id in by_id and a.volunteer_id not in seen_ids:
            assigned_ids.append(a.volunteer_id)
            seen_ids.add(a.volunteer_id)

    assigned = [by_id[vid] for vid in assigned_ids]
    n_assigned = len(assigned)

    # Robustness: drop each assigned volunteer in turn; the rescue pool is the rest of the
    # roster plus standby. A fresh matching checks that all MUST slots remain coverable.
    passed = 0
    for dropped in assigned:
        pool_ids = [vid for vid in assigned_ids if vid != dropped.id]
        for s in roster.standby:
            if s.volunteer_id in by_id and s.volunteer_id not in pool_ids:
                pool_ids.append(s.volunteer_id)
        pool = [by_id[vid] for vid in pool_ids]
        if _rescue_matches(must_slots, pool, roles_by_id, task):
            passed += 1
    if n_assigned:
        robustness = passed / n_assigned
    else:
        robustness = 1.0 if not must_slots else 0.0

    repeat_pick_share = (sum(1 for v in assigned if v.times_picked_last_90d >= 3) / n_assigned
                         if n_assigned else 0.0)
    # A1: Gini over the task-ELIGIBLE candidate pool (eligible for at least one role); selected people get +1.
    eligible_pool = [v for v in volunteers if any(is_eligible(v, r, task) for r in task.roles)]
    exposure_gini = _gini([v.times_picked_last_90d + (1 if v.id in seen_ids else 0) for v in eligible_pool])
    district_spread = len({(v.district, v.block) for v in assigned})
    novices = sum(1 for v in assigned if v.is_novice)

    novice_ids = {v.id for v in assigned if v.is_novice}
    mentor_ids = {v.id for v in assigned if v.can_mentor}
    paired_novices: set[str] = set()
    for role in task.roles:
        if not role.needs_experienced:
            continue
        role_novices = {a.volunteer_id for a in roster.assignments if a.role_id == role.id} & novice_ids
        role_mentors = {a.volunteer_id for a in roster.assignments if a.role_id == role.id} & mentor_ids
        if role_mentors:
            paired_novices |= role_novices
    mentor_pairs = len(paired_novices)

    must_set = set(must_slots)
    should_slots = [s for s in all_slots if s not in must_set]
    must_filled = len(filled_slots & must_set)
    should_filled = len(filled_slots - must_set)
    return RosterMetrics(
        role_coverage=(must_filled / len(must_slots) if must_slots else 1.0),
        slots_filled=must_filled,
        slots_required=len(must_slots),
        should_coverage=(should_filled / len(should_slots) if should_slots else None),
        robustness=robustness,
        repeat_pick_share=repeat_pick_share,
        exposure_gini=exposure_gini,
        district_spread=district_spread,
        novices=novices,
        mentor_pairs=mentor_pairs,
    )


__all__ = [
    "EARTH_RADIUS_KM", "TRAVEL_EPS_KM", "haversine_km", "distance_km", "best_skill_level",
    "is_eligible", "compute_metrics", "unfilled_slots",
]


def unfilled_slots(task: TaskSpec, volunteers: list[Volunteer], assignments: list[Assignment]) -> list[tuple[str, int]]:
    """MUST slots not filled by an eligible assignment, in role order (A1: report exact (role_id, slot_index))."""
    by_id = {v.id: v for v in volunteers}
    roles_by_id = {r.id: r for r in task.roles}
    filled = {(a.role_id, a.slot_index) for a in assignments
              if a.role_id in roles_by_id and a.volunteer_id in by_id
              and is_eligible(by_id[a.volunteer_id], roles_by_id[a.role_id], task)}
    return [s for s in _slot_list(task.roles, must_only=True) if s not in filled]
