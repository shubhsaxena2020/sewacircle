# PROGRESS Lane B-llm-evidence

## Pre-batch context
- Read docs/COMMON.md and docs/lanes/B-llm-evidence/TASK.md. Workdir C:/Users/shubh/Projects/sewacircle.
- Baseline full suite before any work: `10 passed, 1 warning in 0.57s`.
- Research check before B1: docs/research/ was EMPTY (Lane C still writing). R2/R3 landed during B1; lead read them before B2.

## BATCH B1 — redact / rules / ledger (3 parallel subagents, blocking)
- Task 1 (B1a): created backend/app/llm/redact.py (regex PII, six typed placeholders, overlap resolution, priority EMAIL>UPI>AADHAAR>PAN>PHONE>BANK_ACCOUNT), made extract.redact a thin wrapper, wrote backend/tests/llm/test_redact.py with 33 positive + 35 negative distinct cases (4 Devanagari surroundings). Report: reports/B1a_redact.md. NOTE: ~1 MB because mid-write full-suite tracebacks were pasted verbatim; B4 must trim to the final authoritative run.
- Task 2 (B1b): implemented backend/app/evidence/rules.py check_card with 10 deterministic rules (9 required + missing_evidence_ref, justified), backend/tests/evidence/test_rules.py (33 tests) and __init__.py. Report: reports/B1b_rules.md.
- Task 3 (B1c): implemented backend/app/evidence/ledger.py (sha256 chain over 6 fields, JSON-lines journal, .head sidecar, RLock appends, first_bad_index verification) and backend/tests/evidence/test_ledger.py (11 tests). Report: reports/B1c_ledger.md.
- Subagent full-suite runs were unreliable: Lane A's tests/solver/test_factories.py was mid-write (B1a 2495 failed/175 passed; B1b 2496 failed/174 passed; B1c hit a collection SyntaxError then 2 contract-drift failures). NOT accepted as the batch result.

### Lead verification of B1 (ran directly)
Command: from backend, venv python `-c` importing app.llm.redact, app.llm.extract, app.evidence.rules, app.evidence.ledger.
Printed: `redact docstring has NER note: True`; module doc starts `Regex-based, defence-in-depth PII redaction for text sent to a language model.`; `rule codes found: 10 [... all ten codes ...]`; ledger doc contains `A hash chain shows edits, not truth; truth comes from host confirmation.`; `extract.redact wrapper: 1`.

### LEAD AUTHORITATIVE FULL SUITE — B1 (pasted verbatim)
Command:
```
cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q .
```
Output (exit 0):
```
C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pytest_asyncio\plugin.py:306: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture scope. Future versions of pytest-asyncio will default the loop scope for "function" scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session".

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))

........................................................................ [ 17%]
........................................................................ [ 34%]
........................................................................ [ 51%]
........................................................................ [ 68%]
........................................................................ [ 85%]
.....................................................                    [100%]
============================== warnings summary ===============================
..\.venv\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

tests/evidence/test_rules.py: 59 warnings
  C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pydantic\main.py:280: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
420 passed, 60 warnings in 3.49s
```
B1 RESULT: GREEN (420 passed).

## HEAD AMENDMENT A1 — discovered between B1 and B2
- Head appended AMENDMENT-A1 to TASK.md and wrote docs/AMENDMENT-A1.md. Lane B items 8-11 are mandatory: typed AttendanceRow in check_card and draft_cards, typed Assignment in draft_cards, deterministic card ids, Ledger.head_hash() + verify(trusted_head=None) + crash-safe fsync, LLMError on failure, role ids assigned as role-01.. in extraction conversion.
- Lead re-read schemas.py: AttendanceRow, SlotRef, deterministic card id comment all present. Lead ran inspect: check_card still `list[dict]`, Ledger.verify still no trusted_head, head_hash absent, draft_cards still `list[dict]`. Full suite still printed `420 passed, 60 warnings in 2.95s` (suite alone does not enforce A1).
- Decision: insert B1X (A1 adaptation) before B2. Research check: R2, R3 present; R6 still ABSENT.

## BATCH B1X — A1 contract adaptation (rules / ledger / review)
- Task A: adapted backend/app/evidence/rules.py to A1 item 8 — signature now `check_card(card, all_cards, attendance_rows: list[AttendanceRow])`, row.hours = RECORDED, minor rule uses row.age/guardian_consent, ISO-8601 offsets normalised, all 10 rules preserved; rewrote tests with real AttendanceRow fixtures (43 targeted tests). Report: reports/B1X_a_rules_a1.md.
- Task B: adapted backend/app/evidence/ledger.py to A1 item 10 — added `head_hash()`, `verify(trusted_head: str | None = None)`, honest tail-truncation/RFC6962 docstring, flush+os.fsync on journal and atomic sidecar rewrite, RLock; tests include coordinated journal+sidecar truncation caught only by a previously captured trusted head, and a real fsync spy (18 targeted tests). Report: reports/B1X_b_ledger_a1.md.
- Task C: independent audit — B1 redaction PASS (33 positive/35 negative re-counted, PIN/date/hour-range negatives = 0), rules PASS 10 codes, ledger PASS A1 item 10 with real truncation probe; flagged A1 item 8 PARTIAL (draft_cards still list[dict], B3) and A1 items 9/11 deferred to B2/B3. Trimmed B1a report 1,059,388 -> 6,261 bytes with a real command. Report: reports/B1X_c_review.md. NOTE: B1b report is still 1,140,214 bytes (out of that task's write scope); B4 must trim it.

### Lead verification of B1X (ran directly)
`inspect` probe printed: `check_card (card, all_cards, attendance_rows: 'list[AttendanceRow]') -> 'list[Flag]'`; `verify (self, trusted_head: 'str | None' = None)`; `head_hash (self) -> 'str'`; `doc has tail-truncation note: True`; constructed a real AttendanceRow with hours=4.0, age=17, guardian_consent=False.
Lane B tests only: `138 passed, 72 warnings in 3.63s` (tests/llm + tests/evidence).
Sizes: B1a 6,261 B; B1X_a 8,394 B; B1X_b 10,064 B; B1X_c 24,092 B; B1b 1,140,214 B (to trim in B4).

### LEAD AUTHORITATIVE FULL SUITE — B1X (pasted verbatim)
Command:
```
cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q .
```
Output (exit 0):
```
C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pytest_asyncio\plugin.py:306: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture scope. Future versions of pytest-asyncio will default the loop scope for "function" scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session".

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
437 passed, 73 warnings in 8.47s
```
B1X RESULT: GREEN (437 passed).

### Research check before B2
docs/research now has R1, R2, R3, R4, R5, R6 and up_districts.json. Lead read R6 in full: freeze fixtures before first run and record SHA-256; n=10 intervals are descriptive only; no p-values/"significantly better"; publish raw rows and misses; never call manual_greedy "today's baseline". R2 read in full (prompt-as-data, verbatim spans, negation, Devanagari digits, abstention). R3 read in full (OB3 unsigned only, no proof field, no MY Bharat endorsement). R6's extraction rules cross-reference R2 and forbid contradicting it.

## BATCH B2 — extraction prompts + labelled briefs + label/prompt review
Pending.

---
HEAD NOTICE 2026-11-19 00:10: provider down since about 23:30; remaining Lane B items (extract_roles, draft_cards, badges, extraction eval) REASSIGNED TO THE HEAD. Do not write more files.
CARD BLOCKED: reassigned to head (provider outage)

HEAD ORDER: LANE CANCELLED. STOP NOW. Do not edit any more files. Write CARD BLOCKED: lane cancelled by head as the last line of PROGRESS.md and end your turn.
