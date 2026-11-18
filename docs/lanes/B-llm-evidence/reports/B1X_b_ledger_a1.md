# B1X-b — Ledger A1 item 10 adaptation (Lane B)

## Scope

Only three files were touched by this subagent: `backend/app/evidence/ledger.py`,
`backend/tests/evidence/test_ledger.py`, and this report. No other lane file was
written. `schemas.py` was read only; the `LedgerEntry` / `LedgerVerification`
models already present were used unchanged.

Amendment implemented: docs/AMENDMENT-A1.md item 10 — "Ledger threat model: the
claims are limited to detecting edits, reordering and interior deletion; tail
truncation is detectable only against a separately kept head hash. Add
`Ledger.head_hash()` and `verify(trusted_head: str | None = None)` and say so in
the docstring. Appends must be crash-safe (flush+fsync) and thread-safe."

## What changed in `ledger.py`

1. **`Ledger.head_hash() -> str`** — returns the current chain head taken from
   the journal: the last entry's `entry_hash`, or `GENESIS_HASH` (64 zeroes) for
   an empty journal. It reads under the existing `RLock`; it survives reopen
   because it reads the journal, not only the in-memory view. The caller must
   copy this value somewhere *outside* both the journal and its `.head`
   sidecar for it to work as an anchor.

2. **`verify(trusted_head: str | None = None) -> LedgerVerification`** — precise
   semantics: with `trusted_head=None` (default) behaviour is unchanged (chain
   recomputation plus `.head` sidecar cross-check). When a `trusted_head` is
   supplied and it differs from the current chain head, verification fails with
   `ok=False` and `first_bad_index` set to the number of stored entries — the
   point just past the end of the current journal — and the note says the
   trusted head does not match the current head, naming possible **tail
   truncation or replacement of the chain**. A matching `trusted_head` agrees
   and normal chain checks apply. This anchor check is the only one that can
   catch an adversary who rewrites *both* the journal and the sidecar.

3. **Module docstring rewritten to the honest threat model** — edits,
   reordering and interior deletion are detected from the journal alone;
   **TAIL TRUNCATION IS DETECTABLE ONLY AGAINST A SEPARATELY KEPT HEAD HASH**;
   the analogy to an externally witnessed RFC 6962 Merkle-tree root from
   `docs/research/R3-credentials-privacy.md` is stated explicitly (an anchor
   shows a byte string was the head at a time, not that the event was real);
   "a hash chain shows edits, not truth"; the sidecar is labelled an aid, not
   an anchor; crash-safety and concurrency behaviour are documented.

4. **Crash-safe appends** — `_write_entry` now does `write` → `flush()` →
   `os.fsync(handle.fileno())` on the journal, and only then `_write_head`
   writes the temp sidecar, does `flush()` → `os.fsync(handle.fileno())`, and
   atomically `os.replace`s it into place. Two real fsyncs per append, in that
   order. The `.head` sidecar and its atomic rewrite are retained.

5. **Unchanged, verified by existing tests**: the `threading.RLock` around
   append/verify/head reads, canonical SHA-256 over
   `prev_hash|ts|action|card_id|actor|payload_hash` with escaping, JSON-lines
   journal, first_bad_index for edited / reordered / interior-deleted entries,
   and the pre-existing sidecar-mismatch detection for a tail cut where only
   the journal was edited.

## What changed in `test_ledger.py`

Kept all 11 pre-existing tests (tamper, reorder, interior deletion, tail cut via
sidecar, persistence/reopen, 6-thread × 12-append concurrency, missing sidecar,
immutability, temp path, clean verify, chain links). Added 7 tests:

- `head_hash()` equals genesis when empty, the last `entry_hash` after appends,
  the persisted last line, and survives reopen; it changes on append.
- `verify(trusted_head=<correct>)` is ok.
- stale head → `ok=False`, `first_bad_index == number of stored entries`, note
  names truncation/replacement.
- plainly wrong head (`GENESIS_HASH` on a one-entry ledger) → `first_bad_index == 1`.
- coordinated tail truncation: delete last journal line **and** rewrite the
  sidecar to match → plain `verify()` is ok (invisible), but
  `verify(trusted_head=<captured before truncation>)` fails with
  `first_bad_index == 2`.
- fsync test: monkeypatches `app.evidence.ledger.os.fsync` with a wrapper that
  **calls the real `os.fsync`**, and records the on-disk state at each call.
  Two calls per append are observed; the first sees the journal line with no
  sidecar temp file, the second sees the sidecar temp file. No fake fsync.
- docstring test asserting the honest threat-model phrases are present.

An earlier draft of the fsync test asserted distinct file descriptors; on
Windows the OS reused fd 11 after each close, so that assertion failed. It was
a test bug, not a production bug; the test was changed to observe the write
path (journal state vs sidecar-temp state) and the real fsync call. The final
targeted and full-suite runs below are the authoritative ones.

## Commands and COMPLETE raw output

Targeted run. Command:

```
cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q tests/evidence/test_ledger.py
```

Raw output (exit 0):

```
C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pytest_asyncio\plugin.py:306: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to "function" scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
..................                                                       [100%]
18 passed in 2.41s
```

Full suite. Command (tee used only to preserve the raw bytes in a scratch file;
`PIPESTATUS[0]` reports pytest's own exit code):

```
cd C:/Users/shubh/Projects/sewacircle/backend && set -o pipefail && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q . 2>&1 | tee C:/Users/shubh/AppData/Local/hermes/profiles/res-s3/cache/scratch/b1x_full_suite.txt; echo "PYTEST_EXIT=${PIPESTATUS[0]}"
```

COMPLETE raw output (pytest exit 0):

```
C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pytest_asyncio\plugin.py:306: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to "function" scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
........................................................................ [ 16%]
........................................................................ [ 33%]
........................................................................ [ 50%]
........................................................................ [ 67%]
........................................................................ [ 84%]
...................................................................      [100%]
============================== warnings summary ===============================
..\.venv\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

tests/evidence/test_rules.py: 59 warnings
  C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pydantic\main.py:280: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
427 passed, 60 warnings in 3.81s
PYTEST_EXIT=0
```

The authoritative full-suite result is the single line printed by pytest:
**427 passed, 60 warnings in 3.81s**. The last authoritative targeted result is
**18 passed in 2.41s**. No failure lines appeared in either authoritative run.

## Limitations / notes for the lead

- Directory-level fsync after the sidecar `os.replace` is not performed (not
  portable to this Windows host); power-loss durability of the rename itself is
  therefore not claimed. File-content fsync of both files is real and tested.
- A `trusted_head` only detects change relative to a value the *caller* kept
  outside the journal and sidecar. If the anchor itself is lost or rewritten,
  coordinated truncation is undetectable; this is the documented R3 / RFC 6962
  external-witness analogy, not a cryptographic guarantee about real-world
  events. A hash chain shows edits, not truth.
- An attacker with full write access can recompute a consistent chain and a new
  `.head`; plain `verify()` cannot detect that, by design.
- Another subagent was concurrently editing `backend/app/evidence/rules.py` and
  `backend/tests/evidence/test_rules.py` for the same amendment batch. No
  transient failures appeared in my targeted or full-suite runs; the lead
  should still re-run the full suite after all concurrent edits settle.
- 60 warnings are pre-existing pytest-asyncio / Starlette / pydantic deprecation
  warnings, unrelated to this change; 59 of them come from `test_rules.py`.
