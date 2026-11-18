"""LANE A interface (solver). Replace the NotImplementedError bodies, keep the signatures. Implementation files live in solver/*.py."""
from __future__ import annotations

from ..schemas import Counterfactual, DropoutResult, RosterOptions, RosterResult, TaskSpec, Volunteer


def build_roster(task: TaskSpec, volunteers: list[Volunteer], options: RosterOptions | None = None) -> RosterResult:
    """CP-SAT roster (method='cp_sat'): role coverage, availability, travel, minors consent, rotation fairness (U2),
    mentor pairing (U2), standby for dropout resilience (U1). Must fill reasons[] per assignment in plain English."""
    raise NotImplementedError


def baseline_nearest_skill(task: TaskSpec, volunteers: list[Volunteer]) -> RosterResult:
    """Greedy: for each role pick the nearest volunteer with any required skill (method='nearest_skill'). Honest baseline."""
    raise NotImplementedError


def baseline_random_feasible(task: TaskSpec, volunteers: list[Volunteer], seed: int = 7) -> RosterResult:
    raise NotImplementedError


def baseline_manual_greedy(task: TaskSpec, volunteers: list[Volunteer]) -> RosterResult:
    """Simulates a human organiser: fills roles in order with the most-experienced available volunteer."""
    raise NotImplementedError


def simulate_dropout(task: TaskSpec, volunteers: list[Volunteer], roster: RosterResult, dropped_id: str,
                     options: RosterOptions | None = None) -> DropoutResult:
    """U1: remove dropped_id, heal with standby first, else re-solve. Report uncovered roles honestly."""
    raise NotImplementedError


def why_not(task: TaskSpec, volunteers: list[Volunteer], roster: RosterResult, volunteer_id: str,
            options: RosterOptions | None = None) -> Counterfactual:
    """U3: re-solve with the volunteer forced in; report feasibility, coverage/robustness deltas and who is displaced."""
    raise NotImplementedError
