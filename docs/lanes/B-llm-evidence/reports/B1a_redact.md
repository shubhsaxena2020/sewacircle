# B1a - Indian PII redaction (Lane B)

TRIMMED 2026-11-18 by the independent B1X reviewer. The original ~1 MB file
contained thousands of verbatim tracebacks from a mid-write full-suite run;
that raw block was removed. It was never the authoritative suite result.
The lead's verbatim authoritative full-suite output remains in
`docs/lanes/B-llm-evidence/PROGRESS.md` ("LEAD AUTHORITATIVE FULL SUITE - B1").
This report keeps only the implementation summary, case counts, targeted test
output, the lead's authoritative command/result line (quoted, not re-run by the
reviewer), and the limitations. All numbers below come from commands whose real
output is pasted here or is explicitly labelled as quoted from PROGRESS.md.
All data and identifiers are SYNTHETIC.

## Implementation summary

- `backend/app/llm/redact.py`: `redact(text: str) -> tuple[str, int]`.
- Regex-only detector, most-specific-first, with six typed placeholders:
  `[EMAIL]` -> `[UPI]` -> `[AADHAAR]` -> `[PAN]` -> `[PHONE]` -> `[BANK_ACCOUNT]`.
- Indian mobile: 10 digits starting 6-9, optional `+91` / `0` prefix, optional
  spaces/dashes/parentheses between groups.
- Aadhaar: 12 contiguous digits or 4-4-4 space grouping. PAN: 5 uppercase
  letters + 4 digits + 1 uppercase letter. Email. UPI `localpart@bank-handle`.
  Bank-account-like runs: 9-18 contiguous digits not already consumed.
- Overlap resolution: candidate spans are collected in rule-priority order,
  overlapping spans are discarded, replacements applied right-to-left; each
  span is replaced and counted exactly once.
- Exactly 10-digit runs beginning with 0 or 1 are excluded from the
  bank-account rule (short IDs, not mobiles).
- `backend/app/llm/extract.py`: `redact()` is a thin wrapper
  (`from .redact import redact as _redact`; `return _redact(text)`).
- `backend/tests/llm/test_redact.py`: unit tests, no network calls; all
  fixtures invented for testing.

## Case counts

- POSITIVE: **33** distinct inputs (independently re-verified by importing the
  test module), including 4 with Devanagari surrounding text and ASCII PII.
- NEGATIVE: **35** distinct inputs (independently re-verified), covering PIN
  codes, dates, hour ranges, 4-digit years, short IDs and 10-digit numbers
  starting 0/1.
- Additional tests: mixed PII types in one string (count and placeholders),
  repeated same-type count, clean text unchanged with count 0, empty string,
  input string not mutated, Aadhaar/phone overlap counted once, and the
  `extract.redact` thin wrapper.

Reviewer's independent count command and real output:

```
$ cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -c "import importlib.util, pathlib; p=pathlib.Path('tests/llm/test_redact.py'); s=importlib.util.spec_from_file_location('t',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print('POSITIVE inputs:', len(m.POSITIVE), 'distinct:', len(set(x[0] for x in m.POSITIVE))); print('NEGATIVE inputs:', len(m.NEGATIVE), 'distinct:', len(set(m.NEGATIVE))); print('positive >=25:', len(m.POSITIVE)>=25, 'negative >=15:', len(m.NEGATIVE)>=15)"
POSITIVE inputs: 33 distinct: 33
NEGATIVE inputs: 35 distinct: 35
positive >=25: True negative >=15: True
```

## Targeted test run (reviewer's own run, 2026-11-18)

```
$ cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q tests/llm/test_redact.py
C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pytest_asyncio\plugin.py:306: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture scope. Future versions of pytest-asyncio will default the loop scope for "function" scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
........................................................................ [ 93%]
.....                                                                    [100%]
77 passed in 0.21s
```

## Full suite

Exact lead authoritative command (QUOTED VERBATIM from
`docs/lanes/B-llm-evidence/PROGRESS.md`, lines 21 and 46; the reviewer did not
run this exact historical command, only the current-state run below):

```
cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q .
```

Its result line (QUOTED from PROGRESS.md, not re-run by the reviewer):

```
420 passed, 60 warnings in 3.49s
```

The complete raw output of that authoritative run is in
`docs/lanes/B-llm-evidence/PROGRESS.md`, section "LEAD AUTHORITATIVE FULL
SUITE - B1". It is not duplicated here.

Reviewer's current-state run after the later A1 adaptation (this one the
reviewer did run):

```
$ cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q .
437 passed, 73 warnings in 3.65s
```

## R2/R3 alignment (short form; full audit in `reports/B1X_c_review.md`)

- PIN codes, dates and hour ranges are NOT redacted; independently probed with
  real output in `reports/B1X_c_review.md`.
- Names are NOT detected: stated in `redact.py` module docstring (no NER).
- R2's Devanagari-digit normalization is planned for B2, not a B1 gap.
- R2 cue-based NAME/ADDRESS patterns and hyphen-separated Aadhaar are not
  implemented in B1; see the full audit for gap/deferred classification.

## Limitations

- Detection is REGEX-BASED ONLY. PERSON NAMES ARE NOT DETECTED (no NER); a name
  in the input passes through unchanged.
- This is a defence-in-depth PRE-MODEL step, NOT a guarantee of PII removal.
- Obfuscated, misspelled, Devanagari-numeral or otherwise non-standard
  identifiers may be missed; dotted phone separators (e.g. `987.654.3210`)
  and hyphen-separated Aadhaar (`1234-5678-9012`) are not matched.
- ALL data shown by the product and all test fixtures is SYNTHETIC; every
  identifier in the tests is invented, no real person's data is used.
