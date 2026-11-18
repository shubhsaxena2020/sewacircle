"""Additive pytest fixtures for Lane A solver tests.

No global state mutation, no monkeypatching of other lanes, no import of modules
owned by parallel workers. Fixture names are prefixed with solver_ so future
conftest files in other lanes cannot collide with them.
"""
from __future__ import annotations

import pytest

from factories import VALID_SEED_COUNT, make_random_case, validate_case
from app.schemas import RoleSpec, RosterOptions, TaskSpec, Volunteer


@pytest.fixture
def solver_seed() -> int:
    """A single reproducible base seed for one test."""
    return 7


@pytest.fixture
def solver_case_factory():
    """Return make_random_case so tests can choose their own seeds/knobs."""
    return make_random_case


@pytest.fixture
def solver_case(solver_seed):
    """A modest (task, volunteers, options) triple with a guaranteed slot."""
    return make_random_case(solver_seed, n_volunteers=18)


@pytest.fixture
def solver_validator():
    """Return validate_case; empty result means internally consistent."""
    return validate_case


@pytest.fixture(params=range(VALID_SEED_COUNT))
def solver_seed_param(request) -> int:
    """Parametrized seed covering the full property-test sweep (one case per seed)."""
    return request.param
