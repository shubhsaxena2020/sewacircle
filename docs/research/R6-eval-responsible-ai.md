# R6 — honest evaluation plan and responsible-AI checks (Lane C, SewaCircle)

Research date 2026-11-18. **All tasks, volunteers, attributes and numbers below are SYNTHETIC.** No real person, no real minor, no real identity document. Claims are labelled FACT (opened source or command output), INFERENCE (our design reasoning) or OPINION. Every external FACT has an opened URL inline with the access date.

## Findings

**F1 — FACT (external).** The NIST/SEMATECH e-Handbook describes the bootstrap as generating subsamples *with replacement* from the data, computing the statistic on each, and sorting those values to form a confidence interval (500 subsamples is given as usually sufficient); it explicitly cautions that "the bootstrap is not appropriate for all distributions and statistics" and is unsuitable for statistics heavily dependent on tails such as the range. Opened: [1.3.3.4 Bootstrap Plot, NIST e-Handbook](https://www.itl.nist.gov/div898/handbook/eda/section3/bootplot.htm), accessed 2026-11-18. **INFERENCE:** a percentile CI on a bounded metric like role coverage is defensible as a *descriptive* interval here, but range/extremestatistics must not be bootstrapped on n=10 without this caveat.

**F2 — FACT (external).** A NIST paper defines the bootstrap percentile interval exactly: resample the per-topic scores with replacement, compute the mean of each resample, sort the means, and take the α and 1−α percentiles; with α=0.05 and 5,000 resamples the endpoints are the 250th and 5,750th ordered values. It reports empirical coverage experiments (e.g. 0.919 nominal-0.95 for a standard interval on one run), recommends bootstrap percentile intervals where no statistical library is available, and states that "using more topics results in tighter confidence intervals". Opened: [Ian Soboroff, Computing Confidence Intervals for Common IR Measures, 6th EVIA Workshop, 9 Dec 2014, Tokyo](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=917303), accessed 2026-11-18. **INFERENCE:** the same mechanics apply to 10 task-level scores; the "more items → tighter interval" sentence is why we must not present n=10 intervals as precise.

**F3 — FACT (measured locally).** A seeded, stdlib-only bootstrap on a synthetic n=10 role-coverage array prints a point estimate of 0.825 and a 95% percentile interval [0.7, 0.95]. Command and verbatim output:

```text
$ C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r6_bootstrap_ci.py
SYNTHETIC DATA ONLY - no real volunteers or tasks
N_TASKS 10
BOOTSTRAP_RESAMPLES 10000
SEED 20261118
POINT_ESTIMATE_MEAN_ROLE_COVERAGE 0.825
CI95_PERCENTILE_LOW 0.7
CI95_PERCENTILE_HIGH 0.95
REPORT_AS: descriptive estimate from 10 synthetic tasks; NOT a production benchmark
EXIT_CODE=0
```

The interval spans 0.25 of the 0–1 scale: that width, not the point estimate, is the honest headline for n=10. The runnable source is reproduced under Recommendation.

**F4 — FACT (external).** NIST AI RMF 1.0 (released 2023-01-26; the NIST page says a revision is in progress as of access) names seven trustworthy-AI characteristics — valid and reliable, safe, secure and resilient, accountable and transparent, explainable and interpretable, privacy-enhanced, and fair with harmful bias managed — and organises its Core into Govern, Map, Measure, Manage. The Core's Measure 2.1 says test sets, metrics and details about TEVV tools are documented; Measure 2.5 requires documented limits of generalizability; Measure 2.6 requires safety metrics including response times for failures; Measure 2.10 privacy risk; Measure 2.11 fairness and bias results; Measure 3.3 requires feedback and appeal processes. Opened: [NIST AI RMF landing page](https://www.nist.gov/itl/ai-risk-management-framework) (released 26 Jan 2023, accessed 2026-11-18), [AI Risks and Trustworthiness, NIST AIRC](https://airc.nist.gov/airmf-resources/airmf/3-sec-characteristics/) (excerpt of AI RMF 1.0, accessed 2026-11-18), [AI RMF Core, NIST AIRC](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) (accessed 2026-11-18).

**F5 — FACT (external).** NIST Special Publication 1270 (March 2022) identifies three categories of AI bias — systemic, computational/statistical, and human-cognitive — states that "it is not possible to achieve zero risk of bias in an AI system", calls for a socio-technical perspective, and says test and evaluation is continuous through the lifecycle; it also says "the most accurate model is not necessarily the one with the least harmful impact". Opened: [Towards a Standard for Identifying and Managing Bias in Artificial Intelligence, NIST SP 1270](https://nvlpubs.nist.gov/NISTpubs/SpecialPublications/NIST.SP.1270.pdf), March 2022, accessed 2026-11-18.

**F6 — FACT (external).** The Model Cards paper (FAT* 2019) recommends short reports with benchmarked evaluation disaggregated by relevant cultural, demographic and phenotypic groups *and* intersectional combinations, together with intended use and evaluation details, and says group definitions and the motivation for metric choices should be disclosed. Opened: [Mitchell et al., Model Cards for Model Reporting](https://ar5iv.labs.arxiv.org/html/1810.03993), FAT* '19, accessed 2026-11-18.

**F7 — FACT (external).** *Fairness and Machine Learning: Limitations and Opportunities* (MIT Press, 2023; site last updated 2023-11-10) states there is "no single test for fairness" and that tests diagnose potential unfairness rather than establish it; moral reasoning and domain-specific considerations determine which test applies. Its testing chapter describes audit studies, blinding tests, an adversarial test that compares two otherwise-identical simulated groups with a permutation test, and warns about proxies and sample size. Opened: [fairmlbook.org](https://fairmlbook.org/) (accessed 2026-11-18) and [Testing discrimination in practice](https://fairmlbook.org/testing.html) (accessed 2026-11-18).

**F8 — FACT (external).** ACM's artifact policy defines *repeatability* as the same team and setup, *reproducibility* as a different team using the authors' artifacts, and *replicability* as a different team with independently developed artifacts; "Artifacts Evaluated – Functional" requires artifacts to be documented, consistent, complete and exercisable with evidence of verification and validation, and "Artifacts Available" requires permanent public retrieval. Opened: [Artifact Review and Badging v1.1, 24 Aug 2020](https://www.acm.org/publications/policies/artifact-review-and-badging-current) and [v1.0 archive](https://www.acm.org/publications/policies/artifact-review-badging), accessed 2026-11-18. **INFERENCE:** our one-command harness can at best demonstrate repeatability today; it is not third-party reproducibility.

**F9 — FACT (external).** Sandve et al. (PLOS Comput Biol, 24 Oct 2013) make "for every result, keep track of how it was produced" Rule 1, recommend executable workflows (shell scripts/makefiles) so the specification cannot drift from what was actually run, and note that recording program versions, parameters and inputs is the minimum. Opened: [Ten Simple Rules for Reproducible Computational Research](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003285), accessed 2026-11-18.

**F10 — FACT (external).** The scikit-learn 1.9.1 documentation warns that data leakage — using information unavailable at prediction time — produces overly optimistic estimates, that test data must never be used to make model choices, and that passing an integer `random_state` makes results repeatable across executions. Opened: [Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html), accessed 2026-11-18. **INFERENCE:** our baseline parameters and fixture labels must be frozen *before* the first scoring run, and the random baseline's seed published, or the comparison is contaminated.

**F11 — FACT (external).** *Datasheets for Datasets* proposes documenting a dataset's motivation, composition, collection process and recommended uses. Opened: [arXiv:1803.09010](https://arxiv.org/abs/1803.09010), submitted 23 Mar 2018, v8 1 Dec 2021, published in CACM Dec 2021; accessed 2026-11-18.

**F12 — FACT (local files read, no URL).** The shipped contract already fixes the metric definitions and the four comparison methods: `backend/app/schemas.py:14` defines `Method = Literal["cp_sat","nearest_skill","random_feasible","manual_greedy"]`; `backend/app/schemas.py:196-217` defines `RosterMetrics` (`role_coverage`, `should_coverage`, `robustness`, `repeat_pick_share`, `exposure_gini`, `district_spread` = distinct (district, block) among assigned, `solve_ms`, `solver_status`) with the exact formulas in its docstring; `backend/app/schemas.py:319-327` defines `EvalReport(n_tasks, n_volunteers, rows, summary, ci95, misses, generated_by, synthetic)`. `backend/eval/harness.py:1-9` currently raises `NotImplementedError` and documents the entry point `python -m eval.harness` from `backend/`. `CONTEXT.md:17` gives the one-command invocation with `--out eval_report.json`. Read-only on 2026-11-18; **no claim here that the harness runs today.**

## Recommendation for our build

**Test set — freeze before the first run.** 10 labelled tasks and 20–40 synthetic volunteers (30 proposed), following R2's annotation mix: 3 English, 3 Devanagari Hindi, 2 Roman Hinglish, 2 Awadhi/Bhojpuri-flavoured briefs; deliberately include two negation cases, two Devanagari-numeral cases, one transliteration-heavy case and one >1,000-character brief. Each volunteer row carries, *synthetically*: id, skills 0–3, availability by slot, district and block, distance km, `times_picked_last_90d`, is_new, novice/mentor flags, gender tag and preferred/first language tag. The last two are **audit-only**: never read by the solver. Every fixture and UI surface shows `SYNTHETIC — NOT REAL DATA`; all volunteers are fictional adults. Record a SHA-256 of the frozen fixture file in the report (F9). Two bilingual annotators label, a third adjudicates; with n=10 publish raw agreement counts, not a stable κ (F6, R2).

**Metrics — use the contract functions verbatim, one implementation for all four methods.** Report each per-task value, then the mean over 10 tasks with its bootstrap interval, plus the list of misses.

| Metric | Exact definition (from `schemas.py:196-217`) | Reporting rule |
|---|---|---|
| Role coverage | Filled qualified MUST slots / total MUST slots, counting each `(role_id, slot_index)` once; 1.0 if no MUST slots | Mean + all 10 task values + unfilled slot IDs; an `INFEASIBLE` solve counts as **0**, never as a dropped task |
| Should coverage | Same for SHOULD slots, `None` if none exist | Report separately; never blend into MUST coverage |
| Roster time | `solve_ms` plus `solver_status` | Median and max over 10 tasks; re-run the identical case ≥3 times and report spread. Our own re-run of the same script printed different wall times (0.0203 s vs 0.0134 s in R1's original; see BATCH1-REVIEW.md), so a single timing is not a benchmark |
| Repeat-pick fairness | `repeat_pick_share` = assigned with `times_picked_last_90d >= 3` / assigned; `exposure_gini` = Gini of `times_picked_last_90d` over the task-**eligible** pool with selected people +1 (0 if all zero or pool empty) | Report **both**; they are different metrics. R1 measured a post-selection Gini rising from 0.2338 to 0.3117 under an exposure cap — never say "Gini improved" from a cap alone |
| District spread | `district_spread` = distinct `(district, block)` among assigned | Also publish per-district selection rate = selected / eligible, so a small eligible pool is not mistaken for bias; report the `max_per_district` policy value |
| Dropout resilience | `robustness`: for each assigned volunteer, 1 if a maximum matching of (assigned minus that volunteer) plus the roster's unique standby pool covers every MUST slot with qualification, availability, travel and consent rechecked; mean over assigned (0 if nobody assigned, 1 if no MUST slots) | Report mean, number of assigned volunteers tested, and every failed dropout; scope is k=1 only |
| Extraction quality | R2 owns this: schema-valid rate, role P/R/F1, count MAE, negation recall, `needs_review` rate | Cross-reference R2; do not duplicate or contradict its definitions |

**Baselines — compare like with like.** The contract already names the four methods (`schemas.py:14`).

| Method | Construction | Honest label |
|---|---|---|
| `cp_sat` | Full model: hard eligibility + fairness policy + standby | Our system under test |
| `nearest_skill` | Greedy: among eligible volunteers, rank by skill surplus then distance; fill slots in fixed role order; no exposure cap or standby | Deterministic heuristic |
| `random_feasible` | Seeded shuffle of eligible volunteers per slot, retry until a feasible roster or a bounded attempt limit | Publish all seeds (proposed: 20), report mean and spread; **never** select the best seed |
| `manual_greedy` | Fixed human-emulable order: first available volunteer meeting the skill threshold, nearest first, no rotation or standby | **"manual-greedy proxy"** — a code emulation, *not* measured current departmental practice. No observed manual baseline exists in this repo; do not write "today's baseline" as an empirical finding |

All four must consume the *same* eligibility matrix, MUST/SHOULD semantics, travel/consent filters and fixture hash; freeze these and the baseline code before scoring (F10). If a method cannot fill a slot, record lower coverage rather than silently excluding the task. Every row records `generated_by`, `synthetic: true`, interpreter version and ortools version (this environment printed Python 3.13.14 and ortools 9.15.6755).

**Reporting with n=10 — no overclaiming.** Bootstrap the *task-level* scores, seeded, 10,000 resamples, percentile endpoints; report the point estimate and the interval together, always with the words "synthetic fixture, descriptive only". The exact proof script (stdlib only; run output pasted in F3):

```python
import random

# SYNTHETIC per-task role-coverage fractions (invented for this demo only).
coverage = [1.00, 0.75, 1.00, 0.50, 1.00, 0.75, 1.00, 0.75, 0.50, 1.00]
n = len(coverage)
assert n == 10, "this proof is for n=10"
seed = 20261118
B = 10000
rng = random.Random(seed)

point = sum(coverage) / n
boot = []
for _ in range(B):
    resample = [coverage[rng.randrange(n)] for _ in range(n)]
    boot.append(sum(resample) / n)
boot.sort()

lo = boot[int(0.025 * B)]
hi = boot[int(0.975 * B) - 1]

print("SYNTHETIC DATA ONLY - no real volunteers or tasks")
print("N_TASKS", n)
print("BOOTSTRAP_RESAMPLES", B)
print("SEED", seed)
print("POINT_ESTIMATE_MEAN_ROLE_COVERAGE", round(point, 4))
print("CI95_PERCENTILE_LOW", round(lo, 4))
print("CI95_PERCENTILE_HIGH", round(hi, 4))
print("REPORT_AS: descriptive estimate from 10 synthetic tasks; NOT a production benchmark")
```

Rules for writing the result up:

1. **Never claim a population property.** "Mean role coverage 0.825 (95% percentile CI 0.70–0.95) on 10 synthetic tasks" is allowed; "our system achieves 82.5% coverage" is not.
2. **Compare methods with paired differences.** Bootstrap `score_cp_sat(task) − score_baseline(task)` over the same 10 tasks, not two independent CIs; a gap between two separate intervals is not a test (F2).
3. **No p-values, no "significantly better", no winner claims** from this set. Overlapping intervals are not proof of equality; non-overlap on synthetic tasks is not proof of a real-world effect (F1, F2, F7).
4. **Publish the raw table and misses.** Include all 10×4 rows, every `INFEASIBLE` status, and `EvalReport.misses` verbatim. An honest "we did not beat the baseline on 6/10 tasks" is a stronger demo than a rounded mean.
5. **Keep uncertainty visible in the UI and video.** Show the interval on the summary slide, not just the point estimate; state the seed and resample count in the screenshot caption.
6. **Do not bootstrap small subgroup statistics** with fewer than 5 members; print `INSUFFICIENT_N` and the numerator/denominator instead (F6, F7).
7. **Timing is not a benchmark.** Report median, max, repeats and version pins; single-run wall time on a 9-volunteer toy instance says nothing about production scale (F4 Measure 2.5).
8. **Re-run before quoting.** The harness prints `generated_by`; paste that string into the report rather than retyping numbers (F9).

**Bias tests across gender, district and language (synthetic attributes only).** These are *tests that can fail*, not a fairness certificate (F5, F7).

| Axis | Concrete test | Pass evidence | Limitation to print alongside |
|---|---|---|---|
| Gender | **Twin swap:** take each of the 10 tasks, duplicate a volunteer changing only the gender tag (identical skills, availability, distance, exposure), solve both, compare selected/role/standby. Also compute selection rate = selected / eligible by gender over the 30 volunteers | Zero pick/role/standby flips in the 10 twin pairs; rates printed with counts (`k_selected/k_eligible`) | Synthetic gender labels; no inference about real applicants. With small cells print `INSUFFICIENT_N` |
| District | **Label swap:** change only the district/block label, hold distance and skills fixed, re-solve; plus per-(district, block) selection rates and the policy's max-per-district cap | Zero flips attributable to the label alone; no eligible district reduced to zero by the cap without an explicit policy note | District is a *diversity proxy* chosen by policy, not proof of fairness; R1 deliberately excluded gender/caste/religion from the objective |
| Language | **Semantic twins:** render the same role specification as English, Devanagari Hindi, Roman Hinglish and Awadhi-flavoured briefs; compare extracted roles, counts, evidence spans and `needs_review` | Identical extracted role set and review flag across variants (or an explicit, reviewed reason for divergence); solver output unchanged because language tag never reaches CP-SAT | R2's failure modes (Devanagari digits, negation, code-mixing) can produce real divergence — report it, do not average it away |
| Intersectional | Gender × language, district × gender, only where each cell has ≥5 volunteers | Cell counts table | Otherwise mark `NOT EVALUATED`; do not extrapolate from marginal rates (F6) |
| Method-level | **Adversarial/blinding analogue:** after fixing the fixture, run the whole pipeline twice with only the audit attribute flipped and compare output payload hashes | Any difference in roster or card output is a review flag, not an automatic pass | Adapted from F7's adversarial test; with n=10 use counts and a permutation test only if repeated trials exist, never a significance claim |

Protected attributes are read only by the audit module; a code-review check greps the solver and confirms no gender/caste/religion/language term appears in constraints or objective. Report results as "no difference observed in 10 synthetic twin pairs" — F5 says zero risk of bias is impossible, so "bias-free" must never appear.

**Responsible-AI checklist — each row is a click/command a judge can verify in the built product.** Status column is to be filled with `PASS`, `FAIL` or `NOT BUILT` during the final demo rehearsal; nothing is pre-marked PASS here.

| # | Check (NIST characteristic) | Concretely testable in the product | Evidence to paste into the report |
|---|---|---|---|
| 1 | Valid & reliable | Run the one command below; all 10×4 rows exist, `solver_status` is shown for every row, versions printed | Command + tail of `eval_report.json`, `generated_by`, `n_tasks`, `n_volunteers` |
| 2 | Safe | In the UI mark a volunteer unavailable and another below the skill threshold; confirm neither is ever assigned; force an infeasible instance and confirm an explicit message, not a bogus roster | Screenshot of the infeasible state; R1's observed `INFEASIBLE` + stale `Value()` bug is the regression test |
| 3 | Secure & resilient | Click "drop volunteer" for each primary on the demo roster; every MUST role stays covered; re-run the hash-chain tamper proof; re-run R2 redaction proof | `SINGLE_DROPOUT_TESTED / RECOVERED` output, tamper `stored=… recomputed=…` line, redaction counts |
| 4 | Accountable & transparent | Open a pick's reason: it must quote skill level, distance, exposure and mentor/standby facts from solver data; open the ledger and see draft → flag → confirm/correct with actor and hash | Two screenshots (reason, ledger) + exported JSON; no LLM-authored reason string |
| 5 | Explainable & interpretable | Click "why not X?"; the app re-solves with X forced and shows objective delta plus displaced volunteers, or "no feasible roster includes X" | Counterfactual panel screenshot; blocked case shown as a separate example |
| 6 | Privacy-enhanced | Inspect the exact payload sent to the LLM with `SEWA_LLM_MODE=replay`: run the R2 regex set and require zero Aadhaar/PAN/phone/email matches; portable export uses `urn:uuid` only | Redaction count lines from `r2_tests.py`; export JSON with no raw identifier |
| 7 | Fair with harmful bias managed | Run the gender/district/language twin tests above; confirm by code grep that no protected attribute enters the solver | Counts table, `INSUFFICIENT_N` labels, grep output |
| 8 | Human oversight | Confirm the UI blocks final roster approval until the organiser clicks approve, ambiguous briefs (`needs_review=true`) never reach CP-SAT, and a card cannot read "verified" until a distinct host confirms | Three UI states captured; ledger `confirm` actor differs from card author |
| 9 | Children | Age gate on the demo path refuses under-18 volunteers and shows the guardian-consent notice; no real minor's data anywhere | Screenshot of the blocked state; R3's DPDP s.9 / Rule 10 note in the report |
| 10 | Credential honesty | The portable record displays an "unsigned / synthetic — not a verifiable credential" badge and has no `proof` field | Export screenshot + JSON check from R3 |
| 11 | Reproducible | A fresh shell runs the one command and reproduces the same rows/CI within stated tolerance; fixture hash matches | Command + output + SHA-256 pasted, not paraphrased |

**What to put in the README so judges can reproduce with one command (PROPOSED text for the README owner; not implemented by this research lane).** `CONTEXT.md:17` already specifies the entry point; the block below should be added under `## Run`, with the honest status line retained until `backend/eval/harness.py` is implemented:

````md
### Reproduce the evaluation (synthetic data only)

One command, offline, from the repository root:

```sh
cd backend ; ..\.venv\Scripts\python -X utf8 -m eval.harness --out eval_report.json
```

Prints pasted artifacts, not prose: `n_tasks`, `n_volunteers`, all `rows`
(task x method), `summary`, `ci95` (seeded 95% percentile bootstrap over the
10 task-level scores), and `misses` (tasks where we did not beat a baseline).
Every result is labelled `synthetic: true`. Environment used in the proof:
Python 3.13.14, ortools 9.15.6755, seed 20261118, 10,000 bootstrap resamples.
CI numbers are descriptive intervals over 10 synthetic tasks, not performance
claims about real volunteers. `-X utf8` is required on Windows for Hindi text.

Check the pinned versions with:

```sh
cd backend ; ..\.venv\Scripts\python -m pip show ortools
```

STATUS: this is the target command. As of 2026-11-18 `backend/eval/harness.py`
raises `NotImplementedError`; do not quote evaluation numbers until a fresh run
of this command has printed them and the fixture SHA-256 is recorded here.
````

**INFERENCE — implementation order for the build lanes.** (1) Freeze fixtures and hash; (2) implement the shared metric function from `schemas.py:196-217` and call it for all four methods; (3) add seeded paired bootstrap to `EvalReport.ci95`; (4) add the twin-swap audit module reading protected attributes *only* from a separate audit fixture; (5) wire the checklist rows into `PROJECT_REPORT.md` with blank status cells; (6) only then add README numbers from a fresh run. Steps 1–3 are prerequisites for any claim in the demo video.

## Risks

1. **n=10 cannot carry inference.** The measured interval [0.7, 0.95] is 0.25 wide on a 0–1 scale; method differences, subgroup parity and κ are descriptive at best (F1, F2, F6). Any slide saying "fair", "unbiased" or "better than manual" from this set is an overclaim.
2. **Synthetic twin tests can be tautological.** If the twin swap changes nothing because the attribute was never a solver input, the test passes by construction — that is still worth showing as a design fact, but it is not evidence about real-world bias (F5, F7).
3. **Proxy baseline mislabelled as reality.** `manual_greedy` is our code, not an observed organiser workflow. Calling it "today's baseline" would manufacture a comparison we never measured.
4. **Protected-attribute collection.** Adding gender/district/language to volunteer records for auditing creates new sensitive data. In this prototype they must stay synthetic and out of exports; DPDP obligations for real children's data are out of scope (R3).
5. **Gini/cap confusion.** The exposure cap and the Gini are different objectives; R1 measured Gini *rising* under the cap. Reporting only one invites a false fairness story.
6. **Timing variance.** Re-running identical scripts printed different wall times; a single fast number in a video is not a scalability result, and ortools/Python versions must be pinned (F9).
7. **Bootstrap misuse.** Bootstrapping extremes, subgroup cells with n<5, or unpaired method comparisons violates the caveats in F1/F2; percentile intervals are first-order accurate, not a guarantee of nominal coverage at n=10.
8. **Harness is a stub.** `backend/eval/harness.py` raises `NotImplementedError` as read on 2026-11-18. The README block is a target; quoting its numbers before a real run would invent results.
9. **Checklist theatre.** A row marked PASS from a screenshot without the underlying command output is not verification; NIST's TEVV guidance and ACM's "exercisable + evidence of verification" definition require the artifact, not the adjective (F4, F8).
10. **Source access limits.** The NIST Dataplot bootstrap page opened only as a revision-history stub and `https://dl.acm.org/journal/tsas/reproducibility` returned HTTP 502; no claim here depends on either. The reproducible-results paragraph relies on the opened ACM badging pages instead.

## Sources

1. 1.3.3.4. Bootstrap Plot — NIST/SEMATECH e-Handbook of Statistical Methods — https://www.itl.nist.gov/div898/handbook/eda/section3/bootplot.htm — accessed 2026-11-18.
2. Ian Soboroff, Computing Confidence Intervals for Common IR Measures — 6th EVIA Workshop, 9 Dec 2014, Tokyo — https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=917303 — accessed 2026-11-18.
3. AI Risk Management Framework — NIST — https://www.nist.gov/itl/ai-risk-management-framework — released 26 Jan 2023; page notes revision in progress; accessed 2026-11-18.
4. 3 AI Risks and Trustworthiness (AI RMF 1.0 excerpt) — NIST AIRC — https://airc.nist.gov/airmf-resources/airmf/3-sec-characteristics/ — accessed 2026-11-18.
5. 5 AI RMF Core (AI RMF 1.0 excerpt) — NIST AIRC — https://airc.nist.gov/airmf-resources/airmf/5-sec-core/ — accessed 2026-11-18.
6. NIST SP 1270, Towards a Standard for Identifying and Managing Bias in Artificial Intelligence — https://nvlpubs.nist.gov/NISTpubs/SpecialPublications/NIST.SP.1270.pdf — March 2022; accessed 2026-11-18.
7. Model Cards for Model Reporting (Mitchell et al.) — https://ar5iv.labs.arxiv.org/html/1810.03993 — FAT* '19, 2019; accessed 2026-11-18.
8. Fairness and Machine Learning: Limitations and Opportunities — https://fairmlbook.org/ — MIT Press 2023, page last updated 2023-11-10; accessed 2026-11-18.
9. Testing discrimination in practice (ch. 7 of #8) — https://fairmlbook.org/testing.html — accessed 2026-11-18.
10. Artifact Review and Badging, Version 1.1 — ACM — https://www.acm.org/publications/policies/artifact-review-and-badging-current — 24 Aug 2020; accessed 2026-11-18.
11. Artifact Review and Badging, Version 1.0 (archive) — ACM — https://www.acm.org/publications/policies/artifact-review-badging — revised 24 Aug 2020; accessed 2026-11-18.
12. Ten Simple Rules for Reproducible Computational Research (Sandve et al.) — PLOS Comput Biol 9(10):e1003285 — https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003285 — 24 Oct 2013; accessed 2026-11-18.
13. Common pitfalls and recommended practices — scikit-learn 1.9.1 documentation — https://scikit-learn.org/stable/common_pitfalls.html — accessed 2026-11-18.
14. Datasheets for Datasets (Gebru et al.) — arXiv:1803.09010 — https://arxiv.org/abs/1803.09010 — submitted 23 Mar 2018, v8 1 Dec 2021, CACM Dec 2021; accessed 2026-11-18.
15. BOOTSTRAP PLOT (Dataplot reference) — NIST — https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/bootplot.htm — accessed 2026-11-18; page yielded only a revision-history stub, not used for any claim.

Local files read (not URLs): `docs/COMMON.md`, `docs/lanes/C-research/TASK.md`, `docs/research/R1-optimization.md`, `docs/research/R2-nlp-hindi.md`, `docs/research/R3-credentials-privacy.md`, `backend/app/schemas.py`, `backend/eval/harness.py`, `CONTEXT.md`, `README.md` — all read 2026-11-18.

Research counts: 4 web-search queries; 16 distinct URLs attempted; 15 pages opened (14 returned substantive text, 1 returned only a revision-history stub); 1 fetch failed with HTTP 502; 5 independent primary publishers/institutions (NIST, ACM, scikit-learn/Probabl, PLOS, MIT Press/arXiv authors).

UNRESOLVED / NOT FOUND: (i) `https://dl.acm.org/journal/tsas/reproducibility` returned HTTP 502 on extraction; no claim relies on it. (ii) No externally published evaluation numbers for SewaCircle exist — the only measured numbers in this file are from the local bootstrap run pasted in F3. (iii) No observed manual/organiser baseline was found in the repository; `manual_greedy` remains a defined proxy. (iv) The evaluation harness is not yet implemented; the one-command README block is a target, not a verified current capability.
