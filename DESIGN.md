# SewaCircle - DESIGN.md

Design system for the SewaCircle organiser console. Base: **Airtable's** design analysis from our local collection (`awesome-design-md/design-md/airtable/DESIGN.md`): a sober, editorial workflow-software look on a white canvas with near-black ink, hairline borders and colour-block surfaces instead of shadows. We chose it because organisers and judges must trust a data-dense tool at a glance, and calm beats flashy for government-facing software. Status tints are borrowed from Notion's soft card tints. We adapt it for Hindi-first use and for a demo on a projector. SewaCircle is not affiliated with Airtable or Notion.

## 1. Principles
1. **People decide, AI drafts.** Every AI output looks provisional (a "draft" chip) until a person confirms it. Confirmed state looks final.
2. **Show the reason next to the result.** No roster row without a one-line reason. No flag without its rule.
3. **Honest data labelling.** A persistent "Synthetic data" banner is visible on every screen. Never hide it.
4. **Calm density.** Tables over cards where comparing, whitespace between sections, one primary action per viewport.
5. **Hindi is not an afterthought.** Devanagari renders at the same size and weight as Latin, never smaller.

## 2. Colour tokens (CSS variables)
Taken from the Airtable palette; no extra accents are introduced.

| Token | Value | Use |
|---|---|---|
| `--ink` | `#181d26` | Primary text, primary button |
| `--body` | `#333840` | Body text |
| `--muted` | `#41454d` | Secondary text |
| `--hairline` | `#dddddd` | Borders, dividers |
| `--canvas` | `#ffffff` | Page background |
| `--surface-soft` | `#f8fafc` | Table stripes, side panels |
| `--link` / `--info` | `#1b61c9` / `#254fad` | Links, info chips |
| `--success` | `#006400` | Confirmed |
| `--forest` | `#0a2e0e` | Signature surface for "verified and exported" banner |
| `--coral` | `#aa2d00` | Flags, blocked, destructive |
| `--mint` `#a8d8c4`, `--cream` `#f5e9d4`, `--peach` `#fcab79`, `--yellow` `#f4d35e` | | Tint backgrounds for chips and callouts |

Chip tints (Notion-style, softened): confirmed = mint background + forest text; draft = cream + ink; flagged = peach + coral text; pending = yellow tint + ink; info = sky `#dcecfa` + info text. Contrast of every text/background pair must be >= 4.5:1 (verified in QA).

## 3. Typography
- Latin: **Inter** (self-hosted via `@fontsource/inter`), the open substitute for Airtable's Haas Grotesk. Weights 400 body, 500 headings and buttons; never bolder than 600.
- Devanagari: **Noto Sans Devanagari** (self-hosted via `@fontsource`), same weights. Fallback stack: `"Nirmala UI", "Segoe UI", system-ui, sans-serif`.
- Scale: body 14px/1.5, table 14px, label 12px uppercase tracking 0.6px, h3 20px, h2 28px, h1 40px (landing only). On the demo projector mode (`?demo=1`) base size rises to 16px.
- Numerals tabular (`font-variant-numeric: tabular-nums`) in tables and metrics.

## 4. Layout and shape
- 8px spacing grid (4, 8, 12, 16, 24, 32, 48). Page max width 1280px; two-column workspace (roster | evidence panel) above 1024px, single column below.
- Radius: 12px primary buttons and large cards, 10px content cards, 6px inputs, full radius for icon buttons. No pill radius except filter chips.
- Elevation: flat. 1px hairline for inputs, tables and secondary buttons. A focus ring of 2px `--link` on every interactive element.

## 5. Components (what we build)
| Component | Spec |
|---|---|
| `TopBar` | Product name, current task title, **SYNTHETIC DATA** banner chip, language toggle (हिन्दी / English), demo-mode toggle. |
| `BriefInput` | Large textarea, language auto-detected badge, "Extract roles" primary button. Redaction notice ("N personal items hidden before AI"). |
| `RoleTable` | Role, why the AI proposed it (evidence span), need, confidence chip. Rows editable inline. Low-confidence rows highlighted with "needs your decision". |
| `RosterTable` | Role, volunteer, reason, flags (self-declared, novice, minor with consent), distance. Row actions: Why not X?, Swap, Drop out. |
| `CoverageCompare` | Two horizontal bars: SewaCircle vs nearest-skill baseline, with counts ("6 of 6" / "4 of 6"). Values come from the API, never hard-coded. |
| `ResilienceMeter` | Robustness percent with standby list; the "Drop a volunteer" action animates the heal (row swap) and states who covered whom. |
| `FairnessPanel` | Repeat-pick share, exposure Gini, district spread, novice-mentor pairs; each with a one-line plain-language meaning. |
| `WhyNotDrawer` | Counterfactual narrative from the solver with coverage/robustness deltas and who gets displaced. |
| `EvidenceCard` | Draft chip, role, claimed vs recorded hours, evidence refs, flags with rule names; actions Confirm, Correct, Reject. Nothing auto-confirms. |
| `LedgerTimeline` | Append-only list of entries with short hashes and a "Verify chain" button; explanatory text "shows edits, not truth". |
| `CredentialPreview` | JSON preview of the exported credential with a bold "Unsigned, not issued by any authority" label. |
| `EvalPanel` | Table of methods x metrics with 95% CI and a **Misses** list; "Re-run" button; shows the command that reproduces it. |

## 6. Content and tone
- Plain words, short sentences, no jargon in user-facing text. Hindi strings written natively, not machine-translated word for word; reviewed before the demo.
- Buttons are verbs: "Extract roles", "Approve roster", "Confirm hours". One primary (near-black) action per viewport; secondary actions use the white button with hairline.
- Errors say what happened and what to do next. LLM failure: "The AI could not read this. You can type the roles yourself." and the manual path works.
- Never claim verification the system did not do. Never show a metric that is not computed.

## 7. Accessibility
Keyboard reachable everywhere, visible focus, 44px minimum touch targets (48px for primary), labels linked to inputs, status never conveyed by colour alone (icon + text on every chip), `lang` attribute set per element for Hindi/English, respects `prefers-reduced-motion`. Target WCAG 2.2 AA; the QA pass checks contrast and keyboard flow and records results in `docs/QA.md`.

## 8. Motion
Only functional motion: row swap when a roster heals (200ms), bar fill on metric load (300ms), chip colour change on confirm. None when `prefers-reduced-motion`.

## 9. Do and don't
Do keep whitespace calm, one primary action, reasons next to results, synthetic banner always on. Don't add gradients, glows or mesh backgrounds, don't bold display type, don't invent accent colours, don't use pill buttons outside filter chips, don't show unverifiable numbers.
