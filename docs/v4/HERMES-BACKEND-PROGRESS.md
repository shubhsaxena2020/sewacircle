# Hermes backend patterns - progress

Worktree: `C:\Users\shubh\Projects\sewacircle-backend`, branch `backend-ideas`.
Scope: only `backend/` and `docs/v4/` in this worktree. No push.

Baseline before any change: `pytest -q` in `backend/` printed `692 passed, 93 warnings in 10.97s`.

## Step log

- [x] Step 0 - read README/PROJECT_REPORT/CONTEXT/schemas/main/ledger, ran the suite to record the real
      baseline (692 passed). Created this file.
- [x] Step 1 - card state machine with a back-edge: `backend/app/evidence/transitions.py` (one
      `TRANSITIONS` dict), `request_revision` with a required reason, `revision_requested` status,
      `LedgerEntry.reason` folded into the hash only when non-empty (old journals still verify), 409 on every
      illegal edge, re-draft returns the card to the undecided pool. Tests: one per legal edge (9) and per
      illegal pair (21), plus HTTP tests for actor/reason/timestamp, re-draft, 422, 409, tamper detection.
      (da30d96, hardened in c1045ce)
- [x] Step 2 - opaque share keys: `backend/app/share.py` (base32 HMAC-SHA256, first 16 chars, secret from
      `SEWA_SHARE_SECRET` or random in memory), `GET /api/drive/{share_key}` serving title/district/block/
      slot/role counts/ready with no volunteer name or id, sequential task ids always 404.
      (053432c, extended in 37a33c6)
- [x] Step 3 - capability-driven menu: `backend/app/capabilities.py` (one matrix), `GET /api/capabilities`,
      `X-Demo-Role` enforcement on the mutating routes (default organiser), 403 for a forbidden action.
      Docstrings say plainly: a demo role switch, not authentication. (aa20bf1, hardened in c1045ce)
- [x] Step 4 - independent read-only review by a subagent; fixed the real findings: a revision_requested
      card stranded when its volunteer leaves the draft, the destructive demo reset outside the matrix, the
      unbounded in-memory verdict dict, plus tests for legacy journal lines, a cleared reason and the
      terminal-state converse. (c1045ce)
- [x] Step 5 - `docs/v4/BACKEND-PATTERNS.md`: what each pattern does, why an organiser cares, endpoints and
      schemas, exact test output, and the honest limits.
- [x] Step 6 - head review round 2 (share mint route + plan snapshot, roster gating, Hindi display) done and
      recorded in `docs/v4/HERMES-ROUND2-PROGRESS.md`.
- [x] Step 7 - full suite, real final line: `839 passed, 154 warnings in 16.82s`.

## Per-file test output (real)

```
..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/evidence/test_transitions.py -q
38 passed in 0.18s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/evidence/test_card_state_machine.py -q
35 passed, 37 warnings in 4.67s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_share_keys.py -q
24 passed, 1 warning in 1.83s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_capabilities.py -q
32 passed, 25 warnings in 2.87s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_i18n.py -q
12 passed, 2 warnings in 1.78s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest -q
839 passed, 154 warnings in 16.82s
```

CARD COMPLETE
