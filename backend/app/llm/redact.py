"""Regex-based, defence-in-depth PII redaction for text sent to a language model.

LIMITATIONS (read before relying on this):

* Detection is REGEX-BASED ONLY. PERSON NAMES ARE NOT DETECTED -- there is no
  named-entity recognition (NER) here, so a name in the input will pass through.
* This is a defence-in-depth PRE-MODEL step, NOT a guarantee. It cannot catch
  every possible identifier, obfuscation, or sensitive detail.
* ALL data shown by SewaCircle is SYNTHETIC. Every phone number, Aadhaar, PAN,
  email, UPI id and account number in the examples and test fixtures below is
  invented for illustration; no real person's data is used.

The detector handles Indian mobile numbers (10 digits starting 6-9, with
optional +91 / 0 prefix and optional spaces, dashes or parentheses), Aadhaar
(12 digits, optionally in 4-4-4 groups), PAN, email addresses, UPI ids
(localpart@bank handle) and bank-account-like long digit runs (9-18 digits).
Rules run most-specific-first and claims are resolved to non-overlapping spans,
so one substring is never replaced twice or counted twice.
"""
from __future__ import annotations

import re
from typing import NamedTuple


class _Rule(NamedTuple):
    placeholder: str
    pattern: re.Pattern[str]


# Most-specific first. Boundaries prevent matching inside a larger token.
# Digits are ASCII [0-9] on purpose: Devanagari numerals are ordinary prose here.
# A 10-digit run that cannot be an Indian mobile (leading 0/1) is a short ID,
# not a bank-account-like number; keep it out of the long-digits rule too.
_RULES: tuple[_Rule, ...] = (
    # rahul@example.com ; stop at whitespace, commas and common delimiters.
    _Rule("[EMAIL]", re.compile(r"(?<![A-Za-z0-9._%+\-])[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}(?![A-Za-z0-9.\-])")),
    # UPI: localpart@bank-handle (okhdfcbank, ybl, paytm, sbi, ...), no dot in domain.
    _Rule("[UPI]", re.compile(r"(?<![A-Za-z0-9._\-])[A-Za-z0-9._\-]+@(?:[A-Za-z][A-Za-z0-9\-]*)(?![A-Za-z0-9.\-])")),
    # Aadhaar: 12 consecutive digits, or 4-4-4 grouped with single spaces.
    _Rule("[AADHAAR]", re.compile(r"(?<!\d)\d{4} \d{4} \d{4}(?!\d)|(?<!\d)\d{12}(?!\d)")),
    # PAN: 5 uppercase letters + 4 digits + 1 uppercase letter.
    _Rule("[PAN]", re.compile(r"(?<![A-Z0-9])[A-Z]{5}\d{4}[A-Z](?![A-Z0-9])")),
    # Indian mobile: optional +91 / 0 prefix, separators between any groups.
    # Body is either grouped 3-3-4 or a plain 10-digit run starting 6-9.
    _Rule("[PHONE]", re.compile(
        r"(?<![\d+])"
        r"(?:\+91[\s\-]?)?(?:0[\s\-]?)?"
        r"\(?[6-9](?:[\s\-]?\d){2}\)?(?:[\s\-]?\d){7}"
        r"(?![\d])"
    )),
    # Bank account-like long digit runs not claimed above (9-18 digits).
    # Exclude exactly 10 digits starting 0/1 (short IDs, not mobiles/accounts).
    _Rule("[BANK_ACCOUNT]", re.compile(
        r"(?<!\d)(?![01]\d{9}(?!\d))\d{9,18}(?!\d)"
    )),
)


def redact(text: str) -> tuple[str, int]:
    """Replace detected Indian PII with typed placeholders.

    Returns (clean_text, number_of_replacements). Each non-overlapping span is
    replaced exactly once; overlapping candidates are claimed by the first
    (most specific) matching rule.
    """
    claimed: list[tuple[int, int, str]] = []
    taken: list[tuple[int, int]] = []
    for rule in _RULES:
        for match in rule.pattern.finditer(text):
            span = match.span()
            if any(span[0] < end and start < span[1] for start, end in taken):
                continue
            taken.append(span)
            claimed.append((span[0], span[1], rule.placeholder))

    if not claimed:
        return text, 0

    out = text
    for start, end, placeholder in sorted(claimed, reverse=True):
        out = out[:start] + placeholder + out[end:]
    return out, len(claimed)


__all__ = ["redact"]
