# 07-ops-whiteboard • SewaCircle Ready Crew

## Direction Concept
A visual, spatial, and tactile operations planning board inspired by collaborative whiteboard systems (Miro), tailored specifically for a district youth organiser in Uttar Pradesh managing volunteer deployments. The entire console is treated as an infinite planning canvas: operational phases are structured into distinct frames, roles and volunteer assignments are tactile cards slotted into designated columns, standbys sit on a dedicated redundancy bench, and unfilled slots appear as honest dashed gap containers. Urgent recruit requests, host reminders, and system boundaries are pinned across the canvas as pastel sticky notes (yellow, teal, coral, orange, purple), paired with a floating tool dock, canvas radar minimap, and interactive zoom controls.

## Palette
- **Canvas & Grid:** `#f5f6f9` (tactile board background) with `#e2e5ed` dot-grid texture (`radial-gradient` 24px grid)
- **Frames & Card Surfaces:** `#ffffff` (pure white board frames and slotted cards with soft 4px-16px elevations)
- **Subtle Surface:** `#f8f9fb` (column backgrounds, chip backdrops, and table headers)
- **Ink Typography:** `#1c1c1e` (primary dark ink), `#050038` (deep display titles), `#3c414d` (secondary body text), `#555a6a` (muted labels and metadata)
- **Brand Canary Yellow:** `#ffd02f` (SewaCircle logo mark, top promo tag, highlighted action buttons, and classic yellow sticky notes)
- **Tactile Sticky Note Pastels:**
  - **Yellow Sticky:** `#fff9c4` (border: `#f6e05e`, ink: `#2d3748`)
  - **Teal Sticky:** `#ccfbf1` (border: `#99f6e4`, ink: `#0f766e`)
  - **Coral Sticky:** `#ffe4e6` (border: `#fecdd3`, ink: `#9f1239`)
  - **Blue Sticky:** `#e0f2fe` (border: `#bae6fd`, ink: `#0369a1`)
  - **Orange Sticky:** `#ffedd5` (border: `#fed7aa`, ink: `#9a3412`)
  - **Purple Sticky:** `#f3e8ff` (border: `#e9d5ff`, ink: `#6b21a8`)
- **Status Semantics (WCAG AA Compliant):**
  - **Ready / Verified:** `#047857` text on `#e6f8f1` background with `#6ee7b7` border (> 5:1 contrast)
  - **Not Ready / Action Needed:** `#be123c` text on `#ffe4e6` background with `#fda4af` border (> 6:1 contrast)
  - **Standby Reserve:** `#92400e` text on `#fffbeb` background with `#fde68a` border
  - **Safety Role:** `#991b1b` text on `#fef2f2` background with `#fecaca` border

## Typography
- **Primary Sans:** `Plus Jakarta Sans`, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif (clean, geometric sans with slightly rounded friendly shapes matching Miro's Roobert aesthetic)
- **Monospace:** `JetBrains Mono`, SFMono-Regular, Menlo, Monaco, Consolas, monospace (used for role slots, volunteer IDs, solver timings, coordinates, and SHA-256 block hashes)
- **Devanagari:** `Noto Sans Devanagari` (line-height ≥ 1.75 for fluid, natural Hindi across the landing hero, raw WhatsApp brief text, evidence quotes, and volunteer mobile greeting)

## Key Interaction Ideas
- **Framed Spatial Canvas:** Each page is arranged as spatial frames (`FRAME 01 // ...`, `FRAME 02 // ...`) with label chips, floating shadows, and tactile card slots that evoke a physical workshop board.
- **Floating Canvas Chrome:** Persistent left-hand utility toolbar (Select, Pan, Sticky Note, Frame, Connector Line, Comment) and a bottom-right Canvas Radar minimap preview with interactive zoom chip (`- 100% +`).
- **Tactile Slot Architecture & Standby Bench:** Primary volunteers are slotted into framed role columns with fit scores, distance indicators, and qualifications; standby reserves sit directly underneath or on the Standby Bench with visual coverage callouts.
- **Honest Dashed Gap Slots:** When a drive is NOT READY (task-02), missing volunteers are not hidden behind tables; they are drawn as high-visibility dashed red slot containers (`[EMPTY SLOT: Community Mobiliser #1]`), accompanied by pinned recruit sticky notes with plain-text WhatsApp share buttons.
- **Sticky Note Annotations:** Complex constraints, legal checks, PIB backgrounder citations, and why-not explanations are displayed as taped pastel sticky notes pinned with author tags ("District Operating Protocol", "Solver Engine", "Host Authority").
- **Interactive Discrepancy & Conflict Resolution:** Post-drive evidence displays field notes side-by-side with physical attendance registers, distinguishing informational flags (`round_number_inflation`) from actionable discrepancies (`hours_exceed_recorded`), with immediate one-click host reconciliation.
- **Visually Linked SHA-256 Ledger:** The tamper-evident audit trail renders each state transition as a numbered board block connected with directional link arrows, displaying truncated previous and entry hashes with instant verification.

## Page Roster (All 11 Desktop Pages at 1440px)
1. [`01-landing.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/07-ops-whiteboard/src/01-landing.html): Story canvas framing the gap after Interested, PIB national scale statistics (2.22+ crore youth, 1.52+ lakh opportunities), 6-step whiteboard workflow, live task-01 verdict preview, CP-SAT benchmark matrix with 95% CIs, and honest limits sticky notes.
2. [`02-console-task.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/07-ops-whiteboard/src/02-console-task.html): Left drive selector rail (10 tasks in sample), brief ingestion canvas displaying the verbatim Hindi brief for task-01 in Devanagari, sample buttons, site metadata row, extraction parameters, and right-rail pipeline sticky notes.
3. [`03-console-roles.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/07-ops-whiteboard/src/03-console-roles.html): AI-proposed roles board with Devanagari evidence quotes, confidence badges, slot steppers, safety-critical flags, and the verbatim 4-item "Needs Your Decision" sticky note board.
4. [`04-console-crew-ready.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/07-ops-whiteboard/src/04-console-crew-ready.html): Hero green READY verdict, 6-metric solver strip, 4 assigned role slot cards with scores and pick justifications, standby redundancy bench (Imran B. & Kavya L.), why-not Aarav C. sticky note, drop-out simulation tool, and four-method comparison table on task-01.
5. [`05-console-crew-not-ready.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/07-ops-whiteboard/src/05-console-crew-not-ready.html): Hero coral NOT READY verdict for task-02 (Blood donation camp, Chinhat), 4 filled slots, 2 dashed empty slot gap boxes, exact recruit request sticky note with WhatsApp text preview, and verbatim solver diagnostics.
6. [`06-console-evidence.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/07-ops-whiteboard/src/06-console-evidence.html): Verbatim field host notes sticky notes, physical attendance register table, 4 draft contribution cards with evidence hashes, informational round-number inflation flags, and the Kabir Z. 8h vs 5h conflict reconciliation card.
7. [`07-console-ledger.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/07-ops-whiteboard/src/07-console-ledger.html): 9 cryptographically linked blocks (index 0 to 8) with downward connectors, actor badges (system vs host), truncated hashes, `first_bad_index: null` verification status, and JSON credential export affordance.
8. [`08-console-evaluation.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/07-ops-whiteboard/src/08-console-evaluation.html): Statewide solver evaluation board featuring the four methods with 95% bootstrap confidence interval bands, 3 headline comparison cards, plain-language Gini definition, all 7 documented misses, and small monospace `generated_by` footer.
9. [`09-volunteer.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/07-ops-whiteboard/src/09-volunteer.html): Mobile volunteer viewport mockup inside the desktop canvas for Heena P. (v-008, age 27, Sarvankheda), natural Hindi greeting in Devanagari, opted-in drive details, draft contribution status, standby protection note, and 5 host-checked vs 0 self-declared skills comparison table.
10. [`10-districts.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/07-ops-whiteboard/src/10-districts.html): Original SVG schematic map plotting all 20 Uttar Pradesh districts from approximate WGS84 coordinates, highlighted pins with non-overlapping label badges for the 4 active drive hubs, 16 quiet sample nodes, and district details panel.
11. [`11-method.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/07-ops-whiteboard/src/11-method.html): Comprehensive whiteboard specification of the 3-tier constraint pipeline, CP-SAT optimization objectives, plain-language metric definitions, external data sources and scalability benchmarks, and honest system boundary sticky notes.
