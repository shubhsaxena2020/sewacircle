"""Self-contained, stdlib-only random-instance factories for Lane A property tests.

Every object returned here is a *valid* pydantic schema object from app.schemas and
uses only taxonomy ids from app.taxonomy. No other lane module is imported, so this
file remains usable while synth.py / cp_sat.py / metrics.py are being written.

All generation is driven by `random.Random(seed)`; equal seeds give equal objects.
All people are SYNTHETIC. Coordinates are synthetic points near a fixed UP-like
bounding box; they are illustrative test data, not real locations.
"""
from __future__ import annotations

import math
import random
from typing import Any

from app.schemas import RoleSpec, RosterOptions, TaskSpec, Volunteer
from app.taxonomy import SKILLS, SLOTS

SYNTHETIC_LABEL = "SYNTHETIC DATA - illustrative, no real people"

# Property-test sweep size. Tests use >= 200 distinct seeds (TASK.md batch 1/7).
VALID_SEED_COUNT = 250

# Synthetic district anchors (lat, lon) inside Uttar Pradesh-like bounds.
# Test scaffolding only; NOT a source of real administrative geography.
DISTRICT_ANCHORS: dict[str, tuple[float, float]] = {
    "Lucknow": (26.85, 80.95),
    "Kanpur Dehat": (26.43, 79.84),
    "Kanpur Nagar": (26.45, 80.33),
    "Unnao": (26.55, 80.25),
    "Rae Bareli": (26.23, 81.24),
    "Sitapur": (27.55, 80.18),
    "Hardoi": (27.40, 80.00),
    "Barabanki": (26.92, 81.15),
    "Mathura": (27.49, 77.67),
    "Agra": (27.16, 78.01),
}

# Blocks used for "remote" scenarios: far from the district anchor.
REMOTE_BLOCK_PREFIX = "remote_"
SKILL_IDS: tuple[str, ...] = tuple(SKILLS)
SLOT_IDS: tuple[str, ...] = tuple(SLOTS)

# Skills deliberately made scarce by default, matching the product brief.
SCARCE_DEFAULT: tuple[str, ...] = ("first_aid", "dialect_awadhi", "disaster_response")

# A coherent ordering for varied-slot generation.
_ADVANCE_SLOT = {"mon": "tue", "tue": "wed", "wed": "thu", "thu": "fri",
                 "fri": "sat", "sat": "sun", "sun": "mon"}


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------
def _rng(seed: int) -> random.Random:
    return random.Random(seed)


def _required_skills_choice(rng: random.Random, scarce_skills: tuple[str, ...]) -> str:
    """Pick a skill, biased towards scarce ones so hard instances are reachable."""
    pool: tuple[str, ...] = tuple(scarce_skills) if scarce_skills else SKILL_IDS
    if pool and rng.random() < 0.6:
        return rng.choice(pool)
    return rng.choice(SKILL_IDS)


def _point_near(anchor: tuple[float, float], km: float, rng: random.Random) -> tuple[float, float]:
    """Synthetic jitter around an anchor. 1 deg lat ~= 111 km; lon scaled by cos(lat)."""
    dlat = rng.uniform(-km, km) / 111.0
    lon_scale = max(0.5, math.cos(math.radians(anchor[0])))
    dlon = rng.uniform(-km, km) / (111.0 * lon_scale)
    return round(anchor[0] + dlat, 6), round(anchor[1] + dlon, 6)


def _anchor_for(district: str) -> tuple[float, float]:
    return DISTRICT_ANCHORS.get(district, DISTRICT_ANCHORS["Lucknow"])


def _clamped(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


# ---------------------------------------------------------------------------
# volunteers
# ---------------------------------------------------------------------------
def make_random_volunteers(
    n: int,
    seed: int,
    *,
    scarce_skills: tuple[str, ...] = SCARCE_DEFAULT,
    scarcity_rate: float = 0.85,
    minor_fraction: float = 0.10,
    no_consent_fraction: float = 0.04,
    skill_richness: tuple[int, int] = (1, 5),
    travel_km: float = 30.0,
    exposure_tail: bool = True,
) -> list[Volunteer]:
    """Create n valid synthetic volunteers deterministically.

    Args:
        n: number of volunteers (>= 0).
        seed: RNG seed.
        scarce_skills: skills withheld from most volunteers.
        scarcity_rate: probability a volunteer does NOT hold a scarce skill.
        minor_fraction: approximate share of volunteers aged 16-17.
        no_consent_fraction: share of minors with guardian_consent=False.
        skill_richness: inclusive range of distinct skills per volunteer.
        travel_km: max synthetic jitter from the district anchor.
        exposure_tail: create a few heavy repeat-picks (times_picked_last_90d >= 6).

    Returns:
        List of pydantic Volunteer objects, each with synthetic=True and a
        display name that visibly labels the data as synthetic.
    """
    if n < 0:
        raise ValueError("n must be >= 0")
    rng = _rng(seed)
    scarce = set(scarce_skills)
    districts = list(DISTRICT_ANCHORS)
    people: list[Volunteer] = []

    for i in range(n):
        district = rng.choice(districts)
        anchor = _anchor_for(district)
        lat, lon = _point_near(anchor, travel_km, rng)
        is_minor = rng.random() < minor_fraction
        age = rng.randint(16, 17) if is_minor else rng.randint(18, 35)
        if is_minor:
            consent = rng.random() >= no_consent_fraction
        else:
            consent = None if rng.random() < 0.5 else True

        n_skills = rng.randint(skill_richness[0], skill_richness[1])
        chosen: set[str] = set()
        guard = 0
        while len(chosen) < n_skills and guard < 50:
            guard += 1
            skill = _required_skills_choice(rng, scarce_skills)
            if scarce and skill in scarce and rng.random() < scarcity_rate:
                continue
            chosen.add(skill)
        if not chosen:  # keep every volunteer at least minimally useful
            chosen.add(rng.choice(SKILL_IDS))
        skills = {s: rng.randint(1, 3) for s in sorted(chosen)}

        self_declared: list[str] = []
        if rng.random() < 0.15:
            extra = rng.choice(SKILL_IDS)
            if extra not in skills:
                self_declared = [extra]

        past = rng.randint(0, 10)
        heavy = exposure_tail and i < max(1, n // 10) and rng.random() < 0.7
        times = rng.randint(6, 11) if heavy else rng.randint(0, 5)

        people.append(Volunteer(
            id=f"v{seed}_{i:04d}",
            display_name=f"SYNTH V{i:04d} (seed {seed})",
            age=age,
            gender=rng.choice(["F", "M", "X", "undisclosed"]),
            district=district,
            block=rng.choice(["central", "east", "west", "north", "south"]),
            lat=lat,
            lon=lon,
            skills=skills,
            self_declared_skills=self_declared,
            languages=[s for s in ("hi", "en") if rng.random() < 0.7] or ["hi"],
            available_slots=rng.sample(SLOT_IDS, k=rng.randint(1, 6)),
            has_vehicle=rng.random() < 0.3,
            past_drives=past,
            times_picked_last_90d=times,
            guardian_consent=consent,
            synthetic=True,
        ))
    return people


# ---------------------------------------------------------------------------
# tasks
# ---------------------------------------------------------------------------
def make_random_task(
    seed: int,
    *,
    slot: str | None = None,
    slots: tuple[str, ...] | None = None,
    district: str | None = None,
    block: str | None = None,
    remote: bool | None = None,
    scarce_skills: tuple[str, ...] = SCARCE_DEFAULT,
    force_scarce_skill: bool | None = None,
    min_level: int | None = None,
    role_count: int | None = None,
    max_travel_km: float | None = None,
    allow_minors: bool | None = None,
    forced_in: tuple[str, ...] = (),
    forced_out: tuple[str, ...] = (),
    time_limit_s: float | None = None,
    options_seed: int | None = None,
) -> tuple[TaskSpec, RosterOptions]:
    """Create one valid synthetic task and its RosterOptions, deterministically.

    Returns:
        (task, options). Every skill id is from the taxonomy and every slot is
        from taxonomy.SLOTS. `forced_in`/`forced_out` are passed through verbatim
        (the caller supplies volunteer ids from make_random_volunteers).
    """
    rng = _rng(seed)
    district = district or rng.choice(list(DISTRICT_ANCHORS))
    anchor = _anchor_for(district)
    is_remote = remote if remote is not None else rng.random() < 0.35
    block = block or ((REMOTE_BLOCK_PREFIX + "hills") if is_remote else rng.choice(
        ["central", "east", "west", "north", "south"]))
    # Remote blocks are placed much further from the anchor; the solver must
    # reject most volunteers on travel distance when travel_km is tight.
    center = _point_near(anchor, 90.0 if is_remote else 20.0, rng)

    if slots is not None:
        chosen_slots = tuple(slots)
    elif slot is not None:
        chosen_slots = (slot,)
    else:
        start = rng.choice(SLOT_IDS)
        day, part = start.split("_", 1)
        chosen_slots = (start,) if rng.random() < 0.6 else (
            start, f"{_ADVANCE_SLOT[day]}_{part}")

    rc = role_count if role_count is not None else rng.randint(1, 4)
    skills_for_roles: list[str] = []
    force_scarce = (rng.random() < 0.45) if force_scarce_skill is None else force_scarce_skill
    for r in range(rc):
        if force_scarce and r == 0:
            skills_for_roles.append(rng.choice(scarce_skills) if scarce_skills else "first_aid")
        else:
            skills_for_roles.append(_required_skills_choice(rng, scarce_skills))
    lvl = min_level if min_level is not None else rng.choice([1, 1, 2, 3])

    # Every role has at least one taxonomy skill; the forced-scarce role gets
    # exactly one so adversarial tests can make it provably unfillable.
    skills_per_role = [
        [s] if (force_scarce and i == 0) else list(dict.fromkeys([s, rng.choice(SKILL_IDS)]))
        for i, s in enumerate(skills_for_roles)
    ]
    roles = [
        RoleSpec(
            id=f"r{i}",
            role=f"synthetic_role_{i}",
            count=rng.randint(1, 2),
            required_skills=skills_per_role[i],
            min_level=lvl if min_level is not None else rng.randint(1, 3),
            priority="must" if rng.random() < 0.8 else "should",
            needs_experienced=rng.random() < 0.3,
            evidence_span="",
            confidence=rng.choice(["high", "medium", "low"]),
        )
        for i in range(rc)
    ]
    if not roles:
        roles = [RoleSpec(id="r0", role="synthetic_role_0", count=1,
                          required_skills=["first_aid"], min_level=1, priority="must")]

    travel = max_travel_km if max_travel_km is not None else _clamped(
        rng.choice([3.0, 5.0, 8.0, 15.0, 40.0, 90.0]), 0.5, 500.0)
    allow = allow_minors if allow_minors is not None else rng.random() < 0.75
    limit = time_limit_s if time_limit_s is not None else rng.choice([1.0, 5.0, 10.0])

    task = TaskSpec(
        id=f"task_{seed}",
        title=f"Synthetic task seed {seed}",
        brief_text=f"{SYNTHETIC_LABEL}. Generated by tests.solver.factories.",
        language=rng.choice(["hi", "en", "hinglish"]),
        slot=chosen_slots[0],
        district=district,
        block=block,
        lat=center[0],
        lon=center[1],
        team_size=sum(r.count for r in roles),
        max_travel_km=travel,
        allow_minors=allow,
        roles=roles,
        synthetic=True,
    )
    options = RosterOptions(
        fairness=rng.random() < 0.8,
        resilience=rng.random() < 0.8,
        mentor_pairing=rng.random() < 0.7,
        forced_in=list(forced_in),
        forced_out=list(forced_out),
        time_limit_s=limit,
        seed=options_seed if options_seed is not None else seed,
    )
    return task, options


def make_random_case(
    seed: int,
    *,
    n_volunteers: int | None = None,
    volunteer_kwargs: dict[str, Any] | None = None,
    **task_kwargs: Any,
) -> tuple[TaskSpec, list[Volunteer], RosterOptions]:
    """Convenience: (task, volunteers, options) with the task slot guaranteed present.

    `task_kwargs` are forwarded to make_random_task; `volunteer_kwargs` are
    forwarded to make_random_volunteers (use this for scarcity/consent knobs).
    The volunteers' available_slots are patched (deterministically, using the
    seed) to include the task slot, so a random case is not trivially infeasible
    for availability alone. Adversarial knobs still apply.
    """
    task, options = make_random_task(seed, **task_kwargs)
    n = n_volunteers if n_volunteers is not None else 12 + seed % 25
    people = make_random_volunteers(n, seed + 1, **(volunteer_kwargs or {}))
    for person in people:
        if task.slot not in person.available_slots:
            person.available_slots = sorted(person.available_slots + [task.slot])
    return task, people, options


# ---------------------------------------------------------------------------
# consistency checks
# ---------------------------------------------------------------------------
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km (stdlib only)."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def volunteer_is_eligible(volunteer: Volunteer, task: TaskSpec, role: RoleSpec,
                         options: RosterOptions | None = None) -> bool:
    """Return True iff volunteer may fill one slot of role under hard constraints."""
    if volunteer.id in (options.forced_out if options else []):
        return False
    if task.slot not in volunteer.available_slots:
        return False
    if volunteer.is_minor and not (task.allow_minors and volunteer.guardian_consent is True):
        return False
    if haversine_km(volunteer.lat, volunteer.lon, task.lat, task.lon) > task.max_travel_km + 1e-9:
        return False
    if any(s not in SKILLS for s in role.required_skills):
        return False
    if role.required_skills:
        confirmed = any(volunteer.skills.get(s, 0) >= role.min_level for s in role.required_skills)
        # INFERENCE: a self-declared skill is allowed but must be flagged; it has
        # no level, so we accept it as satisfying min_level for scaffolding only.
        declared = any(s in volunteer.self_declared_skills for s in role.required_skills)
        if not (confirmed or declared):
            return False
    # NOTE: needs_experienced is an objective/fairness factor, NOT a hard
    # constraint in the Lane A contract, so it is deliberately not checked here.
    return True


def validate_case(task: TaskSpec, volunteers: list[Volunteer],
                  options: RosterOptions | None = None) -> list[str]:
    """Return a list of internal-consistency problems; empty list means consistent.

    Checks schema invariants, unique ids, taxonomy ids, slot membership,
    forced_in/forced_out disjointness and existence, minor-consent consistency,
    and _warning_ messages for roles with no locally eligible volunteer. An
    infeasible role is a legitimate adversarial case, so it is reported with a
    'warn:' prefix rather than treated as an invalid instance.
    """
    problems: list[str] = []
    if not task.roles:
        problems.append("task has no roles")
    ids = [v.id for v in volunteers]
    if len(ids) != len(set(ids)):
        problems.append("duplicate volunteer ids")
    if task.slot not in SLOT_IDS:
        problems.append(f"task slot not in taxonomy: {task.slot}")
    for role in task.roles:
        if not role.id:
            problems.append("role with empty id")
        if any(s not in SKILLS for s in role.required_skills):
            problems.append(f"role {role.id} has non-taxonomy skill")
    for v in volunteers:
        # A minor WITHOUT consent is valid input data: the solver must exclude
        # that person (hard constraint), but the instance itself is consistent.
        if any(s not in SKILLS for s in v.skills):
            problems.append(f"volunteer {v.id} has non-taxonomy skill")
        if any(s not in SKILLS for s in v.self_declared_skills):
            problems.append(f"volunteer {v.id} has non-taxonomy self-declared skill")
        for s in v.available_slots:
            if s not in SLOT_IDS:
                problems.append(f"volunteer {v.id} has non-taxonomy slot {s}")
    if options is not None:
        fin, fout = set(options.forced_in), set(options.forced_out)
        if fin & fout:
            problems.append("forced_in and forced_out overlap")
        for vid in fin | fout:
            if vid not in ids:
                problems.append(f"forced id does not exist: {vid}")
        if options.time_limit_s <= 0:
            problems.append("time_limit_s must be positive")
        for role in task.roles:
            eligible = [v for v in volunteers if volunteer_is_eligible(v, task, role, options)]
            if len(eligible) < role.count:
                problems.append(
                    f"warn: role {role.id} has {len(eligible)} eligible volunteers, needs {role.count}")
    return problems


def validate_instances(seed_start: int, seed_end: int, *, n_volunteers: int = 25) -> list[str]:
    """Batch-check a range of seeds; returns ['seed: problem', ...] for hard failures only."""
    bad: list[str] = []
    for seed in range(seed_start, seed_end):
        task, people, options = make_random_case(seed, n_volunteers=n_volunteers)
        for problem in validate_case(task, people, options):
            if not problem.startswith("warn:"):
                bad.append(f"seed {seed}: {problem}")
    return bad
