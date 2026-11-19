# Brief for Codex (gpt-6-luna, one session): frontend v3 ROUND 3 - paper fidelity polish

Same rules as docs\v5\BRIEF-codex-frontend-v3.md and BRIEF-codex-v3-round2.md: inline only, no sub-agents, worktree
C:\Users\shubh\Projects\sewacircle-v3, branch frontend-v3, commit locally, never push, never edit backend\, one heavy process at a
time, stop only PIDs you start (never by image name), no oryzo/Lusion assets, every number from the live API. The backend at
http://127.0.0.1:8000 and the Vite dev server on port 5180 are already running - do not stop them (use your own port for preview).

Rounds 1-2 (c12f192) are functionally complete and verified (Lighthouse story 97 / console 100, axe 0). Do not regress any of it.
This round has ONE goal: the live village must look like the owner's film, not like stylised low-poly.

## Reference
Frames from the film: design\scrolly\media\video\c1-LAST-FRAME.png ... c5-LAST-FRAME.png and frames you extract yourself from
sewacircle-film-web.mp4 (ffmpeg, into a gitignored temp folder). Put 3 film frames next to 3 current screenshots and write down,
in the report, the concrete differences before you start.

## Must fix (in priority order)
1. Organic cut edges. Every silhouette (houses, roofs, trees, fields, river, hills, figures, ring) gets slightly irregular,
   hand-cut outlines: jitter the 2D path points with a seeded noise before extrusion, rounded corners, no perfect boxes/cylinders.
2. Visible paper. Stronger paper fibre: use paper.jpg as both colour multiply and a subtle normal/bump map, small per-object
   hue/value variation, a thin lighter "cut edge" on the extrusion sides (side material differs from face material).
3. Layering and depth. Stacked paper layers with visible gaps and soft contact shadows between them (PCF soft shadows tuned,
   shadow bias fixed, no acne/peter-panning); gentle tilt-shift depth of field on wide shots only if it keeps performance >= 90.
4. Prop detail matching the film: terracotta tiled roofs with tile rows, the hand pump with handle and spout, the wooden notice
   board with posts and pinned paper notices, mustard field rows with small flower dots (instanced), trees as layered paper
   canopies, paper river with lighter ripple strips, faceless figures with head, body and simple scarf/dupatta layers.
5. Light. Warm low sun, soft sky gradient, no grey haze; dusk/night window glow and lanterns stay.

## Budget and performance
- Keep the 3D code split from /console. Instancing for repeated items. Try to bring the scene chunk under 900 KB minified.
- Story Lighthouse performance >= 90 desktop (it is 97 now). Re-run Lighthouse / and /console.

## Keep and re-verify
Everything from rounds 1-2: all live interactions (plan, dropout, share, revision, role switch, districts, volunteer, mock,
Hindi), film transitions, intro poster, counters 70/10/23/40, reduced-motion and no-WebGL fallbacks. Run build, lint, vitest,
npm run verify:v3, axe en+hi.

## Report
Append "Round 3" to docs\v5\FRONTEND-V3-REPORT.md: the film-vs-current difference list, before/after screenshots of every
chapter in docs\screens\v5\round3\{before,after}\, a side-by-side film-frame vs live-frame comparison image, the commands with
their real outputs, and honest remaining gaps. Look at every screenshot yourself. Commit in logical commits.
