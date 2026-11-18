"""LANE B: hash-chained audit ledger. A hash chain shows edits, not truth. Replace body, keep signatures."""
from __future__ import annotations

from ..schemas import ContributionCard, LedgerEntry, LedgerVerification


class Ledger:
    def __init__(self, path: str | None = None) -> None:
        raise NotImplementedError

    def append(self, action: str, card: ContributionCard, actor: str) -> LedgerEntry:
        raise NotImplementedError

    def entries(self) -> list[LedgerEntry]:
        raise NotImplementedError

    def verify(self) -> LedgerVerification:
        raise NotImplementedError
