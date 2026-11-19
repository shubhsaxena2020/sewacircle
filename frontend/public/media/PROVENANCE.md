# Frontend media provenance

`sewacircle-film-web.webm` and `.mp4` are direct copies of the owner's finished film at `design/scrolly/media/video/sewacircle-film-web.*`. The story plays six time ranges from that one source (0–10, 10–20, 20–30, 30–38.8, 38.8–48.8 and 48.8–58.8 seconds). The film is muted, skippable, labelled Illustrative, and retains its Gemini watermark. Each transition waits until it is near the viewport before requesting the video; its poster is a frame from the corresponding range.

The six `film-poster-*.jpg` files were sampled from the source film at 5, 15, 25, 35, 45 and 55 seconds. They are loaded before their video as the visible fallback. `paper.jpg` and `village-poster.jpg` are copies of the reviewed generated stills. `up-map.webp` is a web-optimized copy of the illustrative source map in `design/scrolly/media/images/up-map.png`.

Earlier `intro.*` and `c2.mp4` through `c5.mp4` files remain in this folder from round 1 but are no longer referenced by the story. No c6–c9 fallback slots remain in the UI. The film supplies mood and transitions only; it does not provide interaction or application data.
