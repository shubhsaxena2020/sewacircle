# SewaCircle front-end report

## 3D and motion

### Deliverables

- Six original Fusion 360 components, named and exported by [`SewaCrewKit.py`](../../design/fusion/SewaCrewKit/SewaCrewKit.py): `volunteer_token`, `role_slot`, `standby_node`, `gap_marker`, `ready_seal`, and the six-position `crew_ring`. The checked-in manifest does not auto-run.
- Six optimized GLBs in [`frontend/public/models`](../../frontend/public/models/), totaling **47,112 bytes**. [`PROVENANCE.md`](../../frontend/public/models/PROVENANCE.md) records dimensions, export settings, conversion commands, and individual sizes. A locally generated HDR is 8,239 bytes. Individual preview PNGs and a gallery are in [`docs/screens/v4/models`](../screens/v4/models/).
- The landing page uses these meshes in a lazy React Three Fiber scene: incoming instanced volunteer tokens, recessed role slots, standby nodes, a pulsing gap, and a READY seal. The camera follows the pointer and scroll gently. Local environment lighting, contact shadows, and restrained bloom provide depth. DPR is capped at 1.5.
- The 8-second seamless [`hero-loop.mp4`](../video/hero-loop.mp4) and [`hero-loop.webm`](../video/hero-loop.webm), plus the 60-second [`product-explainer.mp4`](../video/product-explainer.mp4), were rendered from the independent [`design/motion`](../../design/motion/) Remotion project. English captions are burnt into the explainer. English and Hindi caption tracks are [`product-explainer.en.vtt`](../video/product-explainer.en.vtt) and [`product-explainer.hi.vtt`](../video/product-explainer.hi.vtt). No music or voice is used. The three video files total **13,391,592 bytes**, under 20 MB.
- A captured [`hero-still.webp`](../../frontend/public/models/hero-still.webp) serves reduced motion, reduced data, and phone layouts. On a wide screen without WebGL, the loop plays over the same poster. No fallback depends on a remote asset.
- Motion drives the hero text reveal, live evaluation counters, and existing console transitions. The evaluation view has five Recharts graphs with asymmetrical error whiskers calculated from the API's reported 95% confidence limits. Values and limits remain available in adjacent text.

### Research and choices

| Choice | Version and licence | Reason and source |
| --- | --- | --- |
| Autodesk Fusion API | Installed Fusion 360; Autodesk terms apply | [`ExportManager`](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_ExportManager.htm) documents OBJ, STL, 3MF/C3MF, and USD options. [`createOBJExportOptions`](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_ExportManager_createOBJExportOptions.htm) supports per-component export; [`OBJExportOptions`](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_OBJExportOptions.htm) exposes mesh refinement. The model uses [sketch/extrude](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_ExtrudeFeatureInput.htm) and [fillet radius edge sets](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/fusion_FilletEdgeSetInputs_addConstantRadiusEdgeSet.htm). |
| React Three Fiber / drei | 9.8.2 / 10.7.9; MIT | [`useGLTF`](https://drei.docs.pmnd.rs/loaders/gltf-use-gltf) loads the local GLBs. Instanced tokens and capped DPR follow [R3F performance guidance](https://r3f.docs.pmnd.rs/advanced/scaling-performance). |
| React postprocessing / postprocessing | 3.2.2 MIT / 6.39.6 Zlib | A single bloom pass lights the READY state; no depth of field is used because the text must stay crisp. [Project and licence](https://github.com/pmndrs/react-postprocessing). |
| Motion | 14.14.0; MIT | One motion system handles UI reveals and counters; [`useReducedMotion`](https://motion.dev/docs/react-use-reduced-motion) and CSS media queries respect user settings. GSAP and Lenis were unnecessary. |
| Recharts | 3.11.0; MIT | Its [`ErrorBar`](https://recharts.github.io/en-US/api/ErrorBar/) accepts distances from a point estimate, so the chart computes the lower and upper distances from real API bounds. [Licence](https://github.com/recharts/recharts/blob/main/LICENSE). It is lazy only in the console evaluation step. |
| Lucide | 1.75.0; ISC | Existing icon set, retained. Radix was not added because native controls covered the current interactions. |
| Remotion / CLI | 4.0.518; Remotion licence | Code-native video rendered separately from the site. Remotion's [pricing/licence](https://www.remotion.dev/docs/license/pricing) permits free use for individuals, teams of up to three, and nonprofits; other use may require a licence. [Render API](https://www.remotion.dev/docs/render). |
| obj2gltf / glTF Transform CLI | 3.2.0 / 4.5.1; invoked via npx | Converts Fusion's low-refinement OBJ output and optimizes it with meshopt. Exact commands are in the model provenance. |

The [Fusion add-in manifest guidance](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-9701BBA7-EC0E-4016-A9C8-964AA4838954) informed the temporary `runOnStartup` copy. Fusion wrote `result.json` with `ok: true` and six OBJ files totaling 675,155 bytes. The temporary add-in files were removed after export, and only the Fusion PID launched for this task was stopped. The exported geometry is original and carries no government or third-party identity. The web scene assigns materials at render time, keeping the meshes tiny.

### Reproduce the video

From `design/motion`, run `npm ci`, `npm run render:hero`, and `npm run render:explainer`, one render at a time. The WebM fallback was produced with FFmpeg from the hero MP4. The project reads actual app captures in `docs/screens/v4` as its `public-dir`; the hero loop uses `docs/screens/v4/models/hero-ready.png`. The loop's scale and glow are periodic over 192 frames at 24 fps. The explainer has eight 7.5-second sections at 24 fps.

### Verification

Executed on the `frontend-v2` branch with the existing local API at `127.0.0.1:8000`:

```text
npm run build       exit 0; vite v8.3.8, 3592 modules, built in 1.13s
npm run lint        exit 0; oxlint
npm run test        exit 0; 3 test files, 7 tests passed
npm run test:e2e    exit 0; 6 passed (34.2s)
```

The Playwright suite covers live and mock organiser flows, phone pages with axe, keyboard preferences, reduced motion, WebGL fallback, and the absence of the `CrewScene` chunk on non-landing routes. Every page was captured at 1440x900 and 390x844 in [`docs/screens/v4`](../screens/v4/), then visually checked. The evaluation screenshots waited for all 20 interval whiskers to render.

Lighthouse 13.6.0, local production preview, simulated mobile and desktop. Raw audits are in [`docs/v4/lighthouse`](lighthouse/):

| Route | Profile | Performance | Accessibility | Best practices | SEO | 3D requests |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `/` | Mobile | 94 | 100 | 100 | 100 | 0 (static hero) |
| `/` | Desktop | 90 | 100 | 100 | 100 | 8 |
| `/console` | Mobile | 94 | 100 | 100 | 100 | 0 |
| `/console` | Desktop | 100 | 100 | 100 | 100 | 0 |

All four cumulative layout shift values were below 0.001. The 3D `CrewScene` chunk is 323.57 kB gzip and loads only on wide landing views. The console entry and shared chunks remain under the roughly 350 kB gzip target before the evaluation chart is requested. Vite warns that the lazy 3D chunk exceeds 500 kB uncompressed.

### Limits

The 3D interaction is intentionally static on phone and reduced-data settings to protect load time. The video and screenshots show synthetic app data; they are not field evidence. The Remotion licence depends on the eventual user's eligibility. The Fusion design is reproducible from the script and OBJ export; it is not a native `.f3d` archive. Lighthouse scores are from one local run per profile and can vary by machine.

The automatic approval review rejected removal of the now-empty temporary Fusion add-in directory under `%APPDATA%`. Its Python and manifest files were removed, so it cannot auto-run. Seven screenshot paths were already modified when this task began; the Playwright captures refreshed them locally, but those files remain unstaged to avoid committing pre-existing work without review. The unrelated `backend/` and `docs/lanes/` worktree files were not touched.
