# Final idea-form answers (v4, Ready Crew)

Built on docs/v3/DA-SYNTHESIS.md, updated with verified results (docs/EVAL_RESULTS.md, docs/LOCAL_MODEL_RESULTS.md,
PROJECT_REPORT.md) and the MY Bharat public-sources comparison (docs/MYBHARAT-COMPARISON.md). Form limit 500 characters;
counts are Unicode code points after NFC, printed by the script that wrote this file. The team lead submits the form.

### Q1. How does your solution address the use case? (461 characters)

MY Bharat lets young people find drives and show interest; an organiser then approves names one by one. SewaCircle Ready Crew covers the next step. It turns a Hindi or English task brief into roles, builds a crew from youth who opted in, and answers one question: can this drive run? READY, or NOT READY plus an exact recruit request (1 host-checked first-aider, Saturday morning, within 15 km). After the drive, a host confirms who did what against attendance.

### Q2. What makes your solution unique? Call out two features. (425 characters)

1) Ready verdict with standby: a solver checks every essential role survives any single dropout and turns gaps into precise recruit requests. On 10 synthetic drives it was ready on 7, nearest-skill matching on 1. 2) Safe and private by design: first-aid, disaster and driving roles accept only host-checked skills; names become ids before any AI call; a skill we cannot map stays unresolved instead of being opened to anyone.

### Q3. How will you build it? (455 characters)

An LLM extracts roles with their source phrases (a 7B open model on one free T4 GPU reached 0.93 recall as an offline fallback); the organiser edits them. OR-Tools CP-SAT assigns people under skill, availability, travel, minor-consent, standby and fair-rotation constraints, with a reason per pick and why-not answers. FastAPI and React, Hindi/English. Evidence: AI drafts cards, fixed rules flag conflicts, a host confirms, a hash-chained log records it.

### Q4. What MVP will you build in the hackathon window? (477 characters)

Live: paste an unseen Hindi brief, correct the roles, get a crew with a READY or NOT READY verdict next to three baselines, drop a volunteer and watch it heal or issue a recruit request, ask why someone was not picked, then settle one contribution card whose claimed hours conflict with attendance. Plus an evaluation harness with confidence intervals and its own list of failures. Synthetic data only; 16-17 year olds need recorded guardian consent; no government integration.

### Q5. Why should your idea be shortlisted? (422 characters)

It targets the step MY Bharat's public documents leave to manual judgement: turning 'Interested' into a safe, complete, fair crew. It is measured: ready on 7 of 10 drives vs 1, as ready as a careful organiser with 20 points fewer repeat picks, under 0.4 s for 500 volunteers. AI only reads text; a solver decides; a human approves. Our idea-stage prototype is public and every number comes from a command anyone can rerun.

## Numbers used and where they come from
- ready 7/10 vs nearest-skill 1/10; ties careful organiser 7/10; repeat-pick share -0.197: docs/EVAL_RESULTS.md
- max solve 0.327 s at 500 volunteers (80/80 OPTIMAL): Kaggle CPU notebook, PROJECT_REPORT.md section 3
- Qwen2.5-7B 4-bit on one T4, role recall 0.932: docs/LOCAL_MODEL_RESULTS.md (easy synthetic briefs, n = 30)
- MY Bharat 'Interested' tab, approve or reject 'based on your discretion': docs/MYBHARAT-COMPARISON.md source 2
