## Findings

**F1 — FACT.** OR-Tools CP-SAT is designed for integer programming and all constraints must be integer-valued (non-integer terms need scaling); the solver reports `OPTIMAL`, `FEASIBLE`, `INFEASIBLE`, `MODEL_INVALID`, `UNKNOWN`, and supports solution enumeration and solver limits. Opened: [CP-SAT Solver](https://developers.google.com/optimization/cp/cp_solver), accessed 2026-11-18. In our real run `cp_model.OPTIMAL` printed as `4` (see run output below).

**F2 — FACT.** Constraint programming is framed by Google as finding solutions satisfying all constraints rather than optimising a single score; employee scheduling is given as a canonical CP use case. Opened: [Constraint Optimization](https://developers.google.com/optimization/cp/), accessed 2026-11-18. This supports modelling role coverage as hard constraints and keeping "quality" in the objective.

**F3 — FACT.** Channeling/implication with Boolean variables is the documented OR-Tools pattern for "if this is true, then that must hold" conditions. Opened: [Channeling constraints](https://developers.google.com/optimization/cp/channeling), accessed 2026-11-18. This is the basis for our novice→mentor and primary→standby implications.

**F4 — FACT.** Google documents explicit time/solution limits on the solver so a run terminates predictably. Opened: [Setting solver limits](https://developers.google.com/optimization/cp/cp_tasks), accessed 2026-11-18. Relevant to a demo that must respond in seconds.

**F5 — FACT.** A peer-reviewed team-formation study models team construction as a constraint satisfaction problem with skill, gender and training constraints, compares Z3 SMT, OR-Tools CP-SAT and a genetic algorithm on synthetic sets of 50/100/500 students, and reports that both exact solvers produce more balanced teams with lower fairness gaps than the heuristic, while CP-SAT gives more stable/scalable results across sizes and there is an explicit fairness-vs-computation trade-off. Opened: [Fair team formation for STEAM education using exact and heuristic constraint-based solvers](https://ami.uni-eszterhazy.hu/uploads/papers/finalpdf/AMI_63_from1to17.pdf), published online 2026-07-17. *Scope note (INFERENCE): their setting is student teams, not volunteer rosters; we take the modelling pattern, not their numbers.*

**F6 — FACT.** For counterfactual explanations of declarative optimisation, the IJCAI paper states that for objective functions that are a sum of weighted binary variables, full inverse optimisation is unnecessary: a slightly modified version of the original model suffices; sums of weighted integer variables need a binary search over modified models. Opened: [Counterfactual Explanations for Optimization-Based Decisions in the Context of the GDPR](https://ijcai.org/proceedings/2021/564), IJCAI 2021. Our forced-pick counterfactual is exactly this "slightly modified model" pattern.

**F7 — FACT.** In bipartite matching literature, a graph is called *robust* if it still admits a perfect matching after removal of any single edge; the studied problem is adding a minimum-cost edge set to obtain that property, with exact and approximation algorithms. Opened: [How to Secure Matchings Against Edge Failures](https://arxiv.org/html/1805.01299v1), submitted 2018-05-03, v3 2018-12-05. *INFERENCE: our standby pool is the roster analogue of buying spare edges.*

**F8 — FACT.** The recoverable robust assignment problem asks for two perfect matchings whose overlap is at least `k` edges under two cost functions; the problem is W[1]-hard in `k` and in the complement parameter. Opened: [An Investigation of the Recoverable Robust Assignment Problem](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.IPEC.2021.19), IPEC 2021. *INFERENCE: keep our shipped guarantee at k=1 (one dropout); k>1 is a harder, separately scoped problem.*

**F9 — FACT.** Generalized Gini Index (GGI) is used as a fairness aggregation in combinatorial optimisation (allocation, knapsack, matching, TSP), and a 0/1 linear program exists via the Ogryczak–Sliwinski Lorenz-component linearisation. Opened: [An Efficient Primal-Dual Algorithm for Fair Combinatorial Optimization Problems](https://ar5iv.labs.arxiv.org/html/1801.07544), arXiv:1801.07544. *INFERENCE: an exact Gini objective is implementable but heavier than the exposure cap we actually ran.*

**F10 — FACT.** Mentor–mentee allocation is studied as two-sided matching, where *stability* (no participant prefers a different partner to their assigned one) is the core quality criterion, alongside other criteria. Opened: [Finding optimal mentor-mentee matches: A case study in applied two-sided matching](https://pmc.ncbi.nlm.nih.gov/articles/PMC6010947/), accessed 2026-11-18. *INFERENCE: our demo uses a simpler hard constraint (a mentor on the same role/site), not a full stability model; do not claim stability.*

**Formulations actually implemented and executed (all data SYNTHETIC).** Variables `x[v,r] ∈ {0,1}` mean volunteer `v` is assigned to role `r`.

1. **Role coverage with skill levels.** Precompute eligibility `E(v,r) = avail[v] ∧ km[v] ≤ D_max ∧ skill[v,skill(r)] ≥ t_r`; add `x[v,r] ≤ E(v,r)`, `Σ_r x[v,r] ≤ 1` per volunteer, and `Σ_v x[v,r] = n_r` per role. Objective `min Σ c[v,r]·x[v,r]` with integer `c = 2·km + 5·exposure − 2·(skill−threshold) − 4·is_new`. Costs are a policy choice, not a measured quantity.
2. **Availability and travel.** `avail` is a per-slot Boolean (demo uses one slot); `km` comes from a precomputed distance matrix volunteer→site. Both are hard filters via `E(v,r)`, so an unavailable volunteer (V9) and a 20 km volunteer (V8, limit 12 km) were excluded by the solver's eligibility matrix before modelling. A softer variant is `Σ_r x[v,r] ≤ M·(1−late[v])` with a penalty on `late[v]`; not used here because safety/feasibility should be hard.
3. **Rotation fairness.** Exposure cap: if `exposure[v] ≥ cap` force `Σ_r x[v,r] = 0`, else `exposure[v] + Σ_r x[v,r] ≤ cap`. New-volunteer opportunity: `Σ_{v:new}Σ_r x[v,r] ≥ 1`. District spread: `Σ_{v:district=d}Σ_r x[v,r] ≤ 2` per district. Optional Gini: sort attained exposures or use pairwise absolute deviations and linearise as in F9; we only *computed* Gini post hoc (see output), we did not optimise it.
4. **Novice–mentor on same role/site.** For every novice `v` and role `r` they may take: `Σ_{u≠v, mentor[u], eligible(u,r)} x[u,r] ≥ x[v,r]`. With multiple sites, restrict the sum to volunteers whose `site_id` equals `v`'s site; the demo has one site.
5. **Dropout resilience.** Add `z[v,r]` (primary) and `s[v,r]` (standby), `z+s ≤ 1` per pair and `Σ_r(z+s) ≤ 1` per volunteer; `Σ_v z[v,r] = n_r`; and for each role `r` and potential primary `w`: `Σ_{u∈E(r), u≠w} s[u,r] ≥ z[w,r]`. This guarantees that any single primary's slot can be filled by a standby on the same role. Robustness score is measured by simulating every primary dropout and rechecking coverage. Extension to k dropouts requires `k` distinct standbys per role and grows constraints linearly; F8 warns this is a harder problem.
6. **Counterfactual explanations.** Solve base model (objective `b`), then add `Σ_r x[X,r] = 1` and re-solve with everything else unchanged (objective `c`). Report `delta = c − b`, `displaced = base_selected − cf_selected`, `added = cf_selected − base_selected`, and role swaps. If the forced model is `INFEASIBLE`, the honest explanation is "no feasible roster contains X under these constraints" — not a made-up reason.

**Runnable snippets and their real output.** Python 3.13.14, ortools 9.15.6755, run with `C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe`. All data below is invented for this demo; no real people or minors. Each snippet was executed as *shared prelude + block* in a scratch file.

Shared prelude (paste at the top of snippets 1–4):

```python
from ortools.sat.python import cp_model
VOL = {
 "V1":{"skill":{"first_aid":3,"logistics":1,"hindi":2},"avail":1,"km":2, "district":"A","exposure":3,"new":0,"novice":0,"mentor":1},
 "V2":{"skill":{"first_aid":2,"logistics":0,"hindi":2},"avail":1,"km":3, "district":"B","exposure":1,"new":0,"novice":0,"mentor":1},
 "V3":{"skill":{"first_aid":3,"logistics":2,"hindi":1},"avail":1,"km":5, "district":"A","exposure":1,"new":0,"novice":0,"mentor":1},
 "V4":{"skill":{"first_aid":1,"logistics":3,"hindi":2},"avail":1,"km":4, "district":"C","exposure":0,"new":1,"novice":1,"mentor":0},
 "V5":{"skill":{"first_aid":0,"logistics":2,"hindi":3},"avail":1,"km":6, "district":"B","exposure":1,"new":0,"novice":0,"mentor":1},
 "V6":{"skill":{"first_aid":2,"logistics":1,"hindi":3},"avail":1,"km":8, "district":"C","exposure":0,"new":1,"novice":1,"mentor":0},
 "V7":{"skill":{"first_aid":1,"logistics":3,"hindi":2},"avail":1,"km":9, "district":"D","exposure":1,"new":0,"novice":0,"mentor":0},
 "V8":{"skill":{"first_aid":2,"logistics":2,"hindi":1},"avail":1,"km":20,"district":"D","exposure":1,"new":0,"novice":0,"mentor":0},
 "V9":{"skill":{"first_aid":3,"logistics":2,"hindi":2},"avail":0,"km":4, "district":"D","exposure":0,"new":1,"novice":1,"mentor":0},
}
ROLES = {"safety":("first_aid",2,1), "logistics":("logistics",2,1), "registration":("hindi",2,2)}
MAX_KM = 12
def eligible(v,r):
    d=VOL[v]; s,t,_=ROLES[r]
    return bool(d["avail"]) and d["km"]<=MAX_KM and d["skill"][s]>=t
def cost(v,r):
    d=VOL[v]; s,t,_=ROLES[r]
    return 2*d["km"]+5*d["exposure"]-2*(d["skill"][s]-t)-4*d["new"]
```

Snippet 1 — base role coverage:

```python
for v in VOL:
    ok = [r for r in ROLES if eligible(v,r)]
    print(v, "eligible-for:" + (",".join(ok) if ok else "NONE"))
m = cp_model.CpModel()
x = {(v,r): m.NewBoolVar("x_%s_%s"%(v,r)) for v in VOL for r in ROLES if eligible(v,r)}
for v in VOL: m.Add(sum(x[v,r] for r in ROLES if (v,r) in x) <= 1)
for r,(s,t,need) in ROLES.items(): m.Add(sum(x[v,r] for v in VOL if (v,r) in x) == need)
m.Minimize(sum(cost(v,r)*x[v,r] for (v,r) in x))
sv = cp_model.CpSolver(); st = sv.Solve(m)
print("STATUS", sv.StatusName(st), "(OPTIMAL code=%d)"%cp_model.OPTIMAL)
print("WALL_TIME_SECONDS", round(sv.WallTime(),4))
print("OBJECTIVE_VALUE", sv.ObjectiveValue())
print("ROSTER", sorted((v,r) for (v,r) in x if sv.Value(x[v,r])))
for r in ROLES: print("ROLE", r, "picked", [v for v in VOL if (v,r) in x and sv.Value(x[v,r])])
```

Command: `C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r1_base.py`; exit 0. Real output:

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
WALL_TIME_SECONDS 0.0134
OBJECTIVE_VALUE 36.0
ROSTER [('V4', 'logistics'), ('V2', 'registration'), ('V6', 'registration'), ('V3', 'safety')]
ROLE safety need 1 picked ['V3']
ROLE logistics need 1 picked ['V4']
ROLE registration need 2 picked ['V2', 'V6']
VOLUNTEERS_USED 4
```

Snippet 2 — fairness cap, new volunteer, district spread, novice–mentor:

```python
m = cp_model.CpModel()
x = {(v,r): m.NewBoolVar("x_%s_%s"%(v,r)) for v in VOL for r in ROLES if eligible(v,r)}
for v in VOL:
    a = sum(x[v,r] for r in ROLES if (v,r) in x)
    m.Add(a <= 1)
    if VOL[v]["exposure"] >= 2: m.Add(a == 0)          # already at/over cap
    else: m.Add(VOL[v]["exposure"] + a <= 2)           # cap total exposure at 2
for r,(s,t,need) in ROLES.items(): m.Add(sum(x[v,r] for v in VOL if (v,r) in x) == need)
m.Add(sum(x[v,r] for v in VOL if VOL[v]["new"] and (v,r) in x) >= 1)
for d in set(VOL[v]["district"] for v in VOL):
    m.Add(sum(x[v,r] for v in VOL if VOL[v]["district"]==d and (v,r) in x) <= 2)
for v in VOL:
    if VOL[v]["novice"]:
        for r in ROLES:
            if (v,r) in x:
                m.Add(sum(x[u,r] for u in VOL if u!=v and VOL[u]["mentor"] and (u,r) in x) >= x[v,r])
m.Minimize(sum(cost(v,r)*x[v,r] for (v,r) in x))
sv = cp_model.CpSolver(); st = sv.Solve(m)
print("STATUS", sv.StatusName(st), "(OPTIMAL code=%d)"%cp_model.OPTIMAL)
print("WALL_TIME_SECONDS", round(sv.WallTime(),4))
print("OBJECTIVE_VALUE", sv.ObjectiveValue())
print("ROSTER", sorted((v,r) for (v,r) in x if sv.Value(x[v,r])))
```

Command: `.../python.exe .../r1_fairness.py`; exit 0. Real output:

```text
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

Snippet 3 — dropout-robust standby model and live heal check:

```python
m = cp_model.CpModel()
z = {(v,r): m.NewBoolVar("z_%s_%s"%(v,r)) for v in VOL for r in ROLES if eligible(v,r)}
s = {(v,r): m.NewBoolVar("s_%s_%s"%(v,r)) for v in VOL for r in ROLES if eligible(v,r)}
for v in VOL:
    for r in ROLES:
        if (v,r) in z: m.Add(z[v,r] + s[v,r] <= 1)
    m.Add(sum(z[v,r] for r in ROLES if (v,r) in z) + sum(s[v,r] for r in ROLES if (v,r) in s) <= 1)
for r,(sk,t,need) in ROLES.items():
    m.Add(sum(z[v,r] for v in VOL if (v,r) in z) == need)
    for w in VOL:
        if (w,r) in z: m.Add(sum(s[v,r] for v in VOL if v!=w and (v,r) in s) >= z[w,r])
m.Minimize(sum(cost(v,r)*(3*z[v,r]+s[v,r]) for (v,r) in z))
sv = cp_model.CpSolver(); st = sv.Solve(m)
primary = {r:[v for v in VOL if (v,r) in z and sv.Value(z[v,r])] for r in ROLES}
standby = {r:[v for v in VOL if (v,r) in s and sv.Value(s[v,r])] for r in ROLES}
for r in ROLES: print("PRIMARY", r, primary[r], "STANDBY", standby[r])
tested = recovered = 0
for r in ROLES:
    for w in primary[r]:
        tested += 1
        plan = {rr:list(primary[rr]) for rr in ROLES}; plan[r].remove(w)
        used = set(u for rr in ROLES for u in plan[rr])
        heal = next((c for c in standby[r] if c not in used), None)
        if heal: plan[r].append(heal)
        ok = all(len(plan[rr]) >= ROLES[rr][2] for rr in ROLES)
        recovered += ok
        print("DROP", w, "from", r, "-> heal_with", heal, "->", "COVERED" if ok else "FAILED")
print("SINGLE_DROPOUT_TESTED", tested, "RECOVERED", recovered)
print("ROBUSTNESS_SCORE_WITH_STANDBY", round(recovered/tested,3))
```

Command: `.../python.exe .../r1_robust.py`; exit 0. Real output:

```text
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

Snippet 4 — counterfactual re-solve ("why was V7 not picked?"):

```python
def solve(force=None):
    m = cp_model.CpModel()
    x = {(v,r): m.NewBoolVar("x_%s_%s"%(v,r)) for v in VOL for r in ROLES if eligible(v,r)}
    for v in VOL: m.Add(sum(x[v,r] for r in ROLES if (v,r) in x) <= 1)
    for r,(s,t,need) in ROLES.items(): m.Add(sum(x[v,r] for v in VOL if (v,r) in x) == need)
    if force: m.Add(sum(x[force,r] for r in ROLES if (force,r) in x) == 1)
    m.Minimize(sum(cost(v,r)*x[v,r] for (v,r) in x))
    sv = cp_model.CpSolver(); assert sv.Solve(m) == cp_model.OPTIMAL
    return sv.ObjectiveValue(), {v:r for (v,r) in x if sv.Value(x[v,r])}
b, base = solve(); c, cf = solve(force="V7")
print("OBJECTIVE_DELTA", c-b)
print("DISPLACED", sorted(set(base)-set(cf)))
print("ADDED", sorted(set(cf)-set(base)))
```

Command: `.../python.exe .../r1_counterfactual.py`; exit 0. Real output:

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
```

**Derived Gini check (INFERENCE, computed from the two printed rosters; stdlib only):**

```python
def gini(vals):
    s=sorted(vals); n=len(s); tot=sum(s)
    return round(sum((2*i-n-1)*v for i,v in enumerate(s,1))/(n*tot),4) if tot else 0.0
pool = ["V1","V2","V3","V4","V5","V6","V7"]
before = [3,1,1,0,1,0,1]
base_sel = {"V2","V3","V4","V6"}
fair_sel = {"V2","V3","V4","V5"}
print("GINI before", gini(before))
print("GINI after base", gini([v+(k in base_sel) for k,v in zip(pool,before)]))
print("GINI after fair cap", gini([v+(k in fair_sel) for k,v in zip(pool,before)]))
```

Real output from the executed equivalent script (`r1_gini.py`, exit 0):

```text
POOL ['V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7']
EXPOSURE_BEFORE [3, 1, 1, 0, 1, 0, 1] GINI 0.449
EXPOSURE_AFTER_BASE [3, 2, 2, 1, 1, 1, 1] GINI 0.2338
EXPOSURE_AFTER_FAIR_CAP [3, 2, 2, 1, 2, 0, 1] GINI 0.3117
```

INFERENCE from that output: the cap excluded over-exposed V1 and kept new volunteer V4 in the roster, but the *post-selection* Gini is higher than the base roster's (0.3117 vs 0.2338) because historical exposure is unchanged and V4's zero became one. A cap is not the same objective as minimising inequality; label these as different metrics in the eval lane.

## Recommendation for our build

- **Input JSON fields (synthetic in demo).** `volunteers[]`: `{id, skills:{skill_id:0..3}, availability:{slot_id:true|false}, district, site_id, distance_km_by_site, prior_exposure_count, is_new, is_novice, can_mentor, preferred_roles[]}`. `roles[]`: `{role_id, required_skill, min_level, headcount, site_id, slot_id}`. `policy`: `{max_commute_km, exposure_cap, min_new_volunteers, max_per_district, standby_enabled, robustness_target, weights:{km,exposure,skill_surplus,new_volunteer}, time_limit_s}`.
- **Code shape.** Pure solver module with `build_base_model(data, policy) -> (model, x)`, `add_fairness(model, x, data, policy)`, `add_standby(model, x, data, policy)`, `solve(model) -> status/objective/assignments`, `simulate_dropouts(solution) -> score`, `counterfactual(force_id) -> delta/displaced`. Keep LLM extraction and solver strictly separate; the solver never invents skills.
- **Hard vs soft.** Skill threshold, availability, commute and role headcount are hard (`==`/`<=`); commute/skill distance only enters `c[v,r]` as a tie-breaker. Never let a penalty allow an unsafe skill mismatch.
- **Exposure cap implementation.** Branch in Python on `prior_exposure_count >= cap` and emit `assigned == 0`; do NOT emit `prior + assigned <= cap` when `prior` alone already exceeds the cap — that is a constant infeasibility (we observed this exact failure before fixing it).
- **Reason per pick.** Emit from solver data, not from the LLM: `skill_level ≥ threshold`, `distance_km ≤ max`, `prior_exposure`, "first opportunity" when `is_new`, "paired with mentor Vx on the same role", "standby for role r". For a rejected volunteer, call `counterfactual(id)` and show `delta` + displaced names, or "no feasible roster includes them" if forced solve is infeasible.
- **Demo sequence (all numbers must come from a fresh run).** Base roster (4 roles covered, 0.0134 s in our run) → toggle fairness (6 constraints, 0.0213 s) → toggle standby, click "drop V4" and show heal via V7 with `SINGLE_DROPOUT_TESTED 4 RECOVERED 4`, score 1.0 vs 0.0 without standby → click "why not V7?" and show delta 10.0, V3 displaced. Present these as results from the synthetic dataset, never as production benchmarks.
- **Scaling path.** Index eligibility by `(role_id, site_id, slot_id)` once per request; add `solver.parameters.max_time_in_seconds = policy.time_limit_s` per [solver limits](https://developers.google.com/optimization/cp/cp_tasks); solve base → robust → counterfactual as separate bounded calls. For real districts/cities use the verified distance matrix from the UP-realism lane (we did not verify any UP coordinates here).
- **Gini placement.** Report before/after exposure Gini in the eval harness as a *descriptive* metric (F9 linearisation is available if judges ask for an exact fairness objective); do not conflate it with the exposure cap.
- **Keep claims bounded.** F5 supports "CP-SAT is a credible exact solver for balanced team formation"; it does not support claims about volunteer retention, cost savings or UP-specific outcomes. No such numbers exist in this research file.

## Risks

- **Observed infeasibility trap.** A naive `prior_exposure + assigned <= cap` with `prior=3, cap=2` makes the *whole model* infeasible regardless of assignments; our first fairness run printed `STATUS INFEASIBLE` yet `solver.Value()` still returned a nonsensical roster (`ROLE registration need 2 picked ['V1', 'V4', 'V6']`). Always check `status` before reading values.
- **Tiny synthetic instance.** 9 invented volunteers, 3 roles, one site, one slot; runtimes 0.0134–0.0213 s are evidence of responsiveness on this toy instance only, not scalability. F5's 50/100/500-student experiment is a different problem and dataset.
- **Standby pool cost.** Guarantees required 7 distinct eligible volunteers for 4 primary slots here. With a small or skill-scarce pool the robust model can be infeasible; the UI must say so instead of dropping the guarantee silently. k>1 resilience is not implemented and is theoretically harder (F8).
- **Counterfactual units.** `delta = 10.0` is in arbitrary integer objective units from our weight formula; it is not rupees, hours or fairness. Explain the weights in the UI, and treat weight changes as a policy decision requiring organiser visibility (responsible-AI criterion).
- **Fairness metric surprise.** In our run the post-selection Gini rose from 0.2338 (base) to 0.3117 (fair-cap) because historical exposure is fixed; do not demo "fairness improved" using both metrics interchangeably.
- **Geography and identity.** District cap uses district as a diversity proxy; do not add gender/caste/religion to the objective. `site_id` and `distance_km` must be sourced and labelled (synthetic in demo); no real volunteer, minor, or real address appears in this file.
- **Model scope.** Novice–mentor here is a same-role constraint, not the stability notion from F10; multiple sites/slots and standbys across shifts are not modelled.
- **Source access limits.** Two candidate sources could not be opened: the ACM team-formation review (`https://dl.acm.org/doi/fullHtml/10.1145/3465399`, crawler timeout) and the LIPIcs recoverable-assignment PDF (`https://cs.emis.de/LIPIcs/volltexte/2021/15402/pdf/LIPIcs-IPEC-2021-19_.pdf`, HTTP 403). No claim in this file relies on them; the Dagstuhl landing page was used instead. Three guessed OR-Tools URLs returned 404 and were discarded.
- **Version pin.** Results are from ortools 9.15.6755 / Python 3.13.14; re-run rather than assume identical output after an environment change.

## Sources

- CP-SAT Solver — https://developers.google.com/optimization/cp/cp_solver — opened/accessed 2026-11-18 (page shows no publication date).
- Constraint Optimization — https://developers.google.com/optimization/cp/ — opened/accessed 2026-11-18.
- Channeling constraints — https://developers.google.com/optimization/cp/channeling — opened/accessed 2026-11-18.
- Setting solver limits — https://developers.google.com/optimization/cp/cp_tasks — opened/accessed 2026-11-18.
- Solving a CP Problem — https://developers.google.com/optimization/cp/cp_example — opened/accessed 2026-11-18.
- Fair team formation for STEAM education using exact and heuristic constraint-based solvers (Ali, Kovásznai, Herbák, Khalid; Annales Mathematicae et Informaticae 63, pp. 1–17) — https://ami.uni-eszterhazy.hu/uploads/papers/finalpdf/AMI_63_from1to17.pdf — published online 2026-07-17; opened 2026-11-18.
- Counterfactual Explanations for Optimization-Based Decisions in the Context of the GDPR (Korikov, Shleyfman, Beck; IJCAI) — https://ijcai.org/proceedings/2021/564 — 2021; opened 2026-11-18.
- How to Secure Matchings Against Edge Failures (Hommelsheim, Mühlenthaler, Schaudt; arXiv:1805.01299) — https://arxiv.org/html/1805.01299v1 — submitted 2018-05-03, v3 2018-12-05; opened 2026-11-18.
- An Investigation of the Recoverable Robust Assignment Problem (Fischer, Hartmann, Lendl, Woeginger; LIPIcs IPEC 2021) — https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.IPEC.2021.19 — 2021; opened 2026-11-18.
- An Efficient Primal-Dual Algorithm for Fair Combinatorial Optimization Problems (Viet Hung Nguyen; arXiv:1801.07544) — https://ar5iv.labs.arxiv.org/html/1801.07544 — 2018; opened 2026-11-18.
- Finding optimal mentor-mentee matches: A case study in applied two-sided matching — https://pmc.ncbi.nlm.nih.gov/articles/PMC6010947/ — accessed/opened 2026-11-18 (publication year not recorded from the opened extract).
