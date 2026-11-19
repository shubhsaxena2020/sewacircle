# Brief for Codex (gpt-6-sol, one session): build the SewaCircle front end v3 from scratch - a scroll-driven 3D story + console

Claude Code is the head; it plans, monitors and reviews. The owner wants the website to feel like https://oryzo.ai (by Lusion):
a very long, scroll-driven, 3D, highly interactive story. Quality first. Finish it completely.

## HARD RULES
1. Work INLINE in this one session. No sub-agents, workers, other models or agent-dispatch skills.
2. Worktree C:\Users\shubh\Projects\sewacircle-v3, branch `frontend-v3` (already checked out, based on merged `main`).
   Commit locally in logical commits. Never push. Do not edit `backend\`. If the UI truly needs a backend change, write it in
   docs\v5\BACKEND-REQUESTS.md and make the UI work without it.
3. Build the front end from scratch in `frontend\`: you may delete and replace everything under frontend\src. The previous
   front end lives on branch `frontend-v2` (worktree C:\Users\shubh\Projects\sewacircle) - read it as a functional reference
   only; do not modify that worktree.
4. The merged backend API is running at http://127.0.0.1:8000 (record/replay LLM cache, synthetic data). Do not stop it.
   Stop only PIDs you start. Never kill by image name. RAM is limited (~6-8 GB free): run ONE heavy process at a time
   (vite build, Playwright, Fusion, ffmpeg).
5. Antigravity is generating media into design\scrolly\media\images and design\scrolly\media\video in parallel. Use whatever
   exists when you reach the media step; if a file is missing, build the scene without it and list it under Known gaps.
6. Original work only. Study oryzo.ai for PATTERNS (pinned chapters, camera moving through one physical scene, huge type,
   video inserts, playful interactions, chapter nav and progress rail). Copy nothing from it: no code, models, textures,
   images, copy or layouts. No MY Bharat lookalike, no government emblems, no flag/tricolour branding, no brand logos.
7. Honesty: every number and name comes from the live API or design\scrolly\sample-data.json; MY Bharat numbers only as in
   the storyboard with source "PIB backgrounder, 05 July 2026". Show "Synthetic data" and "Not affiliated with MY Bharat or any
   government body." Video inserts are mood only and must be captioned "Illustrative".

## WHAT TO BUILD
Read `design\scrolly\STORYBOARD.md` (the story, chapter by chapter) and the product docs (README.md, PROJECT_REPORT.md,
docs\v4\BACKEND-PATTERNS.md, docs\v4\IDEA-ANSWERS-v4.md).

A. The story page `/` - implement all 10 chapters of the storyboard as ONE continuous scroll:
   - A single persistent react-three-fiber canvas behind the page with the desk scene and the crew-board hero object; the camera
     path and every object animation are driven by scroll (GSAP ScrollTrigger scrubbing timelines, with Lenis smooth scroll).
   - Pinned chapters with huge bilingual type that animates in and out (Hindi in Noto Sans Devanagari / a fine Devanagari display
     face; English in a strong grotesk or editorial face - research and choose; self-host fonts).
   - The interactive moments from the storyboard: click a highlighted brief phrase to see its role; hover a token for its pick
     reasons; the "Drop Heena P." moment must call the REAL API (/api/roster then /api/roster/dropout) and show the real result,
     including the honest NOT READY after healing.
   - Chapter nav (Intro, Brief, Crew, Verdict, Evidence, Numbers, Try it) + a vertical progress rail + "scroll to continue".
   - Video inserts from design\scrolly\media\video (re-encode with ffmpeg to web-friendly webm+mp4, < 2.5 MB each, poster frames).
   - Live numbers on the Numbers chapter read from GET /api/eval and count up on scroll.
B. 3D assets: model the hero objects in Autodesk Fusion 360 (installed; Python API; unattended run via a temporary
   runOnStartup add-in that writes a done marker and is removed afterwards - see C:\Users\shubh\Projects\sewacircle\design\fusion\
   on branch frontend-v2 and its SewaCrewKit.py, which already has an unfinished redesign: person-silhouette token, docking
   standby pin, deeper sockets, READY seal with a raised check). Finish that redesign, add desk props (paper brief sheet,
   clipboard, chai glass, pen, phone) in Fusion or as clean procedural three.js geometry, export, convert to compressed GLB
   (gltf-transform, meshopt/draco), total 3D payload < 1.5 MB. Use the generated images as textures (desk wood, paper, map).
   Real-time lighting: a local HDR environment, soft shadows (contact or baked), subtle post-processing (bloom on the READY
   seal, SMAA). Record provenance in frontend\public\models\PROVENANCE.md.
C. The organiser console `/console` - rebuilt in the SAME visual language (desktop-first), every feature working against the
   merged API: task + Hindi/English/Hinglish samples, roles (source phrase, confidence, unresolved, edit), crew (verdict hero,
   crew board with standby, reasons, four methods, planner options, why-not, drop-out), NOT READY recruit requests with copy and a
   real share link (POST /api/drive/share -> /drive/<key> public summary page with freshness and stale flag), evidence (draft,
   confirm, correct, request revision with reason, redraft, flags), ledger (linked blocks, verify, credential export),
   evaluation (charts with confidence intervals and the misses list). A clearly labelled demo-role switch (organiser, host,
   volunteer, viewer) driven by GET /api/capabilities and the X-Demo-Role header ("simulation, not authentication").
   Hindi mode uses the backend display objects (lang=hi) where they exist.
D. `/volunteer`, `/districts` (GET /api/geo/tree + GET /api/drive/status, read-only, the ink-map texture as the base),
   `/method` (plain-language method, metric definitions, sources, honest limits).
E. Quality: plain language for organisers; projector mode; Hindi/English toggle that persists; accessible (WCAG AA, keyboard,
   visible focus, prefers-reduced-motion -> no scroll-scrubbed motion, static hero still + normal page; no-WebGL fallback);
   performance (3D and video lazy; the console must not load the 3D chunk; DPR cap; 60 fps target on a mid laptop; no layout
   shift). Pin exact dependency versions; check licences (GSAP is free incl. plugins - cite the licence page).

## VERIFY (paste real output in the report)
- npm run build, npm run lint, vitest (unit tests for verdict, recruit requests, i18n completeness, number formatting).
- Playwright against the live API: the full story scroll (screenshot each chapter at 1440x900 by scrolling to its anchor), the
  live drop-out moment, the console journey end to end incl. share link, revision cycle, role switch (403 handling), Hindi
  toggle, districts, volunteer; a mock/offline run; axe on every page in both languages (0 serious/critical).
- Record a Playwright VIDEO of a slow full scroll of `/` at 1440x900 to docs\screens\v5\story-scroll.webm and look at it.
- Lighthouse desktop for / and /console.
- Screenshots of every page and every chapter in docs\screens\v5\ - look at each and fix what is off.

## DELIVERABLES
Finished front end committed on `frontend-v3`; docs\v5\FRONTEND-V3-REPORT.md (what was built per chapter/page, research with
URLs, libraries + versions + licences, Fusion pipeline, media pipeline and sizes, every test command with real output,
Lighthouse, screenshots and video list, honest known gaps).
