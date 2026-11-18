# SewaCircle - Technical Requirements Document (TRD)

Status: v1, 2026-11-18. Companion to PRD.md. Decisions and their reasons are in ADR.md. Schemas are the source of truth in `backend/app/schemas.py`.

## 1. Architecture
```
Browser (React + Vite + TypeScript)  --HTTP/JSON-->  FastAPI backend (Python 3.13)
                                                      |-- llm/        extraction, redaction, evidence drafting  (LLM = Claude Sonnet 5.5 via an OpenAI-compatible gateway; record/replay cache)
                                                      |-- solver/     OR-Tools CP-SAT roster, baselines, dropout simulation, counterfactuals, shared metrics
                                                      |-- evidence/   deterministic rules, hash-chained ledger, credential export
                                                      |-- data/       deterministic synthetic volunteers and tasks
                                                      '-- eval/       harness (all methods x 10 tasks, bootstrap CIs) and extraction eval (30 labelled briefs)
```
Design rule: **AI reads messy human text; a deterministic solver decides; a human approves; nothing is called verified without a host.**

## 2. Stack
Python 3.13, FastAPI 0.164, pydantic 2.14, OR-Tools 9.15 (CP-SAT), httpx, pytest. Frontend: React 18, Vite, TypeScript, self-hosted Inter and Noto Sans Devanagari. SQLite/JSON-lines for the ledger. No cloud dependency except the LLM gateway; replay mode runs fully offline from cached outputs.

## 3. Data model (summary of `schemas.py`)
`Volunteer` (synthetic; skills dict level 1..3 over a 24-skill taxonomy, availability slots, location, past_drives, times_picked_last_90d, guardian_consent), `TaskSpec` with `RoleSpec[]`, `ExtractionResult`, `RosterOptions`, `RosterResult` (assignments with reasons, standby, unfilled roles, metrics), `Counterfactual`, `DropoutResult`, `ContributionCard` (draft/flagged/confirmed/corrected/rejected), `Flag`, `LedgerEntry`, `LedgerVerification`, `EvalReport`.

## 4. API
| Method and path | Purpose |
|---|---|
| GET `/api/health`, `/api/meta` | status, disclaimer, taxonomy |
| GET `/api/volunteers`, `/api/tasks` | synthetic data |
| POST `/api/extract-roles` | brief -> `ExtractionResult` |
| POST `/api/roster` | task + options -> `{cp_sat, nearest_skill}` rosters |
| POST `/api/roster/why-not` | counterfactual for one volunteer |
| POST `/api/roster/dropout` | simulate one dropout and heal |
| POST `/api/evidence/draft` | host notes + attendance -> draft cards (rules run, ledger appended) |
| GET `/api/evidence/cards`; POST `/api/evidence/{id}/confirm|correct|reject` | host decisions |
| GET `/api/ledger`, `/api/ledger/verify` | audit chain and its verification |
| GET `/api/export/credential/{id}` | unsigned credential for host-confirmed cards (409 otherwise) |
| GET `/api/eval` | evaluation report (all methods) |
Unimplemented lane functions return 501, never 500. LLM failures map to 502 with a manual-entry path in the UI.

## 5. Solver (CP-SAT)
Variables: `x[v,s]` volunteer v fills slot s of a role (one role per volunteer). Hard constraints: availability in the task slot; qualification (any required skill at >= min level; self-declared skills allowed but flagged); haversine distance <= max travel; minors only with guardian consent and when the task allows; forced-in/forced-out. Lexicographic-style weighted objective: (1) must-role coverage, (2) skill fit, (3) proximity, (4) fairness (penalise heavy recent picks; bonus for novices within a cap; novice-mentor pairs where `needs_experienced`; district spread), (5) resilience (standby set `b[v]` chosen so every single dropout leaves all must roles coverable). Status is reported honestly (OPTIMAL/FEASIBLE/INFEASIBLE); unfillable roles go to `unfilled_role_ids`.
**Robustness** (one function for all methods): for each assigned volunteer v, can every must slot still be filled from (assigned minus v) plus the roster's standby, using qualified, available, in-range volunteers via bipartite matching? robustness = share of v that pass. Baselines get honest credit: `manual_greedy` includes one backup per role.
**Counterfactual (U3):** re-solve with the volunteer forced in; report feasibility, coverage and robustness deltas, displaced volunteers, and the blocking constraint when infeasible.
**Dropout (U1):** remove the volunteer, promote a standby if it covers, otherwise re-solve; report uncovered roles.

## 6. LLM layer
`llm/client.py::complete_json` calls an OpenAI-compatible gateway (`SEWA_LLM_BASE_URL`, default `http://127.0.0.1:20128/v1`) with `stream:false`, `temperature:0`, `max_tokens` >= 3000, tolerant JSON extraction, retries, and a **record/replay cache** (`record` default, `live`, `replay`). Default model: Claude Sonnet 5.5. Measured 2026-11-18 on a Hindi extraction prompt: Claude Sonnet 5.5 returned valid JSON with correct Hindi roles in about 11 s; Gemini 3.8 Flash returned valid JSON but set every count to 0; DeepSeek v4.1 Flash is a reasoning model that spent all 3000 tokens thinking and returned empty content (ADR-005).
Extraction: PII redaction first (phone, Aadhaar, PAN, email, UPI, long account numbers; names are not detected), taxonomy-constrained prompt with few-shot Hindi/English/Hinglish examples, output validated against `ExtractionResult`, unknown skills dropped with a note, low-confidence roles listed in `needs_decision`. Evidence drafting never sets a card to confirmed.

## 7. Evidence ledger
Cards carry claimed and recorded hours. Deterministic rules (no AI): hours exceed recorded; no attendance record; implausible daily hours; duplicate evidence reference; identical summary text; overlapping tasks; minor without guardian consent; self-declared skill unconfirmed; round-number inflation; plus one lane-chosen rule. Flags never auto-reject. The ledger is an append-only JSON-lines hash chain, `entry_hash = sha256(prev_hash | ts | action | card_id | actor | payload_hash)`. `verify()` returns the first bad index. **A hash chain shows edits, not truth; truth comes from host confirmation.** Credential export (U4) is an unsigned Open Badges 3.0 / W3C VC compatible document only if Lane C verified the fields from the primary specs.

## 8. Evaluation and testing
`python -m eval.harness --out eval_report.json` runs cp_sat, nearest_skill, random_feasible, manual_greedy over 10 labelled tasks, 95% bootstrap CIs (seeded, 1000 resamples), and lists misses. Extraction eval: `python -m eval.extraction.run` over 30 labelled briefs (12 Hindi, 10 English, 8 Hinglish) reporting recall, precision, count accuracy, abstention by language. Unit tests (pytest) never touch the network. Property tests over 200 random seeds check hard constraints. Every number in README, project report and the pitch must come from these commands' real output.

## 9. Non-functional requirements
Roster solve under 10 s on a laptop; API p95 under 200 ms excluding LLM calls; deterministic results for the same seed; full test suite under 3 minutes; works offline in replay mode; no secrets in the repository; synthetic labels in every UI view; WCAG 2.2 AA target (DESIGN.md section 7).

## 10. Security and privacy
Redaction before model calls; no real personal data anywhere; minors appear only with guardian consent flags in synthetic data; CORS open only for local development; the LLM gateway key comes from the environment, never from files; the cache directory is git-ignored.

## 11. Path to pilot (documented, not built)
Export-first adapter (CSV/JSON) for any programme owner; authentication and roles; consent management; WhatsApp or IVR intake; signed credentials by a recognised issuer; data-sharing agreements and a DPDP review; hosting inside a department's environment. Integration with MY Bharat or any UP system requires approval and a documented API, which we did not find publicly.

## 12. Repository layout
`backend/app/{schemas,taxonomy,main}.py`, `backend/app/{llm,solver,evidence,data}/`, `backend/eval/`, `backend/tests/`, `frontend/`, `docs/` (research, lane cards, QA), root documents (PRD, TRD, PLAN, ADR, CONTEXT, DESIGN, PROJECT_REPORT).
