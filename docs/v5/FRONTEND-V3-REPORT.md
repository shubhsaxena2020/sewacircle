# SewaCircle Frontend v3 report

**Branch:** `frontend-v3`
**Verification date:** 2026-11-19
**Scope:** frontend only. No backend files were changed.

## What was built

The front end is a paper-craft village story and organiser console driven by the running API at `http://127.0.0.1:8000`. Its own banner says **Synthetic data** and **Not affiliated with MY Bharat or any government body.** Video is labelled illustrative and is used only as art direction / transition footage, never as an application data source.

### Story `/`

One persistent, lazy-loaded React Three Fiber canvas renders an original procedural village: paper homes, fields, a river, trees, people, notice board and floating crew ring. The scene loads its paper texture and local HDR and follows scroll progress. GSAP ScrollTrigger scrubs copy motion and tracks chapter progress; Lenis smooths scrolling. The navigation rail links to Intro, Brief, Crew, Verdict, Evidence, Numbers and Try it. Interest, bench, dropout and district beats are additional story sections; the “Many villages” storyboard chapter is split into map and evaluation sections, so the page has 11 capture anchors while representing all 10 storyboard beats.

| Storyboard beat | Implementation |
|---|---|
| Intro | Owner-provided c1 cross-fades into the live scene; English/Hindi hero, illustrative label, watermark retained. |
| Interest | API opt-in volunteers, hover tags, and PIB figures with the required `PIB backgrounder, 05 July 2026` source line. |
| The brief | Live task brief and role extraction; selecting a highlighted source phrase reveals its proposed role and confidence. |
| Crew | Calls `POST /api/roster`; assignments, reasons, standby, and READY/NOT READY are live API data. |
| Bench | Displays actual standby coverage and the safety/host-check explanation. |
| Verdict | Shows the real roster verdict and exact recruit requests; public share action calls the API. |
| Dropout | Calls live roster and dropout endpoints and prints the returned verdict/request. |
| Drive and evidence | Synthetic example card, host review explanation and route into the working evidence console. |
| Many villages | Illustrative UP map plus live geo tree and drive-status markers; a separate scroll beat counts live evaluation values. |
| Try it | Links to organiser console and volunteer view, with the synthetic-data and non-affiliation disclosure. |

The API’s default task does **not** seat Heena P. in its first roster. The story therefore drops a currently seated volunteer: the real API heals with standby and returns **NOT READY — 1 Logistics and supplies**. The next real dropout action can then drop Heena after she has been promoted. This preserves the actual API sequence instead of claiming Heena’s first dropout produces that earlier NOT READY response.

### Console and supporting routes

- `/console`: Hindi/English/Hinglish sample briefs; extraction with source phrase, confidence, unresolved state and editable roles; four planner methods, roster reasons, standby, why-not, dropout and recruit requests; real share creation; evidence drafting, flags, confirmation, correction, rejection, revision request with reason and batch re-draft; ledger verification and credential export; evaluation charts and misses.
- `/drive/:key`: public summary, role counts, verdict timestamp and stale-plan notice from the real API.
- `/volunteer`: API-backed volunteer-facing view.
- `/districts`: read-only API geography and drive status over a labelled illustrative map.
- `/method`: plain-language pipeline, metric definitions, source and limitations.
- The global role selector fetches `/api/capabilities` and sets `X-Demo-Role`. Its UI clearly says **simulation, not authentication**. The real viewer role’s restricted API requests show the API’s 403 response.
- Language choice and projector mode persist in local storage. The console does not import the 3D story chunk.

## Design and source notes

The referenced [Oryzo site](https://oryzo.ai/) was consulted only for interaction patterns such as pinned scroll chapters, scale shifts, transition inserts, progress navigation and large type. The product identity, world, copy, geometry, typography and media are original SewaCircle assets; no Oryzo/Lusion site assets or code were used. The official [GSAP ScrollTrigger documentation](https://gsap.com/docs/v3/Plugins/ScrollTrigger/) informed the scrubbed chapter setup. The two MY Bharat figures use the [PIB backgrounder dated 05 July 2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2281200&lang=1&reg=3). English uses self-hosted Space Grotesk / Inter; Hindi uses self-hosted Noto Sans Devanagari.

### 3D provenance and size

The live scene is procedural Three.js geometry and does not load a GLB. It does not use Autodesk Fusion exports. Existing v2 SewaCrewKit GLBs were left unused and are identified in [`frontend/public/models/PROVENANCE.md`](../../frontend/public/models/PROVENANCE.md). The scene’s built JS chunk is 1,136.27 KB minified / 343.28 KB gzip; `paper.jpg` is 139,802 bytes and `studio.hdr` is 8,239 bytes. Together the downloaded scene code, texture and environment are about 1.31 MB uncompressed (1.25 MiB), or about 0.50 MB with the JS chunk gzipped, below the 1.5 MB requested scene budget. The map is a separate districts-page asset. The procedural scene, local HDR source and unused GLBs are documented in the provenance file.

The map is explicitly illustrative and not a geographic-boundary claim. The HDR is a local inherited v2 studio environment, not a generated village photograph. No model or asset from the Oryzo/Lusion site is in the runtime.

### Media pipeline

The image source folder’s [`PROVENANCE.md`](../../design/scrolly/media/images/PROVENANCE.md) records that the files arrived from an earlier Codex image-generation run and that exact prompts were lost when concurrent sessions overwrote the generation log. This session used the reviewed files already present; it does not claim to have generated those images. The map source was converted from PNG to WebP for the page. The exact prompts could not be recovered from the source log.

The owner-provided c1 clip is encoded as `intro.mp4` (349,205 bytes) and `intro.webm` (690,612 bytes); its Gemini watermark remains. The c2–c5 owner clips are scaled to 960×540 and re-encoded H.264 with their watermarks intact. Their web sizes are c2 1,046,928 bytes; c3 1,355,877; c4 650,328; c5 1,245,970. Poster frames are 32–59 KB. Chapter slots c6–c9 look for their matching files and show the live village/poster when absent; c6–c9 clips were not present at verification. Each insert says “Illustrative.” Details are in [`frontend/public/media/PROVENANCE.md`](../../frontend/public/media/PROVENANCE.md).

## Libraries and licences

Versions are exact package pins in `frontend/package.json` and the lockfile. Licences below were checked against installed package metadata; links point to upstream licence/source pages.

| Package | Version | Licence | Use |
|---|---:|---|---|
| React / React DOM | 19.3.1 | MIT | UI |
| Three.js | 0.187.0 | MIT ([upstream](https://github.com/mrdoob/three.js/blob/dev/LICENSE)) | Procedural scene |
| `@react-three/fiber` | 9.8.2 | MIT ([upstream](https://github.com/pmndrs/react-three-fiber/blob/master/LICENSE)) | React renderer for Three.js |
| `@react-three/postprocessing` | 3.2.2 | MIT wrapper; its `postprocessing` engine is Zlib ([engine licence](https://github.com/pmndrs/postprocessing/blob/main/LICENSE.md)) | HDR environment, bloom and SMAA pipeline |
| GSAP | 3.13.0 | GSAP Standard “No Charge” licence ([terms](https://gsap.com/standard-license)); ScrollTrigger is included in the registered package | Scrubbed chapter motion |
| Lenis | 1.3.17 | MIT ([upstream](https://github.com/darkroomengineering/lenis/blob/main/LICENSE)) | Smooth scrolling |
| Motion | 14.14.0 | MIT | Interface transitions |
| React Router | 8.5.2 | MIT | Client routes |
| Recharts | 3.11.0 | MIT | Evaluation charts |
| Lucide React | 1.75.0 | ISC | Icons |
| `@fontsource/inter` | 5.3.0 | SIL OFL 1.1 | Self-hosted body font |
| `@fontsource/space-grotesk` | 5.2.9 | SIL OFL 1.1 | Self-hosted display font |
| `@fontsource/noto-sans-devanagari` | 5.3.0 | SIL OFL 1.1 | Self-hosted Hindi font |
| Vite / React plugin | 8.3.8 / 6.3.0 | MIT | Build and local preview |
| Vitest | 4.1.12 | MIT | Unit tests |
| Playwright | 1.61.1 | Apache-2.0 | Browser verification |
| `@axe-core/playwright` | 4.11.0 | MPL-2.0 | Accessibility scans |
| TypeScript / oxlint | 7.0.2 / 1.94.0 | Apache-2.0 / MIT | Type-checking and lint |

GSAP’s upstream repository points to its current standard licence and documents ScrollTrigger as a GSAP plugin ([licence](https://gsap.com/standard-license), [ScrollTrigger](https://gsap.com/docs/v3/Plugins/ScrollTrigger/)).

## Verification results

Commands were run from `frontend/`. The backend at port 8000 remained running.

```text
> npm run lint
> oxlint
```

```text
> npm test
> vitest run

RUN  v4.1.12
Test Files  1 passed (1)
     Tests  4 passed (4)
Duration  466ms
```

The four unit cases cover API READY/null handling, exact recruit-request copy, English/Hindi key completeness, and locale grouping/Hindi digits.

```text
> npm run build
vite v8.3.8 building client environment for production...
✓ 3074 modules transformed.
VillageScene-DZeiLnY8.js  1,136.27 kB │ gzip: 343.28 kB
(!) Some chunks are larger than 500 kB after minification.
✓ built in 941ms
```

This build warning is retained as a known performance limit. The console remains split from the 3D scene chunk.

`npm audit --audit-level=low` returned `found 0 vulnerabilities`. The installed Vitest pin was advanced from 4.0.14 to 4.1.12 after the audit reported two advisories; the compatible update removed them.

The final full browser run used `BASE_URL=http://127.0.0.1:4176 npm run verify:v3`, Playwright at 1440×900, and the production preview proxying the live API. The captured summary is [`verification-summary.json`](../screens/v5/verification-summary.json). Excerpt from the actual run:

```json
{
  "viewport": "1440x900",
  "e2e": [
    {
      "storyDropout": "Dropout recorded. Standby promoted. Current verdict: NOT READY. 1 Logistics and supplies",
      "apiCalls": ["POST /api/roster", "POST /api/roster/dropout", "POST /api/roster/dropout"]
    },
    {"story": "all 11 anchors captured; Hindi title rendered in Devanagari"},
    {
      "samples": "Hindi and Hinglish text loaded; English selected for extraction",
      "hindiConsoleHeading": "रुचि को टीम के निर्णय में बदलें।",
      "console": "English sample -> live role extraction -> crew planner -> READY/NOT READY view -> real public share",
      "extractedRoleCount": 6,
      "readyText": true,
      "sharePath": "/drive/5LSMDAWESWLD7HFX"
    },
    {
      "evidence": "drafted cards, requested revision with reason, redrafted card, confirmed and corrected records, verified ledger, opened evaluation",
      "draftedCardCount": 5,
      "initialFlagCount": 4
    },
    {
      "roleSwitch": "capabilities loaded for host, volunteer and viewer; viewer volunteer request returned HTTP 403; UI surfaced the error; organiser restored",
      "roleActions": {
        "host": "not authentication · 9 API actions",
        "volunteer": "not authentication · 1 API actions",
        "viewer": "not authentication · 1 API actions"
      },
      "viewerActions": "not authentication · 1 API actions",
      "forbiddenUrl": "http://127.0.0.1:4176/api/volunteers"
    },
    {
      "districts": "loaded 20 read-only map markers; selected Kanpur Dehat",
      "volunteer": "A volunteer’s view"
    },
    {"mock": "fixture task/extraction/planner completed (MOCK · not live); zero API network calls"}
  ],
  "reducedMotion": {"canvas": 0, "video": 0, "still": 1},
  "noWebgl": {"canvas": 0, "still": 1},
  "pageErrors": []
}
```

The run covered all 11 story screenshot anchors, English/Hindi story rendering, Hindi/Hinglish samples, real role extraction and planner, real share link, evidence revision/redraft/confirm/correct, ledger verification, evaluation, organiser/host/volunteer/viewer capability refresh, viewer 403 responses, districts, volunteer route, offline mock, reduced motion and no-WebGL fallback. It captured six routes in each of English and Hindi for axe; there were no serious or critical issues (zero total axe violations).

Desktop Lighthouse 12.8.2 used the production build on Chromium 1248. Full JSON results are saved as [`lighthouse-home.json`](../screens/v5/lighthouse-home.json) and [`lighthouse-console.json`](../screens/v5/lighthouse-console.json).

| Route | Performance | Accessibility | Best practices | SEO | LCP | TBT | CLS |
|---|---:|---:|---:|---:|---:|---:|---:|
| `/` | 78 | 100 | 100 | 83 | 1.0 s | 440 ms | 0.077 |
| `/console` | 100 | 100 | 100 | 82 | 0.8 s | 0 ms | 0.037 |

The story score reflects its 3D scene cost; the large minified scene chunk is visible in the build output. Lighthouse is a desktop lab run, not a field-device or sustained frame-rate test.

Three.js 0.187 emits one development-console deprecation warning because React Three Fiber 9.8.2 creates `THREE.Clock` internally. The app-level HDR and shadow configuration use the current `HDRLoader` and PCF shadow API.

## Screenshots and recording

All PNGs are 1440×900; the names identify route or chapter. They are saved in [`docs/screens/v5/`](../screens/v5/):

```text
page-story.png, page-story-hi.png, story-dropout-not-ready.png
chapter-00-intro.png, chapter-01-interest.png, chapter-02-brief.png,
chapter-03-crew.png, chapter-04-bench.png, chapter-05-verdict.png,
chapter-06-dropout.png, chapter-07-evidence.png, chapter-08-districts.png,
chapter-09-numbers.png, chapter-10-try.png
page-console.png, page-volunteer.png, page-districts.png,
page-method.png, page-share.png
```

`story-scroll.webm` is the 1440×900 slow full-story Playwright recording: 29.00 seconds, 3,684,204 bytes. It was reviewed at multiple points through the scroll; the film transitions into the scene and chapter copy remains legible. `review-chapters.jpg`, `review-pages.jpg`, and `review-video.jpg` are contact sheets used for the visual check.

## Known gaps and limits

- The optional c6–c9 owner clips were absent; their transition slots fall back to the illustrated live village/poster. c1–c5 are present and watermarked.
- There is no new Fusion 360 export or GLB compression step: the shipped scene is procedural three.js geometry. Inherited v2 kit assets remain unused.
- The source image prompts were lost before this session; image provenance records that gap.
- The live village map is labelled illustrative and is not an accurate district boundary map.
- A browser-based Lighthouse run does not establish 60 fps on a mid-range laptop. The scene chunk exceeds Vite’s 500 KB advisory threshold after minification even though gzip is 343.34 KB.
- Demo roles are an interface simulation, not authentication. The running API explicitly returns 403 for viewer-only restricted actions; production identity and authorization remain backend work.
- The final browser run began with `POST /api/demo/reset` as organiser; the API archived `cards.json`, `ledger.jsonl` and `ledger.jsonl.head` synthetic state files before the evidence workflow ran.
- Public share keys are in-memory demo keys and can expire if the backend process restarts; the UI displays freshness/staleness from the API.
- All displayed roster, status and evaluation data is synthetic. No government service is integrated, and the site makes no field-impact claim.

## Round 2 — film-like paper story

This round reshapes the story around the owner's finished film. The procedural Three.js scene now uses extruded, irregular cut-paper forms with the supplied paper texture, warm colors, layered shadows, terracotta roof tiles, a winding paper river, mustard fields, notice board, pump, paper figures and the turmeric ring with sockets. The scroll path rises from the board to the ring, moves into the sockets, crosses to the second village, then ends above the map at night. Warm sun direction/color, sky, windows, lanterns and stars change through the scroll. Chapter copy is a compact paper label with a maximum 30vw width; the scene remains the hero.

The completed film is used as six full-bleed, muted, skippable transitions. Each transition loads the local master lazily near its chapter, seeks within the clip's documented time range, keeps the Gemini watermark, and is labelled illustrative. A film poster is used while the clip initializes. The intro also shows a film frame immediately, so it is not a blank capture. Removed the old absent-c6-c9 fallbacks. Evaluation counters now settle at the API values 70 / 10 / 23 / 40 before screenshot capture.

### Round 2 visual evidence

All chapter images are 1440×900. The `before` and `after` directories contain matching chapter-00 through chapter-10 captures; the `after` directory also contains six film-cut captures and the route screenshots. I reviewed the full chapter set and five sampled frames from the slow scroll recording against the finished film frames. The live scene now has the requested warm paper palette, layers, tiled roofs, river, ring, day cycle and camera progression. It remains a simplified procedural diorama; its prop detail and organic cut shapes do not yet reach the owner's film fidelity.

- Before: [`docs/screens/v5/round2/before/`](../screens/v5/round2/before/)
- After and all six transition cuts: [`docs/screens/v5/round2/after/`](../screens/v5/round2/after/)
- Full-scroll recording: [`story-scroll.webm`](../screens/v5/round2/after/story-scroll.webm), 1440×900, 34.68 seconds, 5,087,971 bytes (`ffprobe`).
- Film reference frames reviewed: [`film-reference/`](../screens/v5/round2/film-reference/)

The owner film masters and six generated poster frames are local in `frontend/public/media/`. Their provenance and the source time ranges are recorded in [`frontend/public/media/PROVENANCE.md`](../../frontend/public/media/PROVENANCE.md). The master files are 7,465,611 bytes (MP4) and 4,891,736 bytes (WebM); poster frames are 51–105 KB each.

### Round 2 verification

PowerShell commands were run from `frontend/` unless noted:

```text
npm run build
vite v8.3.8 building client environment for production...
✓ 3055 modules transformed.
VillageScene-*.js  933.43 kB │ gzip: 247.45 kB
✓ built successfully (Vite retains its >500 kB chunk advisory)

npm run lint
> oxlint
No warnings or errors.

npm test
RUN v4.1.12
Test Files 1 passed (1)
Tests 4 passed (4)

$env:BASE_URL='http://127.0.0.1:4176'; npm run verify:v3
demoReset HTTP 200
evaluationCounters: 70%, 10%, 23%, 40%
story: all 11 anchors captured; Hindi title rendered in Devanagari
filmCuts: all six documented intervals exercised
console: live extraction, planning, readiness and share succeeded
evidence: draft, revision, redraft, confirm, correct, ledger verify and evaluation succeeded
roles: host, volunteer and viewer exercised; viewer restricted request returned HTTP 403
districts: 20 markers loaded; Kanpur Dehat selected
mock: completed with zero API requests
axe: zero violations across 6 routes in English and 6 routes in Hindi
reducedMotion: canvas=0, video=0, still=1
noWebgl: canvas=0, still=1
pageErrors: []

Console chunk check
{"route":"/console","VillageSceneRequests":[]}
```

The complete browser record, including the exact API calls and axe result for each route/language, is [`verification-summary.json`](../screens/v5/round2/after/verification-summary.json). The final desktop Lighthouse 12.8.2 production-preview run produced:

| Route | Performance | Accessibility | Best practices | SEO | LCP | TBT | CLS |
|---|---:|---:|---:|---:|---:|---:|---:|
| `/` | 97 | 100 | 100 | 83 | 1,112 ms | 48 ms | 0.076 |
| `/console` | 100 | 100 | 100 | 82 | 734 ms | 0 ms | 0.037 |

Commands from `frontend/`, run serially against the production preview:

```text
npx --yes lighthouse@12.8.2 http://127.0.0.1:4176/ --preset=desktop --quiet --output=json --output-path=../docs/screens/v5/round2/after/lighthouse-home.json
npx --yes lighthouse@12.8.2 http://127.0.0.1:4176/console --preset=desktop --quiet --output=json --output-path=../docs/screens/v5/round2/after/lighthouse-console.json
```

Full results: [`lighthouse-home.json`](../screens/v5/round2/after/lighthouse-home.json) and [`lighthouse-console.json`](../screens/v5/round2/after/lighthouse-console.json). These are desktop lab scores, not evidence of sustained frame rate on a device.

### Remaining gaps

- The paper forms, people, trees and props are procedural approximations. The scene is substantially warmer and layered, but not film-level authored art; some outlines and forms still read as stylized low-poly geometry.
- The scene chunk fell from 1,136.27 KB to 933.43 KB minified (343.28 KB to 247.45 KB gzip) and is split away from `/console`, but it still triggers Vite's 500 KB advisory and costs more to render than a static scene. No mid-range device frame-rate test was performed.
- The six chapter transitions use time ranges from the same full film master rather than independently encoded clip files. The browser seeks to the relevant interval after lazy load; startup/seek behavior can vary by browser and network.
- Lighthouse is a desktop run. The accessibility scan is automated and does not replace a full keyboard/screen-reader review.
