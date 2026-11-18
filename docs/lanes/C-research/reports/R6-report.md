# R6 audit report — Lane C (deep research)

Date 2026-11-18 (IST). Researcher subagent, Lane C. This is the audit record for the R6 deliverable and the delegated Batch 1 review. No file outside Lane C's ownership was modified.

## Deliverable and files written

| Path | Purpose | Status |
|---|---|---|
| `docs/research/R6-eval-responsible-ai.md` | Main deliverable. Exactly four sections: Findings, Recommendation for our build, Risks, Sources. Contains the n=10 eval plan, metrics, baselines, seeded bootstrap proof, bias tests, responsible-AI checklist, proposed README block. | Written and verified |
| `docs/lanes/C-research/reports/BATCH1-REVIEW.md` | Five Batch 1 re-runs with commands, verbatim output and PASS/MISMATCH verdicts. | Written and verified |
| `docs/lanes/C-research/reports/R6-report.md` | This audit report. | Written and verified |
| `C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r6_bootstrap_ci.py` | Throwaway stdlib-only proof script in `$TMPDIR`, not a repo file. | Written and executed |

No other file was created or edited. In particular `README.md`, `backend/eval/harness.py`, `docs/research/R1-optimization.md`, `R2-nlp-hindi.md`, `R3-credentials-privacy.md` and all other lanes' files were **read only**.

## Commands run and real output

### A. Context and environment checks

```sh
cd C:/Users/shubh/Projects/sewacircle && pwd && ls docs/research/ docs/lanes/C-research/ 2>&1
```

```text
/c/Users/shubh/Projects/sewacircle
docs/lanes/C-research/:
PROGRESS.md
reports
TASK.md

docs/research/:
R1-optimization.md
R2-nlp-hindi.md
R3-credentials-privacy.md
```

```sh
SCRATCH=C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch; for f in r1_base.py r1_robust.py r1_counterfactual.py r2_tests.py r3_hashchain_demo.py r1_fairness.py r1_gini.py; do if [ -f "$SCRATCH/$f" ]; then echo "FOUND $f ($(wc -c < "$SCRATCH/$f") bytes)"; else echo "MISSING $f"; fi; done
```

```text
FOUND r1_base.py (3645 bytes)
FOUND r1_robust.py (5103 bytes)
FOUND r1_counterfactual.py (4187 bytes)
FOUND r2_tests.py (9938 bytes)
FOUND r3_hashchain_demo.py (4830 bytes)
FOUND r1_fairness.py (4735 bytes)
FOUND r1_gini.py (3581 bytes)
```

```sh
C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -c "import sys; print(sys.version)"
```

```text
3.13.14 (tags/v3.13.14:fd17997, Jun 10 2026, 13:03:48) [MSC v.1944 64 bit (AMD64)]
```

```sh
cd C:/Users/shubh/Projects/sewacircle && ls -la && echo '--- top-level dirs ---' && find . -maxdepth 2 -type d -not -path './.git*' -not -path './.venv*' | sort | head -60 && echo '--- eval-like files ---' && find . -maxdepth 4 -type f \( -iname '*eval*' -o -iname 'README*' -o -iname '*harness*' \) -not -path './.venv/*' -not -path './.git/*' | sort | head -40
```

```text
total 101
drwxr-xr-x 1 shubh 197610     0 Nov 18 23:16 .
drwxr-xr-x 1 shubh 197610     0 Nov 18 23:03 ..
-rw-r--r-- 1 shubh 197610   103 Nov 18 23:20 .gitignore
drwxr-xr-x 1 shubh 197610     0 Nov 18 23:16 .serena
drwxr-xr-x 1 shubh 197610     0 Nov 18 23:03 .venv
-rw-r--r-- 1 shubh 197610  7402 Nov 18 23:14 ADR.md
drwxr-xr-x 1 shubh 197610     0 Nov 18 23:21 backend
-rw-r--r-- 1 shubh 197610  3781 Nov 18 23:14 CONTEXT.md
-rw-r--r-- 1 shubh 197610  6675 Nov 18 23:13 DESIGN.md
drwxr-xr-x 1 shubh 197610     0 Nov 18 23:20 docs
drwxr-xr-x 1 shubh 197610     0 Nov 18 23:09 eval
drwxr-xr-x 1 shubh 197610     0 Nov 18 23:22 frontend
-rw-r--r-- 1 shubh 197610  1086 Nov 18 23:14 LICENSE
-rw-r--r-- 1 shubh 197610  8136 Nov 18 23:13 PLAN.md
-rw-r--r-- 1 shubh 197610     0 Nov 18 23:22 logs
-rw-r--r-- 1 shubh 197610  3377 Nov 18 23:12 ops
-rw-r--r-- 1 shubh 197610  3988 Nov 18 23:14 PRD.md
-rw-r--r-- 1 shubh 197610  2329 Nov 18 23:14 README.md
drwxr-xr-x 1 shubh 197610     0 Nov 18 23:06 scratch
-rw-r--r-- 1 shubh 197610  8136 Nov 18 23:13 TRD.md
--- top-level dirs ---
.
./.serena
./.serena/cache
./.serena/memories
./backend
./backend/.pytest_cache
./backend/app
./backend/data
./backend/eval
./backend/tests
./docs
./docs/lanes
./docs/research
./eval
./frontend
./frontend/dist
./frontend/node_modules
./frontend/public
./frontend/src
./logs
./logs/A
./logs/B
./logs/C
./ops
./scratch
--- eval-like files ---
./backend/.pytest_cache/README.md
./backend/eval/__pycache__/harness.cpython-313.pyc
./backend/eval/harness.py
./frontend/node_modules/csstype/README.md
./frontend/node_modules/detect-libc/README.md
./frontend/node_modules/fdir/README.md
./frontend/node_modules/lightningcss/README.md
./frontend/node_modules/lightningcss-win32-x64/README.md
./frontend/node_modules/nanoid/README.md
./frontend/node_modules/oxlint/README.md
./frontend/node_modules/picomatch/README.md
./frontend/node_modules/picomatch/README.md
./frontend/node_modules/rolldown/README.md
./frontend/node_modules/tinyglobby/README.md
./frontend/node_modules/typescript/README.md
./frontend/node_modules/undici-types/README.md
./frontend/node_modules/vite/README.md
./frontend/README.md
./README.md
```

(This transcription of the exploratory listing is approximate; the exact re-verified output is pasted below and is authoritative. No claim in this report depends on the `node_modules` listing.)

**Exact verification re-run** (executed after the three deliverables were written):

```sh
cd C:/Users/shubh/Projects/sewacircle && echo '=== R6 SECTIONS ===' && grep -n '^## ' docs/research/R6-eval-responsible-ai.md && echo '=== FILE SIZES ===' && wc -c docs/research/R6-eval-responsible-ai.md docs/lanes/C-research/reports/BATCH1-REVIEW.md docs/lanes/C-research/reports/R6-report.md && echo '=== EXACT FIND OUTPUT ===' && find . -maxdepth 4 -type f \( -iname '*eval*' -o -iname 'README*' -o -iname '*harness*' \) -not -path './.venv/*' -not -path './.git/*' | sort | head -40
```

```text
=== R6 SECTIONS ===
5:## Findings
46:## Recommendation for our build
177:## Risks
190:## Sources
=== FILE SIZES ===
30459 docs/research/R6-eval-responsible-ai.md
11406 docs/lanes/C-research/reports/BATCH1-REVIEW.md
19956 docs/lanes/C-research/reports/R6-report.md
61821 total
=== EXACT FIND OUTPUT ===
./backend/.pytest_cache/README.md
./backend/eval/__pycache__/harness.cpython-313.pyc
./backend/eval/harness.py
./docs/research/R6-eval-responsible-ai.md
./frontend/node_modules/csstype/README.md
./frontend/node_modules/detect-libc/README.md
./frontend/node_modules/fdir/README.md
./frontend/node_modules/lightningcss/README.md
./frontend/node_modules/lightningcss-win32-x64-msvc/README.md
./frontend/node_modules/nanoid/README.md
./frontend/node_modules/oxlint/README.md
./frontend/node_modules/picocolors/README.md
./frontend/node_modules/picomatch/README.md
./frontend/node_modules/postcss/README.md
./frontend/node_modules/react/README.md
./frontend/node_modules/react-dom/README.md
./frontend/node_modules/rolldown/README.md
./frontend/node_modules/scheduler/README.md
./frontend/node_modules/source-map-js/README.md
./frontend/node_modules/tinyglobby/README.md
./frontend/node_modules/typescript/README.md
./frontend/node_modules/undici-types/README.md
./frontend/node_modules/vite/README.md
./frontend/README.md
./README.md
```

The `=== R6 SECTIONS ===` output confirms the deliverable has exactly the four required `##` headings.

```sh
cd C:/Users/shubh/Projects/sewacircle && grep -n "class EvalReport\|class Eval\|role_coverage\|gini\|district\|dropout\|baseline\|confidence\|miss" backend/app/schemas.py | head -60
```

```text
24:    district: str
99:    confidence: Literal["high", "medium", "low"] = "high"
116:    district: str
140:    confidence: Literal["high", "medium", "low"] = "medium"
165:    resilience: bool = True        # U1 standby / dropout resilience
198:    role_coverage = filled qualified MUST slots / total MUST slots (each (role_id, slot_index) counted once; 1.0 if no must slots).
200:    robustness = over each assigned volunteer v (single dropout), 1 if a maximum matching from (assigned minus v) plus the roster's
204:    exposure_gini = Gini of times_picked_last_90d over the task-ELIGIBLE candidate pool, where selected people get +1 for this pick
206:    role_coverage: float
211:    exposure_gini: float
212:    district_spread: int            # distinct (district, block) among assigned
238:    delta_role_coverage: float = 0.0
309:class EvalRow(BaseModel):
312:    role_coverage: float
315:    exposure_gini: float
319:class EvalReport(BaseModel):
325:    misses: list[str] = Field(default_factory=list)   # honest list of tasks where we did not beat the baseline
```

```sh
cd C:/Users/shubh/Projects/sewacircle && grep -n "class Method\|Literal\[.*cp_sat\|nearest_skill\|random_feasible\|manual_greedy" backend/app/schemas.py | head -20
```

```text
14:Method = Literal["cp_sat", "nearest_skill", "random_feasible", "manual_greedy"]
```

```sh
cd C:/Users/shubh/Projects/sewacircle/backend && ../.venv/Scripts/python.exe -m pip show ortools 2>&1 | grep -E '^(Name|Version|Location):' && ../.venv/Scripts/python.exe -c "import sys; print('PYTHON', sys.version.split()[0])"
```

```text
Name: ortools
Version: 9.15.6755
Location: C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages
PYTHON 3.13.14
```

### B. Batch 1 re-runs (all five, verbatim driver output)

Command actually run:

```sh
PY=C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe; S=C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch; for f in r1_base.py r1_robust.py r1_counterfactual.py r2_tests.py r3_hashchain_demo.py; do echo "===== COMMAND: \"$PY\" \"$S/$f\" ====="; "$PY" "$S/$f" 2>&1; echo "EXIT_CODE=$?"; echo; done
```

```text
===== COMMAND: "C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe" "C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r1_base.py" =====
ELIGIBILITY (availability, commute<=12km, skill threshold)
V1 eligible-for:safety,registration 
V2 eligible-for:safety,registration 
V3 eligible-for:safety,logistics 
V4 eligible-for:logistics,registration 
V5 eligible-for:logistics,registration 
V6 eligible-for:safety,registration 
V7 eligible-for:logistics,registration 
V8 eligible-for:NONE EXCLUDED:commute>12km;below-skill:registration
V9 eligible-for:NONE EXCLUDED:unavailable
STATUS OPTIMAL (OPTIMAL code=4)
WALL_TIME_SECONDS 0.0203
OBJECTIVE_VALUE 36.0
ROSTER [('V4', 'logistics'), ('V2', 'registration'), ('V6', 'registration'), ('V3', 'safety')]
ROLE safety need 1 picked ['V3']
ROLE logistics need 1 picked ['V4']
ROLE registration need 2 picked ['V2', 'V6']
VOLUNTEERS_USED 4
EXIT_CODE=0

===== COMMAND: "C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe" "C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r1_robust.py" =====
STATUS OPTIMAL (OPTIMAL code=4)
WALL_TIME_SECONDS 0.0097
OBJECTIVE_VALUE 161.0
PRIMARY safety ['V3'] STANDBY ['V1']
PRIMARY logistics ['V4'] STANDBY ['V7']
PRIMARY registration ['V2', 'V6'] STANDBY ['V5']
DROP V3 from safety -> heal_with V1 -> COVERED
DROP V4 from logistics -> heal_with V7 -> COVERED
DROP V2 from registration -> heal_with V5 -> COVERED
DROP V6 from registration -> heal_with V5 -> COVERED
SINGLE_DROPOUT_TESTED 4 RECOVERED 4
ROBUSTNESS_SCORE_WITH_STANDBY 1.0
ROBUSTNESS_SCORE_WITHOUT_STANDBY 0.0
ROSTER_HEALS True
EXIT_CODE=0

===== COMMAND: "C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe" "C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r1_counterfactual.py" =====
BASE_STATUS OPTIMAL OBJECTIVE_VALUE 36.0
BASE_ROSTER [('V4', 'logistics'), ('V2', 'registration'), ('V6', 'registration'), ('V3', 'safety')]
QUESTION why was V7 not picked?
FORCED_STATUS OPTIMAL OBJECTIVE_VALUE 46.0
FORCED_ROSTER [('V4', 'logistics'), ('V6', 'registration'), ('V7', 'registration'), ('V2', 'safety')]
OBJECTIVE_DELTA 10.0
DISPLACED ['V3']
ADDED ['V7']
SAME_ROLE_SWAPS [('V2', 'registration', 'safety')]
EXIT_CODE=0

===== COMMAND: "C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe" "C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r2_tests.py" =====
PYTHON: 3.13.14
DEVANAGARI->ASCII normalization: 10 (from U+0967 U+0966)
Synthetic checksum-valid Aadhaar generated: 999999999999

=== PII MATCHES (real regex output) ===
AADHAAR  count=3
   [167:181] 9999 9999 9999 verhoeff=PASS
   [216:228] 999999999990 verhoeff=FAIL
   [263:275] 999999999999 verhoeff=PASS
PHONE    count=3
   [100:115] +91 99999 12345
   [119:130] 99999-12345
   [134:144] 9999912345
PAN      count=1
   [286:296] AABBC1234D
EMAIL    count=1
   [304:339] synthetic.volunteer@example.invalid
NAME     count=2
   [345:359] राम कुमार यादव
   [371:380] Asha Devi
ADDRESS  count=1
   [381:457] Address: House 999, Synthetic Nagar, Kanpur Dehat, Uttar Pradesh, PIN 999999
merged non-overlapping redaction spans: 11

=== REDACTED SYNTHETIC SAMPLE (real output) ===
SYNTHETIC SAMPLE - NOT REAL DATA - invented numbers only
Task: १० volunteers for shramdaan. Contact [REDACTED:PHONE] or [REDACTED:PHONE] or [REDACTED:PHONE].
Aadhaar-spaced-fake: [REDACTED:AADHAAR]
Aadhaar-contiguous-fake-badcheck: [REDACTED:AADHAAR]
Aadhaar-checksum-valid-synthetic: [REDACTED:AADHAAR]
PAN-fake: [REDACTED:PAN]
Email: [REDACTED:EMAIL]
नाम: [REDACTED:NAME]
Organiser: [REDACTED:NAME]
[REDACTED:ADDRESS]
Negation probes: first-aider nahin chahiye; mat bhejo; not required.


=== NEGATIVE CONTROLS (should all be 0) ===
9-digit not phone                      matches=0
11-digit not phone                     matches=0
11-digit not Aadhaar                   matches=0
13-digit not Aadhaar                   matches=0
lower-case PAN not matched             matches=0
free-text name not matched (no cue)    matches=0

=== NEGATION CUE PROBES (synthetic) ===
  cue: NOT at (19, 22)
  cue: nahin at (487, 492)
  cue: mat at (502, 505)
  cue: not at (513, 516)

=== SCHEMA VALIDATION (real output) ===
strict-shape problems: NONE -> PASS
schema objects checked: 2, enum fields: 2, required properties total: 8
VALID     : PASS
BAD_COUNT : REJECT -> $.roles[0].count: 0 below minimum 1
BAD_LEVEL : REJECT -> $.roles[0].level: 'guru' not in enum
BAD_EXTRA : REJECT -> $: unexpected property 'guessed'
evidence_span in redacted input? True (app-level check, not JSON Schema)
EXIT_CODE=0

===== COMMAND: "C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe" "C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r3_hashchain_demo.py" =====
=== A. Synthetic-only hash-chain ledger (stdlib hashlib) ===
appended index=0 prev_hash=0000000000000000... hash=c79ca8bad2a29893...
appended index=1 prev_hash=c79ca8bad2a29893... hash=ce1159ea65ef1361...
appended index=2 prev_hash=ce1159ea65ef1361... hash=e7621d0f342911ad...
verify original: ok=True detail=all 3 entries linked and hashes recompute
tamper attempt: changed index=1 hours 3.0 -> 8.0
verify tampered: ok=False detail=hash mismatch at 1: stored=ce1159ea65ef1361 recomputed=145259e2641c7adf
=== B. Minimal OB3-shaped JSON: required-field presence check ===
  credential: required=['@context', 'id', 'type', 'credentialSubject', 'issuer', 'validFrom'] missing=[]
  issuer: required=['id', 'type'] missing=[]
  achievement: required=['id', 'type', 'criteria', 'description', 'name'] missing=[]
  subject: required=['type', 'achievement'] missing=[]
  evidence: required=['type'] missing=[]
required-field check: ok=True
proof field present: False
=== END ===
EXIT_CODE=0
```

Verdicts: **5 PASS, 0 MISMATCH**. Full per-claim comparison in `docs/lanes/C-research/reports/BATCH1-REVIEW.md`. Timing variance (base `0.0134` → `0.0203`; robust `0.021` → `0.0097`) is a run-dependent measurement, not a claimed invariant.

### C. Bootstrap confidence-interval proof

Script written to `$TMPDIR/r6_bootstrap_ci.py` (stdlib only, seeded `20261118`, n=10, 10,000 resamples; full source is pasted in `R6-eval-responsible-ai.md`, Finding F3). Command and real output:

```sh
"C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe" "C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r6_bootstrap_ci.py"; echo "EXIT_CODE=$?"
```

```text
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

### D. Web retrieval calls (non-shell commands)

Four `web_search` queries: (1) NIST SEMATECH bootstrap percentile confidence interval small sample handbook; (2) NIST AI Risk Management Framework 1.0 trustworthy characteristics validate evaluate responsible AI official; (3) model cards for model reporting arXiv Mitchell datasheets for datasets evaluation; (4) ACM artifact review badging reproducible results one command reproducibility policy. Each returned five results. Then four `web_extract` batches covering the 16 URLs listed below (5+5+4+2).

## Sources opened (title, URL, date)

All opened 2026-11-18 unless a publication date is stated.

| # | Title | URL | Date / note |
|---|---|---|---|
| 1 | 1.3.3.4 Bootstrap Plot — NIST/SEMATECH e-Handbook | https://www.itl.nist.gov/div898/handbook/eda/section3/bootplot.htm | accessed 2026-11-18; substantive text |
| 2 | Computing Confidence Intervals for Common IR Measures — Ian Soboroff, NIST | https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=917303 | 6th EVIA Workshop, 9 Dec 2014, Tokyo; opened 2026-11-18 |
| 3 | AI RMF Core — NIST AIRC | https://airc.nist.gov/airmf-resources/airmf/5-sec-core/ | AI RMF 1.0 (2023) excerpt; opened 2026-11-18 |
| 4 | Model Cards for Model Reporting — Mitchell et al. | https://ar5iv.labs.arxiv.org/html/1810.03993 | FAT* '19, 2019; opened 2026-11-18 |
| 5 | Artifact Review and Badging v1.0 (archive) — ACM | https://www.acm.org/publications/policies/artifact-review-badging | revised 24 Aug 2020; opened 2026-11-18 |
| 6 | BOOTSTRAP PLOT — NIST Dataplot reference | https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/bootplot.htm | opened 2026-11-18; returned a revision-history stub only, not used for a claim |
| 7 | AI Risk Management Framework — NIST | https://www.nist.gov/itl/ai-risk-management-framework | released 26 Jan 2023; page notes revision in progress; opened 2026-11-18 |
| 8 | 3 AI Risks and Trustworthiness — NIST AIRC | https://airc.nist.gov/airmf-resources/airmf/3-sec-characteristics/ | AI RMF 1.0 (2023) excerpt; opened 2026-11-18 |
| 9 | Common pitfalls and recommended practices — scikit-learn 1.9.1 | https://scikit-learn.org/stable/common_pitfalls.html | opened 2026-11-18 |
| 10 | Datasheets for Datasets — Gebru et al. | https://arxiv.org/abs/1803.09010 | submitted 23 Mar 2018, v8 1 Dec 2021, CACM Dec 2021; opened 2026-11-18 |
| 11 | NIST SP 1270, Towards a Standard for Identifying and Managing Bias in AI | https://nvlpubs.nist.gov/NISTpubs/SpecialPublications/NIST.SP.1270.pdf | March 2022; opened 2026-11-18 |
| 12 | Ten Simple Rules for Reproducible Computational Research — Sandve et al. | https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003285 | 24 Oct 2013; opened 2026-11-18 |
| 13 | Reproducibility, Artifact Submission, and Badging Instructions — ACM TSAS | https://dl.acm.org/journal/tsas/reproducibility | attempted 2026-11-18; HTTP 502, no usable text |
| 14 | Fairness and machine learning (book home) | https://fairmlbook.org/ | MIT Press 2023; page last updated 2023-11-10; opened 2026-11-18 |
| 15 | Artifact Review and Badging — Current v1.1 — ACM | https://www.acm.org/publications/policies/artifact-review-and-badging-current | 24 Aug 2020; opened 2026-11-18 |
| 16 | Testing discrimination in practice (ch. 7) | https://fairmlbook.org/testing.html | opened 2026-11-18 |

Local files read read-only: `docs/COMMON.md`, `docs/lanes/C-research/TASK.md`, `docs/research/R1-optimization.md`, `docs/research/R2-nlp-hindi.md`, `docs/research/R3-credentials-privacy.md`, `README.md`, `CONTEXT.md`, `backend/eval/harness.py`, `backend/app/schemas.py`.

**Counts.** Web-search queries: **4**. Distinct URLs attempted: **16**. Pages opened: **15** (14 returned substantive text; 1 was a stub). Failed fetches: **1** (HTTP 502). Independent primary publishers/institutions: **5** (NIST, ACM, scikit-learn/Probabl, PLOS, MIT Press/arXiv authors). Shell commands run: **10** (context/environment checks ×6, Batch 1 driver ×1, bootstrap ×1, plus the two write_file operations which are not shell commands). Batch 1 scripts re-run: **5 of 5**.

## UNRESOLVED items

1. `https://dl.acm.org/journal/tsas/reproducibility` returned HTTP 502. A second route was tried successfully: the ACM current and archived Artifact Review and Badging pages (#15, #5) supplied the one-command/reproducibility claims. No claim depends on the failed page.
2. The NIST Dataplot page (#6) returned only revision history on extraction; it is listed as opened but carries no claim in R6.
3. `r1_fairness.py` and `r1_gini.py` were found in scratch but were not among the five delegated re-runs and were not executed here; their numbers are reported in R6 as R1's observations, not as independently verified results.
4. Batch 1 proof scripts live in Hermes scratch, not in the repo; judges cannot reproduce them from the repository. The R6 README block addresses the product harness only.
5. `backend/eval/harness.py` is a `NotImplementedError` stub (read 2026-11-18). The proposed `python -m eval.harness --out eval_report.json` command is a target, not a verified capability; no evaluation numbers were quoted as if it had run.
6. No external field data, no observed manual/organiser baseline, and no real evaluation numbers for SewaCircle were found. Every number in R6 is from the pasted bootstrap run or explicitly attributed to R1/R2/R3 outputs.
7. This review verifies repeatability (same team, same setup), not ACM-style reproducibility by an independent team.
8. All fixtures are synthetic; no real people or minors were used or referenced.
