# Brief for Codex (gpt-6-sol, one session) - SewaCircle strategy review and redesign

You are the STRATEGIST and ADVERSARIAL REVIEWER for a hackathon entry. Claude Code is the head and will review your output
before anything is merged. The owner, Shubh (17, BCA student, Kanpur, Uttar Pradesh), wants to WIN the event (top 5), not
just pass screening. Work as deeply as you can. This is one run: no polling, no sleeping, no installs, do not start servers.
You MAY read any file, run read-only commands, run the test suite (`.venv\Scripts\python -m pytest -q` from backend\) and
the eval harness (`python -m eval.harness` from backend\), and use web search/fetch if your tools allow it.

## 1. The event (verified facts; official text is in C:\Users\shubh\Projects\ai-kaushal-research\01_OFFICIAL_USECASES.md)
AI Kaushal Hackathon 2026: InMobi with the Department of IT & Electronics, Government of Uttar Pradesh; tech partner OpenAI;
academic partner and venue IIIT Lucknow. 17 use cases. Idea form closes 20 Nov 2026 (5 answers of max 500 characters +
optional 20 MB zip). Shortlist 27 Nov. Build: 24 hours in person, 8 Dec 11:00 to 9 Dec 11:00, then panel evaluation and
finals (4-7 PM). Top 5 teams get Rs 1 lakh each; winners may be deployed in a UP department. Claude, OpenAI and Gemini credits
are given on the day. A team may submit ideas for several use cases but only one is shortlisted per team.
Idea screening criteria: relevance; innovation and uniqueness ("novelty of approach counts for more than novelty of concept");
solution approach and technical soundness with AI at the centre; feasibility and clarity of 24-hour scope.
Build-day criteria: working solution and completeness (live demo); technical execution and architecture; innovation and
differentiation ("inventiveness in solving the more difficult aspects"); impact against the use case (show or estimate the
gain over today); scalability and path to production (integration, cost, regulatory fit); responsible AI as BUILT.
Jury: Mohit Saxena (Co-founder and CTO, InMobi); Dr Subi Chaturvedi (Global SVP, Chief Corporate Affairs and Public Policy,
InMobi; conceived the event); Srikanth Sundarrajan (Partner Engineer II, InMobi); Alok Kumar IAS (Principal Secretary,
Planning and IT & Electronics UP; nodal officer, One Trillion Dollar Economy Mission and Zero Poverty Program); Kumar Vineet IAS
(event page: Special Secretary, Ministry of Youth Affairs and Sports; a third-party tracker lists him as UP-cadre Special
Secretary, UP Sports and Youth Welfare Department - UNVERIFIED which); Prof Deepak Singh (Dean Research, IIIT Lucknow).

## 2. The use case the owner has LOCKED: UC16 AI Youth Volunteer and Community Project Matcher (Dept of Youth Affairs & Sports)
Challenge: young people struggle to find community projects matching skills, interests, location, availability; organisers
struggle to identify suitable volunteers, form balanced teams and track individual contributions, so volunteer experience is
hard to recognise and document. Good solution: AI platform that matches youth to projects; helps organisers form teams with
complementary abilities; tracks and verifies contributions; keeps a record of each volunteer's experience and impact.
Do NOT reopen the choice of UC16. Everything else is open.

## 3. The owner's doubt (paraphrased from his message, 2026-11-19 00:25)
"Reading the PRD and PLAN, we are just making a cheap copy of MY Bharat. There is nothing special in our software. We are
choosing the hard way, building it code by code, and not making something new." He wants: a deep review that finds every
loophole; UNIQUE features (he stresses that merely new features are not automatically unique); a redesign of the concept,
documents, structure and plan if needed; and a strategy that uses reverse engineering of existing software (he proposed copying
existing software 1:1 and reusing its parts) and free Kaggle GPU/CPU (30 h/week) where useful.

## 4. What exists now (read these)
Repo C:\Users\shubh\Projects\sewacircle (public: https://github.com/shubhsaxena2020/sewacircle):
- Root docs: PRD.md, TRD.md, ADR.md, PLAN.md, DESIGN.md, CONTEXT.md, PROJECT_REPORT.md, README.md.
- docs/EVAL_RESULTS.md (real harness output), docs/eval_report.json, docs/CONTRACT_REVIEW.md (your own earlier pass), docs/AMENDMENT-A1.md,
  docs/research/R1..R6 + INDEX.md + up_districts.json (primary-sourced research: CP-SAT formulations, Hindi NLP, Open Badges 3.0 /
  W3C VC / DPDP Act children's data, UP realism, demo UX, eval and responsible AI), docs/screens/*.png (live UI screenshots).
- backend/app: schemas.py (contract), solver/cp_sat.py (tiered CP-SAT, standby resilience, fairness, counterfactuals, dropout heal),
  solver/baselines.py + metrics.py, llm/extract.py + prompts.py + redact.py + client.py, evidence/rules.py + ledger.py + badges.py,
  data/synth.py; backend/eval/harness.py and eval/extraction/ (30 author-written briefs). 673 tests pass.
- Measured (synthetic, n=10 tasks, 80 volunteers): role coverage tied with all baselines; dropout robustness +0.61 vs nearest-skill
  and tied with a careful manual organiser; repeat-pick share -0.20 vs manual; 6 misses listed. Extraction: Claude Sonnet 30/30 briefs
  fully correct, DeepSeek 59/60 roles, BUT the 30 briefs were written by the head and are easy (explicit counts) - weak evidence.
- Earlier research in C:\Users\shubh\Projects\ai-kaushal-research: orch\UC16-champion.md (your independent UC16 study: MY Bharat
  overlap, verdict hedge-only for a plain matcher), orch\ANSWERS-review.md, orch\DIRECTIVES-pass1.md, src16\mb.txt and pib1.txt (MY Bharat
  official text), lanes\K2-winners\reports\ (past winners and judges; spot-check before relying), lanes\K1-usecases\uc\UC16.md (NOTE: it
  missed MY Bharat entirely), submission\answers_v2.py (the idea answers drafted so far), submission\assets\onepager.html.

## 5. Your tasks
A. VERDICT ON THE DOUBT. Is SewaCircle a copy of MY Bharat? Compare feature by feature against what MY Bharat, NSS/NYKS tools and other
   volunteer platforms actually offer (cite opened sources; mark UNVERIFIED). Say plainly what is genuinely distinct, what is not, and
   whether the distinct part is strong enough to make the top 5 against teams on all 17 use cases.
B. LOOPHOLES. Every weakness a judge, a rival team or a sceptical IAS officer would exploit: concept, positioning, metrics (are any
   rigged or trivial?), synthetic-data credibility, demo risks, responsible-AI gaps, deployment story, the idea answers, the team's
   ability to rebuild in 24 hours.
C. THE WINNING CONCEPT. Propose 2-3 sharply different concept directions for UC16 that would win, then choose one. Think about what makes
   a government + industry jury remember a team: a real, felt problem with a number attached; something they cannot get today; AI doing
   the hard part; proof it works; a credible path into a UP department. "Unique" means distinctive and defensible, not just new.
   Consider (do not limit yourself to): turning the evidence ledger into the hero; impact measurement for the department; a
   district-level youth-capacity view for officials; volunteer-side experience (WhatsApp/voice, Hindi); integrating with real public
   programmes; using OpenAI/Claude/Gemini credits in a way that is central, not decorative. Keep what already works if it serves the
   chosen concept; say what to cut.
D. FEATURES. A feature table for the chosen concept: what it does, why a judge cares (map to the six build-day criteria), how unique it is
   versus existing platforms (with evidence), 24-hour build cost, demo moment, risk. Cap the must-have list to what 4 people can build in
   24 hours with these credits; mark the rest stretch.
E. REVERSE ENGINEERING AND REUSE. The owner proposed copying existing software 1:1 and reusing its parts. Evaluate honestly: legality
   (copyright, licences, terms of use of government portals), hackathon rules (build must happen in the 24 hours; originality), ethics,
   and judge perception. Then give the LEGITIMATE version: which open-source projects (with licence and URL) can be reused, which public
   products should be studied for UX and feature gaps (what to look for), what may be prepared before 8 Dec (to ask organisers), and
   how the REA reverse-engineering toolkit available to the head could help with competitive analysis of public web apps.
F. KAGGLE. The owner has 30 h/week of free Kaggle GPU/CPU. Say concretely if and how it helps this concept (e.g. benchmarking Indic
   speech or OCR models, larger evaluations, a small fine-tune) or say it is not needed. No hand-waving.
G. DOCUMENTS. Write these NEW files under C:\Users\shubh\Projects\sewacircle\docs\v2\ (do not edit any other file):
   STRATEGY-REVIEW.md (A and B, with a clear verdict), CONCEPT-v2.md (C, the chosen concept in one page plus the rejected options and why),
   FEATURES-v2.md (D), PRD-v2.md (full product requirements for the chosen concept), PLAN-v2.md (dated plan: now to 20 Nov idea form,
   20 Nov to 8 Dec preparation, the 24-hour build hour by hour for 4 people, demo and finals), ADR-v2.md (new decisions, numbered from
   ADR-015), DEMO-v2.md (3-minute demo script with timings and the exact numbers to show), IDEA-ANSWERS-v3.md (the five answers, each
   at most 480 characters with the count computed by a command and pasted, plus a project name), REUSE-AND-RE.md (E and F).

## 6. Rules
Never invent facts, names, numbers, URLs or results; cite URLs you actually opened; mark UNVERIFIED / NOT FOUND. Separate FACT,
INFERENCE and OPINION. Be blunt: if the current product should be cut down or pivoted, say so. Write concise, specific documents
(no filler). When done, end with a short summary of the verdict and the top 10 changes.
