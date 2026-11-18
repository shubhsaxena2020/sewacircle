# Batch 1 proof re-run review — Lane C / R6

Date 2026-11-18. Reviewer duty from `docs/lanes/C-research/TASK.md`: independently re-run the Batch 1 proof scripts and compare real output against the numbers claimed in the Batch 1 deliverables (`docs/research/R1-optimization.md`, `R2-nlp-hindi.md`, `R3-credentials-privacy.md`) and their lane reports.

**Integrity statement.** All output below is verbatim from commands actually executed on 2026-11-18 with `C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe` (Python 3.13.14, ortools 9.15.6755). Nothing was retyped from the original reports. All fixture people, IDs, numbers and text are SYNTHETIC; no real person or minor.

**Driver command actually run** (one shell call, five scripts in sequence; the driver printed the `===== COMMAND:` headers and `EXIT_CODE` lines):

```sh
PY=C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe; S=C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch; for f in r1_base.py r1_robust.py r1_counterfactual.py r2_tests.py r3_hashchain_demo.py; do echo "===== COMMAND: \"$PY\" \"$S/$f\" ====="; "$PY" "$S/$f" 2>&1; echo "EXIT_CODE=$?"; echo; done
```

**Pre-check command and real output** (all five scripts present; two extra scripts also found):

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

## Re-run 1 — R1 base objective

Command: `C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r1_base.py`

```text
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
```

**Verdict: PASS.** Claimed base objective `36.0` — re-run printed `OBJECTIVE_VALUE 36.0`. Status `OPTIMAL (code=4)` and the roster match `R1-optimization.md` lines 91–99. **Variance note (not a mismatch):** the original R1 output printed `WALL_TIME_SECONDS 0.0134`; the re-run printed `0.0203`. R1 presents this as a timing from "our run", not an invariant; timings must be re-measured, never quoted as a benchmark.

## Re-run 2 — R1 dropout robustness

Command: `C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r1_robust.py`

```text
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
```

**Verdict: PASS.** Claimed `4 RECOVERED 4`, score `1.0` with standby vs `0.0` without — all three lines printed verbatim. Objective `161.0` also matches R1. **Variance note:** R1 printed `WALL_TIME_SECONDS 0.021`; re-run printed `0.0097`.

## Re-run 3 — R1 counterfactual

Command: `C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r1_counterfactual.py`

```text
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
```

**Verdict: PASS.** Claimed `OBJECTIVE_DELTA 10.0` and V3 displaced — both printed. Base/forced rosters and `ADDED ['V7']` match R1 lines 218–226.

## Re-run 4 — R2 PII regexes, negation probes and schema validation

Command: `C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r2_tests.py`

```text
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
```

**Verdict: PASS.** Claimed PII counts (AADHAAR 3, PHONE 3, PAN 1, EMAIL 1, NAME 2, ADDRESS 1, merged spans 11), all six negative controls at 0, and schema `strict-shape problems: NONE -> PASS` with three `REJECT` cases — all reproduced exactly as printed in `R2-nlp-hindi.md` lines 18–77. The `verhoeff=PASS` on the all-9s synthetic number and `FAIL` on the wrong one also match; R2 explicitly warns these are format signals, not identity verification.

## Re-run 5 — R3 hash-chain tamper detection and OB3 field check

Command: `C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r3_hashchain_demo.py`

```text
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

**Verdict: PASS.** Claimed tamper detection `stored=ce1159ea65ef1361 recomputed=145259e2641c7adf` printed verbatim; `verify original: ok=True`, `verify tampered: ok=False` and all `missing=[]` lines match `R3-credentials-privacy.md` lines 38–53. `proof field present: False` confirms R3's honest "unsigned / not a verifiable credential" position.

## Summary table

| Script | Claim checked | Re-run output | Verdict |
|---|---|---|---|
| `r1_base.py` | base objective 36.0 | `OBJECTIVE_VALUE 36.0` | PASS |
| `r1_robust.py` | `4 RECOVERED 4`, score 1.0 vs 0.0 | all three lines printed | PASS |
| `r1_counterfactual.py` | delta 10.0, V3 displaced | `OBJECTIVE_DELTA 10.0`, `DISPLACED ['V3']` | PASS |
| `r2_tests.py` | PII counts + schema PASS | exact counts, `VALID : PASS`, 3 rejects | PASS |
| `r3_hashchain_demo.py` | stored `ce1159…`, recomputed `145259…` | exact mismatch line | PASS |

**MISMATCHES: none.** All five scripts existed at the exact paths, exited 0, and reproduced the claimed numbers.

**Variance observations (not mismatches).** Two R1 wall-time lines differ from the original pasted outputs (`0.0134` → `0.0203` for base; `0.021` → `0.0097` for robust). These are run-dependent measurements, explicitly presented in R1 as timings from a run; R6 recommends median/max over repeats instead of a single number.

**UNRESOLVED items.**

1. The two extra scripts found in scratch (`r1_fairness.py`, `r1_gini.py`) were **not** part of the delegated five re-runs and were not executed here; their R1 numbers (`OBJECTIVE_VALUE 45.0`, Gini `0.2338` vs `0.3117`) remain unverified by this review. They are cited in R6 only as R1's reported observation, labelled as such.
2. The proof scripts live in the Hermes scratch directory, not in the repository; they are not part of the shipped artifact, so a judge cannot reproduce them from the repo alone. The R6 README recommendation addresses this for the harness, not for these Batch 1 scratch scripts.
3. No independent second implementation was run; this review verifies repeatability (same team, same setup), not reproducibility in the ACM sense — see R6 F8.
4. `backend/eval/harness.py` remains a `NotImplementedError` stub; the Batch 1 proofs do not constitute the product-level evaluation harness.
