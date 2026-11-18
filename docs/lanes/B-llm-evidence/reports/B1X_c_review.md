# B1X_c - independent A1 compliance review of Lane B B1 output

Reviewer: independent B1X subagent (Hermes, profile res-s3). Date: 2026-11-18.
Scope: the three B1 deliverables (redaction, rules, ledger) as they stand at
HEAD, judged against `docs/lanes/B-llm-evidence/TASK.md` including the appended
HEAD AMENDMENT A1 (items 8-11) and `docs/AMENDMENT-A1.md`, with R2/R3 alignment.
Method: read the card and amendment, inspected the source, imported the test
module, parsed source with `ast`, and ran the commands pasted below. I did not
trust the B1 subagent reports; every count/claim below is either re-run here or
explicitly labelled as quoted from `PROGRESS.md`.

All volunteer, task, phone, Aadhaar, PAN and email values in this report are
SYNTHETIC and invented for testing. No real person's data is used.

## Verdict

- **B1 redaction: PASS** against TASK B1.1. 33 positive + 35 negative distinct
  cases, 77 targeted tests pass, PIN/date/hour-range negatives verified by a
  separate probe, names-not-detected documented in the module docstring.
- **B1 rules: PASS** against TASK B1.5 and A1 item 8 for `check_card`. 10 rule
  codes, typed `list[AttendanceRow]` signature, typed and dict rows produce the
  same flags in a runtime probe.
- **B1 ledger: PASS** against TASK B1.6 and A1 item 10. Honest docstring,
  `head_hash()`, `verify(trusted_head=...)`, journal and sidecar fsync, RLock;
  a coordinated journal+sidecar truncation is caught by `trusted_head`.
- **A1 item 8 overall: PARTIAL** because `extract.draft_cards` is still typed
  `list[dict]` (B3 owns it).
- **A1 item 9 (deterministic card ids): MISSING** - only a schema comment
  exists; no implementation.
- **A1 item 11 (LLMError/no-network tests): MISSING (deferred)** - the LLM
  functions are still `NotImplementedError`; B1 redaction tests make no network
  calls, but the LLMError path cannot exist until B2/B3.
- Current full suite (reviewer-run): `437 passed, 73 warnings in 3.65s`.

## Audit table

Statuses are for HEAD at the time of this review (2026-11-18, after the
concurrent rules/ledger A1 edits landed). `file:line` is the evidence I read.

| # | Requirement (source) | Status | Evidence | Gap / concrete fix |
|---|---|---|---|---|
| A1-8 | Attendance is typed: `check_card(card, all_cards, attendance_rows: list[AttendanceRow])`; `draft_cards(task, host_notes, attendance_rows: list[AttendanceRow], assignments: list[Assignment])`; `minor_without_guardian_consent` uses `AttendanceRow.age/guardian_consent` (A1 item 8) | **PARTIAL** | `check_card` is typed at `backend/app/evidence/rules.py:407-408`; `AttendanceRow` import at `rules.py:76`; typed normaliser `rules.py:166-181`; consent rule at `rules.py:485`; `AttendanceRow` fields `backend/app/schemas.py:261-270`. Runtime probe: typed row -> `['hours_exceed_recorded', 'minor_without_guardian_consent', 'missing_evidence_ref']`; dict row -> identical. **But** `extract.draft_cards` is still `attendance_rows: list[dict], assignments: list[dict]` at `backend/app/llm/extract.py:22`. | Fix in B3: change `draft_cards` to `attendance_rows: list[AttendanceRow], assignments: list[Assignment]`, import both from `..schemas`, and add a test that constructs real `AttendanceRow`/`Assignment` objects. `Assignment` is defined at `schemas.py:173-180`. |
| A1-9 | Card ids deterministic `card-{task_id}-{volunteer_id}-{role_slug}`; one card per volunteer/task/role; draft for assigned volunteers plus explicitly mentioned volunteers (A1 item 9) | **MISSING** | Only a documentation comment: `backend/app/schemas.py:274` (`id: str # deterministic: f"card-{task_id}-{volunteer_id}-{role_slug}" ...`). `grep -rn 'card-{' backend/app` finds no implementation; `role_slug` appears only in that comment. `extract.draft_cards` is a stub (`extract.py:22-24`). | Fix in B3: implement a slug helper (ASCII lower, `[^a-z0-9]+` -> `-`, strip), build `card-{task_id}-{volunteer_id}-{slug}`, key cards by `(task_id, volunteer_id, role)` to avoid duplicates, and test that two calls return the same ids. |
| A1-10 | Ledger threat model limited to edits/reorder/interior deletion; tail truncation only against a separately kept head; `head_hash()`; `verify(trusted_head: str | None = None)`; crash-safe flush+fsync; thread-safe; docstring says so (A1 item 10) | **SATISFIED** | Honest limit at `backend/app/evidence/ledger.py:5` and `:11-21`; `head_hash()` at `:236-247`; `verify(trusted_head=...)` at `:254` and anchor check at `:325-335`; journal fsync at `:188`; sidecar fsync at `:198`; `RLock` at `:140`; append under lock at `:210-234`. Runtime probe (below): after deleting the tail and rewriting the sidecar consistently, legacy `verify()` returns `ok=True`, while `verify(trusted_head=anchor)` returns `ok=False, first_bad_index=1`. | None for A1. Residual documented limitation: no directory fsync after `os.replace` (`ledger.py:72-74`); acceptable for this prototype and already stated. |
| A1-11 | LLM failures raise `llm.client.LLMError`; unit tests monkeypatch the client; no network in tests (A1 item 11) | **MISSING (deferred to B2/B3)** | `extract.extract_roles` and `extract.draft_cards` still `raise NotImplementedError` (`backend/app/llm/extract.py:13-15`, `:22-24`). B1 redaction tests explicitly make no network calls (`backend/tests/llm/test_redact.py:1-6`) and pass, but there is no LLM call to raise `LLMError` from yet. | Fix in B2 (extract_roles) and B3 (draft_cards): catch client failures and raise `LLMError`; add monkeypatched tests (no network) for both success and failure paths. |
| TASK B1.1 | `llm/redact.py` + `extract.redact()`: Indian PII before any model call; phone/Aadhaar/PAN/email/UPI/bank-account; typed placeholders; count; at least 25 positive and 15 negative cases; PIN/date/hour ranges not redacted; document names not detected in module docstring (TASK.md line 7) | **SATISFIED** | Six rules at `backend/app/llm/redact.py:35-57`; `redact()` overlap resolution/count at `:60-83`; names-not-detected docstring at `:5-6`; wrapper at `backend/app/llm/extract.py:5,8-10`. Independent counts: 33 positive / 35 negative, all distinct. 77 targeted tests pass. Probe: PIN/date/hour-range inputs all return count 0. | None against the card. Optional R2 improvements are in the R2 section below (none are B1 acceptance failures). |
| TASK B1.2 | `extract_roles(brief_text, language_hint)`: redact first; taxonomy; validation; counts; Devanagari tolerance; `max_tokens 3000`; `LLMError` on failure (TASK.md line 7) | **PARTIAL** | `extract.redact()` wrapper works (`extract.py:5,8-10`), but `extract_roles` is still `raise NotImplementedError` (`extract.py:13-15`). Prompt/taxonomy/LLMError work is B2 by the batch plan (`TASK.md:17`). | B2 owns the remainder. No B1 fix; just do not claim B1.2 complete. |
| TASK B1.5 | `evidence/rules.py check_card`: at least 9 deterministic rules, each tested; codes/severity/plain message; nothing auto-rejected (TASK.md line 11) | **SATISFIED** | 10 codes parsed from source at `backend/app/evidence/rules.py:426,435,444,455,466,476,485,494,506,516`; catalogue/docstring at `:1-59`; `check_card` at `:407-522`; no mutation/auto-reject stated at `:4-7`; typed rows now accepted (`:407-408`). Targeted evidence tests pass; full suite green. | None. |
| TASK B1.6 | `evidence/ledger.py Ledger`: append-only SHA-256 chain over prev_hash/ts/action/card_id/actor/payload_hash; JSON-lines file; `verify()` detects edited/deleted/reordered and reports `first_bad_index`; thread-safe; tamper test; docstring states "a hash chain shows edits, not truth" (TASK.md line 12) | **SATISFIED** | Canonical line/hash at `ledger.py:102-128`; class/append/verify at `:131-340`; honest statement at `:5`; tamper semantics at `:276-287`; fsync at `:188,198`; RLock at `:140`; tamper tests in `backend/tests/evidence/test_ledger.py` (targeted suite passes). | None. |

## Commands and raw outputs

Windows console output below is shown with CR characters removed; the text is
otherwise verbatim. Commands were run from the repo root unless they `cd` into
`backend`.

### 1. Redaction case counts (independent import of the test module)

```
$ cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -c "import importlib.util, pathlib; p=pathlib.Path('tests/llm/test_redact.py'); s=importlib.util.spec_from_file_location('t',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print('POSITIVE inputs:', len(m.POSITIVE), 'distinct:', len(set(x[0] for x in m.POSITIVE))); print('NEGATIVE inputs:', len(m.NEGATIVE), 'distinct:', len(set(m.NEGATIVE))); print('positive >=25:', len(m.POSITIVE)>=25, 'negative >=15:', len(m.NEGATIVE)>=15)"
POSITIVE inputs: 33 distinct: 33
NEGATIVE inputs: 35 distinct: 35
positive >=25: True negative >=15: True
```

### 2. Ten rule codes, parsed from source with `ast`

```
$ cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -c "import ast, pathlib; t=ast.parse(pathlib.Path('app/evidence/rules.py').read_text(encoding='utf-8')); codes=sorted({n.value.value for n in ast.walk(t) if isinstance(n,ast.keyword) and n.arg=='code' and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str)}); print('rule code count:',len(codes)); print('codes:', ', '.join(codes))"
rule code count: 10
codes: duplicate_evidence_ref, hours_exceed_recorded, identical_summary_text, implausible_hours, minor_without_guardian_consent, missing_evidence_ref, no_attendance_record, overlapping_tasks, round_number_inflation, self_declared_skill_unconfirmed
```

### 3. Ledger docstring: honest hash-chain limit

```
$ cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -c "import ast,pathlib; s=ast.parse(pathlib.Path('app/evidence/ledger.py').read_text(encoding='utf-8')); d=ast.get_docstring(s); print('docstring states hash-chain limit:', 'hash chain shows edits, not truth' in d.lower()); print('docstring mentions tail truncation:', 'TAIL TRUNCATION' in d); print('docstring mentions trusted_head:', 'trusted_head' in d); print('docstring mentions head_hash:', 'head_hash()' in d); print('docstring mentions fsync:', 'fsync' in d)"
docstring states hash-chain limit: True
docstring mentions tail truncation: True
docstring mentions trusted_head: True
docstring mentions head_hash: True
docstring mentions fsync: True
```

### 4. Final A1 signatures (after the concurrent sibling edits)

```
$ cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -c "import inspect; from app.evidence import rules, ledger; print('check_card:',inspect.signature(rules.check_card)); print('verify:',inspect.signature(ledger.Ledger.verify)); print('head_hash:',inspect.signature(ledger.Ledger.head_hash))"
check_card: (card: 'ContributionCard', all_cards: 'list[ContributionCard]', attendance_rows: 'list[AttendanceRow]') -> 'list[Flag]'
verify: (self, trusted_head: 'str | None' = None) -> 'LedgerVerification'
head_hash: (self) -> 'str'
```

An earlier snapshot during the review (before the sibling finished) showed
`attendance_rows: 'list[dict]'`, `verify: (self)`, and no `head_hash`; I did not
use that stale snapshot for the verdict. The final signatures above are the
current state.

### 5. `check_card` actually consumes typed `AttendanceRow`

```
$ cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -c 'from app.schemas import AttendanceRow, ContributionCard
from app.evidence.rules import check_card
card=ContributionCard(id="card-task-01-v-001-first-aider",task_id="task-01",volunteer_id="v-001",role="first-aider",claimed_hours=8.0,summary="synthetic",status="draft")
row=AttendanceRow(volunteer_id="v-001",task_id="task-01",hours=3.0,age=16,guardian_consent=None)
print("typed row -> codes:", [f.code for f in check_card(card,[], [row])])
print("dict row  -> codes:", [f.code for f in check_card(card,[], [row.model_dump()])])'
typed row -> codes: ['hours_exceed_recorded', 'minor_without_guardian_consent', 'missing_evidence_ref']
dict row  -> codes: ['hours_exceed_recorded', 'minor_without_guardian_consent', 'missing_evidence_ref']
```

### 6. `trusted_head` catches a coordinated journal + sidecar truncation

```
$ cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -c 'import json,tempfile,pathlib
from app.schemas import ContributionCard
from app.evidence.ledger import Ledger
p=tempfile.mktemp(suffix=".jsonl")
L=Ledger(p)
c1=ContributionCard(id="card-task-01-v-001-first-aider",task_id="task-01",volunteer_id="v-001",role="first-aider",claimed_hours=3.0,summary="synthetic")
c2=ContributionCard(id="card-task-01-v-002-first-aider",task_id="task-01",volunteer_id="v-002",role="first-aider",claimed_hours=3.0,summary="synthetic two")
L.append("draft",c1,"host-01"); L.append("draft",c2,"host-01")
anchor=L.head_hash()
print("anchor:",anchor[:16],"verify:",L.verify().ok)
lines=pathlib.Path(p).read_text(encoding="utf-8").splitlines(); pathlib.Path(p).write_text(lines[0]+"\n",encoding="utf-8")
pathlib.Path(p+".head").write_text(json.dumps({"count":1,"head_hash":json.loads(lines[0])["entry_hash"]}),encoding="utf-8")
print("after coordinated truncation, legacy verify ok:",L.verify().ok,"first_bad:",L.verify().first_bad_index)
v=L.verify(trusted_head=anchor)
print("trusted-head verify ok:",v.ok,"first_bad:",v.first_bad_index)
print("note:",v.note)'
anchor: 3f75161e26832f3f verify: True
after coordinated truncation, legacy verify ok: True first_bad: None
trusted-head verify ok: False first_bad: 1
note: Trusted head hash does not match the current chain head (expected 3f75161e26832f3f76a5a16411bb19108d90170c929cde49c7da1ab72f8fdf7e, found 0a73a08680bb458862ee3e888851164003f6a58be70d5f28723929734c02c8fd): possible tail truncation or replacement of the chain. Hash chain shows edits, not truth; truth comes from host confirmation.
```

This is exactly A1 item 10's claim: the chain alone sees a shorter, consistent
history; only the separately kept `head_hash()` anchor exposes the truncation.

### 7. Targeted suites (redaction + rules + ledger)

```
$ cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q tests/llm/test_redact.py tests/evidence/test_rules.py tests/evidence/test_ledger.py
C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pytest_asyncio\plugin.py:306: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture scope. Future versions of pytest-asyncio will default the loop scope for "function" scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
........................................................................ [ 52%]
..................................................................       [100%]
============================== warnings summary ===============================
tests/evidence/test_rules.py: 72 warnings
  C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pydantic\main.py:280: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
138 passed, 72 warnings in 2.41s
```

Redaction-only run (reviewer):

```
$ cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q tests/llm/test_redact.py
77 passed in 0.21s
```

### 8. Full suite, current HEAD (reviewer-run)

```
$ cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q .
437 passed, 73 warnings in 3.65s
```

The lead's earlier authoritative B1 run was `420 passed, 60 warnings in 3.49s`
(quoted from `PROGRESS.md:46`; I did not re-run that historical command). The
current 437 reflects the sibling A1 test additions; the suite is green now.

## R2/R3 alignment of the B1 redactor

R2's redaction recommendation (R2 lines 137-149) and limitations (R2 lines
159-169) were checked against `redact.py`:

- **False positives on PIN codes, dates, hour ranges: PASS.** The dedicated
  negative cases are in `test_redact.py:82-118` and the count guard is
  `:128-129`. I also ran an independent probe:

```
$ cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -c 'from app.llm.redact import redact
cases=[("PIN 6digit","208001"),("PIN prose","PIN 208001 and year 2026"),("date slash","12/01/2026"),("date ISO","2026-01-12"),("date text","12 Jan 2026"),("hour range","9am-5pm"),("hour range 24h","09:00-17:00"),("Aadhaar hyphen R2","1234-5678-9012"),("Devanagari digits R2","९८७६५४३२१०"),("dotted phone","987.654.3210"),("NAME cue R2","नाम: राम कुमार यादव"),("ADDRESS cue R2","Address: House 999, Synthetic Nagar"),("free name","Asha Devi coordinated the camp")]
for label,raw in cases:
 out,n=redact(raw)
 print(label, "|", raw, "->", out, "| count=", n)'
PIN 6digit | 208001 -> 208001 | count= 0
PIN prose | PIN 208001 and year 2026 -> PIN 208001 and year 2026 | count= 0
date slash | 12/01/2026 -> 12/01/2026 | count= 0
date ISO | 2026-01-12 -> 2026-01-12 | count= 0
date text | 12 Jan 2026 -> 12 Jan 2026 | count= 0
hour range | 9am-5pm -> 9am-5pm | count= 0
hour range 24h | 09:00-17:00 -> 09:00-17:00 | count= 0
Aadhaar hyphen R2 | 1234-5678-9012 -> 1234-5678-9012 | count= 0
Devanagari digits R2 | ९८७६५४३२१० -> [BANK_ACCOUNT] | count= 1
dotted phone | 987.654.3210 -> 987.654.3210 | count= 0
NAME cue R2 | नाम: राम कुमार यादव -> नाम: राम कुमार यादव | count= 0
ADDRESS cue R2 | Address: House 999, Synthetic Nagar -> Address: House 999, Synthetic Nagar | count= 0
free name | Asha Devi coordinated the camp -> Asha Devi coordinated the camp | count= 0
```

- **Names are not detected: documented, PASS for the card.** `redact.py:5-6`
  says "PERSON NAMES ARE NOT DETECTED -- there is no named-entity recognition
  (NER) here". B1a's limitations say the same. This is the exact limit the card
  requires, not a hidden gap.
- **R2 patterns B1 lacks, classified:**
  - *Devanagari digit normalization* (`DEV_TO_ASCII` in R2 line 140) is
    explicitly planned for B2, not a B1 gap. One related nit is real: the
    `redact.py:32` comment says "Digits are ASCII [0-9] on purpose", but the
    Aadhaar/bank patterns use `\d`, which in Python 3 matches Devanagari digits;
    the probe shows a 10-digit Devanagari numeral becomes `[BANK_ACCOUNT]`. Fix
    in B2 when normalisation lands (or switch those two rules to `[0-9]`).
  - *Cue-based NAME/ADDRESS regexes* (R2 lines 145-146) are high-precision,
    low-recall heuristics R2 recommends; the B1 card only requires documenting
    that names are not detected. Deferred to B2/UI; not a B1 acceptance gap.
  - *Hyphen-separated Aadhaar* (`1234-5678-9012`): R2's pattern allows
    `[\s\-]?`, B1 only allows spaces. The B1 card says "with or without spaces",
    so this is an R2 alignment gap, not a card failure; a one-line regex
    extension in B2 is cheap. The probe above confirms the miss.
  - *Dotted phone separators* are deliberately unmatched, and R2's phone
    pattern also does not use dots, so this is a documented limitation, not an
    R2 pattern B1 dropped.
  - *Verhoeff flag* (R2 lines 149, 162) is an optional second-order signal; B1
    correctly does not use a checksum to skip redaction. Not required.
  - *Local raw-brief audit log* (R2 line 84) is a pipeline/architecture item, not
    in the B1 card; note for B2/B3.
- **R3 ledger alignment: PASS.** R3 lines 105-106 recommend canonical bytes,
  `prev_hash`, recompute-on-verify and an external head anchor; R3 line 126
  states the honest limit. `ledger.py:5,11-21,102-128,236-247,254-335`
  implements exactly that and does not overclaim. No R3 gap in B1.

## Report trim: B1a_redact.md

The original B1a report was 1,059,388 bytes because a mid-write full-suite run
with thousands of tracebacks was pasted verbatim. I rewrote it to the
implementation summary, case counts, targeted command/output, the quoted lead
authoritative command and `420 passed, 60 warnings in 3.49s` line, a pointer to
`PROGRESS.md`, R2/R3 short notes, and the limitations. No output was fabricated:
the 420 line is labelled as quoted from `PROGRESS.md`; the 437 line is a run I
did make.

```
$ cd C:/Users/shubh/Projects/sewacircle && wc -c docs/lanes/B-llm-evidence/reports/B1a_redact.md
6261 docs/lanes/B-llm-evidence/reports/B1a_redact.md
```

| File | Before (bytes) | After (bytes) | Saved |
|---|---:|---:|---:|
| `docs/lanes/B-llm-evidence/reports/B1a_redact.md` | 1,059,388 | 6,261 | 1,053,127 (99.41%) |

Arithmetic was run, not estimated:

```
$ cd C:/Users/shubh/Projects/sewacircle && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -c "b=1059388; a=6261; print('before',b); print('after',a); print('saved',b-a); print('pct',round((b-a)/b*100,2))"
before 1059388
after 6261
saved 1053127
pct 99.41
```

**Out of scope but worth noting:** `B1b_rules.md` is still 1,140,214 bytes with
the same kind of raw full-suite traceback block. I may not write that file; the
lead (or B1b's owner) should trim it the same way.

## Prioritized gaps for the lead

1. **P0 - A1 item 9 is unimplemented.** Only the `schemas.py:274` comment exists;
   no code builds `card-{task_id}-{volunteer_id}-{role_slug}`. B3's
   `draft_cards` must implement it (slug + dedupe + mentioned-volunteer rule)
   and test idempotence.
2. **P0 - A1 item 8 is only half done.** `check_card` is typed and verified, but
   `extract.draft_cards` still takes `list[dict]` (`extract.py:22`). B3 must
   change the signature to `list[AttendanceRow]` / `list[Assignment]`.
3. **P0 - A1 item 11 does not exist yet.** No `LLMError` path and no
   monkeypatched LLM tests until B2/B3 implement `extract_roles`/`draft_cards`.
4. **P1 - trim `B1b_rules.md` (1.14 MB).** Raw mid-write tracebacks are still
   there; use the same treatment as B1a.
5. **P1 - `redact.py:32` comment/code mismatch.** `\d` is Unicode-aware, so
   long Devanagari numerals hit `[BANK_ACCOUNT]`; resolve with B2 normalisation
   (or `[0-9]` in the Aadhaar/bank patterns) and add a test.
6. **P2 - R2 alignment nits, not B1 failures:** hyphen-separated Aadhaar,
   cue-based NAME/ADDRESS heuristics, Verhoeff flag, audit-log copy of the raw
   brief. Schedule with B2/B3, do not claim them for B1.
7. **Process note - concurrent writers.** `rules.py` and `ledger.py` were being
   edited while I reviewed. I saw a stale `list[dict]`/no-`head_hash` snapshot
   first and waited for the A1 signatures; all evidence above is the final state
   (`rules.py` mtime 23:38:39 IST). If those files change again, re-run the
   signature and suite commands before trusting this table.

## Self-verification of this report

Command:

```
$ cd C:/Users/shubh/Projects/sewacircle && test -f docs/lanes/B-llm-evidence/reports/B1X_c_review.md && echo EXISTS && wc -c docs/lanes/B-llm-evidence/reports/B1X_c_review.md && wc -l docs/lanes/B-llm-evidence/reports/B1X_c_review.md
EXISTS
23985 docs/lanes/B-llm-evidence/reports/B1X_c_review.md
306 docs/lanes/B-llm-evidence/reports/B1X_c_review.md
```

Exit code: 0. The report exists on disk. The `wc -c`
figure was measured immediately before this verification block was appended,
so the final file is a few bytes larger than that figure.
