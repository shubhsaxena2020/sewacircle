# Image Generation Provenance

This document records the provenance, prompts, parameters, and generation outcomes for the SewaCircle scroll story assets specified in `STORYBOARD.md`.

| File Name | Tool & Model Used | Exact Prompt | Size / Aspect Ratio | Status / Outcome |
| :--- | :--- | :--- | :--- | :--- |
| `desk-wood.jpg` | Gemini MCP (`gemini-generate-image`) / `gemini-3-pro-image` | `Seamless top-down warm wooden desk surface texture, high resolution timber grain, rich warm teak wood finish, soft natural morning sunlight illumination, flat lay texture, completely empty surface, no objects, no vignette, repeating tileable pattern` | 4K (1:1) | **Failed**: API quota exceeded (HTTP 429 - `generativelanguage.googleapis.com/generate_content_free_tier_requests` limit is 0 on Free Tier). |
| `paper.jpg` | Gemini MCP (`gemini-generate-image`) / `gemini-3-pro-image` | `Seamless off-white paper texture with subtle fibres, no text` | 4K (1:1) | **Failed**: API quota exceeded (HTTP 429 - `generativelanguage.googleapis.com/generate_content_free_tier_requests` limit is 0 on Free Tier). |
| `up-map.png` | Gemini MCP (`gemini-generate-image`) / `gemini-3-pro-image` | `A hand-drawn ink line illustration of the district outlines of the Indian state of Uttar Pradesh on off-white paper, schematic, no labels, no text, no flags, no emblems` | 4K (1:1) | **Failed**: API quota exceeded (HTTP 429 - `generativelanguage.googleapis.com/generate_content_free_tier_requests` limit is 0 on Free Tier). |
| `hero-desk.jpg` | Gemini MCP (`gemini-generate-image`) / `gemini-3-pro-image` | `16:9 photoreal top-down view of an Indian district office desk in warm morning light: a printed paper brief with Hindi handwriting-like lines (no readable words), a glass of chai, a pen, a clipboard, a phone face down, and in the centre a round wooden tray with six circular sockets holding small rounded tokens. No people, no logos, no flags, no emblems.` | 4K (16:9) | **Failed**: API quota exceeded (HTTP 429 - `generativelanguage.googleapis.com/generate_content_free_tier_requests` limit is 0 on Free Tier). |
| `og-share.jpg` | Gemini MCP (`gemini-generate-image`) / `gemini-3-pro-image` | `Warm editorial image of an Indian district youth office desk in soft morning light with a printed paper brief, glass of chai, pen, clipboard, phone face down, and a round wooden tray with six circular sockets holding small rounded tokens. With the words SewaCircle Ready Crew in clean type as the only text. 1200x630 banner composition.` | 4K (16:9, target 1200x630) | **Failed**: API quota exceeded (HTTP 429 - `generativelanguage.googleapis.com/generate_content_free_tier_requests` limit is 0 on Free Tier). |

### Error Details
All generation attempts returned HTTP 429 `RESOURCE_EXHAUSTED` from the Google Generative Language API:
- **Error Code**: `429 RESOURCE_EXHAUSTED`
- **Metric**: `generativelanguage.googleapis.com/generate_content_free_tier_requests` (limit: 0 for `gemini-3-pro-image` on Free Tier)
- **Retry Window**: Suggested retry delay was approximately ~4 hours, or requires an active billing plan / paid tier API key with image generation quota enabled.
