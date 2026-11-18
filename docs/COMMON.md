# SEWACIRCLE BUILD - COMMON BRIEF (read first)

Date 2026-11-18 night. Deadline for 90% done: 2026-11-19 06:00 IST. Priority order: QUALITY first, then speed. Head = Claude Code. Orchestrator = Codex gpt-6-luna (discrete passes). Workers = Hermes leads on nilabh/Deepseek-v4.1-Flash, each running exactly 3 parallel subagents per batch.

## What we are building
SewaCircle: an organiser-side "Fair Crew Planner" for youth volunteering, for the AI Kaushal 2026 hackathon, use case UC16 (AI Youth Volunteer and Community Project Matcher, Dept of Youth Affairs and Sports, UP). It is an IDEA-STAGE PROTOTYPE built now to strengthen the idea submission (demo video, screenshots, measured numbers). Repo: C:\Users\shubh\Projects\sewacircle. Official use-case text: C:\Users\shubh\Projects\ai-kaushal-research\01_OFFICIAL_USECASES.md. Submitted concept: C:\Users\shubh\Projects\ai-kaushal-research\submission\answers_v2.py and submission\assets\onepager.html.

Flow: organiser enters a task (Hindi/English) -> AI extracts roles/skills -> constraint solver (OR-Tools CP-SAT) builds a role-covered, fair, safe roster with a reason per pick -> organiser edits/approves -> after the event, AI drafts contribution cards from host notes, rules flag anomalies, a host confirms -> hash-chained ledger and portable record export.
Build-day judging the product must win on: working end-to-end solution; technical execution and architecture; innovation and differentiation; outcome vs today's baseline (measured); scalability and path to production; responsible AI BUILT IN.

## Features (core + chosen unique features)
CORE: role extraction (LLM, schema-validated, Hindi/English); CP-SAT roster; nearest-skill baseline; evidence cards + rule flags + host confirmation + hash-chained ledger; eval harness (10 labelled tasks, 20+ labelled synthetic volunteers) reporting role coverage, roster time, repeat-pick spread vs baselines with misses shown.
UNIQUE: (U1) dropout-resilient roster: standby assignment so any single dropout still leaves every role covered; robustness score; live "drop a volunteer, roster heals". (U2) rotation fairness: exposure-aware selection so the same few volunteers are not picked every time, new-volunteer opportunity, novice-mentor pairing; district spread. (U3) counterfactual explanations: "why not volunteer X?" answered by re-solving with X forced and reporting what changes. (U4, only if verified from the primary spec) portable skill passport export in an Open Badges 3.0 / W3C Verifiable Credential compatible JSON.

## Integrity rules (violations get output rejected)
1. NEVER invent facts, names, numbers, URLs, citations, benchmark results or quotes. Every non-trivial research claim needs a source URL you actually opened, in the file. UNVERIFIED and NOT FOUND are valid answers. Separate FACT / INFERENCE / OPINION.
2. All volunteer/task data is SYNTHETIC and must be labelled so everywhere it is shown. No real people, no real minors.
3. Never state a number in any report that a command did not print; paste the command and output.
4. Write only files your lane owns (your TASK.md says which). Never pip install or npm install: the shared environment is C:\Users\shubh\Projects\sewacircle\.venv (python.exe there) and is pre-built. Never edit files owned by another lane. Save each subagent report to disk immediately.
5. No double quote characters inside prompt files for the runner (PowerShell 5.1).
6. Models: the app LLM layer uses Claude Sonnet 5.5 via 9Router (default). DeepSeek via Nilabh is a REASONING model that returns empty content when max_tokens is low, so it is for the Hermes workers only.
