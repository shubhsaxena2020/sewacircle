# Frontend media provenance

`sewacircle-film-web.webm` and `.mp4` are direct copies of the owner's finished film at `design/scrolly/media/video/sewacircle-film-web.*`. The story plays six time ranges from that one source (0–10, 10–20, 20–30, 30–38.8, 38.8–48.8 and 48.8–58.8 seconds). The film is muted, skippable, labelled Illustrative, and retains its Gemini watermark. Each transition waits until it is near the viewport before requesting the video; its poster is a frame from the corresponding range.

The six `film-poster-*.jpg` files were sampled from the source film at 5, 15, 25, 35, 45 and 55 seconds. They are loaded before their video as the visible fallback. `paper.jpg` and `village-poster.jpg` are copies of the reviewed generated stills. `up-map.webp` is a web-optimized copy of the illustrative source map in `design/scrolly/media/images/up-map.png`.

Earlier `intro.*` and `c2.mp4` through `c5.mp4` files remain in this folder from round 1 but are no longer referenced by the story. No c6–c9 fallback slots remain in the UI. The film supplies mood and transitions only; it does not provide interaction or application data.

## Round 4 film-layer backdrops

The chapter backdrops are derived from the owner's `design/scrolly/media/video/sewacircle-film-master.mp4` (1280x720, 24 fps). The following full-resolution source frames were extracted with ffmpeg and retained under `docs/screens/v5/round4/source-frames/`:

| Frame set | Source time | Chapters |
|---|---:|---|
| `dawn-board` | 00:00:04.500 | Intro and brief |
| `youth-gather` | 00:00:13.500 | Interest |
| `turmeric-ring` | 00:00:24.500 | Crew |
| `crew-backups` | 00:00:33.500 | Bench |
| `ready-seal` | 00:00:43.500 | Verdict and dropout |
| `drive-evidence` | 00:00:52.500 | Evidence |
| `map-night` | 00:00:57.800 | Districts, numbers, and try-it |

Each frame has four WebP depth images: an unchanged full-frame base plus transparent sky, mid-village, and foreground cutouts. Hand-authored, gently wavy horizontal masks are feathered by 8 px; the base remains uncut behind every layer, so the small parallax offsets never reveal empty gaps and no inpainting is needed. The masks span approximately 36% for sky, 19-77% for mid-village, and 59-102% for foreground. WebP quality is 68. The full-frame base retains the source Gemini watermark; the page keeps an `Illustrative` label over the layered scene and in every film transition.

`frontend/scripts/generate-film-layers.py` reproduces the masks and WebP files from the retained source frames using Pillow. Total payload for the 28 chapter layer files is 3,462,316 bytes (3.30 MiB), below the 4 MB budget. Only the current and next chapter sets are mounted; the intro set is eager and preloaded. Reduced motion snaps between static chapter layers without scroll-scrub or parallax; no-WebGL mode shows the static dawn still.
