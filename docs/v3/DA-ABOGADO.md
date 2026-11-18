# Abogado del Diablo: can SewaCircle win UC16?

Review date: 19 November 2026. **FACT** = checked repository text, command output, or opened source. **INFERENCE** = conclusion from that evidence. **OPINION** = judgment. This is an attack on an entry aiming for the hackathon's top prize group, not a claim to predict the jury. UC16 remains fixed.

## VERDICT

**OPINION:** As currently pitched, SewaCircle can pass a technical demo and still lose. The likely reason is not a broken solver. It is that the jury sees a staff rostering aid, an authored synthetic benchmark, and an unproven adopter while the use case asks for a youth-to-project experience and a credible contribution record. The proposed v2 pivot reduces duplication but does not yet answer that attack.

## The cracks, ranked by damage

### 1. False premise: a checked crew is already available

**The blow — FACT:** [UC16 starts with young people finding suitable projects by skills, interests, location and availability](https://www.inmobi.com/ai-kaushal). `../v2/PRD-v2.md` assumes an opt-in candidate list exists. `../../backend/app/schemas.py` stores no interest or per-task opt-in decision. The current fixture creates synthetic people and then alters their skills or availability to make most tasks feasible (`../../backend/app/data/synth.py:91-128`).

**Why it is lethal — INFERENCE:** The system optimises a pool that the product has not shown it can form. A judge can reject the UC16 fit without disputing the algorithm.

**What would have to be true — OPINION:** Demonstrate a specific volunteer expressing interest in a specific task, then route that choice into the roster. If no organiser is willing to supply such a list, show how a consented CSV would be obtained and name that as an unvalidated pilot input.

### 2. Feasibility: the safety story rests on unchecked skills

**The blow — FACT:** The proposed checked-skill rule in `../v2/ADR-v2.md` is not represented in `../../backend/app/schemas.py`. `../../backend/app/solver/metrics.py:91-104` lets a self-declared skill qualify at any level. `../../backend/app/llm/extract.py:50-65` drops unknown skills and can leave a role with no skill constraint. The API accepts a caller-supplied task (`../../backend/app/main.py:122-142`).

**Why it is lethal — INFERENCE:** A "ready" first-aid roster can be false for a reason the interface hides. That is more damaging than an honest red shortage.

**What would have to be true — OPINION:** Checked evidence must be a distinct field and a hard gate on safety-critical roles. Unknown extracted requirements must stop approval. If the fix is not complete, do not call the roster safe or qualified.

### 3. Competition: an existing organiser can do much of this without SewaCircle

**The blow — FACT:** [CiviVolunteer assigns roles and shifts and logs hours](https://civicrm.org/extensions/civivolunteer); [Better Impact describes assignments, conflicts and attendance](https://support.betterimpact.com/en/articles/18325829-comprehensive-guide-to-scheduling). [MY Bharat already offers youth volunteering opportunities](https://mybharat.gov.in/about_mybharat). A spreadsheet plus messages is the local status quo; its exact performance for the target organiser is **UNVERIFIED**.

**Why it is lethal — INFERENCE:** A dropout button is copyable. A judge can reasonably ask why an existing portal or attentive organiser needs a new product.

**What would have to be true — OPINION:** Show the hard decision the existing workflow misses: the smallest *safe* action that turns an infeasible crew into a feasible one, with a traceable reason. Test that action against a backup-aware manual process on independent tasks.

### 4. Execution: the proposed demo describes a product that has not been built

**The blow — FACT:** `../v2/PRD-v2.md` promises a plain mission packet and checked qualification; `../../backend/app/main.py:253-265` currently exposes credential export, and no checked-skill field exists. `../v2/DEMO-v2.md` labels its one-task interface as planned. The [event page](https://www.inmobi.com/ai-kaushal) says the MVP is built during the in-person hackathon; whether this pre-event code may be reused is **UNVERIFIED**.

**Why it is lethal — INFERENCE:** Rehearsal can succeed only on a scripted fixture while an unseen brief, qualification check or export handoff fails on stage. If prepared code is disallowed, the broad scope consumes the build window.

**What would have to be true — OPINION:** Lock the minimum to a youth opt-in, reviewed roles, preflight, one dropout and a concrete repair/no-go. Add one reviewed contribution record only after that works. Get the organiser's written reuse ruling; keep a smaller rebuild path.

### 5. Problem and market: the real buyer and frequency are unknown

**The blow — FACT:** The project names district/block officers, NSS officers and NGO coordinators as users (`../../PRD.md`, `../v2/PRD-v2.md`), but the reviewed documents include no observed organiser workflow, buyer commitment or use frequency. Public programme descriptions do not establish private MY Bharat organiser gaps; that capability is **NOT FOUND**, not absent.

**Why it is lethal — INFERENCE:** The team may solve an occasional planning annoyance while the programme's actual bottleneck is getting reliable volunteers, transport, approval or attendance. A technically correct solver cannot create demand for an unwanted step.

**What would have to be true — OPINION:** Ask a willing organiser to walk through a de-identified past drive, identify the precise delayed decision and show how they would act on a shortage card. Record whether this replaces a real step. No participant or buyer validation exists yet: **UNVERIFIED**.

### 6. Numbers: the current comparison cannot carry an outcome claim

**The blow — FACT:** The rerun `..\.venv\Scripts\python.exe -m eval.harness` from `backend/` produced role coverage **0.917** for CP-SAT and both nearest-skill and manual-greedy; dropout robustness **0.760** for CP-SAT and backup-aware manual-greedy. The harness covers **10 synthetic tasks and 80 synthetic volunteers**, with **6** listed misses (`../EVAL_RESULTS.md`). There is no measured manual time, organiser adoption, cost per mission, service budget or community outcome in the cited documents: **NOT MEASURED**.

**Why it is lethal — INFERENCE:** The only numerical advantage in the fixture is a fairness proxy over the manual heuristic. It does not establish faster decisions, more completed drives or fairer opportunity in the field. There is no unit economics case for a continuing service.

**What would have to be true — OPINION:** Publish a paired, independent challenge set and a timed organiser workflow if an organiser consents. For a pilot, price the model call, staff review, hosting, support and integration per mission against an identified owner and budget. Do not invent CAC, LTV or impact estimates for the idea form.

### 7. Blind spot: the "human verified" closeout has no accountable human identity

**The blow — FACT:** `../../backend/app/main.py:202-224` accepts an arbitrary `actor` string and can mark a card confirmed. `../../backend/app/evidence/ledger.py:1-35` correctly says its chain establishes integrity relative to a stored head, not event truth. `../v2/IDEA-ANSWERS-v3.md` says a host reviews a claim against attendance, but the current API cannot prove the reviewer is the host.

**Why it is lethal — INFERENCE:** The most persuasive contribution story can become the least trustworthy claim in cross-examination. It also does little to show a volunteer receiving a useful record.

**What would have to be true — OPINION:** Label the event as a demo host decision. Export the claim, attendance value and correction with provenance; do not call it independently verified or a credential. A pilot needs authenticated authority and a volunteer correction path.

### 8. Pre-mortem: the likely deaths are mundane

**The blow — INFERENCE, imagined sequence:** At the final demo, the team opens a polished roster. A judge asks the youth volunteer to choose a project and asks how the first-aid qualification was checked. The former was skipped and the latter was a self-declared tag. The team retreats to synthetic fairness figures that tie a careful organiser on dropout survival. The entry loses despite passing tests. A later pilot also stalls when no programme owner can supply permissioned profiles and a host reviewer.

**Real analogue — FACT:** [Kambeo's own shutdown notice says it ceased its volunteer platform after years without the hoped-for growth](https://kambeo.io/blog/volunteer-platform-retailers/). [Reach Volunteering planned closure because of funding pressure, then reversed it after funders intervened](https://reachvolunteering.org.uk/news-and-blogs/reach-staying-open). Neither proves SewaCircle will fail; both show that volunteer-platform utility and sustainable operation are different questions.

**Why it is lethal — INFERENCE:** Building a broad platform compounds adoption and maintenance costs before the team has identified a funded operator.

**What would have to be true — OPINION:** Win with one defensible decision module and an exportable record, then let an authorised programme owner decide whether it belongs in an existing workflow.

## The one that kills it

**OPINION:** The largest present risk is a **use-case credibility gap**: the demo assumes willing, eligible youth appear, then claims a safe crew without checked qualification evidence. This combines product relevance and trust failure. No amount of UI polish repairs it.

## If proceeding, fix these first

1. **OPINION:** Rewrite the idea submission around a volunteer's expressed interest leading to an organiser's go/no-go and exact gap-closing action. Keep the technical label in the appendix.
2. **OPINION:** Implement and test checked qualification as a hard gate; make unknown extracted skills and missing counts block approval. Until then, show those cases as failures, not successes.
3. **OPINION:** Freeze independent task cases and compare with a backup-aware manual workflow. Report all ties and failures. Seek one consented, de-identified organiser walkthrough; mark it **NOT FOUND** if unavailable.
4. **OPINION:** Reconcile the promised plain mission export with the actual credential endpoint; use a host-labelled, unsigned record and avoid verification language.
5. **OPINION:** Obtain the event's written ruling on prepared code before deciding what can be demonstrated as a build-day result. Cut the on-site scope accordingly.

**Survival verdict — OPINION:** The core idea survives only as a narrow, conditional crew decision and youth opt-in flow. The current v1 platform story and the v2 "Mission Assurance" pitch do not yet survive a win-oriented review. Top-five odds are **UNVERIFIED**.
