# SewaCircle - Architecture Decision Records (ADR)

Format: Context, Decision, Consequences. Status values: Accepted, Conditional, Superseded. Dated 2026-11-18 unless noted.

## ADR-001 Build an idea-stage prototype now; do not assume reuse on build day
**Context.** The AI Kaushal page says no prototype is needed at idea stage and lists a demo video as a valid attachment, but also says "building happens at the in-person hackathon" (8 to 9 Dec). Rules on bringing pre-built code are not stated.
**Decision.** Build a prototype in its own repo, labelled idea-stage, to produce measured results, screenshots and a demo video for the idea round. Plan to rebuild on the day from the spec unless the organisers confirm prepared code is allowed. Ask them in writing.
**Consequences.** Spec, solver design, prompts, eval set and design assets carry over safely; code reuse is a decision for after the organisers answer. The repo states clearly that it is a prototype built before the event.

## ADR-002 Position as a complement to MY Bharat
**Context.** MY Bharat's official pages already cover volunteering, geotagging, credentials and an AI CV builder. We found no organiser-side team formation there (not found, not proof of absence).
**Decision.** Pitch an organiser-side crew planner and evidence workflow that works alongside MY Bharat, DYOs and NSS. Never claim exclusivity.
**Consequences.** Honest and defensible on stage; the novelty risk is stated openly in the PRD and report.

## ADR-003 Hybrid design: LLM for reading, deterministic solver for deciding
**Context.** A plain LLM matcher is easy to build, hard to audit and unfair to reproduce. Government and judges value explainability.
**Decision.** The LLM only converts messy Hindi/English text to schema-validated fields and drafts evidence cards. A CP-SAT solver makes roster decisions. Humans approve.
**Consequences.** Reproducible, explainable assignments; AI is central to input understanding but never the final authority. Solver failures are explicit (unfilled roles), not hallucinated.

## ADR-004 OR-Tools CP-SAT as the solver
**Context.** We need hard constraints plus tiered objectives, standby selection, forced-in/out for counterfactuals, and fast solves on 40 to a few hundred volunteers.
**Decision.** Use OR-Tools CP-SAT (open source, Python, deterministic with a seed, handles the forced re-solves cheaply).
**Consequences.** Scales comfortably past demo size; modelling effort sits with Lane A and is verified by property tests. Alternatives (greedy heuristics, MIP libraries) kept only as baselines.

## ADR-005 Default LLM: Claude Sonnet 5.5 through an OpenAI-compatible gateway; not DeepSeek
**Context.** A same-prompt test on 2026-11-18 (Hindi task brief, JSON-only output) gave: Claude Sonnet 5.5 valid JSON with correct Hindi roles in about 11 s; Gemini 3.8 Flash valid JSON but all counts 0; DeepSeek v4.1 Flash is a reasoning model that consumed 3000 tokens thinking and returned empty content; a GPT route returned 503.
**Decision.** Default to Claude Sonnet 5.5, `max_tokens` >= 3000, `temperature` 0, with a provider interface so the model is configurable (hackathon credits cover Claude, OpenAI and Gemini).
**Consequences.** DeepSeek is used for build workers only. Model choice must be re-tested before the event; the extraction eval is the gate.

## ADR-006 Record/replay LLM cache
**Context.** A live demo must not die on a network or rate-limit failure; tests must not hit the network.
**Decision.** `complete_json` caches by hash of (model, prompts, max_tokens); modes `record`, `live`, `replay`. Unit tests monkeypatch the client.
**Consequences.** Offline demos from cached outputs; the cache is git-ignored because it is derived data.

## ADR-007 Export-first, no external integration
**Context.** No public MY Bharat or UP department API was found; integration needs approval.
**Decision.** The prototype exports CSV/JSON and credential JSON and integrates with nothing.
**Consequences.** Nothing to break during the demo; the path to pilot is documented in the TRD, not claimed as built.

## ADR-008 Host confirmation and a hash-chained ledger
**Context.** Judges score responsible AI in the built product; volunteer-hour fraud is a known problem; AI must not verify.
**Decision.** AI drafts cards; deterministic rules flag; a host confirms, corrects or rejects; every event goes to an append-only hash chain.
**Consequences.** Clear accountability; the chain proves edits, not truth, and the UI says so.

## ADR-009 Synthetic data only
**Context.** Real volunteers and minors would raise consent and DPDP issues.
**Decision.** All volunteers and tasks come from a deterministic generator, labelled "synthetic" in schemas, API and every UI view. Real names are never used.
**Consequences.** Results are proxy measures; we say so everywhere.

## ADR-010 Feature selection rule and the chosen uniques
**Context.** More features are not better; each must map to a judged criterion and be demo-able and testable.
**Decision.** Core plus three uniques: U1 dropout-resilient rosters (technical depth, resilience), U2 rotation fairness and novice-mentor pairing (responsible AI, impact), U3 counterfactual why-not (explainability). U4 Open Badges export is conditional on verifying the spec from primary sources.
**Consequences.** Cap of three extra features; others (voice input, WhatsApp, map view) are stretch goals documented but not promised.

## ADR-011 Delivery process: head + orchestrator + test-gated lanes
**Context.** Seven hours, one prototype, several workers with uneven reliability (an earlier lane skipped its subagents and cited no URLs).
**Decision.** Claude Code is head and owns the contract (schemas, API, LLM client, UI). Codex (gpt-6-luna) is orchestrator/reviewer in short passes. Hermes leads (nilabh/Deepseek-v4.1-Flash, 3 subagents per batch) own lanes with file ownership and tests as gates: A solver and eval, B LLM and evidence, C research. The head runs the tests itself after every batch and does not trust summaries.
**Consequences.** Parallel throughput with guardrails; lane output is accepted only when tests pass and numbers come from real commands.

## ADR-012 Design system: Airtable base with soft tints
**Context.** The product must look trustworthy and calm to government and industry judges and handle Hindi well.
**Decision.** Follow the Airtable design analysis from the local collection (white canvas, near-black ink, hairlines, colour-block over shadow) with Notion-style status tints; self-host Inter and Noto Sans Devanagari. See DESIGN.md.
**Consequences.** Distinctive but sober look; no extra accent colours.

## ADR-013 Frontend: Vite, React, TypeScript
**Context.** Fast iteration, easy Playwright recording for the demo video, static build served by FastAPI for a one-command demo.
**Decision.** Vite + React + TypeScript with typed API client generated by hand from the pydantic schemas.
**Consequences.** Small dependency surface; a single `npm run build` artefact.

## ADR-014 Credential export is unsigned and says so
**Context.** Only a recognised issuer can issue credentials; we are not one.
**Decision.** Emit an unsigned Open Badges 3.0 / W3C VC compatible JSON (only if the fields are verified) with an explicit "unsigned, not issued by any authority" notice.
**Consequences.** No false authority claim; shows a path to interoperability.
