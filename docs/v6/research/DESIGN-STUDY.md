# SewaCircle website - design study (19 Nov 2026)

## What was studied
- 200 sites: 170 latest Awwwards "Site of the Day" winners (collected from awwwards.com, each site's real URL) + 30
  all-time references (Lusion, Igloo, Bruno Simon, Apple product pages, Linear, Stripe, oryzo, charity: water,
  The Ocean Cleanup, The Pudding, Our World in Data, ...).
- Each site opened at 1440x900 in Chromium, 5 frames (hero + 4 scroll positions) and a signature (WebGL, GSAP, video,
  max font size, fonts, background, page length). 185 loaded; 15 blocked by bot walls or "browser not supported".
- Every frame reviewed by eye: NOTES.md has the per-site observations. Contact sheets: review/*.jpg. Raw: scan-*.json.

## Numbers (116 full content sites)
| Measure | Value |
|---|---|
| Largest type on the page | median 112 px (middle half 72-195 px) |
| WebGL canvas present | 48% |
| Video present | 64% |
| Light / dark background | 52% / 46% |
| Page length | median 13 screens |
| Typefaces | sans dominant; most pair a grotesk with a mono or a serif accent; never more than 2-3 faces |
| Awwwards tags (170) | GSAP 56%, WebGL 41%, three.js 31%, Storytelling 26%, Typography 24% |

## The patterns that separate the best from the rest
1. One idea per screen: one statement (3-8 words) + one visual. No boxed paragraphs over busy backgrounds.
2. Type is the main visual: 100-300 px headlines, tight leading, often with an image or object breaking through the letters.
3. One hero object or metaphor carried through the whole scroll (oryzo's coaster, Igloo's igloo, Steven.com's ring dial,
   Agrumea's circle). The object changes state as the story moves; the page does not swap scenes every chapter.
4. Crisp material beats soft imagery: flat cut-paper and collage (Sweet Tape, Aardvark, Decathlon) or real photography;
   upscaled AI video frames behind text read as blurry.
5. Big numbers as visuals (Nick Ho "98", Zirka "224", Truck'N Roll "70+ / +140 / 100%").
6. Impact storytelling = a human + one big fact + one action (charity: water "696 million people lack...").
7. Restraint: one accent colour, 2 typefaces, generous empty space, a fixed minimal nav, no clutter labels.
8. Interaction is a toy you want to touch (Bruno Simon's car, Don't Look Up's crowd), not a form.

## Why the current SewaCircle site fails these tests
- Every chapter stacks: a boxed text card with a paragraph, a film backdrop, up to 8 name tags, a progress rail, an
  "Illustrative" label and a scroll hint -> no single focal point.
- Headlines ~60 px inside a card; best sites use ~112 px median and let type carry the screen.
- The backdrop changes every chapter (7 film stills) instead of one object evolving.
- The film frames are 1280x720 AI video, soft when stretched to 1440+; the live 3D ring added on top looked plastic.

## Video model on Kaggle (tested, not assumed)
Wan 2.2 TI2V-5B on Kaggle's free T4 with a 4-bit transformer: 2.0 s of 832x480 video took 35 min; 1.4 s of 704x384
took 16 min; peak 11.7 GB VRAM. Paper look acceptable, people malformed. With ~30 GPU-hours/week that is ~50 short clips
per week at below-Veo quality, so it is not a Higgsfield substitute. The provided notebook runs Unsloth Studio (text-LLM
chat/fine-tuning), which cannot generate video. Decision: the new site does not depend on generated video.

## Three directions (mockups in mockups/, screenshots in mockups/shots/)
- A. Cut-Paper Bold: flat saturated cut paper (turmeric, terracotta, indigo), giant condensed bilingual type, a marigold
  ring made of paper petals, tiny paper people you can drag into seats. Warm, Indian, playful. (Sweet Tape, Crav,
  Aardvark, Don't Look Up, Agrumea)
- B. The Ring: dark and cinematic; one real-time 3D ring (brass/marigold material) is the only object; seats light up as
  the solver fills them; white type at 160-240 px. Premium tech. (oryzo, Igloo, Steven.com, Moto)
- C. Field Report: warm off-white editorial; huge numbers and serif/grotesk pairing; volunteers drawn as dots that flock
  into crews; charts are the hero. Credible, judge-friendly. (charity: water, The Pudding, OWID, Apple)
