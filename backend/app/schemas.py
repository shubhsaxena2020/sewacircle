"""THE CONTRACT. Shared pydantic models for every lane. Do not change a field name or type without the head's approval;
adding OPTIONAL fields (with defaults) is allowed only via the head."""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from .taxonomy import SAFETY_CRITICAL_SKILLS, SKILLS, SLOTS

Gender = Literal["F", "M", "X", "undisclosed"]
Language = Literal["hi", "en", "hinglish"]
Method = Literal["cp_sat", "nearest_skill", "random_feasible", "manual_greedy"]
CardStatus = Literal["draft", "flagged", "revision_requested", "confirmed", "corrected", "rejected"]


# ---------------- localized display text (Hindi/English) ----------------
class SkillLabel(BaseModel):
    id: str
    label: str


class RoleDisplay(BaseModel):
    role_id: str
    role: str          # role name in the requested language
    count: int
    required_skills: list[SkillLabel] = Field(default_factory=list)


class TaskDisplay(BaseModel):
    """Localized copy of a task's display text. Ids, counts and decisions are unchanged."""
    lang: Literal["en", "hi"]
    title: str
    slot: str
    roles: list[RoleDisplay] = Field(default_factory=list)


class RecruitDisplay(BaseModel):
    role_id: str
    role: str
    needed: int
    text: str


class AssignmentDisplay(BaseModel):
    volunteer_id: str
    role_id: str
    text: str


class RosterDisplay(BaseModel):
    """Localized rendering of a roster's verdict, explanations and repair asks.

    ``ready`` is copied from the roster, never re-decided; ``recruit[].needed`` and the numbers inside
    every sentence come from the same structured fields, so English and Hindi cannot disagree.
    """
    lang: Literal["en", "hi"]
    ready: Optional[bool] = None
    verdict: str = ""
    explanations: list[str] = Field(default_factory=list)
    recruit: list[RecruitDisplay] = Field(default_factory=list)
    assignments: list[AssignmentDisplay] = Field(default_factory=list)


class Volunteer(BaseModel):
    """SYNTHETIC volunteer opt-in card. Never real people."""
    id: str
    display_name: str
    age: int = Field(ge=15, le=70)
    gender: Gender = "undisclosed"
    district: str
    block: str
    lat: float
    lon: float
    skills: dict[str, int] = Field(default_factory=dict, description="skill id -> level 1..3 (1 basic, 3 expert)")
    self_declared_skills: list[str] = Field(default_factory=list, description="skills not yet host-confirmed")
    languages: list[str] = Field(default_factory=list)
    available_slots: list[str] = Field(default_factory=list)
    has_vehicle: bool = False
    past_drives: int = 0
    times_picked_last_90d: int = 0
    guardian_consent: Optional[bool] = None  # required True if age < 18
    opted_in_task_ids: list[str] = Field(default_factory=list, description="Ready Crew: drives this volunteer chose to join")
    synthetic: bool = True

    @field_validator("skills")
    @classmethod
    def _skills_valid(cls, v: dict[str, int]) -> dict[str, int]:
        for k, lvl in v.items():
            if k not in SKILLS:
                raise ValueError(f"unknown skill {k}")
            if lvl not in (1, 2, 3):
                raise ValueError("skill level must be 1..3")
        return v

    @field_validator("available_slots")
    @classmethod
    def _slots_valid(cls, v: list[str]) -> list[str]:
        bad = [s for s in v if s not in SLOTS]
        if bad:
            raise ValueError(f"unknown slots {bad}; use taxonomy.SLOTS")
        return v

    @field_validator("lat")
    @classmethod
    def _lat(cls, v: float) -> float:
        if not -90 <= v <= 90:
            raise ValueError("lat out of range")
        return v

    @field_validator("lon")
    @classmethod
    def _lon(cls, v: float) -> float:
        if not -180 <= v <= 180:
            raise ValueError("lon out of range")
        return v

    @field_validator("past_drives", "times_picked_last_90d")
    @classmethod
    def _nonneg(cls, v: int) -> int:
        if v < 0:
            raise ValueError("must be >= 0")
        return v

    @property
    def is_minor(self) -> bool:
        return self.age < 18

    @property
    def is_novice(self) -> bool:
        return self.past_drives < 3

    @property
    def can_mentor(self) -> bool:
        return self.past_drives >= 5


class RoleSpec(BaseModel):
    id: str
    role: str
    count: int = Field(ge=1, le=10)
    required_skills: list[str] = Field(default_factory=list, description="any-of; taxonomy ids")
    min_level: int = Field(default=1, ge=1, le=3)
    priority: Literal["must", "should"] = "must"
    needs_experienced: bool = False
    evidence_span: str = ""
    confidence: Literal["high", "medium", "low"] = "high"
    safety_critical: bool = False   # self-declared skills never qualify; only host-checked skill levels count
    unresolved: bool = False        # AI could not map the role to known skills: nobody is assigned until an organiser decides

    @field_validator("required_skills")
    @classmethod
    def _skills_in_taxonomy(cls, v: list[str]) -> list[str]:
        bad = [s for s in v if s not in SKILLS]
        if bad:
            raise ValueError(f"unknown skills {bad}")
        return v  # empty list = open to any volunteer, unless unresolved=True

    @model_validator(mode="after")
    def _auto_safety_critical(self) -> "RoleSpec":
        if set(self.required_skills) & SAFETY_CRITICAL_SKILLS:
            self.safety_critical = True   # cannot be switched off for first aid, disaster response, driving
        return self


class TaskSpec(BaseModel):
    id: str
    title: str
    brief_text: str = ""
    language: Language = "en"
    slot: str = "sat_morning"
    district: str
    block: str
    lat: float
    lon: float
    team_size: Optional[int] = None
    max_travel_km: float = 15.0
    allow_minors: bool = True
    roles: list[RoleSpec] = Field(default_factory=list)
    display: Optional[TaskDisplay] = None   # localized text for GET /api/tasks; canonical fields stay as written
    synthetic: bool = True

    @field_validator("slot")
    @classmethod
    def _slot_valid(cls, v: str) -> str:
        if v not in SLOTS:
            raise ValueError(f"unknown slot {v}; use taxonomy.SLOTS")
        return v


# ---------------- public drive summary (opaque share keys) ----------------
class SharedRoleCount(BaseModel):
    """One role in a public summary: what the drive needs, never who fills it."""
    role: str
    count: int
    required_skills: list[str] = Field(default_factory=list)
    safety_critical: bool = False


class DriveShareSummary(BaseModel):
    """Public, read-only view of ONE drive reached through an opaque share key.

    Deliberately has no volunteer id, name, contact field or task id: the key is
    the only handle the holder gets, and the summary is safe to paste into a
    WhatsApp group. When a roster for this drive was computed in this server
    process, the summary is the snapshot of what was actually planned (title,
    roles, ready verdict, ``computed_at``); otherwise it is built from the known
    task with ``ready=None`` and no timestamp.

    ``plan_version`` identifies the plan this summary describes (SHA-256 of roles,
    options and crew). ``stale`` is True when the organiser's latest solved roster
    for the task is a different plan - for example after a dropout healed the crew -
    so a viewer is never told an old verdict is current.
    """
    title: str
    district: str
    block: str
    slot: str
    roles: list[SharedRoleCount] = Field(default_factory=list)
    ready: Optional[bool] = None
    computed_at: Optional[datetime] = None
    plan_version: str = ""
    stale: bool = False
    notice: str = "Public read-only summary of one synthetic drive. No volunteer is named or identified."
    synthetic: bool = True


class DriveStatusRow(BaseModel):
    """One row of the district map: the LAST computed verdict for a task, never a new solve."""
    task_id: str
    ready: Optional[bool] = None          # None = no roster computed for this task in this process
    computed_at: Optional[datetime] = None
    stale: bool = False


class DriveStatus(BaseModel):
    """GET /api/drive/status: read-only summary for the district map, no solver run, no state change."""
    tasks: list[DriveStatusRow] = Field(default_factory=list)
    note: str = ("Reads the last computed verdict per task id. Never runs the planner and never changes state; "
                 "no volunteer is named or identified.")


class ShareLink(BaseModel):
    """What an organiser gets back when minting a public link for one drive."""
    share_key: str
    path: str
    note: str = "Read-only public summary. Anyone holding this key can open it; it names no volunteer."


# ---------------- extraction (LLM) ----------------
class ExtractedRole(BaseModel):
    unresolved: bool = False
    role: str
    count: int = Field(ge=1, le=10)
    required_skills: list[str]
    evidence_span: str = ""
    confidence: Literal["high", "medium", "low"] = "medium"
    reason: str = ""

    @field_validator("required_skills")
    @classmethod
    def _skills_in_taxonomy(cls, v: list[str]) -> list[str]:
        bad = [s for s in v if s not in SKILLS]
        if bad:
            raise ValueError(f"unknown skills {bad}")
        return v


class ExtractionResult(BaseModel):
    roles: list[ExtractedRole]
    needs_decision: list[str] = Field(default_factory=list)
    language_detected: Language = "en"
    model: str = ""
    cached: bool = False
    redactions: int = 0
    notes: list[str] = Field(default_factory=list)


# ---------------- roster (solver) ----------------
class RosterOptions(BaseModel):
    fairness: bool = True          # U2 rotation fairness
    resilience: bool = True        # U1 standby / dropout resilience
    mentor_pairing: bool = True    # U2 novice-mentor pairing
    forced_in: list[str] = Field(default_factory=list)   # volunteer ids that must be included
    forced_out: list[str] = Field(default_factory=list)  # volunteer ids excluded
    opted_in_only: bool = False    # Ready Crew: plan only with volunteers who chose this drive
    time_limit_s: float = 10.0
    seed: int = 7


class PickReason(BaseModel):
    """ONE structured cause for a pick, next to the English sentence it renders.

    The solver writes ``Assignment.reasons`` (English, human readable) AND these codes with their
    parameters. The Hindi view is rendered from the codes, so both languages carry the same facts -
    the same skill and level, the same distance, the same "not picked in N days", the same newcomer
    count and mentor name - instead of Hindi paraphrasing a finished sentence. ``params`` holds only
    primitives, so it survives JSON and can be compared field by field in a test.
    """
    code: Literal["skill_confirmed", "skill_self_declared", "open_role", "slot_and_distance",
                  "not_picked_recently", "picked_heavily", "newcomer", "experienced_mentor",
                  "minor_guardian_consent", "promoted_from_standby"]
    params: dict[str, str | int | float] = Field(default_factory=dict)


class Assignment(BaseModel):
    role_id: str
    slot_index: int = 0
    volunteer_id: str
    volunteer_name: str
    score: float = 0.0
    distance_km: float = 0.0
    reasons: list[str] = Field(default_factory=list)
    reason_codes: list[PickReason] = Field(default_factory=list)  # the same reasons, structured, for Hindi
    flags: list[str] = Field(default_factory=list)  # e.g. "self_declared_skill", "novice", "minor_guardian_consent"


class StandbyPick(BaseModel):
    volunteer_id: str
    volunteer_name: str
    covers_role_ids: list[str]
    reason: str = ""


class SlotRef(BaseModel):
    role_id: str
    slot_index: int = Field(ge=0)


class RosterMetrics(BaseModel):
    """DEFINITIONS (head amendment A1, from Codex contract review; every method uses the SAME function):
    role_coverage = filled qualified MUST slots / total MUST slots (each (role_id, slot_index) counted once; 1.0 if no must slots).
    should_coverage = same for 'should' slots (None if there are none).
    robustness = over each assigned volunteer v (single dropout), 1 if a maximum matching from (assigned minus v) plus the roster's
      unique standby pool covers every must slot (each person used once; qualification, availability, travel, consent re-checked),
      else 0; robustness = mean over assigned volunteers (0.0 if nobody assigned, 1.0 if there are no must slots). Dropping a standby is out of scope.
    repeat_pick_share = assigned with times_picked_last_90d >= 3 / assigned (0.0 if nobody assigned).
    exposure_gini = Gini of times_picked_last_90d over the task-ELIGIBLE candidate pool, where selected people get +1 for this pick
      (0.0 if all zero or pool empty); this stops a planner looking fair by choosing only newcomers."""
    role_coverage: float
    slots_filled: int
    slots_required: int
    robustness: float
    repeat_pick_share: float
    exposure_gini: float
    district_spread: int            # distinct (district, block) among assigned
    should_coverage: Optional[float] = None
    novices: int = 0
    mentor_pairs: int = 0
    solve_ms: int = 0
    solver_status: str = ""


class RecruitRequest(BaseModel):
    """Ready Crew repair action: what exactly to recruit to make the crew ready."""
    kind: Literal["unresolved", "unfilled", "standby"] = "unfilled"   # which template produced `reason`
    role_id: str
    role: str
    needed: int
    skills: list[str]
    min_level: int = 1
    checked_skill_required: bool = False
    slot: str
    area: str
    max_travel_km: float
    reason: str
    blocked_by_names: list[str] = Field(default_factory=list)  # standby kind: who is the single point of failure


class RosterResult(BaseModel):
    task_id: str
    method: Method
    assignments: list[Assignment]
    standby: list[StandbyPick] = Field(default_factory=list)
    unfilled_role_ids: list[str] = Field(default_factory=list)  # derived summary: roles with at least one unfilled MUST slot
    unfilled_slots: list[SlotRef] = Field(default_factory=list)  # exact unfilled (role_id, slot_index) pairs; assignments are unique per pair
    metrics: RosterMetrics
    explanations: list[str] = Field(default_factory=list)
    recruit_requests: list[RecruitRequest] = Field(default_factory=list)
    display: Optional[RosterDisplay] = None   # localized verdict/explanations for POST /api/roster
    ready: Optional[bool] = None    # True only if every must slot is filled AND any single dropout leaves them coverable
    synthetic: bool = True


class Counterfactual(BaseModel):
    """U3: answer to 'why not volunteer X?' by re-solving with X forced in."""
    volunteer_id: str
    volunteer_name: str
    feasible: bool
    narrative: str
    delta_role_coverage: float = 0.0
    delta_robustness: float = 0.0
    displaced_volunteer_ids: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)


class DropoutResult(BaseModel):
    """U1: simulate one volunteer dropping out of the approved roster."""
    task_id: str
    dropped_volunteer_id: str
    healed_with_standby: bool
    replacement_volunteer_id: Optional[str] = None
    uncovered_role_ids: list[str] = Field(default_factory=list)
    roster_after: RosterResult


# ---------------- evidence ledger ----------------
class Flag(BaseModel):
    code: str
    severity: Literal["info", "warn", "block"]
    message: str


class AttendanceRow(BaseModel):
    """One row of the attendance sheet. `hours` = RECORDED hours on site (never the volunteer's claim). Claims live on the card.
    check_in/check_out are ISO-8601 with offset when present; if both are present `hours` must equal their difference (+-0.1 h)."""
    volunteer_id: str
    task_id: str
    hours: float = Field(ge=0, le=24)
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    age: Optional[int] = None
    guardian_consent: Optional[bool] = None


class ContributionCard(BaseModel):
    id: str   # deterministic: f"card-{task_id}-{volunteer_id}-{role_slug}" so retries are idempotent
    task_id: str
    volunteer_id: str
    role: str
    claimed_hours: float = Field(ge=0, le=24)
    recorded_hours: Optional[float] = Field(default=None, ge=0, le=24)   # from the attendance sheet
    summary: str = ""
    evidence_refs: list[str] = Field(default_factory=list)
    status: CardStatus = "draft"
    flags: list[Flag] = Field(default_factory=list)
    drafted_by: Literal["ai", "human"] = "ai"
    confirmed_by: Optional[str] = None
    revision_reason: Optional[str] = None   # set by request_revision, cleared by the next re-draft
    created_at: datetime = Field(default_factory=datetime.utcnow)
    synthetic: bool = True


class LedgerEntry(BaseModel):
    index: int
    ts: datetime
    action: Literal["draft", "flag", "confirm", "correct", "reject", "request_revision", "export"]
    card_id: str
    actor: str
    reason: str = ""   # why the actor moved the card; hashed when non-empty
    payload_hash: str
    prev_hash: str
    entry_hash: str


class LedgerVerification(BaseModel):
    ok: bool
    entries: int
    first_bad_index: Optional[int] = None
    note: str = "Hash chain shows edits, not truth; truth comes from host confirmation."


# ---------------- capability menu (demo roles, not authentication) ----------------
class CapabilitySet(BaseModel):
    """What one DEMO role may open and do. demo_only is always True: the caller picks its own role."""
    role: str
    screens: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    demo_only: bool = True
    note: str = ""


# ---------------- evaluation ----------------
class EvalRow(BaseModel):
    task_id: str
    method: Method
    role_coverage: float
    robustness: float
    repeat_pick_share: float
    exposure_gini: float
    solve_ms: int
    ready: float = 0.0   # 1.0 if the roster is READY (all must slots filled and single-dropout safe), else 0.0


class EvalReport(BaseModel):
    n_tasks: int
    n_volunteers: int
    rows: list[EvalRow]
    summary: dict[str, dict[str, float]]  # method -> metric -> mean
    ci95: dict[str, dict[str, list[float]]] = Field(default_factory=dict)  # method -> metric -> [lo, hi] (bootstrap)
    misses: list[str] = Field(default_factory=list)   # honest list of tasks where we did not beat the baseline
    generated_by: str = ""
    synthetic: bool = True
