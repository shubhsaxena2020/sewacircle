# SewaCircle - Product Requirements Document (PRD)

Status: v1, 2026-11-18. Owner: Shubh Saxena (team lead). Stage: **idea-stage prototype** for the AI Kaushal Hackathon 2026, use case UC16 (AI Youth Volunteer and Community Project Matcher, Department of Youth Affairs and Sports, Uttar Pradesh). Not affiliated with InMobi, the UP Government, MY Bharat or IIIT Lucknow.

## 1. Problem
Platforms already help young people discover volunteering opportunities (MY Bharat, NSS and NYKS channels, NGO portals). What a district organiser still does by hand is the next step: turn a pool of willing people into a **role-complete, fair, safe team for one specific task**, then afterwards document who actually did what. Typical failures: two first-aiders and no logistics person; the same few volunteers picked every time; one dropout collapses a role; contribution records depend on memory and paper; claimed hours are hard to check.
UC16's official text asks for matching, balanced teams "with complementary abilities", tracking and verifying contributions, and a record of each volunteer's experience.

## 2. Positioning (honest)
SewaCircle is an **organiser-side module that complements existing platforms**, not a replacement. In our review of MY Bharat's official pages (about page and PIB releases, opened 2026-11-18) we found volunteering, geotagging, digital credentials, an AI CV builder, experiential programmes and 780 District Youth Offices, and **no organiser-side team formation or role allocation**. That is "not found in the pages we read", not proof of absence; the pitch never claims exclusivity.

## 3. Users
| Persona | Needs |
|---|---|
| District / block youth organiser (DYO staff, NSS programme officer, NGO coordinator) | Build a balanced crew quickly, explain choices to stakeholders, handle dropouts, record contributions fairly. |
| Volunteer (synthetic in the prototype) | Be considered fairly, get a record of real contributions, privacy (especially minors). |
| Host / supervisor on site | Confirm who actually did what, simply. |
| Department official (reader of outputs) | Trust the process, see aggregate fairness and coverage, export records. |

## 4. Goals and non-goals
Goals: (1) a working end-to-end prototype with measured gains against honest baselines; (2) AI used where it is strong (reading messy Hindi/English text) and deterministic logic used where decisions need to be reproducible; (3) responsible AI built into the product; (4) reproducible evaluation anyone can re-run with one command.
Non-goals: a volunteer marketplace or social network; certificates issued by any authority; live integration with MY Bharat or any government system; handling of real personal data or real minors; a claim of field impact.

## 5. Features and acceptance criteria
| ID | Feature | Acceptance |
|---|---|---|
| F1 | **Role extraction**: Hindi/English/Hinglish task brief -> roles, counts, required skills (24-skill taxonomy), evidence span, confidence, "needs your decision" list. PII redacted before any model call. | Schema-valid JSON on every call; unknown skills dropped and noted; low-confidence roles surfaced; measured role recall/precision on 30 labelled briefs reported with failures. |
| F2 | **Roster planner (CP-SAT)**: fills roles under availability, skills, travel limit, minor-consent rules; plain-English reason per assignment. | No hard-constraint violation over 200 random instances; every unfilled role reported; solve under 10 s. |
| F3 | **Baselines + comparison**: nearest-skill, random-feasible, manual-greedy (with one backup per role). | One shared metric function for all methods; comparison shown live in the UI. |
| F4 | **Evidence ledger**: AI drafts contribution cards from host notes; >= 9 deterministic rules flag anomalies; host confirms/corrects/rejects; hash-chained audit log. | Nothing is ever auto-confirmed or auto-rejected; tamper test detects any edited, deleted or reordered entry. |
| F5 | **Evaluation harness**: all methods over 10 labelled tasks with 95% bootstrap CIs and an honest misses list. | One command reproduces the report; numbers in docs come from that output only. |
| U1 | **Dropout-resilient roster**: standby choice so any single dropout still leaves every must-role covered; "Drop a volunteer" heals live. | Robustness metric computed identically for every method; heal shown with real solver output. |
| U2 | **Rotation fairness + novice-mentor pairing**: penalise heavy recent picks, give newcomers chances, pair novices with experienced volunteers on roles that need it. | Repeat-pick share and exposure Gini reported against baselines. |
| U3 | **Counterfactual "why not X?"**: re-solve with X forced in; narrate the real deltas and who is displaced. | Narrative generated from solver deltas, not templates; infeasible cases explain the blocking constraint. |
| U4 (conditional) | **Skill passport export**: unsigned Open Badges 3.0 / W3C VC compatible JSON for confirmed cards, only if the spec fields are verified from primary sources. | Clearly labelled unsigned and not issued by any authority. |

## 6. Responsible-AI requirements (built, not described)
AI never selects alone and never verifies hours. Protected traits (gender, caste, religion) are never used to rank; a fairness panel reports aggregate effects. PII redaction before model calls (names are not detected; this limit is stated). Minors appear only with guardian consent in the data and the solver rejects them otherwise. Every edit is logged. Failure of the LLM degrades to manual entry. All data is labelled synthetic. Errors and abstentions are shown, not hidden.

## 7. Success metrics (prototype)
Measured on 10 labelled synthetic tasks, reported with 95% CIs and misses: role coverage, dropout robustness, repeat-pick share and exposure Gini versus baselines; extraction role F1 on 30 labelled briefs by language; rule-flag precision on planted anomalies; roster solve time; end-to-end demo completes in under 3 minutes without manual rescue. These are **proxy measures on synthetic data, not a claim of field impact**.

## 8. Constraints
Built overnight as a prototype (deadline 2026-11-19 06:00 IST for ~90% completion); no real data; the hackathon's rule on pre-built work is unconfirmed, so the plan assumes the build-day product is rebuilt from the spec on 8 to 9 December unless organisers say otherwise (see ADR-001). Offline-capable demo (cached model outputs).

## 9. Risks
Novelty overlap with MY Bharat (mitigated by positioning and by not claiming exclusivity); LLM misreads dialect text (abstention + manual path + measured accuracy); synthetic data critique (labelled, plus scripted generator); time (lane plan with tests as gates, see PLAN.md); rules uncertainty about pre-building (ADR-001).

## 10. Out of scope for this prototype
Authentication, multi-tenant admin, real notifications (WhatsApp/IVR), payments, mobile apps, real certificates, integrations. They appear in the path-to-pilot section of the TRD only.
