"""FastAPI app. OWNED BY HEAD. Wires lane modules; any unimplemented lane function returns HTTP 501 until its lane lands.
LLM failures map to 502 (the UI then offers manual entry). Local demo only: unauthenticated, 'actor' is a label, not an identity."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Optional

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
                      RosterResult, SharedRoleCount, TaskSpec, Volunteer)
from . import capabilities, share
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
    roster_ready: dict[str, Optional[bool]] | None = None


S = _State()


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


def roster_ready() -> dict[str, Optional[bool]]:
    """Ready verdict per task id, for rosters computed in THIS process (never persisted)."""
    if S.roster_ready is None:
        S.roster_ready = {}
    return S.roster_ready


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
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CARDS_PATH.write_text(json.dumps([c.model_dump(mode="json") for c in cards().values()], ensure_ascii=False), encoding="utf-8")


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
def list_tasks() -> Any:
    return _guard(tasks)


@app.get("/api/drive/{share_key}", response_model=DriveShareSummary)
def drive_summary(share_key: str) -> Any:
    """Public, read-only summary of one drive, addressed by an opaque share key - never by a task id.

    ``share_key`` is the first 16 base32 characters of HMAC-SHA256(secret, task id). The secret is
    ``SEWA_SHARE_SECRET`` when that environment variable is set; otherwise a random value is generated
    at first use and kept in memory for this process only, so nothing is written to disk, no secret is
    committed, and a restart invalidates every link the server handed out. Because a key cannot be
    computed without the secret, sequential task ids are useless on this route: anything that is not a
    key derived from this secret is 404, and the task id is never echoed back. The body is built from
    the task spec plus the in-memory ready verdict, so it contains no volunteer name, id or contact.
    """
    def run() -> DriveShareSummary:
        known = tasks()
        task_id = share.task_id_for_share_key(share_key, [t.id for t in known])
        if task_id is None:
            raise HTTPException(404, "unknown share link")
        task = next(t for t in known if t.id == task_id)
        return DriveShareSummary(
            title=task.title,
            district=task.district,
            block=task.block,
            slot=task.slot,
            roles=[SharedRoleCount(role=r.role, count=r.count, required_skills=list(r.required_skills),
                                   safety_critical=r.safety_critical) for r in task.roles],
            ready=roster_ready().get(task.id),
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


class RosterAll(BaseModel):
    cp_sat: RosterResult
    nearest_skill: RosterResult
    random_feasible: RosterResult
    manual_greedy: RosterResult


@app.post("/api/roster", response_model=RosterAll)
def make_roster(req: RosterReq) -> Any:
    def run() -> RosterAll:
        v = volunteers()
        o = req.options  # every method gets the same candidate pool (opt-in filter included)
        result = RosterAll(cp_sat=solver.build_roster(req.task, v, o),
                           nearest_skill=solver.baseline_nearest_skill(req.task, v, o),
                           random_feasible=solver.baseline_random_feasible(req.task, v, o.seed, o),
                           manual_greedy=solver.baseline_manual_greedy(req.task, v, o))
        # Remembered in memory only, so the public share route can show the verdict it was given here.
        roster_ready()[req.task.id] = result.cp_sat.ready
        return result
    return _guard(run)


class WhyNotReq(BaseModel):
    task: TaskSpec
    roster: RosterResult
    volunteer_id: str
    options: RosterOptions = Field(default_factory=RosterOptions)


@app.post("/api/roster/why-not", response_model=Counterfactual)
def why_not(req: WhyNotReq) -> Any:
    return _guard(lambda: solver.why_not(req.task, volunteers(), req.roster, req.volunteer_id, req.options))


class DropoutReq(BaseModel):
    task: TaskSpec
    roster: RosterResult
    dropped_volunteer_id: str
    options: RosterOptions = Field(default_factory=RosterOptions)


@app.post("/api/roster/dropout", response_model=DropoutResult)
def dropout(req: DropoutReq) -> Any:
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

    Revision back-edge: a card the host sent back with request_revision is re-drafted. It passes through the state
    machine's revision_requested -> draft edge (see evidence/transitions.py), the stale reason is cleared, and the
    ledger records a 'draft' entry whose reason names the revision request."""
    def run() -> list[ContributionCard]:
        store = cards()
        out: list[ContributionCard] = []
        drafted = llm_extract.draft_cards(req.task, req.host_notes, req.attendance_rows, req.assignments)
        new_ids = {c.id for c in drafted}
        for stale in [x for x in store.values() if x.task_id == req.task.id and x.id not in new_ids
                      and x.status in ("draft", "flagged")]:
            del store[stale.id]
        for c in drafted:
            existing = store.get(c.id)
            if existing is not None and existing.status not in ("draft", "flagged", "revision_requested"):
                out.append(existing)
                continue
            redrafted = existing is not None and existing.status == "revision_requested"
            if redrafted:
                transitions.next_state(existing.status, "redraft")   # asserts the table allows the move
            c.flags = rules.check_card(c, [x for x in store.values() if x.id != c.id] + out, req.attendance_rows)
            c.status = "flagged" if any(f.severity in ("warn", "block") for f in c.flags) else "draft"
            c.revision_reason = None
            store[c.id] = c
            ledger().append("flag" if c.status == "flagged" else "draft", c, "system",
                            "re-drafted after a host revision request" if redrafted else "")
            out.append(c)
        _save_cards()
        return out
    return _guard(run)


@app.post("/api/demo/reset")
def demo_reset() -> dict:
    """Start a clean demo: archive the current card store and ledger (renamed with a timestamp, never deleted)."""
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
    return {"ok": True, "archived": archived}


@app.get("/api/evidence/cards", response_model=list[ContributionCard])
def list_cards() -> Any:
    return list(cards().values())


class DecisionReq(BaseModel):
    actor: str = "host"                      # demo label, not an authenticated identity
    claimed_hours: Optional[float] = Field(default=None, ge=0, le=24)  # required for correct
    reason: Optional[str] = Field(default=None, max_length=500)        # required for request_revision


def _decide(card_id: str, action: str, req: DecisionReq) -> ContributionCard:
    """Move one card along its state machine; the target state comes from the table, never from here.

    Illegal moves are HTTP 409 with the legal actions named. ``request_revision`` needs a non-blank
    reason, which is stored on the card and folded into the ledger entry's hash.
    """
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
    if action == "correct":
        if req.claimed_hours is None:
            raise HTTPException(422, "claimed_hours is required to correct a card")
        c.claimed_hours = req.claimed_hours
    c.status = status  # type: ignore[assignment]
    c.revision_reason = reason if action == "request_revision" else None
    if status in ("confirmed", "corrected"):
        c.confirmed_by = req.actor
    ledger().append(action, c, req.actor, reason)
    _save_cards()
    return c


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
