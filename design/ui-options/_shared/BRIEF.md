SEWACIRCLE UI OPTIONS - SHARED BRIEF (read fully before starting)

The owner will compare 8 complete UI/UX design directions for the SewaCircle Ready Crew website and pick one. You build ONE (or the
ones named in your task) as static, high-fidelity HTML mockups of EVERY page, then capture them as images. The current React site
is only a functional reference: do NOT reuse its look. Design from scratch in your assigned direction.

THE PRODUCT (one paragraph). SewaCircle Ready Crew is a desktop tool for a district youth organiser in Uttar Pradesh. Young people
have already shown interest in a volunteering drive. The organiser pastes the drive brief (Hindi, English or Hinglish), AI proposes
the roles needed (the organiser confirms), a solver builds a crew from the interested youth with a standby for every essential
role, and the tool answers one question: can this drive run? READY, or NOT READY plus exact recruit requests. Safety roles (first
aid, disaster response, driving) only accept host-checked skills. After the drive, AI drafts contribution cards from host notes,
fixed rules flag conflicts with attendance, a host confirms, and a tamper-evident log records every step. It complements MY Bharat
(the national youth platform): it covers the step after a youth clicks Interested. All data is synthetic. Read README.md and
docs/v4/IDEA-ANSWERS-v4.md in C:/Users/shubh/Projects/sewacircle for detail.

REAL CONTENT. Use ONLY the data in C:/Users/shubh/Projects/sewacircle/design/ui-options/_shared/sample-data.json (real API
responses). Use its names, roles, reasons, numbers, verdicts, recruit requests, cards, ledger entries and evaluation values
verbatim. Never invent statistics, partners, logos, testimonials or user counts. The only outside numbers allowed are in its
allowed_external_numbers block, always with the source named.

PAGES (exactly these 11 files in src/, each a complete desktop page at 1440 px wide, sharing one header/nav and footer):
01-landing.html            story page: the gap after Interested, how it works, the verdict, measured results, limits, CTA
02-console-task.html       pick a drive, the brief text (Hindi sample from the data), sample buttons, Extract roles action
03-console-roles.html      AI-proposed roles with source phrase, count, confidence, a needs-your-decision list, edit controls
04-console-crew-ready.html READY verdict as the hero of the screen, crew board by role with standby, reason per pick, the four
                           methods compared, why-not and drop-out tools
05-console-crew-not-ready.html  the not_ready_example: NOT READY, exact recruit requests with a copy/share action
06-console-evidence.html   host notes, attendance, AI-drafted contribution cards with flags, confirm / correct / send back
07-console-ledger.html     the tamper-evident log as linked blocks, verify result, credential export
08-console-evaluation.html evaluation: the four methods with confidence intervals, misses list, plain-language explanation
09-volunteer.html          what a young volunteer sees: drives they chose, checked vs self-declared skills, their contributions
10-districts.html          the 20 UP districts (names from the tasks/volunteers data) and drive readiness; an original stylised
                           map or schematic, no copied map art
11-method.html             how the crew is decided, metric definitions in plain words, data sources, honest limits
Every page must show a small Synthetic data badge and the line Not affiliated with MY Bharat or any government body.
Hindi: include a visible language toggle and render at least the landing hero and one console screen element in natural Hindi
(Noto Sans Devanagari) to prove the type system handles Devanagari well.

TECH. Plain HTML + CSS (one shared styles.css in src/ is fine) and optional small inline JS for nothing essential. Fonts and icons
from Google Fonts or a CDN are fine. Images: original only (CSS/SVG shapes, illustrations you draw in SVG); no stock photos, no
brand logos, no government emblems, no flag colours used as branding, nothing that imitates MY Bharat. You may take inspiration
from the assigned brand design system file, but SewaCircle has its own name and mark; never show the inspiring brand's name or logo.

QUALITY BAR. Each direction must feel like a finished, distinctive product, not a template: real hierarchy, the verdict and the
crew are the visual heroes of the console, plain language for organisers (metrics like Gini only on evaluation/method pages, and
explained), dense data presented calmly, consistent spacing and type scale, accessible contrast (WCAG AA).

CAPTURE. When the 11 pages are done, run:
  python C:/Users/shubh/Projects/sewacircle/design/ui-options/_shared/capture.py <your option folder>
It writes screens/<page>.png. Open and look at every image yourself; fix overlaps, cut text, empty areas, broken Devanagari, then
capture again. Finally write <your option folder>/README.md: direction name, the idea in 3 sentences, palette, type, key
interaction ideas, and the page list. Do not commit; do not touch anything outside your option folder.
