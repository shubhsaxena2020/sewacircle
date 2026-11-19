# PROGRESS - Hermes backend patterns (card state)

Worktree: `C:\Users\shubh\Projects\sewacircle-backend`, branch `backend-ideas`.
Edits only under `backend/` and `docs/v4/`. Local commits only, never pushed.

Detailed logs: `docs/v4/HERMES-BACKEND-PROGRESS.md` (round 1: three patterns) and
`docs/v4/HERMES-ROUND2-PROGRESS.md` (round 2: head-review follow-ups and Hindi display).
Design write-up: `docs/v4/BACKEND-PATTERNS.md`.

## Delivered

1. Card state machine with a back-edge - `backend/app/evidence/transitions.py` (one `TRANSITIONS` dict),
   `POST /api/evidence/{card_id}/request_revision` (required reason, 422 if blank), `revision_requested`
   status, illegal moves 409 with the legal actions named, re-draft returns the card to `draft`, and
   `LedgerEntry.reason` is hashed when present while old reason-less journals still verify.
2. Opaque share keys - `backend/app/share.py` (`base32(HMAC-SHA256(secret, task_id))[:16]`, 80 bits),
   `GET /api/drive/{share_key}` public read-only summary with no volunteer id or name and no sequential
   task ids accepted, `POST /api/drive/share` to mint a link (organiser only), secret from
   `SEWA_SHARE_SECRET` or a random value generated at startup and kept in memory only.
3. Capability-driven menu - `backend/app/capabilities.py` (one matrix for organiser/host/volunteer/viewer),
   `GET /api/capabilities`, and `X-Demo-Role` enforcement (default organiser) on the mutating roster,
   evidence, export, share-mint and demo-reset routes; 403 on a forbidden action. Docstrings state that
   this is a demo role switch, not authentication.
4. Round-2 follow-ups - share mint route, plan snapshot served by the public summary, roster gating,
   and `lang=en|hi` display blocks for tasks and rosters whose ids, counts and decisions are identical in
   both languages (card text stays in its original language).

## Verification (real output)

```
..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/evidence/test_transitions.py -q
38 passed in 0.18s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/evidence/test_card_state_machine.py -q
36 passed, 39 warnings in 5.20s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_share_keys.py -q
26 passed, 1 warning in 1.54s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_capabilities.py -q
32 passed, 25 warnings in 2.12s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_i18n.py -q
15 passed, 2 warnings in 1.46s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest -q
845 passed, 156 warnings in 17.14s
```

Baseline before this work was 692 passed; all of those still pass.

## Verification rounds (independent, read-only subagents)

Three independent reviewers checked the code against the brief. Real defects they
found were fixed, not documented away:

1. A re-draft that tripped a rule ended in `flagged` because the transition table's
   return value was discarded; the back-edge now applies the table's target (`draft`)
   and keeps the rule flags on the card.
2. `_decide` mutated the shared card object before appending to the ledger, so a failed
   append left a decided card with no audit entry; the entry is now appended first and
   the card committed after it.
3. The Hindi pick sentence rounded distance differently from the English one (stored
   `distance_km` is 1 dp, English uses the raw value), so it no longer quotes a
   distance; the Hindi standby sentence used the English role name; the Hindi verdict
   lines dropped the unfilled-role and robustness facts. All three fixed, each with a test.
4. The legacy-journal test was hash-neutral (it stripped a field that was already
   absent from the hash); it now builds a genuine six-field pre-feature journal by hand.
5. The share route's snapshot branch had no no-leak test; it now scans the snapshot
   response for every synthetic volunteer id and name.
6. The share-secret docstring claimed that changing the environment variable rotates
   keys in-process; it does not (the value is cached), and the docstring now says so
   with a test pinning the behaviour.

CARD COMPLETE
