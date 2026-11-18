"""Opaque, read-only share links for one drive.

A district organiser often wants to show a drive to people who have no account
on the platform: a school principal, a panchayat member, a volunteer's parent.
The obvious link - ``/api/drive/task-01`` - leaks two things at once: how many
drives exist and the order in which they were created (sequential ids), and it
invites anyone to walk the id space and read every drive. Neither is acceptable
for a route that is deliberately open.

So the public route is addressed by a *key*, not by an id::

    share_key = base32(HMAC-SHA256(secret, task_id))[:16]

* HMAC (not a plain hash) means an outsider cannot precompute the key for
  ``task-01`` without the secret, so the ids stay unguessable even though they
  are sequential.
* 16 base32 characters carry 80 bits, which is far more than enough to make
  guessing a live link impractical, while staying short enough to read out.
* The key is one-way: seeing a key does not reveal the task id, and the route
  never echoes the task id back.
* Only task ids that this process knows are matched, and every candidate is
  compared with :func:`hmac.compare_digest`, so a request cannot learn *which*
  prefix of a key was wrong.

Where the secret comes from (stated because it decides who can mint links)
-----------------------------------------------------------------------
:func:`server_secret` reads the ``SEWA_SHARE_SECRET`` environment variable. When
that variable is unset (the default for a local demo) it generates 32 random
bytes at first use and keeps them **in memory only** for the lifetime of the
process: nothing is written to disk, no key is committed to the repository, and
restarting the server invalidates every link it handed out. Setting the variable
makes links survive a restart and lets two workers agree; rotating the variable
(or calling :func:`reset_secret`) deliberately invalidates the old links.

This module never returns volunteer data - it only computes and resolves keys.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from typing import Iterable, Optional

#: Number of base32 characters kept from the HMAC digest (80 bits).
KEY_LENGTH = 16

#: Base32 alphabet used by :func:`base64.b32encode` (RFC 4648, no padding kept).
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"

_SECRET: Optional[bytes] = None


def server_secret() -> bytes:
    """Return the process-wide share secret, generating it in memory if needed.

    ``SEWA_SHARE_SECRET`` wins when it is set and non-blank. Otherwise 32 random
    bytes are created on first call and cached for the process lifetime only.
    """
    global _SECRET
    if _SECRET is None:
        configured = os.environ.get("SEWA_SHARE_SECRET", "").strip()
        _SECRET = configured.encode("utf-8") if configured else secrets.token_bytes(32)
    return _SECRET


def reset_secret() -> None:
    """Forget the cached secret so the next call re-reads the environment.

    Used by tests, and by an operator who wants to rotate links on purpose: every
    key minted before this call stops resolving afterwards.
    """
    global _SECRET
    _SECRET = None


def _digest(secret: bytes, task_id: str) -> bytes:
    return hmac.new(secret, task_id.encode("utf-8"), hashlib.sha256).digest()


def share_key_for(task_id: str) -> str:
    """Return the opaque public key for one task id (deterministic per secret)."""
    if not task_id:
        raise ValueError("task_id must be a non-empty string")
    return base64.b32encode(_digest(server_secret(), task_id)).decode("ascii")[:KEY_LENGTH]


def looks_like_share_key(candidate: str) -> bool:
    """True only for a 16-character RFC 4648 base32 string.

    This rejects sequential task ids (``task-01`` has a hyphen and lowercase
    letters) before any secret is touched, which is what keeps ids off the route.
    """
    return len(candidate) == KEY_LENGTH and all(ch in ALPHABET for ch in candidate)


def task_id_for_share_key(share_key: str, task_ids: Iterable[str]) -> Optional[str]:
    """Resolve a key back to one known task id, or ``None``.

    Every candidate is compared in constant time; the loop does not stop at the
    first match, so response time does not reveal the position of the match.
    """
    if not looks_like_share_key(share_key):
        return None
    secret = server_secret()
    found: Optional[str] = None
    for task_id in task_ids:
        if hmac.compare_digest(share_key_for(task_id), share_key):
            found = task_id
    return found
