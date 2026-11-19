# Head review notes - frontend-v3 (Claude Code)

## Generated stills (Codex, 10:04)
- hero-desk.jpg: on-brief and strong (warm desk, clipboard, chai, folded map, crew tray with person tokens). No logos/flags/text.
  Check: the tray centre has a carved petal medallion; confirm it does not read as the Ashoka Chakra (24 spokes) - it should
  stay clearly floral, or remove it.
- up-map.png: schematic ink outline, boundaries NOT accurate -> label "Illustrative map" wherever used; real positions from data.
- og-share.jpg: 8 tokens in a 6-socket story; title text must be overlaid in code (none baked in).

## First look at Codex's work-in-progress screenshots (11:20)
Structure is right: 11 chapters, pinned bilingual-ready copy cards, progress rail with labels, live "Plan the crew" button,
console / districts / method / share / volunteer pages exist. Copy is strong ("Many say yes. Then what?", "Make a circle that can
hold.", "Every seat needs a second plan.", "A real exit. A real re-plan.", "Work leaves a paper trail.").
Gaps against STORYBOARD v2 (to send back if the final build still has them):
1. The 3D village does NOT look like paper craft: flat untextured low-poly (cone trees, plain tiles, a grey disc, a blank board),
   desaturated haze; nothing like the film (paper.jpg texture, layered cut-paper edges, terracotta roofs, warm sun).
2. The copy card covers ~half the frame on every chapter, so the 3D scene is a background, not the hero.
3. Chapters look identical: the camera barely moves and the day-cycle (dawn -> dusk -> night) is not visible.
4. The film appears as a small thumbnail inside the card; it should be a full-bleed transition between chapters.
5. The finished 58.8 s film (design/scrolly/media/video/sewacircle-film-web.*) exists now; use it.

## Head review of commits 6619fbe + cfc0ba8 (11:55)
Verified: live story dropout, console extraction -> crew -> share link, evidence revision/redraft/confirm/correct, ledger verify,
role switch with 403, districts, volunteer, mock (0 API calls), reduced motion + no-WebGL fallbacks, axe 0 violations (en + hi),
Lighthouse story 78/100/100/83, console 100/100/100/82, npm audit 0. Live /api/eval = cp_sat ready 0.70, repeat 0.23.

Must fix (round 2):
A. chapter-00-intro capture is BLANK WHITE (first impression).
B. Numbers chapter shows 67% / 10% / 22% / 39% - the counters were captured mid-animation; final values must be 70 / 10 / 23 / 40
   and screenshots must wait for final values.
C. The 5 visual gaps from the first look are still present (flat untextured low-poly, not paper; copy card covers half the
   frame; chapters look the same, no visible day cycle; film only as a thumbnail; finished film not used - only c1-c5 used and
   c6-c9 "absent" although sewacircle-film-web.mp4 covers the whole story).
D. Fusion 360 was not used (procedural only) - acceptable if the procedural paper look is reached; otherwise use it.
E. Story Lighthouse performance 78 (TBT 440 ms) - lazy-load the film, defer non-visible chapter work.
