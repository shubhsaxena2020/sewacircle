"""SYNTHETIC tests for the Lane B hash-chained audit ledger.

No real people, no real task data: every card below is invented for this test.
The tests edit journal files directly to simulate tampering; no network access.
"""
from __future__ import annotations

import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from app.evidence import ledger as ledger_module
from app.evidence.ledger import GENESIS_HASH, Ledger
from app.schemas import ContributionCard, Flag

FIXED_TS = datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc)


def _card(card_id: str, task_id: str = "task-synth-01", hours: float = 3.0) -> ContributionCard:
    """A fully synthetic contribution card (invented ids, no real person)."""
    return ContributionCard(
        id=card_id,
        task_id=task_id,
        volunteer_id="vol-synth-" + card_id,
        role="first_aid",
        claimed_hours=hours,
        recorded_hours=hours,
        summary="SYNTHETIC: stocked the first-aid table and directed participants.",
        evidence_refs=["synth://attendance/" + card_id],
        status="draft",
        flags=[Flag(code="synthetic_fixture", severity="info", message="Synthetic test data.")],
        drafted_by="ai",
        created_at=FIXED_TS,
        synthetic=True,
    )


def _lines(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _write_lines(path: str, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")) + "\n")


def test_append_builds_chain_links_and_sequential_indices(tmp_path):
    ledger = Ledger(str(tmp_path / "journal.jsonl"))
    entries = [ledger.append("draft", _card(f"card-{i}"), "host") for i in range(3)]

    assert [e.index for e in entries] == [0, 1, 2]
    assert entries[0].prev_hash == GENESIS_HASH == "0" * 64
    assert entries[1].prev_hash == entries[0].entry_hash
    assert entries[2].prev_hash == entries[1].entry_hash
    for entry in entries:
        # Independent recomputation of the canonical chain hash.
        raw = "|".join((entry.prev_hash, entry.ts.isoformat(), entry.action,
                        entry.card_id, entry.actor, entry.payload_hash))
        assert entry.entry_hash == hashlib.sha256(raw.encode("utf-8")).hexdigest()
        expected_payload = json.dumps(_card(entry.card_id).model_dump(mode="json"),
                                      sort_keys=True, ensure_ascii=False,
                                      separators=(",", ":"))
        assert entry.payload_hash == hashlib.sha256(expected_payload.encode("utf-8")).hexdigest()
    assert [e.index for e in ledger.entries()] == [0, 1, 2]


def test_clean_verify_ok(tmp_path):
    ledger = Ledger(str(tmp_path / "journal.jsonl"))
    for i in range(4):
        ledger.append("draft", _card(f"card-{i}"), "host")
    result = ledger.verify()
    assert result.ok is True
    assert result.entries == 4
    assert result.first_bad_index is None
    assert "hash chain shows edits, not truth" in result.note.lower()


def test_verify_detects_edited_entry(tmp_path):
    path = str(tmp_path / "journal.jsonl")
    ledger = Ledger(path)
    for i in range(3):
        ledger.append("draft", _card(f"card-{i}"), "host")
    records = _lines(path)
    records[1]["actor"] = "mallory"  # unilateral edit of a stored entry
    _write_lines(path, records)

    result = Ledger(path).verify()
    assert result.ok is False
    assert result.first_bad_index == 1
    assert "entry_hash" in result.note.lower() or "mismatch" in result.note.lower()


def test_verify_detects_deleted_middle_entry(tmp_path):
    path = str(tmp_path / "journal.jsonl")
    ledger = Ledger(path)
    for i in range(3):
        ledger.append("draft", _card(f"card-{i}"), "host")
    records = _lines(path)
    del records[1]  # delete a middle entry; sidecar is left untouched
    _write_lines(path, records)

    result = Ledger(path).verify()
    assert result.ok is False
    assert result.first_bad_index == 1
    assert result.entries == 2


def test_verify_detects_reordered_entries(tmp_path):
    path = str(tmp_path / "journal.jsonl")
    ledger = Ledger(path)
    for i in range(3):
        ledger.append("draft", _card(f"card-{i}"), "host")
    records = _lines(path)
    records[0], records[1] = records[1], records[0]
    _write_lines(path, records)

    result = Ledger(path).verify()
    assert result.ok is False
    assert result.first_bad_index == 0


def test_verify_detects_deleted_tail_entry_via_sidecar(tmp_path):
    path = str(tmp_path / "journal.jsonl")
    ledger = Ledger(path)
    for i in range(3):
        ledger.append("draft", _card(f"card-{i}"), "host")
    records = _lines(path)
    del records[-1]  # the pure chain of remaining entries is still valid
    _write_lines(path, records)

    result = Ledger(path).verify()
    assert result.ok is False
    assert result.first_bad_index == 2
    assert "sidecar" in result.note.lower()
    assert "count" in result.note.lower()


def test_persistence_reopen(tmp_path):
    path = str(tmp_path / "journal.jsonl")
    first = Ledger(path)
    a, b = first.append("draft", _card("card-a"), "host"), first.append("confirm", _card("card-b"), "host")
    assert os.path.exists(path) and os.path.exists(path + ".head")

    reopened = Ledger(path)
    assert [e.index for e in reopened.entries()] == [0, 1]
    assert reopened.verify().ok is True
    c = reopened.append("correct", _card("card-c"), "host")
    assert c.index == 2 and c.prev_hash == b.entry_hash
    assert [e.index for e in Ledger(path).entries()] == [0, 1, 2]
    assert reopened.verify().ok is True
    assert a.prev_hash == GENESIS_HASH


def test_thread_safety_concurrent_append(tmp_path):
    path = str(tmp_path / "journal.jsonl")
    ledger = Ledger(path)
    n_threads, per_thread = 6, 12

    def worker(worker_id: int) -> list:
        return [ledger.append("draft", _card(f"t{worker_id}-{i}"), "host")
                for i in range(per_thread)]

    with ThreadPoolExecutor(max_workers=n_threads) as pool:
        batches = list(pool.map(worker, range(n_threads)))
    appended = [entry for batch in batches for entry in batch]

    assert len(appended) == n_threads * per_thread
    assert sorted(e.index for e in appended) == list(range(n_threads * per_thread))
    assert len({e.entry_hash for e in appended}) == n_threads * per_thread
    stored = ledger.entries()
    assert len(stored) == n_threads * per_thread
    assert [e.index for e in stored] == list(range(n_threads * per_thread))
    result = ledger.verify()
    assert result.ok is True
    assert result.entries == n_threads * per_thread
    assert result.first_bad_index is None
    with open(path + ".head", "r", encoding="utf-8") as handle:
        assert json.load(handle)["count"] == n_threads * per_thread


def test_missing_sidecar_is_reported_honestly(tmp_path):
    path = str(tmp_path / "journal.jsonl")
    ledger = Ledger(path)
    ledger.append("draft", _card("card-a"), "host")
    os.unlink(path + ".head")

    result = ledger.verify()
    assert result.ok is False
    assert "missing" in result.note.lower()
    assert "sidecar" in result.note.lower()


def test_append_never_mutates_card(tmp_path):
    ledger = Ledger(str(tmp_path / "journal.jsonl"))
    card = _card("card-immutable")
    before = card.model_dump(mode="json")
    ledger.append("flag", card, "host")
    assert card.model_dump(mode="json") == before
    assert card.status == "draft" and card.flags[0].code == "synthetic_fixture"


def test_temp_path_journal_survives_for_object_lifetime():
    ledger = Ledger()
    try:
        assert os.path.exists(ledger.path)
        ledger.append("draft", _card("card-temp"), "host")
        assert len(_lines(ledger.path)) == 1
        assert ledger.verify().ok is True
    finally:
        for p in (ledger.path, ledger.head_path):
            if os.path.exists(p):
                os.unlink(p)


# ---------------- A1 item 10: head anchor + crash-safe appends ----------------

def test_head_hash_equals_last_entry_hash_and_changes_after_append(tmp_path):
    path = str(tmp_path / "journal.jsonl")
    ledger = Ledger(path)
    assert ledger.head_hash() == GENESIS_HASH  # empty chain

    first = ledger.append("draft", _card("card-head-1"), "host")
    assert ledger.head_hash() == first.entry_hash
    assert ledger.head_hash() == Ledger(path).head_hash()  # survives reopen

    second = ledger.append("confirm", _card("card-head-2"), "host")
    assert ledger.head_hash() == second.entry_hash
    assert ledger.head_hash() != first.entry_hash
    assert ledger.head_hash() == _lines(path)[-1]["entry_hash"]
    assert ledger.verify().ok is True


def test_verify_with_correct_trusted_head_is_ok(tmp_path):
    ledger = Ledger(str(tmp_path / "journal.jsonl"))
    for i in range(3):
        ledger.append("draft", _card(f"card-anchor-{i}"), "host")
    trusted = ledger.head_hash()

    result = Ledger(ledger.path).verify(trusted_head=trusted)
    assert result.ok is True
    assert result.entries == 3
    assert result.first_bad_index is None


def test_verify_with_stale_trusted_head_fails_at_point_past_end(tmp_path):
    path = str(tmp_path / "journal.jsonl")
    ledger = Ledger(path)
    ledger.append("draft", _card("card-old-1"), "host")
    stale = ledger.head_hash()  # anchor captured after the second append
    ledger.append("draft", _card("card-old-2"), "host")
    ledger.append("confirm", _card("card-old-3"), "host")

    result = Ledger(path).verify(trusted_head=stale)
    assert result.ok is False
    assert result.entries == 3
    assert result.first_bad_index == 3  # number of stored entries
    lowered = result.note.lower()
    assert "trusted head" in lowered
    assert "truncat" in lowered or "replac" in lowered


def test_verify_with_wrong_trusted_head_fails_at_point_past_end(tmp_path):
    ledger = Ledger(str(tmp_path / "journal.jsonl"))
    ledger.append("draft", _card("card-wrong-anchor"), "host")

    result = ledger.verify(trusted_head=GENESIS_HASH)  # never the real head
    assert result.ok is False
    assert result.first_bad_index == 1


def test_coordinated_tail_truncation_invisible_to_plain_verify_but_caught_by_trusted_head(tmp_path):
    path = str(tmp_path / "journal.jsonl")
    ledger = Ledger(path)
    for i in range(3):
        ledger.append("draft", _card(f"card-tail-{i}"), "host")
    trusted = ledger.head_hash()  # ANCHOR KEPT OUTSIDE BOTH FILES

    records = _lines(path)
    del records[-1]  # truncate the tail of the journal
    _write_lines(path, records)
    # Adversary also rewrites the sidecar to match the truncated chain.
    with open(path + ".head", "w", encoding="utf-8") as handle:
        handle.write(json.dumps({"count": len(records),
                                 "head_hash": records[-1]["entry_hash"]},
                                sort_keys=True, separators=(",", ":")))

    plain = Ledger(path).verify()
    assert plain.ok is True  # coordinated truncation is invisible without an anchor
    assert plain.entries == 2

    anchored = Ledger(path).verify(trusted_head=trusted)
    assert anchored.ok is False
    assert anchored.entries == 2
    assert anchored.first_bad_index == 2  # just past the end of the 2 stored entries
    assert "trusted head" in anchored.note.lower()
    assert "truncat" in anchored.note.lower() or "replac" in anchored.note.lower()


def test_append_fsyncs_journal_and_sidecar_for_every_append(monkeypatch, tmp_path):
    """The real os.fsync is called after each journal write and sidecar write."""
    real_fsync = os.fsync
    path = str(tmp_path / "journal.jsonl")
    observed: list[tuple[int, bool]] = []

    def recording_fsync(fd: int) -> None:
        lines = 0
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as journal:
                lines = sum(1 for _ in journal)
        observed.append((lines, os.path.exists(path + ".head.tmp")))
        real_fsync(fd)  # actually flush; do not fake the call

    monkeypatch.setattr(ledger_module.os, "fsync", recording_fsync)
    ledger = Ledger(path)

    ledger.append("draft", _card("card-fsync-1"), "host")
    assert len(observed) == 2
    # First fsync is the journal line; second is the sidecar temp file.
    assert observed[0] == (1, False)
    assert observed[1] == (1, True)

    ledger.append("confirm", _card("card-fsync-2"), "host")
    assert len(observed) == 4
    assert observed[2] == (2, False)
    assert observed[3] == (2, True)
    assert os.path.exists(path + ".head")
    result = Ledger(path).verify()
    assert result.ok is True
    assert result.entries == 2


def test_module_docstring_states_honest_threat_model():
    doc = (ledger_module.__doc__ or "").lower()
    assert "shows edits, not truth" in doc
    assert "reorder" in doc
    assert "interior deletion" in doc
    assert "tail truncation" in doc
    assert "separately kept head hash" in doc
    assert "rfc 6962" in doc
    assert "fsync" in doc
