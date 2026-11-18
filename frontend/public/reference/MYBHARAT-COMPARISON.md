# MY Bharat vs SewaCircle Ready Crew - public-sources feature comparison

Date: 2026-11-19. Method: we read **only public documents about MY Bharat hosted outside the portal** (PIB releases, a PIB
backgrounder PDF, a college-hosted copy of the MY Bharat user manual, the Google Play listing summary). We did **not** crawl,
scrape, automate, decompile or reverse-engineer mybharat.gov.in: its Terms of Use (Section 3) prohibit using "any computer
program, bot, robot, spider ... to retrieve, index, data mine" the site, "automated software", and reverse engineering, and
allow viewing "for non-commercial purposes only". Anything a person wants to double-check on the portal itself should be
checked by hand in a browser.

"Not found" below means **not found in the sources we read**. It is not proof that the portal lacks the feature.

## Sources
1. PIB Backgrounder "MY Bharat - Where Digital India Meets Young India", 05 July 2026 -
   https://static.pib.gov.in/WriteReadData/specificdocs/documents/2026/jul/doc202675911701.pdf
2. MY Bharat user manual (Partner / Youth / NSS PO modules), college-hosted copy, file date 2024-11-13 -
   https://mswebdocstorage.blob.core.windows.net/ismailyusufcollegedocuments/Manual_-_MY_Bharat.pdf
3. PIB release on MY Bharat 2.0 (30 June 2025; CV builder, AI chatbots, National Career Services section, Mentorship Hub) -
   https://pib.gov.in/PressReleasePage.aspx?PRID=2140836 ; app launch release - https://www.pib.gov.in/PressReleasePage.aspx?PRID=2173543
3b. News (secondary, not official): Organiser, 31 Oct 2025, "Future Roadmap: AI, skill mapping, and entrepreneurship" (planned
   AI-driven career counselling and skill-gap analysis) - https://organiser.org/2025/10/31/323567/bharat/india-scales-up-mera-yuva-bharat-digital-mission-over-2-crore-youth-empowered-through-ai-and-skill-development/
4. Google Play listing - https://play.google.com/store/apps/details?id=com.gov.mybharat
5. MY Bharat Terms of Use - https://mybharat.gov.in/pages/terms_of_use (read once, by hand-equivalent single fetch, to check what is allowed)

## What MY Bharat documents (verbatim where quoted)
| Area | What the sources say | Source |
|---|---|---|
| Scale | "2.22+ Crore Youth Registered", "1.52+ Lakh Volunteer Opportunities", "24900+ Experiential Learning Programs" (as of 02 July 2026) | 1 |
| Volunteer management | "end-to-end digital volunteer management through online registration, attendance, geo-tagging, certificate generation and impact tracking" | 1 |
| Recognition | "digital badges, certificates and verified participation records" | 1 |
| Event creation (partner/DYO) | Fields: Event Type, Event Name, Partner Name, Highlights, About Event, No. of Days, Last date to show interest, Event Time & Dates, Event Age Group, Activity Lineup; image; "Send for Approval"; "published upon Verifier (DYO) approval" | 2 |
| Selecting people | Youth click "Show Interest" with a reason; partner opens the **Interested** tab, checks "Candidate Details & Qualifications", clicks "Approve or Reject based on your discretion" | 2 |
| Experiential learning | screening by college programme officers; shortlisting "based on qualifications and suitability"; "within a 30-kilometer radius"; partner assigns learning tasks, evaluates submissions with a rating; certificate after tenure | 2 |
| AI today | "AI-powered Resume builder", AI chatbots, voice-assisted navigation, 22 languages | 1, 3 |
| AI planned | "MY Bharat 2.0 is transforming youth engagement through Artificial Intelligence (AI), multilingual technologies, open APIs and digital credentials" (official); "skill mapping" / skill-gap analysis on the roadmap (news report only) | 1, 3b |

## Side-by-side
| Capability | MY Bharat (public sources) | SewaCircle Ready Crew |
|---|---|---|
| Youth discovery of opportunities, registration, profiles | **Yes, at national scale** | No (out of scope; we assume people already opted in) |
| Event publishing and approval workflow | Yes (partner -> DYO verifier) | No (we take an existing task) |
| Attendance, geo-tagging, certificates, badges | Yes | Attendance rows only; unsigned OB3-shaped export for demo |
| Per-role crew needs (roles x head count x required skill) for one event | Not found: event form has no role, skill or head-count fields | **Yes**: extracted from a Hindi/English brief, organiser edits |
| Choosing who does what | Manual approve/reject per person "based on your discretion" | **Solver builds the whole crew** with a reason per pick |
| "Can this drive run?" verdict | Not found | **READY / NOT READY** + exact recruit requests |
| Backups / standby, dropout re-planning | Not found | **Yes**: standby so any single dropout keeps every role; live heal |
| Safety-critical roles need checked skills | Not found | **Yes**: first aid, disaster response, driving accept host-checked skills only |
| Fair rotation across drives | Not found | **Yes**: repeat-pick share -0.20 vs a careful organiser |
| Per-person contribution evidence beyond attendance | "verified participation records" (method not described) | Draft cards from host notes, deterministic flags, host confirms, hash-chained log |
| Skill mapping with AI | On the roadmap per a news report (not in PIB text we read) | Uses skills; does not do career skill mapping |
| Open APIs | Planned (MY Bharat 2.0) | Designed to consume an interest list + profiles |

## What this means for the pitch
1. **Do not compete on discovery, registration, certificates or scale.** MY Bharat has 2.22 crore youth and 1.52 lakh
   opportunities. Say so first; it earns trust with the judges.
2. **The gap is the step after "Interested".** The documented flow ends in a list the organiser approves one person at a
   time. Ready Crew turns that list into a crew decision: roles covered, standby in place, safety roles checked, fair
   rotation, or a precise "recruit 1 more host-checked first-aider, Saturday morning, within 10 km".
3. **Integration story, not replacement:** MY Bharat 2.0 plans open APIs. Ready Crew could read an event's Interested list
   and approved profiles through such an API and hand back a proposed crew for the organiser to approve on MY Bharat.
   (Hypothetical; no API documentation was found.)
4. **Risk to state honestly:** a news report puts AI skill mapping on MY Bharat's roadmap, so simple skill matching may
   arrive there. Our defensible part is the crew-level decision (coverage + standby + safety gating + fairness + ready verdict),
   which is a constraint-solving problem, not a matching score.

## Limits of this comparison
The manual copy is from 2024 and the portal has changed since (app launched 01 Oct 2025, MY Bharat 2.0 under way). We
did not log in or use the portal. Features may exist that these documents do not describe.
