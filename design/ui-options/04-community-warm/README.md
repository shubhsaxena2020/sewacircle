# SewaCircle Ready Crew — Direction 04: Community Warm

**Inspiration System:** `airbnb/DESIGN.md` (Airbnb Cereal typographic rhythm, warm Rausch coral accent `#FF385C`, rounded cards, pastel initial-avatars, and generous whitespace).

---

## 1. The Idea (in 3 Sentences)

1. SewaCircle Ready Crew addresses the critical operational hurdle that occurs after an enthusiastic young person clicks *Interested* on MY Bharat: turning an unorganized pool of willing youth into a role-complete, safe, and dropout-resilient team for district volunteering drives.
2. Inspired by Airbnb's welcoming, human-first design philosophy, this direction replaces rigid enterprise administrative tables with tactile, rounded cards, distinctive initial-avatars for volunteers, and calm, generous whitespace that feels like a community celebration rather than administrative software.
3. By uniting privacy-preserving open LLM role extraction (with a 61,000-name Indian gazetteer mask), deterministic OR-Tools CP-SAT constraint solving with guaranteed standby redundancy, and a tamper-evident audit ledger, district organizers in Uttar Pradesh can answer the single question that matters: *Can this drive safely run?*

---

## 2. Color Palette & Surface Tokens

The palette is built strictly from the semantic design tokens of the Airbnb design system, anchored on pure white canvas, deep near-black ink, and a single voltage of Rausch coral:

* **Brand Accent (Rausch Coral):**
  * Primary: `#FF385C` (The signature brand voltage for hero CTAs, search orbs, active tabs, and primary badges)
  * Active / Press: `#E00B41`
  * Soft Highlight Tint: `#FFF0F3`
  * Hairline Tint: `#FFD1DA`
* **Surfaces & Canvas:**
  * Canvas Floor: `#FFFFFF` (Pure white floor throughout)
  * Surface Soft: `#F7F7F7` (Sub-navigation bars, parameter grids, filter chips)
  * Surface Subtle: `#FAFAFA` (Card hover states and nested panels)
* **Ink & Typography:**
  * Headline & Display Ink: `#222222` (High-contrast, warm near-black)
  * Body Text: `#484848` (Editorial running text)
  * Muted Microcopy: `#717171` (Timestamps, counts, helper labels)
  * Borders & Hairlines: `#EBEBEB` (Hairline soft) and `#DDDDDD` (Border strong)
* **Operational Status Tokens:**
  * Ready Green: `#008A05` (Background: `#EBF9F1`, Border: `#B6ECC9`)
  * Not Ready Alert Coral: `#C13515` (Background: `#FFF2EF`, Border: `#FFD8D0`)
  * Warning Amber: `#B25E00` (Background: `#FFF8EB`, Border: `#FFE6B0`)
  * Informational Blue: `#0E65C9` (Background: `#EEF5FC`)
* **Community Volunteer Avatars (Pastel Palette):**
  * `HP` Heena P. (Coral): `#FFE4E8` / `#D92648`
  * `MZ` Mohit Z. (Mint): `#D8F3E5` / `#0A7D42`
  * `DH` Divya H. (Amber): `#FEF0D4` / `#965800`
  * `KZ` Kabir Z. (Lavender): `#EDE4F9` / `#6236A3`
  * `IB` Imran B. (Sky): `#D9EDF8` / `#1B6C9E`
  * `KL` Kavya L. (Peach): `#FFE8D9` / `#A44C16`
  * `UY` Uday Y. (Teal): `#D3F4F1` / `#0F736E`
  * `RZ` Ruchi Z. (Rose): `#FDDCE5` / `#A22554`
  * `SP` Sahil P. (Indigo): `#E3E6FB` / `#3D4CA8`
  * `TL` Tanvi L. (Warm Yellow): `#FFF3C4` / `#8A6700`

---

## 3. Typography & Spatial Scale

* **Primary Sans-Serif:** `Plus Jakarta Sans`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`, `sans-serif` (matching Airbnb Cereal VF with humanist geometric curves, generous x-height, and warm open apertures).
* **Indic & Devanagari Script:** `Noto Sans Devanagari` (delivering authentic, natural Hindi rendering across hero displays, drive briefs, and regional dialect tags).
* **Monospace:** `ui-monospace`, `SFMono-Regular`, `Consolas`, `monospace` (for IDs, cryptographic hashes, and solver constraints).
* **Type Hierarchy:**
  * Hero Display XL: 38px / 800 (Hindi headline), 26px / 700 (English subtitle)
  * Page Title: 32px / 700 (Letter-spacing: -0.6px)
  * Section Headers: 20px / 700
  * Body Text: 16px / 400 (Line-height: 1.5–1.6)
  * Small Meta: 13px–14px / 500
  * Badges & Tags: 11px–12px / 700 (Border-radius: 9999px)
* **Radii & Soft Geometry:**
  * Pill Elements & Search Bars: `border-radius: 9999px`
  * Standard Cards: `border-radius: 16px` to `20px`
  * Small Badges: `border-radius: 8px`
  * Avatars: `border-radius: 50%`

---

## 4. Key Interaction Ideas

1. **The Hero Verdict Banner:** Every console state is anchored by a high-impact, reassuring status banner (`VERDICT: READY TO RUN` or `NOT READY — RECRUIT REQUEST GENERATED`) that immediately provides organizers with operational certainty.
2. **People-First Crew Slots:** Roles are represented as inviting community cards pairing volunteer avatars, age, block location, fit scores, and exact solver reasons with clear badges for novices and host-checked qualifications.
3. **Standby Redundancy & Live Dropout Simulation:** Standbys are visually integrated with dashed boundary styling. An interactive drop-out trigger demonstrates how standby volunteers (e.g. Imran B.) auto-promote to heal the roster in real time.
4. **Counterfactual "Why Not X?" Explorer:** Organizers can audit alternative candidates (e.g. Aarav C.) with verbatim solver explanations showing the exact trade-offs in fit, distance, and fairness.
5. **One-Click WhatsApp Broadcast Generator:** When a drive is NOT READY (e.g., Blood donation camp missing 2 community mobilisers), the system translates the solver gap into a copy-ready WhatsApp/SMS message to dispatch to local youth networks.
6. **Rule-Based Evidence Review:** Automated deterministic heuristics flag round-number inflation and discrepancies between claimed hours and check-in logs before cards are committed.
7. **Linked Cryptographic Audit Chain:** Visual sequence of SHA-256 blocks (#0 to #8) illustrating how drafts, flags, corrections, and confirmations build a tamper-evident record, alongside W3C Verifiable Credential export.
8. **Original UP Topological Schematic Map:** An original SVG schematic connecting all 20 Uttar Pradesh districts into regional clusters (Central Awadh, Eastern Purvanchal, Western UP, Bundelkhand), visualizing live readiness without copied map art.

---

## 5. Complete Page Inventory

All 11 desktop pages are implemented as clean, standalone HTML files sharing a unified header and footer in `src/`, with full-page screenshots captured at 1440 px in `screens/`:

| Page | File | Screenshot | Purpose & Core Content |
|---|---|---|---|
| **01. Story & Landing** | [`src/01-landing.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/src/01-landing.html) | [`screens/01-landing.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/screens/01-landing.png) | Story page: The gap after *Interested*, 3-step workflow, hero READY preview, PIB July 2026 numbers, limits, and dual CTAs. |
| **02. Task Brief Input** | [`src/02-console-task.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/src/02-console-task.html) | [`screens/02-console-task.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/screens/02-console-task.png) | Drive selector (10 drives), verbatim Hindi brief textarea, sample buttons, parameters grid, 61k-name PII scrubbing banner. |
| **03. Role Extraction** | [`src/03-console-roles.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/src/03-console-roles.html) | [`screens/03-console-roles.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/screens/03-console-roles.png) | 4 extracted roles with Hindi source phrases ("पोस्टर", "प्राथमिक उपचार"), confidence chips, 4-item decision banner, solver specs. |
| **04. Crew Board (Ready)** | [`src/04-console-crew-ready.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/src/04-console-crew-ready.html) | [`screens/04-console-crew-ready.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/screens/04-console-crew-ready.png) | Hero READY verdict, 4 primary crew cards with avatars, 2 standbys, "Why Not Aarav C.?", dropout healing test, 4-method table. |
| **05. Crew Board (Not Ready)** | [`src/05-console-crew-not-ready.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/src/05-console-crew-not-ready.html) | [`screens/05-console-crew-not-ready.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/screens/05-console-crew-not-ready.png) | NOT READY verdict for Blood Donation Camp, 2-mobiliser recruit request spotlight with WhatsApp share copy, partial crew. |
| **06. Evidence Review** | [`src/06-console-evidence.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/src/06-console-evidence.html) | [`screens/06-console-evidence.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/screens/06-console-evidence.png) | Host notes, attendance log, 4 AI-drafted cards, round-number inflation info flags, Kabir Z. 8hr-vs-5hr conflict resolution. |
| **07. Tamper-Evident Ledger** | [`src/07-console-ledger.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/src/07-console-ledger.html) | [`screens/07-console-ledger.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/screens/07-console-ledger.png) | Cryptographic chain verification banner (9/9 intact), 9 linked SHA-256 blocks (#0 to #8), W3C Verifiable Credential export. |
| **08. Evaluation Harness** | [`src/08-console-evaluation.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/src/08-console-evaluation.html) | [`screens/08-console-evaluation.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/screens/08-console-evaluation.png) | 4 allocation methods with 95% confidence intervals, delta comparisons, 7-item misses transparency list, plain metric definitions. |
| **09. Volunteer Portal** | [`src/09-volunteer.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/src/09-volunteer.html) | [`screens/09-volunteer.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/screens/09-volunteer.png) | Youth portal for Heena P. (`v-008`): 6 host-checked skills vs 2 self-declared skills, opted-in drives, and verified ledger contributions. |
| **10. 20 UP Districts** | [`src/10-districts.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/src/10-districts.html) | [`screens/10-districts.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/screens/10-districts.png) | Original SVG schematic network of Uttar Pradesh connecting all 20 districts, readiness chips, and 4-column card grid. |
| **11. Method & Limits** | [`src/11-method.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/src/11-method.html) | [`screens/11-method.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm/screens/11-method.png) | Mathematical CP-SAT formulation, 4 metric definitions, external data sources (PIB backgrounder), and honest ethical limits. |

---

## 6. Verification & Compliance Checklist

- [x] All 11 files present in `src/` matching exact named structure.
- [x] All data sourced strictly from `_shared/sample-data.json` verbatim (names, reasons, metrics, hash values, misses).
- [x] Mandatory Synthetic data badge and disclaimer on every page (`Not affiliated with MY Bharat or any government body.`).
- [x] Natural Hindi (`Noto Sans Devanagari`) tested and rendered on landing hero and console elements.
- [x] Playwright capture executed successfully with 0 page errors.
- [x] All screenshots visually inspected and verified.
- [x] Contained strictly within `C:/Users/shubh/Projects/sewacircle/design/ui-options/04-community-warm`. No git commits made.
