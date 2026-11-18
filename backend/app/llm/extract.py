"""LLM layer: role extraction and contribution-card drafting. Every model call goes through llm.client.complete_json
(record/replay cache) and every input is PII-redacted first; rostered people are replaced by ids and other Indian names
from a gazetteer are masked (see names.py for the limits: Latin script only)."""
from __future__ import annotations

import re
import unicodedata

from ..schemas import Assignment, AttendanceRow, ContributionCard, ExtractedRole, ExtractionResult, RoleSpec, TaskSpec
from ..taxonomy import SKILLS
from . import client
from .client import LLMError
from .prompts import DRAFT_SYSTEM, EXTRACT_FEWSHOT, EXTRACT_SYSTEM
from .names import mask_names, pseudonymise
from .redact import redact as _redact

_DEVANAGARI_DIGITS = str.maketrans("०१२३४५६७८९", "0123456789")


def redact(text: str) -> tuple[str, int]:
    return _redact(text)


def _detect_language(text: str) -> str:
    dev = sum(1 for ch in text if "ऀ" <= ch <= "ॿ")
    latin = sum(1 for ch in text if ch.isascii() and ch.isalpha())
    if dev > latin:
        return "hi"
    hinglish_words = {"hai", "chahiye", "mein", "aur", "kal", "ke", "ki", "ko", "nahi", "ek", "do", "sambhale", "lagane"}
    words = set(re.findall(r"[a-z]+", text.lower()))
    return "hinglish" if len(words & hinglish_words) >= 2 else "en"


def _user_prompt(text: str) -> str:
    shots = "\n\n".join(f"INPUT:\n{i}\nOUTPUT:\n{o}" for i, o in EXTRACT_FEWSHOT)
    return f"Examples:\n\n{shots}\n\nNow the real input.\nINPUT:\n{text}\nOUTPUT:"


def extract_roles(brief_text: str, language_hint: str | None = None) -> ExtractionResult:
    clean, n = redact(brief_text)
    clean, k = mask_names(clean)   # person names never reach the model
    n += k
    if not clean.strip():
        return ExtractionResult(roles=[], needs_decision=["The task description is empty."], language_detected="en", model="none", redactions=n)
    data, meta = client.complete_json("extract", EXTRACT_SYSTEM, _user_prompt(clean), max_tokens=3000)
    if not isinstance(data, dict) or not isinstance(data.get("roles"), list):
        raise LLMError("model returned no roles list")
    roles: list[ExtractedRole] = []
    notes: list[str] = []
    needs = [str(q) for q in data.get("needs_decision", []) if str(q).strip()]
    for raw in data["roles"]:
        if not isinstance(raw, dict) or not str(raw.get("role", "")).strip():
            continue
        skills = [s for s in raw.get("required_skills", []) if s in SKILLS]
        dropped = [s for s in raw.get("required_skills", []) if s not in SKILLS]
        unresolved = bool(dropped) and not skills
        if dropped:
            notes.append(f"Dropped unknown skills {dropped} for role '{raw.get('role')}'.")
        if unresolved:   # never let an unmapped requirement silently become 'open to anyone'
            needs.append(f"'{raw.get('role')}' needs a skill we do not track ({', '.join(map(str, dropped))}). "
                         "Pick a skill or mark the role open before planning.")
        try:
            count = int(str(raw.get("count", 1)).translate(_DEVANAGARI_DIGITS))
        except ValueError:
            count, raw["confidence"] = 1, "low"
        count = max(1, min(10, count))
        span = str(raw.get("evidence_span", ""))
        conf = raw.get("confidence") if raw.get("confidence") in ("high", "medium", "low") else "medium"
        if span and unicodedata.normalize("NFC", span) not in unicodedata.normalize("NFC", clean):
            notes.append(f"Evidence for '{raw.get('role')}' was not found verbatim in the text; confidence lowered.")
            conf = "low"
        roles.append(ExtractedRole(role=str(raw["role"])[:80], count=count, required_skills=skills, evidence_span=span[:200],
                                   confidence="low" if unresolved else conf, reason=str(raw.get("reason", ""))[:200],
                                   unresolved=unresolved))
        if conf == "low":
            needs.append(f"Please check the role '{raw['role']}' (the AI was not sure).")
    lang = data.get("language_detected") if data.get("language_detected") in ("hi", "en", "hinglish") else None
    return ExtractionResult(roles=roles, needs_decision=list(dict.fromkeys(needs)),
                            language_detected=(language_hint if language_hint in ("hi", "en", "hinglish") else lang or _detect_language(clean)),  # type: ignore[arg-type]
                            model=meta["model"], cached=meta["cached"], redactions=n, notes=notes)


def to_role_specs(extraction: ExtractionResult) -> list[RoleSpec]:
    return [RoleSpec(id=f"role-{i + 1:02d}", role=r.role, count=r.count, required_skills=r.required_skills,
                     evidence_span=r.evidence_span, confidence=r.confidence, unresolved=r.unresolved)
            for i, r in enumerate(extraction.roles)]


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "role"


def _hash(text: str) -> str:
    """Short content hash of the quoted evidence, so two cards citing the SAME note line are caught by the duplicate rule
    while different lines from one shared notes document are not (a shared generic ref caused false duplicate flags)."""
    import hashlib
    return hashlib.sha256(" ".join(text.casefold().split()).encode("utf-8")).hexdigest()[:10]


def _card_id(task_id: str, volunteer_id: str, role: str) -> str:
    return f"card-{task_id}-{volunteer_id}-{_slug(role)}"


def _fallback_cards(task: TaskSpec, notes: str, rows: dict[str, AttendanceRow], assignments: list[Assignment]) -> list[dict]:
    """Deterministic parser used when the LLM is unavailable: '<name> ... <n> hours'."""
    out = []
    role_name = {r.id: r.role for r in task.roles}
    for a in assignments:
        first = a.volunteer_name.split()[0]
        m = re.search(rf"{re.escape(first)}[^\n]*?(\d+(?:\.\d+)?)\s*(?:hours|hrs|h|घंटे)", notes, re.I)
        line = next((ln for ln in notes.splitlines() if first.lower() in ln.lower()), "")
        out.append({"volunteer_id": a.volunteer_id, "role": role_name.get(a.role_id, a.role_id),
                    "claimed_hours": float(m.group(1)) if m else 0.0, "evidence": line.strip(),
                    "summary": (f"Host notes mention {a.volunteer_name}." if line else f"{a.volunteer_name} is not mentioned in the host notes.")})
    return out


def draft_cards(task: TaskSpec, host_notes: str, attendance_rows: list[AttendanceRow], assignments: list[Assignment]) -> list[ContributionCard]:
    rows = {r.volunteer_id: r for r in attendance_rows if r.task_id == task.id}
    pii_clean, _ = redact(host_notes)
    names = {a.volunteer_id: a.volunteer_name for a in assignments}
    pseudo, _ = pseudonymise(pii_clean, {name: vid for vid, name in names.items()})   # rostered people -> [v-xxx]
    clean, _ = mask_names(pseudo)                                                      # anyone else -> [NAME]
    role_name = {r.id: r.role for r in task.roles}
    roster_list = "\n".join(f"- {a.volunteer_id} ({role_name.get(a.role_id, a.role_id)})" for a in assignments)  # ids only, no names
    try:
        data, _meta = client.complete_json("draft", DRAFT_SYSTEM, f"ROSTER:\n{roster_list}\n\nHOST NOTES:\n{clean}", max_tokens=3000)
        raw_cards = data.get("cards", []) if isinstance(data, dict) else []
        drafted_by = "ai"
    except LLMError:
        raw_cards, drafted_by = _fallback_cards(task, pii_clean, rows, assignments), "human"  # local parser, no model call
    valid_ids = {a.volunteer_id for a in assignments}
    cards: dict[str, ContributionCard] = {}
    for c in raw_cards:
        vid = str(c.get("volunteer_id", ""))
        if vid not in valid_ids:
            continue
        role = next((role_name.get(a.role_id, a.role_id) for a in assignments if a.volunteer_id == vid), "Volunteer")  # roster, not model text
        try:
            hours = max(0.0, min(24.0, float(c.get("claimed_hours", 0) or 0)))
        except (TypeError, ValueError):
            hours = 0.0
        cid = _card_id(task.id, vid, role)
        ev = str(c.get("evidence", "")).strip()
        cards[cid] = ContributionCard(
            id=cid, task_id=task.id, volunteer_id=vid, role=role, claimed_hours=hours,
            recorded_hours=rows[vid].hours if vid in rows else None,
            summary=re.sub(r"\[(v-\d+)\]", lambda m: names.get(m.group(1), m.group(0)), str(c.get("summary", "")))[:300],
            evidence_refs=([f"host_note:{task.id}:{vid}:{_hash(ev)}"] if ev else []) + ([f"attendance:{task.id}:{vid}"] if vid in rows else []),
            status="draft", drafted_by=drafted_by)  # type: ignore[arg-type]
    for a in assignments:   # every rostered volunteer gets a card even if the notes skip them
        if not any(c.volunteer_id == a.volunteer_id for c in cards.values()):
            role = role_name.get(a.role_id, a.role_id)
            cid = _card_id(task.id, a.volunteer_id, role)
            cards[cid] = ContributionCard(id=cid, task_id=task.id, volunteer_id=a.volunteer_id, role=role, claimed_hours=0.0,
                                          recorded_hours=rows[a.volunteer_id].hours if a.volunteer_id in rows else None,
                                          summary=f"{a.volunteer_name} is not mentioned in the host notes.",
                                          evidence_refs=[f"attendance:{task.id}:{a.volunteer_id}"] if a.volunteer_id in rows else [],
                                          status="draft", drafted_by=drafted_by)  # type: ignore[arg-type]
    return list(cards.values())
