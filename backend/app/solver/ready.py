"""Ready Crew: decide whether a roster is READY and turn every gap into an exact recruitment request.

READY means: every MUST slot is filled by an eligible person AND, for every single assigned person who drops out, the
remaining crew plus standby can still cover every MUST slot (robustness == 1.0, same definition as metrics.py).
Gaps become RecruitRequests derived from solver facts only (never from the LLM):
  * unfilled must slots  -> recruit N people with the role's skills, slot, area and travel limit;
  * single points of failure (a must-role holder whose dropout cannot be covered) -> recruit 1 standby for that role;
  * unresolved roles (AI could not map them to known skills) -> organiser decision needed; nobody is assigned.
"""
from __future__ import annotations

from ..schemas import RecruitRequest, RoleSpec, RosterResult, TaskSpec, Volunteer
from ..taxonomy import SKILLS
from .metrics import _rescue_matches, _slot_list


def _request(task: TaskSpec, role: RoleSpec, needed: int, reason: str) -> RecruitRequest:
    return RecruitRequest(role_id=role.id, role=role.role, needed=needed, skills=list(role.required_skills),
                          min_level=role.min_level, checked_skill_required=role.safety_critical, slot=task.slot,
                          area=f"{task.block}, {task.district}", max_travel_km=task.max_travel_km, reason=reason)


def annotate(task: TaskSpec, volunteers: list[Volunteer], roster: RosterResult) -> RosterResult:
    roles = {r.id: r for r in task.roles}
    by_id = {v.id: v for v in volunteers}
    requests: list[RecruitRequest] = []

    for r in task.roles:
        if r.unresolved:
            requests.append(_request(task, r, r.count, "The AI could not match this role to known skills. Choose the skills "
                                                        "(or mark it open to anyone) before anyone is assigned."))

    unfilled: dict[str, int] = {}
    for s in roster.unfilled_slots:
        if roles.get(s.role_id) is not None and not roles[s.role_id].unresolved:
            unfilled[s.role_id] = unfilled.get(s.role_id, 0) + 1
    for rid, n in unfilled.items():
        role = roles[rid]
        skill_txt = " or ".join(SKILLS[s].lower() for s in role.required_skills) or "no special skill"
        checked = " (host-checked, self-declared does not count)" if role.safety_critical else ""
        requests.append(_request(task, role, n, f"No eligible volunteer for {n} slot(s): needs {skill_txt}{checked}, "
                                                f"free {task.slot.replace('_', ' ')}, within {task.max_travel_km:.0f} km."))

    must_slots = _slot_list(task.roles, must_only=True)
    assigned = list(dict.fromkeys(a.volunteer_id for a in roster.assignments if a.volunteer_id in by_id))
    standby = [s.volunteer_id for s in roster.standby if s.volunteer_id in by_id]
    fragile_roles: dict[str, list[str]] = {}
    if not unfilled:
        for vid in assigned:
            pool = [by_id[x] for x in assigned if x != vid] + [by_id[x] for x in standby if x not in assigned]
            if not _rescue_matches(must_slots, pool, roles, task):
                held = next((a.role_id for a in roster.assignments if a.volunteer_id == vid), None)
                if held is not None and roles[held].priority == "must":
                    fragile_roles.setdefault(held, []).append(by_id[vid].display_name)
    for rid, names in fragile_roles.items():
        role = roles[rid]
        requests.append(_request(task, role, 1, f"Single point of failure: if {', '.join(names)} cannot come, nobody "
                                                f"qualified can step in as {role.role}. Recruit one standby."))

    roster.recruit_requests = requests
    roster.ready = (not unfilled) and (not fragile_roles) and not any(r.unresolved for r in task.roles) and bool(must_slots)
    if roster.ready:
        roster.explanations.append("READY: every essential role is filled and any one person can drop out without leaving a gap.")
    else:
        roster.explanations.append(f"NOT READY: {len(requests)} action(s) needed before this drive is safe to run.")
    return roster
