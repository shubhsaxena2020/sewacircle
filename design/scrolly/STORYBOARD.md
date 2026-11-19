# SewaCircle Ready Crew - storyboard v2: a LIVE, interactive paper-craft village (three.js)

## Why v2
The owner's point: oryzo.ai feels alive because it is real-time WebGL (built on three.js), not video. Videos can only play.
So the experience is a real-time 3D world in the browser that responds to scroll, pointer and clicks, and calls the live API.
We do NOT copy oryzo's desk/product-macro look. Our world is ORIGINAL: a handcrafted paper-cut diorama of a village in Uttar
Pradesh. The owner's own Gemini clip (media/video/c1.mp4, frames c1-frame-*.jpg) is the ART-DIRECTION REFERENCE for the look:
layered matte paper, terracotta roofs, mustard fields, a paper river, a hand water pump, a wooden notice board, warm low sun.

## The world (rendered live with react-three-fiber / three.js)
- Built from paper layers: extruded 2D shapes (three ExtrudeGeometry from SVG paths, small depth, tiny bevel) with a paper
  texture (media/images/paper.jpg) and slightly varied paper colours: indigo, terracotta, turmeric, leaf green, off-white.
- Soft real-time shadows between layers (directional sun + shadow map or baked AO), gentle tilt-shift depth of field.
- A sun that moves with scroll: dawn -> noon -> dusk -> night across the chapters (light colour, direction and sky gradient).
- Faceless paper figures for people (a capsule body + round head cut from paper, simple idle bob).
- The crew ring: a paper ring with role sockets that floats above the square (the hero object of the story). Its parts can be
  the Fusion 360 kit (design/fusion/SewaCrewKit) re-exported, or modelled procedurally - whichever looks better in paper.
- Everything performant: instancing for figures and crops, one draw-call-friendly material set, DPR cap, < 3 MB of 3D/textures.

## Chapters (one continuous scroll; a camera spline flies through the diorama; each chapter pins while it plays)
0. INTRO - the c1 clip plays full-bleed while the 3D loads (labelled "Illustrative"), then cross-fades into the live diorama at
   the same framing. Huge headline "इच्छुक युवा तैयार हैं। क्या यह अभियान चल सकता है?" / "Willing volunteers are here. Can this
   drive run?" Pointer parallax on the layers.
1. INTEREST - the camera settles on the notice board; a paper notice pins itself; twelve paper figures walk in from the lanes
   (names from the API volunteers who opted in to task-01); a warm dot over each. HOVER a figure: a small paper tag with name,
   age, skills (checked vs self-declared). Copy: national platforms bring scale (2.22+ crore youth on MY Bharat, 1.52+ lakh
   opportunities, PIB 05 July 2026); the organiser still has to turn a list into a safe crew. Not affiliated with MY Bharat.
2. THE BRIEF - the notice shows the real Hindi brief as crisp HTML/troika text on paper; phrases highlight one by one and lift
   off as paper role chips (Poster team, First-aid support, Supplies and site setup, Local-language liaison - from the API
   extraction, with confidence). CLICK a phrase: its chip flips to show "AI proposed, you confirm".
3. THE CREW - the crew ring rises above the square; CLICK "Plan the crew" (or scroll on) -> calls POST /api/roster live and
   animates the REAL picks: the assigned figures float up and settle into sockets with a paper "click"; reason chips (Not
   picked in 90 days, Newcomer, distance) unfold beside each. HOVER a seated figure for the full reason list.
4. THE BENCH - standby figures dock behind the sockets they cover (real standby data); the First-aid socket has no standby and
   glows amber "no standby yet"; a small host-check badge stamps onto the first-aid figure (safety roles need host-checked skills).
5. THE VERDICT - the ring warms to turmeric gold and a paper seal with a raised check presses onto it with marigold petals:
   READY / तैयार. Then the camera pans to a second village (Blood donation camp, Chinhat, Lucknow): two red pulsing empty
   sockets -> NOT READY + "2 more community mobilisers, Sunday morning, within 25 km" with a working copy/share button.
6. WHAT IF SOMEONE DROPS - a "Drop a volunteer" control (pick any seated figure) calls POST /api/roster/dropout live: that figure
   walks away, the standby slides in, and the honest verdict shows (healed, but now a single point of failure -> NOT READY with
   the real recruit request).
7. THE DRIVE AND THE EVIDENCE - time-lapse: the sun arcs, figures work at the pump and posters; at dusk paper cards float from
   each figure to a host figure with a lantern; one card (8 h claimed vs 5 h recorded) shows a flag; the cards link into a chain
   of glowing paper blocks (the ledger) - CLICK "Verify" calls GET /api/ledger/verify live.
8. MANY VILLAGES - the camera pulls up: the village becomes a point on the paper map of UP (media/images/up-map.png, labelled
   "Illustrative map"); pins from GET /api/geo/tree + GET /api/drive/status light up (ready / not ready / not computed). CLICK a
   pin for its drive. The numbers from GET /api/eval count up: ready 7/10 vs 1/10, repeat picks 23% vs 43%, < 0.33 s for 500
   volunteers, 93% role recall on one free GPU. Honest limits list.
9. TRY IT - night; lanterns glow; CTAs into the working console and the volunteer view. Footer: Synthetic data; Not affiliated
   with MY Bharat or any government body.

Reduced motion / no WebGL: a calm static page with the stills and the same text and real data; no scroll scrubbing.
