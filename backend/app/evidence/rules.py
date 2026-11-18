"""LANE B - deterministic rule checks for contribution cards (no AI, no network).

``check_card(card, all_cards, attendance_rows)`` returns ``Flag(code, severity,
message)`` objects. It is pure: it never calls an LLM, the network, the clock or
a random generator, and it never mutates the card, the other cards, the rows,
or ``card.status``. A host (not this module) decides what a flag means; nothing
is auto-rejected. All example volunteer/task data in this lane is SYNTHETIC.

Rule catalogue (code | severity | deterministic definition)
------------------------------------------------------------
hours_exceed_recorded | warn
    AttendanceRow.hours is the RECORDED hours from the attendance sheet,
    NEVER the volunteer's claim. If claimed_hours > row.hours + 0.01 this
    rule flags the gap; the 0.01 epsilon tolerates rounding. If several rows
    match, the largest row.hours is used (a conservative choice that avoids
    flagging split attendance records). card.recorded_hours is never used as
    the comparison source: only attendance rows are.
no_attendance_record | warn
    No attendance row is attributable to (volunteer_id, task_id).
implausible_hours | block
    claimed_hours > 12 in a day (strictly greater).
duplicate_evidence_ref | warn
    A non-blank evidence ref on this card also appears on another card in the
    submitted batch. Refs are compared after strip() + casefold().
identical_summary_text | warn
    The normalized summary (strip + casefold + collapse whitespace) is
    non-empty and identical to the normalized summary of another card in the
    batch. Catches copy-paste claims.
overlapping_tasks | warn
    From AttendanceRow.check_in / check_out (ISO-8601 strings, with an
    optional offset), the same volunteer has strictly overlapping windows on
    two DIFFERENT task ids, one of which is this card's task. Timezone rule:
    naive values are interpreted as UTC and offset-aware values are converted
    to UTC, then both are stored as (date ordinal, minute-of-day) in that
    common UTC-ish clock - so 09:00+05:30 and 03:30Z denote the same instant.
    Windows are compared only when both dates are equal after UTC
    normalisation, or both are time-only; inverted / zero-length / unparseable
    windows are skipped rather than false-flagged.
minor_without_guardian_consent | block
    A matching AttendanceRow with age < 18 and guardian_consent is not exactly
    True. Legacy card/row context (age / is_minor) is consulted only when no
    matching typed row supplies an age; it never overrides a typed row's
    guardian_consent.
self_declared_skill_unconfirmed | info
    A matching row or the card context carries self_declared_skills, or a flag
    labelled self_declared_skill. Informational: self-declaration is normal,
    it simply needs host confirmation.
round_number_inflation | info
    claimed_hours is an exact whole number AND at least 3 cards in the batch
    (including this one) claim exactly that same value. Round shifts (e.g. 3 h)
    are completely ordinary, so this is a soft nudge to spot-check, never a
    block and never evidence of wrongdoing.
missing_evidence_ref | warn (10th rule, chosen by this implementation)
    The card has no non-blank evidence_refs. A card with no pointer to an
    artifact (photo, signed sheet, host note) cannot be independently checked,
    so the host should be nudged to attach one. It is only a warning because
    small, low-risk activities may legitimately have no saved artifact and
    because hosts can still confirm the card manually.

Matching of attendance rows is intentionally tolerant: the public signature is
typed (list[AttendanceRow]) and tests use real AttendanceRow objects, but odd
legacy dict-like rows are still read defensively via model_validate where
possible and otherwise via case-insensitive, punctuation-collapsed alias
lookups (e.g. Volunteer ID / volunteerId, hours / recorded_hours). Ids are
compared as stripped, casefolded strings, and rows missing a task id still
match on a volunteer id. Rows with neither id are ignored.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from ..schemas import AttendanceRow, ContributionCard, Flag

HOURS_EPSILON = 0.01
MAX_DAILY_HOURS = 12.0
ROUND_CLUSTER_MIN_CARDS = 3

_MISSING = object()

# Alias groups are normalized with _norm_key before lookup, so both "volunteer_id"
# and "Volunteer ID" / "volunteerId" resolve to the same key.
_VOLUNTEER_KEYS = ("volunteer_id", "volunteer", "volunteerid", "vol_id", "vid",
                   "participant_id", "person_id", "user_id")
_TASK_KEYS = ("task_id", "task", "taskid", "tid", "activity_id", "activity")
_HOURS_KEYS = ("recorded_hours", "hours", "logged_hours", "hours_logged", "actual_hours")
_AGE_KEYS = ("age", "volunteer_age", "participant_age", "years_old")
_CONSENT_KEYS = ("guardian_consent", "guardianconsent", "guardian_consent_given",
                 "parental_consent", "consent")
_CHECK_IN_KEYS = ("check_in", "checkin", "start_time", "start", "time_in", "in_time", "begin")
_CHECK_OUT_KEYS = ("check_out", "checkout", "end_time", "end", "time_out", "out_time", "finish")
_SELF_DECLARED_KEYS = ("self_declared_skills", "self_declared_skill", "selfdeclaredskills")
_FLAGS_KEYS = ("flags", "labels", "tags", "solver_flags")
_MINOR_KEYS = ("is_minor", "minor", "under_18")

_SELF_DECLARED_TOKENS = frozenset({
    "self_declared_skill", "selfdeclaredskill", "self declared skill",
    "self_declared_skills", "selfdeclaredskills", "self declared skills",
})

_NUMBER_PREFIX = re.compile(r"^\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))")
_HHMM = re.compile(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?$")


def _norm_key(key: Any) -> str:
    """Normalize a mapping key so odd spellings still match an alias."""
    return re.sub(r"[^a-z0-9]+", "_", str(key).strip().casefold()).strip("_")


def _normalized_mapping(source: Any) -> dict[str, Any]:
    if not isinstance(source, dict):
        return {}
    out: dict[str, Any] = {}
    for key, value in source.items():
        normalized = _norm_key(key)
        if normalized and normalized not in out:
            out[normalized] = value
    return out


def _get(source: Any, aliases: tuple[str, ...], default: Any = None) -> Any:
    """Fetch an alias from a dict-like row, model, or model extras."""
    mappings = []
    if isinstance(source, dict):
        mappings.append(_normalized_mapping(source))
    else:
        extra = getattr(source, "model_extra", None)
        if extra:
            mappings.append(_normalized_mapping(extra))
        fields = getattr(source, "__dict__", None)
        if fields:
            mappings.append(_normalized_mapping(fields))
    for mapping in mappings:
        for alias in aliases:
            key = _norm_key(alias)
            if key in mapping:
                return mapping[key]
    return default


def _as_id(value: Any) -> str | None:
    if value is None or isinstance(value, (list, tuple, dict, set)):
        return None
    text = str(value).strip().casefold()
    return text or None


def _as_number(value: Any) -> float | None:
    """Parse a finite number, tolerating strings like '3.5 hours'."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
    else:
        match = _NUMBER_PREFIX.match(str(value).strip())
        if not match:
            return None
        number = float(match.group(1))
    return number if math.isfinite(number) else None


def _row_source(row: Any) -> Any:
    """Accept a typed AttendanceRow; defensively validate odd legacy mappings.

    A dict that validates as an AttendanceRow is normalised (e.g. a numeric
    string in `hours` becomes a float). An odd legacy dict that cannot be
    validated - missing fields, unusual key spellings - is returned unchanged
    so the alias lookups in `_get` can still read it. Never mutates the input.
    """
    if isinstance(row, AttendanceRow):
        return row
    if isinstance(row, dict):
        try:
            return AttendanceRow.model_validate(row)
        except ValueError:
            return row
    return row


def _recorded_hours(row: Any) -> float | None:
    """RECORDED hours from the attendance sheet (AttendanceRow.hours)."""
    if isinstance(row, AttendanceRow):
        return _as_number(row.hours)
    return _as_number(_get(row, _HOURS_KEYS))


def _row_matches(row: Any, card: ContributionCard) -> bool:
    """Tolerant (volunteer_id, task_id) attribution for one attendance row."""
    row_volunteer = _as_id(_get(row, _VOLUNTEER_KEYS))
    row_task = _as_id(_get(row, _TASK_KEYS))
    if row_volunteer is None and row_task is None:
        return False
    if row_volunteer is not None and row_volunteer != _as_id(card.volunteer_id):
        return False
    if row_task is not None and row_task != _as_id(card.task_id):
        return False
    # A row with only a task id cannot be attributed to this volunteer.
    return row_volunteer is not None


def _pool(card: ContributionCard, all_cards: list[ContributionCard] | None) -> list[ContributionCard]:
    """Batch under comparison; include the card itself even if callers omit it."""
    pool = list(all_cards or [])
    card_id = _as_id(getattr(card, "id", None))
    if not any(item is card or (card_id is not None and _as_id(getattr(item, "id", None)) == card_id)
               for item in pool):
        pool.append(card)
    return pool


def _evidence_refs(item: Any) -> set[str]:
    refs = _get(item, ("evidence_refs", "evidence_ref", "refs"), default=None)
    if isinstance(refs, (str, int, float)) and not isinstance(refs, bool):
        refs = [refs]
    if not isinstance(refs, (list, tuple, set)):
        return set()
    return {text for ref in refs if (text := str(ref).strip().casefold())}


def _summary(item: Any) -> str:
    value = getattr(item, "summary", None)
    return " ".join(str(value).strip().casefold().split()) if isinstance(value, str) else ""


def _flag_texts(value: Any) -> list[str]:
    """Flatten flag-like fields (list of str/dict, dict, scalar) to plain strings."""
    if value is None:
        return []
    if isinstance(value, dict):
        parts = []
        for key, item in value.items():
            parts.append(str(key))
            if isinstance(item, (str, bool, int, float)):
                parts.append(str(item))
            elif isinstance(item, (list, tuple, dict)):
                parts.extend(_flag_texts(item))
        return parts
    if isinstance(value, (list, tuple, set)):
        parts = []
        for item in value:
            if isinstance(item, dict):
                parts.extend(_flag_texts(item))
            else:
                parts.append(str(item))
        return parts
    return [str(value)]


def _nonempty(value: Any) -> bool:
    """True for a present, non-blank field (used for optional context keys)."""
    if value is None or isinstance(value, bool) or value is _MISSING:
        return False
    if isinstance(value, (list, tuple, set, dict, str)):
        return len(value) > 0 if not isinstance(value, str) else bool(value.strip())
    return True


def _has_self_declared(value: Any) -> bool:
    tokens = {_norm_key(token) for token in _SELF_DECLARED_TOKENS}
    return any(_norm_key(text) in tokens for text in _flag_texts(value))


def _parse_time(value: Any) -> tuple[int | None, float] | None:
    """Return (day ordinal or None, minutes from midnight) for HH:MM or ISO.

    Timezone rule: naive values are interpreted as UTC; offset-aware values
    are converted with astimezone(UTC) and stripped of tzinfo. Both therefore
    share one naive UTC-ish clock (e.g. 09:00+05:30 -> 03:30Z -> 210 minutes),
    so offsets are compared correctly rather than as wall-clock strings.
    """
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, datetime):
        moment = value
    elif hasattr(value, "hour") and hasattr(value, "minute"):  # datetime.time
        if getattr(value, "tzinfo", None) is not None:
            moment = datetime.combine(datetime(2000, 1, 1).date(),
                                      value.replace(tzinfo=None)).replace(tzinfo=value.tzinfo)
        else:
            return (None, value.hour * 60 + value.minute + getattr(value, "second", 0) / 60)
    else:
        text = str(value).strip()
        if not text:
            return None
        match = _HHMM.match(text)
        if match:
            hour, minute = int(match.group(1)), int(match.group(2))
            second = int(match.group(3) or 0)
            if hour < 24 and minute < 60 and second < 60:
                return (None, hour * 60 + minute + second / 60)
            return None
        iso = text[:-1] + "+00:00" if text.endswith(("Z", "z")) else text
        try:
            moment = datetime.fromisoformat(iso.replace(" ", "T", 1))
        except ValueError:
            return None
    if moment.tzinfo is not None:
        moment = moment.astimezone(timezone.utc).replace(tzinfo=None)
    return (moment.toordinal(), moment.hour * 60 + moment.minute + moment.second / 60)


def _window(row: Any) -> tuple[int | None, float, float] | None:
    start = _parse_time(_get(row, _CHECK_IN_KEYS))
    end = _parse_time(_get(row, _CHECK_OUT_KEYS))
    if start is None or end is None:
        return None
    if end[1] <= start[1]:  # inverted, zero-length or unsupported cross-midnight
        return None
    if (start[0] is None) != (end[0] is None):
        return None
    if start[0] is not None and start[0] != end[0]:
        return None
    return (start[0], start[1], end[1])


def _windows_overlap(left: tuple[int | None, float, float], right: tuple[int | None, float, float]) -> bool:
    # Never compare a dated window with a time-only window: different dates
    # would produce a false positive, so skip that pair instead.
    if (left[0] is None) != (right[0] is None):
        return False
    if left[0] is not None and left[0] != right[0]:
        return False
    return left[1] < right[2] and right[1] < left[2]


def _overlapping_other_tasks(card: ContributionCard, rows: list[Any]) -> list[str]:
    by_task: dict[tuple[str, str], list[tuple[int | None, float, float]]] = {}
    task_display: dict[str, str] = {}
    for row in rows:
        volunteer = _as_id(_get(row, _VOLUNTEER_KEYS))
        raw_task = _get(row, _TASK_KEYS)
        task = _as_id(raw_task)
        if volunteer is None or task is None:
            continue
        if isinstance(raw_task, str) and raw_task.strip():
            task_display.setdefault(task, raw_task.strip())
        else:
            task_display.setdefault(task, task)
        window = _window(row)
        if window is not None:
            by_task.setdefault((volunteer, task), []).append(window)

    card_volunteer, card_task = _as_id(card.volunteer_id), _as_id(card.task_id)
    others: set[str] = set()
    for (volunteer, task), windows in by_task.items():
        if volunteer != card_volunteer:
            continue
        for (other_volunteer, other_task), other_windows in by_task.items():
            if other_volunteer != volunteer or other_task == task:
                continue
            if card_task not in (task, other_task):
                continue
            if any(_windows_overlap(a, b) for a in windows for b in other_windows):
                others.add(other_task)
    return sorted(task_display.get(task, task) for task in others)


def _ages_and_consent(card: ContributionCard, matching_rows: list[Any]) -> tuple[list[float], list[Any]]:
    ages: list[float] = []
    consents: list[Any] = []
    for source in list(matching_rows) + [card]:
        age = _as_number(_get(source, _AGE_KEYS))
        if age is not None:
            ages.append(age)
        if any(text.casefold() == "true" for text in _flag_texts(_get(source, _MINOR_KEYS))):
            ages.append(17.0)
        consent = _get(source, _CONSENT_KEYS, _MISSING)
        if consent is not _MISSING:
            consents.append(consent)
    return ages, consents


def _minor_without_consent(card: ContributionCard, matching_rows: list[Any]) -> bool:
    """Typed first: row.age < 18 and row.guardian_consent is not True.

    If any matching typed AttendanceRow supplies an age, only typed rows
    decide this rule - a recorded guardian consent of True on that row is
    authoritative. Old-style card/row context (age, is_minor, guardian_consent)
    is a fallback for legacy callers that still pass dict-like rows.
    """
    typed = [row for row in matching_rows if isinstance(row, AttendanceRow)]
    if any(row.age is not None for row in typed):
        return any(row.age is not None and row.age < 18 and row.guardian_consent is not True
                   for row in typed)
    ages, consents = _ages_and_consent(card, matching_rows)
    if not any(age < 18 for age in ages):
        return False
    return not any(consent is True for consent in consents)


def _self_declared(card: ContributionCard, matching_rows: list[Any]) -> bool:
    for source in list(matching_rows) + [card]:
        raw = _get(source, _SELF_DECLARED_KEYS, _MISSING)
        if _nonempty(raw) or _has_self_declared(raw):
            return True
        if _has_self_declared(_get(source, _FLAGS_KEYS)):
            return True
    for flag in getattr(card, "flags", None) or []:
        if _has_self_declared(getattr(flag, "code", None)) or _has_self_declared(getattr(flag, "message", None)):
            return True
    return False


def check_card(card: ContributionCard, all_cards: list[ContributionCard],
               attendance_rows: list[AttendanceRow]) -> list[Flag]:
    """Deterministically flag anomalies on one SYNTHETIC contribution card.

    Returns a fresh list of Flags in a fixed rule order. Inputs are read-only:
    the card's status and flags are never modified. `attendance_rows` are typed
    AttendanceRow objects: their `hours` is RECORDED time, never the claim.
    """
    flags: list[Flag] = []
    rows = [_row_source(row) for row in (attendance_rows or [])]
    matching = [row for row in rows if _row_matches(row, card)]
    pool = _pool(card, all_cards)

    # 1. hours_exceed_recorded
    recorded = [number for row in matching
                if (number := _recorded_hours(row)) is not None]
    claimed = _as_number(card.claimed_hours)
    if recorded and claimed is not None and claimed > max(recorded) + HOURS_EPSILON:
        flags.append(Flag(
            code="hours_exceed_recorded",
            severity="warn",
            message=f"Claims {claimed:g} hours but attendance records at most {max(recorded):g}; "
                    "ask the host to check the difference.",
        ))

    # 2. no_attendance_record
    if not matching:
        flags.append(Flag(
            code="no_attendance_record",
            severity="warn",
            message="No attendance row matches this volunteer and task; the hours cannot "
                    "be checked against the attendance sheet.",
        ))

    # 3. implausible_hours
    if claimed is not None and claimed > MAX_DAILY_HOURS:
        flags.append(Flag(
            code="implausible_hours",
            severity="block",
            message=f"Claims {claimed:g} hours in one day, above the 12-hour limit; host "
                    "review is required before this card can be confirmed.",
        ))

    # 4. duplicate_evidence_ref
    ref_counts = Counter(ref for item in pool for ref in _evidence_refs(item))
    duplicated = sorted(ref for ref in _evidence_refs(card) if ref_counts[ref] > 1)
    if duplicated:
        flags.append(Flag(
            code="duplicate_evidence_ref",
            severity="warn",
            message="Evidence reference(s) " + ", ".join(repr(ref) for ref in duplicated) +
                    " also appear on another card in this batch; check that the evidence "
                    "was not reused.",
        ))

    # 5. identical_summary_text
    normalized_summary = _summary(card)
    if normalized_summary and sum(1 for item in pool if _summary(item) == normalized_summary) > 1:
        flags.append(Flag(
            code="identical_summary_text",
            severity="warn",
            message="This summary is identical to another card's summary after normalizing "
                    "case and spacing; check whether claim text was copied.",
        ))

    # 6. overlapping_tasks
    overlapping = _overlapping_other_tasks(card, rows)
    if overlapping:
        flags.append(Flag(
            code="overlapping_tasks",
            severity="warn",
            message="Attendance times overlap task(s) " + ", ".join(repr(task) for task in overlapping) +
                    " for the same volunteer; verify the check-in/check-out times.",
        ))

    # 7. minor_without_guardian_consent
    if _minor_without_consent(card, matching):
        flags.append(Flag(
            code="minor_without_guardian_consent",
            severity="block",
            message="The volunteer is recorded as under 18 and no guardian consent is "
                    "recorded as true; do not confirm until consent is verified.",
        ))

    # 8. self_declared_skill_unconfirmed
    if _self_declared(card, matching):
        flags.append(Flag(
            code="self_declared_skill_unconfirmed",
            severity="info",
            message="At least one skill is self-declared and not yet host-confirmed; "
                    "the host may want to verify it before confirming this card.",
        ))

    # 9. round_number_inflation
    if (claimed is not None and math.isfinite(claimed) and claimed.is_integer()
            and sum(1 for item in pool
                    if (value := _as_number(getattr(item, "claimed_hours", None))) is not None
                    and value == claimed) >= ROUND_CLUSTER_MIN_CARDS):
        flags.append(Flag(
            code="round_number_inflation",
            severity="info",
            message=f"{claimed:g} hours is a round number shared by at least "
                    f"{ROUND_CLUSTER_MIN_CARDS} cards in this batch; worth a quick "
                    "spot-check, but round shifts are normal and this is not a rejection.",
        ))

    # 10. missing_evidence_ref (chosen rule; see module docstring)
    if not _evidence_refs(card):
        flags.append(Flag(
            code="missing_evidence_ref",
            severity="warn",
            message="No evidence reference is attached to this card; add a link to a "
                    "photo, signed sheet or host note so the claim can be checked.",
        ))

    return flags
