# Brief for Codex (gpt-6-luna, one session): frontend v3 ROUND 2 - make the story look and feel like the film

Same rules as docs\v5\BRIEF-codex-frontend-v3.md (inline only, no sub-agents, worktree C:\Users\shubh\Projects\sewacircle-v3,
branch frontend-v3, commit locally, never push, never edit backend\, one heavy process at a time, stop only PIDs you start, no
oryzo/Lusion assets). Your round-1 work (commits 6619fbe, cfc0ba8) is functionally strong and stays. Read
docs\v5\HEAD-REVIEW-NOTES.md (head review) first. This round is about the LOOK and the FEEL.

## The target look
Watch design\scrolly\media\video\sewacircle-film-web.mp4 (58.8 s, the owner's finished film) and look at its frames. The live
village must feel like that film rendered in real time: layered cut paper, visible paper fibre, soft shadows between layers,
terracotta tiled roofs, mustard fields, a paper river, a hand pump, a wooden notice board, warm low sun, faceless paper figures,
the floating turmeric ring with glowing sockets. The current scene is flat untextured low-poly in a grey-green haze: replace it.

## Must fix
1. Paper look. Build every object from extruded 2D shapes (ExtrudeGeometry from SVG-style paths, small depth, tiny bevel) with
   design\scrolly\media\images\paper.jpg as a tiling texture (plus subtle per-object colour), slightly irregular cut edges, and
   soft shadows (directional sun + PCF soft shadows or baked AO) between layers. Warm palette from the film (indigo, terracotta,
   turmeric, leaf green, off-white), no grey haze. Optional: a light tilt-shift depth of field.
2. The scene is the hero. The copy card currently covers about half the frame on every chapter: make it a compact, translucent
   paper label (max ~30% width), positioned per chapter so it never hides the action; the 3D fills the viewport.
3. Chapters must look different. A real camera path through the diorama (dawn at the notice board -> rising to the ring ->
   close on the sockets -> the second village -> the square at dusk -> high above the map at night). A visible day cycle driven by
   scroll: sky gradient, sun colour and direction, window lights and lanterns at dusk/night.
4. Use the finished film. Play sewacircle-film-web.webm/mp4 as FULL-BLEED cinematic transitions between chapters, cut by time
   ranges from design\scrolly\media\video\CLIPS-NOTES.md (the film is 6 joined clips: 0-10 dawn/board, 10-20 youth gather,
   20-30 ring forms, 30-38.8 crew + backups, 38.8-48.8 last gap + seal, 48.8-58.8 drive, evidence, map). Labelled
   "Illustrative", Gemini watermark kept, skippable, muted, lazy-loaded (do not load the film until near its chapter), poster
   frames from the film. Remove the "c6-c9 absent" fallbacks: the film covers the whole story.
5. Intro must never be blank: chapter-00 capture is blank white now. The first frame shows the film poster or the scene instantly.
6. Numbers: counters were captured mid-animation (67/10/22/39). Final values are 70 / 10 / 23 / 40 (live /api/eval). Make
   screenshots wait for final values, and make counters land exactly on the API values.
7. Performance: story Lighthouse performance is 78 (TBT 440 ms). Lazy-load the film, split the scene, defer offscreen work;
   target >= 85 desktop. Keep the console free of the 3D chunk.

## Keep
Every live interaction and test from round 1 (dropout, share, revision, role switch, districts, mock, reduced motion, no-WebGL,
axe 0 violations in both languages). Re-run them all.

## Verify and report
Append "Round 2" to docs\v5\FRONTEND-V3-REPORT.md: before/after screenshots of every chapter (docs\screens\v5\round2\), a new
slow full-scroll recording, the commands and real outputs (build, lint, vitest, full browser verification, axe en+hi,
Lighthouse / and /console), and honest remaining gaps. Look at every screenshot yourself and compare it with the film frames.
