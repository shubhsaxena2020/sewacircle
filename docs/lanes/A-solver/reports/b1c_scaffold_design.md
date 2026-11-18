# B1c report - property-test scaffolding and solver DESIGN

## Files written

- backend/tests/solver/factories.py
- backend/tests/solver/conftest.py
- backend/tests/solver/test_factories.py
- docs/lanes/A-solver/DESIGN.md

No other files were edited. No existing conftest.py existed, so the new one is purely additive; it defines only solver_-prefixed fixtures and mutates no global state.

## Generator API summary

All generators are deterministic (stdlib `random.Random(seed)`), valid against `app.schemas`, use only `app.taxonomy` skill and slot ids, and import nothing from synth.py, metrics.py, baselines.py or cp_sat.py.

- `make_random_volunteers(n, seed, *, scarce_skills, scarcity_rate, minor_fraction, no_consent_fraction, skill_richness, travel_km, exposure_tail)` -> list of valid synthetic `Volunteer`. Can emit minors with consent True or False, scarce-skill volunteers, heavy repeat-pickers, self-declared skills, multiple districts/blocks.
- `make_random_task(seed, *, slot, slots, district, block, remote, scarce_skills, force_scarce_skill, min_level, role_count, max_travel_km, allow_minors, forced_in, forced_out, time_limit_s, options_seed)` -> `(TaskSpec, RosterOptions)`. Can emit remote blocks, tight travel limits, forced scarce skills, varied slots, forced_in/forced_out ids.
- `make_random_case(seed, *, n_volunteers, volunteer_kwargs, **task_kwargs)` -> `(TaskSpec, list[Volunteer], RosterOptions)`: convenience wrapper that also guarantees every volunteer lists the task slot as available, so cases are not trivially infeasible on availability. Volunteer knobs go in `volunteer_kwargs`; task knobs go directly as keyword args.
- `haversine_km(lat1, lon1, lat2, lon2)` -> great-circle km, stdlib only.
- `volunteer_is_eligible(volunteer, task, role, options)` -> single-volunteer check of availability, skill/level (self-declared allowed), travel and minor consent, plus forced_out; `needs_experienced` is deliberately not treated as hard.
- `validate_case(task, volunteers, options)` -> list of internal-consistency problems; empty list means consistent. Unfillable roles are reported with a `warn:` prefix because they are valid adversarial cases, and a minor without consent is valid input data.
- `validate_instances(seed_start, seed_end, *, n_volunteers)` -> batch check returning only hard failures.
- Constants: `VALID_SEED_COUNT = 250`, `SCARCE_DEFAULT`, `DISTRICT_ANCHORS`, `SLOT_IDS`.

Fixtures in conftest.py: `solver_seed`, `solver_case_factory`, `solver_case`, `solver_validator`, `solver_seed_param` (parametrized over the seed sweep).

## Proof command and FULL pasted output

Command run from `C:/Users/shubh/Projects/sewacircle/backend`:

    C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q tests/solver/test_factories.py

Full pasted output:

    C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pytest_asyncio\plugin.py:306: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
    The event loop scope for asynchronous fixtures will default to the fixture scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to "function" scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.

      warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
    ........................................................................ [ 26%]
    ........................................................................ [ 53%]
    ........................................................................ [ 80%]
    .....................................................                    [100%]
    269 passed in 0.67s

The shell also printed `EXIT=0` after the pytest output. Result: green.

## Full-suite command and FULL pasted output

Command run from `C:/Users/shubh/Projects/sewacircle/backend`:

    C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q .

Full pasted output (tail shown by the shell; the complete pytest output is pasted here):

    C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pytest_asyncio\plugin.py:306: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
    The event loop scope for asynchronous fixtures will default to the fixture scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to "function" scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.

      warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
    ........................................................................ [ 17%]
    ........................................................................ [ 34%]
    ........................................................................ [ 51%]
    ........................................................................ [ 68%]
    ........................................................................ [ 85%]
    ............................................................                 [100%]
    ============================== warnings summary ===============================
    ..\.venv\Lib\site-packages\fastapi\testclient.py:1
      C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
        from starlette.testclient import TestClient as TestClient  # noqa

    tests/evidence/test_rules.py: 59 warnings
      C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pydantic\main.py:280: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
        validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)

    -- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
    420 passed, 60 warnings in 3.14s

The shell also printed `EXIT=0`. Result: green. Other workers had added test files by the time the full suite ran; all collected tests passed.

## Assumptions

- A minor without `guardian_consent` is valid input data, not an invalid instance; the solver must exclude that volunteer. Same for an otherwise-unfillable role: valid adversarial input, reported by `validate_case` with a `warn:` prefix.
- Self-declared skills are allowed but must be flagged. The scaffolding treats them as satisfying `min_level` because the schema stores no level for them; B2 may refine this.
- `needs_experienced` is an objective factor, not a hard constraint, because TASK.md places mentor pairing in the fairness objective. The eligibility helper does not filter on it.
- District anchors in factories.py are synthetic test points in a UP-like bounding box, not authoritative geography. Lane C research may replace them later; this file stays self-contained.
- DESIGN.md contains no numeric solver weights. Exact weights, and whether the ladder is implemented lexicographically, belong to B2/B3. Research docs were empty at the time of writing.
- The proof tests only the generator and the consistency checker. Solver hard-constraint compliance over the seed sweep is B2 work; this scaffolding does not claim it.
