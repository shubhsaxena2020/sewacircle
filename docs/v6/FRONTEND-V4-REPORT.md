# Frontend v4 "The Ring": report (19 Nov 2026)

Built from zero by Claude Code (inline, no sub-agents) after a 200-site design study. Branch `frontend-v4`.

## Why a rebuild
The owner judged the v3 site (film-layer village) not good enough. A study of 200 award-winning sites
(`docs/v6/research/DESIGN-STUDY.md`, per-site notes in `NOTES.md`, raw data in `scan-results.json`) showed what v3 lacked:
one idea per screen, type as the main visual (median largest type 112 px; v3 used ~60 px), one hero object carried
through the scroll, and crisp material instead of soft upscaled video frames. Three directions were mocked up
(`research/mockups/*-strip.jpg`); the owner chose **B · The Ring**.

## What was built
- **Story (`/`)**: a dark stage with one real-time three.js brass ring (`src/RingScene.tsx`, react-three-fiber,
  physically based material lit by a procedural RoomEnvironment, bloom + vignette). 12 chapters, each moves the ring to a
  new framing; the ring's seats are the drive's real slots.
  - Interest: the opted-in volunteers of the drive (from `GET /api/volunteers`) are points of light around the ring.
  - Brief: the real Hindi brief; phrases from `POST /api/extract-roles` are tappable and map to role chips.
  - Crew: "Plan the crew" calls `POST /api/roster`; the chosen volunteers' lights fly into their seats and their names,
    roles and host-check badge appear on the ring (projected HTML labels, also listed for screen readers).
  - Bench / Verdict: standby and the live READY · तैयार verdict; "Copy public summary link" calls `POST /api/drive/share`.
  - Gap: a second drive (task-05) is planned live and is honestly NOT READY; seats glow red; the recruit request can be copied.
  - Dropout: `POST /api/roster/dropout`; the standby steps in and the result (NOT READY, single point of failure) is shown.
  - Evidence: `GET /api/ledger/verify`; after a demo reset the log is empty and the page says so instead of claiming
    "intact" or "broken".
  - Numbers: 70% vs 10% ready and 23% repeat picks counted up from `GET /api/eval`; 0.33 s and 93% from the documented runs.
  - Districts: one small ring per drive coloured by `GET /api/drive/status`.
- **Other pages** (console, districts, volunteer, method, share): unchanged logic, re-themed to the same palette.
  The v3 console lost ~75 component styles in the rebuild; they were restored from v2 and recoloured by token
  (`src/console-base.css`, `src/pages.css`).
- **Type and palette**: Inter Tight (variable, 200-800), JetBrains Mono for labels, Tiro Devanagari Hindi; one accent
  (#f2a93b) on #0a0807. Fonts self-hosted via Fontsource (exact versions in package.json).
- **Performance design**: the first screen shows a still rendered from the same scene (`public/media/ring-hero*.webp`,
  18 KB each, made by `scripts/render-hero-still.mjs`); the live WebGL scene mounts on the first pointer, wheel, touch,
  key or scroll event (or after 6 s). The 3D code is a separate chunk the console never loads.
- **Fallbacks**: reduced motion = no smooth scroll and no animation loop (the ring renders as a still frame); no WebGL =
  an SVG ring; phone width = ring centred above the text, no horizontal scroll.
- Removed: the film-layer village, transition films and 22 MB of film media from `public/` (kept in `design/scrolly/media`).

## Verification (real outputs)
- `npm run build`: OK. `npm run lint` (oxlint): 0 warnings, 0 errors. `npx vitest run`: 4/4 passed.
- `BASE_URL=http://127.0.0.1:5181 npm run verify:v4` (`docs/screens/v6/verification-summary.json`):
  - Story: planned live "5/5 · 14 ms", 6 named seats on the ring, verdict "READY · तैयार", gap drive "NOT READY" with a
    recruit request, dropout "Divya H. left the crew … NOT READY 1 × Logistics and supplies — Single point of failure …",
    counters 70% / 23% / 0.33 s / 93%.
  - Console journey, share page, evidence draft/revision/confirm/correct, ledger, role denials (5 expected 403s), mock
    mode, districts and volunteer: as in the v3 script, all passed.
  - axe WCAG 2.1 A/AA: 12 checks (6 pages × English/Hindi), 0 violations.
  - Reduced motion: canvas present, no Lenis. No WebGL: 0 canvases, SVG fallback shown. Phone 390 px: no horizontal
    overflow on story or console. Browser page errors: none.
- Lighthouse 12.8.2 desktop, production build (`docs/screens/v6/lighthouse-*.json`):
  - `/`: performance 100, accessibility 100, best practices 100, SEO 91; TBT 30 ms; CLS 0.
  - `/console`: performance 100, accessibility 100, best practices 100, SEO 91.
- Screenshots: `docs/screens/v6/story-*.png` (12 chapters), `story-contact-sheet.jpg`, `page-*.png`, `phone-*.png`.

## Video model on Kaggle (tested)
Wan 2.2 TI2V-5B on a free Kaggle T4 (4-bit transformer): 2.0 s of 832x480 in 35 min, 1.4 s of 704x384 in 16 min,
11.7 GB peak VRAM; paper look acceptable, people malformed (`research/kaggle-wan-*`). Not a Higgsfield substitute; the
site does not depend on generated video.

## Honest limits
- Lighthouse runs on desktop only; no frame-rate test on a mid-range laptop was performed. The 3D chunk (three.js core
  ~728 KB minified) is loaded only on the story page after the first interaction.
- The live scene renders in software (SwiftShader) in the headless test runs; real GPUs look sharper.
- 0.33 s and 93% are documented results from earlier runs (`docs/EVAL_RESULTS.md`, `docs/LOCAL_MODEL_RESULTS.md`), not
  computed by the page. All data is synthetic; not affiliated with MY Bharat or any government body.

## v4.1 polish (19 Nov 2026, night)

**Library research.** 447 candidate repos from brillout/awesome-react-components, birobirobiro/awesome-shadcn-ui and known
design/animation libraries; GitHub API metadata for each; ranked by stars, relevance, recent activity and licence.
The ranked 200 are in `docs/v6/research/libraries/LIBRARIES-200.md` (169 MIT, 12 Apache-2.0; 99 component kits,
41 motion/scroll, 20 3D/WebGL, 15 overlays, 10 text, 10 charts, 5 icons).
- **Installed (MIT):** `@react-three/drei` 10.7.9 (Environment + Lightformer studio lighting, Sparkles) and
  `maath` 0.10.8 (critically damped camera easing).
- **Patterns adopted and written fresh, no code copied:** word-by-word blur reveal (Motion Primitives `TextEffect`,
  React Bits `SplitText`); magnetic buttons (Motion Primitives `Magnetic`); scroll progress bar; hover cards; chapter
  tooltips. React Bits is MIT + Commons Clause, so nothing was copied from it.

**Ring.**
- A flat, bevelled band (lathe of a rounded-rectangle profile) replaces the plain tube, with 120 engraved bezel ticks,
  an inner hairline and an outer orbit line.
- Seats are recessed sockets with brass rims and glowing pearls. Volunteers fly in and merge into the pearls.
- Studio softbox reflections (drei Lightformers) light the brass, and soft dust particles float in the air.
- The camera eases between per-chapter shots, with a slow breathing motion and pointer parallax (maath).

**Text and hover.**
- Headlines reveal word by word.
- Hovering a name on the ring lights its seat and opens a card with the solver's reasons.
- Hovering a pearl does the same.
- Buttons pull toward the cursor, and chapter dots show their names.

**Robustness found and fixed.**
- Bloom blanked whole frames whenever any pixel was NaN or infinite.
- Three causes were traced:
  - an invalid volunteer-point position after a dropout;
  - zero-scale instance matrices;
  - grazing-angle specular maths.
- Fixes:
  - finite guards on positions;
  - a minimum instance scale;
  - a shader guard that clamps every lit material to finite HDR;
  - a single-pass kernel bloom instead of the mipmap chain.
- Three consecutive full captures show no blank chapter.

**Verification.**
- `npm run build`, `oxlint` (0 warnings) and vitest 4/4 pass.
- `npm run verify:v4` passes: counters 70/23, live READY, gap NOT READY, dropout re-plan, axe 12 checks / 0 violations,
  reduced motion, no WebGL, phone overflow, no page errors.
- The axe check now waits 1.8 s on `/` so it does not score text that is still fading in.
- Lighthouse `/`: performance 100, accessibility 100, best practices 100, TBT 20 ms, CLS 0.
