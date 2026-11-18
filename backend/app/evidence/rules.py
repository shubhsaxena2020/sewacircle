"""LANE B: deterministic rule checks for contribution cards (no AI). Replace body, keep signature."""
from __future__ import annotations

from ..schemas import ContributionCard, Flag


def check_card(card: ContributionCard, all_cards: list[ContributionCard], attendance_rows: list[dict]) -> list[Flag]:
    """Flags: hours claimed > recorded, duplicate evidence, impossible overlap, minor without consent, self-declared skill, etc."""
    raise NotImplementedError
