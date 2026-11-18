"""LANE B interface (LLM layer). Uses llm.client.complete_json (record/replay cache). Replace bodies, keep signatures."""
from __future__ import annotations

from ..schemas import ContributionCard, ExtractionResult, RoleSpec, TaskSpec
from .redact import redact as _redact


def redact(text: str) -> tuple[str, int]:
    """Remove Indian PII (phone, Aadhaar, PAN, email, ...) before any model call. Returns (clean_text, n_redactions)."""
    return _redact(text)


def extract_roles(brief_text: str, language_hint: str | None = None) -> ExtractionResult:
    """Hindi/English/Hinglish task brief -> roles with taxonomy skills, evidence spans, confidence, needs_decision."""
    raise NotImplementedError


def to_role_specs(extraction: ExtractionResult) -> list[RoleSpec]:
    raise NotImplementedError


def draft_cards(task: TaskSpec, host_notes: str, attendance_rows: list[dict], assignments: list[dict]) -> list[ContributionCard]:
    """After the event: AI drafts contribution cards from host notes. Never sets status confirmed. recorded_hours from attendance_rows."""
    raise NotImplementedError
