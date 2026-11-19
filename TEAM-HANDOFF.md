# SewaCircle Ready Crew - team handoff (19 Nov 2026)

**What it is.** An organiser tool for youth volunteering in Uttar Pradesh, for the AI Kaushal Hackathon 2026 (use case UC16).
Young people have already said they are interested in a drive. The tool answers one question: *"Willing volunteers are here.
Can this drive run?"* - **READY**, or **NOT READY** plus exactly who to recruit. It complements MY Bharat (it covers the step
after a youth clicks "Interested"); it is not affiliated with MY Bharat or any government body. **All data is synthetic.**

**Key dates.** Idea form closes **20 Nov 2026** (team lead submits) · shortlist 27 Nov · 24-hour build 8-9 Dec at IIIT Lucknow.

## Where everything is (GitHub: shubhsaxena2020/sewacircle)

| Branch | What is on it | State |
|---|---|---|
| `main` | Everything: backend (FastAPI + OR-Tools CP-SAT solver + LLM layer), the new website (merged from `frontend-v3`), docs, idea answers | **Stable.** 948 backend tests pass; site verified (axe 0, Lighthouse story 100 / console 100) |
| `frontend-v4` | **Current website "The Ring"**: dark 3D brass-ring story rebuilt from zero after a 200-site design study | Merged into `main` on 19 Nov (evening) |
| `frontend-v3` | Previous website (film-layer paper village) | Superseded by v4 |
| `frontend-v2` | Previous website (kept as a template) + the **8 UI design options** in `design/ui-options/` | Reference |
| `backend-ideas` | Backend feature branch | Already merged into `main` |

Most useful files:
- Idea-form answers (final): [`docs/v4/IDEA-ANSWERS-v4.md`](docs/v4/IDEA-ANSWERS-v4.md)
- Measured results: [`docs/EVAL_RESULTS.md`](docs/EVAL_RESULTS.md), [`docs/LOCAL_MODEL_RESULTS.md`](docs/LOCAL_MODEL_RESULTS.md),
  [`PROJECT_REPORT.md`](PROJECT_REPORT.md)
- How we differ from MY Bharat (sourced): [`docs/MYBHARAT-COMPARISON.md`](docs/MYBHARAT-COMPARISON.md)
- Backend features and API: [`docs/v4/BACKEND-PATTERNS.md`](docs/v4/BACKEND-PATTERNS.md); review: [`docs/v4/HARD-REVIEW.md`](docs/v4/HARD-REVIEW.md) (on `frontend-v2`)
- Website report and screenshots: `docs/v6/FRONTEND-V4-REPORT.md`, `docs/screens/v6/`; design study of 200 sites: `docs/v6/research/DESIGN-STUDY.md`
- The 58.8 s paper-craft film: `design/scrolly/media/video/sewacircle-film-web.mp4` (on `frontend-v3`)
- 8 design directions with 11 screens each, plus a side-by-side gallery: `design/ui-options/index.html` (on `frontend-v2`)

## Run it locally (Windows; any OS works with the usual path changes)

```powershell
git clone https://github.com/shubhsaxena2020/sewacircle ; cd sewacircle
python -m venv .venv ; .venv\Scripts\python -m pip install -r backend\requirements.txt
cd backend
$env:SEWA_LLM_MODE="replay"                      # offline: AI answers come from the committed cache
..\.venv\Scripts\python -m pytest -q             # backend tests
..\.venv\Scripts\python -m uvicorn app.main:app --port 8000
# second terminal
cd frontend ; npm ci ; npm run dev               # open http://127.0.0.1:5173
```

- **Offline is fine.** `SEWA_LLM_MODE=replay` serves cached AI answers for the sample briefs. A brand-new brief needs a live
  OpenAI-compatible endpoint (`SEWA_LLM_BASE_URL`, `SEWA_LLM_API_KEY`, `SEWA_LLM_MODEL`); without one, type the roles by hand.
- **No backend at all?** Open the site with `?mock=1` - it runs on built-in fixtures and labels itself "Mock data".

## What works today (verified by running it)

- **Solver:** a crew with a standby for every essential role, fair rotation, safety roles accept host-checked skills only,
  guardian consent for 16-17 year olds. On 10 synthetic drives: **READY on 7 of 10 vs 1 of 10** for nearest-skill matching; as ready
  as a careful human organiser but with far fewer repeat picks (**23% vs 43%**). Solves 500 volunteers in under 0.33 s.
- **AI role reading:** Hindi / English / Hinglish briefs -> roles with the source phrase; personal details masked first.
  A small open model on one free GPU found 93% of roles.
- **Evidence:** host notes -> AI draft cards -> rule flags -> host confirms, corrects or sends back for revision; every step goes
  into a tamper-evident hash-chained log.
- **Backend extras:** share links for a drive's public summary, demo role switch (organiser / host / volunteer / viewer, a
  simulation not real login), Hindi display text, public-demo mode with an operator token, district tree.
- **New website (frontend-v3, round 1):** all 11 story chapters, live "Plan the crew" and "Drop a volunteer" against the API,
  full console, share page, districts, volunteer view, mock mode, reduced-motion and no-WebGL fallbacks; accessibility (axe) 0
  violations in English and Hindi.

## Done since the first handoff, and still to do

- **The website was rebuilt from zero as "The Ring" (v4) and merged into `main`** (19 Nov, evening), after studying 200
  award-winning sites. One real-time 3D brass ring carries the whole story; its seats are the drive's real slots and fill
  live from the solver (names, roles, host-check), then show READY · तैयार, an honest NOT READY drive with a recruit request,
  and a live dropout re-plan. Checked: build, lint, unit tests, full browser run (`npm run verify:v4`), accessibility
  0 violations in English and Hindi, Lighthouse story 100 / console 100. Report: `docs/v6/FRONTEND-V4-REPORT.md`.
1. Remaining: re-record the demo video and screenshots from the v4 site for the submission pack (the current pack shows v3).
2. Team lead: team details on the form, ask the organisers about the age rule (one member is 17), **submit the idea form by 20 Nov**.

## Rules we keep (please keep them too)

- Never invent a number, name, partner or quote. Every figure comes from the API or the documents above.
- Synthetic data only, labelled everywhere. No real people.
- Do not copy MY Bharat's website, logo, colours or code, and no government emblems or flag colours as branding.
- AI drafts, the solver decides, a person confirms. Nothing is auto-verified.
