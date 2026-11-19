"""Capability-driven menu: which screens and actions each DEMO role may use.

THIS IS A DEMO ROLE SWITCH, NOT AUTHENTICATION.
----------------------------------------------
The caller picks its own role with the ``X-Demo-Role`` request header. There is
no login, no password, no session, no signature and no server-side identity: any
client can send any role, so the matrix below protects nothing against a hostile
caller. Its job is to make the product's *intended* division of labour visible
and testable - an organiser plans a crew, a host confirms what volunteers did, a
volunteer follows a drive, a viewer reads the evaluation - so the demo can show
the same UI behaving differently for each role and the same rules on the server
side. Real deployments must put an authenticated identity in front of this and
derive the role from it; that is deliberately out of scope here.

Why it is still enforced server-side
------------------------------------
A menu that only hides buttons is a suggestion. The mutating evidence routes call
:func:`may` through a FastAPI dependency, so a request that forges its way past
the UI still gets HTTP 403. That is the same code path the menu uses, so the two
cannot drift apart.

The matrix
----------
One dict, ``CAPABILITIES``: role -> {"screens": [...], "actions": [...]}. The
default role is ``organiser``, which keeps every existing client working
unchanged (it is the only role that may run the whole flow).

* ``organiser`` - runs the district side: plans rosters (and the why-not and
  dropout repair tools), drafts cards, makes and revisits every decision,
  exports credentials, mints the read-only share link, resets the demo, and
  reads the ledger and evaluation. The volunteer pool is planning data, so
  ``read_volunteers`` is organisers only.
* ``host`` - the person who was on site: may confirm, correct, reject, ask for a
  revision and export the record, but does not run the roster planner and does
  not draft cards (the drafting step belongs to the organiser/system).
* ``volunteer`` - read-only: sees the public summary of a drive. Seeing *their
  own* cards needs an identity this demo does not have, so it is not offered.
* ``viewer`` - read-only: the evaluation only, for a funder or a reviewer.
"""
from __future__ import annotations

from typing import Any

#: Header a client uses to pick its demo role.
ROLE_HEADER = "X-Demo-Role"

#: The role assumed when the header is absent (keeps existing clients working).
DEFAULT_ROLE = "organiser"

DEMO_ROLES: tuple[str, ...] = ("organiser", "host", "volunteer", "viewer")

DEMO_NOTICE = ("Demo role switch only - the X-Demo-Role header is chosen by the caller, so it is not "
               "authentication and must not be treated as a security boundary.")

#: The ONE capability matrix: demo role -> screens it may open and actions it may perform.
CAPABILITIES: dict[str, dict[str, tuple[str, ...]]] = {
    "organiser": {
        "screens": ("roster", "evidence", "ledger", "evaluation", "drive_summary", "capabilities"),
        "actions": ("read_roster", "read_cards", "read_ledger", "read_eval", "read_drive_summary", "read_volunteers",
                    "draft_cards", "confirm_card", "correct_card", "reject_card", "request_revision",
                    "export_credential", "share_drive", "reset_demo"),
    },
    "host": {
        "screens": ("evidence", "ledger", "evaluation", "drive_summary", "capabilities"),
        "actions": ("read_cards", "read_ledger", "read_eval", "read_drive_summary", "confirm_card", "correct_card",
                    "reject_card", "request_revision", "export_credential"),
    },
    "volunteer": {
        "screens": ("drive_summary", "capabilities"),
        "actions": ("read_drive_summary",),
    },
    "viewer": {
        "screens": ("evaluation", "capabilities"),
        "actions": ("read_eval",),
    },
}

#: Actions that write something; these are the ones the API enforces on X-Demo-Role.
#: ``reset_demo`` is included because it archives the card store and the ledger;
#: ``read_roster`` and ``share_drive`` because they write the in-memory plan snapshot.
MUTATING_ACTIONS: tuple[str, ...] = (
    "read_roster",
    "draft_cards",
    "confirm_card",
    "correct_card",
    "reject_card",
    "request_revision",
    "export_credential",
    "share_drive",
    "reset_demo",
)


class UnknownRole(Exception):
    """Raised for a role that is not in :data:`CAPABILITIES`."""

    def __init__(self, role: str) -> None:
        super().__init__(f"unknown demo role {role!r}; choose one of {', '.join(DEMO_ROLES)}")
        self.role = role


def normalise_role(raw: str | None) -> str:
    """Turn a header/query value into a known role name, defaulting to ``organiser``.

    Blank or missing means the default role; case and surrounding spaces are
    ignored. Anything else must be a known role or :class:`UnknownRole` is raised.
    """
    role = (raw or "").strip().lower() or DEFAULT_ROLE
    if role not in CAPABILITIES:
        raise UnknownRole(role)
    return role


def capabilities_for(role: str) -> dict[str, Any]:
    """Return the menu for one role: screens, actions and the demo notice."""
    role = normalise_role(role)
    entry = CAPABILITIES[role]
    return {"role": role, "screens": list(entry["screens"]), "actions": list(entry["actions"]),
            "demo_only": True, "note": DEMO_NOTICE}


def may(role: str, action: str) -> bool:
    """True when the demo role lists ``action``. Unknown roles may do nothing."""
    return action in CAPABILITIES.get(role, {}).get("actions", ())


def require(role: str, action: str) -> None:
    """Raise :class:`PermissionError` unless ``role`` may ``action``."""
    if not may(role, action):
        raise PermissionError(f"the demo role {role!r} may not {action}. {DEMO_NOTICE}")
