# SewaCircle Ready Crew — Direction 05: Minimal Keynote

**Inspiration System:** `apple/DESIGN.md` (Apple Keynote presentation rhythm, SF Pro Display tight tracking, vast airy whitespace, near-monochrome canvas with a single Action Blue `#0066cc` accent, and product-shot style device framing with ambient soft drop-shadow).

---

## 1. The Idea (in 3 Sentences)

1. SewaCircle Ready Crew bridges the operational void that occurs after an enthusiastic young person registers interest on MY Bharat: turning an unorganized pool of interested youth into a role-complete, safety-checked, and dropout-resilient team for district volunteering drives across Uttar Pradesh.
2. Inspired by Apple's minimalist keynote product presentations, this direction champions "one idea per screen" with massive confident typography, edge-to-edge section cadence, studio-framed console devices resting on ambient shadows, and an ultra-restrained UI chrome where all interactivity is carried by a single Action Blue accent.
3. Combining offline open-weights NLP role extraction (masked with a 61,000-name Indian gazetteer), deterministic OR-Tools CP-SAT constraint optimization with guaranteed standby redundancy, and a tamper-evident SHA-256 audit chain, district organizers can answer the only question that matters with total operational certainty: *Can this drive safely run?*

---

## 2. Color Palette & Surface Tokens

Built strictly from the semantic tokens of Apple's design system:

* **Interactive Brand Accent (Action Blue):**
  * Primary: `#0066cc` (The universal "click me" signal for pill buttons, text links, and focus rings)
  * Primary Focus: `#0071e3`
  * Sky Link on Dark: `#2997ff` (Bright blue for in-copy links on dark keynote tiles)
* **Surfaces & Canvases:**
  * Pure Canvas White: `#ffffff` (Dominant clean gallery floor)
  * Canvas Parchment: `#f5f5f7` (Signature Apple off-white for alternating slides, footers, and sub-navs)
  * Pearl Surface: `#fafafc` (Subtle off-white for nested utility panels)
  * Dark Tile 1: `#161617` (Deep graphite for cinematic architecture slides)
  * Dark Tile 2: `#1d1d1f` (Primary dark tile surface)
  * Dark Tile 3: `#242426` (Hardware frame interior on dark canvases)
  * Pure Black: `#000000` (Global 44px navigation bar background)
* **Ink & Text:**
  * Primary Ink: `#1d1d1f` (High-contrast near-black photographic text)
  * Secondary Ink: `#515154`
  * Muted Ink: `#86868b` (Helper labels, counts, subtitles)
  * Light Ink on Dark: `#a1a1a6` / `#ffffff`
* **Hairlines & Elevation:**
  * Hairline Soft: `#e5e5ea` (1px utility card borders and dividers)
  * Translucent Frosted Glass: `rgba(245, 245, 247, 0.82)` with `backdrop-filter: saturate(180%) blur(20px)`
  * Signature Product Shadow: `0 30px 60px -12px rgba(0, 0, 0, 0.14), 0 4px 16px rgba(0, 0, 0, 0.04)` (The single drop-shadow in the system, reserved for product/console frames)
* **Status Indicators:**
  * Ready Green: `#34c759` (Background: `#e8f8ed`, Border: `#b7ebc5`)
  * Alert Red: `#ff3b30` (Background: `#fff1f0`, Border: `#ffa39e`)
  * Warning Amber: `#ff9500` (Background: `#fffbe6`, Border: `#ffe58f`)

---

## 3. Typography & Spatial System

* **Primary Font Stack:** `-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif`
  * Negative tracking (`-0.02em` to `-0.03em`) on display headlines for the iconic "Apple tight" typographic feel.
  * Weight 600 for headlines, Weight 400 for running body text at 17px with 1.47 line height.
* **Indic & Devanagari Script:** `Noto Sans Devanagari` (delivering authentic, natural Hindi rendering across hero statements, brief messages, and dialect tags).
* **Monospace:** `SF Mono`, `SFMono-Regular`, `ui-monospace`, `Menlo`, `Consolas`, `monospace` (used exclusively for volunteer IDs, coordinates, and cryptographic SHA-256 hashes).
* **Button Grammars:**
  * `.btn-primary`: Full pill capsule (`border-radius: 9999px`) in Action Blue `#0066cc` with white text, micro-scale press state (`scale(0.96)`).
  * `.btn-secondary-pill`: Transparent ghost pill with 1px Action Blue border.
  * `.btn-dark-utility`: Compact dark rect (`border-radius: 8px`) in `#1d1d1f`.
* **Rhythm & Layout:**
  * 1440px locked desktop width with 1200px inner container.
  * 80px to 88px vertical keynote slide padding.
  * Alternating full-bleed slide rhythm: Pure White (`#ffffff`) ↔ Deep Dark (`#161617`) ↔ Parchment (`#f5f5f7`).

---

## 4. Key Interaction Ideas

1. **The Hero Verdict as the Centerpiece:** Every console screen is anchored by an unmistakable, calm status statement (`VERDICT: READY TO RUN` or `VERDICT: NOT READY`) with instant key metrics (Slots Filled, Dropout Robustness, Standby Count, Solve Time).
2. **Product-Shot Studio Framing:** Console views are presented as precision hardware windows on a gallery pedestal, framed by macOS-style window controls, whisper-thin hairlines, and ambient drop-shadow.
3. **Pre-Allocated Standby Redundancy:** Essential roles are backed by pre-arranged standbys with dashed blue boundaries, guaranteeing that single-volunteer dropouts auto-promote without canceling the drive.
4. **Counterfactual "Why Not X?" Inspector:** Verbatim CP-SAT solver explainability that allows organizers to interrogate alternative volunteers (e.g. Aarav C.) with transparent score trade-offs (score 118 vs 98).
5. **Dropout Stress-Test Simulator:** An interactive stress-test proving that sudden drop-out of a volunteer (e.g. Heena P.) auto-heals immediately with standby Imran B. at 100% role coverage.
6. **One-Click WhatsApp Broadcast Generator:** When a drive is NOT READY (e.g. Chinhat Blood Donation Camp missing 2 community mobilisers), the system translates the solver deficit into a copy-ready WhatsApp/SMS call-out.
7. **Rule-Based Post-Drive Reconciliation:** Raw host field notes and check-in logs are cross-checked with deterministic rules that spot-check round-number inflation and flag attendance discrepancies (Kabir Z. 8h vs 5h) before cards are sealed.
8. **Linked 9-Block SHA-256 Audit Log:** Visual stream of cryptographic blocks (#0 through #8) proving chain continuity alongside a W3C Verifiable Credential export in JSON-LD.
9. **Original UP Topological Schematic Map:** An original vector circuit network connecting all 20 Uttar Pradesh districts across Western UP, Central Awadh, and Eastern Purvanchal without copied map art.

---

## 5. Complete Page Inventory

All 11 desktop pages are implemented as clean, standalone HTML files in `src/`, with full-page screenshots captured at 1440 px wide in `screens/`:

| Page | File | Screenshot | Purpose & Core Content |
|---|---|---|---|
| **01. Story & Landing** | [`src/01-landing.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/src/01-landing.html) | [`screens/01-landing.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/screens/01-landing.png) | Story page: The gap after *Interested*, 3-step workflow, hero READY preview, PIB July 2026 numbers, limits, and dual CTAs. |
| **02. Task Setup & Brief** | [`src/02-console-task.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/src/02-console-task.html) | [`screens/02-console-task.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/screens/02-console-task.png) | Drive picker (10 drives), verbatim Hindi brief textarea in Noto Devanagari, parameters grid, 61k-name PII scrubbing banner. |
| **03. Role Extraction** | [`src/03-console-roles.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/src/03-console-roles.html) | [`screens/03-console-roles.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/screens/03-console-roles.png) | 4 extracted roles with Hindi source phrases ("पोस्टर", "प्राथमिक उपचार"), confidence chips, 4-item decision banner, solver specs. |
| **04. Crew Board (Ready)** | [`src/04-console-crew-ready.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/src/04-console-crew-ready.html) | [`screens/04-console-crew-ready.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/screens/04-console-crew-ready.png) | Hero READY verdict, 4 primary crew cards with avatars, 2 standbys, "Why Not Aarav C.?", dropout healing test, 4-method table. |
| **05. Crew Board (Not Ready)** | [`src/05-console-crew-not-ready.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/src/05-console-crew-not-ready.html) | [`screens/05-console-crew-not-ready.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/screens/05-console-crew-not-ready.png) | NOT READY verdict for Blood Donation Camp, 2-mobiliser recruit request spotlight with WhatsApp share copy, partial crew. |
| **06. Evidence Review** | [`src/06-console-evidence.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/src/06-console-evidence.html) | [`screens/06-console-evidence.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/screens/06-console-evidence.png) | Host notes, attendance log, 4 AI-drafted cards, round-number inflation info flags, Kabir Z. 8hr-vs-5hr conflict resolution. |
| **07. Tamper-Evident Ledger** | [`src/07-console-ledger.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/src/07-console-ledger.html) | [`screens/07-console-ledger.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/screens/07-console-ledger.png) | Cryptographic chain verification banner (9/9 intact), 9 linked SHA-256 blocks (#0 to #8), W3C Verifiable Credential export. |
| **08. Evaluation Harness** | [`src/08-console-evaluation.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/src/08-console-evaluation.html) | [`screens/08-console-evaluation.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/screens/08-console-evaluation.png) | 4 allocation methods with 95% confidence intervals, delta comparisons, 7-item misses transparency list, plain metric definitions. |
| **09. Volunteer Portal** | [`src/09-volunteer.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/src/09-volunteer.html) | [`screens/09-volunteer.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/screens/09-volunteer.png) | Youth portal for Heena P. (`v-008`): 6 host-checked skills vs 2 self-declared skills, opted-in drives, and verified ledger contributions. |
| **10. 20 UP Districts** | [`src/10-districts.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/src/10-districts.html) | [`screens/10-districts.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/screens/10-districts.png) | Original SVG schematic network of Uttar Pradesh connecting all 20 districts, readiness chips, and 4-column card grid. |
| **11. Method & Limits** | [`src/11-method.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/src/11-method.html) | [`screens/11-method.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote/screens/11-method.png) | Mathematical CP-SAT formulation, 4 metric definitions, external data sources (PIB backgrounder), and honest ethical limits. |

---

## 6. Verification & Compliance Checklist

- [x] All 11 files present in `src/` matching exact named structure.
- [x] All data sourced strictly from `_shared/sample-data.json` verbatim (names, reasons, metrics, hash values, misses).
- [x] Mandatory Synthetic data badge and disclaimer on every page (`Not affiliated with MY Bharat or any government body.`).
- [x] Natural Hindi (`Noto Sans Devanagari`) tested and rendered on landing hero and console elements.
- [x] Playwright capture executed successfully with 0 page errors.
- [x] All screenshots visually inspected and verified for zero visual defects, overlaps, or truncation.
- [x] Contained strictly within `C:/Users/shubh/Projects/sewacircle/design/ui-options/05-minimal-keynote`. No git commits made.
