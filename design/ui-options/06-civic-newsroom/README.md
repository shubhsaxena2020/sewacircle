# 06-civic-newsroom • SewaCircle Ready Crew

## Direction Name
**06-civic-newsroom** (Civic Broadsheet & Newsroom Console)

## The Idea in Three Sentences
SewaCircle Civic Newsroom treats volunteer mobilization across Uttar Pradesh as a transparent public broadsheet of civic accountability rather than a black-box administrative dashboard. Built with the visual gravity of classical editorial print—combining monumental condensed headlines, literary serif prose, and disciplined wire-service monospace labels—it anchors operational decisions in verifiable, on-the-record evidence. From bilingual brief extractions and single-dropout invariant rosters to deterministic discrepancy auditing and chained SHA-256 ledgers, every page answers a single question with journalistic honesty: can this drive run?

## Palette
All colors are drawn directly from the broadsheet newsprint design system and engineered for strict WCAG AA contrast against paper surfaces:
- **Paper & Surfaces:**
  - `--paper`: `#f2eee4` (creamy, tactile newsprint broadsheet background canvas)
  - `--paper-2`: `#e9e3d4` (warm, aged newsprint paper for footers, Hindi callouts, and secondary panels)
  - `--paper-3`: `#faf7ef` (clean newsprint sheet surface for card containers, panels, and map frames)
- **Ink Typography & Hairlines:**
  - `--ink`: `#15120e` (dense newsprint black ink for headlines, major borders, and 3px structural rules; 14.8:1 contrast against `#f2eee4`)
  - `--ink-2`: `#3a3429` (dark secondary body ink for reading text, tables, and lead descriptions)
  - `--muted`: `#6b6456` (weathered newsprint ink for captions, secondary metadata, and figure labels)
  - `--rule`: `#cdc5b1` (broadsheet newspaper column divider rule)
  - `--rule-soft`: `#ddd6c5` (delicate inner card divider hairline)
- **Editorial Chromatic Accents:**
  - `--red`: `#b81f19` (editorial newsroom vermilion for section kickers, alert notices, NOT READY verdicts, and angled stamps)
  - `--red-bright`: `#ff8071` (vivid red highlight for active indicator tags)
  - `--red-ink`: `#8d1611` (deep headline red for high-contrast alert callouts)
  - `--red-tint`: `#f3ddd8` (soft red wash for recruit alert headers and flagged discrepancy cards)
  - `--green`: `#14503a` (dense editorial forest green for READY verdicts, cleared stamps, and verified badges; > 7.5:1 contrast)
  - `--green-tint`: `#dde8dd` (soft green tint for confirmed ledger records and positive metric highlights)
  - `--amber`: `#7d5310` (newsroom sepia amber for novice tags, awaiting-decision status, and simulation cards)
  - `--amber-tint`: `#f4e6c4` (warm amber highlight wash)
  - `--blue`: `#1d3f73` (deep editorial navy blue)

## Typography
- **Display Headlines:** `Anton, "Arial Narrow", Impact, sans-serif` — heavy, condensed, high-impact wood-type display sans for monumental headlines, mammoth verdict words (`READY` / `NOT READY`), drop caps, and brand headers.
- **Body & Longform:** `Newsreader, Georgia, "Times New Roman", serif` — optical-sized, literary editorial serif with italic cuts for lede paragraphs, story narratives, pullquotes, and editorial decks.
- **Labels, Wire & Monospace:** `IBM Plex Mono, "SFMono-Regular", Consolas, monospace` — newsroom wire-service monospace with generous letter-spacing (0.12em–0.18em) for kickers, stepbars, timestamps, tabular numbers, task IDs, coordinates, and SHA-256 cryptographic hashes.
- **UI Chrome & Tables:** `Archivo, "Helvetica Neue", Helvetica, Arial, sans-serif` — neutral, mechanical grotesque sans-serif for table data, button controls, input panels, and card metadata.
- **Devanagari Typography:**
  - `Noto Sans Devanagari` (unclipped, natural Hindi runs with generous `line-height: 1.7` for raw drive briefs, Hindi editions, evidence spans, and volunteer greetings)
  - `Noto Serif Devanagari` (high-contrast, editorial headline serif for monumental Hindi displays like `रुचि के बाद का कदम।`)

## Key Interaction Ideas
1. **Broadsheet Masthead & Running Wire:** Persistent editorial header featuring a synthetic data indicator badge, language switcher (`EN` / `हिंदी`), district edition dateline, dual-rule masthead branding, and running strap (`AI drafts · deterministic code decides · a human confirms`).
2. **Monumental Binary Verdicts with Editorial Stamps:** High-impact, uncluttered front-page statements rendering `READY` (forest green) or `NOT READY` (vermilion red) alongside skewed rubber stamps (`[CLEARED TO RUN]`, `[HOLD THE DRIVE]`) that instantly communicate operational viability.
3. **Transparent Slot Journalism & Honest Dashed Gaps:** In incomplete drives (task-02), missing volunteers are never smoothed over; unfilled positions are rendered as honest dashed gap containers (`[EMPTY SLOT: Community mobiliser · 1]`), accompanied by pre-formatted, one-click copyable WhatsApp recruitment alerts.
4. **The Standby Redundancy Bench:** Dedicated bench rows visibly mapping replacement volunteers (`S1`, `S2`) to primary slots with exact coverage callouts, proving single-point-of-failure invariance without disguising bench gaps.
5. **Auditing Tools ("Why Not?" & "What If?"):** Interactive editorial investigation cards explaining why alternative candidates (e.g. Aarav C.) were ranked lower based on fit, travel distance, and 90-day exposure fairness, paired with a real-time dropout simulator testing automatic slot healing.
6. **Host-in-the-Loop Discrepancy Auditing:** Side-by-side presentation of verbatim field host notes and physical attendance registers, explicitly separating benign informational flags (`round_number_inflation`) from operational warnings (`hours_exceed_recorded`).
7. **Chained SHA-256 Ledger:** An auditable chronological block stream connecting 9 state transitions (draft, flag, confirm) with downward link connectors, payload hashes, and JSON credential export affordances, explicitly noting that a hash chain proves edits rather than ground truth.
8. **Cartographic District Locator Plot:** An original geometric SVG schematic plotting all 20 Uttar Pradesh districts by latitude and longitude coordinates on a plotting grid, clearly differentiating 4 active drive hubs from 16 quiet sample nodes without making controversial territorial claims.

## Page Roster (All 11 Desktop Pages at 1440px)
1. [`01-landing.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/06-civic-newsroom/src/01-landing.html) — Story broadsheet exploring the operational gap after "Interested", national PIB scale statistics (2.22+ crore youth, 1.52+ lakh opportunities), 5-step editorial flow, side-by-side READY vs NOT READY front-page spread, CP-SAT benchmark matrix with 95% bootstrap CIs, and plain-language limits.
2. [`02-console-task.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/06-civic-newsroom/src/02-console-task.html) — Brief ingestion console displaying verbatim Hindi text for task-01 in Devanagari, sample switcher (Hindi, Hinglish, English), highlighted span key (graphic_design, first_aid, supplies, dialect), extraction metadata, and drive picker across 10 UP drives.
3. [`03-console-roles.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/06-civic-newsroom/src/03-console-roles.html) — AI-proposed roles table with source phrases, confidence track indicators, count steppers, safety gates, and the four unedited "Needs your decision" open editorial questions.
4. [`04-console-crew-ready.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/06-civic-newsroom/src/04-console-crew-ready.html) — READY hero screen for task-01 (Akbarpur, Kanpur Dehat), 4-row crew board with reasons per pick, standby redundancy bench (Imran B. & Kavya L.), "Why not Aarav C." inspector, single-dropout healing simulator, and four-method comparison table.
5. [`05-console-crew-not-ready.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/06-civic-newsroom/src/05-console-crew-not-ready.html) — NOT READY hero screen for task-02 (Blood donation camp, Chinhat, Lucknow), 6-slot status grid with dashed unfilled recruit boxes, copyable recruit request card for 2 community mobilisers, mentor-pairing notes, and solver diagnostics.
6. [`06-console-evidence.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/06-civic-newsroom/src/06-console-evidence.html) — Post-drive proof console displaying verbatim host notes, physical attendance register, 4 draft contribution cards with evidence hashes, round-number inflation flags, and the Kabir Z. 8h vs 5h discrepancy card.
7. [`07-console-ledger.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/06-civic-newsroom/src/07-console-ledger.html) — 9 cryptographically chained SHA-256 blocks (indices #00 to #08), verification banner (`first_bad_index: null`), chain-at-a-glance sequence, and JSON credential export affordance.
8. [`08-console-evaluation.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/06-civic-newsroom/src/08-console-evaluation.html) — Statewide solver evaluation scoreboard comparing CP-SAT against 3 baselines across 10 tasks, paired bootstrap 95% confidence intervals, plain-language metric definitions, delta comparisons, and 7 printed solver misses.
9. [`09-volunteer.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/06-civic-newsroom/src/09-volunteer.html) — Young volunteer perspective for Heena P. (v-008, age 27, Sarvankheda), chosen task-01 card with pick reasons, draft contribution card with spot-check flag, and 6 host-checked vs 0 self-declared skills breakdown.
10. [`10-districts.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/06-civic-newsroom/src/10-districts.html) — Original SVG locator plot of 20 Uttar Pradesh districts plotted from approximate WGS84 coordinates on a coordinate grid, highlighting the 4 active drive hubs (Kanpur Dehat, Lucknow, Varanasi, Gorakhpur) and 16 inactive sample nodes with numbered legend.
11. [`11-method.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/06-civic-newsroom/src/11-method.html) — Formal CP-SAT mathematical solver methodology, 5 sequential moves, plain-language metric glossaries, cited data sources (PIB July 2026, OR-Tools, Qwen2.5-7B), and 7 honest operational limits.
