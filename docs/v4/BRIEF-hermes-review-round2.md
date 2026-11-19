YOU ARE A HERMES LEAD. Same rules as docs\v4\BRIEF-hermes-backend-patterns.md (worktree C:\Users\shubh\Projects\sewacircle-backend,
branch backend-ideas, edit only backend\ and docs\v4\, commit locally, no push, at most 3 parallel subagents). Keep progress in
docs\v4\HERMES-ROUND2-PROGRESS.md and write CARD COMPLETE as its last line when done.

Close every OPEN item in docs\v4\REVIEW-backend-ideas.md (head review). Specifically:
1. Share keys: add POST /api/drive/share with body {task_id} returning {share_key, path} where path is /api/drive/<key>; gated by
   the capability matrix (organiser only, new action share_drive). Tests: organiser gets a key that resolves; host/volunteer/viewer
   get 403; unknown task_id 404.
2. Share summary consistency: when /api/roster runs, store an in-memory snapshot {title, district, block, slot, roles with counts
   and required skills and safety_critical, ready, computed_at ISO time} for that task id (only for known task ids) and have
   GET /api/drive/{key} serve the snapshot; without a snapshot serve the synthetic task with ready null and computed_at null.
   Add computed_at to DriveShareSummary. Test that edited roles in the roster request appear in the public summary.
3. share.py task_id_for_share_key: remove the unused `secret = server_secret()` line.
4. Capabilities: gate POST /api/roster, /api/roster/why-not and /api/roster/dropout with action read_roster (organiser only), and
   document in docs\v4\BACKEND-PATTERNS.md that an unknown role is 403 via header on mutating routes but 422 via query on
   GET /api/capabilities.
5. docs\v4\BACKEND-REQUESTS.md (written by the front-end agent) asks for localized display text (lang=en|hi). Implement the
   smallest honest version: a `lang` query/body parameter on GET /api/tasks and POST /api/roster that adds a `display` object with
   Hindi for task title, role names, skill labels, and the fixed reason/recruit-request templates the solver generates (find them
   in backend\app\solver\). Translate the templates by hand into natural Hindi (not word-by-word); ids, numbers and decisions must
   be identical in both languages. Contract tests prove that. Leave LLM-generated text (card summaries) in its original language
   and say so in BACKEND-PATTERNS.md.
Run the full suite at the end; paste the final line into the progress file. All tests must pass.
