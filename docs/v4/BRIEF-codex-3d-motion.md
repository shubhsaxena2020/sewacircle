# Brief for Codex (gpt-6-sol, one session): 3D assets from Fusion 360 + motion design, integrated into the SewaCircle front end

Claude Code is the head and reviews everything. Owner instruction: make the front end "10x better" using Fusion 360 for 3D
modelling, motion design, and multiple effects/component libraries, with deep research behind every choice. Quality first.

## HARD RULES
1. Work INLINE in this one session. No sub-agents, workers or other models.
2. Branch `frontend-v2` in `C:\Users\shubh\Projects\sewacircle`. Commit locally in logical commits. Do not push. Do not edit
   `backend\`. Never kill processes by image name; stop only PIDs you started.
3. RAM is tight (~6-7 GB free). Run ONE heavy process at a time (Fusion, vite build, Playwright, Remotion render: never two).
   Close Fusion when its export is done.
4. All original work. Do not copy MY Bharat or any brand's design, assets or code. No government emblems, flags or logos.
   No invented numbers (same "Allowed numbers" list as docs\v4\BRIEF-codex-frontend.md).
5. Keep the existing build, unit tests, lint and Playwright suite green; extend them.

## Part A - 3D assets modelled in Fusion 360 (installed, signed in)
Fusion 360 is at `%LOCALAPPDATA%\Autodesk\webdeploy\production\<hash>\Fusion360.exe`. It has a Python API. A previous project ran a
Fusion script unattended by installing it as an add-in with `"runOnStartup": true` in its manifest under
`%APPDATA%\Autodesk\Autodesk Fusion 360\API\AddIns\<Name>\` (see `C:\Users\shubh\Projects\DeskBuddy\cad\fusion\` and
`C:\Users\shubh\Projects\DeskBuddy\research\08_fusion360_model_spec.md`). Fusion UI automation by keystrokes did NOT work; use the
API add-in route.
1. Research the current Fusion API (adsk.fusion: sketches, extrude/revolve/fillet/shell, appearances; ExportManager options such as
   OBJ/STL/USD/3MF that this installed version supports). Use official Autodesk docs; cite URLs.
2. Write `design\fusion\SewaCrewKit\SewaCrewKit.py` (+ manifest) that parametrically models an original, cohesive 3D kit that
   explains the product: a volunteer token, a role-slot puck/socket, a standby node, a "gap" marker, a READY seal/crest, and one
   hero composition (e.g. a crew ring of slots). Soft, filleted, product-design quality forms; sensible real-world scale; low poly
   count suitable for the web. One component per part, named.
3. Run it unattended (temporary runOnStartup add-in that builds, exports each part, writes a done-marker file, then exits Fusion
   if the API allows; otherwise stop the Fusion PID you started after the marker appears). Remove the temporary add-in afterwards.
4. Convert exports to optimized glTF binary (`.glb`) with npm tools (e.g. obj2gltf + @gltf-transform/cli 4.x already available via
   npx: weld, simplify if needed, draco or meshopt compression). Put them in `frontend\public\models\` with a
   `PROVENANCE.md` (Fusion script, parameters, export settings, conversion commands, file sizes). Target < 300 kB total.
5. Render a preview PNG of each part (three.js offscreen or Fusion viewport capture) into `docs\screens\v4\models\` and inspect them.

## Part B - Use the models in the site (react-three-fiber)
Replace the procedural hero shapes in `CrewScene.tsx` with the Fusion models (drei useGLTF, instancing for tokens), keeping the
story: tokens stream in, snap into role slots, a standby node lights behind each essential role, a gap pulses until a recruit fills
it, then the crest turns READY. Research and use well-chosen effects: @react-three/postprocessing (bloom, SMAA, subtle
depth-of-field or N8AO), environment lighting (drei Environment with a bundled local HDR, no remote fetch), contact shadows,
camera rig on scroll. Pin exact versions. Keep: lazy-loaded only on the landing page, DPR cap, reduced-motion and no-WebGL fallback
(a pre-rendered still of the hero), no layout jank.

## Part C - Motion design
After Effects is NOT installed on this machine; do not try to install it. Use code-native motion instead:
1. In-site motion: research and apply a coherent motion system (durations, easings, stagger) with `motion` (already installed),
   and GSAP 3 + ScrollTrigger only if it adds something motion cannot (GSAP is free incl. plugins since 2025; verify the licence
   page and cite it). Smooth scroll (Lenis) only if it does not break accessibility or reduced-motion. Animated number counters for
   live evaluation figures, text reveals, section transitions, crew-board micro-interactions, verdict state change animation.
2. Motion pieces with Remotion: `C:\Users\shubh\Projects\OpenMontage\remotion-composer` has a working Remotion setup. Create a
   separate Remotion project at `design\motion\` (do not modify OpenMontage) that renders (a) a 6-10 s seamless hero loop
   (webm + mp4, used as the no-WebGL / reduced-data fallback poster) and (b) a 60-90 s product explainer cut from real app
   screenshots in docs\screens\v4 with captions in English (and a Hindi caption track), no voice needed, no music unless
   royalty-free and credited. Output to `docs\video\`. Keep total < 20 MB.
3. Component libraries: research and adopt where they genuinely help, with licences checked: e.g. Radix UI primitives (dialog,
   tabs, tooltip, toggle-group) for accessible behaviour, a charting library for the evaluation and fairness views (e.g. visx or
   Recharts) with confidence intervals drawn honestly, lucide icons (installed). Avoid dumping in kits that fight the design.

## Part D - Verify and report
- build, lint, vitest, full Playwright suite (live + mock + phone + axe) green; paste real output.
- Lighthouse (npx lighthouse, mobile + desktop) for / and /console; report scores; console route must not download the 3D chunk.
- New screenshots for every page (1440x900 and 390x844) and look at each one.
- Append a section "3D and motion" to `docs\v4\FRONTEND-REPORT.md`: research URLs, libraries+versions+licences, Fusion script and
  export pipeline, asset sizes, render commands, honest gaps.
