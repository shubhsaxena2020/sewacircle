# SewaCircle - PLAN.md

Goal: by **2026-11-19 06:00 IST** a working end-to-end prototype (>= 90% of PRD), real evaluation numbers, a recorded demo and an upgraded submission zip. Quality first, then time. Today is 2026-11-18; the idea form closes 2026-11-20. The team lead submits the form, not the fleet.

## Definition of done (90%)
1. `npm run build` + `uvicorn` serves the app; one organiser flow runs end to end: brief -> roles -> roster (with baseline comparison) -> why-not -> dropout heal -> evidence cards -> confirm -> ledger verify -> credential export.
2. All tests green (backend suite, property tests, ledger tamper test).
3. Eval harness and extraction eval run once each; real output pasted into the report; misses listed.
4. Demo video (under 15 MB) recorded with Playwright from the real app; zip v2 built.
5. Docs: PRD, TRD, ADR, PLAN, CONTEXT, DESIGN, PROJECT_REPORT, README with honest limitations.

## Lanes and ownership
| Lane | Who | Owns | Gate |
|---|---|---|---|
| Head | Claude Code | schemas, API, LLM client, frontend, integration, docs, final verification | contract tests, UI QA, end-to-end run |
| A solver + eval | Hermes lead res-s2 (3 subagents/batch) | `backend/app/solver`, `data/synth.py`, `backend/eval` | solver tests incl. 200-seed property test; eval report |
| B LLM + evidence | Hermes lead res-s3 | `llm/extract.py`, `redact.py`, `evidence/`, `eval/extraction` | unit tests; live extraction eval on 30 briefs |
| C research | Hermes lead researcher | `docs/research` (R1..R6 + INDEX) | each file with opened sources and run code |
| Orchestrator | Codex gpt-6-luna | contract review (pass 1), final review (pass 2) | written review, no polling |

## Timeline (IST, targets)
| Time | Milestone |
|---|---|
| ~00:30 | Contract skeleton green (done); lanes A, B, C running; documents drafted |
| ~01:30 | Lane C batch 1 done (R1 to R3); A batch 1 (data, metrics, baselines) green |
| ~02:30 | Solver core green (A batch 2); extraction prompts + labelled set (B batch 2); frontend skeleton against stubs |
| ~04:00 | U1/U2/U3 in solver; draft_cards, rules, ledger green; frontend screens wired; first end-to-end run |
| ~05:00 | Eval harness and extraction eval run; demo recorded; Codex review pass |
| ~06:00 | Zip v2 and report finalised; remaining 10% logged in the report |

## Checkpoint rule
At every checkpoint the head runs the full test suite itself and compares claims against files and command output. A lane whose output fails verification is re-run or fixed by the head before dependants proceed.

## Risks and fallbacks
| Risk | Fallback |
|---|---|
| A lane stalls or skips subagents | Head finishes the module; reduce scope to core + one unique |
| LLM provider slow/rate-limited | Replay cache; run extraction eval once; smaller briefs |
| Solver slower than expected | Reduce volunteers per task; time-limit with FEASIBLE status; document |
| Hindi extraction weaker than hoped | Report honestly; manual path; tighten prompts; do not tune on the eval set |
| Gateway restart by a neighbour project cuts a lead | Runner resumes the session; head checks `PROGRESS.md` |
| Time | Cut stretch goals first (voice, map), never the tests or the eval |

## After 06:00
Submit by midday if the lead wishes (zip v2), email organisers about prepared-code rules and age, then plan the 8 to 9 Dec build from the spec (ADR-001).
