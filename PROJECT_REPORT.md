# SewaCircle - Project Report

Living document. Last updated: 2026-11-18 night (checkpoint 0). Rule: **a number appears here only if a command printed it**; everything else is marked TBD. All data is synthetic. Not affiliated with InMobi, the UP Government, MY Bharat or IIIT Lucknow.

## 1. Summary
SewaCircle is an organiser-side crew planner for youth volunteering, built as an idea-stage prototype for AI Kaushal 2026 UC16. It extracts roles from Hindi/English task briefs, builds a role-covered, fair and dropout-resilient roster with CP-SAT and a reason per pick, and turns host notes into reviewable contribution records with deterministic flags and a hash-chained log.

## 2. How we got here (selection)
- We scanned the official event page (fetched 2026-11-18) and extracted the verbatim texts of all 17 use cases and the judging criteria from the page's embedded data.
- A multi-lane research fleet (use-case deep dives, past winners and judges, technical feasibility) ran in parallel. The owner then selected UC16.
- An independent Codex study of UC16 (not shown the other lanes' conclusions) found that MY Bharat already covers much of the opportunity-and-credential journey and recommended not leading with a plain matcher. We therefore positioned the product as an organiser-side module (ADR-002).
- Verified on 2026-11-18: MY Bharat's official about page mentions volunteering, geotagging, digital credentials and badges; a PIB release mentions an AI-enabled CV builder, experiential programmes and 780 District Youth Offices; none of the pages we read mentions organiser-side team formation or role allocation (not found, not proof of absence).

## 3. Verified technical findings so far
| Finding | How it was measured |
|---|---|
| Claude Sonnet 5.5 via the gateway returned valid JSON with correct Hindi roles (about 11 s) on a Hindi task brief at `max_tokens` 3000 | direct API call, output parsed |
| Gemini 3.8 Flash returned valid JSON but every role count was 0 | same call |
| DeepSeek v4.1 Flash (reasoning model) returned empty content after 3000 reasoning tokens | same call; `finish_reason: length` |
| Nilabh/DeepSeek throughput is about 110 tokens/s single-stream and about 70 tokens/s per stream with 6 concurrent requests (about 420 combined) | timed requests |
| Contract skeleton: 10 contract tests pass | `pytest -q` in `backend/` |

## 4. Progress by component (checkpoint 0)
| Component | State |
|---|---|
| Contract (schemas, taxonomy, API, LLM client, tests) | done, tests green |
| Solver, baselines, metrics, synthetic data, eval harness (Lane A) | in progress |
| Extraction, redaction, evidence drafting, rules, ledger, credential export (Lane B) | in progress |
| Research R1 to R6 (Lane C) | in progress |
| Frontend (head) | not started |
| Demo video and zip v2 | not started |

## 5. Results
TBD. This section is filled only from `python -m eval.harness` and `python -m eval.extraction.run` output: role coverage, robustness, repeat-pick share, exposure Gini versus nearest-skill, random-feasible and manual-greedy with 95% bootstrap intervals; extraction recall/precision by language; rule-flag results on planted anomalies; solve times; and the list of misses.

## 6. Limitations (stated up front)
Synthetic data; proxy metrics only, no field-impact claim; names are not detected by the redactor; Hindi/Awadhi extraction accuracy is measured on a small labelled set; the hash chain shows edits not truth; credential export is unsigned and not issued by any authority; no integration with any government system; rules about reusing pre-built code at the event are unconfirmed (ADR-001); novelty relative to MY Bharat is unverified beyond the pages we read.

## 7. Next steps
Finish lanes A, B and C; build the frontend and end-to-end flow; run both evaluations once; record the demo; build zip v2; review with Codex; ask the organisers about prepared code and the age question (team lead action); plan the 8 to 9 Dec build from the spec.
