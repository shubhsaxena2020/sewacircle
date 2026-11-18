YOU ARE A HERMES LEAD. Work in C:\Users\shubh\Projects\sewacircle-backend (a git worktree, branch backend-ideas). Edit ONLY files
under backend\ and docs\v4\ in that folder. Do not touch C:\Users\shubh\Projects\sewacircle (another agent is working there),
do not push, do not touch frontend\. Commit locally in small commits. Use at most 3 parallel subagents. Keep a PROGRESS.md at
docs\v4\HERMES-BACKEND-PROGRESS.md and update it after every step.

CONTEXT. SewaCircle Ready Crew is a FastAPI prototype (backend\app\main.py, schemas.py, evidence\ledger.py, solver\, llm\) for an
organiser-side youth-volunteering crew planner. Read README.md, PROJECT_REPORT.md, CONTEXT.md and backend\app\schemas.py first.
Tests: from backend\ run ..\..\sewacircle\.venv\Scripts\python.exe -m pytest -q (the venv lives in the main checkout). All 692
current tests must keep passing.

WHAT TO ADD. Four original, clean-room features. They are generic engineering patterns; do NOT copy any code, text, names,
endpoint paths, keys or assets from any other system. Write every line yourself.

1. Contribution card state machine with a back-edge. Today a card goes draft or flagged, then the host does confirm, correct or
   reject. Add a host action request_revision (with a required reason) that moves a card to revision_requested; a re-draft
   of that volunteer's card returns it to draft. Every transition records actor, reason and timestamp in the hash-chained ledger
   (add the new action name to LedgerEntry.action). Illegal transitions return HTTP 409 with a clear message. Add a
   transition table in code (one dict) and a test per legal and illegal edge.

2. Opaque share keys. Add GET /api/drive/{share_key} that returns a public, read-only summary of one drive (title, district,
   block, slot, roles with counts, ready verdict if a roster was computed in this process) and NO volunteer names or ids.
   share_key = first 16 chars of base32 of HMAC-SHA256(server secret, task id). The server secret comes from env SEWA_SHARE_SECRET,
   or a random value generated at startup and kept in memory (state that in the docstring). Sequential task ids must never be
   accepted on this route. Tests: unknown key 404, key does not reveal the task id, response contains no volunteer id or name.

3. One cached geography tree. Add GET /api/geo/tree returning the 20 UP districts from docs\research\up_districts.json with their
   blocks from backend\app\data\synth.py BLOCKS as one nested JSON tree (state > district > block), with the source URL fields
   carried through, computed once and cached (functools.lru_cache). Include an ETag header and honour If-None-Match with 304.
   Tests for shape, caching and 304.

4. Capability-driven menu (demo roles, no real auth). Add GET /api/capabilities?role=organiser|host|volunteer|viewer returning
   the list of screens and actions that role may use (for example host may confirm cards; viewer may only read the evaluation).
   Enforce the same matrix server-side on the mutating evidence routes using a request header X-Demo-Role (default organiser so
   current clients keep working); a forbidden action returns 403. Say clearly in the docstring that this is a demo role switch,
   not authentication. Tests for each role and the default.

Also write docs\v4\BACKEND-PATTERNS.md: for each feature, what it does, why it matters for a youth-volunteering organiser, the
endpoints and schemas, and the exact test command output. Then run the full test suite and paste its real final line.

RULES. No invented numbers. No secrets in code. Do not change the behaviour of existing endpoints except adding the optional
X-Demo-Role check (default organiser). When done, write DONE as the last line of PROGRESS.md.
