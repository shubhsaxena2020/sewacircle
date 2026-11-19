"""Public-demo boundary: one operator token in front of the routes that write or expose personal data.

Scope, decided by the head: this is NOT a login system
------------------------------------------------------
There is no account, no session, no user table and no password. The whole mechanism is one shared secret
read from the environment (``SEWA_OPERATOR_TOKEN``) and compared with the ``X-Operator-Token`` request
header in constant time. It exists so a publicly reachable demo can be shown to a district officer without
letting an anonymous visitor reset the demo, re-plan a roster, decide contribution cards, mint share links,
or read the volunteer list, the card store and the audit ledger.

Two switches, and the local default is "off"
--------------------------------------------
* ``SEWA_PUBLIC_DEMO`` unset / ``0`` / ``false`` / ``no`` / ``off`` -> the gate is OFF and every route behaves
  exactly as before (the local prototype's behaviour is unchanged). This is the default.
* ``SEWA_PUBLIC_DEMO`` set to anything else (``1``, ``true``, ``YES``, ``on``, and - deliberately - a value
  nobody meant, such as ``production`` or ``enabled``) -> the gate is ON. Unrecognised values therefore fail
  closed: a typo can make the demo refuse traffic, never expose it.

Fail closed, not open
---------------------
If public-demo mode is on but ``SEWA_OPERATOR_TOKEN`` is empty or blank, EVERY protected route refuses with 403
and a message naming the missing variable. A demo that is accidentally open is worse than a demo that is
accidentally closed, so a missing token never means "no token needed". The configured token is compared as
written (it is not stripped): sending exactly what was configured always works, and a value with accidental
leading/trailing spaces is treated as part of the secret.

How it composes with X-Demo-Role
--------------------------------
``X-Demo-Role`` stays a labelled simulation *on top of* this gate: the operator token is checked FIRST, so a
role header can never grant an action the token does not grant (and cannot substitute for a missing token).
The real enforcement order is: operator token -> demo role -> capability matrix.

What stays public (and why)
---------------------------
``/api/tasks``, ``/api/eval``, ``/api/geo/tree``, ``/api/capabilities``, ``/api/drive/{key}`` and
``/api/drive/status`` stay open: they carry no personal data (no volunteer id, name or contact, no card text
and no ledger), and the public drive page and the district map need them to render for a viewer who has no
token at all.
"""
from __future__ import annotations

import hmac
import os

#: Header the operator token travels in.
TOKEN_HEADER = "X-Operator-Token"

#: Environment switch for the whole boundary.
PUBLIC_DEMO_ENV = "SEWA_PUBLIC_DEMO"

#: Environment variable holding the shared secret.
OPERATOR_TOKEN_ENV = "SEWA_OPERATOR_TOKEN"

#: Values of SEWA_PUBLIC_DEMO that turn the gate OFF. Anything else - including values nobody meant - turns it
#: ON, so a typo fails closed instead of publishing an open demo.
_FALSY = frozenset({"", "0", "false", "no", "off"})


class OperatorRequired(Exception):
    """Raised when a protected route is called without a valid operator token in public-demo mode."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def public_demo_enabled() -> bool:
    """True unless ``SEWA_PUBLIC_DEMO`` is unset or explicitly falsy.

    Fail-closed by design: ``production``/``enabled``/``2`` are read as "on", because the cost of guessing
    wrong in that direction is a demo that refuses traffic, not a demo anyone can reset.
    """
    return os.environ.get(PUBLIC_DEMO_ENV, "").strip().lower() not in _FALSY


def operator_token() -> str:
    """The configured shared secret, exactly as written (empty when the deployment has not set one).

    Not stripped: a token with accidental surrounding spaces is compared with those spaces included, so the
    value the deployment configured is the value that works. Blank counts as unset (fail closed).
    """
    token = os.environ.get(OPERATOR_TOKEN_ENV, "")
    return token if token.strip() else ""


def token_matches(candidate: str | None) -> bool:
    """Constant-time comparison of a caller's token with the configured one.

    An unset/empty configured token never matches: in public-demo mode that means every protected route is
    closed until the deployment sets ``SEWA_OPERATOR_TOKEN``.
    """
    expected = operator_token()
    if not expected or not candidate:
        return False
    return hmac.compare_digest(str(candidate).encode("utf-8"), expected.encode("utf-8"))


def check(candidate: str | None) -> None:
    """Raise :class:`OperatorRequired` unless the request may pass the boundary.

    Does nothing at all when public-demo mode is off, which is what keeps the local behaviour unchanged.
    """
    if not public_demo_enabled():
        return
    if not operator_token():
        raise OperatorRequired(
            f"public demo mode is on ({PUBLIC_DEMO_ENV}=1) but {OPERATOR_TOKEN_ENV} is not configured on this "
            "server, so every operator route is closed. Set "
            f"{OPERATOR_TOKEN_ENV} and send the same value in the {TOKEN_HEADER} header.")
    if not token_matches(candidate):
        raise OperatorRequired(
            f"public demo mode: this route needs the {TOKEN_HEADER} header with the operator token. "
            f"The X-Demo-Role header is a labelled simulation and does not grant it.")
