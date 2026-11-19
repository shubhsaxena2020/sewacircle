"""Table tests for the contribution-card state machine (SYNTHETIC data, no network).

Every legal edge in ``transitions.TRANSITIONS`` gets its own test case, and every
``(state, action)`` pair that is NOT in the table gets its own refusal case, so a
future edit that adds or removes an edge immediately shows up as a changed test id.
"""
from __future__ import annotations

import itertools
from typing import get_args

import pytest

from app.evidence import transitions
from app.schemas import CardStatus

LEGAL_EDGES = sorted(transitions.TRANSITIONS.items())
ILLEGAL_EDGES = sorted(
    (state, action)
    for state, action in itertools.product(transitions.CARD_STATES, transitions.KNOWN_ACTIONS)
    if (state, action) not in transitions.TRANSITIONS
)


def test_table_covers_the_expected_number_of_edges():
    assert len(LEGAL_EDGES) == 10
    assert len(ILLEGAL_EDGES) == len(transitions.CARD_STATES) * len(transitions.KNOWN_ACTIONS) - 10


def test_every_key_and_target_is_a_declared_state():
    for (state, action), target in transitions.TRANSITIONS.items():
        assert state in transitions.CARD_STATES
        assert action in transitions.KNOWN_ACTIONS
        assert target in transitions.CARD_STATES


def test_states_match_the_contract_literal():
    """The table and schemas.CardStatus must not drift apart."""
    assert set(transitions.CARD_STATES) == set(get_args(CardStatus))


@pytest.mark.parametrize("edge,target", LEGAL_EDGES)
def test_legal_edge_returns_its_target(edge, target):
    state, action = edge
    assert transitions.next_state(state, action) == target


@pytest.mark.parametrize("state,action", ILLEGAL_EDGES)
def test_illegal_edge_is_refused_with_a_named_reason(state, action):
    with pytest.raises(transitions.IllegalTransition) as err:
        transitions.next_state(state, action)
    assert err.value.status == state
    assert err.value.action == action
    assert "illegal transition" in str(err.value)
    assert repr(state) in str(err.value) and repr(action) in str(err.value)


def test_terminal_states_have_no_outgoing_edge():
    for state in sorted(transitions.TERMINAL_STATES):
        assert transitions.allowed_actions(state) == ()
        assert transitions.is_terminal(state) is True


def test_a_state_with_no_outgoing_edge_is_declared_terminal():
    """The converse of the test above: 'terminal' means exactly 'no edge leaves here'."""
    exhausted = {state for state in transitions.CARD_STATES if transitions.allowed_actions(state) == ()}
    assert exhausted == set(transitions.TERMINAL_STATES)


def test_revision_requested_has_exactly_two_back_edges():
    """A clean redraft returns to draft; a redraft that trips a rule lands in flagged, never silently in draft."""
    assert transitions.allowed_actions("revision_requested") == ("redraft", "redraft_flagged")
    assert transitions.next_state("revision_requested", "redraft") == "draft"
    assert transitions.next_state("revision_requested", "redraft_flagged") == "flagged"
    assert transitions.is_terminal("revision_requested") is False


def test_no_other_state_has_a_redraft_edge():
    redrafts = {(state, action) for (state, action) in transitions.TRANSITIONS if action.startswith("redraft")}
    assert redrafts == {("revision_requested", "redraft"), ("revision_requested", "redraft_flagged")}


def test_undecided_states_offer_the_same_four_host_actions():
    expected = ("confirm", "correct", "reject", "request_revision")
    assert transitions.allowed_actions("draft") == expected
    assert transitions.allowed_actions("flagged") == expected


def test_illegal_message_for_a_final_state_says_so():
    with pytest.raises(transitions.IllegalTransition) as err:
        transitions.next_state("confirmed", "confirm")
    assert "final state" in str(err.value)
