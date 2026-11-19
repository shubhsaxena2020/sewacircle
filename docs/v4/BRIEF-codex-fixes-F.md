# Brief for Codex (gpt-6-sol, one session): implement front-end fix packages F1, F2, F3

Same rules as the earlier front-end briefs in docs\v4\: work INLINE in this one session (no sub-agents), branch `frontend-v2` in
C:\Users\shubh\Projects\sewacircle, commit locally in logical commits, never push, never edit `backend\`, one heavy process at a time,
stop only PIDs you start. A Hermes agent is editing the backend in a separate worktree at the same time; do not touch it.

Read `docs\v4\HARD-REVIEW.md` and `docs\v4\FIX-PLAN.md` (independent hard review). Implement F1, F2 and F3 exactly, meeting every
acceptance check in FIX-PLAN.md. Head decisions:

- F1: split Console.tsx into one component per step (task, roles, crew, evidence, ledger, evaluation) with no line over 160
  characters; keep behaviour. Invalidate roster/comparison/cards on any plan edit; label the four-method comparison "original solve"
  after a dropout. Revision UI (reason input, revision_requested badge, redraft) must be built against the NEW backend contract,
  which is not running yet: put it behind a capability check that hides it when GET /api/capabilities 404s, and cover it with
  mock-mode tests now. Integration with the live new API is a later package (I1).
- F2: mock evaluation = a verbatim frozen copy of docs\eval_report.json summary with a visible "recorded run, seed 7" label and a
  source link. Captures must wait for final counter values. Re-render the explainer with each scene zoomed/cropped to the active
  UI element so text is readable at 1280x720 on a projector; fix the Hindi caption (host, not organiser, confirms cards). Re-capture
  docs\screens\v4 after all UI changes.
- F3 hero craft: redesign the Fusion kit so it explains itself. Re-run design\fusion\SewaCrewKit with a volunteer token that reads as a
  person (an abstract head + shoulders silhouette on the disc, not a face), a standby node that visibly docks to its socket (a small
  linked pin on a short bridge), sockets with a deeper recess and a contrasting rim, and a READY seal with a raised check mark.
  Keep the add-in route that worked (runOnStartup copy, done marker, remove the copy afterwards; the empty folder can stay). Keep
  total GLB < 300 kB. Remove the backing rectangle in the scene. Add a WebGL error boundary + webglcontextlost handler that swaps to
  the still. Re-render the hero loop from the new scene.
- Hindi: fix the logo accessible name to include the visible "SewaCircle"; translate opt-in as interest in this drive, not consent;
  run axe after the Hindi toggle on every route and console step; zero serious/critical.

Verification (paste real output in a new section "Fix round F1-F3" of docs\v4\FRONTEND-REPORT.md): build, lint, vitest, full
Playwright suite including new tests, axe in both languages, Lighthouse for / and /console (mobile + desktop), new screenshots
(look at each), new model previews and video frames.
