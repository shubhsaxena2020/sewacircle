# Reconciled recommendation for SewaCircle

Review date: 19 November 2026. **FACT** = checked repository text, command output, or an opened source. **INFERENCE** = deduction. **OPINION** = recommendation. UC16 remains fixed; the owner has not approved v2 or this revision. The [official form](https://www.inmobi.com/ai-kaushal) asks for five short answers, and the [official UC16](https://www.inmobi.com/ai-kaushal) includes youth discovery, complementary teams and contribution records.

## Decision

**OPINION:** Pitch **SewaCircle: Ready Crew**. Hook: **"Willing volunteers are here. Can this drive run?"** The single strongest concept is a **volunteer choice to crew decision**: an adult youth chooses a suitable drive; AI proposes roles from a Hindi or English brief; an organiser confirms them; constrained planning tests a one-person dropout; the screen names the exact qualification gap and produces a specific role request or shows a qualified standby. A host-labelled closeout leaves a plain contribution record. This modifies v2, rather than reverting to v1's broad platform.

**Why this beats the current framing — OPINION:** "Ready Crew" is plain enough for a public-service judge and still gives a technical judge a real counterfactual to interrogate. The memorable visual is a crew changing from apparently complete to "need one checked first-aider," then an exact safe repair or no-go. It covers the youth side of UC16 without rebuilding a discovery marketplace. The algorithmic contribution is the decision and repair, not a new badge, feed or guarantee of safety. Exact novelty among rivals and top-five placement are **UNVERIFIED**.

## Keep, cut, add

| Decision | Reason and boundary |
|---|---|
| **Keep:** reviewed Hindi/English role extraction, deterministic allocation, genuine dropout re-solve and unfilled-role display. | **FACT:** these are core to v1 (`../../PRD.md`, `../../backend/app/solver/cp_sat.py`) and map to the official team's complementary-abilities requirement. A model output is a draft, not a decision. |
| **Keep:** one host-labelled hours correction and plain provenance record. | **FACT:** `../../backend/app/main.py` can correct a card. **INFERENCE:** it completes the use-case arc. The actor is not authenticated, so label it a demo review. |
| **Keep:** the synthetic comparison and explicit misses, but as supporting evidence. | **FACT:** the rerun matches `../EVAL_RESULTS.md`; coverage ties nearest and manual, and dropout robustness ties backup-aware manual. No observed time or field effect exists. |
| **Cut:** "Mission Assurance" as the public name, broad marketplace, chatbot, WhatsApp, voice, badge/credential hero, district prevalence heatmap and LLM-drafted closeout as build-day requirements. | **OPINION:** they dilute the result or add work without proving the central decision. `../v2/FEATURES-v2.md` already cuts several; go further on the minimum. |
| **Add:** one explicit youth interest/opt-in choice feeding the candidate pool. | **FACT:** UC16 names interests; current `../../backend/app/schemas.py` does not. A single task card is enough to demonstrate it. |
| **Add:** a server-owned checked-qualification gate, especially for safety-critical roles, and an unresolved-extraction stop state. | **FACT:** `../../backend/app/solver/metrics.py:91-104` currently accepts self-declared skills; `../../backend/app/llm/extract.py:50-65` can turn unknown skills into an open role. The positive-path demo must not claim this is already fixed. |
| **Add:** an exact "make this crew ready" action derived from the solver, such as an unfilled role request specifying required skill, slot and area; if no safe repair is known, say so. | **OPINION:** this turns the red alert into a useful organiser action without pretending to have a volunteer to fill it. The minimum-repair logic is a proposal, **NOT BUILT**. |

## Changes with the biggest effect on winning

1. **OPINION — Fix relevance in the first impression.** Show a youth volunteer's project choice before the organiser roster. This is the missing half of the official use case, and it makes the journey more legible than a pure staff scheduler. Keep the interface to one task and one opt-in action.
2. **OPINION — Make the failure actionable and safe.** Implement checked qualifications, block unknown role requirements, then show dropout -> precise shortage -> role request or eligible standby. This is the defensible moment; a generic "not ready" badge is too thin.
3. **OPINION — Replace authored-fixture superiority with credible evidence.** Freeze independent language/roster cases, compare against a backup-aware manual process, and, if a willing organiser exists, time a de-identified real planning task. Publish ties and misses. If no organiser participates, mark that result **NOT MEASURED** and avoid a time-saved claim.

The stage script should open on the choice and failed preflight, then show repair, closeout and one compact evidence card. State "synthetic demo" visibly once; reserve detailed caveats for the evidence panel and questions. This is truthful without making caveats the headline. The [event criteria](https://www.inmobi.com/ai-kaushal) reward use-case relevance, approach novelty, feasibility, execution and responsible AI; the code review in `DA-CODE-REVIEW.md` identifies the current gaps.

## Revised idea-form answers

These are **proposed build-day features**, not claims that they are already implemented or that an entry was submitted. Copy only the paragraph under each question. The official form's limit is 500 characters; each answer below targets at most 480. Counts are Unicode code points after NFC normalization, including spaces and punctuation and excluding headings. The exact count command and its output appear below.

### Q1. How does your solution address the use case? — 457 characters

Young volunteers should find drives they want to join; organisers must know whether those volunteers form a complete crew. SewaCircle lets an adult volunteer express interest in a local task, turns its Hindi or English brief into reviewed roles, and builds a qualified team. Remove a member: it shows the exact missing capability and a safe next action. After the drive, a host reviews a contribution record against attendance. The demo uses synthetic data.

### Q2. What makes your solution unique? Call out two features. — 404 characters

1) Ready Crew stress-tests essential roles after a volunteer drops out and proposes a qualified replacement or the exact missing skill. 2) Interest to action: a volunteer chooses a relevant drive; the organiser sees a transparent team plan and a precise role request when the crew is short. AI interprets messy task language; constraints and human review govern decisions. The demo uses synthetic adults.

### Q3. How will you build it? — 440 characters

A language model extracts role proposals and source phrases from a Hindi or English brief; an organiser approves edits. A constraint solver uses availability, location, opt-in choice and checked skill evidence to assemble a crew, simulate a dropout and generate a shortage or repair request. FastAPI serves a small React interface; one host-reviewed card records claim versus attendance. The MVP uses synthetic adults and no government API.

### Q4. What MVP will you build in the hackathon window? — 405 characters

We will show one synthetic volunteer choosing a community drive, an organiser correcting AI-drafted roles, a qualified roster, and a live dropout test that finds a standby or names the role to recruit. A host then corrects one conflicting hours claim and exports a plain record. We will compare the roster with a backup-aware manual heuristic and show failures. No live profiles or government integration.

### Q5. Why should your idea be shortlisted? — 440 characters

UC16 asks for youth-to-project matching, complementary teams and contribution records. SewaCircle connects them: a volunteer choice feeds a crew preflight, and a shortage becomes a precise recruitment action. Judges can try an unseen brief, break the roster and inspect a host decision. We will show a working synthetic flow, measured ties and failures, with AI confined to tasks it can explain. Real-world impact needs an authorised pilot.

**Character-count command (run from `docs/v3`):**

```powershell
@'
from pathlib import Path
import re, unicodedata
text = Path('DA-SYNTHESIS.md').read_text(encoding='utf-8')
for n, answer in re.findall(r'^### Q([1-5])[^\n]*\n\n([^\n]+)', text, re.M):
    print(f'Q{n}: {len(unicodedata.normalize("NFC", answer))}')
'@ | & '..\..\.venv\Scripts\python.exe' -
```

```text
Q1: 457
Q2: 404
Q3: 440
Q4: 405
Q5: 440
```

## v2 claims or decisions I now reject

1. **OPINION:** `../v2/CONCEPT-v2.md` calls "Mission Assurance" the chosen strongest direction. The name hides the visible citizen and organiser action and can imply an assurance the data cannot provide. Keep the preflight mechanism, change the public frame.
2. **OPINION:** `../v2/STRATEGY-REVIEW.md` and `../v2/ADR-v2.md` push discovery too far into the background. Discovery is not novel, but the official UC16 requires a youth choice. Retain a bounded interest/opt-in step, without a marketplace.
3. **FACT:** `../v2/PRD-v2.md` R2, `../v2/IDEA-ANSWERS-v3.md` Q3 and `../v2/DEMO-v2.md` speak of checked or qualified safety-critical assignments. The current schema and predicate do not support that stronger claim (`../../backend/app/schemas.py`, `../../backend/app/solver/metrics.py:91-104`). It is a proposed gate, **NOT BUILT**.
4. **FACT:** `../v2/IDEA-ANSWERS-v3.md` Q2 sells a role-linked closeout. `../../backend/app/llm/extract.py:126-137` accepts the model's role string even if it differs from the planned assignment. The role link is **NOT GUARANTEED**; derive it from the assignment instead.
5. **INFERENCE:** `../v2/ADR-v2.md` calls counterfactual readiness the hero metric, but the published robustness includes optional-role dropouts (`../../backend/app/solver/metrics.py:165-189`) and ties backup-aware manual in `../EVAL_RESULTS.md`. It is a useful diagnostic, not a demonstrated win over a careful organiser.
6. **FACT:** `../v2/PRD-v2.md` R9 promises a plain mission packet; `../../backend/app/main.py:253-265` currently exports a credential for a confirmed card. The v2 export is **NOT BUILT**. The reviewed host is only an arbitrary actor label (`main.py:202-224`), so "verified" remains inappropriate.
7. **OPINION:** `../v2/DEMO-v2.md` gives benchmark caveats too much of the live story. Keep them available and accurate, but open with an action and a decision. The scripted one-task UI and three-minute completion are **UNVERIFIED** until the proposed build is rehearsed.

## Verification boundary and verdict

**FACT:** From `backend/`, `..\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` returned `673 passed, 83 warnings in 8.32s`. The same directory's `..\.venv\Scripts\python.exe -m eval.harness` printed synthetic seed **7**, **80** volunteers, **10** tasks, **0.917** coverage for CP-SAT/nearest/manual, **0.760/0.153/0.760** robustness and **6** misses; `../EVAL_RESULTS.md` contains the full output. These are development-fixture measurements. No real-user deployment, authorised integration, organiser timing, independent challenge-set result, qualified-skill provenance or top-five likelihood was verified.

**Verdict — OPINION:** Submit a Ready Crew concept only after the owner approves the wording. Prioritise the youth choice, the checked-skill and unknown-role gates, and the exact repair action. Keep the honest benchmark as evidence; never use it as a claim of field impact.
