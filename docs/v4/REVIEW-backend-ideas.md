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

## Capabilities (Hermes, aa20bf1) - accepted, 2 notes
- Good: one CAPABILITIES dict drives both GET /api/capabilities and a FastAPI dependency on every mutating evidence route,
  so menu and API cannot drift; "demo role switch, not authentication" stated in module, route and every 403 message;
  default organiser keeps old clients working. Suite 813 passed at review time.
- Note 1: unknown role is 403 on mutating routes (header) but 422 on GET /api/capabilities (query). Acceptable, but say so in
  BACKEND-PATTERNS.md.
- Note 2: read_roster is listed but /api/roster, /dropout, /why-not are not gated. Gate them with the same dependency
  (organiser only) so the matrix is honest, or drop read_roster from host's absent list explicitly in the docs.

## Hindi display text (Hermes, feat(i18n)) - accepted with 2 follow-ups
- Good: Hindi built from the same structured facts as the English (no sentence translation), unknown labels left unchanged
  rather than machine-translated, LLM text explicitly out of scope, place names not transliterated; RecruitRequest.kind added so
  the Hindi template is chosen from data, not by parsing English. Natural Hindi for skills/titles/slots. Suite 839 passed.
- Follow-up 1 (honesty): the Hindi pick reason is a fixed "chosen for <role>; N km away, <slot> available" line, while the English
  carries the solver's specific reasons (skill level, not picked in 90 days, newcomer, mentor pairing...). The Hindi view thus
  drops the fairness/newcomer reasons that are the product's point. Render each English reason from its structured cause in Hindi
  too (the reasons are produced in solver/cp_sat.py; expose a reason code + params alongside the text).
- Follow-up 2: the Hindi standby template drops the volunteer's name ("if this person cannot come" -> no name); fine, but then the
  English should not show a name either, or both should. Keep the two languages equivalent in information.
