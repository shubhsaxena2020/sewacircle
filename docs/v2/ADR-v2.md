# Architecture decisions — v2 continuation

Proposed 19 Nov 2026. These extend `../../ADR.md` from ADR-015; they do not silently rewrite v1. **FACT** identifies checked code or an opened source; consequences and decisions are design judgments.

## ADR-015 — Position as mission assurance, not another platform

**Context (FACT):** [MY Bharat](https://www.pib.gov.in/FactsheetDetails.aspx?Id=150695&lang=10&reg=23) already says it manages registration, attendance, geotagging, certificates and impact tracking; [NSS manual](https://nss.gov.in/assets/admin/uploads/homepage/manualNss2006.pdf) describes grouping by aptitude/skill. **Decision:** one organiser task → crew stress test → reviewed closeout. **Consequence:** discovery, badges and department dashboard become context/stretch, and “first to form teams” is forbidden copy.

## ADR-016 — Human-reviewed LLM extraction is the AI boundary

**Context:** field briefs are messy, but an incorrect role/count can create unsafe assignments. **Decision:** model outputs typed role proposals with source spans and uncertainties; organiser confirms. LLM never decides qualifications, roster or truth of hours. **Consequence:** central AI value is measured by independently authored challenge cases and abstention, not a chat panel.

## ADR-017 — Safety gates precede optimisation

**Context:** a self-declared first-aid tag can pass today's skill predicate. **Decision:** any safety-critical role requires checked qualification provenance in v2; otherwise mark slot unfilled. Adult-only synthetic profiles for the event. **Consequence:** lower coverage is acceptable; no “full crew” by relaxing safety.

## ADR-018 — Counterfactual readiness is the hero metric

**Context (FACT):** current synthetic results tie coverage with two baselines and dropout robustness with careful manual-greedy (`../EVAL_RESULTS.md`). **Decision:** show coverage plus single-dropout survival, shortages and all misses; always include backup-aware manual. **Consequence:** no unsupported superiority claim; independent hard-case evaluation is a pre-final gate.

## ADR-019 — Evidence is reviewed provenance, not a certificate

**Context:** [MY Bharat](https://mybharat.gov.in/about_mybharat) issues digital credentials; [Open Badges 3.0](https://standards.1edtech.org/open-badges/specifications/standards/v3p0) makes cryptographic issuer verification distinct from truth of the claim. **Decision:** export a plain, unsigned mission record with source, claim, attendance and host-labelled decision. **Consequence:** retire “verified contribution” and “passport” from the MVP; a future recognised issuer must assess and sign any credential.

## ADR-020 — Respect source terms; use licensed components

**Context (FACT):** [MY Bharat terms](https://mybharat.gov.in/pages/terms_of_use) forbid reverse engineering, automated retrieval and mirroring; the event page does not settle prepared-code reuse. **Decision:** compare permitted public documentation manually; never clone or decompile a government portal; use declared OSS dependencies with notices. Ask organisers in writing whether pre-event SewaCircle code and data may be brought into the build. **Consequence:** have both reuse-permitted and from-scratch 24-hour plans; no unattributed template or competitor UI.

## ADR-021 — Synthetic benchmark is development evidence only

**Context:** fixture scarcity/feasibility is authored by the team and 30 extraction briefs are easy. **Decision:** retain the reproducible harness, freeze independent challenge cases before scoring and publish failures, denominators and model/cache provenance. **Consequence:** no field effectiveness or time-saved figure until observed; a failed independent test triggers scope/pitch revision.

## ADR-022 — Kaggle is a pre-event evaluation tool

**Context:** [Kaggle GPU guidance](https://www.kaggle.com/docs/efficient-gpu-usage) says GPU helps deep-learning workloads, not ordinary Python/OR-Tools; the user has a 30 h/week quota. **Decision:** use CPU notebooks only for optional scale/stress sweeps and dataset review; GPU only if voice becomes a justified stretch with licensed, consent-safe audio and measured WER. **Consequence:** the live demo never depends on Kaggle, a fine-tune or quota availability.
