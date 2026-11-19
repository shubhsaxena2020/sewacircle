"""FastAPI app. OWNED BY HEAD. Wires lane modules; any unimplemented lane function returns HTTP 501 until its lane lands.
LLM failures map to 502 (the UI then offers manual entry). Local demo only: unauthenticated, 'actor' is a label, not an identity.

Concurrency, stated honestly
----------------------------
This prototype is a SINGLE-PROCESS server: one uvicorn worker, one Python process, one in-memory card store. A
card decision (lookup -> transition -> ledger append -> store -> card-file write) runs under one process-wide
``threading.RLock``, and the card file is replaced atomically, so two hosts clicking "confirm" and "reject" on
the same card at the same moment get exactly one 200 and one 409 - never two decisions for one card.

The lock does NOT survive multiple processes: two uvicorn workers (or gunicorn -w 2) would each have their own
lock, their own in-memory store, and the ledger's own RLock is process-local too, so two writers on one journal
would fork the hash chain. Running more than one worker needs a shared store and a cross-process lock (a database
transaction, or a file lock around the append), which is explicitly out of scope for this prototype.
"""
from __future__ import annotations

import json
import os
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Literal, Optional

import functools
import hashlib
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .evidence import badges, ledger as ledger_mod, rules, transitions
from .llm import extract as llm_extract
from .llm.client import LLMError
from .schemas import (Assignment, AttendanceRow, CapabilitySet, ContributionCard, Counterfactual, DropoutResult,
                      DriveShareSummary, EvalReport, ExtractionResult, LedgerEntry, LedgerVerification, RosterOptions,
                      RosterResult, ShareLink, SharedRoleCount, TaskSpec, Volunteer)
from . import capabilities, i18n, share
from .solver import api as solver
from .taxonomy import DISCLAIMER, SKILLS

DATA_DIR = Path(os.environ.get("SEWA_DATA_DIR", Path(__file__).resolve().parents[1] / "data" / "state"))
CARDS_PATH = DATA_DIR / "cards.json"
_DISTRICTS_JSON = Path(__file__).resolve().parents[2] / "docs" / "research" / "up_districts.json"

app = FastAPI(title="SewaCircle", version="0.1.0-idea-stage-prototype")
_origins = [o.strip() for o in os.environ.get("SEWA_CORS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000,http://127.0.0.1:8000").split(",") if o.strip()]
app.add_middleware(CORSMiddleware, allow_origins=_origins, allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(LLMError)
async def _llm_error(_: Request, exc: LLMError) -> JSONResponse:
    return JSONResponse(status_code=502, content={"detail": f"AI unavailable: {exc}", "code": "llm_unavailable", "hint": "enter the roles manually"})


def _guard(fn: Callable[[], Any]) -> Any:
    try:
        return fn()
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="lane module not implemented yet")


def _demo_role(request: Request) -> str:
    """Read the demo role from X-Demo-Role (default organiser); a demo switch, NOT authentication."""
    try:
        return capabilities.normalise_role(request.headers.get(capabilities.ROLE_HEADER))
    except capabilities.UnknownRole as exc:
        raise HTTPException(403, f"{exc}. This is a demo role switch, not authentication.") from exc


def _require_demo(action: str) -> Callable[[Request], str]:
    """FastAPI dependency: 403 unless the caller's demo role lists ``action``."""
    def dependency(request: Request) -> str:
        role = _demo_role(request)
        if not capabilities.may(role, action):
            raise HTTPException(403, f"the demo role {role!r} may not {action}. "
                                     "This is a demo role switch, not authentication.")
        return role
    return dependency


class _State:
    volunteers: list[Volunteer] | None = None
    tasks: list[TaskSpec] | None = None
    cards: dict[str, ContributionCard] | None = None
    ledger: Optional[ledger_mod.Ledger] = None
    share_snapshots: dict[str, DriveShareSummary] | None = None
    latest_plan: dict[str, str] | None = None
    attendance_rows: dict[str, list[AttendanceRow]] | None = None


S = _State()

#: ONE process-wide lock for every mutation of the card store, the ledger and the card file.
#: A re-entrant lock because a route may call a helper that takes it again in the same thread.
CARD_LOCK = threading.RLock()


def volunteers() -> list[Volunteer]:
    if S.volunteers is None:
        from .data import synth
        S.volunteers = synth.make_volunteers()
    return S.volunteers


def tasks() -> list[TaskSpec]:
    if S.tasks is None:
        from .data import synth
        S.tasks = synth.make_tasks()
    return S.tasks


def share_snapshots() -> dict[str, DriveShareSummary]:
    """What was actually planned per task id, for rosters computed in THIS process (never persisted).

    Kept so the public share route shows the plan the organiser really solved (possibly with edited
    roles), not the server's synthetic task with a verdict from a different plan.
    """
    if S.share_snapshots is None:
        S.share_snapshots = {}
    return S.share_snapshots


def latest_plan() -> dict[str, str]:
    """Plan version of the most recent plan (roster or dropout result) computed for each task id.

    The public snapshot keeps the version of the plan a viewer was given; comparing the two is
    what lets ``GET /api/drive/{key}`` say ``stale: true`` instead of serving an older crew.
    """
    if S.latest_plan is None:
        S.latest_plan = {}
    return S.latest_plan


def attendance_rows() -> dict[str, list[AttendanceRow]]:
    """The attendance sheet rows the last draft for each task was given (in memory, this process only).

    ``correct`` re-runs the deterministic rules, and rules that compare a claim with the recorded
    hours need the sheet. A restart loses this cache; the rules then fall back to each card's
    ``recorded_hours`` (persisted with the card) and say so with a ``no_attendance_record`` warning
    on cards that have neither.
    """
    if S.attendance_rows is None:
        S.attendance_rows = {}
    return S.attendance_rows


def ledger() -> ledger_mod.Ledger:
    if S.ledger is None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        S.ledger = ledger_mod.Ledger(os.environ.get("SEWA_LEDGER_PATH") or str(DATA_DIR / "ledger.jsonl"))
    return S.ledger


def cards() -> dict[str, ContributionCard]:
    """Cards persist next to the ledger so a restart does not make them disagree."""
    if S.cards is None:
        S.cards = {}
        if CARDS_PATH.exists():
            for d in json.loads(CARDS_PATH.read_text(encoding="utf-8")):
                c = ContributionCard.model_validate(d)
                S.cards[c.id] = c
    return S.cards


def _save_cards() -> None:
    """Replace the card file atomically: write a temp file in the same directory, fsync, then os.replace.

    A reader (or a crash) can therefore never observe a half-written cards.json: the rename is atomic on
    the same filesystem. Callers hold :data:`CARD_LOCK`, so two writers cannot interleave.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.dumps([c.model_dump(mode="json") for c in cards().values()], ensure_ascii=False)
    fd, tmp_path = tempfile.mkstemp(prefix=".cards-", suffix=".tmp", dir=str(DATA_DIR))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, CARDS_PATH)
    finally:
        if os.path.exists(tmp_path):     # only on failure; os.replace already consumed it otherwise
            os.unlink(tmp_path)


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "disclaimer": DISCLAIMER, "model": os.environ.get("SEWA_LLM_MODEL", "cc/claude-sonnet-5-5"),
            "llm_mode": os.environ.get("SEWA_LLM_MODE", "record")}


@app.get("/api/meta")
def meta() -> dict:
    return {"disclaimer": DISCLAIMER, "skills": SKILLS}


@app.get("/api/capabilities", response_model=CapabilitySet)
def get_capabilities(role: str = capabilities.DEFAULT_ROLE) -> Any:
    """The screens and actions one DEMO role may use.

    THIS IS A DEMO ROLE SWITCH, NOT AUTHENTICATION. The role is chosen by the caller - this query parameter,
    or the X-Demo-Role header on the mutating routes - and both default to ``organiser`` so existing clients
    keep working. It exists to make the intended division of labour visible and testable (a host confirms
    contribution cards, a viewer only reads the evaluation), and the same matrix is enforced server-side on
    the mutating evidence routes, so the menu and the API cannot disagree. Put a real authenticated identity
    in front of this before it protects anything.
    """
    try:
        return CapabilitySet(**capabilities.capabilities_for(role))
    except capabilities.UnknownRole as exc:
        raise HTTPException(422, str(exc)) from exc


@functools.lru_cache(maxsize=1)
def get_geo_tree() -> dict[str, Any]:
    from .data.synth import BLOCKS
    data = json.loads(_DISTRICTS_JSON.read_text(encoding="utf-8"))
    source_url = data.get("coordinate_source_url") or data.get("source_url", "")
    districts = [
        {
            "name": d["name"],
            "lat": d["lat"],
            "lon": d["lon"],
            "source_record_id": d["source_record_id"],
            "blocks": BLOCKS.get(d["name"], []),
            "blocks_available": d["name"] in BLOCKS,
        }
        for d in data["districts"]
    ]
    return {
        "state": "Uttar Pradesh",
        "source_url": source_url,
        "coordinate_caveat": data.get("coordinate_caveat", ""),
        "retrieved_date": data.get("retrieved_date", ""),
        "blocks_note": "Blocks are listed only for the 4 districts used by the synthetic demo data.",
        "districts": districts,
    }


@functools.lru_cache(maxsize=1)
def _geo_tree_payload() -> tuple[bytes, str]:
    tree = get_geo_tree()
    body = json.dumps(tree, ensure_ascii=False).encode("utf-8")
    etag = f'"{hashlib.sha256(body).hexdigest()}"'
    return body, etag


@app.get("/api/geo/tree")
def geo_tree(request: Request) -> Any:
    """Return geo tree for UP districts with RFC 9110 compliant ETag handling."""
    body, etag = _geo_tree_payload()
    if_none_match = request.headers.get("if-none-match")
    if if_none_match:
        tags = [tag.strip() for tag in if_none_match.split(",")]
        if any(t == "*" or t == etag or t == f"W/{etag}" for t in tags):
            return Response(status_code=304, headers={"ETag": etag})
    return Response(content=body, media_type="application/json", headers={"ETag": etag})


@app.get("/api/volunteers", response_model=list[Volunteer])
def list_volunteers() -> Any:
    return _guard(volunteers)


@app.get("/api/tasks", response_model=list[TaskSpec])
def list_tasks(lang: Literal["en", "hi"] = "en") -> Any:
    """Tasks plus a localized `display` block (title, slot, role names, skill labels).

    The canonical fields are never translated: ids, counts and the task text stay exactly as stored, so
    a client can compare or re-post them. `display` is the same facts in the requested language. An
    unknown title or role name is returned unchanged rather than machine-translated.
    """
    def run() -> list[TaskSpec]:
        return [t.model_copy(update={"display": i18n.task_display(t, lang)}) for t in tasks()]
    return _guard(run)


class ShareReq(BaseModel):
    task_id: str


@app.post("/api/drive/share", response_model=ShareLink)
def create_share(req: ShareReq, demo_role: str = Depends(_require_demo("share_drive"))) -> Any:
    """Mint the opaque public link for one drive (organiser demo role only).

    Without this route a share key could never be obtained, so the read-only summary would be
    unreachable. The task must be one this server knows; the response carries only the key and the
    path a client can hand out. A demo role switch, not authentication - see app/capabilities.py.
    """
    task = next((t for t in tasks() if t.id == req.task_id), None)
    if task is None:
        raise HTTPException(404, "task not found")
    key = share.share_key_for(task.id)
    return ShareLink(share_key=key, path=f"/api/drive/{key}")


@app.get("/api/drive/{share_key}", response_model=DriveShareSummary)
def drive_summary(share_key: str) -> Any:
    """Public, read-only summary of one drive, addressed by an opaque share key - never by a task id.

    ``share_key`` is the first 16 base32 characters of HMAC-SHA256(secret, task id). The secret is
    ``SEWA_SHARE_SECRET`` when that environment variable is set; otherwise a random value is generated
    at first use and kept in memory for this process only, so nothing is written to disk, no secret is
    committed, and a restart invalidates every link the server handed out. Because a key cannot be
    computed without the secret, sequential task ids are useless on this route: anything that is not a
    key derived from this secret is 404, and the task id is never echoed back. The body contains no
    volunteer name, id or contact.
    """
    def run() -> DriveShareSummary:
        known = tasks()
        task_id = share.task_id_for_share_key(share_key, [t.id for t in known])
        if task_id is None:
            raise HTTPException(404, "unknown share link")
        snapshot = share_snapshots().get(task_id)
        if snapshot is not None:
            return snapshot                       # exactly what was planned, including any edited roles
        task = next(t for t in known if t.id == task_id)
        return DriveShareSummary(
            title=task.title,
            district=task.district,
            block=task.block,
            slot=task.slot,
            roles=[SharedRoleCount(role=r.role, count=r.count, required_skills=list(r.required_skills),
                                   safety_critical=r.safety_critical) for r in task.roles],
            ready=None,                           # no roster for this drive in this process yet
        )
    return _guard(run)


class ExtractReq(BaseModel):
    brief_text: str
    language_hint: Optional[str] = None


@app.post("/api/extract-roles", response_model=ExtractionResult)
def extract_roles(req: ExtractReq) -> Any:
    return _guard(lambda: llm_extract.extract_roles(req.brief_text, req.language_hint))


class RosterReq(BaseModel):
    task: TaskSpec
    options: RosterOptions = Field(default_factory=RosterOptions)
    lang: Literal["en", "hi"] = "en"    # display language only; the plan and its numbers are identical


class RosterAll(BaseModel):
    cp_sat: RosterResult
    nearest_skill: RosterResult
    random_feasible: RosterResult
    manual_greedy: RosterResult


@app.post("/api/roster", response_model=RosterAll)
def make_roster(req: RosterReq, demo_role: str = Depends(_require_demo("read_roster"))) -> Any:
    def run() -> RosterAll:
        v = volunteers()
        o = req.options  # every method gets the same candidate pool (opt-in filter included)
        result = RosterAll(cp_sat=solver.build_roster(req.task, v, o),
                           nearest_skill=solver.baseline_nearest_skill(req.task, v, o),
                           random_feasible=solver.baseline_random_feasible(req.task, v, o.seed, o),
                           manual_greedy=solver.baseline_manual_greedy(req.task, v, o))
        # Localized text per method: the same ids, counts and verdict, in the requested language.
        for roster in (result.cp_sat, result.nearest_skill, result.random_feasible, result.manual_greedy):
            roster.display = i18n.roster_display(req.task, roster, req.lang)
        # Snapshot of what was solved, in memory only, so a public share link shows the same plan the
        # organiser saw (title and roles may have been edited). Only ids this server knows are stored:
        # a client cannot grow the dict without bound or advertise a verdict for a drive that does not exist.
        if any(t.id == req.task.id for t in tasks()):
            share_snapshots()[req.task.id] = DriveShareSummary(
                title=req.task.title, district=req.task.district, block=req.task.block, slot=req.task.slot,
                roles=[SharedRoleCount(role=r.role, count=r.count, required_skills=list(r.required_skills),
                                       safety_critical=r.safety_critical) for r in req.task.roles],
                ready=result.cp_sat.ready,
                computed_at=datetime.now(timezone.utc),
            )
        return result
    return _guard(run)


class WhyNotReq(BaseModel):
    task: TaskSpec
    roster: RosterResult
    volunteer_id: str
    options: RosterOptions = Field(default_factory=RosterOptions)


@app.post("/api/roster/why-not", response_model=Counterfactual)
def why_not(req: WhyNotReq, demo_role: str = Depends(_require_demo("read_roster"))) -> Any:
    return _guard(lambda: solver.why_not(req.task, volunteers(), req.roster, req.volunteer_id, req.options))


class DropoutReq(BaseModel):
    task: TaskSpec
    roster: RosterResult
    dropped_volunteer_id: str
    options: RosterOptions = Field(default_factory=RosterOptions)


@app.post("/api/roster/dropout", response_model=DropoutResult)
def dropout(req: DropoutReq, demo_role: str = Depends(_require_demo("read_roster"))) -> Any:
    return _guard(lambda: solver.simulate_dropout(req.task, volunteers(), req.roster, req.dropped_volunteer_id, req.options))


class DraftReq(BaseModel):
    task: TaskSpec
    host_notes: str
    attendance_rows: list[AttendanceRow] = Field(default_factory=list)
    assignments: list[Assignment] = Field(default_factory=list)


@app.post("/api/evidence/draft", response_model=list[ContributionCard])
def draft(req: DraftReq, demo_role: str = Depends(_require_demo("draft_cards"))) -> Any:
    """Idempotent: card ids are deterministic; a card already decided by the host is never overwritten by a re-draft.
    Undecided draft/flagged cards of the same task that are not part of the new draft (for example after a dropout
    moved someone to another role) are superseded: removed from the card store so they cannot trigger false
    duplicate-evidence flags. Their earlier 'draft' entries stay in the ledger history. Host-decided cards are kept.

    Revision back-edge: a card the host sent back with request_revision is re-drafted. The table decides the target:
    ``revision_requested --redraft--> draft`` when the new text is clean, and ``revision_requested --redraft_flagged-->
    flagged`` when the new text raises a warn/block rule flag, so a redraft cannot quietly return a card to the
    undecided pool without the flag the host needs to see. The stale revision reason is cleared either way and the
    ledger records a 'draft' or 'flag' entry whose reason names the revision request.

    Empty drafting is non-destructive: if the drafting step produces no card at all - the model returned an empty
    list, or the caller posted no assignments - the route returns HTTP 502 (assignments were sent) or an empty list
    (nothing was sent) and touches neither the card store nor the ledger. A failed draft must never wipe the cards a
    host is still reviewing.
    """
    def run() -> list[ContributionCard]:
        with CARD_LOCK:
            store = cards()
            drafted = llm_extract.draft_cards(req.task, req.host_notes, req.attendance_rows, req.assignments)
            if not drafted:                       # checked BEFORE anything is removed or written
                if req.assignments:
                    raise HTTPException(502, "the drafting step returned no cards for "
                                             f"{len(req.assignments)} assignment(s); nothing was changed. "
                                             "Retry, or enter the cards manually.")
                return []
            attendance_rows()[req.task.id] = list(req.attendance_rows)
            out: list[ContributionCard] = []
            new_ids = {c.id for c in drafted}
            for stale in [x for x in store.values() if x.task_id == req.task.id and x.id not in new_ids
                          and x.status in ("draft", "flagged", "revision_requested")]:
                del store[stale.id]
            for c in drafted:
                existing = store.get(c.id)
                if existing is not None and existing.status not in ("draft", "flagged", "revision_requested"):
                    out.append(existing)
                    continue
                redrafted = existing is not None and existing.status == "revision_requested"
                c.flags = rules.check_card(c, [x for x in store.values() if x.id != c.id] + out, req.attendance_rows)
                flagged = any(f.severity in ("warn", "block") for f in c.flags)
                if redrafted:                     # the table decides where a redraft may land
                    c.status = transitions.next_state(existing.status, "redraft_flagged" if flagged else "redraft")
                else:
                    c.status = "flagged" if flagged else "draft"
                c.revision_reason = None
                reason = ""
                if redrafted:
                    reason = ("re-drafted after a host revision request; the new text raised a rule flag"
                              if flagged else "re-drafted after a host revision request")
                ledger().append("flag" if c.status == "flagged" else "draft", c, "system", reason)
                store[c.id] = c
                out.append(c)
            _save_cards()
            return out
    return _guard(run)


@app.post("/api/demo/reset")
def demo_reset(demo_role: str = Depends(_require_demo("reset_demo"))) -> dict:
    """Start a clean demo: archive the current card store and ledger (renamed with a timestamp, never deleted).
    Destructive, so the capability matrix allows it for the organiser demo role only."""
    import time
    stamp = time.strftime("%Y%m%d-%H%M%S")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    archived = []
    for p in DATA_DIR.glob("*"):
        if p.is_file() and not p.name.startswith("archive-"):
            p.rename(p.with_name(f"archive-{stamp}-{p.name}"))
            archived.append(p.name)
    S.cards = None
    S.ledger = None
    S.share_snapshots = None
    return {"ok": True, "archived": archived}


@app.get("/api/evidence/cards", response_model=list[ContributionCard])
def list_cards() -> Any:
    return list(cards().values())


class DecisionReq(BaseModel):
    actor: str = "host"                      # demo label, not an authenticated identity
    claimed_hours: Optional[float] = Field(default=None, ge=0, le=24)  # required for correct
    reason: Optional[str] = Field(default=None, max_length=500)        # required for request_revision


def _rule_rows(card: ContributionCard) -> list[AttendanceRow]:
    """Attendance rows for the deterministic rules when re-checking an already drafted card.

    The draft route caches the sheet it was handed; if this process never saw one (a restart, or a card
    written by an older build) the card's own ``recorded_hours`` - which IS the recorded sheet value - is
    turned back into one row, so ``hours_exceed_recorded`` can still compare claim with record.
    """
    cached = attendance_rows().get(card.task_id)
    if cached:
        return list(cached)
    return [AttendanceRow(volunteer_id=c.volunteer_id, task_id=c.task_id, hours=c.recorded_hours)
            for c in cards().values()
            if c.task_id == card.task_id and c.recorded_hours is not None]


def _decide(card_id: str, action: str, req: DecisionReq) -> ContributionCard:
    """Move one card along its state machine; the target state comes from the table, never from here.

    Illegal moves are HTTP 409 with the legal actions named. ``request_revision`` needs a non-blank
    reason, which is stored on the card and folded into the ledger entry's hash.

    The whole sequence - lookup, transition, ledger append, store and atomic card-file write - runs under
    ONE process-wide lock, and the ledger append comes before the store commit. So a simultaneous confirm and
    reject on one card produce exactly one decision and one 409, and a failed append leaves both the card and
    the journal exactly as they were. See the module docstring: this is single-process only.

    ``correct`` re-runs the deterministic rules on the corrected card and stores the new flags, so a host who
    raises or lowers the hours sees the rule verdict for the number they are about to confirm (the status stays
    ``corrected``: the decision is theirs, the flags are evidence).
    """
    with CARD_LOCK:
        c = cards().get(card_id)
        if c is None:
            raise HTTPException(404, "card not found")
        try:
            status = transitions.next_state(c.status, action)
        except transitions.IllegalTransition as exc:
            raise HTTPException(409, str(exc)) from exc
        reason = (req.reason or "").strip()
        if action == "request_revision" and not reason:
            raise HTTPException(422, "reason is required to request a revision")
        updates: dict[str, Any] = {"status": status, "revision_reason": reason if action == "request_revision" else None}
        if action == "correct":
            if req.claimed_hours is None:
                raise HTTPException(422, "claimed_hours is required to correct a card")
            updates["claimed_hours"] = req.claimed_hours
        if status in ("confirmed", "corrected"):
            updates["confirmed_by"] = req.actor
        updated = c.model_copy(update=updates)
        if action == "correct":
            others = [x for x in cards().values() if x.id != updated.id]
            updated.flags = rules.check_card(updated, others, _rule_rows(updated))
        # Append FIRST, then commit: the ledger commits to the post-transition card, and a failed append
        # (for example a corrupt journal) must not leave a decided card that no entry exists for.
        ledger().append(action, updated, req.actor, reason)
        cards()[card_id] = updated
        _save_cards()
        return updated


@app.post("/api/evidence/{card_id}/confirm", response_model=ContributionCard)
def confirm(card_id: str, req: DecisionReq = DecisionReq(),
            demo_role: str = Depends(_require_demo("confirm_card"))) -> Any:
    return _guard(lambda: _decide(card_id, "confirm", req))


@app.post("/api/evidence/{card_id}/correct", response_model=ContributionCard)
def correct(card_id: str, req: DecisionReq = DecisionReq(),
            demo_role: str = Depends(_require_demo("correct_card"))) -> Any:
    return _guard(lambda: _decide(card_id, "correct", req))


@app.post("/api/evidence/{card_id}/reject", response_model=ContributionCard)
def reject(card_id: str, req: DecisionReq = DecisionReq(),
           demo_role: str = Depends(_require_demo("reject_card"))) -> Any:
    return _guard(lambda: _decide(card_id, "reject", req))


@app.post("/api/evidence/{card_id}/request_revision", response_model=ContributionCard)
def request_revision(card_id: str, req: DecisionReq = DecisionReq(),
                     demo_role: str = Depends(_require_demo("request_revision"))) -> Any:
    """Host back-edge: send an undecided card back for another draft instead of rejecting it."""
    return _guard(lambda: _decide(card_id, "request_revision", req))


@app.get("/api/ledger", response_model=list[LedgerEntry])
def get_ledger() -> Any:
    return _guard(lambda: ledger().entries())


@app.get("/api/ledger/verify", response_model=LedgerVerification)
def verify_ledger() -> Any:
    return _guard(lambda: ledger().verify())


@app.get("/api/export/credential/{card_id}")
def export_credential(card_id: str, demo_role: str = Depends(_require_demo("export_credential"))) -> Any:
    def run() -> dict:
        c = cards().get(card_id)
        if c is None or c.status not in ("confirmed", "corrected"):
            raise HTTPException(409, "only host-confirmed cards can be exported")
        v = next((x for x in volunteers() if x.id == c.volunteer_id), None)
        if v is None:
            raise HTTPException(404, "volunteer not found")
        out = badges.to_credential(c, v)
        ledger().append("export", c, "system")
        return out
    return _guard(run)


@app.get("/api/eval", response_model=EvalReport)
def run_eval() -> Any:
    from eval import harness  # lane A: backend/eval/harness.py
    return _guard(lambda: harness.run_eval(volunteers(), tasks()))


# Serve the production frontend build (npm run build) when present: one command demo.
_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if _DIST.exists():
    app.mount("/", StaticFiles(directory=str(_DIST), html=True), name="ui")
