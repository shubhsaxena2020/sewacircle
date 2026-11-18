"""FastAPI app. OWNED BY HEAD. Wires lane modules; any unimplemented lane function returns HTTP 501 until its lane lands."""
from __future__ import annotations

import os
from typing import Any, Callable, Optional

from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .evidence import badges, ledger as ledger_mod, rules
from .llm import extract as llm_extract
from .schemas import (ContributionCard, Counterfactual, DropoutResult, EvalReport, ExtractionResult, LedgerEntry,
                      LedgerVerification, RosterOptions, RosterResult, TaskSpec, Volunteer)
from .solver import api as solver
from .taxonomy import DISCLAIMER, SKILLS

app = FastAPI(title="SewaCircle", version="0.1.0-idea-stage-prototype")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _guard(fn: Callable[[], Any]) -> Any:
    try:
        return fn()
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="lane module not implemented yet")


class _State:
    volunteers: list[Volunteer] | None = None
    tasks: list[TaskSpec] | None = None
    cards: dict[str, ContributionCard] = {}
    attendance: dict[str, list[dict]] = {}
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
        S.ledger = ledger_mod.Ledger(os.environ.get("SEWA_LEDGER_PATH"))
    return S.ledger


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "disclaimer": DISCLAIMER, "model": os.environ.get("SEWA_LLM_MODEL", "cc/claude-sonnet-5-5"),
            "llm_mode": os.environ.get("SEWA_LLM_MODE", "record")}


@app.get("/api/meta")
def meta() -> dict:
    return {"disclaimer": DISCLAIMER, "skills": SKILLS}


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


class RosterBoth(BaseModel):
    cp_sat: RosterResult
    nearest_skill: RosterResult


@app.post("/api/roster", response_model=RosterBoth)
def make_roster(req: RosterReq) -> Any:
    def run() -> RosterBoth:
        v = volunteers()
        return RosterBoth(cp_sat=solver.build_roster(req.task, v, req.options),
                          nearest_skill=solver.baseline_nearest_skill(req.task, v))
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
    attendance_rows: list[dict] = Field(default_factory=list)
    assignments: list[dict] = Field(default_factory=list)


@app.post("/api/evidence/draft", response_model=list[ContributionCard])
def draft(req: DraftReq) -> Any:
    def run() -> list[ContributionCard]:
        cards = llm_extract.draft_cards(req.task, req.host_notes, req.attendance_rows, req.assignments)
        S.attendance[req.task.id] = req.attendance_rows
        for c in cards:
            c.flags = rules.check_card(c, list(S.cards.values()) + cards, req.attendance_rows)
            if any(f.severity in ("warn", "block") for f in c.flags):
                c.status = "flagged"
            S.cards[c.id] = c
            ledger().append("flag" if c.status == "flagged" else "draft", c, "system")
        return cards
    return _guard(run)


@app.get("/api/evidence/cards", response_model=list[ContributionCard])
def list_cards() -> Any:
    return list(S.cards.values())


class DecisionReq(BaseModel):
    actor: str = "host"
    claimed_hours: Optional[float] = None  # for correct


def _decide(card_id: str, action: str, status: str, req: DecisionReq) -> ContributionCard:
    c = S.cards.get(card_id)
    if c is None:
        raise HTTPException(404, "card not found")
    if action == "correct" and req.claimed_hours is not None:
        c.claimed_hours = req.claimed_hours
    c.status = status  # type: ignore[assignment]
    if status in ("confirmed", "corrected"):
        c.confirmed_by = req.actor
    ledger().append(action, c, req.actor)
    return c


@app.post("/api/evidence/{card_id}/confirm", response_model=ContributionCard)
def confirm(card_id: str, req: DecisionReq = Body(default_factory=DecisionReq)) -> Any:
    return _guard(lambda: _decide(card_id, "confirm", "confirmed", req))


@app.post("/api/evidence/{card_id}/correct", response_model=ContributionCard)
def correct(card_id: str, req: DecisionReq = Body(default_factory=DecisionReq)) -> Any:
    return _guard(lambda: _decide(card_id, "correct", "corrected", req))


@app.post("/api/evidence/{card_id}/reject", response_model=ContributionCard)
def reject(card_id: str, req: DecisionReq = Body(default_factory=DecisionReq)) -> Any:
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
        c = S.cards.get(card_id)
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
