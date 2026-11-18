"""LANE B: append-only, hash-chained audit ledger for contribution cards.

Threat model (honest claims)
----------------------------
A hash chain shows edits, not truth; truth comes from host confirmation.

* DETECTED from the journal alone: an edited entry (its hash no longer
  recomputes), a reordered entry (its index or ``prev_hash`` link breaks),
  and an interior deletion (the link across the gap breaks). ``verify()``
  reports the first such index in ``first_bad_index``.
* TAIL TRUNCATION IS DETECTABLE ONLY AGAINST A SEPARATELY KEPT HEAD HASH.
  Deleting the last journal line leaves a shorter but perfectly
  self-consistent chain. The ``.head`` sidecar catches the naive case where
  only the journal is truncated; an attacker who rewrites BOTH the journal
  and the sidecar is invisible to a plain ``verify()``. Call
  ``Ledger.head_hash()`` and keep that value OUTSIDE both files (an external
  anchor), then pass it as ``trusted_head`` to ``verify()``. This is the same
  design analogy as an externally witnessed RFC 6962 Merkle-tree root
  (discussed in docs/research/R3-credentials-privacy.md): an anchor shows
  that a particular byte string was the head at that time, not that the
  real-world event it describes actually happened.
* ``verify(trusted_head=...)`` semantics: when ``trusted_head`` is supplied
  and differs from the current chain head (the last journal entry's
  ``entry_hash``, or ``GENESIS_HASH`` for an empty journal), verification
  fails with ``ok=False`` and ``first_bad_index`` set to the number of
  stored entries -- the point just past the end of the current journal --
  with a note naming possible tail truncation or chain replacement. A
  matching ``trusted_head`` agrees with the journal and normal chain checks
  apply. ``trusted_head=None`` (the default) keeps the legacy behaviour of
  checking the chain and the sidecar only.
* No anchor is cryptographic proof of truth: anyone who can rewrite the
  whole store can recompute a consistent chain AND a new head. An anchor
  detects rollback/replacement relative to a value kept elsewhere; it does
  not validate the content of a card. Nothing here auto-rejects, changes,
  or validates card content -- the chain is an integrity record only and
  the host's confirmation is the source of truth.

Design / canonical serialization
--------------------------------
* Each entry commits to six fields, in this fixed order::

      prev_hash | ts | action | card_id | actor | payload_hash

  A non-empty ``reason`` (the actor's stated justification, required by the API
  for ``request_revision``) is appended as a seventh escaped field, so the
  reason is inside the hash. Entries without a reason have no seventh field,
  which keeps journals written before the field existed verifiable unchanged.
  The fields are escaped (backslash -> ``\\\\``, pipe -> ``\\|``), joined with
  a single ASCII ``|``, encoded as UTF-8 and hashed with SHA-256 to produce
  ``entry_hash``. ``ts`` is the timezone-aware ISO-8601 timestamp string that
  is persisted verbatim in the journal line.
* ``prev_hash`` of the first entry is 64 ASCII zeroes (genesis).
* ``payload_hash`` = SHA-256 of the card's canonical JSON:
  ``json.dumps(card.model_dump(mode="json"), sort_keys=True,
  ensure_ascii=False, separators=(",", ":"))`` encoded as UTF-8.
  The card itself is NOT stored in the journal: the payload hash commits to
  the card as presented at append time, but cannot be recomputed from the
  journal alone.
* The journal is JSON-lines: one compact, key-sorted JSON object per entry.
  Each append opens/writes/closes the journal handle (no long-lived handle).
* A sidecar file at ``path + ".head"`` stores ``{"count": N,
  "head_hash": "..."}`` and is updated atomically (temp file + ``os.replace``)
  on every append. It is an aid, not an external anchor: it helps detect
  tail deletion only while the sidecar itself is untouched.
* With ``path=None`` a real temp file is created with ``tempfile.mkstemp`` and
  kept for the lifetime of this object (the file descriptor is closed
  immediately).

Crash safety / concurrency
--------------------------
Every append is serialized under one ``threading.RLock``. It writes the
journal line, ``flush()`` and ``os.fsync()`` on the journal file, THEN
atomically rewrites the sidecar via a temp file with its own ``flush()`` and
``os.fsync()`` before ``os.replace``. A crash cannot leave a journal entry
without its matching sidecar state, and concurrent appends cannot interleave
their writes. Directory-level fsync after the rename is not performed (it is
not portable to this prototype's Windows host); that is a residual, documented
limitation for power-loss recovery.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import threading
from datetime import datetime, timezone
from typing import Any

from pydantic import ValidationError

from ..schemas import ContributionCard, LedgerEntry, LedgerVerification

GENESIS_HASH = "0" * 64
_GOOD_NOTE = "Hash chain shows edits, not truth; truth comes from host confirmation."


class _CorruptLine(Exception):
    """A journal line could not be parsed into a LedgerEntry."""

    def __init__(self, index: int, message: str) -> None:
        super().__init__(message)
        self.index = index


def _escape(value: str) -> str:
    """Escape the two characters that are structural in the canonical line."""
    return str(value).replace("\\", "\\\\").replace("|", "\\|")


def canonical_chain_line(prev_hash: str, ts: str, action: str, card_id: str,
                         actor: str, payload_hash: str, reason: str = "") -> str:
    """Return the deterministic pipe-joined UTF-8 string that gets hashed.

    When ``reason`` is non-empty it is appended as a seventh field (escaped like
    the others), so the host's stated reason is inside the hash and cannot be
    rewritten without breaking ``verify()``. An empty reason is omitted, which
    keeps journals written before this field existed verifiable byte for byte.
    """
    line = "|".join((prev_hash, ts, _escape(action), _escape(card_id),
                     _escape(actor), payload_hash))
    return line + "|" + _escape(reason) if reason else line


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _payload_hash(card: ContributionCard) -> str:
    canonical_card = json.dumps(card.model_dump(mode="json"), sort_keys=True,
                                ensure_ascii=False, separators=(",", ":"))
    return _sha256(canonical_card)


def _entry_hash(entry: LedgerEntry) -> str:
    return _sha256(canonical_chain_line(
        entry.prev_hash, entry.ts.isoformat(), entry.action, entry.card_id,
        entry.actor, entry.payload_hash, entry.reason,
    ))


class Ledger:
    """Append-only audit trail; every mutation is serialized under one RLock."""

    def __init__(self, path: str | None = None) -> None:
        if path is None:
            fd, path = tempfile.mkstemp(prefix="sewa_ledger_", suffix=".jsonl")
            os.close(fd)
        self.path = path
        self.head_path = path + ".head"
        self._lock = threading.RLock()
        # Seed the in-memory view from disk (a reopened ledger sees old entries).
        with self._lock:
            self._entries: list[LedgerEntry] = self._load_entries()

    # ---------- persistence helpers (callers must hold self._lock) ----------
    def _load_entries(self) -> list[LedgerEntry]:
        entries: list[LedgerEntry] = []
        if not os.path.exists(self.path):
            return entries
        with open(self.path, "r", encoding="utf-8") as handle:
            for line_no, raw in enumerate(handle, 1):
                line = raw.strip()
                if not line:
                    continue
                index = len(entries)
                try:
                    data: Any = json.loads(line)
                    entries.append(LedgerEntry(
                        index=data["index"],
                        ts=datetime.fromisoformat(str(data["ts"])),
                        action=data["action"],
                        card_id=str(data["card_id"]),
                        actor=str(data["actor"]),
                        reason=str(data.get("reason", "")),
                        payload_hash=str(data["payload_hash"]),
                        prev_hash=str(data["prev_hash"]),
                        entry_hash=str(data["entry_hash"]),
                    ))
                except (ValueError, KeyError, TypeError, ValidationError) as exc:
                    raise _CorruptLine(index, f"line {line_no}: {exc}") from exc
        return entries

    def _write_entry(self, entry: LedgerEntry) -> None:
        record = {
            "index": entry.index,
            "ts": entry.ts.isoformat(),
            "action": entry.action,
            "card_id": entry.card_id,
            "actor": entry.actor,
            "reason": entry.reason,
            "payload_hash": entry.payload_hash,
            "prev_hash": entry.prev_hash,
            "entry_hash": entry.entry_hash,
        }
        line = json.dumps(record, sort_keys=True, ensure_ascii=False,
                          separators=(",", ":")) + "\n"
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())

    def _write_head(self, count: int, head_hash: str) -> None:
        tmp_path = self.head_path + ".tmp"
        payload = json.dumps({"count": count, "head_hash": head_hash},
                             sort_keys=True, ensure_ascii=False,
                             separators=(",", ":"))
        with open(tmp_path, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, self.head_path)

    def _read_head(self) -> tuple[int, str] | None:
        """Return (count, head_hash); None if the sidecar does not exist yet."""
        if not os.path.exists(self.head_path):
            return None
        with open(self.head_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return int(data["count"]), str(data["head_hash"])

    # ---------- public API ----------
    def append(self, action: str, card: ContributionCard, actor: str,
               reason: str = "") -> LedgerEntry:
        """Append one immutable entry; returns it. The card is never modified.

        ``reason`` is the actor's stated justification (required by the API for
        ``request_revision``). When non-empty it is folded into ``entry_hash``
        as a seventh canonical field, so a reason cannot be edited or removed
        later without breaking :meth:`verify`.
        """
        with self._lock:
            current = self._load_entries()
            index = len(current)
            prev_hash = current[-1].entry_hash if current else GENESIS_HASH
            ts = datetime.now(timezone.utc)
            ts_text = ts.isoformat()
            payload = _payload_hash(card)
            entry = LedgerEntry(
                index=index,
                ts=ts,
                action=action,  # type: ignore[arg-type]
                card_id=card.id,
                actor=actor,
                reason=reason or "",
                payload_hash=payload,
                prev_hash=prev_hash,
                entry_hash=_sha256(canonical_chain_line(
                    prev_hash, ts_text, action, card.id, actor, payload, reason or "",
                )),
            )
            self._write_entry(entry)
            self._write_head(index + 1, entry.entry_hash)
            self._entries = current + [entry]
            return entry

    def head_hash(self) -> str:
        """Return the current chain head hash, for keeping as an external anchor.

        This is the ``entry_hash`` of the last entry in the journal, or
        ``GENESIS_HASH`` when the journal is empty. Copy the value somewhere
        OUTSIDE the journal and its ``.head`` sidecar: a plain ``verify()``
        cannot detect a coordinated truncation of both files, but
        ``verify(trusted_head=<this value>)`` can.
        """
        with self._lock:
            stored = self._load_entries()
            return stored[-1].entry_hash if stored else GENESIS_HASH

    def entries(self) -> list[LedgerEntry]:
        """Return a snapshot of the journal, read fresh from disk under lock."""
        with self._lock:
            return list(self._load_entries())

    def verify(self, trusted_head: str | None = None) -> LedgerVerification:
        """Recompute the chain, cross-check the sidecar and (optionally) an anchor.

        ``trusted_head`` is a head hash previously captured with
        ``head_hash()`` and stored separately from the journal and sidecar.
        If it is supplied and differs from the current chain head,
        verification fails with ``ok=False`` and ``first_bad_index`` set to
        the number of stored entries (the point just past the end), with a
        note naming possible tail truncation or chain replacement. A
        matching anchor agrees with the journal. ``None`` skips this check.
        """
        with self._lock:
            first_bad: int | None = None
            notes: list[str] = []
            try:
                stored = self._load_entries()
            except _CorruptLine as exc:
                return LedgerVerification(
                    ok=False, entries=exc.index + 1, first_bad_index=exc.index,
                    note=f"Unreadable journal entry at index {exc.index}: {exc}",
                )

            for position, entry in enumerate(stored):
                problems: list[str] = []
                if entry.index != position:
                    problems.append(f"index {entry.index} != expected {position}")
                expected_prev = stored[position - 1].entry_hash if position else GENESIS_HASH
                if entry.prev_hash != expected_prev:
                    problems.append("prev_hash link mismatch")
                if _entry_hash(entry) != entry.entry_hash:
                    problems.append("entry_hash mismatch (edited entry)")
                if problems and first_bad is None:
                    first_bad = position
                    notes.append(f"Entry at index {position}: " + "; ".join(problems) + ".")

            try:
                head = self._read_head()
            except (ValueError, TypeError, KeyError, OSError) as exc:
                head = None
                notes.append(f"Sidecar {self.head_path} is unreadable: {exc}.")
                if first_bad is None:
                    first_bad = max(len(stored) - 1, 0)

            if head is None:
                notes.append(
                    f"Sidecar {self.head_path} is missing; tail deletion cannot "
                    "be ruled out."
                )
                if first_bad is None:
                    first_bad = max(len(stored) - 1, 0)
            else:
                count, head_hash = head
                if count != len(stored):
                    notes.append(
                        f"Sidecar count {count} != journal entries {len(stored)} "
                        "(possible tail deletion or insertion)."
                    )
                    if first_bad is None:
                        # First index the sidecar expects but the journal lacks
                        # (tail deletion), or the first unexpected extra entry.
                        first_bad = min(count, len(stored))
                if stored:
                    if head_hash != stored[-1].entry_hash:
                        notes.append("Sidecar head_hash != last entry_hash.")
                        if first_bad is None:
                            first_bad = len(stored) - 1
                elif head_hash != GENESIS_HASH:
                    notes.append("Sidecar head_hash is non-genesis for an empty journal.")
                    if first_bad is None:
                        first_bad = 0

            # External head anchor: the ONLY check that catches a coordinated
            # truncation/replacement of BOTH the journal and the sidecar.
            current_head = stored[-1].entry_hash if stored else GENESIS_HASH
            if trusted_head is not None and trusted_head != current_head:
                notes.append(
                    "Trusted head hash does not match the current chain head "
                    f"(expected {trusted_head}, found {current_head}): possible "
                    "tail truncation or replacement of the chain."
                )
                # The trusted head describes the state just past the current end.
                first_bad = len(stored)

            ok = first_bad is None and not notes
            note = _GOOD_NOTE if ok else " ".join(notes) + " " + _GOOD_NOTE
            return LedgerVerification(ok=ok, entries=len(stored),
                                      first_bad_index=first_bad, note=note)

