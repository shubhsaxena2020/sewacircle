"""FastAPI app. OWNED BY HEAD. Wires lane modules; any unimplemented lane function returns HTTP 501 until its lane lands.
LLM failures map to 502 (the UI then offers manual entry). Local demo only: unauthenticated, 'actor' is a label, not an identity."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Optional

import functools
import hashlib
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .evidence import badges, ledger as ledger_mod, rules
from .llm import extract as llm_extract
from .llm.client import LLMError
from .schemas import (Assignment, AttendanceRow, ContributionCard, Counterfactual, DropoutResult, EvalReport, ExtractionResult,
                      LedgerEntry, LedgerVerification, RosterOptions, RosterResult, TaskSpec, Volunteer)
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


class _State:
    volunteers: list[Volunteer] | None = None
    tasks: list[TaskSpec] | None = None
    cards: dict[str, ContributionCard] | None = None
    ledger: Optional[ledger_mod.Ledger] = None


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
        }
        for d in data["districts"]
    ]
    return {
        "state": "Uttar Pradesh",
        "source_url": source_url,
        "districts": districts,
    }


build_geo_tree = get_geo_tree


@functools.lru_cache(maxsize=1)
def _geo_tree_payload() -> tuple[bytes, str]:
    tree = get_geo_tree()
    body = json.dumps(tree, ensure_ascii=False).encode("utf-8")
    etag = f'"{hashlib.sha256(body).hexdigest()}"'
    return body, etag


@app.get("/api/geo/tree")
def geo_tree(request: Request = None) -> Any:
    if request is None:
        return get_geo_tree()
    body, etag = _geo_tree_payload()
    if_none_match = request.headers.get("if-none-match")
    if if_none_match and (
        if_none_match == etag
        or if_none_match.strip('"') == etag.strip('"')
        or if_none_match == f"W/{etag}"
    ):
        return Response(status_code=304, headers={"ETag": etag})
    return Response(content=body, media_type="application/json", headers={"ETag": etag})


@app.get("/api/volunteers", response_model=list[Volunteer])
def list_volunteers() -> Any:
    return _guard(volunteers)


@app.get("/api/tasks", response_model=list[TaskSpec])
def list_tasks() -> Any:
    return _guard(tasks)


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
        return RosterAll(cp_sat=solver.build_roster(req.task, v, o),
                         nearest_skill=solver.baseline_nearest_skill(req.task, v, o),
                         random_feasible=solver.baseline_random_feasible(req.task, v, o.seed, o),
                         manual_greedy=solver.baseline_manual_greedy(req.task, v, o))
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
def draft(req: DraftReq) -> Any:
    """Idempotent: card ids are deterministic; a card already decided by the host is never overwritten by a re-draft.
    Undecided draft/flagged cards of the same task that are not part of the new draft (for example after a dropout
    moved someone to another role) are superseded: removed from the card store so they cannot trigger false
    duplicate-evidence flags. Their earlier 'draft' entries stay in the ledger history. Host-decided cards are kept."""
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
            if existing is not None and existing.status not in ("draft", "flagged"):
                out.append(existing)
                continue
            c.flags = rules.check_card(c, [x for x in store.values() if x.id != c.id] + out, req.attendance_rows)
            c.status = "flagged" if any(f.severity in ("warn", "block") for f in c.flags) else "draft"
            store[c.id] = c
            ledger().append("flag" if c.status == "flagged" else "draft", c, "system")
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


_ALLOWED_FROM = {"draft", "flagged"}


def _decide(card_id: str, action: str, status: str, req: DecisionReq) -> ContributionCard:
    c = cards().get(card_id)
    if c is None:
        raise HTTPException(404, "card not found")
    if c.status not in _ALLOWED_FROM:
        raise HTTPException(409, f"card is already {c.status}; decisions are final in this prototype")
    if action == "correct":
        if req.claimed_hours is None:
            raise HTTPException(422, "claimed_hours is required to correct a card")
        c.claimed_hours = req.claimed_hours
    c.status = status  # type: ignore[assignment]
    if status in ("confirmed", "corrected"):
        c.confirmed_by = req.actor
    ledger().append(action, c, req.actor)
    _save_cards()
    return c


@app.post("/api/evidence/{card_id}/confirm", response_model=ContributionCard)
def confirm(card_id: str, req: DecisionReq = DecisionReq()) -> Any:
    return _guard(lambda: _decide(card_id, "confirm", "confirmed", req))


@app.post("/api/evidence/{card_id}/correct", response_model=ContributionCard)
def correct(card_id: str, req: DecisionReq = DecisionReq()) -> Any:
    return _guard(lambda: _decide(card_id, "correct", "corrected", req))


@app.post("/api/evidence/{card_id}/reject", response_model=ContributionCard)
def reject(card_id: str, req: DecisionReq = DecisionReq()) -> Any:
    return _guard(lambda: _decide(card_id, "reject", "rejected", req))


@app.get("/api/ledger", response_model=list[LedgerEntry])
def get_ledger() -> Any:
    return _guard(lambda: ledger().entries())


@app.get("/api/ledger/verify", response_model=LedgerVerification)
def verify_ledger() -> Any:
    return _guard(lambda: ledger().verify())


@app.get("/api/export/credential/{card_id}")
def export_credential(card_id: str) -> Any:
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
