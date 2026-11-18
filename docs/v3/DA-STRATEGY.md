# Devil's Advocate: SewaCircle strategy and the proposed v2 pivot

Review date: 19 November 2026. **FACT** = checked repository text, command output, or opened source; **INFERENCE** = deduction from those facts; **OPINION** = product judgment. The owner has not approved the v2 pivot. This review attacks both the v1 product and v2 proposal. UC16 is fixed.

## Steel-man

The v1 design correctly separates language understanding from roster decisions and human review (`../../PRD.md`, `../../ADR.md`). Its v2 pivot also acknowledges that [MY Bharat already offers volunteering opportunities](https://mybharat.gov.in/about_mybharat), while [CiviVolunteer already supports roles, shifts and hour reports](https://civicrm.org/extensions/civivolunteer). A live, explainable crew stress test gives the project a visible decision that a directory screen lacks. The synthetic harness is rerunnable and does not conceal ties or misses (`../EVAL_RESULTS.md`). These are sound starting constraints, not evidence of a winning pitch.

## Ranked concerns

### 1

Concern: v2 narrows UC16 until the youth side almost disappears.
Severity: High — blocks a credible shortlist pitch until addressed.
Framework: Socratic probing of the official problem.

What I see:
  **FACT:** [UC16 asks for matching young people to projects by skills, interests, location and availability, then team formation and contribution records](https://www.inmobi.com/ai-kaushal). `../v2/PRD-v2.md` presents an organiser with an already available opt-in pool. `../../backend/app/schemas.py` has availability and location, but no interest or project preference field. v1 (`../../PRD.md`) also spends little time on the volunteer's actual choice.

Why it matters:
  **INFERENCE:** A panel could score the demo as a staff scheduler that handles only the latter half of UC16. This is a relevance risk, even if the organiser workflow is novel.

What to do:
  Add a small volunteer choice step: an invented adult profile sees relevant missions, expresses interest in one, and the organiser preflight uses only that opt-in set. Show why a relevant opportunity was offered. Keep it one screen and one task, not a marketplace.

### 2

Concern: "Mission Assurance" makes a technical mechanism sound like the public benefit.
Severity: High — blocks the current headline, not the solver.
Framework: Inversion: how to make a judge forget the pitch.

What I see:
  **FACT:** `../v2/CONCEPT-v2.md`, `../v2/DEMO-v2.md` and `../v2/IDEA-ANSWERS-v3.md` lead with an abstract readiness frame. **OPINION:** An IAS officer can understand a missing first-aider; an ad-tech CTO can appreciate counterfactual search. Neither needs the term "Mission Assurance" to remember either point. It can also suggest a safety guarantee the prototype cannot give.

Why it matters:
  **INFERENCE:** The label competes with the more vivid result: "We need one qualified person or this drive cannot run." A broad UC16 jury may see a clever optimisation widget instead of an answer to youth participation.

What to do:
  Keep SewaCircle as the name. Pitch "SewaCircle: Ready Crew" with the hook "Willing volunteers are here. Can this drive run?" Show a volunteered interest, the missing role, and the actionable repair on one screen. Treat readiness as a conditional planning assessment, never a guarantee.

### 3

Concern: the numerical hero does not beat the strongest baseline.
Severity: High — blocks any superiority claim.
Framework: Pre-mortem: a judge asks "Why not a careful organiser with a backup?"

What I see:
  **FACT:** The command `..\.venv\Scripts\python.exe -m eval.harness` from `backend/` produced the same table as `../EVAL_RESULTS.md`: role coverage **0.917** for CP-SAT, nearest-skill and manual-greedy; dropout robustness **0.760** for CP-SAT and backup-aware manual-greedy. The fixture is author-generated in `../../backend/app/data/synth.py`. The fairness proxy differs, but there is no observed organiser time or field outcome.

Why it matters:
  **INFERENCE:** A live benchmark panel will see no current evidence that preflight outperforms a careful human on the headline metric. The "top-five contender" story then rests on novelty of presentation.

What to do:
  Test frozen, independently authored hard cases and a real organiser workflow, if one consents. Measure time to a defensible decision and missed constraints against an actual manual process. Make the demo's comparison a small evidence panel, not its climax. Preserve ties and misses.

### 4

Concern: the proposed safety gate exists in prose, not in the current product.
Severity: High — blocks a "qualified/safe crew" demo claim.
Framework: AI blind spot: confidence without correctness.

What I see:
  **FACT:** `../v2/PRD-v2.md` R2 and `../v2/ADR-v2.md` ADR-017 require checked safety qualification. `../../backend/app/solver/metrics.py:91-104` accepts a self-declared skill at any required level. `../../backend/app/schemas.py` has no checked-skill provenance. `../../backend/app/llm/extract.py:50-65` can drop an unknown skill and leave a role open to anyone.

Why it matters:
  **INFERENCE:** A visually complete first-aid crew can fail the very rule that the pitch says makes SewaCircle trustworthy. A human approval button does not repair a hidden eligibility error.

What to do:
  Make qualification provenance explicit and block safety-critical assignments without it. Make unsupported extracted skills unresolved rather than open. Until that works, use a non-safety role for the success path and show first aid as a no-go case.

### 5

Concern: the three-minute script spends its scarce attention defending the prototype.
Severity: Medium — not a software blocker, but a pitch blocker.
Framework: Inversion: guarantee a flat final demo.

What I see:
  **FACT:** `../v2/DEMO-v2.md` begins by discussing existing systems and reserves an extended segment for synthetic benchmark ties and misses. `../v2/IDEA-ANSWERS-v3.md` is accurate but repeatedly uses phrases such as "complements existing platforms" and "not a new directory or certificate." **OPINION:** These are good answers to objections, weak opening images.

Why it matters:
  **INFERENCE:** The jury may remember the caveat instead of the decision. Honesty is necessary, but its placement can be tighter.

What to do:
  Open with a concrete youth-to-drive choice and a crew that looks full but fails. Show the specific repair or no-go state. Put one visible "synthetic demo" label on the screen, state the key evidence limit once, and move detailed baseline caveats to the comparison panel and questions.

### 6

Concern: the MVP is still several workflows pretending to be one.
Severity: Medium — non-blocking for the idea form; blocks an unrehearsed on-site build.
Framework: Pre-mortem of the build day.

What I see:
  **FACT:** `../v2/FEATURES-v2.md` requires extraction, role review, constraint solve, standby, comparison, host-note AI drafting, correction, export and failure rails. The current `../../backend/app/main.py` exports a credential, while `../v2/PRD-v2.md` promises a plain mission packet. The exact prepared-code policy is **UNVERIFIED** on the [event page](https://www.inmobi.com/ai-kaushal).

Why it matters:
  **INFERENCE:** If reuse is barred, closeout and export integration can consume rehearsal time while the hero decision remains brittle. If reuse is allowed, prose and API still disagree.

What to do:
  Set a hard build order: opted-in candidate choice, reviewed roles, crew, dropout/no-go and exact repair first; one simple host-reviewed record second. Cut LLM note drafting and badge export from the on-site minimum. Rehearse both reuse rulings.

### 7

Concern: "not found in public pages" is still doing too much work as novelty evidence.
Severity: Medium — watch and validate before deployment claims.
Framework: Socratic probing of competitor evidence.

What I see:
  **FACT:** `../v2/STRATEGY-REVIEW.md` carefully says organiser-side preflight was *not found* in inspected public material. [Better Impact documents detailed scheduling and conflict handling](https://support.betterimpact.com/en/articles/18325829-comprehensive-guide-to-scheduling); [CiviVolunteer documents role and shift assignment](https://civicrm.org/extensions/civivolunteer). Private MY Bharat organiser capabilities are **NOT FOUND**. No programme owner has confirmed a roster handoff or data-sharing route in the cited project documents.

Why it matters:
  **INFERENCE:** A rival with existing programme access can copy a standalone dropout button. Defensibility lies in a trusted workflow, hard-case performance and the exact action to close a gap.

What to do:
  Ask one organiser to show a de-identified past roster and point to the decision they could not make promptly. Validate whether a shortage-to-recruitment handoff would actually be used. Position SewaCircle as a tested decision module, not as an unoccupied market category.

## Verdict

**Ship with changes** for the idea-stage concept. Do not ship the v2 wording or a "safe qualified crew" claim as written. The strongest revision is a youth choice leading to an organiser's exact go/no-go and repair decision, backed by explicit qualification gates and an honest comparison against a backup-aware human process. This is a plausible UC16 entry; top-five rank remains **UNVERIFIED**.
