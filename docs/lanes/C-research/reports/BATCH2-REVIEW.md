# BATCH 2 REVIEW — Lane C (research)

Reviewer role: Batch 2 reviewer, Lane C.
Review date: 2026-11-19 01:25 IST (+0530).
Method: re-ran every claimed measurement myself on the files as they exist on disk; pasted the command and its real stdout verbatim; compared against the number claimed in the deliverable. No web access, no packages installed, no source files modified. Only file written by this review: `docs/lanes/C-research/reports/BATCH2-REVIEW.md`.

Interpreter for all runs (verified): `C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe` → `Python 3.13.14`.

| Item | Claim under test | Verdict |
|---|---|---|
| R4 | `up_districts.json` has exactly 20 districts, all inside lat 23.5..30.5 / lon 77..84.5, each with a coordinate source | **PASS** |
| R5 | 10-segment demo script summing to 180 seconds | **PASS** |
| R6 | n=10 bootstrap, 10000 resamples, seed 20261118, point 0.825, CI95 [0.70,0.95] | **PASS** |

---

## Item 1 — R4: 20 districts, all in UP bbox, each sourced

Claimed in `docs/research/R4-up-realism.md:3` ("contains exactly 20 real Uttar Pradesh district names with one WGS84 point each… Each JSON row carries the same shared `source` URL plus a per-district `source_record_id`") and in `docs/lanes/C-research/reports/R4-report.md:6,229`.

Command run (from `C:/Users/shubh/Projects/sewacircle`):

```
.venv/Scripts/python.exe -c "import json;d=json.load(open('docs/research/up_districts.json',encoding='utf-8'));rows=d['districts'];print('FILE','docs/research/up_districts.json');print('ROWS',len(rows));print('BBOX','lat 23.5..30.5 lon 77..84.5');oob=[r['name'] for r in rows if not (23.5<=r['lat']<=30.5 and 77.0<=r['lon']<=84.5)];print('OUT_OF_BBOX',len(oob),oob);ms=[r['name'] for r in rows if not (r.get('source') or '').strip()];print('MISSING_SOURCE',len(ms),ms);mr=[r['name'] for r in rows if not (r.get('source_record_id') or '').strip()];print('MISSING_SOURCE_RECORD_ID',len(mr),mr);print('UNIQUE_NAMES',len(set(r['name'] for r in rows)));print('LAT_MIN',min(r['lat'] for r in rows),'LAT_MAX',max(r['lat'] for r in rows));print('LON_MIN',min(r['lon'] for r in rows),'LON_MAX',max(r['lon'] for r in rows))"
```

Full real stdout:

```
FILE docs/research/up_districts.json
ROWS 20
BBOX lat 23.5..30.5 lon 77..84.5
OUT_OF_BBOX 0 []
MISSING_SOURCE 0 []
MISSING_SOURCE_RECORD_ID 0 []
UNIQUE_NAMES 20
LAT_MIN 24.385 LAT_MAX 29.897
LON_MIN 77.486 LON_MAX 84.033
EXIT_CODE=0
```

Verdict: **PASS**.
- 20 rows (claim: exactly 20) — matches.
- 0 rows outside the stated bbox; observed extremes lat 24.385–29.897, lon 77.486–84.033 sit strictly inside 23.5–30.5 / 77–84.5.
- 0 rows missing `source`; 0 rows missing `source_record_id`.
- 20 unique names, so the count is not padded with duplicates.

### Item 1b — R4 corroboration: are the coordinates actually verbatim from the source?

Verdict text in R4 says values are "copied verbatim from the source; no coordinates were computed or guessed." A row can carry a `source` string and still have invented numbers, so I checked the numbers against the cached source file that exists on disk (`…/cache/scratch/up_source_all_district.json`, 635 rows, the file R4's Command A/B parsed).

Command:

```
.venv/Scripts/python.exe -c "import json;src=json.load(open('C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/up_source_all_district.json',encoding='utf-8'));ours=json.load(open('docs/research/up_districts.json',encoding='utf-8'))['districts'];byid={r['id']:r for r in src};... joined per row on source_record_id, compared geo.lat/geo.lon/name.en"
```

Full real stdout:

```
CHECKED 20
ID_NOT_IN_SOURCE 0 []
LAT_MISMATCH 0 []
LON_MISMATCH 0 []
NAME_MISMATCH 0 []
```

Verdict: **PASS** — all 20 `source_record_id` values resolve to a real record in the source, and lat, lon and name match that record exactly. The "verbatim, nothing computed" claim holds for the delivered slice.

Also checked, since R4-report asserts it (`R4-report.md:229-230`):

```
TAXONOMY_ROWS 24 OBSERVED 21 INFERRED 3 SUM 24
INFERRED_IDS ['first_aid', 'crowd_safety', 'translation']
```

The 24-entry skill taxonomy and the "21 observed + 3 inferred = 24" split are both exactly as claimed. **PASS.**

---

## Item 2 — R5: 10-segment demo script summing to 180 seconds

Claimed in `docs/research/R5-demo-ux.md:62` (heading "Improved 3-minute demo script (segments sum to 180 s)"), table at lines 66–77, and restated at line 114 ("Ten segments leave little slack").

Command run (script pre-existed, 1,069 bytes, mtime 2026-11-18 23:40; not recreated):

```
.venv/Scripts/python.exe C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r5_timing_proof.py
```

Full real stdout:

```
 1. Hook: today's manual roster vs our baseline             00:00-00:15 seconds= 15 cumulative= 15
 2. Hindi task in                                           00:15-00:35 seconds= 20 cumulative= 35
 3. Roles extracted                                         00:35-00:55 seconds= 20 cumulative= 55
 4. CP-SAT roster with reasons                              00:55-01:25 seconds= 30 cumulative= 85
 5. Fairness toggle                                         01:25-01:40 seconds= 15 cumulative=100
 6. Drop-a-volunteer heal                                   01:40-02:00 seconds= 20 cumulative=120
 7. Why-not-X counterfactual                                02:00-02:15 seconds= 15 cumulative=135
 8. Contribution card + rules + host confirm                02:15-02:40 seconds= 25 cumulative=160
 9. Hash-chain ledger + export                              02:40-02:55 seconds= 15 cumulative=175
10. Close: measured outcome + reproducibility               02:55-03:00 seconds=  5 cumulative=180
TOTAL_SECONDS=180
PROOF OK: parsed demo segments sum to 180 seconds
EXIT_CODE=0
```

Verdict: **PASS**.
- Exactly 10 segments parsed from the actual markdown table (script asserts `len(rows) == 10`).
- Sum is 180 s (claim: 180 s).
- Stronger than the claim: each row's written clock window equals its stated seconds, windows are contiguous with no gaps or overlaps, and the last segment ends at exactly 03:00. The durations are internally consistent, not just arithmetically summed.
- Per instruction, any wall-clock timing variance in a live rehearsal would be variance, not mismatch; this proof parses the written plan and is deterministic, so no variance applies.

---

## Item 3 — R6: seeded n=10 bootstrap, 10000 resamples, seed 20261118, point 0.825, CI95 [0.70,0.95]

Claimed in `docs/research/R6-eval-responsible-ai.md:11` (F3: "point estimate of 0.825 and a 95% percentile interval [0.7, 0.95]"), with the pasted output block at lines 13–24, and prescribed at line 73 ("seeded, 10,000 resamples, percentile endpoints").

Command run (script pre-existed, 1,027 bytes, mtime 2026-11-18 23:34; not recreated):

```
.venv/Scripts/python.exe C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r6_bootstrap_ci.py
```

Full real stdout:

```
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

Verdict: **PASS** — every element of the claim reproduces: n=10, 10000 resamples, seed 20261118, point 0.825, CI95 low 0.7, high 0.95. The output also matches the block pasted in R6 F3 line for line.

### Item 3b — is the CI computed, or hardcoded?

A script that `print`s constants would pass the check above, so I re-implemented the bootstrap independently (same seed, same synthetic array, 10000 resamples, indices 250 and 9749) and recomputed:

```
INDEP_POINT 0.825
INDEP_LO 0.7 INDEP_HI 0.95
DISTINCT_MEANS [0.55, 0.575, 0.6, 0.625, 0.65, 0.675, 0.7, 0.725, 0.75, 0.775, 0.8, 0.825, 0.85, 0.875, 0.9, 0.925, 0.95, 0.975, 1.0]
SUM_ARRAY 8.25
```

Verdict: **PASS** — reproduced from the data, not from a literal. The point estimate is the plain mean of the array (8.25 / 10 = 0.825), and 0.7 and 0.95 are members of the reachable mean set for this array, so both endpoints are attainable values rather than impossible ones. Independent check, not a trust in the shipped script.

Environment claims in the same file also hold: `PY_VERSION 3.13.14`, `ORTOOLS 9.15.6755` (`R6-eval-responsible-ai.md:160`).

---

## Secondary arithmetic I checked while reviewing

R5 line 42 asserts "15 MB in 180 s allows 666667 bit/s (0.667 Mbps); 15 MiB allows 699051 bit/s (0.699 Mbps)". Recomputed:

```
BITRATE_15MB_180s 666667 bps = 0.667 Mbps
BITRATE_15MiB_180s 699051 bps = 0.699 Mbps
```

Both figures are exact. **PASS.**

R4 line 3 and `R4-report.md:235` claim the coordinate source has 69 UP rows. Counted from the cached source:

```
SOURCE_TOTAL 635
UP_ROWS 69
```

69 confirmed (of 635 total rows in `all-district.json`). **PASS.**

---

## OBSERVATIONS (documentation drift, not counted as mismatches)

1. **R6's `harness.py` citation no longer resolves.** `R6-report.md:426` and F12 state `backend/eval/harness.py` "is a `NotImplementedError` stub". On disk today `grep -n "NotImplementedError" backend/eval/harness.py` returns nothing; the file is a working implementation (6,312 bytes). Cause is file movement after authoring, not a bad claim: R6 was written 2026-11-18 23:46, and `git log -1` shows `harness.py` last committed 2026-11-19 01:13:17 (`58f21ff`) and `schemas.py` 2026-11-19 01:03:06 (`a59f0f7`). Same cause for the shifted line references: F12 cites `schemas.py:319-327` for `EvalReport`, which now sits at `schemas.py:347-355`. Recommend Lanes cite symbols (`class EvalReport`) rather than line numbers in files other lanes still own.

2. **R6's prescribed bootstrap settings are not what the harness implements.** R6 line 73 and the risk table prescribe "seeded, 10,000 resamples, percentile endpoints, seed 20261118" for `EvalReport.ci95`. `backend/eval/harness.py:23` reads `BOOT_N, BOOT_SEED = 1000, 7`, and its docstring (line 5) says "1000 resamples, seed 7". R6's own proof script does use 10000 / 20261118, so R6 is internally honest; the gap is between the research recommendation and the build implementation. If any README ever publishes a CI, it must quote the harness's 1000/7 settings, not R6's 10000/20261118 — otherwise the published number will not be reproducible from the committed code. Flagging for the owning build lane.

3. **R6 numbers are explicitly synthetic and are presented that way.** The array is `[1.00, 0.75, 1.00, 0.50, 1.00, 0.75, 1.00, 0.75, 0.50, 1.00]`; the script prints "SYNTHETIC DATA ONLY" and the deliverable says "descriptive estimate from 10 synthetic tasks; NOT a production benchmark". No overclaim observed in the F3 text — the interval width (0.25) is called out as the honest headline rather than the 0.825.

---

## UNRESOLVED — claims I could not test

Each entry names a claim in the Batch 2 deliverables whose truth depends on an external document this offline review cannot open. None of them affects the three verdicts above; all are tagged FACT in the deliverables with a URL, and Batch 1 already audited URL liveness.

**R4 (`docs/research/R4-up-realism.md`)**

1. Wikipedia lists **75 districts in 18 divisions** for UP (line 3, and the 69-vs-75 comparison at line 61). Reason: external page `en.wikipedia.org/wiki/Uttar_Pradesh`, not on disk; I verified only the 69-row side of the comparison.
2. Kanpur Dehat **6 tehsils / 10 development blocks** and the six tehsil and ten block names (lines 6, 24). Reason: six `kanpurdehat.nic.in` pages, none cached locally.
3. Lucknow **8 development blocks** and **5 tehsils**, and the page footer date `27.01.2026` (lines 7, 24). Reason: two `lucknow.nic.in` pages, not on disk.
4. Varanasi **3 sub-divisions / 8 development blocks**, **3 tehsils**, and block-level education office names (lines 8, 24). Reason: three `varanasi.nic.in` pages, not on disk.
5. Gorakhpur **7 tehsils, 19 blocks, 191 Nyay Panchayats, 1354 Gram Sabhas**, plus the **20-row** blocks table and the 19-vs-20 inconsistency (lines 9, 24, 62). Reason: two `gorakhpur.nic.in` pages, not on disk. This is the one factual conflict the deliverable itself leaves open; I could not adjudicate it offline and did not try to.
6. YAS Annual Report 2013-14 figures: **~100 student volunteers per NSS unit**, **15 Regional Centres** including Lucknow, **28 zonal offices**, **2 National Youth Corps volunteers per block** (line 11). Reason: the audit's extracted text (`commence_267647.txt` in scratch) is not the YAS report and I did not re-extract the PDF in this pass.
7. MY Bharat / NSS **15–29 age band** and **15 Indian languages** (line 13). Reason: `digitalindia.gov.in` and `negd.gov.in` PDF, not on disk.
8. Census 2011 Table C-16 mother-tongue categories, and Wikipedia language shares (**Bhojpuri ~11%, Urdu 5.4%, Punjabi 0.3%, Bengali 0.1%**) (line 15). Reason: Census catalogue page and two Wikipedia pages, not on disk.
9. Source repository metadata **CC-BY-4.0, last updated 2026-08-20** (lines 3, 71). Reason: GitHub repository page; only the raw JSON is cached, and the JSON does not carry a licence field I could check.

**R5 (`docs/research/R5-demo-ux.md`)**

10. Google 2024 Solution Challenge **Demo Day of 10 teams, three top prizes, one People's Choice**, with Spoon Share and Saheli named (line 13). Reason: `blog.google` post, not on disk. Note this is a *different* "10" from the 10 demo segments; no confusion in the deliverable.
11. Playwright documentation does **not guarantee a bitrate** (line 42). Reason: external doc page, not cached. The arithmetic half of that sentence I did verify (above).
12. WCAG 2.2 recommendation date **2024-12-12** and the NN/G heuristic article numbering in the sources table (lines 131, 134). Reason: `w3.org` and `nngroup.com`, not on disk.

**R6 (`docs/research/R6-eval-responsible-ai.md`)**

13. NIST/SEMATECH e-Handbook: bootstrap resamples **with replacement**, **500 subsamples usually sufficient**, unsuitable for range/extreme statistics (F1). Reason: `itl.nist.gov` page, not on disk.
14. Soboroff (EVIA 2014): **5,000 resamples → 250th and 5,750th ordered values**, empirical coverage **0.919 nominal-0.95**, "more topics → tighter intervals" (F2). Reason: NIST publication PDF, not on disk.
15. NIST AI RMF: seven trustworthiness characteristics and Core items **Measure 2.1, 2.5, 2.6, 2.10, 2.11, 3.3** (F4). Reason: three `nist.gov` / `airc.nist.gov` pages, not on disk.
16. NIST SP 1270 quotes — "not possible to achieve zero risk of bias", "the most accurate model is not necessarily the one with the least harmful impact" (F5). Reason: `nvlpubs.nist.gov` PDF, not on disk.
17. The claim that `dl.acm.org/journal/tsas/reproducibility` returned **HTTP 502** and that the NIST Dataplot page was a **revision-history stub** (line 188). Reason: negative results of a past fetch; I cannot re-verify a 502 offline and did not browse.

---

## Counting

Three claimed items were tested (R4 districts/bbox/sourcing, R5 10×180 s, R6 bootstrap figures). All three reproduce exactly on re-run. No claimed number in Batch 2 failed. Two documentation-drift observations are recorded above and deliberately not counted as mismatches, because in both cases the cited file was legitimately changed by another lane after R6 was authored — the claims were true when written and are stale, not false.

MISMATCHES: 0
