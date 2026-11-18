# INDEX — the ten implementation decisions for the SewaCircle build

Synthesised on 2026-11-18 from `R1-optimization.md`, `R2-nlp-hindi.md`, `R3-credentials-privacy.md`, `R4-up-realism.md`, `R5-demo-ux.md`, `R6-eval-responsible-ai.md` and `up_districts.json`. All demo data referenced here is **SYNTHETIC**. This file is a decision list, not a summary: each entry is one rule, one line of why, and the section to open before coding. **How to use this file:** implement the bold sentence; if this index and a research file ever disagree, the research file wins and this index gets fixed.

## The ten decisions

1. **Model the roster as binary `x[v,r]` with skill, availability, commute and headcount as hard constraints, and keep "quality" only in the integer objective.**
   Why: a penalty must never be able to buy an unsafe skill mismatch, and CP-SAT needs integer terms anyway. → `R1-optimization.md` > Recommendation for our build ("Hard vs soft") and Findings (implemented formulation 1).

2. **Make single-dropout standby part of the model, not a UI afterthought: add primary `z[v,r]` + standby `s[v,r]` with, for every potential primary `w` on role `r`, `Σ_{u≠w} s[u,r] ≥ z[w,r]`; ship k=1 only and surface an infeasible robust model instead of silently dropping the guarantee.**
   Why: this is the constraint that makes "drop a volunteer, every role stays covered" true by construction rather than by luck, and k>1 is a documented harder problem. → `R1-optimization.md` > Findings (formulation 5) and Recommendation (Code shape: `add_standby`).

3. **Implement the exposure cap as a Python branch (`prior_exposure >= cap` → `assigned == 0`) and report repeat-pick share and Gini as two separate descriptive metrics, never as one "fairness improved" number.**
   Why: emitting `prior + assigned <= cap` when `prior > cap` makes the whole model infeasible (observed `STATUS INFEASIBLE` with a stale `Value()` roster), and post-selection Gini actually rose from 0.2338 to 0.3117 under the cap. → `R1-optimization.md` > Recommendation ("Exposure cap implementation", "Gini placement") and Risks.

4. **Answer "why not X?" only by re-solving the base model with `Σ_r x[X,r] = 1` forced and reporting the objective delta plus displaced/added names; if the forced model is INFEASIBLE, say "no feasible roster includes X".**
   Why: it is the documented "slightly modified model" counterfactual pattern, and inventing a reason is the one failure mode judges can catch live. → `R1-optimization.md` > Findings (formulation 6) and Recommendation ("Reason per pick").

5. **Extract roles through a closed JSON schema (every property required, `additionalProperties: false`, closed enums, `count` integer ≥ 1, verbatim `evidence_span`) plus a mandatory `needs_review` abstention path, and gate CP-SAT behind our own provider-agnostic validator.**
   Why: constrained decoding guarantees shape only — Gemini does not guarantee numeric bounds such as `minimum`, and OpenAI excludes refusals from the guarantee — so `count ≥ 1`, substring evidence, taxonomy membership and PII-freedom must be checked in our code, and an unreviewed extraction must never reach the solver. → `R2-nlp-hindi.md` > Recommendation for our build ("Proposed JSON schema", "Abstention triggers").

6. **Redact Indian PII before every model call: normalise Devanagari digits, then apply Aadhaar → phone → PAN → email → cue-based name/address patterns, merge overlapping spans, substitute `[REDACTED:CLASS]`, and log counts only — then re-run the same patterns on every emitted string.**
   Why: a checksum pass is not authenticity, and a verbatim `evidence_span` can re-introduce a name the redactor missed; names/addresses are cue-based and must stay review-covered, not declared solved. → `R2-nlp-hindi.md` > Recommendation ("Pipeline", "Redaction code shape") and Risks ("Evidence-span leakage").

7. **Generate every fixture from the verified UP registry: the 20 district points in `up_districts.json` labelled "approximate district point", block/tehsil names only from the lists R4 verified, ages 15–29, languages from the Census categories, and skills drawn from the 24-ID taxonomy (rows whose anchor is marked inferred stay labelled that way).**
   Why: real geography and real drive archetypes make the demo credible, while the source documents no centroid method, lists 69 of 75 UP districts, and the skill list is our normalisation — not a government standard — so every label must say so. → `R4-up-realism.md` > Recommendation for our build (bullets 1–2 and the 24-skill table); `up_districts.json` (`coordinate_caveat`).

8. **Emit the portable record with OB 3.0's exact field names, `@context` order and required list but with no `proof` field, labelled "unsigned, data-model-shaped — not a verifiable credential"; treat the hash chain the same way — tamper-evidence of appended bytes, not truth of the hours.**
   Why: both artefacts prove syntax and ordering only; without an issuer key or an external anchor, "verified credential" and "tamper-proof" are false, and a whole-chain rollback stays invisible from the chain alone. → `R3-credentials-privacy.md` > Recommendation ("Concrete minimal JSON", "Ledger shapes") and Risks 1 & 5.

9. **Score all four methods (`cp_sat`, `nearest_skill`, `random_feasible`, `manual_greedy`) with one shared metric implementation, freeze fixtures, seeds and baseline code before the first run, and report paired seeded bootstrap intervals (10,000 resamples) always prefixed "synthetic fixture, descriptive only".**
   Why: n=10 gave 0.825 with a 95% interval of [0.70, 0.95] — 0.25 wide — so only paired differences may be described, `manual_greedy` is a code proxy rather than observed practice, an INFEASIBLE solve scores 0, and every miss is published. → `R6-eval-responsible-ai.md` > Recommendation for our build ("Baselines — compare like with like", "Reporting with n=10 — no overclaiming").

10. **Rehearse the ten-segment 180-second demo against its own timings and build the UI to GIGW/WCAG basics first — ≥4.5:1 contrast, 200% zoom, 320 px reflow, `lang` per span, Devanagari-capable font stack, icon + Hindi label + English gloss, literal error text — then record at 960×540, 25 fps, one worker.**
    Why: ten segments leave almost no slack and every on-screen number must come from a fresh run, while accessibility is only evidence once it has actually been tested, not asserted. → `R5-demo-ux.md` > Recommendation for our build (R3 "Improved 3-minute demo script", R2 accessibility checklist, R4 recording recipe).

## Do not claim

> - **No population property from n=10.** "Mean role coverage 0.825 (95% CI 0.70–0.95) on 10 synthetic tasks" is allowed; "our system achieves 82.5% coverage" is not. No p-values, no "significantly better", no winner claims, no κ as a stable estimate.
> - **No production or scalability result.** R1's 0.0134–0.0213 s solves are a 9-volunteer toy instance; a single timing is not a benchmark, and `manual_greedy` is a "manual-greedy proxy", never "today's baseline" measured in a department.
> - **No credential overclaim.** Not a "verified credential", "Open Badge issued by MY Bharat", "accredited", "government-issued", "digital skill passport recognised by the Department"; no fake `proof` field, no hours property invented into OB3.
> - **No endorsement implication.** MY Bharat, NYKS and any district administration do not endorse, supply data to, or use this prototype (not found on official pages); the demo only imitates the *shape* of NSS/NYKS district work.
> - **No "tamper-proof", "fraud-proof" or "hours are true".** The chain proves these bytes were appended in this order; rollback/restart is invisible without an outside anchor, and no field pilot or fraud-reduction measurement exists.
> - **No "bias-free", "fair" certificate, or "fairness improved" from a cap alone.** Twin-swap tests on synthetic labels can pass by construction; zero risk of bias is not achievable.
> - **No compliance claim.** DPDP s.9/Rule 10 guardian consent is not implemented (and sits in the 18-month commencement tranche); no real minor's data may be processed, and redaction is not complete.
> - **No stability claim.** Novice–mentor is a same-site/same-role hard constraint, not two-sided matching stability; only single-dropout resilience is tested (k=1).
> - **No data-provenance overclaim.** District coordinates are approximate locator points, not centroids or legal boundaries; the 24-skill taxonomy is our proposal, not a government framework; age/language mixes are labelled INFERENCE.
> - **No unverified tooling or conformance claims.** No `npx playwright test --video=on`; no "under 15 MB" before `ls -l` prints it; no WCAG/GIGW conformance or low-literacy suitability without testing, and 18 px Devanagari is W3C's own stylesheet choice, not a normative minimum.
