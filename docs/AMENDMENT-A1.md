## HEAD AMENDMENT A1 (2026-11-18, from the Codex contract review, docs/CONTRACT_REVIEW.md) - MANDATORY, supersedes your card where they conflict

schemas.py has changed (additive): READ backend/app/schemas.py again, especially the RosterMetrics docstring (the exact metric definitions), SlotRef, AttendanceRow, and the new validators. Re-run the whole suite after adapting.

BOTH LANES
1. Slots: task.slot and volunteer.available_slots must be members of taxonomy.SLOTS (validators now reject others).
2. IDs: volunteers v-001.., tasks task-01.., roles role-01.. (role ids are assigned during extraction conversion and preserved). Skills are validated against the taxonomy; an empty required_skills list means open to any volunteer.

LANE A (solver, data, eval)
3. metrics.py must implement the RosterMetrics docstring EXACTLY: role_coverage over MUST slots only (should_coverage separately); robustness = share of single-dropout scenarios where a maximum matching from (assigned minus that volunteer) plus the roster's UNIQUE standby pool covers every must slot (each person once; qualification, availability, travel, consent re-checked); repeat_pick_share = assigned with times_picked_last_90d >= 3 / assigned; exposure_gini over the task-ELIGIBLE candidate pool with +1 for selected people. Re-check what you already wrote and fix any difference; keep ONE shared function for all methods.
4. RosterResult must fill unfilled_slots (list of SlotRef) as well as unfilled_role_ids; assignments are unique per (role_id, slot_index).
5. Objective priority must be enforceable: solve in sequential tiers (maximise must coverage first, add it as a constraint, then skill fit, then proximity, then fairness, then resilience) or use integer weights with a proven bound; add an adversarial test where every secondary preference conflicts with one must slot and the must slot still wins.
6. nearest_skill = the nearest ELIGIBLE qualified candidate under the same hard constraints as cp_sat (availability, travel, minor consent, qualification). The property cp_sat coverage >= nearest_skill coverage is asserted only when solver_status is OPTIMAL.
7. Eval: random_feasible averaged over 20 declared seeds; bootstrap resamples TASK ids, paired across methods (same resampled tasks for every method); report paired deltas, raw per-task rows and the misses; record generator seed, solver version and settings in EvalReport.generated_by.

LANE B (LLM, evidence)
8. Attendance is typed: schemas.AttendanceRow (hours = RECORDED hours from the attendance sheet, never the volunteer's claim; optional check_in/check_out ISO-8601; optional age and guardian_consent). Signatures become check_card(card, all_cards, attendance_rows: list[AttendanceRow]) and draft_cards(task, host_notes, attendance_rows: list[AttendanceRow], assignments: list[Assignment]). Update your modules and tests. minor_without_guardian_consent uses AttendanceRow.age/guardian_consent.
9. Card ids are deterministic: card-{task_id}-{volunteer_id}-{role_slug}; one card per volunteer/task/role; draft for assigned volunteers plus any volunteer explicitly mentioned in the notes.
10. Ledger threat model: the claims are limited to detecting edits, reordering and interior deletion; tail truncation is detectable only against a separately kept head hash. Add Ledger.head_hash() and verify(trusted_head: str | None = None) and say so in the docstring. Appends must be crash-safe (flush+fsync) and thread-safe.
11. LLM failures raise llm.client.LLMError; unit tests monkeypatch the client; no network in tests.
