# SewaCircle Ready Crew - scroll story storyboard (reference: oryzo.ai by Lusion)

What we take from the reference (patterns, not assets): ONE hero object carried through a very long scroll; the camera moves
around a real-feeling physical scene as you scroll; huge type that enters and leaves with the scroll; short video inserts;
playful interactive moments the visitor can trigger; a minimal top nav (chapters) and a progress rail; "scroll to continue" cue.
We copy nothing from oryzo/Lusion: no code, models, textures, images, copy or layout files. Everything is original.

## The scene and the hero object
An organiser's desk in a district youth office in Uttar Pradesh, warm morning light: wooden desk, a printed drive brief in
Hindi, a clipboard, a glass of chai, a pen, a folded hand-drawn schematic of UP districts, a phone. On the desk sits THE CREW
BOARD - the hero object: a round tray (the Fusion crew ring) with role sockets. Volunteer tokens (person silhouette on a disc),
standby pins that dock behind sockets, a red pulsing gap ring, and a READY seal (stamp with a check). These objects carry the
whole story. No government emblems, flags or tricolour; no brand logos; no real people's faces in 3D.

## Chapters (one long page; each chapter pins while its animation plays)
0. INTRO - Huge headline "इच्छुक युवा तैयार हैं। क्या यह अभियान चल सकता है?" / "Willing volunteers are here. Can this drive
   run?" Camera high above the desk, slowly descending. Scroll cue.
1. THE GAP - The phone on the desk lights up with an "Interested" list (12 names from sample-data). Copy: national platforms
   bring scale (2.22+ crore youth on MY Bharat, 1.52+ lakh opportunities, PIB 05 July 2026); the organiser still has to turn a
   list into a safe crew. Not affiliated with MY Bharat.
2. THE BRIEF - The printed Hindi brief fills the frame; key phrases highlight one by one (पोस्टर, प्राथमिक उपचार, सामान,
   स्थानीय बोली) and lift off the paper as role labels (AI proposes; organiser confirms). Interactive moment: visitor can click
   a phrase to see the role it became, with confidence.
3. THE CREW - Role sockets rise on the crew ring; volunteer tokens fly in from the list and snap into sockets (Heena P., Mohit
   Z., Divya H., Kabir Z.) with their reason chips. Fair rotation and newcomer tags appear. Interactive moment: hover a token
   to see why it was picked.
4. THE BENCH - Standby pins dock behind sockets (Imran B. behind Poster team and Local-language liaison; Kavya L. behind
   Supplies). First-aid socket has no standby: it glows amber "no standby yet". Safety note: first aid only accepts host-checked
   skills (a small check badge animates onto Mohit Z.'s token).
5. THE VERDICT - The READY seal drops and stamps the brief. Giant "READY / तैयार". Then a second drive slides in (Blood
   donation camp, Chinhat, Lucknow): the ring has two empty red pulsing gaps -> "NOT READY: 2 more community mobilisers, Sunday
   morning, within 25 km" with a copy/share chip.
6. WHAT IF SOMEONE DROPS - Interactive moment: a "Drop Heena P." button; her token lifts away, Imran B.'s standby pin slides
   into the socket, and the honest result appears: the gap is healed, but Imran B. is now a single point of failure -> the
   verdict turns NOT READY with 1 recruit request. (Use the real API text.)
7. AFTER THE DRIVE - The camera moves to the clipboard: host notes become contribution cards; one card (Kabir Z. 8 h vs 5 h
   recorded) gets a flag; a host stamp confirms the others. Then cards link into a chain of blocks (the ledger) with short
   hashes; "chain verified".
8. THE NUMBERS - Calm full-width section: ready on 7 of 10 synthetic drives vs 1 of 10 for nearest-skill; same readiness as a
   careful organiser with fewer repeat picks (23% vs 43%); under 0.33 s for 500 volunteers; 93% role recall on one free GPU.
   Numbers count up on scroll. Short honest-limits list.
9. TRY IT - The camera pulls back to the whole desk; CTA "Open the organiser console" (the working app) and "Volunteer view".
   Footer: Synthetic data; Not affiliated with MY Bharat or any government body.

## Video inserts (generated with Gemini/Veo; illustrative, labelled as such)
V1 intro ambience: slow top-down push-in over a warm wooden desk with a Hindi brief, chai glass and a round tray, morning light.
V2 community moment: young volunteers setting up a village water-and-hygiene awareness camp (posters, a handwashing station),
   seen from behind or at a distance, no identifiable faces, no logos or flags.
V3 the stamp: macro shot of a rubber stamp pressing onto paper (no readable words), dust in the light.
V4 the phone: a phone on a desk receiving a short message notification (screen content abstract, no app logos).
Each clip 5-8 s, 16:9, calm camera, cohesive warm grade. Videos are mood inserts; product facts are always rendered as real UI.

## Images (generated; textures and stills)
I1 wooden desk top texture (seamless, top-down, warm). I2 paper texture (off-white, slight fibre). I3 a hand-drawn ink map
style of Uttar Pradesh district outlines on paper (schematic, no labels baked in, no flags/emblems). I4 hero still of the
complete desk scene for the no-WebGL / reduced-motion fallback. I5 open-graph share image 1200x630 with "SewaCircle Ready
Crew" as the only text.
