# Hermes fixes B1-B3 - progress

Worktree `C:\Users\shubh\Projects\sewacircle-backend`, branch `backend-ideas`. Brief:
`docs/v4/BRIEF-hermes-fixes-B.md`; inputs `docs/v4/HARD-REVIEW.md`, `docs/v4/FIX-PLAN.md`.
Edits only under `backend/` and `docs/v4/`. Local commits only, never pushed.

## State at the end of this session

**NOT STARTED.** This brief arrived while the previous card (backend patterns v4:
card state machine, share keys, capability menu, Hindi display) was finishing, and the
session budget was exhausted before any of B1-B3 could be written. No code for B1, B2
or B3 was started, so nothing is half-done: the tree is green and the working tree is
clean apart from this file.

Verified on handing over (real output, from `backend/`):

```
..\..\sewacircle\.venv\Scripts\python.exe -m pytest -q
845 passed, 156 warnings in 19.82s
```

Already in place from the previous card, which B1-B3 build on:

- `_decide` in `backend/app/main.py` appends the ledger entry first and stores the
  updated card after it (commit 40e049a / 2308abd), so an append failure cannot leave
  an unaudited decision. The process-wide lock and atomic card-file write from B1 are
  still to do.
- The transition table is `backend/app/evidence/transitions.py`; the redraft target is
  applied from the table, flags stay on the card. B2 asks for a separate
  `redraft_flagged` edge and for `correct` to re-run `rules.check_card` - neither is
  done.
- Share snapshots exist (`main.py` roster handler stores `DriveShareSummary` with
  `computed_at`); `plan_version`, the dropout refresh, `stale`, the operator-token
  boundary (`SEWA_PUBLIC_DEMO` / `X-Operator-Token`) and `GET /api/drive/status` are
  not built.

## Next steps for the next session

1. Read `docs/v4/HARD-REVIEW.md` and `docs/v4/FIX-PLAN.md` in full; the brief's B1-B3
   headings name the exact work.
2. B1: one process-wide lock around lookup -> transition -> ledger append -> store ->
   atomic card write (temp file + `os.replace`), plus the injected-failure and
   barrier-race tests; document single-process.
3. B2: re-run rules after `correct` and persist flags; add
   `("revision_requested", "redraft_flagged") -> "flagged"` to the one table and choose
   it from the flags; make empty drafting non-destructive (502, store untouched);
   structured reason codes + params for every solver pick reason with Hindi rendered
   from the codes (keep the standby person's name in both languages).
4. B3: `SEWA_PUBLIC_DEMO` + `X-Operator-Token` (constant-time compare) on every
   mutating route and on cards/ledger/volunteers; plan-versioned snapshots with
   `stale`; `GET /api/drive/status` that never runs the solver.
5. Update `docs/v4/BACKEND-PATTERNS.md` for each change with real test output, then
   replace this line with CARD COMPLETE.

CARD BLOCKED: session budget exhausted before B1-B3 were started; tree is green at 845 passed and nothing is half-implemented, so the next session can start from a clean base.
