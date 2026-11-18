# R5 — Demo & UX research for SewaCircle

All volumes, rosters, names and host notes shown in the demo are **SYNTHETIC** demo data. No real people and no minors are represented.

## Findings

### F1. What demonstrably wins hackathon demos (re-verified against primaries)

- **FACT — Working prototypes, not slideware, were the format at the OpenAI Academy × NxtWave Buildathon at India AI Impact Summit 2026.** The finale brought finalists "to present working prototypes rather than presentations"; 70,000+ students registered, 90 teams reached the final, and the first-place LUMOS AI wearable was reported as costing about Rs 10,000 with judges noting "practical design and immediate usability, not a prototype waiting for a lab, but a product ready for people." (https://www.indiatoday.in/education-today/news/story/meet-the-winners-of-indias-largest-genai-buildathon-at-india-ai-impact-summit-2026-2870537-2026-02-19, published 2026-02-19). **Re-verification:** the exact URL used in the inherited K2 report was opened again in this pass and those statements are present in the page text. Caveat: this is a reputable news report, not the organiser's own site.
- **FACT — OpenAI's own winner page states the judging axes and builder profile.** "Judges evaluated each project on technical implementation, design and user experience, potential impact, and the quality of the idea." Nearly 47,000 builders from 186 countries submitted 8,000+ projects; eight winners shared $100,000; a veterinarian with no coding background built a triage tool piloted in her clinic and a cardiologist built a cardiac-arrest research prototype between hospital shifts. (https://developers.openai.com/blog/build-week-winners). **Re-verification:** primary page opened in this pass; all quoted lines present.
- **FACT — Anthropic's winner page shows domain experts, not just engineers, winning with working tools.** The Opus 4.6 winners included a personal injury lawyer, a cardiologist, a roads/infrastructure specialist, an electronic musician and one professional software engineer; "four out of five winners were not professional developers". CrossBeam lets builders drag/drop blueprints and correction letters and produces a 20-minute action plan; a city is looking at adopting it. (https://claude.com/resources/articles/meet-the-winners-of-our-built-with-opus-4-6-claude-code-hackathon, published 2026-04-20). **Re-verification:** primary page opened in this pass.
- **FACT — Microsoft states its 2025 AI Agents Hackathon judging criteria and scale.** "over 18,000 developers registered and 570 project submissions"; "Projects were judged on innovation, impact, usability, solution quality, and category alignment". Winners include RiskWise (Best Overall), Apollo, Bit2Brain, WorkWizee and ModelProof. (https://microsoft.github.io/AI_Agents_Hackathon/winners/). **Re-verification:** primary page opened in this pass.
- **FACT — Google's 2024 Solution Challenge winners were presented at a live Demo Day of 10 teams with three top prizes and one People's Choice award.** Indian winners Spoon Share (food surplus map; Flutter/Firebase/Google Maps) and Saheli (SOS alerts and safe navigation) are named on Google's own blog. (https://blog.google/innovation-and-ai/technology/developers-tools/meet-the-students-that-are-changing-the-world-through-technology/, published 2024-07-01). **Re-verification:** primary page opened in this pass.
- **FACT — SIH 2025 official results name real winners and prize amounts.** The official grand-finale result table lists SIH25001, team CORE_401, leader Shubh Sharma, status Winner, prize Rs 1,50,000, institute Acropolis Institute of Technology & Research, Indore. (https://www.sih.gov.in/sih2025/sih2025-grand-finale-result, opened in a real browser in this pass because direct fetch is blocked). **Re-verification:** yes, from the primary official result page. The same page does **not** describe any team's demo style; claims about SIH demo technique remain NOT FOUND.
- **INFERENCE (not a fact from these pages):** across the re-verified set, the reusable pattern is a *running, domain-specific artefact + one concrete number + a named user/workflow*, not a theme label or model choice. Government-flavoured panels (SIH, India Today's MeitY-linked buildathon) reward deployability and clear public-service use; industry/sponsor panels (OpenAI, Anthropic, Microsoft, Google) state design/UX, usability, solution quality and impact among their criteria. This supports putting a real end-to-end roster flow and a measured baseline on screen early.
- **NOT RE-VERIFIED, therefore NOT USED:** the inherited claim that Google's Solution Challenge FAQ scores "Impact 25 pts + Technology 25 pts" (https://developers.google.com/community/dsc-solution-challenge/faq) could not be re-verified — a fetch timed out and the browser was redirected to a generic Google community page. Also not re-verified and not relied on here: UIDAI OPI statistics, VYOMA/PIB winner details, IndiaAI/I4C CyberGuard details and InMobi judging criteria from the inherited reports.

### F2. Organiser-tool UX patterns (complex, domain-specific workflows)

- **FACT — System status is a first-order requirement in complex applications; progress plus steps/time remaining reduce uncertainty and build confidence.** (https://www.nngroup.com/articles/usability-heuristics-complex-applications/; https://www.nngroup.com/articles/visibility-system-status/).
- **FACT — The same source recommends speaking the user's language rather than internal jargon, giving recognition cues instead of relying on recall, giving an "emergency exit"/undo, and deferring rarely used controls via staged disclosure.** (https://www.nngroup.com/articles/usability-heuristics-complex-applications/).
- **FACT — Progressive disclosure explicitly means showing only a few important options initially and offering specialised options on request; NN/G distinguishes it from staged disclosure, which reveals features later in a linear task.** (https://www.nngroup.com/articles/progressive-disclosure/).
- **INFERENCE for an organiser:** the primary screen should be a single "task → roster → confirm → ledger" pipeline with a visible step counter; solver constraints, fairness knobs and ledger internals belong behind progressive disclosure, while "undo approve", "restore roster" and "why?" stay one click away.

### F3. Hindi UI, accessibility and low-literacy cues (primary sources)

- **FACT — WCAG 2.2 is a W3C Recommendation dated 12 December 2024; it extends WCAG 2.1, and conformance to 2.2 also conforms to 2.0 and 2.1.** (https://www.w3.org/TR/WCAG22/).
- **FACT — GIGW 3.0 requires text contrast of at least 4.5:1 (3:1 for large text), text resizable to 200% without loss of content or functionality, and no loss of content at 320 CSS px width / 256 CSS px height reflow.** (https://guidelines.india.gov.in/guidelines/; https://guidelines.india.gov.in/accessibility-guidelines-and-attributes/).
- **FACT — GIGW 3.0 explicitly requires Unicode characters for Hindi/regional-language fonts and testing Hindi/regional fonts in popular browsers for layout loss.** (https://guidelines.india.gov.in/guidelines/).
- **FACT — W3C's Devanagari layout requirements note that danda/double-danda should not wrap to a new line, the double danda should use its dedicated Unicode character, and underlining is not a traditional Devanagari text decoration.** (https://www.w3.org/International/ilreq/devanagari/).
- **FACT — The W3C Internationalization site's own stylesheet sets `font-size: 18px` for `:root[lang=hi] body` versus `16px` for Latin-language body text, with a Devanagari-capable font stack.** (https://www.w3.org/International/style/article-2022.css). This is evidence of W3C's own design choice, **not** a normative minimum font size; no normative Devanagari point-size threshold was found in the sources opened.
- **FACT — WAI's cognitive accessibility patterns advise familiar icons beside key content (one meaning per icon, avoid clutter) and literal, concrete language on headings, labels, instructions and error messages; these are supplemental guidance, not WCAG conformance requirements.** (https://www.w3.org/WAI/WCAG2/supplemental/patterns/o1p07-icons-used/; https://www.w3.org/WAI/WCAG2/supplemental/patterns/o3p04-literal-language/).
- **INFERENCE:** use `lang="hi"`/`lang="en"` per span, Devanagari-capable font stack with ~18px baseline and relative units for zoom, icon + Hindi text + English gloss on primary actions, and short literal error sentences ("Role first aid is uncovered. Add 1 volunteer."). Avoid glyph-based icons whose meaning is not obvious locally; test with actual target users before claiming low-literacy suitability.

### F4. Playwright video recording: commands and flags that actually exist in the docs

- **FACT — Playwright Test video is configured with `use.video`; current docs list modes `off`, `on`, `on-first-retry`, `on-all-retries`, `retain-on-failure`, `retain-on-first-failure`, `retain-on-failure-and-retries`.** (https://playwright.dev/docs/videos; https://playwright.dev/docs/api/class-testoptions).
- **FACT — Video size defaults to the viewport scaled to fit 800x800; with no explicit viewport the size is 800x450. `fps` defaults to 25 and "Higher frame rates and sizes use more CPU for encoding"; Firefox and WebKit currently capture up to 25 fps.** (https://playwright.dev/docs/api/class-testoptions; https://playwright.dev/docs/api/class-browser).
- **FACT — The library API accepts `browser.newContext({ recordVideo: { dir, size, fps } })` and the video is only available after the page or context is closed; `page.video().path()` returns its path.** (https://playwright.dev/docs/api/class-browser; https://playwright.dev/docs/videos).
- **FACT — The current CLI documentation lists `--output <dir>` ("Folder for output artifacts (default: test-results)") and `--workers <workers>`/`-j`, but no `--video` switch; video is set in config/`test.use()`.** (https://playwright.dev/docs/test-cli). Do not put `npx playwright test --video=on` in the README as a verified command.
- **FACT — FFmpeg's libvpx wrapper documents `b` (target bitrate in bits/s), `crf`, `deadline` (`good` recommended as a speed/quality trade-off) and `cpu-used`; the FFmpeg codecs page also shows `-b:v` in a real example command.** (https://ffmpeg.org/ffmpeg-codecs.html).
- **FACT — Arithmetic run locally:** 15 MB in 180 s allows 666667 bit/s (0.667 Mbps); 15 MiB allows 699051 bit/s (0.699 Mbps). Full command and output are in the audit report. **INFERENCE:** target ~550-600 kbps for VP8 to leave muxing/audio headroom, then measure the actual file with `ls -l`; Playwright docs do not state a bitrate guarantee, so a size claim must come from a real measured file.

## Recommendation for our build

### R1. Screen design for the organiser

1. Keep one primary canvas: **Hindi/English task in → extracted roles → roster with reasons → approve → contribution card → ledger**. Show a 5-step progress chip (NN/G visibility of system status).
2. Show extraction as an editable table: role, required skill, level, confidence, source phrase. Unknown/low-confidence rows get a visible "check" chip; never silently drop a role.
3. Show each roster pick with a one-line reason and a "why not X?" button. Constraints (travel, availability, exposure cap) appear as badges on hover/expand, not as a wall of settings (progressive disclosure).
4. Keep **Undo approve**, **Restore previous roster**, and **Export** visible; make the fairness toggle a clearly labelled switch with one-sentence effect text, not a jargon slider.
5. Label every visible record `SYNTHETIC DEMO DATA` in a persistent header/banner.

### R2. Hindi + accessibility implementation checklist

- `<html lang="en">` with `lang="hi"` on Devanagari spans; Unicode Devanagari only; font stack e.g. `"Noto Sans Devanagari", "Devanagari MT", "Arial Unicode MS", sans-serif`; base 18px for Hindi body text with `rem` scaling and no `maximum-scale=1`.
- Verify contrast >= 4.5:1, 200% text zoom, and 320px reflow; test Hindi layout in Chromium and Firefox/WebKit before recording (GIGW).
- Use `word-break: normal` and never split Devanagari syllables; keep `।` attached to preceding text (W3C Devanagari layout).
- Primary buttons: familiar icon + Hindi label + small English gloss; one meaning per icon; short literal error text; no idioms such as "heal the roster" in user-facing copy — use "One volunteer removed. Roles still covered." ("heal" is fine as our internal feature name only).
- Focus ring, keyboard reachability, `aria-live="polite"` for solver status and heal results.

### R3. Improved 3-minute demo script (segments sum to 180 s)

The timing table below is machine-parsed by the proof script in the audit report. Every on-screen value must come from the actual run of our eval harness / app, not from a hardcoded screenshot; all data is synthetic.

| # | Time | Segment | Seconds | On-screen evidence |
|---|------|---------|---------|--------------------|
| 1 | 00:00-00:15 | Hook: today's manual roster vs our baseline | 15 | 10-second manual count-up; label "manual baseline - measured live" |
| 2 | 00:15-00:35 | Hindi task in | 20 | Type/paste a synthetic Hindi task; show raw text + language tag |
| 3 | 00:35-00:55 | Roles extracted | 20 | Schema-validated role/skill table with confidence and source phrase |
| 4 | 00:55-01:25 | CP-SAT roster with reasons | 30 | Solver status, coverage, one reason per pick, roster time from harness |
| 5 | 01:25-01:40 | Fairness toggle | 15 | Toggle exposure cap; show repeat-pick spread before/after |
| 6 | 01:40-02:00 | Drop-a-volunteer heal | 20 | Remove one synthetic volunteer; re-solve; all roles still covered |
| 7 | 02:00-02:15 | Why-not-X counterfactual | 15 | Force X; show which role/volunteer/constraint breaks |
| 8 | 02:15-02:40 | Contribution card + rules + host confirm | 25 | AI draft from synthetic host notes, rule flag, explicit confirm click |
| 9 | 02:40-02:55 | Hash-chain ledger + export | 15 | Append card, show previous/current hash link, download JSON/CSV |
| 10 | 02:55-03:00 | Close: measured outcome + reproducibility | 5 | Coverage/time vs baseline from eval command + "one command to reproduce" |

Delivery notes: record at 960x540 or 1280x720, 25 fps, one worker, no browser UI, and use action annotations only if they do not cover the reason text. Keep each segment to its slot with a visible run sheet off-camera; if a live call is slow, show the precomputed artifact and say so. Rehearse once against the exact 180 s timing before the video run.

### R4. Recording recipe (verified flags only)

```ts
// playwright.config.ts — API verified at https://playwright.dev/docs/api/class-testoptions
import { defineConfig } from '@playwright/test';
export default defineConfig({
  use: {
    viewport: { width: 960, height: 540 },
    video: { mode: 'on', size: { width: 960, height: 540 }, fps: 25 },
  },
});
```

```bash
# flags verified at https://playwright.dev/docs/test-cli
npx playwright test demo.spec.ts --workers=1 --output=test-results
ls -l test-results
```

For the library API (if we script rather than use the runner), use `browser.newContext({ recordVideo: { dir: 'videos/', size: { width: 960, height: 540 }, fps: 25 } })`, then `await context.close()` before reading `await page.video().path()` (https://playwright.dev/docs/api/class-browser; https://playwright.dev/docs/videos).

If the measured WebM exceeds 15 MB, re-encode once (flags documented at https://ffmpeg.org/ffmpeg-codecs.html) and measure again:

```bash
ffmpeg -i test-results/demo.webm -c:v libvpx -b:v 600k -deadline good -cpu-used 2 demo-15mb.webm
ls -l demo-15mb.webm
```

Do **not** claim the re-encode is under the cap until `ls -l` prints a byte count below 15,000,000.

## Risks

- **Re-verification gaps.** Several inherited winner claims could not be opened (Google Solution Challenge scoring FAQ, UIDAI numbers, PIB/VYOMA details, InMobi criteria). None are used above; do not add them back without opening a source.
- **Demo timing drift.** Ten segments leave little slack; the 30 s solver slot and 25 s contribution slot are most at risk. Mitigation: pre-warm the app, precompute all LLM/CP-SAT results, and keep a fallback screenshot sequence with the same timings.
- **Video file size is empirical.** Playwright documents size/fps but no bitrate guarantee; VP8 output depends on motion. Only a measured `ls -l` can support a "under 15 MB" claim.
- **Tooling drift.** Playwright docs are a moving target (new modes/fps options appear); the absent `--video` CLI switch may exist in older/newer releases. Check `npx playwright --help` at build time before relying on any flag.
- **Accessibility claims.** WCAG/GIGW conformance is not proven by following tips; 200% zoom, reflow and Devanagari rendering must be actually tested. No normative Devanagari font-size minimum was found — the 18px figure is W3C's own stylesheet choice.
- **Misreading "fairness" or "heal".** Keep explanations factual: the tool re-optimises under constraints; it does not guarantee social fairness, and a single-dropout heal says nothing about two simultaneous dropouts unless separately tested.
- **Integrity.** All names, tasks, host notes and hashes must be obviously synthetic; no real person, real minor or real credential may appear in screenshots or the ledger.

## Sources

| # | Title | URL | Date |
|---|-------|-----|------|
| 1 | Meet the winners of OpenAI Build Week | https://developers.openai.com/blog/build-week-winners | accessed 2026-11-18 |
| 2 | Meet the winners of India's largest GenAI buildathon at India AI Impact Summit 2026 (India Today) | https://www.indiatoday.in/education-today/news/story/meet-the-winners-of-indias-largest-genai-buildathon-at-india-ai-impact-summit-2026-2870537-2026-02-19 | published 2026-02-19; accessed 2026-11-18 |
| 3 | Meet the winners of our Built with Opus 4.6 Claude Code hackathon (Anthropic) | https://claude.com/resources/articles/meet-the-winners-of-our-built-with-opus-4-6-claude-code-hackathon | published 2026-04-20; accessed 2026-11-18 |
| 4 | Meet the students that are changing the world through technology (Google, Solution Challenge 2024) | https://blog.google/innovation-and-ai/technology/developers-tools/meet-the-students-that-are-changing-the-world-through-technology/ | published 2024-07-01; accessed 2026-11-18 |
| 5 | Winners — AI Agents Hackathon 2025 (Microsoft) | https://microsoft.github.io/AI_Agents_Hackathon/winners/ | accessed 2026-11-18 |
| 6 | SIH 2025 Grand Finale Result (official) | https://www.sih.gov.in/sih2025/sih2025-grand-finale-result | accessed 2026-11-18 |
| 7 | 10 Usability Heuristics Applied to Complex Applications (NN/G) | https://www.nngroup.com/articles/usability-heuristics-complex-applications/ | accessed 2026-11-18 |
| 8 | Visibility of System Status (NN/G) | https://www.nngroup.com/articles/visibility-system-status/ | accessed 2026-11-18 |
| 9 | Progressive Disclosure (NN/G) | https://www.nngroup.com/articles/progressive-disclosure/ | accessed 2026-11-18 |
| 10 | Web Content Accessibility Guidelines (WCAG) 2.2 (W3C Recommendation) | https://www.w3.org/TR/WCAG22/ | 2024-12-12; accessed 2026-11-18 |
| 11 | Guidelines for Indian Government Websites and apps (GIGW 3.0) — Guidelines | https://guidelines.india.gov.in/guidelines/ | accessed 2026-11-18 |
| 12 | GIGW 3.0 — Accessibility: Guidelines and attributes | https://guidelines.india.gov.in/accessibility-guidelines-and-attributes/ | accessed 2026-11-18 |
| 13 | Devanagari Layout Requirements (W3C Internationalization) | https://www.w3.org/International/ilreq/devanagari/ | accessed 2026-11-18 |
| 14 | W3C Internationalization stylesheet article-2022.css | https://www.w3.org/International/style/article-2022.css | accessed 2026-11-18 |
| 15 | Cognitive Accessibility Design Pattern: Use Icons that Help the User (W3C WAI) | https://www.w3.org/WAI/WCAG2/supplemental/patterns/o1p07-icons-used/ | content first published 2021-04-29; pattern posted 2022-01; accessed 2026-11-18 |
| 16 | Cognitive Accessibility Design Pattern: Use Literal Language (W3C WAI) | https://www.w3.org/WAI/WCAG2/supplemental/patterns/o3p04-literal-language/ | content first published 2021-04-29; pattern posted 2022-01; accessed 2026-11-18 |
| 17 | Videos (Playwright docs) | https://playwright.dev/docs/videos | accessed 2026-11-18 |
| 18 | TestOptions (Playwright API) | https://playwright.dev/docs/api/class-testoptions | accessed 2026-11-18 |
| 19 | Browser (Playwright API, newContext recordVideo) | https://playwright.dev/docs/api/class-browser | accessed 2026-11-18 |
| 20 | Command line (Playwright docs) | https://playwright.dev/docs/test-cli | accessed 2026-11-18 |
| 21 | Configuration (use) (Playwright docs) | https://playwright.dev/docs/test-use-options | accessed 2026-11-18 |
| 22 | Page (Playwright API, page.video().path()) | https://playwright.dev/docs/api/class-page | accessed 2026-11-18 |
| 23 | BrowserContext (Playwright API) | https://playwright.dev/docs/api/class-browsercontext | accessed 2026-11-18 |
| 24 | FFmpeg Codecs Documentation (libvpx options) | https://ffmpeg.org/ffmpeg-codecs.html | accessed 2026-11-18 |

Blocked / not usable as sources: https://developers.google.com/community/dsc-solution-challenge/faq (fetch timeout; browser redirect to a generic page), https://www.w3.org/WAI/tutorials/cognitive/ (404), https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html and https://www.w3.org/International/questions/qa-html-language-declarations (browser bot check), https://www.w3.org/WAI/WCAG2/supplemental/patterns/o3p03-familiar-words/ (http error).
