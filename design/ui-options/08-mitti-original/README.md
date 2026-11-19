# SewaCircle Ready Crew — Direction 08: Mitti Original

**Design Concept:** *Indian Craft, Made Modern* (भारतीय शिल्प, आधुनिक तकनीक).  
A tactile, deeply dignified aesthetic inspired by handmade paper (*kora kagaz*), natural vegetable dyes (terracotta, indigo, turmeric), wooden block-print architectural geometries, and Devanagari-forward bilingual typography. Strictly avoids national flag tricolour branding or government imitation, while feeling like a high-precision, trustworthy operational tool for a district youth organiser in Uttar Pradesh.

---

## 1. The Idea (in 3 Sentences)

1. SewaCircle Ready Crew resolves the critical operational chasm that unfolds after enthusiastic young citizens click *Interested* on national volunteering platforms: turning an unorganized pool of willing youth into a role-complete, safe, standby-resilient team for single-day district drives.
2. Rooted in the visual dignity of handcrafted Indian paper, earthen terracotta clay (*mitti*), and deep indigo ink (*neel*), this direction pairs traditional block-print motifs and authentic Devanagari typography with modern Swiss data hierarchy, replacing sterile administrative spreadsheets with warm, authoritative craftsmanship.
3. By harmonizing privacy-preserving open LLM role extraction (with 61,000-name Indian gazetteer masking), deterministic OR-Tools CP-SAT constraint optimization (guaranteeing 100% dropout redundancy), and a tamper-evident audit ledger, district organizers get an unambiguous answer to the only question that matters: *Can this drive safely run?*

---

## 2. Color Palette & Natural Dye Tokens

The palette is strictly derived from traditional Indian artisanal materials (clay, indigo, turmeric, madder, neem) without any tricolour or flag imitation:

* **Surfaces & Canvas (Kora Kagaz / कोरा कागज़):**
  * Canvas Floor: `#F5EFEB` with subtle CSS SVG stippled fiber grain and warm radial gradients.
  * Elevated Card Floor: `#FFFEFA` (Warm cotton rag paper)
  * Secondary Surface: `#FAF6F0` and `#FAF4EB`
  * Inset / Chips: `#EAE0D0`
  * Borders & Hairlines: `#E4D8C6` (Subtle) and `#C8B7A0` (Strong)
* **Terracotta (मिट्टी / गेरुआ):**
  * Primary Terracotta: `#BD4A26` (Hero action buttons, safety badges, priority accents)
  * Terracotta Dark: `#8E3013`
  * Terracotta Wash: `#FDF2EE`, Border: `#ECC6B8`
* **Indigo (नील / स्याही):**
  * Primary Indigo: `#1C3558` (Brand titles, primary navigation, table headers)
  * Indigo Deep: `#0F2038`
  * Indigo Wash: `#EEF3FA`, Border: `#C6D8ED`
* **Turmeric (हल्दी / पीताम्बरी):**
  * Warm Mustard Turmeric: `#C48214` (Needs-decision banners, secondary alerts)
  * Turmeric Wash: `#FCF6E8`, Border: `#F3DCAC`
* **Botanical Status Tokens:**
  * Ready Neem Green: `#236C42` (Background: `#EEF7F1`, Border: `#B5DFCA`)
  * Not Ready Madder Red: `#A6291E` (Background: `#FDF0EE`, Border: `#EBB6B0`)
* **Typography Ink (Kajal & Umber):**
  * Primary Ink: `#221D1A` (Charcoal soot / kajal)
  * Secondary Ink: `#4A403A` (Raw umber)
  * Muted Ink: `#796C63` (Weathered stone)

---

## 3. Typography & Dual-Script Hierarchy

* **Display & Devanagari Title Font:** `Eczar` (Google Fonts by Vaibhav Singh) paired with `Noto Serif Devanagari`. Carved like traditional Indian stone/woodblock chisels, conveying authority and cultural confidence.
* **Indic Functional UI Font:** `Noto Sans Devanagari` (delivering authentic, natural Hindi rendering across task briefs, source phrases, and dialect tags).
* **Latin Body Font:** `Plus Jakarta Sans` (clean geometric humanist sans-serif for dense data legibility).
* **Monospace Data Font:** `JetBrains Mono` (for volunteer IDs, cryptographic SHA-256 hashes, coordinates, and solver runtimes).
* **Bilingual Hierarchy:**
  * Every major section and card leads with a primary Devanagari heading followed by an uppercase English structural subtitle (e.g. `निर्णय: दल तत्पर एवं पूर्णतः तैयार · VERDICT: READY TO RUN`).

---

## 4. Key Interaction Ideas

1. **Clay Plaque Hero Verdict:** Both console states anchor the page with high-impact clay seals and reassurance plaques (`VERDICT: READY TO RUN` in neem green or `NOT READY + RECRUIT REQUEST` in madder red), instantly giving organisers operational certainty.
2. **People-First Role Cards with Exact Solver Reasons:** Crew slots explicitly show volunteer names, ages, blocks, distances (e.g. Heena P. 7.4 km, Mohit Z. 1.7 km), scores, and verbatim CP-SAT justification points.
3. **Standby Redundancy & Live Dropout Healing:** Pre-assigned standbys (Imran B. and Kavya L.) sit behind the primary crew. An interactive simulator demonstrates how dropping Heena P. auto-heals the poster role with standby Imran B. in real time.
4. **Counterfactual "Why-Not Aarav C.?" Tool:** Verbatim solver re-solve showing why Aarav C. (`v-001`) was not chosen over Kabir Z. (`v-011`) due to fit, travel distance, and opportunity rotation.
5. **One-Click Local WhatsApp Recruiter:** When a drive is NOT READY (e.g. Blood donation camp missing 2 community mobilisers), a pre-formatted Hindi WhatsApp broadcast message is generated with a single-click copy button.
6. **Rule-Based Evidence Spot-Check:** Automated heuristics flag round-number inflation (5.0 hours) and attendance discrepancies (Kabir Z. claiming 8 hours vs 5 hours check-in), requiring host resolution before ledger commitment.
7. **Linked Cryptographic Audit Bahi-Khata:** Visual sequence of 9 linked SHA-256 blocks (#00 to #08) illustrating drafts, flags, and host confirmations, complete with W3C Verifiable Credential JSON-LD export.
8. **Original UP Topological Schematic Map:** An original vector schematic of all 20 Uttar Pradesh districts divided into Western, Central Awadh, Purvanchal, and Bundelkhand zones with zero text overlap, cleanly differentiating active sample hubs from the 16 zero-drive districts.

---

## 5. Complete Page Inventory

All 11 desktop pages are implemented as clean, standalone HTML files in `src/` sharing `styles.css`, with full-page screenshots captured at 1440 px in `screens/`:

| Page | File | Screenshot | Purpose & Core Content |
|---|---|---|---|
| **01. Story & Landing** | [`src/01-landing.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/src/01-landing.html) | [`screens/01-landing.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/screens/01-landing.png) | Story page: The gap after *Interested*, 4-stage craft pipeline, hero READY preview, PIB July 2026 numbers, ethical limits, and dual CTAs. |
| **02. Task Brief Input** | [`src/02-console-task.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/src/02-console-task.html) | [`screens/02-console-task.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/screens/02-console-task.png) | Task selector (10 drives), verbatim Hindi brief textarea, sample chips, parameter grid, 61k-name PII scrubbing banner. |
| **03. Proposed Roles** | [`src/03-console-roles.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/src/03-console-roles.html) | [`screens/03-console-roles.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/screens/03-console-roles.png) | 4 extracted roles with Hindi source phrases ("पोस्टर", "प्राथमिक उपचार"), confidence chips, 4-item decision banner, unresolved skill rule. |
| **04. Crew Board (Ready)** | [`src/04-console-crew-ready.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/src/04-console-crew-ready.html) | [`screens/04-console-crew-ready.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/screens/04-console-crew-ready.png) | Hero READY verdict, 4 primary crew cards, 2 standbys, Why-Not Aarav C. tool, drop-out healing test, 4-method comparison table. |
| **05. Crew Board (Not Ready)** | [`src/05-console-crew-not-ready.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/src/05-console-crew-not-ready.html) | [`screens/05-console-crew-not-ready.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/screens/05-console-crew-not-ready.png) | NOT READY verdict for Blood Donation Camp, 2-mobiliser recruit request spotlight with WhatsApp share copy, partial crew. |
| **06. Evidence Review** | [`src/06-console-evidence.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/src/06-console-evidence.html) | [`screens/06-console-evidence.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/screens/06-console-evidence.png) | Raw host notes, attendance log, 4 AI-drafted cards, round-number inflation info flags, Kabir Z. 8hr-vs-5hr conflict resolution. |
| **07. Tamper-Evident Ledger** | [`src/07-console-ledger.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/src/07-console-ledger.html) | [`screens/07-console-ledger.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/screens/07-console-ledger.png) | Cryptographic chain verification banner (9/9 intact), 9 linked SHA-256 blocks (#00 to #08), W3C Verifiable Credential export. |
| **08. Evaluation Harness** | [`src/08-console-evaluation.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/src/08-console-evaluation.html) | [`screens/08-console-evaluation.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/screens/08-console-evaluation.png) | 4 allocation methods with 95% confidence intervals, delta comparisons, 7-item misses transparency list, plain metric definitions. |
| **09. Volunteer Portal** | [`src/09-volunteer.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/src/09-volunteer.html) | [`screens/09-volunteer.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/screens/09-volunteer.png) | Youth portal for Heena P. (`v-008`): 6 host-checked skills vs 2 self-declared skills, opted-in drives, and verified ledger contributions. |
| **10. 20 UP Districts** | [`src/10-districts.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/src/10-districts.html) | [`screens/10-districts.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/screens/10-districts.png) | Original SVG topological schematic network connecting all 20 UP districts, readiness chips, and 4-column card grid. |
| **11. Method & Limits** | [`src/11-method.html`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/src/11-method.html) | [`screens/11-method.png`](file:///C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original/screens/11-method.png) | Mathematical CP-SAT formulation, 4 plain-language metric definitions, external data sources (PIB backgrounder), and honest ethical limits. |

---

## 6. Verification & Quality Checklist

- [x] All 11 files present in `src/` matching exact named structure.
- [x] All data sourced strictly from `_shared/sample-data.json` verbatim (names, reasons, metrics, hash values, misses).
- [x] Mandatory Synthetic data badge and disclaimer on every page (`Not affiliated with MY Bharat or any government body.`).
- [x] Natural Hindi (`Noto Sans Devanagari` and `Eczar`) tested and rendered on landing hero and console elements.
- [x] Playwright capture executed successfully with 0 page errors.
- [x] All screenshots visually inspected and verified with zero text overlap or clipping.
- [x] Contained strictly within `C:/Users/shubh/Projects/sewacircle/design/ui-options/08-mitti-original`. No git commits made.
