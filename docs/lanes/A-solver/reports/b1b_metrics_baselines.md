# B1b report - shared metrics and honest baselines

## Files written

- backend/app/solver/metrics.py
- backend/app/solver/baselines.py
- backend/tests/solver/test_metrics.py
- backend/tests/solver/test_baselines.py
- docs/lanes/A-solver/reports/b1b_metrics_baselines.md (this report)

No other file was written. synth.py was not imported or touched.

## Exact metric definitions (also in the metrics.py module docstring)

Shared entry point: `compute_metrics(task, volunteers, roster) -> RosterMetrics`. Every baseline calls
it, so comparisons use exactly the same code as the future CP-SAT roster.

Travel: no haversine helper exists elsewhere in the codebase (searched backend/app, including api.py
and main.py; only Assignment.distance_km exists as a schema field). `haversine_km` is implemented in
metrics.py with stdlib math only, Earth radius R = 6371.0088 km, and a 1e-9 km tolerance on the
travel limit.

Shared hard-constraint predicate `is_eligible(v, role, task)`: task.slot in v.available_slots;
haversine(v, task) <= task.max_travel_km; skill any-of at role.min_level OR listed in
v.self_declared_skills (no level is stored for declarations, so they are treated as qualifying at
any min_level and the assignment is flagged self_declared_skill); if v.is_minor then
task.allow_minors AND v.guardian_consent is True. Empty required_skills means no skill constraint.

- all slots: for every RoleSpec (both priority must and should, each slot equal weight), every
  (role.id, index) for index in range(role.count). must slots: same, restricted to priority must.
- slots_filled: number of distinct (role_id, slot_index) assignments naming a known role, a valid
  index and a known volunteer that pass is_eligible. Duplicate slots count once.
- slots_required: number of all slots. role_coverage = slots_filled / slots_required; 1.0 when
  there are no slots; never greater than 1.
- robustness: for each distinct assigned volunteer v, rescue pool = all other assigned volunteers
  plus roster.standby (unknown/duplicate ids ignored). The scenario passes iff every must slot can
  be matched to a DISTINCT eligible pool volunteer by fresh bipartite matching (Kuhn augmenting
  paths, stdlib only), with cross-role reassignment allowed. robustness = passed / number of
  assigned volunteers; 0.0 for an empty roster with must slots, 1.0 when there are no must slots.
- repeat_pick_share: share of distinct assigned volunteers with times_picked_last_90d >= 3.
- exposure_gini: Gini of times_picked_last_90d over distinct assigned volunteers, sorted ascending,
  G = 2 * sum((i+1) * x[i]) / (n * sum(x)) - (n+1)/n; 0.0 for n == 0 or sum(x) == 0.
- district_spread: number of distinct (district, block) pairs among distinct assigned volunteers.
- novices: count of distinct assigned volunteers with past_drives < 3.
- mentor_pairs: number of distinct novice assigned volunteers assigned to a role with
  needs_experienced True that also has at least one assigned volunteer with past_drives >= 5.
- solve_ms and solver_status are caller-owned status/timing fields; compute_metrics leaves them at
  schema defaults and the baselines fill them honestly (baseline_complete / baseline_partial).

## Baselines

All three respect the same shared predicate, assign each volunteer at most once, return
RosterResult with plain-English reasons[] and flags[], report unfilled_role_ids honestly, and use
compute_metrics for their metrics.

- nearest_skill: roles in task order; nearest eligible unassigned volunteer per slot (ties broken
  by confirmed skill level, past drives, id). Naive on purpose: no fairness objective.
- random_feasible: seeded random.Random(seed) choice among eligible unassigned volunteers;
  deterministic per seed (candidates sorted by id before the draw).
- manual_greedy: roles in task order; most experienced eligible volunteer per slot (tie break:
  skill level, distance, id), plus exactly ONE next-best eligible backup per role as a StandbyPick
  covering that role, so the baseline gets honest credit for backups.
- forced_in/forced_out are honoured when an optional RosterOptions is passed (or when the task
  object carries those attributes). Impossible forced_in picks are reported in explanations rather
  than smuggled in through a hard constraint. The optional options keyword keeps api.py call
  signatures working unchanged; api.py-style aliases baseline_nearest_skill,
  baseline_random_feasible and baseline_manual_greedy are exported too.

## Proof command and FULL pasted output

Command (run from C:/Users/shubh/Projects/sewacircle/backend):

C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q tests/solver/test_metrics.py tests/solver/test_baselines.py

Output:

```
C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pytest_asyncio\plugin.py:306: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to "function" scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
................                                                         [100%]
16 passed in 0.05s
```

Note: the double quotes above are part of the verbatim pytest output, not authored prose.

## Full-suite command and output

Command (same workdir):

C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q .

The run printed 1,134,196 characters (55,172 lines), so the exact head and tail of the captured
output are pasted below with a marked truncation. Full raw log:
C:\Users\shubh\AppData\Local\hermes\profiles\res-s2\cache\terminal-output\out-1795024538-28608-2780.log

```
C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pytest_asyncio\plugin.py:306: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to "function" scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
........................................................................ [  2%]
............................................................F.....FFFFFF [  5%]
FFFF.FFFFFFFFFF.FFFFFFFFFF.FFFFFFFFFF.FFFFFFFFFF.FFFFFFFFFF.FFFFFFFFFF.F [  8%]
... [exact middle omitted here; see the raw log path above] ...
FAILED tests/solver/test_factories.py::test_parametrized_seed_fixture_shape[249-8]
FAILED tests/solver/test_factories.py::test_parametrized_seed_fixture_shape[249-9]
FAILED tests/solver/test_factories.py::test_scarce_skill_knob_produces_unfillable_role
FAILED tests/solver/test_factories.py::test_minor_consent_knobs_reachable - p...
FAILED tests/solver/test_factories.py::test_minors_blocked_when_task_disallows_them
FAILED tests/solver/test_factories.py::test_minor_with_consent_can_be_eligible
FAILED tests/solver/test_factories.py::test_min_level_and_role_count_knobs_reachable
2496 failed, 174 passed, 60 warnings in 48.14s
```

A grep over the raw log printed `2496 FAILED tests/solver/test_factories.py` and nothing else: every
full-suite failure came from tests/solver/test_factories.py (a file owned by a different subagent,
being written in parallel), for example:

```
    def test_full_case_is_deterministic():
        a = make_random_case(17, n_volunteers=20)
        b = make_random_case(17, n_volunteers=20)
>       assert [x.model_dump() for x in a] == [x.model_dump() for x in b]
E       AttributeError: 'list' object has no attribute 'model_dump'

    def test_parametrized_seed_fixture_shape(solver_seed_param, seed):
>       assert solver_seed_param == seed
E       assert 0 == 1
```

No failure in the raw log names test_metrics.py or test_baselines.py. The targeted proof command
above is green; the full suite was red at the time of this run for reasons outside the five files
owned by this subagent.

### Later full-suite rerun (same command, after the other subagent edited its factories)

The same command was rerun from the same workdir. Exact printed summary:

```
5 failed, 415 passed, 60 warnings in 4.01s
```

A grep over that rerun printed `5 FAILED tests/solver/test_factories.py` and no other file. The
five failing tests were test_scarce_skill_knob_produces_unfillable_role,
test_minor_consent_knobs_reachable, test_minors_blocked_when_task_disallows_them,
test_minor_with_consent_can_be_eligible and test_min_level_and_role_count_knobs_reachable, all in
tests/solver/test_factories.py. First printed failure detail:

```
    def test_scarce_skill_knob_produces_unfillable_role():
        task, people, options = make_random_case(
            11, n_volunteers=40,
            volunteer_kwargs={"scarce_skills": ("first_aid",), "scarcity_rate": 1.0},
            force_scarce_skill=True, min_level=1,
        )
>       assert task.roles[0].required_skills == ["first_aid"]
E       AssertionError: assert ['disaster_response'] == ['first_aid']
```

Neither the first run nor the rerun showed a failure in the two test files owned by this subagent.

## Assumptions

- Self-declared skills have no stored level, so they count for any role min_level and are flagged.
  If CP-SAT chooses a stricter interpretation, change is_eligible in metrics.py (one place) so
  solver, baselines and metrics stay aligned.
- Baselines fill both must and should roles; robustness checks must slots only, as specified.
- Baselines have an extra optional options keyword for forced_in/forced_out; api.py signatures
  remain callable unchanged.
- solve_ms is wall-clock and is deliberately excluded from determinism comparisons.
- Tiny equator-coordinate fixtures are synthetic and test-only; no real people or places.

## Needed schema changes (request only; read-only files were not edited)

- None required for this deliverable.
- Optional follow-up for the head: store a level for self_declared_skills (or a documented default)
  so min_level can be checked literally instead of using the documented any-level convention.
- Optional follow-up: add forced_in/forced_out to TaskSpec so baselines can honour them without
  RosterOptions; today the optional options argument covers this.
