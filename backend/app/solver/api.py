"""Solver interface used by the API and the eval harness. Implementations: cp_sat.py (head) and baselines.py (Lane A)."""
from __future__ import annotations

from ..schemas import Counterfactual, DropoutResult, RosterOptions, RosterResult, TaskSpec, Volunteer
from . import baselines, cp_sat, ready


def candidate_pool(task: TaskSpec, volunteers: list[Volunteer], options: RosterOptions | None) -> list[Volunteer]:
    """Ready Crew: with opted_in_only, every method (cp_sat AND baselines) plans only with volunteers who chose this drive."""
    if options is not None and options.opted_in_only:
        return [v for v in volunteers if task.id in v.opted_in_task_ids]
    return volunteers


def build_roster(task: TaskSpec, volunteers: list[Volunteer], options: RosterOptions | None = None) -> RosterResult:
    pool = candidate_pool(task, volunteers, options)
    return ready.annotate(task, pool, cp_sat.build_roster(task, pool, options))


def baseline_nearest_skill(task: TaskSpec, volunteers: list[Volunteer], options: RosterOptions | None = None) -> RosterResult:
    pool = candidate_pool(task, volunteers, options)
    return ready.annotate(task, pool, baselines.nearest_skill(task, pool, options))


def baseline_random_feasible(task: TaskSpec, volunteers: list[Volunteer], seed: int = 7,
                             options: RosterOptions | None = None) -> RosterResult:
    pool = candidate_pool(task, volunteers, options)
    return ready.annotate(task, pool, baselines.random_feasible(task, pool, seed, options))


def baseline_manual_greedy(task: TaskSpec, volunteers: list[Volunteer], options: RosterOptions | None = None) -> RosterResult:
    pool = candidate_pool(task, volunteers, options)
    return ready.annotate(task, pool, baselines.manual_greedy(task, pool, options))


def simulate_dropout(task: TaskSpec, volunteers: list[Volunteer], roster: RosterResult, dropped_id: str,
                     options: RosterOptions | None = None) -> DropoutResult:
    pool = candidate_pool(task, volunteers, options)
    r = cp_sat.simulate_dropout(task, pool, roster, dropped_id, options)
    r.roster_after = ready.annotate(task, pool, r.roster_after)
    return r


def why_not(task: TaskSpec, volunteers: list[Volunteer], roster: RosterResult, volunteer_id: str,
            options: RosterOptions | None = None) -> Counterfactual:
    return cp_sat.why_not(task, candidate_pool(task, volunteers, options), roster, volunteer_id, options)
