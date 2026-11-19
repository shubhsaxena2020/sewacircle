YOU ARE A HERMES LEAD. Worktree C:\Users\shubh\Projects\sewacircle-backend, branch backend-ideas. Edit only backend\ and docs\v4\.
Commit locally in small commits; never push. At most 3 parallel subagents. Progress file: docs\v4\HERMES-FIXES-PROGRESS.md; write
CARD COMPLETE as its last line when done. Tests: from backend\ run ..\..\sewacircle\.venv\Scripts\python.exe -m pytest -q
(840 pass now; all must keep passing).

Read docs\v4\HARD-REVIEW.md and docs\v4\FIX-PLAN.md (an independent hard review). Implement packages B1, B2 and B3 exactly as
described there, with these head decisions:

B1 atomic decisions. The append-before-store patch is already committed (40e049a). Add one process-wide threading.Lock around
lookup -> transition -> ledger append -> store -> atomic card-file write (write to a temp file then os.replace). On append failure
the card and journal stay unchanged. Tests: injected append failure; a barrier-based simultaneous confirm and reject on one card
gives exactly one 200 and one 409, one decision entry, and ledger verify ok. Document that the prototype is single-process.

B2 rules and revision semantics. Re-run rules.check_card after correct and persist the new flags. A redraft whose new text raises a
warn/block flag must end in flagged, not draft: add the edge ("revision_requested","redraft_flagged") -> flagged to the ONE
transition table and choose it from the flags. Empty drafting is non-destructive: if assignments were sent but no card was drafted,
return 502 and leave the store untouched. Add structured reason codes + params for every pick reason the solver writes
(backend\app\solver\cp_sat.py) and render Hindi from the codes so Hindi and English carry the same facts (skill level, not picked
in N days, newcomer, mentor pairing, distance, slot); keep the standby person's name in both languages. Tests for each.

B3 public-demo boundary (scope decided by the head: NO real login system). Add env SEWA_PUBLIC_DEMO. When it is unset (local
default) behaviour is unchanged. When it is set to 1: every mutating route (reset, roster runs, draft, decisions, share minting)
requires header X-Operator-Token equal to env SEWA_OPERATOR_TOKEN (compare with hmac.compare_digest); without it they return 403
with a clear message; GET /api/evidence/cards, /api/ledger and /api/volunteers return 403 to callers without the token, while
/api/tasks, /api/eval, /api/geo/tree, /api/capabilities and /api/drive/{key} stay public. X-Demo-Role remains a labelled
simulation on top and can never grant what the operator token does not. Make share snapshots plan-versioned: store a plan_version
(sha256 of the planned roles and options) and computed_at; update the snapshot after /api/roster/dropout; GET /api/drive/{key}
returns stale: true when the latest roster for that task differs from the snapshot. Add GET /api/drive/status that returns, for
each known task id, the last computed ready verdict and computed_at (null when not computed) WITHOUT running the solver, for the
district map. Tests for public-mode 403s, token success, stale flag after dropout, and that /api/drive/status changes nothing.

Update docs\v4\BACKEND-PATTERNS.md for every change, with real test output. Then mark B1-B3 done in the progress file.
