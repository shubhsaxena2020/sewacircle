# Backend patterns (v4): what was added, why it matters, and how it is tested

Scope: `backend/` in the `backend-ideas` worktree of `sewacircle-backend`. Every
line here was written for this repository; all data is synthetic. Each section
states the endpoint or schema it touches, the reason a district youth organiser
would care, and the real test output.

Test command (run from `backend/`, the venv lives in the main checkout):

```
..\..\sewacircle\.venv\Scripts\python.exe -m pytest -q
```

Final line of the full suite after this work:

```
845 passed, 156 warnings in 17.14s
```

---

## 1. Contribution card state machine with a back-edge

**What it does.** A contribution card is a claim about a person's unpaid work, so
it moves through named states and never skips a step. `backend/app/evidence/transitions.py`
holds the only table that decides where a card may go:

| from | action | to |
|---|---|---|
| draft | confirm / correct / reject / request_revision | confirmed / corrected / rejected / revision_requested |
| flagged | confirm / correct / reject / request_revision | confirmed / corrected / rejected / revision_requested |
| revision_requested | redraft (internal, performed by the drafting route) | draft |

`confirmed`, `corrected` and `rejected` have no outgoing edge: a decision is final
in this prototype and the ledger keeps the history instead. `revision_requested`
has exactly one exit, so the host can send a card back instead of destroying a
genuine contribution over a wrong hour count - that is the *back-edge* the old
one-way flow lacked.

**Why an organiser cares.** Before this, a host who spotted a mismatch had two
options: confirm something they did not believe, or reject a volunteer who really
did turn up. Now there is a third: "fix the card and show it to me again". The
revision reason is not a comment box that disappears - it is a hashed field in the
audit trail, and the re-draft clears it only after the card has actually been
redrafted.

**Endpoints and schemas.**

* `POST /api/evidence/{card_id}/request_revision`, body
  `{"actor": "...", "reason": "..."}`; `reason` is required and must not be blank
  (HTTP 422 otherwise). Returns the updated `ContributionCard`.
* Existing `confirm` / `correct` / `reject` keep their paths and bodies; they now
  consult the table instead of a hard-coded allowlist.
* `ContributionCard.status` gains `revision_requested`; `ContributionCard.revision_reason`
  carries the host's words while the card waits; `LedgerEntry.action` gains
  `request_revision`; `LedgerEntry.reason` records why the actor moved the card.
* Illegal moves return **HTTP 409** with the state, the action and the actions
  that are legal from that state, e.g.
  `illegal transition: cannot 'confirm' a card in state 'confirmed'; legal actions from 'confirmed': none (final state)`.
* Unknown card id stays **404**.

**Ledger integrity.** The reason is appended as a seventh escaped field of the
canonical chain line **only when it is non-empty**, so a journal written before
this feature still verifies byte for byte, while a reason-bearing entry cannot be
edited or cleared without breaking `verify()`. Both directions are tested.

**Tests.**

```
..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/evidence/test_transitions.py -q
38 passed in 0.18s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/evidence/test_card_state_machine.py -q
36 passed, 39 warnings in 5.20s
```

`test_transitions.py` has one case per legal edge (9) and one per illegal
`(state, action)` pair (21), plus invariants: every key and target is a declared
state, the table matches `schemas.CardStatus`, `revision_requested` has exactly one
exit, and "terminal" means exactly "no outgoing edge". `test_card_state_machine.py`
drives the same edges through HTTP: actor/reason/timestamp in the ledger, re-draft
back to draft, non-blank reason required, 409 from every final state, no card
stranded in `revision_requested` when its volunteer leaves the draft, legacy
journal lines still verifying, and an edited or cleared reason breaking the chain.

---

## 2. Opaque share keys for a public drive summary

**What it does.** `GET /api/drive/{share_key}` returns a public, read-only summary
of exactly one drive: title, district, block, slot, roles with counts (and their
required skills / safety-critical flag), the ready verdict, and when that verdict
was computed. It contains **no volunteer id, name or contact field** and never
echoes the task id.

The key is not an id. It is derived, one-way:

```
share_key = base32(HMAC-SHA256(secret, task_id))[:16]
```

16 base32 characters carry 80 bits (16 x 5), taken from the 256-bit digest, so a
key cannot be guessed from a sequential id without the secret. Resolution compares
every known candidate with `hmac.compare_digest` and does not stop early.

**Where the secret comes from.** `SEWA_SHARE_SECRET` when that environment variable
is set. Otherwise 32 random bytes are generated at first use and kept **in memory
for the process only**: nothing is written to disk, no secret is committed, and
restarting the server invalidates every link it handed out. `share.reset_secret()`
rotates deliberately (old links stop resolving). This is stated in the module and
route docstrings.

**Why an organiser cares.** A district organiser wants to show a drive to a school
principal, a panchayat member or a parent without giving them an account - and
without handing out a link that enumerates every drive in the district or names the
young people on it. A derived key gives one drive, read-only, with no personal data.

**Endpoints and schemas.**

* `POST /api/drive/share` body `{"task_id": "..."}` -> `{"share_key": "...", "path": "/api/drive/<key>"}`.
  Gated to the organiser demo role (403 otherwise); unknown `task_id` is 404.
* `GET /api/drive/{share_key}` -> `DriveShareSummary`
  (`title, district, block, slot, roles[SharedRoleCount], ready, computed_at, notice, synthetic`).
* Sequential ids (`task-01`, `1`, `TASK-01`) are refused with 404 before any secret
  is touched: the resolver requires a 16-character uppercase RFC 4648 base32 string.
* When a roster was computed in this process, the summary is the snapshot of **what
  was actually planned** (edited title/roles included) with `ready` and
  `computed_at`; otherwise it is the known task with `ready = null`,
  `computed_at = null`.

**Tests.**

```
..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_share_keys.py -q
26 passed, 1 warning in 1.54s
```

Covered: the key is exactly the truncated HMAC (recomputed independently from the
secret), stable per secret, 16 base32 characters, does not contain the task id, the
resolver only accepts keys for known tasks, unknown/malformed keys 404, sequential
ids 404, the body contains no volunteer id or name from the synthetic pool, the id is
never echoed, rotation invalidates old keys, the secret comes from the environment
or is generated in memory, minting works for the organiser and is 403 for other demo
roles, and edited roles appear in the public summary with `computed_at`.

**Known limit, stated honestly.** In this prototype `GET /api/tasks` and
`GET /api/volunteers` are still open (they are the local demo's data source), so the
"ids stay unguessable" property protects the *share route*, not the whole API. A
real deployment puts those routes behind the same identity boundary.

---

## 3. Capability-driven menu (demo roles, not authentication)

**What it does.** `GET /api/capabilities?role=organiser|host|volunteer|viewer`
returns the screens and actions a role may use, from one dict in
`backend/app/capabilities.py`. The mutating routes enforce the **same** dict through
a FastAPI dependency reading `X-Demo-Role`, so hiding a button and refusing the call
cannot drift apart.

| role | may |
|---|---|
| organiser (default) | run rosters, draft cards, confirm / correct / reject / request_revision, export credentials, mint share links, reset the demo, read everything |
| host | confirm, correct, reject, request_revision, export, read cards/ledger/evaluation; **not** draft, **not** run rosters, **not** reset |
| volunteer | read the public drive summary only |
| viewer | read the evaluation only |

**This is a demo role switch, not authentication.** The caller chooses its own role
in a header; there is no login, session, signature or server-side identity, so any
client can send `organiser`. It exists to make the intended division of labour
visible and testable, and it is stated as such in the module docstring, the route
docstring and every 403 body. Real deployments must derive the role from an
authenticated identity - that is out of scope here.

**Endpoints and schemas.**

* `GET /api/capabilities?role=...` -> `CapabilitySet` (`role, screens, actions, demo_only, note`).
  Missing role means organiser; an unknown role here is **422** (query validation).
* Mutating routes read `X-Demo-Role`; an unknown role there is **403**, as is a known
  role without the action. Missing header means organiser, which keeps every
  existing client working unchanged.
* Enforced: `POST /api/roster`, `/api/roster/why-not`, `/api/roster/dropout`
  (`read_roster`), `/api/evidence/draft` (`draft_cards`), `/confirm`, `/correct`,
  `/reject`, `/request_revision`, `/api/export/credential/{id}`, `POST /api/drive/share`
  (`share_drive`) and `POST /api/demo/reset` (`reset_demo`).

**Tests.**

```
..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_capabilities.py -q
32 passed, 25 warnings in 2.12s
```

Covered: the menu equals the matrix for each of the four roles, the default is
organiser, role names are case/space tolerant, unknown role is 422 with the choices
named, the matrix invariants (organiser may every mutating action; viewer and
volunteer may none; host may confirm but not draft or reset), no header keeps the old
behaviour, viewer/volunteer get 403 on **every** mutating route (the test table is
asserted equal to `capabilities.MUTATING_ACTIONS`, so a new action cannot be added
without a test), host confirms and exports, only the organiser may reset, and an
unknown header role is 403 with the reason.

---

## 4. Follow-up: localized display text (Hindi / English)

**What it does.** `GET /api/tasks?lang=hi` and `POST /api/roster` with
`{"lang": "hi"}` attach a `display` block: task title, slot, role names and skill
labels in Hindi, plus the READY / NOT READY verdict, the recruit-request sentences
and the per-pick reason for every roster method. `display.lang` says which language
a block is in.

**Why it matters.** Hindi is how the work is actually discussed at the block level.
The organiser can hand the screen to a host or a panchayat member without translating
"single point of failure" by hand.

**The contract: the Hindi is a view, not a second source of truth.** Each Hindi
sentence is built from the same structured fields as its English counterpart (role,
needed count, skill ids, slot, area, travel limit), so ids, counts and the verdict
are identical in both languages, and a number only appears in Hindi where it is
computed by the same expression as the English one: the gap count, the unfilled-role
count and the robustness percentage (`:.0%` on the same float).

One deliberate exception: the Hindi pick sentence quotes no distance. English quotes
the raw distance (`:.0f` in `solver/cp_sat.py`), while `Assignment.distance_km` is
stored rounded to one decimal, so a kilometre figure in Hindi could round to a
different digit than the English sentence for the same volunteer. Rather than show
two different numbers for one pick, the Hindi sentence states the role and the slot
and leaves the distance in the structured field; a test asserts the Hindi pick text
contains no digits. The tests compare the numbers that do appear, field by field,
rather than trusting the prose.

**What is NOT translated, deliberately.**

* Text a language model wrote - contribution card summaries and evidence text -
  stays in whatever language the host wrote it in. Cards carry no `display` block.
* District and block names are place names and stay as they are.
* A role name or title this module does not know is returned **unchanged** in both
  languages. No machine translation, no invented label.

**Endpoints and schemas.** `TaskSpec.display` (`TaskDisplay` -> `RoleDisplay`,
`SkillLabel`), `RosterResult.display` (`RosterDisplay` -> `RecruitDisplay`,
`AssignmentDisplay`), `RecruitRequest.kind` (`unresolved | unfilled | standby`, which
chooses the Hindi template honestly instead of guessing from the English sentence).

**Tests.**

```
..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_i18n.py -q
15 passed, 2 warnings in 1.46s
```

Covered: ids, counts and skill ids match the canonical task per role; the default
language is English and mirrors the canonical text; an unknown language is 422; for
each of the four roster methods the Hindi block keeps the verdict, recruit role ids,
needed counts, assignment ids and the numbers inside the sentences; an unresolved
role asks for a decision with `needed` unchanged; the two languages produce the same
assignments and metrics (only `solve_ms` differs, it is timing); unknown text is
returned unchanged; card text is not localized.

---

## 5. Cross-cutting notes

* **Existing behaviour.** No existing endpoint changed its contract except for the
  optional `X-Demo-Role` check (default organiser keeps old clients working) and the
  additive fields listed above (`reason`, `revision_reason`, `kind`, `display`,
  `computed_at`). The 692 tests that existed before this work still pass; the suite
  is now 845.
* **No secrets in code.** The share secret is an environment variable or an
  in-memory random value; nothing secret is committed or logged.
* **Hash chain honesty unchanged.** A hash chain shows edits, not truth; the reason
  field is inside the hash, but the host's confirmation is still the source of truth.
  Tail truncation is still only detectable against an externally kept head hash, and
  `GET /api/ledger/verify` still calls `verify()` without such an anchor.
* **Pre-existing limits found while reviewing (not changed here, because changing
  them would change existing endpoint behaviour):** `correct` does not re-run the
  deterministic rules on the new hour count; a draft with an empty assignment list
  supersedes every undecided card for that task; the ledger's RLock is process-local,
  so two workers on one journal would fork the chain; `GET /api/ledger/verify` calls
  `verify()` without an externally kept head anchor.
* **Why the share snapshot is only as trustworthy as the caller.** The snapshot the
  public link serves is built from the task body sent to `POST /api/roster`, because
  the organiser may edit roles before planning and the link should show the plan that
  was solved. With no authentication, anyone who may run a roster can therefore change
  what a share link displays for a known drive id; the public page exposes no volunteer
  data, but its content is not signed. In a deployment this route sits behind the
  organiser identity, and the snapshot is written only by that identity.
* **Not gated by the demo matrix:** `POST /api/extract-roles` and `GET /api/eval`
  (compute/demo routes, no evidence state), and the read routes `GET /api/evidence/cards`,
  `/api/ledger`, `/api/tasks`, `/api/volunteers` (the local demo's data source). The
  matrix describes the mutating routes; the read routes are listed here so the gap is
  explicit rather than implied.
* **Rotating the share secret** is an explicit act: the value is cached per process, so
  changing `SEWA_SHARE_SECRET` needs `share.reset_secret()` or a restart, as the
  docstring now says.
