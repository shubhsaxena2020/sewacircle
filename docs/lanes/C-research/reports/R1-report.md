# R1 audit report — Lane C, SewaCircle

Date of work: 2026-11-18 (IST). Researcher subagent, Lane C (deep research).

## Deliverable

- `docs/research/R1-optimization.md` (path: `C:/Users/shubh/Projects/sewacircle/docs/research/R1-optimization.md`), 25,473 bytes written and verified on disk. Sections are exactly: Findings, Recommendation for our build, Risks, Sources.
- This audit: `C:/Users/shubh/Projects/sewacircle/docs/lanes/C-research/reports/R1-report.md`.

## Files written

- `C:/Users/shubh/Projects/sewacircle/docs/research/R1-optimization.md` (owned by Lane C)
- `C:/Users/shubh/Projects/sewacircle/docs/lanes/C-research/reports/R1-report.md` (owned by Lane C)
- Throwaway scripts/outputs in scratch only (NOT in the repo): `C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r1_probe.py`, `r1_base.py`, `r1_fairness.py`, `r1_robust.py`, `r1_counterfactual.py`, `r1_gini.py`, `r1_fairness_debug.py`, each with a `.out` file.
- Six accidentally-created scratch files were written to the repo root earlier (from a mis-resolved `TMPDIR`) and immediately deleted with the `rm -f` command below; a later `search_files` check found no remaining `r1_probe.py`, `r1_*.py` or `https_developers_google_com_optimization_*.txt` files in the repo. No other lane's files were touched. No installs were performed.

## Commands run and real output

All Python commands used ONLY `C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe` (stdlib + pre-installed ortools).

1. First environment check (failed shell quoting, no Python run):

```text
COMMAND: C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -c "import ortools, sys; from ortools.sat.python import cp_model; print(sys.version); print('ortools', ortools.__version__); print('CpModel', cp_model.CpModel); print('OPTIMAL', cp_model.OPTIMAL, 'FEASIBLE', cp_model.FEASIBLE)"
OUTPUT: /usr/bin/bash: eval: line 5: unexpected EOF while looking for matching `"'
EXIT: 2
```

2. Shell state check:

```text
COMMAND: echo "TMPDIR=$TMPDIR"; echo "PWD=$PWD"
OUTPUT:
TMPDIR=/tmp
PWD=/c/Users/shubh/Projects/sewacircle
```

3. Cleanup of misplaced scratch files:

```text
COMMAND: rm -f /c/Users/shubh/Projects/sewacircle/r1_probe.py /c/Users/shubh/Projects/sewacircle/https_developers_google_com_optimization_*.txt
OUTPUT: (empty)
EXIT: 0
```

4. Correct environment check via probe file:

```text
COMMAND: C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r1_probe.py
OUTPUT:
PYTHON 3.13.14 (tags/v3.13.14:fd17997, Jun 10 2026, 13:03:48) [MSC v.1944 64 bit (AMD64)]
ORTOOLS 9.15.6755
HAS_CPMODEL CpModel
OPTIMAL CpSolverStatus.OPTIMAL FEASIBLE CpSolverStatus.FEASIBLE INFEASIBLE CpSolverStatus.INFEASIBLE
EXIT: 0
```

5. First base run (before fixing the roster-printer bug — `v in x` tested tuple keys instead of `(v,r)`):

```text
COMMAND: .../python.exe .../r1_base.py > .../r1_base.py.out 2>&1
STATUS OPTIMAL (OPTIMAL code=4)
OBJECTIVE_VALUE 38.0
ROSTER []
ROLE safety need 1 picked ['V2']
ROLE logistics need 1 picked ['V4']
ROLE registration need 2 picked ['V5', 'V6']
VOLUNTEERS_USED 0
```

6. First fairness run (constant-infeasibility bug; garbage values printed from an infeasible solve):

```text
COMMAND: .../python.exe .../r1_fairness.py > .../r1_fairness.py.out 2>&1
STATUS INFEASIBLE (OPTIMAL code=4)
OBJECTIVE_VALUE 0.0
ROSTER []
ROLE safety need 1 picked ['V1']
ROLE logistics need 1 picked ['V7']
ROLE registration need 2 picked ['V1', 'V4', 'V6']
NEW_VOLUNTEERS_SELECTED []
DISTRICTS_SELECTED []
Traceback (most recent call last):
  File "...r1_fairness.py", line 73, in <module>
    print("MAX_POST_EXPOSURE", max(VOL[v]["exposure"] + 1 for v in selected))
ValueError: max() iterable argument is empty
EXIT: 1
```

7. First robust run (same roster-printer bug did not affect it; robust logic was correct):

```text
COMMAND: .../python.exe .../r1_robust.py > .../r1_robust.py.out 2>&1
STATUS OPTIMAL (OPTIMAL code=4)
OBJECTIVE_VALUE 172.0
PRIMARY safety ['V2'] STANDBY ['V3']
PRIMARY logistics ['V4'] STANDBY ['V7']
PRIMARY registration ['V5', 'V6'] STANDBY ['V1']
DROP V2 from safety -> heal_with V3 -> COVERED
DROP V4 from logistics -> heal_with V7 -> COVERED
DROP V5 from registration -> heal_with V1 -> COVERED
DROP V6 from registration -> heal_with V1 -> COVERED
SINGLE_DROPOUT_TESTED 4 RECOVERED 4
ROBUSTNESS_SCORE_WITH_STANDBY 1.0
ROBUSTNESS_SCORE_WITHOUT_STANDBY 0.0
ROSTER_HEALS True
```

8. First counterfactual run:

```text
COMMAND: .../python.exe .../r1_counterfactual.py > .../r1_counterfactual.py.out 2>&1
BASE_STATUS OPTIMAL OBJECTIVE_VALUE 38.0
BASE_ROSTER [('V4', 'logistics'), ('V5', 'registration'), ('V6', 'registration'), ('V2', 'safety')]
QUESTION why was V7 not picked?
FORCED_STATUS OPTIMAL OBJECTIVE_VALUE 46.0
FORCED_ROSTER [('V4', 'logistics'), ('V6', 'registration'), ('V7', 'registration'), ('V2', 'safety')]
OBJECTIVE_DELTA 8.0
DISPLACED ['V5']
ADDED ['V7']
SAME_ROLE_SWAPS []
```

9. Toggle-based infeasibility debug (after fixing the printer but before fixing the cap):

```text
COMMAND: .../python.exe .../r1_fairness_debug.py > .../r1_fairness_debug.py.out 2>&1
OPTIMAL exp False new False dist False mentor False force None picks [('V1', 'safety'), ('V4', 'registration'), ('V5', 'registration'), ('V7', 'logistics')]
INFEASIBLE exp True new False dist False mentor False force None picks []
INFEASIBLE exp True new True dist False mentor False force None picks []
INFEASIBLE exp True new True dist True mentor False force None picks []
INFEASIBLE exp True new True dist False mentor True force None picks []
INFEASIBLE exp True new True dist True mentor True force None picks []
INFEASIBLE exp True new True dist True mentor True force [('V2', 'safety'), ('V3', 'logistics'), ('V5', 'registration'), ('V6', 'registration')] picks []
```

Diagnosis: `m.Add(3 + assigned <= 2)` is a model-level contradiction for an over-cap volunteer. Fix: `if exposure >= cap: m.Add(assigned == 0)` else `m.Add(exposure + assigned <= cap)`.

10. Patched fairness run (feasible after the fix):

```text
COMMAND: .../python.exe .../r1_fairness.py > .../r1_fairness.py.out 2>&1
STATUS OPTIMAL (OPTIMAL code=4)
OBJECTIVE_VALUE 45.0
ROSTER [('V3', 'logistics'), ('V4', 'registration'), ('V5', 'registration'), ('V2', 'safety')]
ROLE safety need 1 picked ['V2']
ROLE logistics need 1 picked ['V3']
ROLE registration need 2 picked ['V4', 'V5']
NEW_VOLUNTEERS_SELECTED ['V4']
DISTRICTS_SELECTED ['A', 'B', 'C']
MAX_POST_EXPOSURE 2
NOVICE_PAIR V4 registration mentors_on_same_role ['V5']
```

11. FINAL base run (with wall time; these are the numbers pasted into the deliverable):

```text
COMMAND: C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r1_base.py > C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r1_base.py.out 2>&1
EXIT 0
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
WALL_TIME_SECONDS 0.0134
OBJECTIVE_VALUE 36.0
ROSTER [('V4', 'logistics'), ('V2', 'registration'), ('V6', 'registration'), ('V3', 'safety')]
ROLE safety need 1 picked ['V3']
ROLE logistics need 1 picked ['V4']
ROLE registration need 2 picked ['V2', 'V6']
VOLUNTEERS_USED 4
```

12. FINAL fairness run:

```text
COMMAND: C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r1_fairness.py > .../r1_fairness.py.out 2>&1
EXIT 0
STATUS OPTIMAL (OPTIMAL code=4)
WALL_TIME_SECONDS 0.0213
OBJECTIVE_VALUE 45.0
ROSTER [('V3', 'logistics'), ('V4', 'registration'), ('V5', 'registration'), ('V2', 'safety')]
ROLE safety need 1 picked ['V2']
ROLE logistics need 1 picked ['V3']
ROLE registration need 2 picked ['V4', 'V5']
NEW_VOLUNTEERS_SELECTED ['V4']
DISTRICTS_SELECTED ['A', 'B', 'C']
MAX_POST_EXPOSURE 2
NOVICE_PAIR V4 registration mentors_on_same_role ['V5']
```

13. FINAL robust run (single-dropout check passing):

```text
COMMAND: C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r1_robust.py > .../r1_robust.py.out 2>&1
EXIT 0
STATUS OPTIMAL (OPTIMAL code=4)
WALL_TIME_SECONDS 0.021
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
```

14. FINAL counterfactual run (delta printed):

```text
COMMAND: C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r1_counterfactual.py > .../r1_counterfactual.py.out 2>&1
EXIT 0
BASE_STATUS OPTIMAL OBJECTIVE_VALUE 36.0
BASE_ROSTER [('V4', 'logistics'), ('V2', 'registration'), ('V6', 'registration'), ('V3', 'safety')]
QUESTION why was V7 not picked?
FORCED_STATUS OPTIMAL OBJECTIVE_VALUE 46.0
FORCED_ROSTER [('V4', 'logistics'), ('V6', 'registration'), ('V7', 'registration'), ('V2', 'safety')]
OBJECTIVE_DELTA 10.0
DISPLACED ['V3']
ADDED ['V7']
SAME_ROLE_SWAPS [('V2', 'registration', 'safety')]
```

15. Derived Gini run:

```text
COMMAND: C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r1_gini.py > .../r1_gini.py.out 2>&1
EXIT 0
POOL ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7']
EXPOSURE_BEFORE [3, 1, 1, 0, 1, 0, 1] GINI 0.449
EXPOSURE_AFTER_BASE [3, 2, 2, 1, 1, 1, 1] GINI 0.2338
EXPOSURE_AFTER_FAIR_CAP [3, 2, 2, 1, 2, 0, 1] GINI 0.3117
```

16. Output directory creation/verification:

```text
COMMAND: mkdir -p 'C:/Users/shubh/Projects/sewacircle/docs/research' 'C:/Users/shubh/Projects/sewacircle/docs/lanes/C-research/reports'
OUTPUT: (empty), EXIT 0
COMMAND: ls -d 'C:/Users/shubh/Projects/sewacircle/docs/research' 'C:/Users/shubh/Projects/sewacircle/docs/lanes/C-research/reports'
OUTPUT:
C:/Users/shubh/Projects/sewacircle/docs/lanes/C-research/reports
C:/Users/shubh/Projects/sewacircle/docs/research
```

## Web research calls (opened pages)

Batch A (5 URLs, all opened; first copies deleted with the misplaced scratch files and re-opened in Batch D):
- https://developers.google.com/optimization/cp/cp_solver — "CP-SAT Solver", 22,927 chars, no error.
- https://developers.google.com/optimization/cp/ — "Constraint Optimization", 4,898 chars, no error.
- https://developers.google.com/optimization/cp/cp_example — "Solving a CP Problem", 15,309 chars, no error.
- https://developers.google.com/optimization/cp/channeling — "Channeling constraints", 27,475 chars, no error.
- https://developers.google.com/optimization/cp/cp_tasks — "Setting solver limits", 14,437 chars, no error.

Batch B (3 opened / 2 failed):
- https://dl.acm.org/doi/fullHtml/10.1145/3465399 — FAILED, `CRAWL_LIVECRAWL_TIMEOUT`.
- https://ami.uni-eszterhazy.hu/uploads/papers/finalpdf/AMI_63_from1to17.pdf — opened, 3,249 chars.
- https://ijcai.org/proceedings/2021/564 — opened, 3,207 chars.
- https://arxiv.org/html/1805.01299v1 — opened, 3,183 chars.
- https://cs.emis.de/LIPIcs/volltexte/2021/15402/pdf/LIPIcs-IPEC-2021-19_.pdf — FAILED, HTTP 403.

Batch C (3 opened / 2 failed):
- https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.IPEC.2021.19 — opened, 9,629 chars.
- https://ar5iv.labs.arxiv.org/html/1801.07544 — opened, 40,363 chars.
- https://pmc.ncbi.nlm.nih.gov/articles/PMC6010947/ — opened, 32,752 chars.
- https://developers.google.com/optimization/cp/integer_opt — FAILED, HTTP 404 (guessed URL, discarded).
- https://developers.google.com/optimization/assignment/assignment — FAILED, HTTP 404 (guessed URL, discarded).

Batch D (4 opened / 1 failed):
- https://developers.google.com/optimization/cp/cp_solver — re-opened, 22,927 chars.
- https://developers.google.com/optimization/cp/ — re-opened, 4,898 chars.
- https://developers.google.com/optimization/cp/channeling — re-opened, 27,475 chars.
- https://developers.google.com/optimization/cp/cp_tasks — re-opened, 14,437 chars.
- https://github.com/google/or-tools/blob/main/ortools/sat/docs/modeling_recipes.md — FAILED, HTTP 404 (guessed path, discarded).

## Sources opened (title, URL, date)

1. CP-SAT Solver — https://developers.google.com/optimization/cp/cp_solver — accessed 2026-11-18.
2. Constraint Optimization — https://developers.google.com/optimization/cp/ — accessed 2026-11-18.
3. Solving a CP Problem — https://developers.google.com/optimization/cp/cp_example — accessed 2026-11-18.
4. Channeling constraints — https://developers.google.com/optimization/cp/channeling — accessed 2026-11-18.
5. Setting solver limits — https://developers.google.com/optimization/cp/cp_tasks — accessed 2026-11-18.
6. Fair team formation for STEAM education using exact and heuristic constraint-based solvers — https://ami.uni-eszterhazy.hu/uploads/papers/finalpdf/AMI_63_from1to17.pdf — published online 2026-07-17; opened 2026-11-18.
7. Counterfactual Explanations for Optimization-Based Decisions in the Context of the GDPR — https://ijcai.org/proceedings/2021/564 — 2021; opened 2026-11-18.
8. How to Secure Matchings Against Edge Failures — https://arxiv.org/html/1805.01299v1 — submitted 2018-05-03, v3 2018-12-05; opened 2026-11-18.
9. An Investigation of the Recoverable Robust Assignment Problem — https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.IPEC.2021.19 — 2021; opened 2026-11-18.
10. An Efficient Primal-Dual Algorithm for Fair Combinatorial Optimization Problems — https://ar5iv.labs.arxiv.org/html/1801.07544 — 2018; opened 2026-11-18.
11. Finding optimal mentor-mentee matches: A case study in applied two-sided matching — https://pmc.ncbi.nlm.nih.gov/articles/PMC6010947/ — opened 2026-11-18.

## Counts

- Web search queries issued: **11** (5 + 6).
- Page fetch attempts: **20**; successful opens: **15**; distinct successfully opened URLs: **11** (four were re-opens after the scratch-cleanup mistake).
- Distinct sources in deliverable Sources list: **11**.
- Independent primaries (distinct publishers/author teams, excluding the single Google docs publisher): **6** (AMI journal article, IJCAI proceedings, arXiv paper, LIPIcs/Dagstuhl paper, PMC case study, plus OR-Tools official docs as a seventh primary source family). Requirement of 3+ independent primaries met.
- Python executions: **14** (1 failed quoting attempt, 1 env probe, 4 initial script runs, 1 debug run, 1 patched fairness run, 5 final runs including Gini; plus 2 mkdir/ls verification commands).
- Measured results printed by commands: CP-SAT `STATUS OPTIMAL (OPTIMAL code=4)` for base/fairness/robust; base roster 4 volunteers, objective 36.0, 0.0134 s; fairness objective 45.0, 0.0213 s, novice pair V4→V5; robust 4/4 dropouts recovered, robustness 1.0 vs 0.0 without standby, 0.021 s; counterfactual delta 10.0, displaced V3; Gini 0.449 → 0.2338 (base) / 0.3117 (fair cap).

## UNRESOLVED / not found

- ACM team-formation review (`10.1145/3465399`): crawler timeout; not opened, no claims rely on it.
- LIPIcs recoverable-assignment PDF via `cs.emis.de`: HTTP 403; Dagstuhl landing page used instead.
- OR-Tools `integer_opt`, `assignment/assignment` and GitHub `modeling_recipes.md` URLs: HTTP 404; no claims rely on them. OR-Tools API details used in code were verified by running the installed 9.15.6755 package, not by those pages.
- No source was found in this batch for a formal OR-Tools/Gini CP-SAT recipe implemented end to end; the deliverable therefore reports Gini descriptively and cites the linearisation literature, not an implemented Gini objective.
- Publication year of the PMC mentor–mentee paper was not captured in the opened extract; the Sources entry records access date only rather than guessing.
- Real UP district coordinates, blocks and distance-matrix provenance are out of scope for R1 and belong to the R4 lane; no geographic facts are asserted here.
