# Product requirements — SewaCircle Mission Assurance

Status: proposed v2, 19 Nov 2026. **UC16 only.** This document specifies a 24-hour demonstrable slice and a separate path to an authorised pilot. All demo people, attendance and activities are synthetic; no government affiliation or integration is implied. The [event's UC16 and judging rubric](https://www.inmobi.com/ai-kaushal) are the governing product brief. `CONCEPT-v2.md` gives the choice rationale.

## 1. Problem, promise and boundaries

A district organiser must translate an informal task into complementary roles, choose willing and qualified people, survive absence, then record what each person did. **INFERENCE:** the scarce decision is whether the crew is *mission-ready*, not whether another volunteer listing exists. Public MY Bharat descriptions already cover discovery, attendance, credentials, impact tracking and dashboards; the exact organiser-side preflight remains **NOT FOUND** in reviewed public material ([MY Bharat](https://mybharat.gov.in/about_mybharat), [PIB](https://www.pib.gov.in/FactsheetDetails.aspx?Id=150695&lang=10&reg=23)). NSS's [manual](https://nss.gov.in/assets/admin/uploads/homepage/manualNss2006.pdf) already tells officers to group by aptitude and skill; the proposed improvement is a reproducible stress test and explicit shortage reason, not the idea of balanced teams.

**Promise for demo:** given one task and 20 opt-in synthetic adult profiles, an organiser can approve roles, inspect a qualified crew, remove one person, see the consequent safe plan or shortage, and close one conflicting contribution claim with a documented human decision. No match, recorded hour, hash or badge is represented as proof of real-world impact.

## 2. Actors and authority

| Actor | Can do in demo | Pilot authority still needed |
|---|---|---|
| Organiser | Edit task roles, approve/reject roster, request dropout preflight, export mission record. | Authenticated role, permission to process programme volunteers. |
| Volunteer | Appears as a synthetic, opt-in adult profile; sees a printable contribution record only. | Consent, corrections/appeal, access and deletion workflow. |
| Host | Reviews one draft card and corrects or rejects an hours discrepancy. | Identity verification and separation from volunteer self-attestation. |
| Department reader | Sees synthetic unmet-role and provenance summary. | Data-sharing approval, decision owner, aggregation/small-cell policy. |

## 3. Functional requirements and acceptance

| ID | Requirement | Acceptance in the 24-hour MVP |
|---|---|---|
| R1 | Accept a Hindi or English text task; LLM proposes role names, counts, skill mapping, evidence spans, confidence and unanswered questions. | Schema validation; unsupported skill and missing count become “needs review”; organiser must confirm or manually enter roles before solve. An unseen task is run once live if model access works. |
| R2 | Use only opt-in adult profiles with skills, qualification provenance, coarse location, availability and recent assignment count. | All demo profiles labelled synthetic; no actual minor, phone or ID in requests. Safety-critical skills need a `checked` evidence flag; otherwise the must role stays unfilled. |
| R3 | Build the roster with must-slot coverage first, then dropout resilience, then rotation preference. | Exactly one person per slot/person, eligibility rechecked, no hard-rule break, `unfilled_slots` and solver status visible. If the solver times out or no valid person exists, show a safe partial/no-crew state. |
| R4 | Explain each assignment and exclusion from the same data used by the solver. | Reason includes role, accepted skill/level, availability, area/distance, qualification provenance, and rotation impact; “why not X?” uses a re-solve or names the blocking hard rule. No LLM-invented reasons. |
| R5 | Simulate each primary volunteer's absence, with a unique standby pool. | One-click demo for one absence; show before/after slot coverage and exact replacement or remaining vacancy. Robustness denominator is assigned-volunteer scenarios; no unlimited per-role backup reuse. |
| R6 | Close a mission record from host note and attendance. | LLM summary is explicitly a draft; deterministic rules flag claimed > recorded hours, duplicate reference and missing attendance; a host-labelled reviewer corrects/rejects. Export records claim, attendance, status, review time and source type. No “verified credential.” |
| R7 | Compare methods on identical inputs. | Display role coverage, dropout robustness, repeat-pick share, runtime and all misses against nearest-skill **and backup-aware manual-greedy**; benchmark label says synthetic, n, seed and fixture version. No “impact gain” from proxy metrics. |
| R8 | Provide visible failure and correction paths. | Manual role entry on LLM error; infeasible role shown; organiser can edit roles and recompute; rejected card never appears as confirmed. These paths are rehearsed in the demo. |
| R9 | Export one mission packet. | CSV/JSON contains task/role IDs, assignments, shortages, dropout case, host decision and `synthetic: true`; no personal identifiers beyond invented fixture IDs. No claim of MY Bharat compatibility without an agreed schema. |

## 4. Journey and interface states

1. **Task:** prefilled but editable synthetic Hindi task; visible synthetic and model/replay labels. A separate unseen text field tests live extraction.
2. **Role review:** text span next to proposed role; uncertainty requires a click to accept/edit. Missing essential role stops roster approval.
3. **Mission preflight:** coverage numerator/denominator, qualified primary and standby, reasons, red unmet-slot panel. Explicit approve button; no automatic mobilisation or messages.
4. **Break it:** remove one selected person. Show exactly which reassignment happened or why mission is not ready. Restore button returns the original roster.
5. **Closeout:** synthetic host note and attendance show a conflicting hours claim. Host-labelled correction creates a review record. Export discloses that actor identity is not authenticated.

## 5. Data, AI and safeguards

Flow: task text → bounded PII redaction/validation → model extraction → organiser edits → typed `TaskSpec` → CP-SAT → roster and counterfactual → synthetic host note/attendance → model draft → deterministic discrepancy rules → human decision → local export. Cache/replay must visibly identify itself. If model output is malformed, reject it rather than guessing. The LLM does **not** certify skill, choose a person or verify work.

Demo storage is local and disposable; no real-person data, photographs, government identifiers, credentials or unconsented audio. A pilot needs purpose/consent records, access controls, retention and deletion, incident handling, appeal/correction, model-provider/data-transfer review and legal assessment under the [DPDP Act](https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf?v=20260911235451) and [Rules](https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf?v=20261110123627). The current regex redactor does not reliably identify names; therefore real notes never go to the model in this MVP. Keep under-18 data out of the demo entirely. Prohibit protected traits in ranking; audit selection among *eligible* candidates, with small cells suppressed/marked insufficient. A host-labelled click is an unverified attestation until authentication is added.

## 6. Evaluation and release gates

**Current measured fixture:** 10 author-generated tasks/80 synthetic people, seed 7, OR-Tools 9.15.6755. The 19 Nov rerun of `..\.venv\Scripts\python.exe -m eval.harness` from `backend/` matched `../EVAL_RESULTS.md`: coverage CP-SAT/nearest/manual = **0.917/0.917/0.917**; robustness = **0.760/0.153/0.760**; repeat-pick share CP-SAT/manual = **0.230/0.427**; six misses. This is development evidence only. The extraction 30/30 result is from author-written briefs and cache (reported median 0 s), not prospective accuracy.

**Pre-final test protocol:** freeze 20–30 *independently written* task cases before scoring; include implicit counts, negation, Roman Hinglish, dialect wording, missing safety qualification and scarce backups. Preserve all failures. Run identical cases through (a) current solver, (b) nearest eligible, (c) backup-aware manual heuristic; have an organiser time a realistic manual roster on a subset **only if one agrees**. Report role-slot accuracy, infeasible detection, dropout survival, abstentions, latency and reviewer correction count with denominators. If independent cases or organiser timing do not materialise, mark **NOT MEASURED**, show existing fixture with its caveats and make no time-saved claim.

**Demo gate:** a fresh local run completes task → reviewed roles → crew → dropout → closeout → export within three minutes, plus one prepared offline replay route and manual-error path. On-stage numbers must be the rerun's printed numbers; no changed fixture after viewing results. Tests cover hard eligibility, empty/partial rosters, unique standby, card state changes and export provenance. A bug that assigns an unchecked first-aid volunteer or silently confirms an hours claim blocks the demo.

## 7. Scope cuts and deployment path

**MVP excludes:** new discovery marketplace, WhatsApp, voice, OCR/photos, real minors, automatic credentials, real MY Bharat/NSS/NYKS API access, district prevalence estimates, outcome attribution and live communications. A future pilot would need a willing programme owner, authorised opt-in data export/API terms, authenticated hosts, verified skill evidence, privacy review, hosting, service-cost estimate and an agreed integration contract. [MY Bharat API terms](https://mybharat.gov.in/pages/terms_of_use) describe a required undertaking for API use; access is **NOT VERIFIED**. A local CSV is a proposal for exchange, not an approved government adapter.
