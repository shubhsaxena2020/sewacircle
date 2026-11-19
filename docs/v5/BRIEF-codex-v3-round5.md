# Brief for Codex (gpt-6-luna, one session): frontend v3 ROUND 5 - one ring, not two (narrow fix round)

Same hard rules as rounds 1-4 (inline only, no sub-agents, worktree C:\Users\shubh\Projects\sewacircle-v3, branch frontend-v3,
commit locally, never push, never edit backend\, one heavy process at a time, stop only PIDs you start, never by image name).
Backend :8000 and Vite :5180 are running - do not stop them. Keep this round NARROW: fix only what is listed.

Round 4 (ba0908c, e376747) is a big improvement: the film-layer backdrops look like the owner's film. The head review found:

## Must fix
1. Double rings. In crew, bench, verdict and dropout (docs\screens\v5\round4\after\chapter-03..06) the backdrop already shows the
   film's ring (and seated paper figures), and the shiny yellow 3D ring with block figures is drawn on top of it. Never show two
   rings. Approach: in chapters whose backdrop contains the film ring, REMOVE the 3D ring and block figures and make the film ring
   itself interactive with an aligned overlay:
   - per backdrop, author normalised screen-space anchor points for the film's sockets/seated figures (look at the image, record
     them in one data file); they must follow the backdrop layer's parallax transform;
   - on those anchors show the live API data: small paper tags with the volunteer name + role (from /api/roster), soft glowing
     socket highlights, hover/focus for reasons, the amber "no standby yet" glow, the host-check badge;
   - dropout: the dropped figure's anchor dims (paper-grey overlay + "left" tag), the standby's tag slides in, then the honest
     NOT READY + recruit request, all from the live API as now;
   - the READY / NOT READY seal stays a 3D or HTML paper seal, placed so it never covers a figure.
   Keyboard and screen-reader access to the same data (buttons/list), axe 0 in en+hi.
2. Where a 3D object stays (map pins, evidence cards, ledger blocks), restyle it as matte paper (paper.jpg texture, no glossy
   specular, warm colours matching the film); map pins as small cut-paper markers, not yellow torus rings.
3. Ghosting. chapter-03-crew shows faint duplicate silhouettes around the ring (layer doubling or a stale cross-fade). Remove all
   ghosting/seams in every chapter while scrolling (check mid-scroll frames too, not only anchors).
4. The verdict chapter capture shows "PLAN TO SEE": make the verification scroll trigger the live plan first so the chapter shows
   the real verdict, and keep a clear prompt if the user has not planned yet.

## Verify and report
Build, lint, vitest, npm run verify:v3, axe en+hi, Lighthouse / (>= 90) and /console. Screenshots of every chapter (anchors and
3 mid-scroll frames) into docs\screens\v5\round5\, look at each yourself, fix anything that still doubles or ghosts. Append
"Round 5" to docs\v5\FRONTEND-V3-REPORT.md with real outputs and honest gaps. Commit in logical commits.
