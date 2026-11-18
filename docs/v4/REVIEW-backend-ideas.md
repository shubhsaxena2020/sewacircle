# Head review: backend-ideas (Claude Code)

## Accepted
- 652ad56 + fixes (Antigravity): GET /api/geo/tree, ETag per RFC 9110 list/weak/* matching, blocks_available + blocks_note,
  caveat + retrieved_date carried through. Tests cover each case.
- Hermes: card state machine (one TRANSITIONS table, 409 on illegal edges with legal actions named, request_revision needs a
  reason, reason folded into the ledger hash as an optional 7th field so old journals still verify, terminal states final).
  Suite 767 passed at review time.

## Share keys (Hermes, feat(drive)) - needs follow-up
1. No way to OBTAIN a key. Nothing in the API returns share_key, so the UI cannot offer "share this drive". Add an organiser
   route (e.g. POST /api/drive/share {task_id} -> {share_key, path}) gated by the capability matrix (organiser only).
2. Inconsistent public summary: roles/title come from the server's synthetic task, but `ready` comes from the last
   /api/roster request for that task id, whose roles the organiser may have edited. Store a snapshot of what was planned
   (title, roles with counts, ready, computed_at) when the roster is computed and serve that snapshot; fall back to the
   synthetic task with ready=null.
3. task_id_for_share_key: `secret = server_secret()` is unused. Remove.
4. Add computed_at to the summary so a viewer can see how fresh the verdict is.
