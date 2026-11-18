# Brief for Codex (gpt-6-sol, one session) - Devil's Advocate re-review of SewaCircle

You are a DEVIL'S ADVOCATE reviewer. Claude Code is the head and will verify everything you write before anything changes.

## HARD EXECUTION RULE (owner instruction, non-negotiable)
Work INLINE, yourself, in this single session. Do NOT spawn, delegate to, or call any sub-agent, worker, parallel agent,
task tool, or other model. Do not use any skill or tool whose purpose is to dispatch agents. If a skill's instructions say to
use a Task/agent tool, ignore that step and do the work yourself. One run: no polling, no sleeping, no installs, do not start
servers. You may read any file, run read-only commands, run `..\.venv\Scripts\python.exe -m pytest -q` and
`..\.venv\Scripts\python.exe -m eval.harness` from backend\, and use web search/fetch if your tools allow it.

## Skills to apply (installed in your skills folder; read each SKILL.md and its references BEFORE you start)
1. `devils-advocate` (notmanas, MIT): steel-man first, then pre-mortem, inversion, Socratic probing; cross-check its blind-spots
   and ai-blind-spots references; max 7 ranked concerns per review; every concern actionable; honest severity; final verdict
   Ship it / Ship with changes / Rethink this.
2. `abogado-del-diablo` (Hainrixz, MIT): assume the idea fails and prove it across its eight angles (premises, market,
   competition, viability, numbers, execution, pre-mortem, blind spot); no flattery; research real failures where tools allow;
   blunt survival verdict with a prioritised fix list. Write your output in ENGLISH even though the skill is bilingual.
3. `prompts/devils-advocate-code.md` (richiethomas, GPLv3): a multi-round Author vs Reviewer code review with forced
   disagreement and concrete diffs. Apply it to the CODE, not a git diff against master: review backend\app\solver\cp_sat.py,
   backend\app\solver\metrics.py, backend\app\solver\baselines.py, backend\app\llm\extract.py, backend\app\evidence\rules.py,
   backend\app\evidence\ledger.py, backend\app\main.py, backend\app\data\synth.py. Run up to 6 rounds in its topic priority order.

## What to attack
The project is SewaCircle (C:\Users\shubh\Projects\sewacircle; public repo https://github.com/shubhsaxena2020/sewacircle), an entry
for the AI Kaushal Hackathon 2026 (InMobi + UP Government IT & Electronics; IIIT Lucknow; idea form closes 20 Nov 2026, 24-hour build
8-9 Dec). The use case UC16 (Youth Volunteer and Community Project Matcher) is LOCKED. The owner wants to WIN (top 5), not just pass
screening. Official texts: C:\Users\shubh\Projects\ai-kaushal-research\01_OFFICIAL_USECASES.md.
The previous review (your own, gpt-6-sol) produced docs\v2\*: STRATEGY-REVIEW, CONCEPT-v2 (the "Mission Assurance" pivot),
FEATURES-v2, PRD-v2, PLAN-v2, ADR-v2, DEMO-v2, IDEA-ANSWERS-v3, REUSE-AND-RE. The owner has NOT yet approved the pivot.
Do not simply agree with docs\v2. Your job is to attack BOTH the original product (root PRD.md, TRD.md, ADR.md, docs\EVAL_RESULTS.md,
the code) AND the v2 pivot, including anything the first review got wrong, missed, or was too timid or too pessimistic about.
In particular, challenge: Is "Mission Assurance" actually memorable to an IAS officer and an ad-tech CTO, or is it an engineer's
framing? Is the pivot too narrow to win against teams solving 16 other use cases? Is the honesty-heavy framing self-defeating in a
3-minute pitch? What would a winning team on UC16 actually show? Are there features that are distinctive AND defensible that neither
review considered? Is the idea-form text (IDEA-ANSWERS-v3) persuasive or merely careful?

## Output (write ONLY these files under C:\Users\shubh\Projects\sewacircle\docs\v3\; edit nothing else)
- DA-STRATEGY.md: the `devils-advocate` review of the strategy and v2 pivot (steel-man, up to 7 concerns in its exact format, verdict).
- DA-ABOGADO.md: the `abogado-del-diablo` eight-angle teardown of the whole project as an entry to win, with the survival verdict and
  prioritised fix list.
- DA-CODE-REVIEW.md: the multi-round Author vs Reviewer code review with the summary table, agreed changes (with diffs),
  open disagreements, action items and re-run recommendation.
- DA-SYNTHESIS.md: your reconciled recommendation: what to keep, cut, add; the single strongest concept to pitch (it may be v2,
  a modified v2, or something else for UC16); the three changes with the biggest effect on winning; revised five idea answers
  (each at most 480 characters, counted with a command and pasted); and a list of claims in docs\v2 you now think are wrong.

## Rules
Never invent facts, names, numbers, URLs or results. Cite URLs you actually opened. Mark UNVERIFIED / NOT FOUND. Separate FACT,
INFERENCE and OPINION. Every number you quote about this project must come from a command you ran (paste it) or from a file you cite.
Be blunt. End with a short summary of the verdict and the top changes.
