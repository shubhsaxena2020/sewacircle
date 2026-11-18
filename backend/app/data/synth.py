"""LANE A: synthetic, labelled data. Deterministic with seed. Real district names/coordinates only from docs/research/up_districts.json."""
from __future__ import annotations

from ..schemas import TaskSpec, Volunteer


def make_volunteers(n: int = 40, seed: int = 7) -> list[Volunteer]:
    raise NotImplementedError


def make_tasks(seed: int = 7) -> list[TaskSpec]:
    """10 labelled test tasks (with ground-truth roles) used by eval and the demo."""
    raise NotImplementedError
