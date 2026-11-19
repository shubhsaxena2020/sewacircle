SEWACIRCLE UI OPTIONS - PAGE CONTENT SPEC (same facts in every direction)

Purpose: all 8 options must tell the SAME story with the SAME numbers, so the owner compares design, not data.
Everything below comes from _shared/sample-data.json (see also _shared/districts-20.json). Copy values verbatim.
Do not invent a single number, name, quote, partner, logo, testimonial or user count. Where a fact is not in the
data, say so in plain words instead of making one up.

GLOBAL CHROME (every page)
- Small "Synthetic data" badge.
- Line: "Not affiliated with MY Bharat or any government body."
- Visible language toggle (EN / हिंदी). It may be a static-looking control, but it must be legible and intentional.
- Nav across the console pages: Overview 01, Brief 02, Roles 03, Crew 04, Evidence 06, Ledger 07, Evaluation 08,
  Volunteers 09, Districts 10, Method 11. Use the two crew states from the nav (Crew = 04, or 05 for the not-ready state).
- Every page links somewhere sensible (real files, no dead hrefs).

01-landing.html
- Hero: the gap. Something like "The step after Interested." plus one supporting line. Hindi visible in hero
  (a Devanagari headline or standfirst) to prove the type system.
- Context numbers (only allowed external numbers, always with the source named "PIB backgrounder, 05 July 2026"):
  "2.22+ crore youth registered on MY Bharat", "1.52+ lakh volunteer opportunities". Frame it as the national platform
  working; SewaCircle covers what happens after a youth clicks Interested. No MY Bharat imitation, no logo, no emblem.
- How it works: brief -> roles (AI proposes, host confirms) -> crew + standby -> READY / NOT READY -> after the drive:
  cards, flags, host confirmation, ledger. Five or six steps, plain language.
- Verdict preview: task-01 "Water and hygiene camp", Kanpur Dehat / Akbarpur, sat morning, 6 people -> READY.
  Show the four filled roles and two standby people (Heena P., Mohit Z., Divya H., Kabir Z.; standby Imran B., Kavya L.).
- Measured results (eval, 10 synthetic tasks, 80 volunteers): CP-SAT vs nearest-skill baseline
  role coverage 91.67% both; dropout robustness 76% vs 15%; ready rate 70% vs 10%; repeat-pick share 23% vs 40%.
  95% CI available in eval.ci95. Say clearly these are 10 synthetic tasks, not a field trial.
- Limits: small sample (10 tasks / 80 volunteers), synthetic data, one language pair (Hindi/English), skills are
  host-checked claims not certificates, ledger proves tamper-evidence not truth.
- CTA: open the console; see the method.

02-console-task.html
- Left: the drive list (10 tasks from data: title, district/block, slot, team size). task-01 selected.
- Main: the brief card. Hindi brief_text of task-01 verbatim, in Devanagari, comfortable measure. Meta row:
  Kanpur Dehat / Akbarpur, sat_morning, team size 6, max travel 25 km, minors allowed yes.
- Sample buttons: "Hindi sample - Water and hygiene camp (task-01)", "English sample - Blood donation camp (task-02)".
- Primary action: "Extract roles". Secondary: "Clear". Small meta: extraction model cc/claude-sonnet-5-5,
  language detected hi, cached yes, redactions 0.
- Right rail: what happens next (3 short points), and a note that the AI proposes and the host confirms.

03-console-roles.html
- Heading: "AI proposed 4 roles. You confirm them."
- The 4 roles from extraction.roles, each with: role name, count, required skill(s), confidence (medium/medium/
  medium/low), the evidence phrase in Devanagari, and the reason ("Posters are requested but no number is given.",
  etc.). Role names: Poster team; First-aid support; Supplies and site setup; Local-language liaison.
- Edit controls per role: count stepper, skill chips, priority, remove; plus "Add role".
- "Needs your decision" list, all 4 items verbatim from extraction.needs_decision (dialect? how many per role?
  hygiene educator? check the low-confidence liaison role).
- Footer action: "Confirm 4 roles and build the crew"; a quiet "Re-extract" secondary. Summary: 4 roles, 4 slots,
  1 low confidence, 2 safety-linked roles (first aid).

04-console-crew-ready.html
- Hero of the screen: the verdict READY (task-01, Water and hygiene camp). Sub-line from explanations[0]:
  "READY: every essential role is filled and any one person can drop out without leaving a gap."
- Metrics strip (cp_sat): role coverage 100%, slots 4/4, dropout robustness 100%, novices 2, solve 15 ms, OPTIMAL.
- Crew board by role (4 rows/cards, one per role) with the assigned person, score, distance, and their reasons:
  role-01 Poster team -> Heena P. (score 74, 7.4 km; "Has posters and graphic design (level 2)", "Free sat morning;
  7 km from the site", "Not picked in the last 90 days").
  role-02 First-aid support -> Mohit Z. (113, 1.7 km; first aid level 3; "Newcomer (0 past drives)", flag novice).
  role-03 Supplies and site setup -> Divya H. (89, 16.3 km; logistics level 3).
  role-04 Local-language liaison -> Kabir Z. (118, 5.3 km; awadhi level 3; novel, flag novice).
- Standby rail: Imran B. covers Poster team + Local-language liaison, "Raises dropout robustness to 75%";
  Kavya L. covers Supplies and site setup, "Raises dropout robustness to 100%".
- Four methods compared on THIS task: cp_sat (coverage 100%, robustness 100%, repeat 0%, ready), nearest_skill
  (100% / 0% / 25%, not ready), random_feasible (100% / 0% / 25%, not ready), manual_greedy (100% / 100% / 25%, ready).
  Explain in one plain line: the solver is the only one that also protects against a drop-out without picking the same
  faces again.
- Why-not tool: Aarav C. (v-001) -> "Aarav C. could take Local-language liaison. That would take Kabir Z. off the
  roster. Role coverage 100% -> 100%; dropout robustness 100% -> 100%. The planner preferred the current pick on fit,
  distance and fairness (score 118 vs 98)."
- Drop-out tool: drop Heena P. -> healed with standby Imran B., no role left uncovered.

05-console-crew-not-ready.html
- Hero: NOT READY for task-02 Blood donation camp, Lucknow / Chinhat, sun morning, 6 people.
  "3 of 5 essential slots filled" (role coverage 60%), dropout robustness 0%, 1 action needed.
- Recruit request card, verbatim: Community mobiliser x2, needs community mobilisation at level 1+, free sun morning,
  within 25 km of Chinhat, Lucknow. Reason: "No eligible volunteer for 2 slot(s): needs community mobilisation /
  door-to-door outreach, free sun morning, within 25 km." Copy / share action with a plain-text preview.
- Filled roles shown honestly: Uday Y. (first aid, 8.2 km), Ruchi Z. (first aid, 15.5 km, novice, paired with Uday Y.),
  Sahil P. (documentation, 14.4 km), Tanvi L. (logistics, 15.9 km). Unfilled: Community mobiliser 1 and 2, empty slots
  drawn as gaps.
- Explanations verbatim: "Unfilled: Community mobiliser #1, Community mobiliser #2. No eligible volunteer was
  available; reported, not hidden." / "Dropout robustness is 0%: not enough eligible standby people for every role." /
  "NOT READY: 1 action(s) needed before this drive is safe to run."
- Next step: copy the request to the district WhatsApp group, or widen travel / slot and re-solve. Say that a NOT
  READY answer is the tool doing its job.

06-console-evidence.html
- Host notes (verbatim): "Heena P. worked about 5 hours." / "Mohit Z. worked about 5 hours." / "Divya H. worked about
  5 hours." / "Kabir Z. worked about 8 hours."
- Attendance table: task-01, four volunteers, hours = 5, 5, 5, 5.
- 4 AI-drafted contribution cards, status draft, drafted_by human, with evidence refs (host_note:task-01:v-008:cf512e004c,
  attendance:task-01:v-008). Hours claimed/recorded: Heena 5/5, Mohit 5/5, Divya 5/5, Kabir 8/5.
- Flags: round_number_inflation on the three 5-hour cards with the verbatim message ("5 hours is a round number shared
  by at least 3 cards in this batch; worth a quick spot-check, but round shifts are normal and this is not a
  rejection.") and hours_exceed_recorded on Kabir Z. (8 claimed vs 5 recorded) - the one real conflict to resolve.
- Actions per card: Confirm, Correct, Send back. Batch: confirm the three clean ones, correct Kabir's hours to 5.
  Show the fixed-rule framing: rules flag, the host decides.

07-console-ledger.html
- 9 linked entries as blocks (index 0..8): draft/flag/confirm/draft/draft/draft/flag, actor system or host.
  Show card_id, actor, prev_hash -> entry_hash in monospace, truncated with a copy affordance, and the chain visibly
  linked (index 0 prev_hash all zeros).
- Verify result: "ok, 9 entries, first_bad_index null" and the verbatim note: "Hash chain shows edits, not truth;
  truth comes from host confirmation."
- Credential export action (JSON download), "verify again", and a line on what tampering would look like.
- Actions present in data: draft, flag, confirm. Do not invent "revoke"/"delete" entries.

08-console-evaluation.html
- The four methods with 95% CI bands on each metric: role coverage, dropout robustness, ready rate, repeat-pick share,
  exposure Gini (explain Gini in one plain sentence). Use eval.summary + eval.ci95 values exactly.
- Headline comparisons: robustness 76% vs 15% (nearest skill), ready 70% vs 10%, repeat picks 23% vs 40%.
- Misses list (7 verbatim entries), e.g. "task-02: cp_sat repeat_pick_share 0.17 worse than random_feasible 0.14".
- Plain-language explanation block + honest reading: n=10 tasks, 80 volunteers, synthetic, wide CIs, not a field trial.
- generated_by line verbatim in small monospace at the bottom.

09-volunteer.html
- Volunteer view for Heena P. (v-008), 27, Sarvankheda, Kanpur Dehat. Hindi greeting is a good place for Devanagari.
- Drives they chose: task-01 Water and hygiene camp, sat morning, Akbarpur (opted_in_task_ids = task-01).
- Skills: 5 host-checked (graphic design 2, photography/video 2, Awadhi 3, first aid 2, driving 1) vs 0 self-declared
  - show both columns honestly, and explain what "checked" means (a host confirmed it; it is not a certificate).
- Their contribution: Poster team, 5 hours, card status draft, flagged round_number_inflation with the verbatim note,
  awaiting host confirmation. Standby note: if a crew member drops out, Imran B. covers Poster team.
- Tone: this is what a 20-year-old sees on a phone-sized column inside the desktop frame.

10-districts.html
- Use _shared/districts-20.json: all 20 UP districts, real approximate lat/lon, original stylised schematic (no copied
  map art, no emblem, no flag colours as branding). Plot the 20 points on a hand-drawn SVG schematic of the state's
  rough shape or a plotted grid - your call, but it must read as a map, not a chart.
- Only 4 districts have drives in this sample: Kanpur Dehat (3 drives, task-01 READY), Lucknow (3 drives, task-02 NOT
  READY), Varanasi (2 drives), Gorakhpur (2 drives). The other 16: no drives in this synthetic sample - show them as
  quiet "no drives in this sample" nodes, never with invented volunteer counts or readiness.
- District detail: for the 4, list drive titles with the verdict only where the data gives one (task-01 READY,
  task-02 NOT READY, others "not solved in this sample").
- Caption: 20 districts mapped, 4 with drives in this sample, coordinates approximate (Open Admin Data, CC-BY-4.0).

11-method.html
- How a crew is decided, plainly: hard rules first (must-have skill at level, free slot, within travel radius, minors
  only where allowed, safety roles accept host-checked skills only), then the solver fills slots and adds a standby for
  every essential role, then it re-checks that any one drop-out is survivable. Solver: OR-Tools CP-SAT, 15 ms on
  task-01, OPTIMAL status.
- Metric definitions in plain words: role coverage, dropout robustness, ready rate, repeat-pick share, exposure Gini.
- Data sources: synthetic seed 7, 80 volunteers, 10 tasks; real geography from Open Admin Data; external MY Bharat
  numbers from PIB with date; local model line "Qwen2.5-7B 4-bit on one T4: role recall 0.932" and solver scale
  "80/80 optimal up to 500 volunteers, max 0.327 s".
- Honest limits: 10 tasks, 80 volunteers, one state, Hindi/English only, host-checked skills, ledger proves integrity
  not truth, AI role extraction is recall 0.932 not 1.0.

HINDI
At least two places per direction: the landing hero and one console element (e.g. the brief body on 02, the greeting on
09, or the decision list on 03). Use natural Hindi, not transliterated English. Noto Sans Devanagari, line-height
>= 1.7 for Devanagari runs, and check the conjuncts (/क्ष/, /द्व/, /र्/) render cleanly in the screenshot.
