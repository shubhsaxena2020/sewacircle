# Overnight plan (2026-11-19, owner asleep ~3 h). Head: Claude Code (plan, brief, monitor, review only).

| # | Stage | Delegate | Gate to pass before next stage |
|---|---|---|---|
| 1 | Finish front end v2 (Playwright fix, lazy 3D, report) | Codex sol, frontend-v2 | build+lint+vitest+Playwright green; report exists; head review |
| 1b | Backend patterns: card revision state machine, share keys, capability menu | Hermes res-s2, backend-ideas worktree | 692+ tests green; head review |
| 1c | Geo tree endpoint with ETag | Antigravity, backend-ideas worktree | tests green; head review |
| 2 | Fusion 360 3D kit + motion system + Remotion loop/explainer + libraries | Codex sol, frontend-v2 (BRIEF-codex-3d-motion.md) | assets < 300 kB, suite green, Lighthouse, screenshots |
| 3 | Hard review of everything (frontend-v2 + backend-ideas) | Codex sol, review-only session, devils-advocate code prompt | findings list |
| 4 | Fix review findings | Codex (frontend) / Hermes (backend) | head re-verifies each fix |
| 5 | Merge backend-ideas -> main, frontend-v2 -> main; wire UI to new endpoints; rebuild submission pack + demo video | Codex | full suites, live end-to-end, pack < 20 MB |

Constraints: ~6-7 GB free RAM -> one heavy process at a time; Codex runs sequential. After Effects not installed (Remotion instead).
Fusion trial ends 2026-11-25. No MY Bharat code/assets/brand; dossier used only for generic patterns. Owner submits the form.
