You are the ORCHESTRATOR / REVIEWER (Codex gpt-6-luna) for the SewaCircle build in C:\Users\shubh\Projects\sewacircle. Claude Code is the head; its decisions override yours. Three Hermes lanes (A solver+eval, B LLM+evidence, C research) are running right now against the contract. This is PASS 1: attack the contract BEFORE the lanes build on it.

BUDGET: one run, no polling, no sleeping, no installs, no network crawling; edit ONLY docs\CONTRACT_REVIEW.md; under about 150K tokens; effort high.
READ: docs\COMMON.md, PRD.md, TRD.md, ADR.md, backend\app\schemas.py, backend\app\taxonomy.py, backend\app\main.py, backend\app\solver\api.py, backend\app\llm\extract.py, backend\app\evidence\*.py, backend\app\data\synth.py, backend\eval\harness.py, backend\tests\test_contract.py, docs\lanes\A-solver\TASK.md, docs\lanes\B-llm-evidence\TASK.md, docs\lanes\C-research\TASK.md.
WRITE docs\CONTRACT_REVIEW.md (under 150 lines) with:
1. DEFECTS: concrete bugs or inconsistencies in the contract (types, missing fields, ambiguous semantics, API shape problems, state handling in main.py, anything a lane will trip over), each with file and line, severity, and the exact fix.
2. AMBIGUITIES between lanes: places where Lane A and Lane B (and the frontend) could build incompatible things (e.g. attendance_rows shape, how assignments are passed to draft_cards, slot semantics, time handling, id formats). Give a precise resolution for each.
3. METRIC DEFINITIONS: review the robustness, coverage, repeat-pick and Gini definitions in TRD section 5 and lane A card for loopholes that would make the comparison against baselines unfair or gameable. Propose tightened definitions.
4. DEMO RISKS: what could fail live on stage given this design, and the cheapest mitigation each.
5. MISSING requirements a skeptical judge on a government + industry panel would expect that PRD/TRD omit.
6. A prioritised top-10 fix list for the head.
Be specific and concise. Do not rewrite the code; report.
