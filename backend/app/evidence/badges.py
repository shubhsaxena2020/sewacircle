"""Portable contribution record shaped like an Open Badges 3.0 OpenBadgeCredential (W3C VC Data Model 2.0 conventions).

Field names, multiplicities and @context order follow docs/research/R3-credentials-privacy.md, which quotes the 1EdTech
OB 3.0 spec (v1.4.5) and W3C VC DM 2.0 (opened 2026-11-18). Required: @context, id, type, credentialSubject, issuer,
validFrom; subject: type, achievement; achievement: id, type, criteria, description, name; issuer: id, type; evidence: type.

THIS IS UNSIGNED. It has no `proof`, so it is NOT a verifiable credential (OB3 B.1.2: a proof MUST be expressed for a
credential to be verifiable). It is a data-model-shaped contribution record, not issued or recognised by any authority.
No credentialSchema is declared because no full JSON Schema validation is run (R3 recommendation). Hours are not an OB3
property, so they appear only as text inside evidence.narrative. The subject id is a pseudonymous urn:uuid derived from
the synthetic volunteer id; no phone, Aadhaar, PAN or email is ever included.
"""
from __future__ import annotations

import re
import uuid

from ..schemas import ContributionCard, Volunteer

CONTEXT = ["https://www.w3.org/ns/credentials/v2", "https://purl.imsglobal.org/spec/ob/v3p0/context-3.0.3.json"]
ISSUER_ID = "https://example.invalid/sewacircle/issuer"   # .invalid TLD: deliberately not a real issuer
_NS = uuid.UUID("6f1c2b8e-0d3a-4c3e-9a51-5e7a1c0de016")      # fixed namespace for deterministic pseudonymous ids
REQUIRED = {
    "credential": ["@context", "id", "type", "credentialSubject", "issuer", "validFrom"],
    "issuer": ["id", "type"],
    "subject": ["type", "achievement"],
    "achievement": ["id", "type", "criteria", "description", "name"],
    "evidence": ["type"],
}
NOTICE = "UNSIGNED synthetic demonstration record. Not a verifiable credential and not issued or recognised by any authority."


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "role"


def to_credential(card: ContributionCard, volunteer: Volunteer) -> dict:
    if card.status not in ("confirmed", "corrected"):
        raise ValueError("only host-confirmed or host-corrected cards can be exported")
    subject_id = f"urn:uuid:{uuid.uuid5(_NS, volunteer.id)}"
    hours = card.claimed_hours
    narrative = (f"Host-reviewed contribution as {card.role}: {hours:g} hours "
                 + (f"(attendance sheet {card.recorded_hours:g} h). " if card.recorded_hours is not None else ". ")
                 + (card.summary or "") + f" Status: {card.status} by {card.confirmed_by or 'host'}.")
    return {
        "@context": list(CONTEXT),
        "id": f"urn:uuid:{uuid.uuid5(_NS, card.id)}",
        "type": ["VerifiableCredential", "OpenBadgeCredential"],
        "name": f"{card.role} - SewaCircle contribution record (synthetic)",
        "description": NOTICE,
        "issuer": {"id": ISSUER_ID, "type": ["Profile"], "name": "SewaCircle prototype (not an issuing authority)"},
        "validFrom": card.created_at.replace(microsecond=0).isoformat() + "Z",
        "credentialSubject": {
            "id": subject_id,
            "type": ["AchievementSubject"],
            "role": card.role,
            "achievement": {
                "id": f"https://example.invalid/sewacircle/achievements/{_slug(card.role)}",
                "type": ["Achievement"],
                "name": card.role,
                "description": f"Covered the role '{card.role}' at a synthetic community task ({card.task_id}).",
                "criteria": {"narrative": "A host reviewed the AI-drafted card against host notes and the attendance sheet and confirmed or corrected it. Rule flags at review time: "
                             + (", ".join(f.code for f in card.flags) if card.flags else "none") + "."},
            },
        },
        "evidence": [{"type": ["Evidence"], "name": "Host-reviewed contribution", "narrative": narrative}],
        "sewacircle:notice": NOTICE,
    }


def missing_required(doc: dict) -> dict[str, list[str]]:
    """Stdlib presence check against the required arrays quoted from the spec (not full JSON Schema validation)."""
    subj = doc.get("credentialSubject", {})
    parts = {"credential": doc, "issuer": doc.get("issuer", {}), "subject": subj, "achievement": subj.get("achievement", {})}
    out = {k: [f for f in REQUIRED[k] if f not in v] for k, v in parts.items()}
    out["evidence"] = [f for ev in doc.get("evidence", []) for f in REQUIRED["evidence"] if f not in ev]
    return {k: v for k, v in out.items() if v}
