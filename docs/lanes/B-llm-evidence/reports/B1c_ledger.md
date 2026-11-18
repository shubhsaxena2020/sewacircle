# B1c — Append-only hash-chained audit ledger (Lane B)

Status: Ledger implemented; all 11 dedicated ledger tests pass. The full suite is
**not green**: 26 passed, 2 failed. Both failures are expected contract-test drift
(`tests/test_contract.py` is read-only for this subagent and still asserts that the
ledger endpoints return HTTP 501). See "Failures" below. The lead must update that
test (or confirm the drift) and re-run authoritatively.

## Files written

- `backend/app/evidence/ledger.py` (stub replaced; signatures unchanged)
- `backend/tests/evidence/test_ledger.py` (11 tests, all fixtures SYNTHETIC)

## Commands and raw output

### 1. Focused test command

```
cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q tests/evidence/test_ledger.py
```

```
C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pytest_asyncio\plugin.py:306: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to "function" scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))

...........                                                              [100%]
11 passed in 1.87s
```

### 2. Full suite — first run (concurrent subagent mid-write)

Command:

```
cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q .
```

Complete raw output (exit code 2):

```
C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pytest_asyncio\plugin.py:306: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to "function" scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))

=================================== ERRORS ====================================
___________________ ERROR collecting tests/test_contract.py ___________________
..\ .venv\Lib\site-packages\_pytest\python.py:528: in importtestmodule
    mod = import_path(
..\ .venv\Lib\site-packages\_pytest\pathlib.py:640: in import_path
    importlib.import_module(module_name)
C:\Program Files\Python313\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
<frozen importlib._bootstrap>:1395: in _gcd_import
    ???
<frozen importlib._bootstrap>:1360: in _find_and_load
    ???
<frozen importlib._bootstrap>:1331: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:935: in _load_unlocked
    ???
..\ .venv\Lib\site-packages\_pytest\assertion\rewrite.py:185: in exec_module
    exec(co, module.__dict__)
tests\test_contract.py:5: in <module>
    from app.main import app
app\main.py:12: in <module>
    from .llm import extract as llm_extract
app\llm\extract.py:5: in <module>
    from .redact import redact as _redact
E     File "C:\Users\shubh\Projects\sewacircle\backend\app\llm\redact.py", line 47
E       _PHONE_BODY = r"(?:\(?[6-9]\d{2}\)?[\s\-]?\d{3}[\s\-]?\d{4}|[6-9]\d{9})"
E       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='?
============================== warnings summary ===============================
..\ .venv\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
ERROR tests/test_contract.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 warning, 1 error in 0.99s
```

At the time of this run another subagent was mid-write on
`backend/app/llm/redact.py` (mtime 23:19:36) and `backend/app/llm/extract.py`
(mtime 23:17:12); `git status` also showed untracked solver/frontend files. That
is not a defect in this lane. About 20 s later `redact.py` compiled cleanly
(mtime 23:20:22), so the suite was re-run.

### 3. Full suite — retry after the other subagent finished writing

Command (identical command, second run):

```
cd C:/Users/shubh/Projects/sewacircle/backend && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -m pytest -q .
```

Complete raw output (exit code 1):

```
C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\pytest_asyncio\plugin.py:306: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to "function" scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session". Set it to "fixture-scope" to keep the current behavior.

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))

........................FF..                                             [100%]
================================== FAILURES ===================================
_______________ test_unimplemented_is_501_not_500[/api/ledger] ________________

path = '/api/ledger'

    @pytest.mark.parametrize("path", ["/api/volunteers", "/api/tasks", "/api/ledger", "/api/ledger/verify", "/api/eval"])
    def test_unimplemented_is_501_not_500(path):
>       assert client.get(path).status_code == 501
E       AssertionError: assert 200 == 501
E        +  where 200 = <Response [200 OK]>.status_code
E        +    where <Response [200 OK]> = get('/api/ledger')
E        +      where get = <starlette.testclient.TestClient object at 0x000001F492A64AD0>.get

tests\test_contract.py:36: AssertionError
____________ test_unimplemented_is_501_not_500[/api/ledger/verify] ____________

path = '/api/ledger/verify'

    @pytest.mark.parametrize("path", ["/api/volunteers", "/api/tasks", "/api/ledger", "/api/ledger/verify", "/api/eval"])
    def test_unimplemented_is_501_not_500(path):
>       assert client.get(path).status_code == 501
E       AssertionError: assert 200 == 501
E        +  where 200 = <Response [200 OK]>.status_code
E        +    where <Response [200 OK]> = get('/api/ledger/verify')
E        +      where get = <starlette.testclient.TestClient object at 0x000001F492A64AD0>.get

tests\test_contract.py:36: AssertionError
============================== warnings summary ===============================
..\ .venv\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\shubh\Projects\sewacircle\.venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_contract.py::test_unimplemented_is_501_not_500[/api/ledger]
FAILED tests/test_contract.py::test_unimplemented_is_501_not_500[/api/ledger/verify]
2 failed, 26 passed, 1 warning in 3.07s
```

Test count: the retry printed `2 failed, 26 passed, 1 warning in 3.07s`; the
focused ledger run printed `11 passed in 1.87s`.

## Design decisions

- **Canonical chain string**: `prev_hash|ts|action|card_id|actor|payload_hash`,
  in that order, with backslash and pipe escaped inside string fields, ISO-8601
  (timezone-aware) timestamp, UTF-8 encoded, SHA-256 hashed into `entry_hash`.
  Genesis `prev_hash` is 64 zeroes. The module docstring documents this.
- **Payload hash**: SHA-256 of `json.dumps(card.model_dump(mode="json"),
  sort_keys=True, ensure_ascii=False, separators=(",", ":"))`, UTF-8. The card
  itself is not persisted; the entry commits to the card as presented.
- **Journal**: compact key-sorted JSON lines. Each append opens, writes, flushes
  and closes the file handle — no long-lived handle.
- **Sidecar**: `path + ".head"` holds `{"count": N, "head_hash": "..."}`,
  rewritten via a temp file plus `os.replace` on every append. This is what
  detects removal of the last line, which a hash chain alone cannot see.
- **Missing sidecar**: does not raise; `verify()` reports `ok=False` with a note
  that tail deletion cannot be ruled out (fail closed). A fresh, empty ledger
  whose sidecar has not yet been written is a known special case of this policy.
- **Thread safety**: a single `threading.RLock` surrounds the whole
  read-modify-write in `append()`; `entries()` and `verify()` also take it, so
  concurrent readers never see a partial append. Indices come from the current
  journal length under the lock, so they are sequential and unique.
- **`first_bad_index` semantics**: the 0-based position of the first divergent
  entry (edited hash, index/link break or reorder). For tail deletion, where no
  divergent entry remains in the journal, it is the first index the sidecar
  expects but the journal lacks (i.e. the original last index). `None` only when
  `ok=True` in normal operation.
- **No mutation / no judgement**: `append()` reads the card, hashes it and writes
  the entry; it never changes a card and never rejects one.
- **Temp files**: `Ledger(None)` uses `tempfile.mkstemp` and closes the fd; the
  file persists for the object's lifetime (no `__del__` cleanup, so a caller
  can safely reopen/inspect it).

## Tamper coverage

Tests edit a real on-disk JSON-lines journal and then construct a fresh `Ledger`
to confirm verification is disk-based, not cache-based:

| Scenario | Detected by | Expected `first_bad_index` |
| --- | --- | --- |
| Edited stored entry (`actor` changed) | `entry_hash` recomputation | 1 |
| Deleted middle entry | index/prev_hash link break | 1 |
| Reordered first two entries | index + prev_hash mismatch | 0 |
| Deleted tail entry | sidecar count/head | 2 |

Also covered: chain links and sequential indices, independently recomputed
payload/entry hashes, clean verify, persistence/reopen with continued indexing,
72 appends from 6 threads with unique indices and clean verify, missing sidecar
reported honestly, cards left unmutated, temp-file lifetime.

## Failures

1. `tests/test_contract.py::test_unimplemented_is_501_not_500[/api/ledger]` and
   `...[/api/ledger/verify]`: these assert HTTP 501 for unimplemented endpoints.
   Implementing `Ledger` makes `main.py` return HTTP 200 with real entries and a
   real verification result. `tests/test_contract.py` is outside this subagent's
   write scope, so it was left untouched. **The lead should remove those two
   paths from the 501 parametrization (or adjust the expectation) and re-run the
   full suite.** This is expected integration drift, not a ledger defect.
2. First full-suite run was a collection error from another subagent's
   mid-written `backend/app/llm/redact.py` (SyntaxError at line 47). That file
   compiled cleanly before the retry; the lead should re-run authoritatively
   after all parallel writers finish.

## Limitations

- A coordinated adversary able to rewrite both the journal and the sidecar can
  recompute a self-consistent chain; this design detects unilateral edits and
  accidental damage, not state-level forgery. External anchoring (signatures,
  append-only storage) would be needed for that.
- The journal stores only `payload_hash`, not the card; verification cannot
  recompute a payload hash without the original card, so a card-content change
  must be detected by comparing against the stored hash at presentation time.
- Timestamps are generated by the host clock; no trusted time source is used.
- No cleanup of temp journals after the owning process exits.
- All test data is synthetic and labelled as such; no real people or records.
- Module-level invariant, verbatim: "A hash chain shows edits, not truth; truth
  comes from host confirmation."
