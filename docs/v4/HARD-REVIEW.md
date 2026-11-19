# Hard review before merge

**Verdict: Ship with changes. Do not merge for the public demo yet.** The product has a coherent organiser story, a real solver and evaluation, clear synthetic-data notices, a useful manual-role fallback, and source-qualified MY Bharat copy. The 80-bit HMAC share key is a sensible opaque handle for one synthetic drive. The problems below concern the evidence record, a publicly writable demo, and the mismatch between the two branches.

Scope: `git diff main..frontend-v2` and `git diff main..backend-ideas`, plus the backend worktree's **uncommitted** patch where explicitly noted. I did not change either branch. The running `127.0.0.1:8000` API is the old contract: `GET /api/capabilities?role=host` and `GET /api/geo/tree` both returned **404**, so it cannot validate the merged UI. Live `GET /api/eval` reported 10 tasks, 80 volunteers, ready means **0.70 / 0.10 / 0.70 / 0.15** for CP-SAT / nearest / manual / random, matching `docs/EVAL_RESULTS.md`. `npm run build` passed (CrewScene **1,168.60 kB / 323.57 kB gzip**); `npm run test` passed **7/7**; `npm run lint` passed; backend worktree pytest passed **840 tests**. The backend branch report says 839 because the current worktree contains an uncommitted patch and test. I did not run the E2E suite: `frontend/tests/journey.spec.ts:16,25,30-78,109` resets the API and rewrites the checked-in screenshots.

## Findings, ranked

### Blocker 1 — Branch HEAD can change a card without a ledger entry; simultaneous decisions can both win

**Where:** `backend/app/main.py:369-390,424-453`; `backend/app/evidence/ledger.py:142-271`.

**Evidence:** In `backend-ideas` HEAD, `_decide` assigns `c.claimed_hours`, `c.status`, and `c.revision_reason` **before** `ledger().append(...)` (`git show backend-ideas:backend/app/main.py`, lines 441-450). The draft path stores `store[c.id] = c` before append. The worktree's uncommitted diff changes the order, but will not arrive in a branch merge. Even with that patch, `_decide` reads and checks the state at 430-436 outside the ledger lock, appends at 450, then stores at 451; two FastAPI threadpool requests can both pass the same draft-state check and append conflicting final decisions. `_save_cards` at 123-125 rewrites the JSON without a shared transaction.

**Why it matters:** A failed append can leave a final card in memory with no matching chain entry. A concurrent confirm and reject can both return 200 for one card, contradicting the claimed final-state machine. This attacks the central accountability claim.

**Exact fix:** Commit and review the append-before-store patch, then put state lookup, transition, append, store, and atomic card-file replacement under one process-wide transaction lock; use an interprocess lock or single-writer store if multiple workers are allowed. On append failure the card and journal must retain their previous state. Add a barrier-based simultaneous confirm/reject test asserting exactly one 200, one 409, one terminal card, one decision entry, and a verifying ledger.

### Blocker 2 — A public caller can operate the organiser demo and read the full synthetic record

**Where:** `backend/app/capabilities.py:5-20,43-68`; `backend/app/main.py:50-65,202-216,395-415,481-503`; `frontend/src/api.ts:18-24,34-55`; `frontend/src/App.tsx:18-28`.

**Evidence:** The backend explicitly says the caller chooses `X-Demo-Role`; `normalise_role` defaults a missing header to `organiser`. The frontend sends no role header, so every call is organiser. `POST /api/demo/reset`, roster, card decisions and share minting accept that default. `GET /api/volunteers`, `/api/tasks`, `/api/evidence/cards` and `/api/ledger` are open; the new public share key does not protect those routes. The UI has no role switch or capability menu.

**Why it matters:** On a public demo, any visitor can reset or rewrite its evidence state, and an opaque share link creates a false impression that it is the only way to see a drive. The data are synthetic, so this is demo integrity and privacy-design honesty, not a claim of real-person leakage.

**Exact fix:** For an internet-facing demo, make mutations available only to a controlled operator session or publish a read-only replica with a separately protected writable console. Keep the role switch labelled **simulation, not authentication**; send `X-Demo-Role` consistently; gate the open read routes to match the advertised capability matrix, or mark them explicitly public in both API and UI. Test an untrusted caller cannot reset, decide, or enumerate cards.

### Major 3 — Evidence flags and revisions can be represented inaccurately

**Where:** `backend/app/main.py:355-390,440-450`; `backend/app/evidence/transitions.py:46-69`; `frontend/src/Console.tsx:86-95,116`.

**Evidence:** `correct` changes `claimed_hours` without rerunning `rules.check_card`, so a pre-correction `hours_exceed_recorded` flag can remain or a new mismatch can be introduced without a flag. An empty `drafted` list makes `new_ids` empty and deletes every undecided card for that task at 370-373. In branch HEAD the revision back-edge calls `next_state` but discards its target and sets `flagged` or `draft` from rule results. The uncommitted worktree patch instead forces `draft` even when a fresh warning or block flag is attached. The UI renders `revision_requested` as `statusDraft`, has no revision action or reason, and shows only confirm/correct/reject.

**Why it matters:** A host can confirm an hour claim whose displayed warning refers to the previous value, or miss a new warning. A failed/empty extraction can remove draft cards. A revision's state and flags disagree in the worktree patch, allowing a flagged card to look ordinary.

**Exact fix:** Define the state-table transition for redraft with flagged output explicitly, or always return to `draft` and make the UI enforce/display blocking flags independently. Re-run deterministic rules on correction and persist the new flag set in the hashed card payload. Do not supersede all cards on an empty draft result; distinguish an intentional empty assignment set from extraction failure. Add tests for these three cases, plus the UI revision reason and redraft cycle.

### Major 4 — Merged API work is absent, and existing UI state can show a verdict for a different plan

**Where:** `frontend/src/api.ts:34-55`; `frontend/src/types.ts:4,21-25,50-76`; `frontend/src/Console.tsx:49-58,69-90,107,113-118,125-145`; `frontend/src/District.tsx:16-22,29`; `frontend/src/Volunteer.tsx:13-20`; `backend/app/main.py:207-216,224-269,295-317,329-343`.

**Evidence:** There is no `capabilities`, `geo/tree`, share-mint, share-summary, revision, `lang=hi`, or `display` method in `api.ts`. `CardStatus` omits `revision_requested`; task/roster types omit `display`; recruit requests omit `kind`. `Console` keeps `roster` after editing roles or brief and keeps `all` after dropout, so the board and four-method comparison can represent different plans. `chooseTask` clears cards and never reloads them. `District` fires ten concurrent `POST /api/roster` requests on mount; in the new backend each request overwrites that drive's share snapshot (`main.py:307-317`). Opening a map can therefore replace an organiser's edited public summary with the canonical task plan. The share snapshot is also not updated by `/api/roster/dropout`.

**Why it matters:** After merge, the advertised role, Hindi, revision, share, and geo features are absent. Worse, a district visit or dropout can publish a READY value that no longer corresponds to the visible crew. A 403 from a selected non-organiser role would surface only as a generic error.

**Exact fix:** Implement the post-merge UI contract in the dedicated integration package in `FIX-PLAN.md`. Invalidate the roster and downstream cards on every plan edit; label the four-method comparison as the original solve or recompute it after dropout. Make district readiness a read-only endpoint or cached plan query, never a side-effecting solve. Keep the share snapshot tied to a plan/version and update or mark it stale after dropout. Reload cards for the selected task.

### Major 5 — Mock evaluation and published captures overstate or change the measured result

**Where:** `frontend/src/mock.ts:88-99`; `frontend/src/Landing.tsx:19-28,65`; `design/motion/src/root.tsx:8-17,46-66`; `docs/video/product-explainer.hi.vtt:19-20`.

**Evidence:** `mockEval` claims CP-SAT coverage **0.97** and robustness **0.90**, manual ready **0.60**, and only **40** volunteers. The allowed evaluation and live API are **0.9167**, **0.76**, **0.70**, and **80**. `docs/screens/v4/landing-390x844.png` captures the animated counters at **63/9/63/14%**, while the API and desktop capture show **70/10/70/15%**. `docs/screens/v4/console-task-390x844.png` was captured during a fade, so the main form appears washed out; `console-evaluation-chart-1440x900.png` is blank except for the page shell, despite the separate evaluation capture showing charts. The explainer uses full-page screenshots in a 505×485 box with `objectFit: cover`; its brief preview shows an older person-token hero unlike the current cylinder scene. The Hindi VTT says the *organiser* confirms cards; the English VTT and product contract say the *host* does. Current MY Bharat text is qualified and linked, and I found no government marks or close visual imitation in the inspected screens.

**Why it matters:** Judges may see invented mock statistics and stale or transient numbers as measured evidence; the video misstates who attests a contribution. The small embedded screen cannot demonstrate the product on a projector.

**Exact fix:** In mock mode use a verbatim frozen copy of the actual evaluation with its provenance, or remove evaluation numbers and say they are illustrative. Expose final counter values before screenshots or disable counter motion for capture. Re-capture current UI, zoom to the active decision/card rather than a full page, and render the video again. Change the Hindi caption to `होस्ट पुष्टि या सुधार करता है` and audit all claims against the allowed list.

### Major 6 — Hindi is incomplete, and axe finds a serious failure on every Hindi route

**Where:** `frontend/src/App.tsx:25`; `frontend/src/Console.tsx:113-118,129-138,145`; `frontend/src/District.tsx:29`; `frontend/src/Volunteer.tsx:20`; `frontend/src/i18n.ts:7,17,19,22-25`; `backend/app/i18n.py:165-170,181-211`.

**Evidence:** I ran `@axe-core/playwright` with WCAG A/AA tags at 390×844: English `/`, `/console`, `/volunteer`, `/districts`, `/method` each had `[]`; **all five Hindi routes** reported `label-content-name-mismatch`, serious, at `a[aria-label="सेवासर्कल"]` because the visible logo remains `SewaCircle`. The UI shows canonical English task titles, roles, skill IDs, solver reasons, recruit reasons, extraction decisions, flags, counterfactual narratives and evaluation misses after Hindi toggle. Backend Hindi `display.assignments` drops skill level, recent-pick and mentor reasons, and its standby sentence drops the person's identity; these two follow-ups remain open in `docs/v4/REVIEW-backend-ideas.md`. `optIn` is translated as `सहमति` (consent), conflating opt-in with guardian permission.

**Why it matters:** The bilingual promise fails in the exact decision details a Hindi-speaking organiser must inspect. The logo's accessible name does not contain its visible text, which can break speech control. The backend's Hindi pick explanation loses the fairness reasons the product advertises.

**Exact fix:** Make the logo accessible name include visible `SewaCircle`; run axe after switching to Hindi on every route and console step. Use the new task and roster `display` blocks by stable IDs, with explicit fallback for LLM-produced text. Add reason codes/parameters in the backend so both languages carry equivalent facts; retain the standby person's name in both. Translate `opted-in` as `जिन्होंने इस अभियान में रुचि जताई है` or equivalent, and have a Hindi reviewer read the rendered screens and VTT.

### Minor 7 — Visual proof, load boundary and tests do not yet support the finish claim

**Where:** `frontend/src/CrewScene.tsx:15-51,60-91,98-114`; `frontend/src/Landing.tsx:13,31-50,59`; `frontend/src/Console.tsx:113-118,135-145`; `frontend/tests/journey.spec.ts:9-13,15-80,100-129`; `frontend/src/i18n.test.ts:4-16`; `frontend/src/Verdict.test.tsx:8-34`.

**Evidence:** `docs/screens/v4/models/kit-gallery.png` shows a token, standby and READY seal as plain discs; `hero-ready.png`, `landing-3d-1440x900.png`, and `docs/video/previews/hero-*.png` show a flat rectangle behind the ring and tiny standby nodes. Neither the discs nor scene label identifies a person or an essential-role backup. Build confirms the **323.57 kB gzip** scene chunk; `Landing` lazy imports it and mobile/reduced-motion paths avoid it, so code splitting is real. But `Landing` detects WebGL only once and has no error boundary or context-loss fallback, and the 90 desktop Lighthouse score is a single local run (`docs/v4/lighthouse/landing-desktop.json`: LCP 1.06 s, TBT 237.5 ms). `Console.tsx` has 146 physical lines but lines 116 and 114 are **3,010** and **2,748** characters; the tests mostly assert presence and self-consistency, and the E2E test does not test revision, role restrictions, stale state, or Hindi decision details.

**Why it matters:** The central visual does not quickly explain the crew decision to a judge, and a runtime WebGL failure can leave a blank hero. Passing tests and Lighthouse snapshots are narrower than the report's complete, accessible bilingual flow claim. Dense JSX makes the state bugs harder to review.

**Exact fix:** Give the volunteer token a distinct human-readable silhouette, visibly pair each essential socket with its standby, and remove the rectangular backing; verify at 390 px and projector distance. Add a scene error/context-loss fallback and confirm the chunk is absent from non-landing network traces after merge. Split console views by step without changing behavior. Add tests for plan invalidation, empty draft, failed append, revision, mock numbers, Hindi axe, and source-faithful captions. Treat local Lighthouse as a baseline and remeasure the merged production build on the intended demo machine.

## Merge and integration map

`Compare-Object (git diff --name-only main..frontend-v2) (git diff --name-only main..backend-ideas) -IncludeEqual -ExcludeDifferent` returned **no shared changed paths**. No text merge conflict is predicted from the committed diffs. The conflicts are semantic, and the backend's uncommitted `main.py`/test patch is **outside** the branch merge.

| Post-merge UI location | New contract and required change |
| --- | --- |
| `api.ts` transport; `App.tsx` nav | Fetch `/api/capabilities?role=...`; persist a clearly labelled demo role; attach `X-Demo-Role` to guarded calls; render screens/actions from capability keys and handle 403. Do not call this authentication. |
| `Console.tsx` task and `Volunteer.tsx` opted-in tasks | Request `/api/tasks?lang=hi` after language changes; show `TaskSpec.display` title/slot/roles/skills, retaining canonical IDs and brief for POST. Prevent late English responses overwriting Hindi. |
| `Console.tsx` crew, `Verdict.tsx` | Include `lang` in POST `/api/roster`; use `RosterResult.display` verdict, recruit and assignment text by role/volunteer ID; use `RecruitRequest.kind`; invalidate display on language or plan change. Avoid replacing actual reasons with less informative Hindi. |
| `Console.tsx` evidence and ledger | Add `request_revision` with required reason; show `revision_requested` and reason; allow redraft; show ledger `reason`; handle 409 with refresh. Gate buttons by role action. |
| `Console.tsx` crew/share and a new public summary route | Mint via `POST /api/drive/share {task_id}`; open `/api/drive/{share_key}`; show `ready=null`/`computed_at`; never derive the key from task ID client-side; do not show volunteer details on the public route. |
| `District.tsx` | Consume `/api/geo/tree` for districts, block availability, source/caveat/retrieved date and ETag; stop ten write-like roster calls on mount. Show `not computed` without turning it into NOT READY. |
| `types.ts`, `mock.ts`, `journey.spec.ts` | Mirror all additive schemas and routes; make mock semantics honest; test all four demo roles, Hindi, revision, share and geo. |

## Author versus reviewer: five forced challenges

1. **Correctness.** Author: append-before-store in the worktree prevents an orphaned decision. Reviewer: HEAD lacks it, and two decisions still race. Sketch: `with decision_lock: current=cards()[id]; next=transition(current); ledger.append(next); atomic_save(next)`; assert one 409 under concurrency.
2. **Error handling.** Author: a model can return no cards and the draft route cleans stale cards. Reviewer: an extraction failure must not silently erase all undecided cards. Sketch: `if not drafted and req.assignments: raise HTTPException(502, "no cards drafted")` before supersession; test untouched store and chain.
3. **Performance.** Author: lazy `CrewScene` keeps the console fast. Reviewer: that boundary is real, but ten concurrent district solves produce server work and mutate share summaries. Sketch: replace `Promise.allSettled(data.map(api.roster))` with a read-only status fetch.
4. **Security.** Author: synthetic data and the role notice disclose the demo limitation. Reviewer: a public visitor can still reset the live demonstration. Sketch: require a server-held operator capability for write routes; an arbitrary `X-Demo-Role` remains a visual simulation only.
5. **Testing.** Author: green unit/E2E/Lighthouse reports support launch. Reviewer: the independent Hindi axe run fails and the live API lacks the new routes. Sketch: after switching language, run axe on each page and test role/contract journeys against the merged backend. Re-run this review after those fixes because integration and evidence paths remain unproved.
