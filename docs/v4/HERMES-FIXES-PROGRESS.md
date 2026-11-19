# Hermes fixes B1-B3 - progress

Worktree `C:\Users\shubh\Projects\sewacircle-backend`, branch `backend-ideas`. Brief:
`docs/v4/BRIEF-hermes-fixes-B.md`. Edits only under `backend/` and `docs/v4/`. Local commits only, never
pushed.

Baseline at the start of this session: **845 passed** (measured before touching anything).

Test command (from `backend/`, venv lives in the main checkout):

```
..\..\sewacircle\.venv\Scripts\python.exe -m pytest -q
```

## Where the review documents actually are

`docs/v4/HARD-REVIEW.md` and `docs/v4/FIX-PLAN.md` are **not in this branch's tree** - they were committed
on `frontend-v2` (commit c56a0bd, "Codex hard review + fix plan"). The brief points at them as if they were
local; they are not, so they were read with `git show c56a0bd:docs/v4/HARD-REVIEW.md` and
`git show c56a0bd:docs/v4/FIX-PLAN.md`. Nothing was taken on trust: every B1-B3 acceptance check in
`FIX-PLAN.md` is mapped to a test below. This branch does not need to add those two files - they are
already committed on the other branch, and adding a second copy here would create a merge conflict for no
reason.

## B1-B3 acceptance checks, from FIX-PLAN.md, against this branch

| Check (FIX-PLAN.md) | Where it is satisfied |
|---|---|
| Inject an append failure: card and journal unchanged, `verify` succeeds | `test_a_failed_append_leaves_the_card_and_the_journal_unchanged` (bytes identical, in-memory card `draft`, `verify ok`) |
| Simultaneous confirm/reject: one 200, one 409, one decision entry | `test_simultaneous_confirm_and_reject_give_one_200_and_one_409` (barrier, 3 rounds) |
| Corrected hours and flags agree | `test_correct_above_the_recorded_hours_stores_the_warning`, `test_correct_back_down_clears_the_warning`, `test_correct_to_an_implausible_number_stores_the_block_flag` |
| A flagged redraft cannot look clean | `test_redraft_that_trips_a_rule_lands_in_flagged_not_draft` + `test_no_other_state_has_a_redraft_edge` |
| Empty/failed drafting retains undecided cards | `test_an_empty_draft_with_assignments_is_502_and_changes_nothing`, `test_an_empty_draft_with_no_assignments_keeps_the_undecided_cards` |
| All legal/illegal transitions and bilingual reason facts have API tests | `tests/evidence/test_transitions.py` (10 edges / 26 illegal pairs), `tests/test_i18n.py` (digit-for-digit EN-vs-HI, every code renders, standby name in both) |
| Anonymous requests cannot reset/decide/enumerate cards | `tests/test_public_demo.py` (11 mutating routes 403, 4 private reads 403, wrong token 403, missing token fail-closed) |
| Role simulation is labelled and cannot grant privileges | `test_the_demo_role_can_never_grant_what_the_token_does_not`, `test_the_token_does_not_grant_a_role` |
| District read does not alter share output | `test_drive_status_reports_the_last_verdict_and_changes_nothing`, `test_the_status_route_never_calls_the_solver` |
| Post-dropout share result is current or explicitly stale | `test_a_dropout_refreshes_the_snapshot_and_marks_it_stale`, `test_re_solving_the_roster_clears_staleness` |

One acceptance phrase was treated as documentation rather than code: "define single-writer behavior across
processes". There is no multi-process store to define behaviour for, so the honest answer is written down
instead - one process-wide `threading.RLock`, explicitly single-process, with the consequences of running
two workers spelled out in the `app/main.py` module docstring and in BACKEND-PATTERNS section 5.

## Step log

### B1 - atomic decisions (commit ed69f7b)

- [x] One process-wide `threading.RLock` (`main.CARD_LOCK`) around lookup -> transition -> ledger append ->
      store -> card-file write in `_decide`; the drafting route and the demo reset take the same lock.
- [x] `_save_cards()` writes a temp file in the data directory (`flush` + `os.fsync`), then `os.replace`s it
      over `cards.json`; no `.tmp` file survives a successful write.
- [x] Append-before-store kept (already committed in 40e049a); on append failure nothing is committed,
      because the store write and the file write both happen after it.
- [x] Single-process limitation documented in the `app/main.py` module docstring (two uvicorn workers would
      each have their own lock, store and ledger RLock; the chain would fork).
- [x] Tests: `backend/tests/evidence/test_atomic_decisions.py` (new, 6). The barrier test was validated
      against a deliberately unlocked build (temporary conftest replacing `CARD_LOCK` with
      `contextlib.nullcontext()`): all three rounds failed there, so it detects a missing lock rather than
      passing by luck. The conftest was removed afterwards.

### B2 - rules and revision semantics (commit b26f8c1)

- [x] `correct` re-runs `rules.check_card` on the corrected card and persists the new flags before the ledger
      append, so the flags are inside the hashed card payload; the status stays `corrected`.
- [x] Attendance rows come from a per-task cache filled by the draft route; after a restart the card's
      persisted `recorded_hours` is turned back into one row, so claim-vs-record still works.
- [x] The ONE transition table gains `("revision_requested", "redraft_flagged") -> "flagged"`; the drafting
      route picks `redraft` or `redraft_flagged` from the new text's flags. Ledger action follows (`draft` /
      `flag`), and the reason names the revision request.
- [x] Empty drafting is non-destructive: no cards + assignments sent -> 502 ("nothing was changed"); no
      assignments -> `[]`. Checked before the supersede loop, so nothing is deleted either way.
- [x] `schemas.PickReason(code, params)` + `Assignment.reason_codes`; the solver writes codes for every pick
      reason (skill level, self-declared, open role, slot + distance, not picked in N days, heavy recent
      pick, newcomer + mentor name, experienced mentor, guardian consent, promoted from standby) and the
      English sentences are rendered from them by `i18n.reason_text(code, "en")`.
- [x] Hindi rendered from the same codes (`reason_text(code, "hi")`), so level, km, 90-day window, past-drive
      counts and the mentor's name are identical facts in both languages. `RecruitRequest.blocked_by_names`
      keeps the standby person's name in both.
- [x] Tests: `tests/evidence/test_revision_and_rules.py` (new, 8), `tests/evidence/test_transitions.py`,
      `tests/evidence/test_card_state_machine.py`, `tests/test_i18n.py`.

### B3 - public-demo boundary (commit 1ec4fc4)

- [x] `backend/app/demo_mode.py`: `SEWA_PUBLIC_DEMO` (off unless `1/true/yes/on`) and `SEWA_OPERATOR_TOKEN`,
      compared with `X-Operator-Token` via `hmac.compare_digest`; with the switch on and no token configured
      it **fails closed** (403 naming the missing variable).
- [x] Gate on every mutating route (reset, roster, why-not, dropout, draft, four decisions, export, share
      minting) and on the personal-data reads `/api/evidence/cards`, `/api/ledger`, `/api/ledger/verify`,
      `/api/volunteers`.
- [x] `/api/tasks`, `/api/eval`, `/api/geo/tree`, `/api/capabilities`, `/api/drive/{key}` (plus
      `/api/drive/status`, `/api/health`, `/api/meta`) stay public.
- [x] `X-Demo-Role` remains a labelled simulation on top: operator token -> demo role -> capability matrix.
- [x] Plan-versioned share snapshots: `share.plan_version()` (sha256 over roles + options + crew + standby)
      stored with `computed_at`; the dropout route refreshes the snapshot with the healed plan;
      `GET /api/drive/{key}` computes `stale` on read against the organiser's latest solved roster.
- [x] `GET /api/drive/status`: `{task_id, ready, computed_at, stale}` for every known task id, nulls before
      any plan, no solver call, no state change; declared before `/api/drive/{share_key}` so the literal
      path is not parsed as a key.
- [x] Tests: `tests/test_public_demo.py` (new, 53).

### Docs

- [x] `docs/v4/BACKEND-PATTERNS.md`: sections 1-4 updated (10-edge table, plan-versioned summary, reason-code
      catalogue, i18n contract), new sections 5 (atomic decisions), 6 (rules/revision/empty draft), 7
      (public-demo boundary), cross-cutting notes renumbered to 8 and their "pre-existing limits" list
      rewritten to say what was fixed and what is still open. Every section carries real command output.

## Real command output

```
..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/evidence/test_atomic_decisions.py -q
6 passed, 7 warnings in 2.13s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/evidence/test_revision_and_rules.py -q
8 passed, 10 warnings in 2.65s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/evidence/test_transitions.py -q
45 passed in 0.20s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/evidence/test_card_state_machine.py -q
37 passed, 41 warnings in 5.88s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_public_demo.py -q
53 passed, 23 warnings in 4.02s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_i18n.py -q
17 passed, 2 warnings in 1.67s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_share_keys.py -q
26 passed, 1 warning in 1.97s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_capabilities.py -q
32 passed, 25 warnings in 2.71s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest -q
922 passed, 195 warnings in 23.52s
```

Baseline 845 -> 922: 77 new tests, 3 rewritten (listed below), none deleted.

## Decisions worth flagging

1. **`plan_version` includes the crew.** The brief says "sha256 of the planned roles and options", but a
   dropout changes only who is on the drive, so a roles+options hash could never make the required
   "stale flag after dropout" test observable. The version hashes roles + options +
   `role_id:slot_index:volunteer_id` for every assignment + the standby ids, all sorted (order-independent,
   deterministic, sensitive to a different crew). That keeps FIX-PLAN's "a post-dropout share result is
   current or explicitly stale" true; it is documented in `app/share.py` and BACKEND-PATTERNS 2/7.
2. **Staleness is computed at read time, not stored.** The snapshot stores the version of the plan it
   describes; `latest_plan()` holds the version of the organiser's last solved `/api/roster`. A later roster
   re-syncs them (tested).
3. **Three existing tests were rewritten** because they asserted what this round reverses:
   `test_revision_requested_has_exactly_one_back_edge` (now two),
   `test_redraft_that_trips_a_rule_still_returns_to_draft` (now lands in `flagged`, plus a clean-redraft
   sibling), and `test_hindi_pick_reason_carries_no_number_that_could_disagree` (now asserts the Hindi
   digits EQUAL the English ones - the old rule existed only because Hindi had no structured source).
   `test_transitions.py` edge counts and `test_share_keys.py`'s exact-key-set assertion were updated for the
   new edges and fields.
4. **Two extra routes sit behind the token** beyond the explicit list: `GET /api/ledger/verify` (same data
   family as `/api/ledger`) and `GET /api/export/credential/{id}` (names a volunteer and their hours, and
   appends to the ledger - mutating in effect). Both are documented.
5. **`correct` keeps the status `corrected`** while storing new flags: the host's decision is not
   re-litigated by the rules; the flags are the evidence for that decision.
6. **The attendance-sheet cache is process-local.** After a restart, `correct` rebuilds rows from each card's
   persisted `recorded_hours`; a card with neither gets the honest `no_attendance_record` warning rather
   than a silent pass.
7. **`/api/drive/status` ordering is load-bearing**: FastAPI matches in declaration order, so the literal
   route is declared before `/api/drive/{share_key}` (a 6-character path would otherwise 404 as a bad key).
8. **Frontend items from the review are out of scope here** (only `backend/` and `docs/v4/` were edited):
   `optIn` labelled `सहमति`, the `aria-label` logo mismatch, district 10x roster calls and the UI revision
   controls are F1-F3/I1 work on `frontend-v2`. The backend side of the district fix (a read-only status
   source) is delivered.

CARD COMPLETE
