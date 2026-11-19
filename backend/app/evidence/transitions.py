"""Contribution-card state machine: one table, one function, one exception.

Why a table
-----------
A contribution card is a claim about a person's unpaid work, so it must not be
able to skip a step or to be pushed backwards by accident. The host's review
used to be a one-way street (draft/flagged -> confirmed/corrected/rejected),
which meant a host who spotted a wrong hour count had to reject a genuine
contribution or confirm something they did not believe. This module adds one
back-edge - ``request_revision`` - so a host can send a card back for another
draft without destroying the record, and the volunteer's contribution is not
thrown away over a typo.

The legal moves are exactly one dict, ``TRANSITIONS``, keyed by
``(from_state, action) -> to_state``. Nothing else in the code base is allowed
to decide a target state: routes call :func:`next_state` and turn
:class:`IllegalTransition` into HTTP 409. Because it is a plain dict, a test can
enumerate every key to prove each legal edge works, and generated
``(state, action)`` pairs that are NOT keys to prove every illegal edge is
refused.

States and edges
----------------
``draft`` and ``flagged`` are the undecided pool produced by the drafting step
(``flagged`` means the deterministic rules raised a warn/block flag; a host
still decides). From either one a host may confirm, correct, reject, or ask for
a revision. ``revision_requested`` has exactly two outgoing edges, both internal:
``redraft`` back into ``draft`` when the new text is clean, and
``redraft_flagged`` into ``flagged`` when the new text still (or newly) raises a
warn/block rule flag. The choice is made by the drafting route from the flags, so
a redraft can never present a suspicious card as if it were unremarkable.
``confirmed``, ``corrected`` and ``rejected`` are terminal - a decision is final
in this prototype, and the ledger keeps the history instead.

``redraft`` and ``redraft_flagged`` are internal action names, not API verbs: the
drafting route performs them and records the ledger action ``draft`` or ``flag``
(the ledger keeps its original six action names plus ``request_revision``).
"""
from __future__ import annotations

CARD_STATES: tuple[str, ...] = (
    "draft",
    "flagged",
    "revision_requested",
    "confirmed",
    "corrected",
    "rejected",
)

#: The ONE transition table: (from_state, action) -> to_state.
TRANSITIONS: dict[tuple[str, str], str] = {
    ("draft", "confirm"): "confirmed",
    ("draft", "correct"): "corrected",
    ("draft", "reject"): "rejected",
    ("draft", "request_revision"): "revision_requested",
    ("flagged", "confirm"): "confirmed",
    ("flagged", "correct"): "corrected",
    ("flagged", "reject"): "rejected",
    ("flagged", "request_revision"): "revision_requested",
    ("revision_requested", "redraft"): "draft",
    ("revision_requested", "redraft_flagged"): "flagged",
}

#: A host decision that ends the card's life; nothing leaves these states.
TERMINAL_STATES: frozenset[str] = frozenset({"confirmed", "corrected", "rejected"})

#: Every action name that can appear as the second half of a table key.
KNOWN_ACTIONS: tuple[str, ...] = (
    "confirm",
    "correct",
    "reject",
    "request_revision",
    "redraft",
    "redraft_flagged",
)


class IllegalTransition(Exception):
    """Raised when a (state, action) pair has no edge in :data:`TRANSITIONS`.

    The message names the state, the action and the actions that *are* legal
    from that state, so an API client can show it to a host unchanged.
    """

    def __init__(self, status: str, action: str) -> None:
        legal = allowed_actions(status)
        super().__init__(
            f"illegal transition: cannot {action!r} a card in state {status!r}; "
            f"legal actions from {status!r}: "
            + (", ".join(legal) if legal else "none (final state)")
        )
        self.status = status
        self.action = action
        self.legal_actions = legal


def allowed_actions(status: str) -> tuple[str, ...]:
    """Return the action names that have an edge out of ``status``, sorted."""
    return tuple(sorted(action for (src, action) in TRANSITIONS if src == status))


def next_state(status: str, action: str) -> str:
    """Return the target state for one move, or raise :class:`IllegalTransition`.

    This is the only place a target state is chosen; API routes must not
    hard-code a target themselves.
    """
    try:
        return TRANSITIONS[(status, action)]
    except KeyError:
        raise IllegalTransition(status, action) from None


def is_terminal(status: str) -> bool:
    """True when no action may leave this state."""
    return status in TERMINAL_STATES
