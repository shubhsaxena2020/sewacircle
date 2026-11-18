"""Tests for the deterministic LANE B contribution-card rule engine.

Every name, id, ref and note below is SYNTHETIC. No real person or real event
is represented, and no test calls the network or an LLM. Attendance fixtures
are real app.schemas.AttendanceRow objects: `hours` is RECORDED attendance,
never the volunteer's claim (which lives on ContributionCard.claimed_hours).
A few tests deliberately pass odd legacy mappings to verify defensive reading.
"""
from __future__ import annotations

import inspect
from copy import deepcopy
from typing import get_type_hints

import pytest

from app.evidence import rules
from app.evidence.rules import check_card
from app.schemas import AttendanceRow, ContributionCard, Flag

ALL_CODES = {
    "hours_exceed_recorded",
    "no_attendance_record",
    "implausible_hours",
    "duplicate_evidence_ref",
    "identical_summary_text",
    "overlapping_tasks",
    "minor_without_guardian_consent",
    "self_declared_skill_unconfirmed",
    "round_number_inflation",
    "missing_evidence_ref",
}


def _card(card_id="SYN-C1", volunteer="SYN-V1", task="SYN-T1", hours=3.0,
          recorded=None, summary="SYNTHETIC: helped at the water stall",
          refs=None, status="draft", flags=None):
    if refs is None:
        refs = [f"SYNTHETIC-ref-{card_id}"]
    return ContributionCard(
        id=card_id, task_id=task, volunteer_id=volunteer, role="SYNTHETIC helper",
        claimed_hours=hours, recorded_hours=recorded, summary=summary,
        evidence_refs=list(refs), status=status, flags=list(flags or []),
    )


def _row(volunteer: str = "SYN-V1", task: str = "SYN-T1", hours: float = 3.0,
         check_in: str = "09:00", check_out: str = "12:00",
         age: int | None = None, guardian_consent: bool | None = None, **extra: object):
    """Build a real AttendanceRow; `extra` simulates legacy context keys."""
    row = AttendanceRow(
        volunteer_id=volunteer, task_id=task, hours=hours,
        check_in=check_in, check_out=check_out, age=age,
        guardian_consent=guardian_consent,
    )
    return _with_extras(row, **extra) if extra else row


def _codes(flags):
    return {flag.code for flag in flags}


def _with_extras(model, **extras):
    """Simulate optional context not present on the shared pydantic schemas."""
    object.__setattr__(model, "__pydantic_extra__", dict(extras))
    return model


# ------------------------------------------------- A1 typed-contract tests

def test_a1_check_card_signature_is_typed():
    assert rules.check_card is check_card
    signature = inspect.signature(check_card)
    assert list(signature.parameters) == ["card", "all_cards", "attendance_rows"]
    hints = get_type_hints(check_card)
    assert hints["card"] is ContributionCard
    assert hints["all_cards"] == list[ContributionCard]
    assert hints["attendance_rows"] == list[AttendanceRow]
    assert hints["return"] == list[Flag]
    assert "AttendanceRow" in str(signature.parameters["attendance_rows"].annotation)


def test_a1_row_hours_is_recorded_and_card_recorded_hours_is_ignored():
    # row.hours == claim: no gap, even when card.recorded_hours disagrees.
    card = _card(hours=5.0, recorded=1.0)
    assert "hours_exceed_recorded" not in _codes(check_card(card, [card], [_row(hours=5.0)]))

    # A generous card.recorded_hours must not hide a real gap against row.hours.
    card = _card(hours=4.0, recorded=24.0)
    flags = check_card(card, [card], [_row(hours=2.0)])
    assert "hours_exceed_recorded" in _codes(flags)
    assert "at most 2" in next(f.message for f in flags if f.code == "hours_exceed_recorded")


def test_a1_minor_rule_uses_typed_row_age_and_guardian_consent():
    assert "minor_without_guardian_consent" in _codes(check_card(_card(), [], [_row(age=17)]))
    assert "minor_without_guardian_consent" in _codes(
        check_card(_card(), [], [_row(age=17, guardian_consent=False)]))
    assert "minor_without_guardian_consent" not in _codes(
        check_card(_card(), [], [_row(age=17, guardian_consent=True)]))
    assert "minor_without_guardian_consent" not in _codes(check_card(_card(), [], [_row(age=18)]))


def test_a1_typed_row_consent_is_authoritative_over_legacy_card_context():
    card = _with_extras(_card(), age=17, guardian_consent=False)
    rows = [_row(age=17, guardian_consent=True)]
    assert "minor_without_guardian_consent" not in _codes(check_card(card, [card], rows))


def test_a1_iso_offsets_are_normalised_before_overlap_comparison():
    card = _card()
    # 09:00+05:30 == 03:30Z; both windows are 03:30Z-05:30Z.
    rows = [
        _row(task="SYN-T1", hours=2.0,
             check_in="2026-11-21T09:00:00+05:30", check_out="2026-11-21T11:00:00+05:30"),
        _row(task="SYN-T2", hours=2.0,
             check_in="2026-11-21T03:30:00Z", check_out="2026-11-21T05:30:00Z"),
    ]
    matches = [f for f in check_card(card, [card], rows) if f.code == "overlapping_tasks"]
    assert len(matches) == 1 and "SYN-T2" in matches[0].message


def test_a1_iso_offsets_non_overlap_and_naive_utc_equivalence():
    card = _card()
    rows = [
        _row(task="SYN-T1", hours=2.0,
             check_in="2026-11-21T09:00:00+05:30", check_out="2026-11-21T11:00:00+05:30"),
        _row(task="SYN-T2", hours=2.0,
             check_in="2026-11-21T06:00:00Z", check_out="2026-11-21T08:00:00Z"),
    ]
    assert "overlapping_tasks" not in _codes(check_card(card, [card], rows))

    # A naive timestamp is interpreted as UTC and compared with a Z timestamp.
    rows[1] = _row(task="SYN-T2", hours=2.0,
                   check_in="2026-11-21T04:00:00", check_out="2026-11-21T06:00:00")
    assert "overlapping_tasks" in _codes(check_card(card, [card], rows))


# ---------------------------------------------------------------- rule tests

def test_hours_exceed_recorded_positive():
    flags = check_card(_card(hours=4.0), [_card(hours=4.0)], [_row(hours=3.0)])
    matches = [f for f in flags if f.code == "hours_exceed_recorded"]
    assert len(matches) == 1 and matches[0].severity == "warn"


@pytest.mark.parametrize("claimed,expected", [(3.01, False), (3.02, True)])
def test_hours_exceed_recorded_epsilon_boundary(claimed, expected):
    flags = check_card(_card(hours=claimed), [], [_row(hours=3.0)])
    assert ("hours_exceed_recorded" in _codes(flags)) is expected


def test_no_attendance_record_positive():
    flags = check_card(_card(), [], [])
    matches = [f for f in flags if f.code == "no_attendance_record"]
    assert len(matches) == 1 and matches[0].severity == "warn"


def test_no_attendance_record_ignores_other_volunteers_and_tasks():
    rows = [_row(volunteer="SYN-V9"), _row(task="SYN-T9")]
    assert "no_attendance_record" in _codes(check_card(_card(), [], rows))


def test_implausible_hours_positive():
    flags = check_card(_card(hours=13.0), [], [_row(hours=13.0)])
    matches = [f for f in flags if f.code == "implausible_hours"]
    assert len(matches) == 1 and matches[0].severity == "block"
    assert "hours_exceed_recorded" not in _codes(flags)


def test_duplicate_evidence_ref_positive():
    first = _card(card_id="SYN-C1", summary="SYNTHETIC: first summary", refs=["SYNTHETIC-shared"])
    second = _card(card_id="SYN-C2", summary="SYNTHETIC: second summary", refs=["SYNTHETIC-shared"])
    flags = check_card(first, [first, second], [_row()])
    matches = [f for f in flags if f.code == "duplicate_evidence_ref"]
    assert len(matches) == 1 and matches[0].severity == "warn"


def test_identical_summary_text_positive():
    first = _card(card_id="SYN-C1", summary="SYNTHETIC: water stall")
    second = _card(card_id="SYN-C2", summary="SYNTHETIC: water stall")
    flags = check_card(first, [first, second], [_row()])
    matches = [f for f in flags if f.code == "identical_summary_text"]
    assert len(matches) == 1 and matches[0].severity == "warn"


@pytest.mark.parametrize("other_summary", [
    "  synthetic:   WATER   stall  ",
    "SYNTHETIC: WATER STALL",
])
def test_identical_summary_text_normalizes_case_and_whitespace(other_summary):
    first = _card(card_id="SYN-C1", summary="SYNTHETIC: water stall")
    second = _card(card_id="SYN-C2", summary=other_summary)
    assert "identical_summary_text" in _codes(check_card(first, [first, second], [_row()]))


def test_overlapping_tasks_positive_hhmm():
    card = _card()
    rows = [_row(task="SYN-T1", check_in="09:00", check_out="12:00"),
            _row(task="SYN-T2", check_in="11:00", check_out="14:00")]
    flags = check_card(card, [card], rows)
    matches = [f for f in flags if f.code == "overlapping_tasks"]
    assert len(matches) == 1 and matches[0].severity == "warn"
    assert "SYN-T2" in matches[0].message


def test_overlapping_tasks_positive_iso_datetime():
    card = _card()
    rows = [_row(task="SYN-T1", check_in="2026-11-21T09:00:00Z", check_out="2026-11-21T12:00:00Z"),
            _row(task="SYN-T2", check_in="2026-11-21T11:00:00+00:00",
                 check_out="2026-11-21T14:00:00+00:00")]
    assert "overlapping_tasks" in _codes(check_card(card, [card], rows))


def test_overlapping_tasks_non_overlap_and_touching_endpoints_are_clean():
    card = _card()
    rows = [_row(task="SYN-T1", check_in="09:00", check_out="11:00"),
            _row(task="SYN-T2", check_in="11:00", check_out="13:00")]
    assert "overlapping_tasks" not in _codes(check_card(card, [card], rows))


def test_overlapping_tasks_unparseable_or_inverted_times_do_not_false_flag():
    card = _card()
    rows = [_row(task="SYN-T1", check_in="not-a-time", check_out="whenever"),
            _row(task="SYN-T2", check_in="18:00", check_out="09:00")]
    assert "overlapping_tasks" not in _codes(check_card(card, [card], rows))


def test_overlapping_tasks_zero_length_window_is_skipped():
    card = _card()
    rows = [_row(task="SYN-T1", check_in="09:00", check_out="12:00"),
            _row(task="SYN-T2", check_in="10:00", check_out="10:00", hours=0.0)]
    assert "overlapping_tasks" not in _codes(check_card(card, [card], rows))


def test_overlapping_tasks_different_dates_are_skipped():
    card = _card()
    rows = [_row(task="SYN-T1", check_in="2026-11-21T09:00:00Z", check_out="2026-11-21T12:00:00Z"),
            _row(task="SYN-T2", check_in="2026-11-22T11:00:00Z", check_out="2026-11-22T14:00:00Z")]
    assert "overlapping_tasks" not in _codes(check_card(card, [card], rows))


def test_overlapping_tasks_mixed_date_precision_is_skipped():
    card = _card()
    rows = [_row(task="SYN-T1", check_in="09:00", check_out="12:00"),
            _row(task="SYN-T2", check_in="2026-11-21T11:00:00Z",
                 check_out="2026-11-21T14:00:00Z")]
    assert "overlapping_tasks" not in _codes(check_card(card, [card], rows))


def test_overlapping_tasks_different_volunteer_is_ignored():
    card = _card()
    rows = [_row(task="SYN-T1"), _row(volunteer="SYN-V9", task="SYN-T2", check_in="10:00")]
    assert "overlapping_tasks" not in _codes(check_card(card, [card], rows))


def test_minor_without_guardian_consent_positive():
    row = _row(age=17, guardian_consent=None)
    flags = check_card(_card(), [], [row])
    matches = [f for f in flags if f.code == "minor_without_guardian_consent"]
    assert len(matches) == 1 and matches[0].severity == "block"


def test_minor_with_guardian_consent_true_is_not_flagged():
    flags = check_card(_card(), [], [_row(age=17, guardian_consent=True)])
    assert "minor_without_guardian_consent" not in _codes(flags)


def test_minor_age_from_card_context():
    card = _with_extras(_card(), age=16, guardian_consent=False)
    flags = check_card(card, [card], [_row()])
    assert "minor_without_guardian_consent" in _codes(flags)


def test_self_declared_skill_unconfirmed_from_row():
    flags = check_card(_card(), [], [_row(self_declared_skills=["SYNTHETIC first aid"])])
    matches = [f for f in flags if f.code == "self_declared_skill_unconfirmed"]
    assert len(matches) == 1 and matches[0].severity == "info"


def test_self_declared_skill_unconfirmed_from_card_flag():
    card = _card(flags=[Flag(code="self_declared_skill", severity="info", message="SYNTHETIC note")])
    flags = check_card(card, [card], [_row()])
    assert "self_declared_skill_unconfirmed" in _codes(flags)


def test_round_number_inflation_positive():
    cards = [_card(card_id=f"SYN-C{i}", hours=3.0,
                   summary=f"SYNTHETIC: distinct summary {i}") for i in range(3)]
    flags = check_card(cards[0], cards, [_row()])
    matches = [f for f in flags if f.code == "round_number_inflation"]
    assert len(matches) == 1 and matches[0].severity == "info"


def test_round_number_inflation_needs_three_cards():
    cards = [_card(card_id=f"SYN-C{i}", hours=3.0,
                   summary=f"SYNTHETIC: distinct summary {i}") for i in range(2)]
    assert "round_number_inflation" not in _codes(check_card(cards[0], cards, [_row()]))


def test_round_number_inflation_needs_exact_integer():
    cards = [_card(card_id=f"SYN-C{i}", hours=3.5,
                   summary=f"SYNTHETIC: distinct summary {i}") for i in range(3)]
    assert "round_number_inflation" not in _codes(check_card(cards[0], cards, [_row()]))


def test_missing_evidence_ref_positive():
    flags = check_card(_card(refs=[]), [], [_row()])
    matches = [f for f in flags if f.code == "missing_evidence_ref"]
    assert len(matches) == 1 and matches[0].severity == "warn"


def test_missing_evidence_ref_ignores_blank_refs():
    assert "missing_evidence_ref" in _codes(check_card(_card(refs=["   "]), [], [_row()]))


# ------------------------------------------------------- cross-cutting tests

def test_clean_card_has_no_flags():
    card = _card()
    assert check_card(card, [card], [_row()]) == []


def test_only_info_severity_when_expectations_are_mild():
    cards = [_card(card_id=f"SYN-C{i}", hours=3.0,
                   summary=f"SYNTHETIC: distinct summary {i}") for i in range(3)]
    rows = [_row(self_declared_skills=["SYNTHETIC first aid"])]
    flags = check_card(cards[0], cards, rows)
    assert flags and {flag.severity for flag in flags} == {"info"}


def test_all_expected_codes_are_emitted_by_fixtures():
    seen = set()
    seen |= _codes(check_card(_card(hours=4.0), [], [_row(hours=3.0)]))                 # hours_exceed_recorded
    seen |= _codes(check_card(_card(), [], []))                                        # no_attendance_record
    seen |= _codes(check_card(_card(hours=13.0), [], [_row(hours=13.0)]))              # implausible_hours
    dupe_a = _card(card_id="SYN-C1", summary="SYNTHETIC: first", refs=["SYNTHETIC-shared"])
    dupe_b = _card(card_id="SYN-C2", summary="SYNTHETIC: second", refs=["SYNTHETIC-shared"])
    seen |= _codes(check_card(dupe_a, [dupe_a, dupe_b], [_row()]))                     # duplicate_evidence_ref
    same_a = _card(card_id="SYN-C3", summary="SYNTHETIC: same")
    same_b = _card(card_id="SYN-C4", summary="SYNTHETIC: same")
    seen |= _codes(check_card(same_a, [same_a, same_b], [_row()]))                     # identical_summary_text
    overlap = _card(card_id="SYN-C5", summary="SYNTHETIC: overlap")
    seen |= _codes(check_card(overlap, [overlap],
                              [_row(), _row(task="SYN-T2", check_in="11:00", check_out="14:00")]))
    seen |= _codes(check_card(_card(card_id="SYN-C6", summary="SYNTHETIC: minor"), [],
                              [_row(age=17)]))                                         # minor_without_guardian_consent
    seen |= _codes(check_card(_card(card_id="SYN-C7", summary="SYNTHETIC: skill"), [],
                              [_row(self_declared_skills=["SYNTHETIC first aid"])]))   # self_declared_skill_unconfirmed
    triple = [_card(card_id=f"SYN-C{i}", hours=3.0,
                    summary=f"SYNTHETIC: distinct {i}") for i in range(8, 11)]
    seen |= _codes(check_card(triple[0], triple, [_row()]))                            # round_number_inflation
    seen |= _codes(check_card(_card(card_id="SYN-C11", summary="SYNTHETIC: no ref", refs=[]),
                              [], [_row()]))                                           # missing_evidence_ref
    assert seen == ALL_CODES


def test_flags_carry_code_severity_and_message():
    card = _card(hours=13.0, refs=[])
    flags = check_card(card, [card], [_row(hours=3.0, age=17,
                                           self_declared_skills=["SYNTHETIC skill"])])
    assert flags
    for flag in flags:
        assert isinstance(flag.code, str) and flag.code
        assert flag.severity in {"info", "warn", "block"}
        assert isinstance(flag.message, str) and len(flag.message.strip()) > 10


def test_check_card_does_not_mutate_inputs_or_status():
    card = _card(hours=4.0, status="flagged",
                 flags=[Flag(code="SYNTHETIC-preexisting", severity="info", message="SYNTHETIC note")])
    other = _card(card_id="SYN-C2", summary="SYNTHETIC: another", refs=["SYNTHETIC-shared"])
    card.evidence_refs.append("SYNTHETIC-shared")
    rows = [_row(hours=3.0, age=17)]
    card_before, other_before, rows_before = deepcopy(card), deepcopy(other), deepcopy(rows)
    check_card(card, [other], rows)
    assert card == card_before and other == other_before and rows == rows_before
    assert card.status == "flagged"


def test_tolerant_odd_keys_and_missing_task_id_legacy_rows():
    card = _card(hours=4.0)
    odd_row = {"Volunteer ID": "SYN-V1", "Task ID": "SYN-T1", "Hours": "3.0",
               "Check In": "09:00", "Check Out": "12:00"}
    assert "hours_exceed_recorded" in _codes(check_card(card, [], [odd_row]))
    assert "no_attendance_record" not in _codes(check_card(card, [], [odd_row]))

    standard_dict = {"volunteer_id": "SYN-V1", "task_id": "SYN-T1", "hours": "3.0"}
    assert "hours_exceed_recorded" in _codes(check_card(card, [], [standard_dict]))

    volunteer_only = {"volunteerId": "SYN-V1", "hours": 3.0}
    assert "no_attendance_record" not in _codes(check_card(card, [], [volunteer_only]))


def test_check_card_is_deterministic_across_repeated_calls():
    card = _card(hours=4.0)
    rows = [_row(hours=3.0), _row(task="SYN-T2", check_in="11:00")]
    first = check_card(card, [card], rows)
    assert first == check_card(card, [card], rows) == check_card(card, [card], rows)


def test_empty_batch_and_rows_are_safe():
    assert isinstance(check_card(_card(), [], []), list)


def test_no_auto_rejection_and_rule_order_is_stable():
    card = _card(hours=13.0, refs=[])
    flags = check_card(card, [card], [_row(hours=3.0, age=17)])
    assert card.status == "draft"
    ordered_codes = [
        "hours_exceed_recorded", "no_attendance_record", "implausible_hours",
        "duplicate_evidence_ref", "identical_summary_text", "overlapping_tasks",
        "minor_without_guardian_consent", "self_declared_skill_unconfirmed",
        "round_number_inflation", "missing_evidence_ref",
    ]
    codes = [flag.code for flag in flags]
    assert codes == sorted(codes, key=ordered_codes.index)
