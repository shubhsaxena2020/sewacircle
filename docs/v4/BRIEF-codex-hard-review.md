# Brief for Codex (gpt-6-sol, one session): HARD REVIEW of SewaCircle before merge - review only, no fixes

Claude Code is the head. You are the hard reviewer. The owner asked for "hard reviewing": be adversarial, specific and honest.

## HARD RULES
1. Work INLINE in this one session. No sub-agents, workers or other models.
2. REVIEW ONLY. Do not edit, stage, commit or delete anything except your two output files listed below. Do not push.
3. Read-only commands, builds and tests are fine. RAM is tight: one heavy process at a time. Stop by PID any server you start.
4. The backend API at http://127.0.0.1:8000 is running; do not stop it.

## What to review
- Front end: branch `frontend-v2` (checked out at C:\Users\shubh\Projects\sewacircle; diff vs `main`: `git diff main..frontend-v2`).
  Read docs\v4\BRIEF-codex-frontend.md, BRIEF-codex-frontend-finish.md, BRIEF-codex-3d-motion.md (what was asked) and
  docs\v4\FRONTEND-REPORT.md (what was claimed).
- Backend: branch `backend-ideas` in worktree C:\Users\shubh\Projects\sewacircle-backend (diff vs `main`). Read
  docs\v4\BACKEND-PATTERNS.md and docs\v4\REVIEW-backend-ideas.md (the head's review; note what is still open).
- Integration: the two branches will be merged into `main`. Check the front end against the backend's NEW contract
  (capabilities + X-Demo-Role, /api/drive/share and /api/drive/{key}, card request_revision + revision_requested state, geo tree,
  lang=hi display objects). List every place the UI must change after the merge, and every place the merge can conflict.

Use the `prompts/devils-advocate-code.md` method (Author vs Reviewer, forced disagreement, concrete diffs) and the
`devils-advocate` skill (steel-man, pre-mortem, inversion) from your skills folder.

## Dimensions (cover every one)
1. Correctness bugs (front and back), including edge cases, race conditions, state after dropout/revision, i18n gaps.
2. Architecture and system design: module boundaries, API contract, state management in the UI, coupling, dead code, duplication.
3. Code quality: readability (very long single-line JSX was observed in Console.tsx), naming, types, error handling.
4. Security/privacy for a public demo: secrets, PII in the UI or video, share-key design, demo-role honesty.
5. Accessibility and Hindi quality: run axe yourself; read every Hindi string for naturalness and meaning.
6. Performance: CrewScene chunk is 1,168.6 kB (323.6 kB gzip) - is lazy loading really airtight? Lighthouse claims.
7. Honesty: every number on screen and in the video against docs\EVAL_RESULTS.md, live /api/eval, and the allowed-numbers list;
   every MY Bharat claim against docs\MYBHARAT-COMPARISON.md; no MY Bharat lookalike, no government marks.
8. Visual and product quality, judged as an AI Kaushal hackathon judge would: look at every screenshot in docs\screens\v4 and the
   frames in docs\video\previews. Head's notes to verify and extend: the Fusion parts are simple cylinders and the token does not
   read as a person; a flat rectangle shows behind the hero ring in docs\screens\v4\models\hero-ready.png; crew-ring sockets are
   hard to see; in the explainer the app screenshot is small and unreadable on a projector.
9. Tests: what is untested that matters; are any tests weak or tautological.

## Output (write ONLY these two files)
- `docs\v4\HARD-REVIEW.md`: verdict (Ship / Ship with changes / Rethink), then findings ranked by severity
  (blocker / major / minor), each with file:line, evidence (command output or quote), why it matters, and the exact fix.
- `docs\v4\FIX-PLAN.md`: the fixes grouped into work packages sized for one agent each, marked FRONT (Codex) or BACK (Hermes),
  with acceptance checks. Include the post-merge UI integration work as its own package.
