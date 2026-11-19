# 03-field-notebook — SewaCircle Ready Crew

## Direction Name
**03-field-notebook** (District Operations Field Notebook)

## The Idea in Three Sentences
SewaCircle Field Notebook presents the district youth volunteering operations platform as a literate, calm, living planning document. Built for district youth organisers across Uttar Pradesh, it replaces bureaucratic administrative software with structured field notes, database-style properties, contextual callout blocks, and interactive checklists. Every operational decision—from AI role extraction to CP-SAT standby redundancy and cryptographic ledger verification—reads as an unhurried, transparent entry in a district organiser's working dossier.

## Palette
All colors are engineered for high readability and strict WCAG AA contrast against warm paper surfaces:
- **Canvas Stock:** `#f7f6f2` (creamy, warm off-white notebook canvas)
- **Document Surface:** `#ffffff` (crisp white sheet layer)
- **Subtle Panels:** `#faf9f6` and `#f2f0ea` (tinted warm stone cards)
- **Hairline Rules:** `#e6e3dc`, `#d9d5cc` (delicate notebook ruled borders)
- **Deep Ink:** `#262422` (primary titles; contrast ratio 15.3:1 against white)
- **Body Ink:** `#3d3a36` (reading copy; contrast ratio 10.8:1 against white)
- **Muted Ink:** `#57524b` (metadata and labels; contrast ratio 6.5:1 against white)
- **Subtle Ink:** `#635f57` (secondary captions; contrast ratio 5.5:1 against white)
- **Semantic Tint Accents:**
  - *Ready / Mint:* Background `#edf7ed`, border `#bce3bf`, text `#165322` (contrast 8.5:1)
  - *Alert / Coral:* Background `#fcf1ef`, border `#f5c4bd`, text `#8f2219` (contrast 7.9:1)
  - *Warning / Amber:* Background `#fdf8e6`, border `#f8df93`, text `#704705` (contrast 7.5:1)
  - *Information / Sky:* Background `#edf5fc`, border `#bfdff7`, text `#104c75` (contrast 7.8:1)
  - *Method / Purple:* Background `#f5f0fc`, border `#dac5f3`, text `#482278` (contrast 8.6:1)

## Typography
- **Headings & Display:** `Lora, Georgia, serif` — dignified, literary, evoking a researcher's or field director's notebook.
- **Body & Controls:** `Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif` — clean, neutral, highly legible sans-serif for comfortable reading.
- **Devanagari Runs:** `Noto Sans Devanagari` — natural Hindi typography rendered with generous `line-height: 1.75` for authentic rendering of conjuncts (`/क्ष/`, `/द्व/`, `/र्/`).
- **Identifiers & Hashes:** `JetBrains Mono, monospace` — tabular numerals for metrics, volunteer IDs, timestamps, and SHA-256 cryptographic hashes.

## Key Interaction Ideas
1. **Document Breadcrumb Hierarchy:** Header displays live folder paths (`📓 Kanpur Dehat / Task-01 Brief`) anchoring the organiser in their geographical and operational context.
2. **Database Property Blocks:** Key metadata (scope, block, slot, headcount, safety baseline) is formatted as clean two-column property blocks inspired by modular document systems.
3. **Living Document Callouts:** Softly tinted block callouts highlight optimal solver results, safety rules, and heuristic flags with distinctive iconography.
4. **Human-in-the-Loop Decision Lists:** Ambiguities detected during AI extraction (e.g. Awadhi vs Bhojpuri dialect, hygiene educator inclusion) are presented as checklists for explicit human decisions before the solver executes.
5. **Standby Redundancy Rail:** Primary crew rows are paired with dedicated standby cards explaining how backups eliminate single points of failure.
6. **Transparent Gap Visualization:** Unfilled slots in the NOT READY state are rendered honestly as dashed red gap slots, accompanied by pre-formatted, one-click WhatsApp mobilization text.
7. **Linked Cryptographic Chain:** Post-drive evidence actions (draft, flag, confirm) are visualized as physical linked blocks with visible hash linkages, copy affordances, and verification receipts.
8. **Cartographic State Schematic:** Original hand-drawn SVG schematic of Uttar Pradesh plotting all 20 districts by approximate coordinates, clearly differentiating the 4 active drive hubs from 16 inactive sample nodes.

## Page List
The implementation includes all 11 required desktop pages at 1440px width:
1. `01-landing.html` — Story page explaining the post-"Interested" operational gap, national platform numbers (PIB July 2026), 6-step workflow, task-01 READY preview, solver benchmark summary, limits, and console CTA.
2. `02-console-task.html` — District drive brief editor with 10 UP drives, verbatim Hindi brief text in Devanagari, sample switchers, extraction metadata, and workflow sidebar.
3. `03-console-roles.html` — AI-proposed roles table with evidence spans, count steppers, safety indicators, verbatim "Needs your decision" checklist, and confirm action.
4. `04-console-crew-ready.html` — READY hero screen for task-01 (Akbarpur), metrics strip, 4 assigned crew cards with scores and reasons, standby safety rail, four-method comparison, why-not tool (Aarav C.), and dropout healer.
5. `05-console-crew-not-ready.html` — NOT READY hero screen for task-02 (Chinhat), 3 of 5 filled slots, 2 dashed gap slots, verbatim recruit request card for Community mobiliser x2, and WhatsApp dispatch preview.
6. `06-console-evidence.html` — Post-drive host notes, attendance register, 4 AI-drafted contribution cards with `round_number_inflation` and `hours_exceed_recorded` flags, and fixed-rule framing.
7. `07-console-ledger.html` — 9 linked SHA-256 blocks (indices 0..8) with visible hash connectors, cryptographic verification badge (`ok, 9 entries, first_bad_index null`), and credential export.
8. `08-console-evaluation.html` — Empirical benchmark matrix comparing CP-SAT, nearest_skill, manual_greedy, and random_feasible across 5 metrics with 95% bootstrap CI bands, plain-language Gini definition, and 7 verbatim misses.
9. `09-volunteer.html` — Volunteer mobile perspective for Heena P. (v-008), Hindi greeting in Devanagari, opted-in task-01 card, 5 host-checked vs 0 self-declared skills comparison, and contribution status.
10. `10-districts.html` — Stylised 20-district Uttar Pradesh cartographic schematic with approximate coordinates, highlighting Kanpur Dehat (READY), Lucknow (NOT READY), Varanasi, and Gorakhpur, with quiet inactive nodes for the other 16 districts.
11. `11-method.html` — Mathematical CP-SAT solver methodology, 3-tier formulation, plain-language metric definitions, computational scaling stats, and honest scientific limits.
