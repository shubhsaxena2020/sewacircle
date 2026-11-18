"""LANE B: append-only, hash-chained audit ledger for contribution cards.

A hash chain shows edits, not truth; truth comes from host confirmation.

Design / canonical serialization
--------------------------------
* Each entry commits to six fields, in this fixed order::

      prev_hash | ts | action | card_id | actor | payload_hash

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
  on every append. A pure hash chain cannot see removal of its last entry;
  the sidecar count/head makes tail deletion detectable.
* With ``path=None`` a real temp file is created with ``tempfile.mkstemp`` and
  kept for the lifetime of this object (the file descriptor is closed
  immediately).

Limitations
-----------
An adversary who can rewrite both the journal and the sidecar can recompute a
consistent chain, so verification detects accidental damage and unilateral
edits, not a fully coordinated forgery. Nothing here auto-rejects, changes,
or validates the *content* of a card; the chain is an integrity record only,
and the host's confirmation is the source of truth.
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
                         actor: str, payload_hash: str) -> str:
    """Return the deterministic pipe-joined UTF-8 string that gets hashed."""
    return "|".join((prev_hash, ts, _escape(action), _escape(card_id),
                     _escape(actor), payload_hash))


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _payload_hash(card: ContributionCard) -> str:
    canonical_card = json.dumps(card.model_dump(mode="json"), sort_keys=True,
                                ensure_ascii=False, separators=(",", ":"))
    return _sha256(canonical_card)


def _entry_hash(entry: LedgerEntry) -> str:
    return _sha256(canonical_chain_line(
        entry.prev_hash, entry.ts.isoformat(), entry.action, entry.card_id,
        entry.actor, entry.payload_hash,
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
            "payload_hash": entry.payload_hash,
            "prev_hash": entry.prev_hash,
            "entry_hash": entry.entry_hash,
        }
        line = json.dumps(record, sort_keys=True, ensure_ascii=False,
                          separators=(",", ":")) + "\n"
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()

    def _write_head(self, count: int, head_hash: str) -> None:
        tmp_path = self.head_path + ".tmp"
        payload = json.dumps({"count": count, "head_hash": head_hash},
                             sort_keys=True, ensure_ascii=False,
                             separators=(",", ":"))
        with open(tmp_path, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.flush()
        os.replace(tmp_path, self.head_path)

    def _read_head(self) -> tuple[int, str] | None:
        """Return (count, head_hash); None if the sidecar does not exist yet."""
        if not os.path.exists(self.head_path):
            return None
        with open(self.head_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return int(data["count"]), str(data["head_hash"])

    # ---------- public API ----------
    def append(self, action: str, card: ContributionCard, actor: str) -> LedgerEntry:
        """Append one immutable entry; returns it. The card is never modified."""
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
                payload_hash=payload,
                prev_hash=prev_hash,
                entry_hash=_sha256(canonical_chain_line(
                    prev_hash, ts_text, action, card.id, actor, payload,
                )),
            )
            self._write_entry(entry)
            self._write_head(index + 1, entry.entry_hash)
            self._entries = current + [entry]
            return entry

    def entries(self) -> list[LedgerEntry]:
        """Return a snapshot of the journal, read fresh from disk under lock."""
        with self._lock:
            return list(self._load_entries())

    def verify(self) -> LedgerVerification:
        """Recompute the chain and cross-check the sidecar head metadata."""
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

            ok = first_bad is None and not notes
            note = _GOOD_NOTE if ok else " ".join(notes) + " " + _GOOD_NOTE
            return LedgerVerification(ok=ok, entries=len(stored),
                                      first_bad_index=first_bad, note=note)

