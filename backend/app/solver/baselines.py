"""Honest, constraint-respecting baselines for the Fair Crew Planner.

Every baseline uses the SAME hard-constraint predicate (metrics.is_eligible) that metrics use:
availability in task.slot, qualification (any-of required skills at min_level, self-declared
skills allowed but flagged), haversine distance within task.max_travel_km, minors only with
guardian consent AND task.allow_minors, and at most one role per volunteer. Forced in/out are
honoured when a RosterOptions is supplied (or when the task object carries forced_in/forced_out
attributes). All three return a RosterResult with per-assignment plain-English reasons and
compute their metrics through the single shared metrics.compute_metrics.

The optional ``options`` argument is an extension: the api.py signatures (task, volunteers[,
seed]) keep working unchanged; a caller that has a RosterOptions can pass it to enforce
forced_in/forced_out on baselines too, so comparisons stay fair.
"""
from __future__ import annotations

import random
import time
from typing import Iterable

from ..schemas import (Assignment, Method, RosterMetrics, RosterOptions, RosterResult, RoleSpec,
                       StandbyPick, TaskSpec, Volunteer)
from .metrics import best_skill_level, compute_metrics, distance_km, is_eligible


def _forced_sets(task: TaskSpec, options: RosterOptions | None) -> tuple[list[str], set[str]]:
    """Forced ids from options when present, with task attributes as a compatibility fallback."""
    if options is not None:
        forced_in = list(options.forced_in)
        forced_out = set(options.forced_out)
    else:
        forced_in = list(getattr(task, "forced_in", None) or [])
        forced_out = set(getattr(task, "forced_out", None) or [])
    return forced_in, forced_out


def _candidates(pool: Iterable[Volunteer], role: RoleSpec, task: TaskSpec, used: set[str],
                forced_out: set[str]) -> list[Volunteer]:
    return [v for v in sorted(pool, key=lambda x: x.id)
            if v.id not in used and v.id not in forced_out and is_eligible(v, role, task)]


def _flags(v: Volunteer, role: RoleSpec) -> list[str]:
    flags: list[str] = []
    if any(s in v.self_declared_skills for s in role.required_skills):
        flags.append("self_declared_skill")
    if v.is_novice:
        flags.append("novice")
    if v.is_minor and v.guardian_consent is True:
        flags.append("minor_guardian_consent")
    return flags


def _reasons(v: Volunteer, role: RoleSpec, task: TaskSpec, how: str) -> list[str]:
    skills = ", ".join(role.required_skills) if role.required_skills else "any volunteer"
    return [
        f"{role.role}: qualifies for required skills ({skills}) at level {role.min_level}+.",
        f"Available in {task.slot} and {distance_km(task, v):.1f} km from the site "
        f"(limit {task.max_travel_km:.1f} km).",
        f"Selected by {how}: {v.past_drives} past drives, {v.times_picked_last_90d} picks "
        "in the last 90 days.",
    ]


def _assignment(v: Volunteer, role: RoleSpec, slot_index: int, task: TaskSpec, how: str,
                score: float) -> Assignment:
    return Assignment(
        role_id=role.id,
        slot_index=slot_index,
        volunteer_id=v.id,
        volunteer_name=v.display_name,
        score=score,
        distance_km=round(distance_km(task, v), 3),
        reasons=_reasons(v, role, task, how),
        flags=_flags(v, role),
    )


def _apply_forced_in(task: TaskSpec, volunteers: list[Volunteer], assignments: list[Assignment],
                     forced_in: list[str], forced_out: set[str], explanations: list[str],
                     how: str) -> None:
    """Place forced volunteers without breaking hard constraints; report impossible ones honestly."""
    by_id = {v.id: v for v in volunteers}
    roles_by_id = {r.id: r for r in task.roles}
    for vid in forced_in:
        v = by_id.get(vid)
        if v is None:
            explanations.append(f"forced_in {vid} is not in the candidate list; ignored.")
            continue
        if vid in forced_out:
            explanations.append(f"forced_in {vid} is also forced_out; both cannot be honoured.")
            continue
        if any(a.volunteer_id == vid for a in assignments):
            continue
        eligible_slots = [(r, i) for r in task.roles for i in range(r.count) if is_eligible(v, r, task)]
        empty = [(r, i) for r, i in eligible_slots
                 if not any(a.role_id == r.id and a.slot_index == i for a in assignments)]
        if empty:
            r, i = min(empty, key=lambda ri: distance_km(task, v))
            a = _assignment(v, r, i, task, how, 0.0)
            a.reasons.append("Included because the organiser forced this volunteer in.")
            assignments.append(a)
            continue
        replaceable = [(a, r) for a in assignments for r in [roles_by_id[a.role_id]]
                       if a.volunteer_id not in forced_in and is_eligible(v, r, task)]
        if replaceable:
            old, r = min(replaceable, key=lambda ar: (
                by_id[ar[0].volunteer_id].past_drives, -distance_km(task, by_id[ar[0].volunteer_id]),
                ar[0].role_id, ar[0].slot_index))
            replaced_name = old.volunteer_name
            old.volunteer_id = v.id
            old.volunteer_name = v.display_name
            old.distance_km = round(distance_km(task, v), 3)
            old.reasons = _reasons(v, r, task, how, 0.0) + [
                "Included because the organiser forced this volunteer in "
                f"(replaced {replaced_name} on {r.role})."
            ]
            old.flags = _flags(v, r)
            continue
        explanations.append(f"forced_in {v.display_name} has no slot they can take without "
                            "breaking availability, travel, safety or skill constraints; "
                            "left out rather than violating a hard constraint.")

    del roles_by_id  # kept for readability of the replacement branch; no state retained


def _finish(task: TaskSpec, volunteers: list[Volunteer], method: Method,
            assignments: list[Assignment], standby: list[StandbyPick], explanations: list[str],
            started: float) -> RosterResult:
    filled = {(a.role_id, a.slot_index) for a in assignments
              if any(r.id == a.role_id and 0 <= a.slot_index < r.count for r in task.roles)}
    unfilled = [r.id for r in task.roles if any((r.id, i) not in filled for i in range(r.count))]
    if unfilled:
        explanations.append("Unfilled role slots: " + ", ".join(unfilled) +
                             ". No eligible, unassigned volunteer was available; reported honestly.")
    roster = RosterResult(
        task_id=task.id,
        method=method,
        assignments=assignments,
        standby=standby,
        unfilled_role_ids=unfilled,
        metrics=RosterMetrics(role_coverage=0.0, slots_filled=0, slots_required=0,
                              robustness=0.0, repeat_pick_share=0.0, exposure_gini=0.0,
                              district_spread=0),
        explanations=explanations,
        synthetic=True,
    )
    roster.metrics = compute_metrics(task, volunteers, roster)
    roster.metrics.solve_ms = int((time.perf_counter() - started) * 1000)
    roster.metrics.solver_status = "baseline_complete" if not unfilled else "baseline_partial"
    return roster


def nearest_skill(task: TaskSpec, volunteers: list[Volunteer], options: RosterOptions | None = None
                  ) -> RosterResult:
    """Greedy: for each role/slot take the closest volunteer with any required skill."""
    started = time.perf_counter()
    forced_in, forced_out = _forced_sets(task, options)
    used: set[str] = set()
    assignments: list[Assignment] = []
    explanations: list[str] = ["Method nearest_skill: roles in task order, nearest qualified "
                               "unassigned volunteer each time; no fairness objective."]
    for role in task.roles:
        for i in range(role.count):
            candidates = _candidates(volunteers, role, task, used, forced_out)
            if not candidates:
                continue
            chosen = min(candidates, key=lambda v: (distance_km(task, v),
                                                    -best_skill_level(v, role), -v.past_drives, v.id))
            a = _assignment(chosen, role, i, task, "nearest_skill (distance first)",
                            -round(distance_km(task, chosen), 3))
            assignments.append(a)
            used.add(chosen.id)
    _apply_forced_in(task, volunteers, assignments, forced_in, forced_out,
                     explanations, "forced_in override")
    return _finish(task, volunteers, "nearest_skill", assignments, [], explanations, started)


def random_feasible(task: TaskSpec, volunteers: list[Volunteer], seed: int = 7,
                    options: RosterOptions | None = None) -> RosterResult:
    """Seeded random draw among volunteers who satisfy every hard constraint."""
    started = time.perf_counter()
    forced_in, forced_out = _forced_sets(task, options)
    rng = random.Random(seed)
    used: set[str] = set()
    assignments: list[Assignment] = []
    explanations: list[str] = [f"Method random_feasible: seeded random pick (seed={seed}) among "
                               "eligible unassigned volunteers; no fairness objective."]
    for role in task.roles:
        for i in range(role.count):
            candidates = _candidates(volunteers, role, task, used, forced_out)
            if not candidates:
                continue
            chosen = rng.choice(candidates)
            score = rng.random()
            assignments.append(_assignment(chosen, role, i, task,
                                           f"seeded random draw (seed={seed})", score))
            used.add(chosen.id)
    _apply_forced_in(task, volunteers, assignments, forced_in, forced_out,
                     explanations, "forced_in override")
    return _finish(task, volunteers, "random_feasible", assignments, [], explanations, started)


def manual_greedy(task: TaskSpec, volunteers: list[Volunteer], options: RosterOptions | None = None
                  ) -> RosterResult:
    """Careful organiser: most experienced volunteer per slot, plus one next-best backup per role."""
    started = time.perf_counter()
    forced_in, forced_out = _forced_sets(task, options)
    used: set[str] = set()
    backup_ids: set[str] = set()
    assignments: list[Assignment] = []
    standby: list[StandbyPick] = []
    explanations: list[str] = ["Method manual_greedy: roles in task order, most-experienced "
                               "eligible volunteer per slot, one next-best backup per role."]

    def rank(v: Volunteer, role: RoleSpec) -> tuple:
        return (-v.past_drives, -best_skill_level(v, role), distance_km(task, v), v.id)

    for role in task.roles:
        for i in range(role.count):
            candidates = _candidates(volunteers, role, task, used, forced_out)
            if not candidates:
                continue
            chosen = min(candidates, key=lambda v: rank(v, role))
            assignments.append(_assignment(chosen, role, i, task,
                                           "manual_greedy (most experienced first)",
                                           float(chosen.past_drives)))
            used.add(chosen.id)
        backups = [v for v in _candidates(volunteers, role, task, used, forced_out)
                   if v.id not in backup_ids]
        if backups:
            backup = min(backups, key=lambda v: rank(v, role))
            backup_ids.add(backup.id)
            reason = (f"Next-best backup for {role.role}: {backup.past_drives} past drives, "
                      f"{distance_km(task, backup):.1f} km away, available {task.slot}; "
                      "not used in the primary roster.")
            standby.append(StandbyPick(volunteer_id=backup.id, volunteer_name=backup.display_name,
                                       covers_role_ids=[role.id], reason=reason))

    _apply_forced_in(task, volunteers, assignments, forced_in, forced_out,
                     explanations, "forced_in override")
    # A forced-in override can change who is used; drop any standby that is now assigned.
    assigned_ids = {a.volunteer_id for a in assignments}
    standby = [s for s in standby if s.volunteer_id not in assigned_ids]
    return _finish(task, volunteers, "manual_greedy", assignments, standby, explanations, started)


# api.py-style aliases, so the interface module can wire either naming convention.
baseline_nearest_skill = nearest_skill
baseline_random_feasible = random_feasible
baseline_manual_greedy = manual_greedy

__all__ = [
    "nearest_skill", "random_feasible", "manual_greedy", "baseline_nearest_skill",
    "baseline_random_feasible", "baseline_manual_greedy",
]
