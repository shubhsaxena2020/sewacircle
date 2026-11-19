"""SewaCircle roster planner: OR-Tools CP-SAT with tiered objectives, standby selection, counterfactuals and dropout healing.

Hard constraints (shared with metrics.is_eligible, so solver, baselines and metrics agree):
availability in task.slot, travel <= task.max_travel_km, qualification (any required skill at >= min_level, or a
self-declared skill which is allowed but flagged), minors only with guardian consent and task.allow_minors,
one slot per volunteer, at most one volunteer per slot, forced_in / forced_out.

Objective, solved in sequential tiers so a lower tier can never outweigh a higher one (Codex contract review, A1 item 5):
  Tier 1  maximise filled MUST slots; fix that value.
  Tier 2  maximise filled SHOULD slots; fix that value.
  Tier 3  maximise a weighted quality score (all integer weights, documented in WEIGHTS):
          skill fit + proximity + fairness (U2: penalise volunteers picked >= 3 times in 90 days, small bonus for
          newcomers up to a cap) + newcomer-mentor pairing (U2) - small penalty for self-declared skills.
Standby (U1) is chosen after the roster with the SAME robustness definition used by metrics.compute_metrics:
greedily add the unassigned eligible volunteer that most improves single-dropout robustness, preferring less-used
people, until robustness is 1.0, no candidate helps, or the standby budget (number of MUST roles) is reached.
"""
from __future__ import annotations

import math
import time

from ortools.sat.python import cp_model

from ..i18n import reason_text
from ..schemas import (Assignment, Counterfactual, DropoutResult, PickReason, RoleSpec, RosterMetrics, RosterOptions,
                       RosterResult,
                       SlotRef, StandbyPick, TaskSpec, Volunteer)
from .metrics import best_skill_level, compute_metrics, distance_km, is_eligible, unfilled_slots

#: Fairness window used by the reason codes ("not picked in the last N days").
RECENT_PICK_DAYS = 90

WEIGHTS = {
    "skill_per_level": 30,       # confirmed level 1..3 of the best matching skill
    "self_declared": -12,        # allowed, but a confirmed skill is preferred
    "proximity_max": 20,         # scaled linearly: 20 at the site, 0 at max_travel_km
    "heavy_recent_pick": -40,    # U2 fairness: times_picked_last_90d >= 3
    "per_recent_pick": -4,       # U2 fairness: each recent pick lowers priority a little
    "newcomer": 12,              # U2: give newcomers a chance (capped by NEWCOMER_SHARE)
    "mentor_on_experienced_role": 15,
    "mentor_pair": 25,           # U2: newcomer and mentor together on a needs_experienced role
    "newcomer_excess": 20,       # U2: soft cap, penalty per newcomer beyond half the team
}
NEWCOMER_SHARE = 0.5  # soft target: beyond half the team, extra newcomers are penalised (never forbidden)
HEAVY = 3


def _slots(task: TaskSpec) -> list[tuple[RoleSpec, int]]:
    return [(r, i) for r in task.roles for i in range(r.count)]


def _quality(v: Volunteer, role: RoleSpec, task: TaskSpec, opts: RosterOptions) -> int:
    lvl = best_skill_level(v, role)
    q = WEIGHTS["skill_per_level"] * lvl
    if role.required_skills and lvl < role.min_level:   # qualifies only through a self-declared skill
        q += WEIGHTS["self_declared"]
    d = distance_km(task, v)
    q += int(round(WEIGHTS["proximity_max"] * max(0.0, 1.0 - d / max(task.max_travel_km, 0.1))))
    if opts.fairness:
        q += WEIGHTS["per_recent_pick"] * min(v.times_picked_last_90d, 10)
        if v.times_picked_last_90d >= HEAVY:
            q += WEIGHTS["heavy_recent_pick"]
        if v.is_novice:
            q += WEIGHTS["newcomer"]
    if role.needs_experienced and v.can_mentor:
        q += WEIGHTS["mentor_on_experienced_role"]
    return q


def _solver(seed: int, time_limit: float) -> cp_model.CpSolver:
    s = cp_model.CpSolver()
    s.parameters.num_search_workers = 1          # deterministic
    s.parameters.random_seed = seed
    s.parameters.max_time_in_seconds = max(0.5, time_limit)
    return s


def _status_name(code: int) -> str:
    return {cp_model.OPTIMAL: "OPTIMAL", cp_model.FEASIBLE: "FEASIBLE", cp_model.INFEASIBLE: "INFEASIBLE",
            cp_model.MODEL_INVALID: "MODEL_INVALID"}.get(code, "UNKNOWN")


def _solve_assignment(task: TaskSpec, vols: list[Volunteer], opts: RosterOptions
                      ) -> tuple[dict[tuple[str, int], Volunteer], str, list[str]]:
    """Returns ({(role_id, slot_index): volunteer}, status, explanations)."""
    notes: list[str] = []
    out_ids = set(opts.forced_out)
    pool = [v for v in vols if v.id not in out_ids]
    slots = _slots(task)
    elig = {(v.id, r.id, i): True for v in pool for (r, i) in slots if is_eligible(v, r, task)}
    m = cp_model.CpModel()
    x = {k: m.NewBoolVar(f"x_{k[0]}_{k[1]}_{k[2]}") for k in elig}
    for (r, i) in slots:                                   # one person per slot
        m.Add(sum(x[(v.id, r.id, i)] for v in pool if (v.id, r.id, i) in x) <= 1)
    by_v: dict[str, list] = {}
    for k, var in x.items():
        by_v.setdefault(k[0], []).append(var)
    for vid, vars_ in by_v.items():                       # one slot per person
        m.Add(sum(vars_) <= 1)
    for vid in opts.forced_in:                            # forced in: must take some eligible slot
        if vid in out_ids:
            continue
        if vid in by_v:
            m.Add(sum(by_v[vid]) == 1)
        else:
            notes.append(f"Forced volunteer {vid} has no slot they are eligible for; left out rather than breaking a hard constraint.")
    must = [(r, i) for (r, i) in slots if r.priority == "must"]
    should = [(r, i) for (r, i) in slots if r.priority != "must"]
    fill = lambda group: sum(x[(v.id, r.id, i)] for (r, i) in group for v in pool if (v.id, r.id, i) in x)  # noqa: E731
    solver = _solver(opts.seed, opts.time_limit_s / 3)
    status_codes: list[int] = []
    for group in (must, should):                          # tiers 1 and 2: lexicographic coverage
        if not group:
            continue
        m.Maximize(fill(group))
        st = solver.Solve(m)
        status_codes.append(st)
        if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return {}, _status_name(st), notes + ["The solver found no feasible roster (forced choices may conflict)."]
        m.Add(fill(group) >= int(round(solver.ObjectiveValue())))
    # tier 3: quality, fairness, mentoring
    terms = [_quality(next(v for v in pool if v.id == k[0]), next(r for r in task.roles if r.id == k[1]), task, opts) * var
             for k, var in x.items()]
    vol_by = {v.id: v for v in pool}
    if opts.fairness:
        novice_vars = [var for k, var in x.items() if vol_by[k[0]].is_novice]
        total_vars = list(x.values())
        if novice_vars:   # SOFT cap: newcomers beyond NEWCOMER_SHARE of the team are penalised, never forbidden,
            # because a hard cap could contradict the coverage already fixed in tiers 1-2 (found by a test: all-newcomer pool)
            excess = m.NewIntVar(0, len(total_vars), "newcomer_excess")
            m.Add(excess >= 2 * sum(novice_vars) - sum(total_vars) - 1)
            terms.append(-WEIGHTS["newcomer_excess"] * excess)
    if opts.mentor_pairing:
        for r in task.roles:
            if not r.needs_experienced or r.count < 2:
                continue
            nov = [var for k, var in x.items() if k[1] == r.id and vol_by[k[0]].is_novice]
            men = [var for k, var in x.items() if k[1] == r.id and vol_by[k[0]].can_mentor]
            if nov and men:
                p = m.NewBoolVar(f"pair_{r.id}")
                m.Add(p <= sum(nov))
                m.Add(p <= sum(men))
                terms.append(WEIGHTS["mentor_pair"] * p)
    m.Maximize(sum(terms))
    st = solver.Solve(m)
    status_codes.append(st)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {}, _status_name(st), notes
    chosen: dict[tuple[str, int], Volunteer] = {}
    for k, var in x.items():
        if solver.Value(var):
            chosen[(k[1], k[2])] = vol_by[k[0]]
    status = "OPTIMAL" if all(c == cp_model.OPTIMAL for c in status_codes) else "FEASIBLE"
    return chosen, status, notes


def _reasons(v: Volunteer, role: RoleSpec, task: TaskSpec, mentor_name: str | None) -> tuple[list[PickReason], list[str]]:
    """Structured pick reasons (code + params) and the flag labels they imply.

    The English sentences in ``Assignment.reasons`` are rendered from these codes with
    ``i18n.reason_text(code, "en")``, and the Hindi view from the same codes, so a fact that appears in
    one language cannot be missing from the other. Distance is stored raw (one value, rounded only when
    printed), so the whole-km figure is identical in both languages.
    """
    codes: list[PickReason] = []
    flags: list[str] = []
    confirmed = [(s, v.skills[s]) for s in role.required_skills if v.skills.get(s, 0) >= role.min_level]
    if confirmed:
        s, lvl = max(confirmed, key=lambda t: t[1])
        codes.append(PickReason(code="skill_confirmed", params={"skill": s, "level": lvl}))
    elif role.required_skills:
        s = next(s for s in role.required_skills if s in v.self_declared_skills)
        codes.append(PickReason(code="skill_self_declared", params={"skill": s}))
        flags.append("self_declared_skill")
    else:
        codes.append(PickReason(code="open_role"))
    codes.append(PickReason(code="slot_and_distance",
                            params={"slot": task.slot, "distance_km": distance_km(task, v)}))
    if v.times_picked_last_90d == 0:
        codes.append(PickReason(code="not_picked_recently", params={"days": RECENT_PICK_DAYS}))
    elif v.times_picked_last_90d >= HEAVY:
        codes.append(PickReason(code="picked_heavily",
                                params={"count": v.times_picked_last_90d, "days": RECENT_PICK_DAYS}))
    if v.is_novice:
        flags.append("novice")
        params: dict[str, str | int | float] = {"past_drives": v.past_drives}
        if mentor_name:
            params["mentor_name"] = mentor_name
        codes.append(PickReason(code="newcomer", params=params))
    elif role.needs_experienced and v.can_mentor:
        codes.append(PickReason(code="experienced_mentor", params={"past_drives": v.past_drives}))
    if v.is_minor:
        flags.append("minor_guardian_consent")
        codes.append(PickReason(code="minor_guardian_consent"))
    return codes, flags


def _reason_texts(codes: list[PickReason]) -> list[str]:
    """The canonical English sentences for a pick, rendered from the structured codes."""
    return [reason_text(code, "en") for code in codes]


def _standby(task: TaskSpec, vols: list[Volunteer], roster: RosterResult, opts: RosterOptions) -> list[StandbyPick]:
    must_roles = [r for r in task.roles if r.priority == "must"]
    budget = len(must_roles)
    assigned = {a.volunteer_id for a in roster.assignments}
    out = set(opts.forced_out)
    cands = [v for v in vols if v.id not in assigned and v.id not in out and any(is_eligible(v, r, task) for r in must_roles)]
    cands.sort(key=lambda v: (v.times_picked_last_90d if opts.fairness else 0, distance_km(task, v), v.id))
    picks: list[StandbyPick] = []
    current = compute_metrics(task, vols, roster).robustness
    while current < 1.0 and len(picks) < budget and cands:
        best, best_val = None, current
        for v in cands:
            trial = roster.model_copy(update={"standby": roster.standby + [StandbyPick(volunteer_id=v.id, volunteer_name=v.display_name, covers_role_ids=[])]})
            val = compute_metrics(task, vols, trial).robustness
            if val > best_val + 1e-12:
                best, best_val = v, val
        if best is None:
            break
        covers = [r.id for r in must_roles if is_eligible(best, r, task)]
        names = ", ".join(r.role for r in must_roles if r.id in covers)
        pick = StandbyPick(volunteer_id=best.id, volunteer_name=best.display_name, covers_role_ids=covers,
                           reason=f"Can step in for: {names}. Raises dropout robustness to {best_val:.0%}.")
        roster.standby.append(pick)
        picks.append(pick)
        cands.remove(best)
        current = best_val
    return picks


def build_roster(task: TaskSpec, volunteers: list[Volunteer], options: RosterOptions | None = None) -> RosterResult:
    opts = options or RosterOptions()
    t0 = time.perf_counter()
    chosen, status, notes = _solve_assignment(task, volunteers, opts)
    mentor_for: dict[str, str] = {}
    for r in task.roles:
        men = [v for (rid, _), v in chosen.items() if rid == r.id and v.can_mentor]
        for (rid, _), v in chosen.items():
            if rid == r.id and v.is_novice and men and r.needs_experienced:
                mentor_for[v.id] = men[0].display_name
    roles_by_id = {r.id: r for r in task.roles}
    assignments: list[Assignment] = []
    for (rid, i), v in sorted(chosen.items(), key=lambda kv: ([r.id for r in task.roles].index(kv[0][0]), kv[0][1])):
        codes, flags = _reasons(v, roles_by_id[rid], task, mentor_for.get(v.id))
        assignments.append(Assignment(role_id=rid, slot_index=i, volunteer_id=v.id, volunteer_name=v.display_name,
                                      score=float(_quality(v, roles_by_id[rid], task, opts)),
                                      distance_km=round(distance_km(task, v), 1), reasons=_reason_texts(codes),
                                      reason_codes=codes, flags=flags))
    open_slots = unfilled_slots(task, volunteers, assignments)
    roster = RosterResult(task_id=task.id, method="cp_sat", assignments=assignments, standby=[],
                          unfilled_role_ids=list(dict.fromkeys(r for r, _ in open_slots)),
                          unfilled_slots=[SlotRef(role_id=r, slot_index=i) for r, i in open_slots],
                          metrics=RosterMetrics(role_coverage=0, slots_filled=0, slots_required=0, robustness=0,
                                                repeat_pick_share=0, exposure_gini=0, district_spread=0),
                          explanations=list(notes), synthetic=True)
    if opts.resilience:
        _standby(task, volunteers, roster, opts)
    roster.metrics = compute_metrics(task, volunteers, roster)
    roster.metrics.solve_ms = int((time.perf_counter() - t0) * 1000)
    roster.metrics.solver_status = status
    if open_slots:
        roster.explanations.append("Unfilled: " + ", ".join(f"{roles_by_id[r].role} #{i + 1}" for r, i in open_slots)
                                   + ". No eligible volunteer was available; reported, not hidden.")
    if opts.resilience and roster.metrics.robustness < 1.0 and roster.assignments:
        roster.explanations.append(f"Dropout robustness is {roster.metrics.robustness:.0%}: not enough eligible standby people for every role.")
    return roster


def why_not(task: TaskSpec, volunteers: list[Volunteer], roster: RosterResult, volunteer_id: str,
            options: RosterOptions | None = None) -> Counterfactual:
    opts = options or RosterOptions()
    v = next((x for x in volunteers if x.id == volunteer_id), None)
    if v is None:
        return Counterfactual(volunteer_id=volunteer_id, volunteer_name="", feasible=False, narrative="Unknown volunteer.")
    if any(a.volunteer_id == volunteer_id for a in roster.assignments):
        return Counterfactual(volunteer_id=v.id, volunteer_name=v.display_name, feasible=True,
                              narrative=f"{v.display_name} is already on the roster.")
    blocking: list[str] = []
    eligible_roles = [r for r in task.roles if is_eligible(v, r, task)]
    if not eligible_roles:
        if task.slot not in v.available_slots:
            blocking.append(f"Not available on {task.slot.replace('_', ' ')}")
        d = distance_km(task, v)
        if d > task.max_travel_km:
            blocking.append(f"Lives {d:.0f} km away; the travel limit is {task.max_travel_km:.0f} km")
        if v.is_minor and not (task.allow_minors and v.guardian_consent is True):
            blocking.append("Under 18 without guardian consent, or the task does not allow minors")
        if not any(any(v.skills.get(s, 0) >= r.min_level or s in v.self_declared_skills for s in r.required_skills)
                   or not r.required_skills for r in task.roles):
            blocking.append("Has none of the skills any role needs")
        return Counterfactual(volunteer_id=v.id, volunteer_name=v.display_name, feasible=False, blocking_reasons=blocking,
                              narrative=f"{v.display_name} cannot be placed without breaking a hard rule: " + "; ".join(blocking) + ".")
    forced = opts.model_copy(update={"forced_in": list(dict.fromkeys(opts.forced_in + [v.id]))})
    alt = build_roster(task, volunteers, forced)
    placed = next((a for a in alt.assignments if a.volunteer_id == v.id), None)
    before = {a.volunteer_id for a in roster.assignments}
    after = {a.volunteer_id for a in alt.assignments}
    displaced = sorted(before - after)
    names = {x.id: x.display_name for x in volunteers}
    dcov = alt.metrics.role_coverage - roster.metrics.role_coverage
    drob = alt.metrics.robustness - roster.metrics.robustness
    if placed is None:
        return Counterfactual(volunteer_id=v.id, volunteer_name=v.display_name, feasible=False,
                              narrative=f"The solver could not fit {v.display_name} in without leaving a required slot empty.",
                              blocking_reasons=["No slot left after the higher-priority roles were filled"])
    role_name = next(r.role for r in task.roles if r.id == placed.role_id)
    parts = [f"{v.display_name} could take {role_name}."]
    if displaced:
        parts.append("That would take " + " and ".join(names[d] for d in displaced) + " off the roster.")
    parts.append(f"Role coverage {roster.metrics.role_coverage:.0%} -> {alt.metrics.role_coverage:.0%}; "
                 f"dropout robustness {roster.metrics.robustness:.0%} -> {alt.metrics.robustness:.0%}.")
    if abs(dcov) < 1e-9 and abs(drob) < 1e-9:
        mine = next((a.score for a in roster.assignments if a.role_id == placed.role_id), None)
        if mine is not None and placed.score < mine:
            parts.append(f"The planner preferred the current pick on fit, distance and fairness (score {mine:.0f} vs {placed.score:.0f}).")
    return Counterfactual(volunteer_id=v.id, volunteer_name=v.display_name, feasible=True, narrative=" ".join(parts),
                          delta_role_coverage=round(dcov, 4), delta_robustness=round(drob, 4), displaced_volunteer_ids=displaced)


def simulate_dropout(task: TaskSpec, volunteers: list[Volunteer], roster: RosterResult, dropped_id: str,
                     options: RosterOptions | None = None) -> DropoutResult:
    opts = options or RosterOptions()
    gone = next((a for a in roster.assignments if a.volunteer_id == dropped_id), None)
    if gone is None:
        return DropoutResult(task_id=task.id, dropped_volunteer_id=dropped_id, healed_with_standby=False,
                             uncovered_role_ids=[], roster_after=roster)
    roles_by_id = {r.id: r for r in task.roles}
    by_id = {v.id: v for v in volunteers}
    role = roles_by_id[gone.role_id]
    remaining = [a for a in roster.assignments if a.volunteer_id != dropped_id]
    # 1) direct standby promotion
    for sb in roster.standby:
        v = by_id.get(sb.volunteer_id)
        if v is not None and is_eligible(v, role, task):
            codes, flags = _reasons(v, role, task, None)
            promoted = [PickReason(code="promoted_from_standby")] + codes
            new = Assignment(role_id=role.id, slot_index=gone.slot_index, volunteer_id=v.id, volunteer_name=v.display_name,
                             score=float(_quality(v, role, task, opts)), distance_km=round(distance_km(task, v), 1),
                             reasons=_reason_texts(promoted), reason_codes=promoted, flags=flags)
            after = roster.model_copy(deep=True)
            after.assignments = sorted(remaining + [new], key=lambda a: ([r.id for r in task.roles].index(a.role_id), a.slot_index))
            after.standby = [s for s in roster.standby if s.volunteer_id != v.id]
            after.unfilled_slots = [SlotRef(role_id=r, slot_index=i) for r, i in unfilled_slots(task, volunteers, after.assignments)]
            after.unfilled_role_ids = list(dict.fromkeys(s.role_id for s in after.unfilled_slots))
            after.metrics = compute_metrics(task, volunteers, after)
            after.metrics.solver_status = "HEALED_WITH_STANDBY"
            after.explanations = [f"{gone.volunteer_name} dropped out; {v.display_name} stepped in from standby for {role.role}."]
            return DropoutResult(task_id=task.id, dropped_volunteer_id=dropped_id, healed_with_standby=True,
                                 replacement_volunteer_id=v.id, uncovered_role_ids=after.unfilled_role_ids, roster_after=after)
    # 2) standby joins and the team is reshuffled: re-solve with the remaining team plus standby forced in
    team = [a.volunteer_id for a in remaining]
    pool_in = team + [s.volunteer_id for s in roster.standby]
    keep = opts.model_copy(update={"forced_in": pool_in, "forced_out": list(dict.fromkeys(opts.forced_out + [dropped_id]))})
    after = build_roster(task, volunteers, keep)
    healed = not after.unfilled_role_ids and all(a.volunteer_id in pool_in for a in after.assignments)
    if not healed:   # 3) fall back to a fresh re-solve that keeps the remaining team
        keep = opts.model_copy(update={"forced_in": team, "forced_out": list(dict.fromkeys(opts.forced_out + [dropped_id]))})
        after = build_roster(task, volunteers, keep)
    moved = [a for a in after.assignments if (a.role_id, a.volunteer_id) not in {(b.role_id, b.volunteer_id) for b in remaining}]
    detail = "; ".join(f"{a.volunteer_name} -> {roles_by_id[a.role_id].role}" for a in moved)
    after.explanations.insert(0, f"{gone.volunteer_name} dropped out. " + ("Standby joined and the team was reshuffled: " if healed else "No standby fitted; the planner re-solved: ") + detail + ".")
    if healed:
        after.metrics.solver_status = "HEALED_WITH_STANDBY"
        rep = next((a.volunteer_id for a in after.assignments if a.volunteer_id in {s.volunteer_id for s in roster.standby}), None)
        return DropoutResult(task_id=task.id, dropped_volunteer_id=dropped_id, healed_with_standby=True,
                             replacement_volunteer_id=rep, uncovered_role_ids=after.unfilled_role_ids, roster_after=after)
    newcomer = next((a.volunteer_id for a in after.assignments if a.volunteer_id not in {x.volunteer_id for x in roster.assignments}), None)
    return DropoutResult(task_id=task.id, dropped_volunteer_id=dropped_id, healed_with_standby=False,
                         replacement_volunteer_id=newcomer, uncovered_role_ids=after.unfilled_role_ids, roster_after=after)
