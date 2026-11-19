# Hermes round 2 - progress (head review follow-ups)

Worktree `C:\Users\shubh\Projects\sewacircle-backend`, branch `backend-ideas`. Edits only under
`backend/` and `docs/v4/`. Local commits only, no push.

Baseline at the start of round 2: 820 passed (the 692 original tests plus the round-1 additions and the
geo-tree tests). Closing every OPEN item in `docs/v4/REVIEW-backend-ideas.md`.

## Step log

- [x] 1. `POST /api/drive/share` with `{task_id}` -> `{share_key, path}`. Gated by a new `share_drive`
      capability (organiser only). Tests: organiser gets a key that resolves, host/volunteer/viewer 403,
      unknown task 404. (commit 37a33c6)
- [x] 2. Roster-time snapshot of the plan (title, district, block, slot, roles with counts and required
      skills and safety_critical, ready, computed_at) stored in memory for known task ids only; the public
      summary serves the snapshot, otherwise the synthetic task with `ready=null`, `computed_at=null`.
      `computed_at` added to `DriveShareSummary`. Test: edited roles in the roster request appear in the
      public summary. (commit 37a33c6)
- [x] 3. `share.task_id_for_share_key` no longer computes an unused secret variable; it derives each
      candidate from one secret per call with `hmac.compare_digest`. (commit 37a33c6)
- [x] 4. `POST /api/roster`, `/api/roster/why-not`, `/api/roster/dropout` gated by the `read_roster`
      capability (organiser only). Documented below: an unknown role is 403 via the header on mutating
      routes but 422 via the query on `GET /api/capabilities`. (commit 618866e)
- [x] 5. Localized display text. `GET /api/tasks?lang=` and `POST /api/roster {lang}` attach a `display`
      block; `RecruitRequest.kind` chooses the honest Hindi template. Hand-written Hindi for titles, 24
      skill labels, 29 role names, the 21 slot names, the READY/NOT READY lines and the three recruit
      templates; unknown text is returned unchanged, never machine-translated; card text (LLM/host written)
      is left in its original language. Contract tests compare ids, counts, verdict and the numbers inside
      the sentences across both languages. (commit 618866e)
- [x] 6. `docs/v4/BACKEND-PATTERNS.md` written/replaced with all four patterns, the endpoints and schemas,
      the exact test output, and the honest limits (403 vs 422 difference, default role is not a security
      boundary, cards are not translated, pre-existing behaviour left alone).

## Real command output

```
..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_share_keys.py -q
24 passed, 1 warning in 1.83s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_capabilities.py -q
32 passed, 25 warnings in 2.87s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_i18n.py -q
12 passed, 2 warnings in 1.78s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest -q
839 passed, 154 warnings in 16.82s
```

## 403 vs 422 (as requested by the head)

`GET /api/capabilities?role=nope` is a query-parameter validation failure: 422, with the valid roles named.
`X-Demo-Role: nope` on a mutating route is a request the caller may not perform: 403, with the same
explanation. Both bodies say this is a demo role switch, not authentication.

CARD COMPLETE
