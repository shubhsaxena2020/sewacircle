# CONTEXT.md - read this first (for humans and AI agents)

## What this is
SewaCircle is an **idea-stage prototype** for the AI Kaushal Hackathon 2026 (InMobi with the UP Government's IT and Electronics Department, venue IIIT Lucknow, build days 8-9 Dec 2026), use case **UC16: AI Youth Volunteer and Community Project Matcher**. It helps a district youth organiser turn a task description (Hindi/English) into a role-complete, fair, dropout-resilient volunteer roster with a reason per pick, then turns host notes into reviewable contribution records with a tamper-evident log. It complements existing platforms such as MY Bharat; it does not replace or integrate with them. This repository is not affiliated with InMobi, the UP Government, MY Bharat or IIIT Lucknow. **All data is synthetic.**

## Read in this order
`PRD.md` (what and why) -> `TRD.md` (how) -> `ADR.md` (why we chose) -> `DESIGN.md` (UI rules) -> `PLAN.md` (schedule and lanes) -> `PROJECT_REPORT.md` (status and real results) -> `docs/research/INDEX.md` (research decisions).

## Repo map
`backend/app/schemas.py` is **the contract**; `taxonomy.py` the 24 skills; `main.py` the API. `backend/app/solver` (OR-Tools CP-SAT, baselines, metrics), `llm` (client, extraction, redaction), `evidence` (rules, ledger, credential export), `data` (synthetic generator). `backend/eval` (roster eval, extraction eval). `frontend/` (Vite + React + TypeScript). `docs/` (research, lane cards, QA). `ops/` (runner prompts used to build with a multi-agent fleet).

## Run
```
python -m venv .venv ; .venv\Scripts\python -m pip install -r backend/requirements.txt
cd backend ; ..\.venv\Scripts\python -m pytest -q          # tests (no network)
..\.venv\Scripts\python -m uvicorn app.main:app --port 8000  # API (set SEWA_LLM_MODE=replay to run offline)
..\.venv\Scripts\python -m eval.harness --out eval_report.json   # roster evaluation
```
LLM settings via environment: `SEWA_LLM_BASE_URL` (OpenAI-compatible, default `http://127.0.0.1:20128/v1`), `SEWA_LLM_API_KEY`, `SEWA_LLM_MODEL` (default `cc/claude-sonnet-5-5`), `SEWA_LLM_MODE` (`record`/`live`/`replay`).

## Rules everyone follows
1. **Never invent** facts, numbers, URLs, benchmark results. A number appears in a document only if a command printed it. Mark UNVERIFIED / NOT FOUND honestly.
2. **Synthetic data only**; label it everywhere; no real people or minors.
3. **AI drafts, deterministic code decides, a human confirms.** Never auto-verify or auto-reject.
4. File ownership per lane (see `docs/lanes/*/TASK.md`); only the head edits `schemas.py`, `taxonomy.py`, `main.py`, `llm/client.py`.
5. Tests must not call the network; live LLM runs go through `llm/client.py` with the cache.

## Gotchas learned
- The gateway needs `"stream": false`; Claude responses need `max_tokens` >= 3000 or JSON truncates. DeepSeek via Nilabh is a reasoning model and returns empty content at low `max_tokens`; do not use it for structured output.
- Runner prompt files must not contain double-quote characters (PowerShell 5.1 argument splitting).
- Pass UTF-8 explicitly on Windows (`python -X utf8`); console code page breaks Hindi output otherwise.
- A hash chain shows edits, not truth; say so wherever the ledger is shown.
- The event's rule about reusing pre-built code is unconfirmed (ADR-001).

## Glossary
UC16: the use case. DYO: District Youth Office. NSS: National Service Scheme. NYKS: Nehru Yuva Kendra Sangathan. MY Bharat: Mera Yuva Bharat, the national youth platform. DPDP: Digital Personal Data Protection Act 2023 and Rules 2025. CP-SAT: OR-Tools constraint-programming solver. U1/U2/U3/U4: the chosen unique features (see PRD).

## Current state
See `PROJECT_REPORT.md` (updated at each checkpoint) and the `PROGRESS.md` file in each `docs/lanes/*` folder.
