# B1X-a — rules.py adaptation to HEAD AMENDMENT A1 (item 8)

## Scope and files written
- Adapted `backend/app/evidence/rules.py` (10-rule engine, no coverage loss).
- Rewrote fixtures/tests in `backend/tests/evidence/test_rules.py` to use real `app.schemas.AttendanceRow` objects.
- This report: `docs/lanes/B-llm-evidence/reports/B1X_a_rules_a1.md`.
- No other lane file was written. No installs, no network, no LLM calls.

## Exact commands and COMPLETE raw outputs

### Targeted test command (from `C:/Users/shubh/Projects/sewacircle/backend`)

```
cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q tests/evidence/test_rules.py
```

Raw output (exit code 0):

```
C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pytest_asyncio\plugin.py:306: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to "function" scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
...........................................                              [100%]
============================== warnings summary ===============================
tests/evidence/test_rules.py: 72 warnings
  C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pydantic\main.py:280: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
43 passed, 72 warnings in 0.23s
```

Note: an earlier targeted run failed because a test fixture used `recorded_hours=99.0`, which violates the shared schema's `le=24` validator. The fixture was changed to `recorded_hours=24.0`; the output above is the authoritative post-fix run.

### FULL suite command (from `C:/Users/shubh/Projects/sewacircle/backend`)

```
cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q .
```

Raw output (exit code 0):

```
C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pytest_asyncio\plugin.py:306: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to "function" scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
........................................................................ [ 16%]
........................................................................ [ 32%]
........................................................................ [ 49%]
........................................................................ [ 65%]
........................................................................ [ 82%]
........................................................................ [ 98%]
.....                                                                    [100%]
============================== warnings summary ===============================
..\.venv\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

tests/evidence/test_rules.py: 72 warnings
  C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pydantic\main.py:280: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
437 passed, 73 warnings in 3.76s
```

Test counts printed by the two commands: `43 passed` (targeted), `437 passed` (full suite). Both commands were re-run after the final test-file cleanup and printed the same counts/time-independent results; the full-suite run immediately preceding that cleanup printed `437 passed, 73 warnings in 3.87s`. Failures: none in any authoritative run. No transient errors from concurrent ledger edits were observed in the full runs.

## What changed in rules.py
- Signature is now exactly `check_card(card: ContributionCard, all_cards: list[ContributionCard], attendance_rows: list[AttendanceRow]) -> list[Flag]`, with `AttendanceRow` imported from `..schemas`.
- `hours_exceed_recorded` compares `card.claimed_hours` against `AttendanceRow.hours` (RECORDED sheet hours) with epsilon `0.01`, taking the largest matching row's `hours`. `card.recorded_hours` is never the comparison source.
- `minor_without_guardian_consent` uses typed `row.age < 18 and row.guardian_consent is not True`. If a matching typed row supplies an age, typed rows alone decide (a typed consent of `True` is authoritative); legacy card/row context is only a fallback when no typed row supplies an age.
- `overlapping_tasks` parses ISO-8601 `check_in`/`check_out` strings. Naive values are interpreted as UTC; offset-aware values are converted with `astimezone(timezone.utc)` and stored in a common naive UTC-ish clock, so `09:00+05:30` and `03:30Z` are the same instant. Unparseable, inverted, zero-length, mixed-precision and mismatched-date windows are skipped rather than false-flagged.
- Defensive legacy support retained: dict-like rows are normalised via `AttendanceRow.model_validate` when they validate, otherwise read through the existing case-insensitive alias/getattr lookups. Typed objects are never mutated.
- All 10 original rule codes, severities and definitions preserved (with the A1 semantics documented in the module docstring): `hours_exceed_recorded` (warn), `no_attendance_record` (warn), `implausible_hours` (block), `duplicate_evidence_ref` (warn), `identical_summary_text` (warn), `overlapping_tasks` (warn), `minor_without_guardian_consent` (block), `self_declared_skill_unconfirmed` (info), `round_number_inflation` (info), `missing_evidence_ref` (warn). Order is unchanged; nothing is auto-rejected, no network/LLM, deterministic, no input mutation.

## Tests added / retained
- Real `AttendanceRow` fixtures for every rule; at least one positive per code, clean-card and negative cases, immutability, determinism, unparseable-time and rule-order/no-auto-rejection tests.
- Explicit A1 tests: typed signature via `inspect.signature` + `get_type_hints`; `row.hours` as recorded with `card.recorded_hours` deliberately conflicting; minor rule via `age`/`guardian_consent` on typed rows; ISO-8601 offset equivalence (`09:00+05:30` vs `03:30Z`), non-overlap with offsets, and naive-as-UTC equivalence.
- One dedicated defensive test still passes odd legacy dict-like rows to preserve backward compatibility.

## Limitations (documented, not hidden)
- Timezone normalisation treats naive timestamps as UTC; this is an explicit UTC-ish comparison convention, not a claim about the volunteer's local zone.
- Dated windows whose UTC dates differ are skipped; dated vs time-only windows are never compared, to avoid false positives. Self-declared skills are not a field on `AttendanceRow`, so the row-based test injects legacy context via pydantic extras; the card-flag path uses the real schema.
- The warnings in the outputs are pre-existing pytest-asyncio/FastAPI/pydantic deprecation notices, not failures.
