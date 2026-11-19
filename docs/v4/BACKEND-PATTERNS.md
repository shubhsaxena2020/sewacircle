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
922 passed, 195 warnings in 23.52s
```

Section map: 1-4 are the round-2 patterns (state machine, share keys, capability
menu, Hindi display); 5-7 are the round-3 hard-review fixes (atomic decisions, rules
and revision semantics, the public-demo boundary with plan-versioned snapshots); 8
lists the cross-cutting notes and the limits that are still open.

---

## 1. Contribution card state machine with a back-edge

**What it does.** A contribution card is a claim about a person's unpaid work, so
it moves through named states and never skips a step. `backend/app/evidence/transitions.py`
holds the only table that decides where a card may go:

| from | action | to |
|---|---|---|
| draft | confirm / correct / reject / request_revision | confirmed / corrected / rejected / revision_requested |
| flagged | confirm / correct / reject / request_revision | confirmed / corrected / rejected / revision_requested |
| revision_requested | redraft (internal, clean redraft) | draft |
| revision_requested | redraft_flagged (internal, redraft that trips a rule) | flagged |

`confirmed`, `corrected` and `rejected` have no outgoing edge: a decision is final
in this prototype and the ledger keeps the history instead. `revision_requested`
has exactly two exits, both taken by the drafting route - `redraft` back to `draft`
when the new text is clean, and `redraft_flagged` into `flagged` when the new text
still (or newly) raises a warn/block rule flag. That is the *back-edge* the old
one-way flow lacked, and the second exit is what stops a redraft from quietly
returning a suspicious card to the unremarkable pool.

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
45 passed in 0.20s

..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/evidence/test_card_state_machine.py -q
37 passed, 41 warnings in 5.88s
```

`test_transitions.py` has one case per legal edge (10) and one per illegal
`(state, action)` pair (26), plus invariants: every key and target is a declared
state, the table matches `schemas.CardStatus`, `revision_requested` has exactly two
exits and no other state has a redraft edge, and "terminal" means exactly "no
outgoing edge". `test_card_state_machine.py` drives the same edges through HTTP:
actor/reason/timestamp in the ledger, re-draft back to draft, a redraft that trips a
rule landing in `flagged` (and the clean half landing in `draft`), non-blank reason
required, 409 from every final state, no card stranded in `revision_requested` when
its volunteer leaves the draft, legacy journal lines still verifying, and an edited
or cleared reason breaking the chain.

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
  (`title, district, block, slot, roles[SharedRoleCount], ready, computed_at, plan_version, stale, notice, synthetic`).
* Sequential ids (`task-01`, `1`, `TASK-01`) are refused with 404 before any secret
  is touched: the resolver requires a 16-character uppercase RFC 4648 base32 string.
* When a roster was computed in this process, the summary is the snapshot of **what
  was actually planned** (edited title/roles included) with `ready`, `computed_at`
  and the plan's `plan_version`; otherwise it is the known task with `ready = null`,
  `computed_at = null`, `plan_version = ""`, `stale = false`.

**Plan versioning and staleness.** `share.plan_version(roles, options, assignments,
standby)` is the SHA-256 of the plan: the roles (sorted, all planner-relevant
fields), the roster options, the crew as `role_id:slot_index:volunteer_id` and the
standby ids. It is deterministic (order does not change it) and sensitive (a
different crew, a different count, a different skill is a different version). The
snapshot stores it with `computed_at`; the server also remembers the version of the
organiser's **latest solved roster** per task. `GET /api/drive/{key}` recomputes
`stale = snapshot.plan_version != latest_solved_version` on every read, and
`POST /api/roster/dropout` refreshes the snapshot with the healed plan - which is a
different crew, hence a different version, hence `stale: true` until the organiser
re-runs the roster. The version deliberately includes the crew: a dropout changes
who is on the drive without changing the roles, and that is exactly the change a
viewer of an old link must be told about.

`GET /api/drive/status` returns, for every task id the server knows,
`{task_id, ready, computed_at, stale}` - `ready` and `computed_at` are `null` when no
roster was computed for that task in this process. It reads the in-memory snapshots
and never calls the planner: it is the district map's data source, registered before
the `{share_key}` route so the literal path is not parsed as a key, and a test
asserts it leaves the card store, the journal, the snapshots and the plan registry
byte-identical (and that it still answers 200 when every solver entry point raises).

**Tests.**

```
..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_share_keys.py -q
26 passed, 1 warning in 1.97s
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

**Per-pick reasons: one structured cause, two renderings.** The solver no longer
writes prose that Hindi has to paraphrase. `solver/cp_sat.py` emits
`Assignment.reason_codes` - a list of `PickReason(code, params)` - and the English
`Assignment.reasons` are rendered from those codes with
`i18n.reason_text(code, "en")`. The Hindi view calls the same function with `"hi"`.
The catalogue covers every reason the solver writes:

| code | params | English | Hindi |
|---|---|---|---|
| skill_confirmed | skill, level | Has first aid (level 2) | प्राथमिक उपचार (स्तर 2 तक प्रशिक्षित) |
| skill_self_declared | skill | Self-declared ... (host to confirm) | स्वयं घोषित ... (होस्ट की पुष्टि बाकी) |
| open_role | - | Open role: any volunteer can do it | खुली भूमिका: कोई भी स्वयंसेवक यह काम कर सकता है |
| slot_and_distance | slot, distance_km | Free sat morning; 7 km from the site | शनिवार सुबह उपलब्ध; साइट से 7 किमी दूर |
| not_picked_recently | days | Not picked in the last 90 days | पिछले 90 दिनों में नहीं चुने गए |
| picked_heavily | count, days | Picked 4 times in 90 days; ... | 90 दिनों में 4 बार चुने गए; ... |
| newcomer | past_drives, mentor_name? | Newcomer (1 past drives), paired with X | नए स्वयंसेवक (1 पिछली ड्राइव), X के साथ जोड़ी |
| experienced_mentor | past_drives | Experienced (9 drives): can guide newcomers | अनुभवी (9 ड्राइव): नए साथियों का मार्गदर्शन कर सकते हैं |
| minor_guardian_consent | - | Under 18: guardian consent on file | 18 वर्ष से कम: अभिभावक की सहमति दर्ज है |
| promoted_from_standby | - | Promoted from standby | स्टैंडबाय से पदोन्नत |

Both renderings take the numbers from the same `params`, and the distance is stored
raw (`round(distance_km, 3)`) and formatted with `:.0f` in both languages, so the
whole-kilometre figure cannot differ between them. The test asserts that the
**digits** in the Hindi sentence are the same multiset as the digits in the English
sentences (level, km, 90, past drives), which is a fact check rather than a prose
check; the old "Hindi contains no digits" rule existed only because Hindi had no
structured source, and is gone.

Standby requests keep the person's name in both languages: `RecruitRequest` gained
`blocked_by_names`, so the English "if Imran B. cannot come" and the Hindi
"अगर Imran B. न आ सकें" name the same volunteer. A roster method that writes no codes
(the baselines keep their own English narration) falls back to a role + slot Hindi
line rather than inventing facts.

**What is NOT translated, deliberately.**

* Text a language model wrote - contribution card summaries and evidence text -
  stays in whatever language the host wrote it in. Cards carry no `display` block.
* District and block names are place names and stay as they are.
* A role name or title this module does not know is returned **unchanged** in both
  languages. No machine translation, no invented label.

**Endpoints and schemas.** `TaskSpec.display` (`TaskDisplay` -> `RoleDisplay`,
`SkillLabel`), `RosterResult.display` (`RosterDisplay` -> `RecruitDisplay`,
`AssignmentDisplay`), `RecruitRequest.kind` (`unresolved | unfilled | standby`, which
chooses the Hindi template honestly instead of guessing from the English sentence),
`RecruitRequest.blocked_by_names`, `Assignment.reason_codes` (`PickReason`).

**Tests.**

```
..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_i18n.py -q
17 passed, 2 warnings in 1.67s
```

Covered: ids, counts and skill ids match the canonical task per role; the default
language is English and mirrors the canonical text; an unknown language is 422; for
each of the four roster methods the Hindi block keeps the verdict, recruit role ids,
needed counts, assignment ids and the numbers inside the sentences; an unresolved
role asks for a decision with `needed` unchanged; the two languages produce the same
assignments and metrics (only `solve_ms` differs, it is timing); the Hindi pick text
carries exactly the digits of the English pick text and the facts named by every
reason code; every reason code renders in both languages; the standby sentence names
the same person in both; unknown text is returned unchanged; card text is not
localized.

---

## 5. Atomic card decisions: one lock, one entry, one state

**What it does.** A decision (`confirm`, `correct`, `reject`, `request_revision`) is
one indivisible step in `backend/app/main.py`:

```
CARD_LOCK: lookup card -> transitions.next_state -> ledger.append -> store -> _save_cards()
```

`CARD_LOCK` is one process-wide `threading.RLock`. The ledger append happens *before*
the store commit, and `_save_cards()` writes a temp file in the data directory, fsyncs
it and `os.replace`s it over `cards.json`, so a reader or a crash never sees half a
file. The drafting route and the demo reset take the same lock.

**Why an organiser cares.** Two hosts looking at the same contribution card is the
normal case, not an exotic one: the district organiser and the person who was on site
both open the review screen, and one confirms while the other rejects. Before this,
both requests could pass the state check, both appends could succeed, and one card
could end up with two contradictory decision entries and a final status that no entry
matches. Now the loser gets 409 with the legal actions named, and the ledger has
exactly one decision entry for that card.

**Documented limitation: this is a single-process prototype.** The lock is a
`threading.RLock`, not a database transaction or a file lock, so it protects threads
inside one Python process. Two uvicorn workers would each have their own lock, their
own in-memory card store, and the ledger's own `RLock` is process-local too - two
writers on one journal would fork the hash chain. Running this behind more than one
worker needs a shared store with a real transaction (or a cross-process lock around
the append). That is stated in the `app/main.py` module docstring, not just here.

**Tests.**

```
..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/evidence/test_atomic_decisions.py -q
6 passed, 7 warnings in 2.13s
```

Covered: a barrier releases one `confirm` and one `reject` at the same instant on the
same card (three rounds, fresh cards) and the result is always exactly one 200 and one
409, exactly one decision entry, the stored card matching the winner, and
`/api/ledger/verify` ok; an injected `OSError` from the ledger's write leaves the
journal bytes, the cards file bytes and the in-memory card unchanged (the route is
500 and nothing is decided); the card file is written through `os.replace` on a
`.tmp` file *after* the append, with no temp files left behind; and a plain illegal
second action writes nothing.

The barrier test was checked against a deliberately unlocked build (a temporary
conftest replacing `CARD_LOCK` with `contextlib.nullcontext()`): all three rounds
failed there, so the test detects a missing lock rather than passing by luck.

---

## 6. Rules on correction, flag-aware redraft, non-destructive drafting

**`correct` re-runs the rules.** `_decide` recomputes `rules.check_card` on the
corrected card and stores the flags on it, so a host who raises 5 recorded hours to 9
sees `hours_exceed_recorded` before confirming, and a host who corrects 14 hours sees
the `implausible_hours` block. The status stays `corrected`: the decision is the
host's, the flags are evidence. The attendance rows come from a per-task cache filled
by the draft route; after a restart the cache is empty and the card's own persisted
`recorded_hours` (which *is* the recorded sheet value) is turned back into one row, so
the claim-versus-record rule still works. Both paths are tested.

**A redraft that trips a rule lands in `flagged`.** The one transition table has two
exits from `revision_requested`: `redraft -> draft` and `redraft_flagged -> flagged`.
The drafting route chooses between them from the flags of the new text, so a card the
host asked to fix cannot come back looking unremarkable while it still trips a rule.
The ledger records `draft` or `flag`, and the reason names the revision request.

**Empty drafting is non-destructive.** If the drafting step produces no card, the
route answers **502** when assignments were sent ("nothing was changed") and `[]` when
none were, without touching the card store or the journal. This is checked *before*
the supersede loop, so a failed draft can never delete the undecided cards the host is
still reviewing. A non-empty draft still supersedes stale undecided cards exactly as
before (tested, so the guard has not disabled the real path).

**Tests.**

```
..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/evidence/test_revision_and_rules.py -q
8 passed, 10 warnings in 2.65s
```

Covered: correcting above the recorded hours stores the warning (message quotes the
number), correcting back down clears it, correcting to 14 h stores the block flag
while the status stays `corrected`, the restart fallback still fires, `correct` still
requires hours (422, card unmoved), an empty draft with assignments is 502 with the
journal and cards file byte-identical, an empty draft with no assignments removes
nothing, and a real supersede still happens.

---

## 7. Public-demo boundary and plan-versioned share snapshots

**What it does.** `backend/app/demo_mode.py` holds one switch and one secret:

| env | effect |
|---|---|
| `SEWA_PUBLIC_DEMO` unset / `0` / `false` | gate OFF - the local prototype behaves exactly as before |
| `SEWA_PUBLIC_DEMO=1` + `SEWA_OPERATOR_TOKEN=<secret>` | every mutating route and the personal-data reads need `X-Operator-Token: <secret>` |
| `SEWA_PUBLIC_DEMO=1` and no token configured | **fail closed**: every protected route is 403, naming the missing variable |

The comparison is `hmac.compare_digest`. This is deliberately **not a login system**:
no account, no session, no user table - just a shared secret so a demo reachable from
the internet can be shown to a district officer without letting an anonymous visitor
reset the demo, re-plan a roster, decide cards, mint share links, or read the
volunteer list, the card store and the ledger.

**What is protected, and what stays public.**

* Requires the token: `POST /api/demo/reset`, `POST /api/roster`,
  `/api/roster/why-not`, `/api/roster/dropout`, `POST /api/evidence/draft`, the four
  decision routes, `GET /api/export/credential/{id}` (it names a volunteer and their
  hours, and it appends to the ledger), `POST /api/drive/share`, and the reads
  `GET /api/evidence/cards`, `/api/ledger`, `/api/ledger/verify`, `/api/volunteers`.
* Stays public: `/api/tasks`, `/api/eval`, `/api/geo/tree`, `/api/capabilities`,
  `/api/drive/{key}`, `/api/drive/status`, `/api/health`, `/api/meta`. None of them
  carries a volunteer id, name, contact, card text or ledger line.

**`X-Demo-Role` stays a labelled simulation on top.** The dependency order is
operator token -> demo role -> capability matrix, so a role header can never grant an
action the token does not grant, and can never stand in for a missing token. A valid
token with `X-Demo-Role: viewer` still gets 403 on `confirm`; `X-Demo-Role:
organiser` without the token still gets 403.

**Plan-versioned snapshots.** `share.plan_version(roles, options, assignments,
standby)` is the SHA-256 of the plan. The snapshot stores `plan_version` and
`computed_at`; `POST /api/roster/dropout` refreshes the snapshot with the healed plan;
`GET /api/drive/{key}` computes `stale` on read by comparing the snapshot's version
with the organiser's latest solved roster. `GET /api/drive/status` returns
`{task_id, ready, computed_at, stale}` for every known task id - nulls before any plan
- and never calls the solver.

**Tests.**

```
..\..\sewacircle\.venv\Scripts\python.exe -m pytest tests/test_public_demo.py -q
53 passed, 23 warnings in 4.02s
```

Covered: the gate is off by default and for `0/false/no/off/""`, on for
`1/true/YES/" on "`; every one of the eleven mutating routes is 403 without the token
and 403 with a wrong token (the endpoint table is data, so a new route shows up as a
missing case); the full evidence flow works with the token (draft, confirm, export,
cards, ledger, verify, volunteers, share, roster, reset); the four private reads are
403 without it; the five public reads and the public drive summary answer 200 without
it; `organiser`/`host` role headers never substitute for the token, and a valid token
with `viewer` is still refused; a missing configured token fails closed; the
comparison is exact (`TOKEN+" "` and `TOKEN.upper()` do not match); a roster run
stores a 64-hex `plan_version` that recomputes from roles + crew; a dropout refreshes
the snapshot and makes `stale` true while `latest_plan` keeps the organiser's plan;
re-solving clears it; `/api/drive/status` lists every known task with nulls first,
matches the snapshot afterwards, is idempotent, and leaves the ledger, snapshots, plan
registry and cards file untouched - asserted twice: by comparing state before/after and
by making every solver entry point raise while it still returns 200.

---

## 8. Cross-cutting notes

* **Existing behaviour.** No existing endpoint changed its contract except for the
  optional `X-Demo-Role` check and the optional operator token (both default to "off",
  so old clients keep working) and the additive fields listed above (`reason`,
  `revision_reason`, `kind`, `display`, `computed_at`, `plan_version`, `stale`,
  `blocked_by_names`, `reason_codes`). The 845 tests that existed before this round
  still pass, except three that asserted the behaviour this round deliberately
  reverses (one back-edge only; a redraft that trips a rule returns to `draft`; the
  Hindi pick text quoting no digits) - those three were rewritten to the new contract
  and the suite is now 922.
* **No secrets in code.** The share secret and the operator token are environment
  variables (the share secret may instead be generated in memory); nothing secret is
  committed or logged, and the ledger records no token.
* **Hash chain honesty unchanged.** A hash chain shows edits, not truth; the reason
  field is inside the hash, but the host's confirmation is still the source of truth.
  Tail truncation is still only detectable against an externally kept head hash, and
  `GET /api/ledger/verify` still calls `verify()` without such an anchor.
* **Pre-existing limits found while reviewing, and what this round did about them:**
  `correct` now re-runs the deterministic rules and stores the new flags; an empty
  draft no longer supersedes anything (502 with assignments, `[]` without); per-pick
  reasons are now structured and rendered in both languages. Still open, honestly:
  the decision lock and the ledger's RLock are process-local, so two workers on one
  journal would fork the chain (this prototype is single-process by design); the
  attendance sheet cache is process-local, so after a restart `correct` falls back to
  each card's persisted `recorded_hours`; and `GET /api/ledger/verify` calls `verify()`
  without an externally kept head anchor.
* **Why the share snapshot is only as trustworthy as the caller.** The snapshot the
  public link serves is built from the task body sent to `POST /api/roster`, because
  the organiser may edit roles before planning and the link should show the plan that
  was solved. With no authentication, anyone who may run a roster can therefore change
  what a share link displays for a known drive id; the public page exposes no volunteer
  data, but its content is not signed. In a deployment this route sits behind the
  organiser identity, and the snapshot is written only by that identity.
* **Two different boundaries, deliberately not merged.** `X-Demo-Role` (the
  capability matrix) is a *simulation* of who does what; `X-Operator-Token` (public
  demo mode) is the only thing that keeps an anonymous caller out. They are separate
  on purpose: the matrix must stay fake so the demo can show four roles without four
  accounts, and the token must stay real so the demo can be public. `GET
  /api/evidence/cards`, `/api/ledger` and `/api/volunteers` are not in the capability
  matrix (no demo role is refused them by role) but they ARE behind the operator token
  in public mode; `POST /api/extract-roles` and `GET /api/eval` are behind neither
  (no evidence state, no personal data).
* **Rotating the share secret** is an explicit act: the value is cached per process, so
  changing `SEWA_SHARE_SECRET` needs `share.reset_secret()` or a restart, as the
  docstring now says.
