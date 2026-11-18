"""LANE B (U4, only if R3 verifies the spec): export a confirmed card as an Open Badges 3.0 / W3C VC compatible JSON. Unsigned; say so."""
from __future__ import annotations

from ..schemas import ContributionCard, Volunteer


def to_credential(card: ContributionCard, volunteer: Volunteer) -> dict:
    raise NotImplementedError
