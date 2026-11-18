# Lane A solver DESIGN (B1c scaffolding pass)

Status: DESIGN ONLY at this point. `solver/cp_sat.py`, `solver/metrics.py`, `solver/baselines.py` and `data/synth.py` are being written by other workers in parallel. No objective weight in this document is implemented, tuned or measured here. Research docs were empty when this was written; if `docs/research/R1-optimization.md` appears, B2/B3 must reconcile this design with it.

## FACT - source material read

- F1: `app/schemas.py` defines the shared contract. Relevant solver fields: `Volunteer` (id, age, available_slots, lat, lon, skills as skill-id to level in 1..3, self_declared_skills, guardian_consent, district, block, past_drives, times_picked_last_90d, synthetic), `RoleSpec` (id, role, count, required_skills any-of, min_level, priority must/should, needs_experienced), `TaskSpec` (id, title, slot, district, block, lat, lon, max_travel_km, allow_minors, roles, synthetic), `RosterOptions` (fairness, resilience, mentor_pairing, forced_in, forced_out, time_limit_s, seed), `Assignment`, `StandbyPick`, `RosterMetrics`, `RosterResult`.
- F2: `docs/lanes/A-solver/TASK.md` lists the hard constraints and the objective priority ladder: must-role coverage, skill-fit, proximity, fairness U2, resilience U1.
- F3: `app/taxonomy.py` defines the skill ids (SKILLS) and the allowed slot ids (SLOTS). Every generated skill id and slot id comes from these.
- F4: `RosterMetrics.role_coverage` is documented as filled qualified slots / required slots with must roles weighted equally; `robustness` as the share of single-dropout scenarios leaving all must roles covered.
- F5: `RosterResult` has an explicit `unfilled_role_ids` field and `solver_status` lives on `RosterMetrics`; infeasibility must be reported, not hidden.

## Hard constraints (complete list)

Each item states where it comes from. All of them apply to every assignment; items 6-10 are contract proposals derived from the schema fields and TASK.md.

1. FACT: availability - a volunteer may fill a slot only if `task.slot` is in `volunteer.available_slots`.
2. FACT: qualification - at least one of `role.required_skills` must be held at level at least `role.min_level`. If `required_skills` is empty, the role is unskilled and any otherwise-eligible volunteer may fill it.
3. INFERENCE: self-declared skills - `self_declared_skills` may satisfy a required skill but the assignment must carry a `self_declared_skill` flag. The schema stores no level for self-declarations, so how to compare them with `min_level` is a B2 decision; the scaffolding treats them as satisfying `min_level` and flags them.
4. FACT: travel - haversine distance between volunteer and task coordinates must not exceed `task.max_travel_km`.
5. FACT: minors - a volunteer with age below 18 may be assigned only if `task.allow_minors` is true AND `volunteer.guardian_consent is True`. A minor without consent is valid *input data*; the solver must exclude that person. The assignment should carry a `minor_guardian_consent` flag when this path is used.
6. INFERENCE: one role per volunteer - at most one `Assignment` per volunteer id in a roster. Slots of the same role are distinct assignments to distinct volunteers.
7. INFERENCE: forced_in - every id in `RosterOptions.forced_in` must appear as an assigned volunteer. If such a person cannot satisfy constraints 1-6, the instance is infeasible for that request and the shortfall must be reported. Forcing a person in must never weaken a hard constraint.
8. FACT: forced_out - no id in `RosterOptions.forced_out` may appear in assignments or in standby.
9. INFERENCE: counts and honesty - each role has `role.count` slots; if fewer can be filled, the role id goes into `unfilled_role_ids`. `solver_status` must report OPTIMAL, FEASIBLE or INFEASIBLE as actually returned by the solver, and `time_limit_s` is a ceiling on search, not a licence to violate constraints.
10. INFERENCE: standby eligibility - standby volunteers must themselves satisfy constraints 1-6 for at least one role they claim to cover. Otherwise dropout healing could reintroduce an ineligible person. A standby pick may cover several role ids via `covers_role_ids`, but that list is advisory; the matching test below is authoritative.

NOT a hard constraint: `RoleSpec.needs_experienced`. TASK.md places novice/mentor handling in the fairness objective. The scaffolding's eligibility helper deliberately does not filter on it; filtering there would produce false property-test failures against a solver that correctly treats it as soft.

## Robustness - precise definition (U1)

This is the definition the shared metric and the resilience objective must use. It is an INFERENCE from F4 and TASK.md batch B3; the schema stores only the resulting score, not the intermediate matchings.

Given a roster with assigned volunteer set `A`, standby volunteer set `S`, and the set `M` of must-role slots (a role of priority must with count k contributes k distinguishable slot nodes):

1. For each `v` in `A`, form the survivor pool `P_v = (A \ {v}) union S`, then remove `v` itself, every `forced_out` id, and every person who fails any hard constraint 1-6.
2. Build a bipartite graph between the must-role slot nodes and `P_v`. Put an edge from slot node to person iff that person may fill that role under hard constraints 1-6 (self-declared rule included).
3. Compute a maximum-cardinality bipartite matching of this graph. The dropout scenario for `v` passes iff the matching size equals the number of must-role slots in `M`. Should-role slots are excluded from this test (INFERENCE from F4 wording all must roles covered).
4. `robustness = (# of v in A whose scenario passes) / |A|`. If `A` is empty, `robustness = 0.0` by explicit convention, to avoid division by zero (INFERENCE; must be documented in metrics.py).

Consequences to test in B2/B3: adding an ineligible standby cannot raise robustness; a standby who duplicates an already assigned volunteer cannot heal that volunteer's own dropout; forcing an ineligible volunteer in can lower robustness but must not lower it by mis-reporting the matching.

## Planned CP-SAT objective - strict priority ladder (PLANNED, not measured)

No numeric weights are given here. Exact numeric values, and whether to implement the ladder lexicographically or as a weighted sum with strictly separated magnitudes, are to be finalized in B2/B3. Any weight written in code must be marked as proposed until the eval harness reports measured results.

1. Must-role coverage (highest): maximise the number of filled must-role slots. An unfilled must slot must never be traded for any later term.
2. Skill-fit: among equally covering rosters, prefer higher demonstrated skill level for the required skill and fewer self-declared-only matches (INFERENCE from the flag requirement in item 3).
3. Proximity: prefer smaller haversine distance for assigned volunteers (INFERENCE from the `distance_km` and proximity wording in TASK.md).
4. Fairness U2: penalise high `times_picked_last_90d`, give a bounded bonus to novices, reward novice-mentor pairs where `role.needs_experienced` is true, and reward district spread (FACT: these are listed in TASK.md; the shape of each term is proposed here).
5. Resilience U1 (lowest of the mandated ladder): for a fixed result on all earlier terms, choose standby picks that maximise `robustness` as defined above (FACT: TASK.md batch B3).

OPINION: a strict lexicographic priority is easier to explain to an organiser than a dense weighted sum, and explanation quality is part of the demo. This is a preference, not a finding; B2/B3 own the final choice.

Should-role coverage is not placed in the mandated ladder. INFERENCE: it should sit below must-role coverage, but its exact position relative to skill-fit is a B2 decision and must not be silently assumed.

## Metrics stay shared across all methods

- FACT: `app/solver/metrics.py` is specified to expose ONE `compute_metrics(task, volunteers, roster)`; every method must call that function. No method may compute its own coverage, robustness, fairness or distance score.
- The function takes only public inputs (task, volunteers, roster). It must not read solver internals, solver status or method-specific state. A baseline that records no standby gets robustness computed against its empty standby list; the manual_greedy baseline is explicitly required to supply one backup per role so it is credited honestly for backups.
- The eval harness must build one `EvalRow` per task/method from that single function, and bootstrap confidence intervals must resample those rows. No method-specific normalisation, ceiling or rounding may be applied in the harness.
- If a metric definition changes, change it in metrics.py and update its tests; the eval report must state which definition produced the numbers. This keeps cp_sat versus baseline comparisons like-for-like.

## FACT / INFERENCE / OPINION summary

- FACT: schema fields, taxonomy ids/slots, TASK.md hard-constraint and objective list, the shared-metrics requirement, and the meaning of `unfilled_role_ids` / `solver_status`.
- INFERENCE: self-declared level handling, one-role-per-volunteer, forced_in semantics, standby eligibility, empty-set robustness convention, exclusion of should roles from robustness, and the mathematical shape of each objective term.
- OPINION: preference for lexicographic priority over a weighted sum; not a measured result.

## Scaffolding boundary

`backend/tests/solver/factories.py` is stdlib-only and imports only `app.schemas` and `app.taxonomy`. Its `validate_case` reports internal-consistency failures; an unfillable role is reported with a `warn:` prefix because it is a legitimate adversarial case, not an invalid instance. Minors without consent are likewise legitimate input. The generator therefore does not hide hard-constraint violations - it creates them so B2 property tests can check that the solver rejects them.
