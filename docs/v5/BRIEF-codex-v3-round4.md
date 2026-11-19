# Brief for Codex (gpt-6-luna, one session): frontend v3 ROUND 4 - film-layer world + live 3D hero objects

Same hard rules as docs\v5\BRIEF-codex-frontend-v3.md and rounds 2-3: inline only, no sub-agents, worktree
C:\Users\shubh\Projects\sewacircle-v3, branch frontend-v3, commit locally, never push, never edit backend\, ONE heavy process at a
time (RAM is limited), stop only PIDs you start (never by image name), no oryzo/Lusion assets, every number from the live API.
The backend on :8000 and Vite dev server on :5180 are running - do not stop them; use your own port for previews.

## Why
Round 3 (7f375e1, Lighthouse 95) is functionally complete, but the head review found the procedural village still reads as plastic
toys: red block roofs, peg figures with bowl-cut heads, flat brown sky, no paper texture, the ring intersecting the notice board.
A fourth pass at modelling everything from code will not reach the owner's film. Change the approach.

## The new approach: 2.5D film layers + real 3D hero objects
1. Backdrops from the owner's film. For each chapter pick a still from design\scrolly\media\video\sewacircle-film-master.mp4
   (or c1..c5.mp4) that matches the chapter (dawn board, youth gather, ring, crew + backups, seal, drive/evidence, map at night).
   Extract at full resolution with ffmpeg.
2. Split each backdrop into 3-4 depth layers (sky, far village, mid square, foreground grass/props) as transparent WebP/AVIF:
   - Use local tools only. rembg 2.0.76 is installed (pip). torch is NOT installed; you may pip-install a CPU depth model
     (e.g. Depth Anything V2 Small via onnxruntime or transformers+torch CPU) if it fits in RAM, OR cut layers with hand-authored
     masks (polygon/colour-key in Python + PIL). Fill the holes behind cut-out layers (simple inpaint: OpenCV Telea, or extend the
     back layer) so parallax never reveals empty gaps.
   - Keep the Gemini watermark visible in at least one layer of every backdrop, and keep the "Illustrative" label.
3. Render the layers in the existing react-three-fiber canvas as planes at different depths (or one depth-displaced plane), with
   scroll-driven camera dolly/parallax and gentle pointer parallax, cross-fading between chapter backdrops (and the full-bleed
   film transitions from round 2 stay). Warm the lighting, colour-match everything to the film; no grey or brown flat sky.
4. Keep as REAL interactive 3D, composited in front of the layers and lit/colour-graded to match: the turmeric crew ring with
   glowing sockets, the seated/standby figures that move (restyle them as flat cut-paper figures like the film: layered paper
   silhouettes, faceless, scarves, NOT peg/capsule toys), the READY seal, the evidence cards and ledger blocks, map pins. They
   must sit plausibly in the backdrop (contact shadow, matching perspective) and never intersect backdrop props.
5. Remove the procedural houses, trees, river, roofs that the backdrops replace (or keep only far-hidden pieces). Drop now-unused code.
6. Bug: a strip of the film poster is visible at the top of the crew chapter (docs\screens\v5\round3\after\chapter-03-crew.png,
   top ~35 px). Fix it.

## Budget
- Total backdrop layers <= 4 MB (WebP/AVIF, 1920 px wide max, lazy per chapter, the first chapter preloaded); the 3D chunk stays
  split from /console. Story Lighthouse performance >= 90 desktop. Reduced motion: static layered stills, no scroll scrub.
  No-WebGL fallback: the chapter stills as plain images.

## Keep and re-verify
Everything from rounds 1-3: live plan, dropout (honest NOT READY), share, revision, role switch (403), districts, volunteer, mock,
Hindi toggle, film transitions, intro poster, counters 70/10/23/40, fallbacks. Run build, lint, vitest, npm run verify:v3, axe en+hi,
Lighthouse / and /console.

## Report
Append "Round 4" to docs\v5\FRONTEND-V3-REPORT.md: method (how layers were cut, tools, sizes), before/after for every chapter in
docs\screens\v5\round4\{before,after}\, a new film-vs-live comparison image (same 3 pairs as round 3), commands with real outputs,
honest gaps. Look at every screenshot yourself; if a chapter still looks like toys or shows layer seams/holes, fix it before you
finish. Commit in logical commits; record backdrop provenance (source film timestamp) in frontend\public\media\PROVENANCE.md.
