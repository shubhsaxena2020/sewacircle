# Brief for Codex (gpt-6-sol, one session): FINISH the SewaCircle front end you started

You started this work in an earlier session (`docs\v4\BRIEF-codex-frontend.md`) and the process crashed with an out-of-memory
error before you committed or reported. Claude Code saved your work as commit `52b948b` on branch `frontend-v2`. All the rules of
the original brief still apply (no sub-agents, no push, no backend edits, no invented numbers, no MY Bharat lookalike, bilingual,
mock mode, accessibility). Read it again first.

## Memory warning (this machine has about 6 GB free)
Run ONE heavy process at a time: never run vite build, vitest and Playwright in parallel. Prefer `npx playwright test --workers=1`
and the installed Chrome channel. Stop any server you start, by PID.

## State Claude Code verified
- `npm run build`: OK. `npx vitest run`: 5/5 pass. `npm run lint`: clean.
- Backend API is running at http://127.0.0.1:8000 (record/replay mode). Do not stop it.
- The Playwright test `live organiser journey and desktop pages` FAILS: `locator.click: Test timeout of 120000ms exceeded`.
- Bundle: `CrewScene` chunk 923.7 kB (244.4 kB gzip). It must be lazy-loaded only on the landing page and never in the
  console's path; confirm with the build output.
- `docs\v4\FRONTEND-REPORT.md` was never written.
- `frontend\test-results\` was committed by mistake; Claude Code removed it from git and added it to .gitignore.

## Tasks, in order
1. Find and fix the root cause of the Playwright timeout (do not just raise timeouts). Run the full suite (live journey, mock
   mode, phone pages, axe) until it passes; paste the real output.
2. Confirm the 3D chunk is not loaded on /console, /volunteer, /districts, /method (check the network or the import graph) and
   that the landing page shows a static fallback when WebGL is missing or `prefers-reduced-motion` is set.
3. Review your own pages against the original brief's "What to build" list. Anything missing or half-done: finish it. Check every
   visible string has natural Hindi. Check every number against the "Allowed numbers" list or the live API.
4. Regenerate all screenshots (`docs\screens\v4\`, 1440x900 and 390x844 for every page); look at each one and fix visual defects.
5. Write `docs\v4\FRONTEND-REPORT.md` exactly as the original brief's "Deliverables" section asks, with real command output and
   honest known gaps.
6. Commit in logical commits on `frontend-v2`. Do not push.
