# SewaCircle

**Fair Crew Planner for youth volunteering** - an idea-stage prototype for the AI Kaushal Hackathon 2026 (use case UC16: AI Youth Volunteer and Community Project Matcher).

> **Honest notice.** This is a prototype built before the event. **All data is synthetic.** It is **not affiliated** with InMobi, the Government of Uttar Pradesh, MY Bharat or IIIT Lucknow, and it does not integrate with any government system. Numbers shown are proxy measures on synthetic data, not field impact.

## The idea
Platforms already help young people find volunteering opportunities. A district organiser still has to turn a pool of willing people into a role-complete, fair, safe team for one task, handle dropouts, and afterwards document who actually did what. SewaCircle helps with that step and is designed to complement existing platforms such as MY Bharat.

**AI reads messy text; a deterministic solver decides; a human approves; nothing is called verified without a host.**

## What it does
1. **Role extraction** from a Hindi/English task brief (PII redacted before any model call).
2. **Roster planner** (OR-Tools CP-SAT): role coverage, availability, travel, minor-consent rules, with a plain-English reason per pick, compared live against a nearest-skill baseline.
3. **Dropout-resilient rosters**: standby chosen so any single dropout still leaves every role covered; "drop a volunteer" heals live.
4. **Rotation fairness** and novice-mentor pairing so the same few people are not picked every time.
5. **Why not X?** counterfactual explanations from real re-solves.
6. **Evidence ledger**: AI drafts contribution cards from host notes, deterministic rules flag anomalies, a host confirms, and a hash-chained log records every step (it shows edits, not truth).
7. **Evaluation harness** that reports every method over 10 labelled tasks with confidence intervals and a list of misses.

## Documents
[PRD](PRD.md) · [TRD](TRD.md) · [ADR](ADR.md) · [PLAN](PLAN.md) · [DESIGN](DESIGN.md) · [CONTEXT](CONTEXT.md) · [Project report](PROJECT_REPORT.md)

## Run
See `CONTEXT.md` ("Run"). Tests need no network; `SEWA_LLM_MODE=replay` runs the app from cached model outputs.

## Status
Work in progress; see [PROJECT_REPORT.md](PROJECT_REPORT.md) for what is built and verified, with real command output. Licence: MIT.
