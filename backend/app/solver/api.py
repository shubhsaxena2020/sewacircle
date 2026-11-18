"""Solver interface used by the API and the eval harness. Implementations: cp_sat.py (head) and baselines.py (Lane A)."""
from __future__ import annotations

from ..schemas import Counterfactual, DropoutResult, RosterOptions, RosterResult, TaskSpec, Volunteer
from . import baselines, cp_sat


def build_roster(task: TaskSpec, volunteers: list[Volunteer], options: RosterOptions | None = None) -> RosterResult:
    return cp_sat.build_roster(task, volunteers, options)


def baseline_nearest_skill(task: TaskSpec, volunteers: list[Volunteer], options: RosterOptions | None = None) -> RosterResult:
    return baselines.nearest_skill(task, volunteers, options)


def baseline_random_feasible(task: TaskSpec, volunteers: list[Volunteer], seed: int = 7,
                             options: RosterOptions | None = None) -> RosterResult:
    return baselines.random_feasible(task, volunteers, seed, options)


def baseline_manual_greedy(task: TaskSpec, volunteers: list[Volunteer], options: RosterOptions | None = None) -> RosterResult:
    return baselines.manual_greedy(task, volunteers, options)


def simulate_dropout(task: TaskSpec, volunteers: list[Volunteer], roster: RosterResult, dropped_id: str,
                     options: RosterOptions | None = None) -> DropoutResult:
    return cp_sat.simulate_dropout(task, volunteers, roster, dropped_id, options)


def why_not(task: TaskSpec, volunteers: list[Volunteer], roster: RosterResult, volunteer_id: str,
            options: RosterOptions | None = None) -> Counterfactual:
    return cp_sat.why_not(task, volunteers, roster, volunteer_id, options)
