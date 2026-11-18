"""LANE A: evaluation harness. Run with: python -m eval.harness  (from backend/). Replace body, keep signature."""
from __future__ import annotations

from app.schemas import EvalReport, TaskSpec, Volunteer


def run_eval(volunteers: list[Volunteer], tasks: list[TaskSpec]) -> EvalReport:
    """Run cp_sat, nearest_skill, random_feasible, manual_greedy over every task; bootstrap 95% CIs; list misses honestly."""
    raise NotImplementedError
