"""Unit tests for regex-based Indian PII redaction.

All identifiers below are SYNTHETIC / invented for testing. No real person's
phone number, Aadhaar, PAN, email, UPI id or account number appears here.
No network calls are made.
"""
from __future__ import annotations

import pytest

from app.llm import extract
from app.llm.redact import redact


# ---------------------------------------------------------------------------
# POSITIVE cases (synthetic PII). Each tuple: (input, expected_clean, count, placeholder).
# ---------------------------------------------------------------------------
POSITIVE = [
    # phones
    ("9876543210", "[PHONE]"),
    ("8123456789", "[PHONE]"),
    ("+91 98765 43210", "[PHONE]"),
    ("+91-9876543210", "[PHONE]"),
    ("+91 9876543210", "[PHONE]"),
    ("0 9876543210", "[PHONE]"),
    ("09876543210", "[PHONE]"),
    ("(987)654-3210", "[PHONE]"),
    ("(987) 654 3210", "[PHONE]"),
    ("987 654 3210", "[PHONE]"),
    ("987-654-3210", "[PHONE]"),
    ("+91-987-654-3210", "[PHONE]"),
    ("9999999999", "[PHONE]"),
    # Aadhaar
    ("123456789012", "[AADHAAR]"),
    ("1234 5678 9012", "[AADHAAR]"),
    # PAN
    ("ABCDE1234F", "[PAN]"),
    ("XYZAB9999Z", "[PAN]"),
    # email
    ("rahul@example.com", "[EMAIL]"),
    ("first.last+tag@mail.example.co.in", "[EMAIL]"),
    ("a.b-c_d@example.co.in", "[EMAIL]"),
    # UPI
    ("rahul@okhdfcbank", "[UPI]"),
    ("xyz@ybl", "[UPI]"),
    ("paytmqr@paytm", "[UPI]"),
    ("rahul@okaxis", "[UPI]"),
    ("merchant@upi", "[UPI]"),
    ("test@ybl", "[UPI]"),
    # bank-account-like long digit runs
    ("123456789", "[BANK_ACCOUNT]"),
    ("123456789012345678", "[BANK_ACCOUNT]"),
    ("999999999", "[BANK_ACCOUNT]"),
    # Hindi / Devanagari surrounding text (PII itself ASCII)
    ("रा़ुल का फोन 9876543210 है", "[PHONE]"),
    ("एजेंट 8765432109 से संपर्क करें", "[PHONE]"),
    ("केन्द्र संपर्क 9876543210 करें", "[PHONE]"),
    ("पाइलट 1234 5678 9012 दर्ज करें", "[AADHAAR]"),
]


@pytest.mark.parametrize("raw,placeholder", POSITIVE)
def test_positive_pii_is_redacted(raw: str, placeholder: str) -> None:
    clean, n = redact(raw)
    # Devanagari cases have surrounding Hindi text; others are PII-only.
    if any("\u0900" <= ch <= "\u097f" for ch in raw):
        assert placeholder in clean, (raw, clean)
        assert placeholder not in raw, (raw, clean)
    else:
        assert clean == placeholder, (raw, clean)
    assert n == 1, (raw, n)


def test_positive_count_is_distinct_inputs() -> None:
    # Guards against accidentally parametrizing the same string twice.
    assert len({raw for raw, _ in POSITIVE}) == len(POSITIVE) >= 25


# ---------------------------------------------------------------------------
# NEGATIVE cases. Each input must come back unchanged with count 0.
# ---------------------------------------------------------------------------
NEGATIVE = [
    "208001",                 # 6-digit PIN code
    "PIN 208001 and year 2026",
    "Plot 208001, Sector 12",
    "12/01/2026",             # dates
    "2026-01-12",
    "12 Jan 2026",
    "19/11/2026",
    "18 Nov 2026",
    "2026-11-18",
    "12-01-2026",
    "1/2/2026",
    "2026-01-12T09:00:00",
    "9am-5pm",                # hour ranges
    "09:00-17:00",
    "10am-6pm",
    "08:30-17:30",
    "2026",                   # 4-digit year
    "1998",
    "1234",                   # short IDs
    "12345",
    "ID 123",
    "ID 1234",
    "ID 12345",
    "1234567890",             # 10-digit number starting 1 (cannot be Indian mobile)
    "0123456789",             # 10-digit number starting 0
    "1123456789",
    "98765",
    "Team of 30 volunteers",  # ordinary prose
    "Room 101, Block B",
    "https://example.com/path?x=12345",
    "Aadhaar last 4: 4321",
    "PAN-like ABC123",
    "volunteer 7, group 3",
    "dist 15 km",
    "Meeting at 5pm",
]


@pytest.mark.parametrize("raw", NEGATIVE)
def test_negative_non_pii_is_unchanged(raw: str) -> None:
    clean, n = redact(raw)
    assert clean == raw, (raw, clean)
    assert n == 0, (raw, n)


def test_negative_count_is_distinct_inputs() -> None:
    assert len(set(NEGATIVE)) == len(NEGATIVE) >= 15


# ---------------------------------------------------------------------------
# Counting, mixed types, clean text, immutability, wrapper.
# ---------------------------------------------------------------------------
def test_multiple_pii_types_in_one_string() -> None:
    raw = (
        "Phone: 9876543210; Aadhaar: 1234 5678 9012; PAN: ABCDE1234F; "
        "UPI: rahul@okhdfcbank; email: r@example.com; acct: 123456789"
    )
    clean, n = redact(raw)
    assert n == 6
    assert clean == (
        "Phone: [PHONE]; Aadhaar: [AADHAAR]; PAN: [PAN]; "
        "UPI: [UPI]; email: [EMAIL]; acct: [BANK_ACCOUNT]"
    )
    assert not any(x in clean for x in ("9876543210", "1234 5678 9012", "ABCDE1234F",
                                        "rahul@okhdfcbank", "r@example.com", "123456789"))


def test_repeated_same_type_counts_each_replacement() -> None:
    clean, n = redact("Call 9876543210 or 8765432109")
    assert clean == "Call [PHONE] or [PHONE]"
    assert n == 2


def test_clean_text_unchanged_with_zero_count() -> None:
    raw = "Organise a health camp in the community hall on Saturday morning."
    assert redact(raw) == (raw, 0)


def test_empty_string() -> None:
    assert redact("") == ("", 0)


def test_input_string_is_not_mutated() -> None:
    raw = "Contact 9876543210 or rahul@example.com"
    original = raw[:]
    clean, n = redact(raw)
    assert raw == original
    assert n == 2
    assert clean != raw


def test_placeholder_never_redacted_twice() -> None:
    # A phone inside an Aadhaar span must not be counted a second time.
    clean, n = redact("123456789012")
    assert clean == "[AADHAAR]"
    assert n == 1


def test_extract_redact_is_thin_wrapper() -> None:
    raw = "9876543210 and rahul@example.com"
    assert extract.redact(raw) == redact(raw)
    assert extract.redact("208001") == ("208001", 0)
