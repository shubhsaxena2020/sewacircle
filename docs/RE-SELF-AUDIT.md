# Reverse-engineering self-audit of SewaCircle (REA)

Date: 2026-11-19. Target: our own app, served locally at http://127.0.0.1:8000 (FastAPI + built React UI). Tool: REA
`capture_browser_scenario` (headless Chromium 157, controlled replay), evidence id
`ev_229c7551fcd64432b9a47910aae2ad487aaf170669e1308122fb8381beb6e718`.

## Scenario driven
Load page -> Extract roles -> Confirm roles and build roster -> Drop out first assigned person -> Approve roster ->
Draft contribution cards. (The scripted wait after drafting used a selector that matched 9 chips; that was a script error,
not an app error, so the last three steps were not executed by REA and were verified separately in the browser earlier.)

## Observed (FACT, from the capture)
- 15 network transactions, all HTTP 200: document, 1 JS bundle, 1 CSS file, 5 self-hosted font files, favicon,
  `GET /api/tasks`, `GET /api/volunteers`, `POST /api/extract-roles`, `POST /api/roster`, `POST /api/roster/dropout`,
  `POST /api/evidence/draft`.
- 0 page errors and 0 console messages across the run.
- No third-party origins: every request went to 127.0.0.1:8000 (fonts are self-hosted, no CDN, no analytics).
- `extract-roles` answered from the record/replay cache in this run; `evidence/draft` took about 11.6 s (live model call).

## Defects found and fixed
| # | Finding | Evidence | Fix | Test |
|---|---|---|---|---|
| RE-1 | After a dropout reshuffle, the volunteer's OLD undecided draft card (old role) stayed in the store, so the new card shared the attendance reference and was flagged `duplicate_evidence_ref` (a false flag shown to the host). | card store after the run: `card-task-01-v-068-first-aid-support` (draft) and `card-task-01-v-068-poster-team` (flagged: duplicate_evidence_ref) | `/api/evidence/draft` now supersedes undecided draft/flagged cards of the same task that are not in the new draft; host-decided cards are never touched; ledger history is kept. | `tests/test_api_evidence_flow.py::test_reshuffle_does_not_create_false_duplicate_evidence_flag` (fails on the old code, passes now) |
| RE-2 | Demo state leaked between runs: a fresh walkthrough showed cards already "confirmed"/"corrected" from an earlier session. | same card store | New `POST /api/demo/reset` archives the card store and ledger (renamed with a timestamp, never deleted) and starts clean. | `test_demo_reset_archives_state_and_starts_clean` (fails on the old code) |
| RE-3 | Ops: 9 orphan API server processes and 12 orphan `vite preview` processes had accumulated after session restarts. | process list | Stopped; demo runbook must start exactly one server. | n/a |

## Not yet covered (next REA passes)
Bundle-level static analysis (`analyze_web_bundle` needs a CDP endpoint), keyboard-only/accessibility audit, why-not drawer,
ledger verify and credential export steps under REA, and an offline (`SEWA_LLM_MODE=replay`) cold-start run.
