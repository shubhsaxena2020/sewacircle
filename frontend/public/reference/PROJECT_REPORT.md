# SewaCircle - Project Report

Living document. Last updated: 2026-11-19 (checkpoint 2). Rule: **a number appears here only if a command printed it**; everything else is marked TBD. All data is synthetic. Not affiliated with InMobi, the UP Government, MY Bharat or IIIT Lucknow.

## 1. Summary
SewaCircle **Ready Crew** answers one organiser question - "willing volunteers are here; can this drive run?" - with a READY / NOT READY verdict and concrete recruit requests. It is an organiser-side crew planner for youth volunteering, built as an idea-stage prototype for AI Kaushal 2026 UC16. It extracts roles from Hindi/English task briefs, builds a role-covered, fair and dropout-resilient roster with CP-SAT and a reason per pick, and turns host notes into reviewable contribution records with deterministic flags and a hash-chained log.

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
| CP-SAT scales: 80/80 synthetic instances OPTIMAL up to 500 volunteers, mean 0.132 s, max 0.327 s per solve | Kaggle CPU notebook `kaggle/cpu-solver-scale` |
| Name masking: 38/40 synthetic first names caught; 0 false positives on the 30 extraction briefs and all task texts | `tests/llm/test_names.py` |
| Opt-in only (the product default): 3 of 10 synthetic drives come out READY; the rest get recruit requests | live `/api/roster` call |

## 4. Progress by component (checkpoint 2, 2026-11-19)
| Component | State |
|---|---|
| Contract (schemas, taxonomy, API, LLM client) | done; amended per Codex contract review (docs/AMENDMENT-A1.md) |
| Solver: CP-SAT tiered roster, standby resilience (U1), fairness + mentor pairing (U2), why-not (U3), dropout heal | done (head; Lane A lost to a provider outage 23:37-00:14) |
| Baselines and shared metrics | done (Lane A), adapted to A1 definitions |
| Synthetic data from verified UP districts and blocks | done (head, from Lane C R4) |
| LLM extraction with PII redaction, evidence drafting with fallback | done (head); redaction, rules and ledger by Lane B |
| Unsigned OB3-shaped credential export | done (head, from Lane C R3) |
| Frontend (6 steps, Hindi/English) | done, live end-to-end verified in a browser (docs/screens/) |
| Ready Crew: ready verdict, recruit requests, safety-critical gating, unresolved roles, opt-in pool for all methods | done (docs/v3/DA-SYNTHESIS.md) |
| Name protection (roster ids + gazetteer masking) | done |
| Tests | 690 passing (`pytest -q` in backend/) |
| Strategy reviews by Codex gpt-6-sol (v2) and devil's-advocate (v3) | done (docs/v2/, docs/v3/) |
| Local open-model extraction on Kaggle GPU (Qwen2.5 3B/7B, 4-bit, 1x T4) | done (docs/LOCAL_MODEL_RESULTS.md) |
| LLM resilience: fallback model chain, offline parser fixed | done |

## 5. Results (real command output only)
Roster evaluation (`python -m eval.harness`, full output in docs/EVAL_RESULTS.md), 10 synthetic tasks, 80 synthetic volunteers:
| vs baseline | ready drives | role coverage | dropout robustness | repeat-pick share | exposure Gini |
|---|---|---|---|---|---|
| nearest-skill | +0.60 [0.30, 0.90] | +0.00 | +0.61 [0.32, 0.87] | -0.17 [-0.27, -0.07] | -0.04 |
| careful manual organiser | +0.00 | +0.00 | +0.00 | -0.20 [-0.31, -0.09] | -0.04 |
| random feasible (20 seeds) | +0.55 [0.28, 0.84] | +0.00 | +0.54 [0.28, 0.81] | -0.08 [-0.12, -0.04] | -0.02 |
Ready: SewaCircle 7/10, careful organiser 7/10, random 1.5/10, nearest-skill 1/10. Seven misses are listed by the harness itself (two scarce tasks no method can fill; one task with only 0.60 robustness; four small fairness losses to random).

Extraction (`python -m eval.extraction.run`), 30 author-written synthetic briefs (12 Hindi, 10 English, 8 Hinglish):
Claude Sonnet 5.5: role recall 1.00, precision 1.00, exact counts 1.00, 0 failures. DeepSeek v4.1 Flash: recall 0.983 (missed one role in en-07), exact counts 1.00.
Same briefs, same code path, one free Kaggle T4 GPU, 4-bit: Qwen2.5-7B recall 0.932, precision 0.917, exact counts 1.00, 0 failures, 10.7 s median (Hindi recall 0.87); Qwen2.5-3B recall 0.695 (not good enough). Full table: docs/LOCAL_MODEL_RESULTS.md.
**Caveat:** the briefs were written by the same team that wrote the prompt and state counts explicitly, so this is an easy test; a harder, independently written set is needed before claiming extraction accuracy.

## 6. Limitations (stated up front)
Synthetic data; proxy metrics only, no field-impact claim; name masking is Latin-script only and misses names outside the 61k list; Hindi/Awadhi extraction accuracy is measured on a small labelled set; the hash chain shows edits not truth; credential export is unsigned and not issued by any authority; no integration with any government system; rules about reusing pre-built code at the event are unconfirmed (ADR-001); novelty relative to MY Bharat is unverified beyond the pages we read.

## 7. Next steps
MY Bharat public-pages feature comparison; final idea answers (Ready Crew) and zip; record the demo; team lead: team details, age-eligibility question to organisers, submit the form by 20 Nov; plan the 8 to 9 Dec build from the spec.
