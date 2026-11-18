# Inline Author vs Reviewer code review

**Scope:** the current contents of `../../backend/app/solver/cp_sat.py`, `metrics.py`, `baselines.py`, `../../backend/app/llm/extract.py`, `../../backend/app/evidence/rules.py`, `ledger.py`, `../../backend/app/main.py`, and `../../backend/app/data/synth.py`. Supporting contracts and tests were read. This is **not** a diff against a branch. The exchange below is a single-reviewer simulation, not a conversation with the original author or an independent agent. All diffs are **proposals only**; no source code was edited. The process follows the [opened original Author/Reviewer prompt](https://github.com/richiethomas/claude-devils-advocate/blob/main/devils-advocate.md), adapted to this code scope and run inline.

**Verification commands run from `backend/`:**

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; ..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
# 673 passed, 83 warnings in 8.32s
$env:PYTHONDONTWRITEBYTECODE='1'; ..\.venv\Scripts\python.exe -m eval.harness
# synthetic seed 7; 80 volunteers; 10 tasks
# CP-SAT / nearest / manual role coverage: 0.917 / 0.917 / 0.917
# CP-SAT / nearest / manual robustness:    0.760 / 0.153 / 0.760
# MISSES (6)
```

The harness output matched `../EVAL_RESULTS.md`. Passing tests establish regression status for existing assertions, not satisfaction of the proposed v2 contract.

## Round 1 — Correctness

**Reviewer:** `metrics.is_eligible` accepts any `self_declared_skills` entry regardless of `min_level` (`metrics.py:91-104`). `baselines.py:37-50` and `cp_sat.py:100-102` share that predicate, so an unchecked first-aid claim can become a primary or standby. The assignment gets a flag, but `../v2/PRD-v2.md` R2 promises a checked safety gate. Separately, `extract.py:50-65` removes unknown skill IDs. If all skill IDs are removed, `RoleSpec.required_skills=[]` means anyone qualifies (`../../backend/app/schemas.py:90-107`). These paths combine into a false "ready" result. The current tests passing does not change that.

**Author (simulated pushback):** The v1 contract explicitly permits self-declaration with a flag; the demo uses synthetic profiles. Dropping unknown skills keeps extraction usable rather than failing a whole task.

**Reviewer:** That defence works only for a v1 exploratory roster explicitly labelled "skill claim unverified." It does not support v2's checked-qualification wording. Silent conversion of an unknown requirement into an open role is worse than an extraction failure. Keep the draft visible, block approval until the requirement is mapped, and rerun the benchmark after adding provenance.

**Agreed proposed diff D1 (contract sketch; fixture migration required):**

```diff
--- a/backend/app/schemas.py
+++ b/backend/app/schemas.py
@@ class Volunteer(BaseModel):
+    checked_skills: list[str] = Field(default_factory=list)
@@ class RoleSpec(BaseModel):
+    requires_checked_skill: bool = False
--- a/backend/app/solver/metrics.py
+++ b/backend/app/solver/metrics.py
@@ def is_eligible(volunteer, role, task):
+    if role.requires_checked_skill and not any(
+        s in volunteer.checked_skills and volunteer.skills.get(s, 0) >= role.min_level
+        for s in role.required_skills
+    ):
+        return False
--- a/backend/app/llm/extract.py
+++ b/backend/app/llm/extract.py
@@ def extract_roles(brief_text, language_hint=None):
     if dropped:
-        notes.append(f"Dropped unknown skills {dropped} for role '{raw.get('role')}'.")
+        raise LLMError(f"Unmapped skill in role '{raw.get('role')}'; review before roster approval")
```

**Open design detail:** A caller cannot be trusted to set `requires_checked_skill=False` for a critical role. Define a server-owned safety taxonomy and test it before using this sketch. Do not merely add a flag that a request can disable.

**Reviewer:** The robustness denominator in `metrics.py:165-189` includes assigned `should` roles even though only `must` slots are checked for survival. A `should` volunteer who drops out can contribute an easy success. This is the documented metric, so it is not a hidden implementation error; it is an **outcome-label error** when the result is sold as critical-role readiness.

**Author (simulated pushback):** The current metric intentionally asks what happens after *any* team member drops; all methods use it, so comparison is internally consistent.

**Reviewer:** Internal consistency does not make the label intuitive. Keep that metric if useful, but add a must-role dropout metric for the hero claim and recalculate every published figure before using it. No past figure may be relabelled.

**Reviewer:** The other v2 differentiator is not yet reliable: `extract.py:126-137` accepts `c.get("role")` from the model when creating a contribution card. It does not check that string against the volunteer's planned assignment. A model can produce a convincing card for a role the person was never assigned.

**Author (simulated pushback):** The draft prompt includes the roster and a host reviews every card; allowing role text gives the model room to describe work that changed on site.

**Reviewer:** Actual work can differ, but that difference is exactly what must be visible. Store the planned role from the assignment; put any observed different role in a separate, host-reviewed field. Do not replace the planned link with model prose.

**Agreed proposed diff D1b:**

```diff
--- a/backend/app/llm/extract.py
+++ b/backend/app/llm/extract.py
@@ def draft_cards(task, host_notes, attendance_rows, assignments):
-        role = str(c.get("role") or next((role_name.get(a.role_id, a.role_id) for a in assignments if a.volunteer_id == vid), "Volunteer"))
+        role = next(role_name.get(a.role_id, a.role_id) for a in assignments if a.volunteer_id == vid)
```

The model's role suggestion can be retained as a separate draft observation later, but it must not overwrite assignment provenance.

## Round 2 — Error handling

**Reviewer:** `extract.py:55-65` treats a missing count as one and can leave confidence high; an invalid count is clamped silently to the schema range. A model that omits the count can change a crew size without an explicit review request. `main.py:210-225` mutates a stored card before appending the ledger entry, and `_save_cards` writes directly (`main.py:86-88`). If append or save fails, the in-memory card, JSON file and journal can disagree. `ledger.py:65-73` says a crash cannot leave a journal entry without its matching sidecar, but the journal is fsynced *before* the sidecar write (`ledger.py:185-199`, `210-233`). The claim is too strong.

**Author (simulated pushback):** The parser normalises messy model output for an editable draft; the state files are for a single-user local demo, and the journal sidecar is best-effort.

**Reviewer:** An editable draft is acceptable if uncertain counts visibly block approval. Local scope reduces impact but does not justify a false crash guarantee. Use an immutable proposed card in `_decide`, make card-file replacement atomic, and on startup detect ledger/card disagreement. A true multi-file transaction belongs in a later SQLite implementation.

**Agreed proposed diff D2 (partial fix; still requires recovery check):**

```diff
--- a/backend/app/llm/extract.py
+++ b/backend/app/llm/extract.py
@@ def extract_roles(brief_text, language_hint=None):
-        count = int(str(raw.get("count", 1)).translate(_DEVANAGARI_DIGITS))
+        if "count" not in raw:
+            needs.append(f"Set the count for '{raw['role']}' before approval.")
+            raw["confidence"] = "low"
+        count = int(str(raw.get("count", 1)).translate(_DEVANAGARI_DIGITS))
--- a/backend/app/main.py
+++ b/backend/app/main.py
@@ def _decide(card_id, action, status, req):
-    c = cards().get(card_id)
+    c = cards().get(card_id)
+    proposed = c.model_copy(deep=True) if c is not None else None
@@
-    c.status = status
+    proposed.status = status
@@
-    ledger().append(action, c, req.actor)
+    ledger().append(action, proposed, req.actor)
+    cards()[card_id] = proposed
```

The same `c` to `proposed` change must cover correction and `confirmed_by`. The code sketch is not a complete transaction. Correct the crash-safety documentation and fail closed on a mismatched journal/head at startup.

## Round 3 — Performance

**Reviewer:** Standby choice in `cp_sat.py:199-227` calls `compute_metrics` for each candidate in each greedy iteration. `compute_metrics` rebuilds eligibility and runs matching for every assigned dropout (`metrics.py:149-195`). The CP-SAT solver's time limit covers only its tier solves (`cp_sat.py:79-87`, `110-169`); it does not cap standby search. `ledger.py:210-214` rereads the whole journal on every append. The current small fixture does not show a measured performance failure, but `../../TRD.md` promises a bounded solve and easy scaling.

**Author (simulated pushback):** The current synthetic pool is small; caching and incremental matching would add complexity before there is a benchmark.

**Reviewer:** Agreed on avoiding a speculative rewrite. First report end-to-end roster latency including standby on larger declared synthetic pools. Add a wall-clock budget and an explicit `standby_incomplete` explanation so an over-budget result cannot look fully stress-tested. Profile before caching eligibility or changing matching.

**Agreed proposed diff D3 (illustrative guard):**

```diff
--- a/backend/app/solver/cp_sat.py
+++ b/backend/app/solver/cp_sat.py
@@ def build_roster(task, volunteers, options=None):
     t0 = time.perf_counter()
+    deadline = t0 + opts.time_limit_s
@@
-        _standby(task, volunteers, roster, opts)
+        _standby(task, volunteers, roster, opts, deadline)
@@ def _standby(task, vols, roster, opts, deadline):
         for v in cands:
+            if time.perf_counter() >= deadline:
+                roster.explanations.append("Standby search stopped at the time limit; resilience is incomplete.")
+                return picks
```

The patch needs a signature update and a status field so callers cannot interpret an incomplete search as an optimum.

## Round 4 — Security

**Reviewer:** `extract.py:111-115` redacts `host_notes` but sends `a.volunteer_name` in the separate roster list to the model. The redactor explicitly does not detect names (`extract.py:1-2`). The draft endpoint accepts caller-supplied assignments (`main.py:169-182`), so the synthetic label on stored fixtures is not an enforced privacy boundary. `main.py:202-224` also accepts any `actor` string to confirm a card. This is documented as a local demo, but a "host verified" claim would be false.

**Author (simulated pushback):** The intended demo uses invented names, and authenticated identity is explicitly out of scope for v1.

**Reviewer:** That limits immediate exposure, but the model prompt still violates the stated "PII redacted before any model call" rule (`../../PRD.md`). Remove names from model input; keep the endpoint local and label actor as a demo label. Do not deploy or call the record verified until authentication and access control exist.

**Agreed proposed diff D4:**

```diff
--- a/backend/app/llm/extract.py
+++ b/backend/app/llm/extract.py
@@ def draft_cards(task, host_notes, attendance_rows, assignments):
-    roster_list = "\n".join(f"- {a.volunteer_id}: {a.volunteer_name} ({role_name.get(a.role_id, a.role_id)})" for a in assignments)
+    roster_list = "\n".join(f"- {a.volunteer_id}: {role_name.get(a.role_id, a.role_id)}" for a in assignments)
```

This removes one exposure path; names in free-text host notes remain possible. A real-data route needs consent, stronger detection, retention controls and authenticated reviewers.

## Round 5 — Maintainability

**Reviewer:** `rules.py:60-66`, `84-141` builds a broad alias engine for legacy dicts although the API declares typed `AttendanceRow` inputs. `_row_matches` accepts a row with a volunteer ID but no task ID (`rules.py:190-201`), potentially attributing attendance from another task to the current card. This compatibility path is hard to reason about and does not serve the current typed contract.

**Author (simulated pushback):** Messy field exports are likely in a future pilot, and the tolerant parser helps rather than rejecting useful data.

**Reviewer:** That is a separate import problem. The decision rule should receive fully attributed typed rows. A CSV import adapter can reject or quarantine rows missing either ID, with a visible count. This also makes `no_attendance_record` meaningful.

**Agreed proposed diff D5:**

```diff
--- a/backend/app/evidence/rules.py
+++ b/backend/app/evidence/rules.py
@@ def _row_matches(row, card):
-    if row_volunteer is None and row_task is None:
+    if row_volunteer is None or row_task is None:
         return False
-    if row_volunteer is not None and row_volunteer != _as_id(card.volunteer_id):
+    if row_volunteer != _as_id(card.volunteer_id):
         return False
-    if row_task is not None and row_task != _as_id(card.task_id):
+    if row_task != _as_id(card.task_id):
         return False
-    return row_volunteer is not None
+    return True
```

Keep the remaining alias code only if an explicit import contract needs it; otherwise simplify it in a separate change after regression tests.

## Round 6 — Testing gaps

**Reviewer:** `synth.py:91-128` edits generated people to make most tasks feasible and deliberately leaves named shortage cases. This is transparent development fixture design, but the same fixture underlies the headline evaluation. The tests do cover many constraint invariants, and `tests/solver/test_metrics.py` explicitly tests the current all-assigned robustness definition. They do **not** establish independent generalisation, checked-skill provenance, malformed model count gating, or a real organiser comparison.

**Author (simulated pushback):** The existing suite is substantial and the harness prints misses; independent field data is outside an idea-stage build.

**Reviewer:** Agreed that field impact cannot be required now. A frozen challenge set authored without seeing solver output is feasible as pre-final evidence. Regression tests should assert the intended v2 safety contract rather than only the current v1 implementation. Do not tune the independent set after seeing scores.

**Agreed proposed test diff D6:**

```diff
--- a/backend/tests/solver/test_cp_sat.py
+++ b/backend/tests/solver/test_cp_sat.py
+def test_unchecked_first_aid_leaves_must_slot_open():
+    # Build a task requiring checked first aid and a candidate with only a
+    # self-declared claim; assert no primary or standby assignment fills it.
+    ...
--- a/backend/tests/llm/test_extract_and_draft.py
+++ b/backend/tests/llm/test_extract_and_draft.py
+def test_unknown_required_skill_never_becomes_open_role():
+    # Stub a schema-shaped model response containing an unmapped skill.
+    # Assert extraction blocks roster approval instead of returning [].
+    ...
```

These are test specifications, not runnable additions. Add a must-role-dropout metric test, a cross-task attendance test and an injected file-write failure test alongside them.

## Summary table

| Topic | Rounds | Action items |
|---|---:|---:|
| Correctness | 1 | 3 |
| Error handling | 1 | 2 |
| Performance | 1 | 1 |
| Security | 1 | 2 |
| Maintainability | 1 | 1 |
| Testing gaps | 1 | 2 |
| **Total** | **6** | **11** |

## Agreed changes (proposed diffs)

**D1:** Add checked-skill provenance and server-owned safety classification; block unknown extracted skills. See the D1 diff in Round 1. **D1b:** Derive each card's planned role from the assignment. See D1b. **D2:** Mark missing counts for review, avoid mutating the stored card before append, use atomic card-file replacement and startup consistency checks. See D2. **D3:** Bound standby search by the full roster budget and mark incomplete results. See D3. **D4:** Send roster IDs and roles, not display names, to the model. See D4. **D5:** Require both task and volunteer IDs for attendance attribution. See D5. **D6:** Add the concrete regression cases and freeze independent evaluation cases. See D6. No agreed change was applied in this review.

## Open disagreements

- **Metric definition:** The current all-assigned robustness measure is internally consistent, but the reviewer wants a separate must-role-dropout measure for the hero claim. Preserve the old series under its exact name; decide the new label before recomputing results.
- **Storage architecture:** Atomic JSON replacement plus recovery checks may suffice for a one-user demo. A real multi-user pilot needs a transactional store; the owner has not approved that scope.
- **Legacy row compatibility:** Keep an explicit import adapter only if a real programme export requires it. The current API gives no evidence that the alias engine is needed.

## Action items (11)

1. **High:** Gate safety-critical roles on checked qualification in schema, solver, baselines and metric; test the no-go path.
2. **High:** Stop unknown extracted skills from becoming open roles; require explicit review of missing counts.
3. **High:** Derive a card's planned role from the assignment; record a changed actual role separately for human review.
4. **High:** Recompute and rename the mission-readiness metric so optional-role dropouts cannot inflate the hero result.
5. **High:** Keep the model prompt free of roster display names; document that regex redaction does not clear free-text names.
6. **High:** Stop calling actor-labelled confirmation "verified"; require authenticated authority before any real-data pilot.
7. **Medium:** Make card decisions immutable until append succeeds; atomically replace card JSON and check state on reload.
8. **Medium:** Correct the ledger crash guarantee and handle a journal/sidecar mismatch explicitly.
9. **Medium:** Measure and bound end-to-end standby time before making scale claims.
10. **Medium:** Require task ID in attendance attribution; move messy import parsing to a defined boundary if needed.
11. **Medium:** Freeze independent cases and add regression tests for safety, malformed extraction, attendance attribution and persistence failure.

## Deferred concerns and re-run recommendation

No topic was skipped. Broader API authorisation, concurrent multi-process writes and actual deployment behaviour remain outside this local-demo review. **Re-run after the correctness and error-handling changes**, because their fixes will change the benchmark, schemas and adjacent tests. A subsequent pass should use the newly frozen challenge set and inspect the finished v2 UI states; do not use the existing passing count as closure on these findings.
