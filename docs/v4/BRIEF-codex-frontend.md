# Brief for Codex (gpt-6-sol, one session): build the complete SewaCircle Ready Crew front end

Claude Code is the head. It will review and verify everything you produce before anything is pushed.

## HARD EXECUTION RULES (owner instructions, non-negotiable)
1. Work INLINE, yourself, in this one session. Do NOT spawn, delegate to or call any sub-agent, worker, parallel agent, task
   tool or other model. If a skill says to dispatch agents, ignore that step and do the work yourself.
2. Work only on git branch `frontend-v2` (already checked out) in `C:\Users\shubh\Projects\sewacircle`. Commit locally in
   small logical commits. Do NOT push, do NOT touch `main`, do NOT rewrite history.
3. Replace the front end in `frontend\`. Do NOT edit `backend\` at all. If the UI genuinely needs a backend change, write
   the exact request (endpoint, schema, why) in `docs\v4\BACKEND-REQUESTS.md` and design the UI so it still works without it.
4. A backend API is ALREADY RUNNING at http://127.0.0.1:8000 (started by Claude Code, LLM record/replay mode). Use it. Do not
   stop or restart it. If you start servers (vite dev/preview on a port other than 8000), stop them by PID when done. Never
   kill processes by image name.
5. Never submit anything anywhere, never post, never deploy. No secrets in code or commits.
6. No polling or sleep loops longer than needed; finish with a final written report (section "Deliverables").

## The product (read these first; they are the source of truth)
- `README.md`, `PROJECT_REPORT.md`, `PRD.md`, `DESIGN.md`, `CONTEXT.md` (run instructions)
- `docs\v3\DA-SYNTHESIS.md` (why "Ready Crew"), `docs\v4\IDEA-ANSWERS-v4.md` (final pitch text)
- `docs\MYBHARAT-COMPARISON.md` (how we complement MY Bharat, with sources), `docs\EVAL_RESULTS.md`,
  `docs\LOCAL_MODEL_RESULTS.md`, `docs\research\up_districts.json` (20 UP districts with coordinates and sources)
- Existing front end to replace: `frontend\src\*` (App.tsx, steps.tsx, api.ts, types.ts, mock.ts, i18n.ts). Keep `api.ts`
  and `types.ts` as the API contract (extend types only to match what the backend really returns; check
  `backend\app\schemas.py` and `backend\app\main.py`, read-only).
- Current screens for reference: `docs\screens\v3\*.png`.

SewaCircle Ready Crew is an organiser-side tool for youth volunteering in Uttar Pradesh, built for the AI Kaushal Hackathon 2026
(use case UC16). One question: "Willing volunteers are here. Can this drive run?" It reads a Hindi/English/Hinglish task brief
into roles (LLM; organiser confirms), builds a crew from youth who opted in with OR-Tools CP-SAT (skills, availability, travel,
guardian consent for 16-17 year olds, a standby for every essential role, fair rotation, newcomer-mentor pairing), and answers
READY or NOT READY plus exact recruit requests. Safety-critical roles (first aid, disaster response, driving) accept only
host-checked skills. After the drive, AI drafts contribution cards from host notes, deterministic rules flag conflicts against
attendance, a host confirms, and a hash-chained ledger records every step. It complements MY Bharat (which handles discovery,
registration, attendance, certificates at national scale): we sit after MY Bharat's "Interested" step. All data is synthetic.

## The owner's verdict on the current UI
"Not even a template, not even AI slop; downgraded." He wants a FINAL, complete, striking front end: rich 3D, shapes, motion,
typography, generated imagery where it helps, every feature visible and usable, nothing half-finished. Quality first.

## What to build (all of it, finished)
1. **Landing / story page** (`/`): a memorable hero with a real-time 3D scene (react-three-fiber) that SHOWS the idea, not
   decoration: e.g. volunteer tokens streaming in and snapping into role slots of a crew, a standby node lighting up behind each
   essential role, a gap pulsing red until a recruit fills it, then the whole crew turning READY. Headline from the pitch. Then
   sections: the gap (MY Bharat "Interested" list -> a complete, safe crew; cite the sources from docs\MYBHARAT-COMPARISON.md),
   how it works (4 stages, animated), the safety rules, measured results (pull the evaluation LIVE from `GET /api/eval`; any
   other number must be one listed in "Allowed numbers" below, shown with its source link), responsible-AI principles, limits
   stated honestly, FAQ, footer with the disclaimer. Clear CTAs into the live console and the volunteer view.
2. **Organiser console** (`/console`), the full working flow on the real API, redesigned from scratch:
   task (pick a site/drive, edit the brief, sample briefs in Hindi, English and Hinglish), roles (AI draft with source phrase,
   confidence, unresolved roles clearly marked, edit/add/remove, "needs your decision" list), crew (the READY/NOT READY verdict
   as the hero of the screen; recruit requests with copy button; crew board grouped by role with standby; reasons per pick;
   all four methods side by side - SewaCircle CP-SAT vs nearest-skill vs careful organiser (manual_greedy) vs random - from
   `/api/roster`; planner option toggles; fairness and safety panel; animated drop-out simulation via `/api/roster/dropout`;
   "why not this person?" via `/api/roster/why-not`), evidence (host notes, attendance sheet, draft cards, flags, confirm/correct/
   reject), ledger (visualise the hash chain as linked blocks; verify via `/api/ledger/verify`; credential export), evaluation
   (charts with confidence intervals for ready, coverage, robustness, repeat picks, Gini; the harness's own misses list).
3. **District view**: an original stylised map of the 20 UP districts from `docs\research\up_districts.json` (SVG or 3D; no
   external tile servers, no copied map artwork) showing where the synthetic drives and volunteers are and each drive's readiness
   once computed.
4. **Volunteer view** (`/volunteer`): what a young volunteer sees - pick a synthetic volunteer, see the drives they opted into
   (`opted_in_task_ids`), their skills (checked vs self-declared), why a safety role needs a host check, their confirmed
   contributions. The backend has no opt-in write endpoint: do NOT fake persistence; label any local-only interaction as
   "demo, not saved" or file a backend request.
5. **Method / about page**: how the solver decides, metric definitions (from `backend\app\schemas.py` docstrings), data sources,
   limitations, links to the repo documents.
6. **Everything bilingual**: every visible string in English and Hindi (Devanagari, natural Hindi, not word-by-word), language
   toggle persists. Inter + Noto Sans Devanagari are already installed.
7. **Mock mode** must keep working (`VITE_MOCK` or `?mock`) for offline demos, clearly bannered as mock data.
8. **Projector/demo mode**: larger type and contrast for a hall projector (exists today; keep and improve).

## Design direction
- Original visual identity for SewaCircle. Start from `DESIGN.md` tokens but you may evolve them; make it feel premium and
  confident (think Linear/Stripe-level craft), warm and Indian without clichés. Large expressive type, generous space, real
  hierarchy, purposeful motion (framer-motion / motion), 3D where it explains something, micro-interactions on every control.
- You MAY use the Government of India's UX4G design system guidance (MIT licensed, https://doc.ux4g.gov.in/ ,
  https://www.ux4g.gov.in/skills/Design.md) for accessibility and form patterns. Brand references in
  `C:\Users\shubh\Projects\awesome-design-md\design-md\<brand>\DESIGN.md` may inspire craft.
- DO NOT copy or imitate MY Bharat's site, layout, logo, colours or assets (its Terms of Use forbid derivative works) and do NOT
  use the national emblem, government logos, the tricolour as branding, or anything that makes the prototype look like an
  official government portal. A visible "Synthetic data" badge and "Not affiliated with MY Bharat or any government body"
  notice must stay.
- Imagery: if you have an image-generation tool in this session, generate a small set of ORIGINAL illustrations (stylised,
  e.g. paper-cut / risograph / isometric; no photorealistic people, no real places' landmarks as photos, no text baked into
  images, no logos) and record each prompt in `frontend\src\assets\gen\PROVENANCE.md`. If you do not have one, create original
  SVG / procedural / 3D art instead and say so in the report. No stock photos, no hotlinked images.
- Accessibility: WCAG 2.2 AA contrast, full keyboard use, visible focus, landmarks, aria for live verdicts, `prefers-reduced-
  motion` honoured (3D and animations calm down or stop), WebGL failure falls back to a static illustration.
- Performance: 3D and heavy libraries lazy-loaded (not in the console's critical path); initial JS for the console under
  ~350 kB gzip; 3D scene capped DPR, no layout jank; works on a mid-range laptop and on a 390 px phone.

## Anti-slop and anti-hallucination rules (Claude Code will check every one)
- No lorem ipsum, no placeholder sections, no "coming soon", no dead buttons, no fake links.
- No invented statistics, partners, logos, testimonials, quotes, user counts, awards or "trusted by" rows.
- Every number on screen comes from the live API or from the "Allowed numbers" list with its source link.
- Every claim about MY Bharat must match `docs\MYBHARAT-COMPARISON.md` and carry its source.
- Plain, specific copy. No buzzword soup ("revolutionise", "seamless", "empower" used decoratively, "cutting-edge").
- Do not claim field impact, government use, deployment or partnerships.

## Allowed numbers (besides live API data), with sources
- 2.22+ crore youth registered, 1.52+ lakh volunteer opportunities on MY Bharat (PIB backgrounder, 05 July 2026:
  https://static.pib.gov.in/WriteReadData/specificdocs/documents/2026/jul/doc202675911701.pdf)
- Ready on 7/10 synthetic drives vs nearest-skill 1/10; ties careful organiser 7/10; repeat-pick share -0.20 vs careful
  organiser (docs\EVAL_RESULTS.md; prefer reading the live `/api/eval`)
- CP-SAT 80/80 instances optimal up to 500 volunteers, max 0.327 s (PROJECT_REPORT.md section 3)
- Qwen2.5-7B 4-bit on one T4 GPU: role recall 0.932 on 30 synthetic briefs; Claude Sonnet 5.5: 1.00 (docs\LOCAL_MODEL_RESULTS.md)

## Research (do it; your session has web search enabled if available)
Before designing, research current best practice and real examples (cite URLs in the report): award-winning civic / nonprofit /
volunteer product sites, react-three-fiber hero patterns and performance, data-dense dashboard design, Hindi typography on the
web, accessible animation. Use library docs for exact current APIs (three, @react-three/fiber, @react-three/drei, motion,
react-router). Pin exact versions in package.json.

## Testing and verification (required; paste real command output in the report)
- `npm run build` (tsc + vite) clean; `npm run lint` clean.
- Unit/component tests with Vitest + Testing Library for the verdict panel, recruit requests, i18n completeness (every key has
  en and hi), number formatting.
- End-to-end with Playwright against the running backend (127.0.0.1:8000, served via vite preview or the backend's static mount
  after build): landing -> console -> extract roles (uses the cached Hindi brief) -> build crew -> READY verdict -> drop out a
  volunteer -> why-not -> draft cards -> host confirms -> ledger verifies -> evaluation renders -> Hindi toggle -> volunteer view
  -> district view. Also a mock-mode run. Also axe-core accessibility checks on every page (zero serious/critical violations).
- Screenshots of every page at 1440x900 and 390x844 into `docs\screens\v4\` (overwrite), and look at them yourself; fix what
  looks wrong (overlaps, cut text, empty states, broken Devanagari).
- Note bundle sizes from the build output.
- The backend tests must still pass: from `backend\` run `..\.venv\Scripts\python.exe -m pytest -q` (you changed nothing there).

## Deliverables
- The finished front end on branch `frontend-v2`, committed locally.
- `docs\v4\FRONTEND-REPORT.md`: what you built (page by page), design decisions, research with URLs, libraries and versions,
  every test command with its real output, bundle sizes, screenshots list, known gaps (be honest), and any backend requests.
- `frontend\src\assets\gen\PROVENANCE.md` if you generated images.
