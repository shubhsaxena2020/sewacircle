# Video Provenance Ledger: SewaCircle Ready Crew

Generated and logged in accordance with `STORYBOARD.md` (Section: Video inserts) for the SewaCircle website.

## Overview

| Name | Tool and Model | Exact Prompt | Duration | Resolution | File Size | Status / Error |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `v1-desk.mp4` | Gemini MCP (`gemini-generate-video` / Veo `veo-2.0-generate-001`) | Cinematic 4k, calm slow top-down push-in camera movement over a warm rustic wooden Indian office desk. On the desk is a printed paper brief with unreadable Devanagari Hindi script textures, a clear glass of warm cutting chai with soft steam, a vintage wooden pen, and an artisanal round wooden tray with six carved sockets holding small wooden volunteer tokens. Soft golden morning sunlight streaming at a low angle across the desk surface, warm cohesive cinematic color grading, tranquil atmosphere, 24fps. | N/A | 16:9 (Target 1080p/4k) | 0 B | Failed (API 404: `models/veo-2.0-generate-001` not found/supported for `predictLongRunning` on API v1beta) |
| `v2-camp.mp4` | Gemini MCP (`gemini-generate-video` / Veo `veo-2.0-generate-001`) | Cinematic, young volunteers setting up a village water and handwashing awareness camp in rural Uttar Pradesh, seen from behind or at a distance, posters without readable text, a handwashing station, soft daylight, warm cohesive colour grade, calm camera, 16:9 | N/A | 16:9 (Target 1080p/4k) | 0 B | Failed (API 404: `models/veo-2.0-generate-001` not found/supported for `predictLongRunning` on API v1beta) |
| `v3-stamp.mp4` | Gemini MCP (`gemini-generate-video` / Veo `veo-2.0-generate-001`) | Cinematic macro shot of a rubber stamp pressing down onto paper, dust particles in a sunbeam, no words visible, warm cohesive colour grade, calm camera, 16:9 | N/A | 16:9 (Target 1080p/4k) | 0 B | Failed (API 404: `models/veo-2.0-generate-001` not found/supported for `predictLongRunning` on API v1beta) |
| `v4-phone.mp4` | Gemini MCP (`gemini-generate-video` / Veo `veo-2.0-generate-001`) | Cinematic, a phone lying on a wooden desk lights up with an abstract message notification, no app logos, shallow depth of field, warm cohesive colour grade, calm camera, 16:9 | N/A | 16:9 (Target 1080p/4k) | 0 B | Failed (API 404: `models/veo-2.0-generate-001` not found/supported for `predictLongRunning` on API v1beta) |

---

## Detailed Generation Records

### 1. `v1-desk.mp4`
* **Target File**: `C:/Users/shubh/Projects/sewacircle-v3/design/scrolly/media/video/v1-desk.mp4`
* **Tool Used**: Gemini MCP `gemini-generate-video`
* **Underlying Model**: `veo-2.0-generate-001` via `@google/genai`
* **Aspect Ratio**: `16:9`
* **Target Duration**: 5 to 8 seconds
* **Visual Constraints**: Calm camera, warm cohesive colour grade, morning light, no logos, no flags/emblems, no readable text, no identifiable faces
* **Exact Prompt**: `Cinematic 4k, calm slow top-down push-in camera movement over a warm rustic wooden Indian office desk. On the desk is a printed paper brief with unreadable Devanagari Hindi script textures, a clear glass of warm cutting chai with soft steam, a vintage wooden pen, and an artisanal round wooden tray with six carved sockets holding small wooden volunteer tokens. Soft golden morning sunlight streaming at a low angle across the desk surface, warm cohesive cinematic color grading, tranquil atmosphere, 24fps.`
* **Negative Prompt**: `readable text, legible letters, identifiable faces, logos, flags, emblems, tricolour, watermarks, blurry, jerky camera, fast motion`
* **Execution Result**: Error starting video generation
* **API Error Details**:
  ```json
  {
    "error": {
      "code": 404,
      "message": "models/veo-2.0-generate-001 is not found for API version v1beta, or is not supported for predictLongRunning. Call ModelService.ListModels to see the list of available models and their supported methods.",
      "status": "NOT_FOUND"
    }
  }
  ```

---

### 2. `v2-camp.mp4`
* **Target File**: `C:/Users/shubh/Projects/sewacircle-v3/design/scrolly/media/video/v2-camp.mp4`
* **Tool Used**: Gemini MCP `gemini-generate-video`
* **Underlying Model**: `veo-2.0-generate-001` via `@google/genai`
* **Aspect Ratio**: `16:9`
* **Target Duration**: 5 to 8 seconds
* **Visual Constraints**: Rural Uttar Pradesh, seen from behind or distance, posters without readable text, handwashing station, soft daylight, warm grade, no identifiable faces, no logos or flags
* **Exact Prompt**: `Cinematic, young volunteers setting up a village water and handwashing awareness camp in rural Uttar Pradesh, seen from behind or at a distance, posters without readable text, a handwashing station, soft daylight, warm cohesive colour grade, calm camera, 16:9`
* **Negative Prompt**: `identifiable faces, recognizable people, readable text, logos, flags, emblems, tricolour, watermarks, abrupt camera movements`
* **Execution Result**: Error starting video generation
* **API Error Details**:
  ```json
  {
    "error": {
      "code": 404,
      "message": "models/veo-2.0-generate-001 is not found for API version v1beta, or is not supported for predictLongRunning. Call ModelService.ListModels to see the list of available models and their supported methods.",
      "status": "NOT_FOUND"
    }
  }
  ```

---

### 3. `v3-stamp.mp4`
* **Target File**: `C:/Users/shubh/Projects/sewacircle-v3/design/scrolly/media/video/v3-stamp.mp4`
* **Tool Used**: Gemini MCP `gemini-generate-video`
* **Underlying Model**: `veo-2.0-generate-001` via `@google/genai`
* **Aspect Ratio**: `16:9`
* **Target Duration**: 5 to 8 seconds
* **Visual Constraints**: Macro shot of rubber stamp pressing onto paper, dust particles in sunbeam, no words visible, warm cohesive colour grade, calm camera
* **Exact Prompt**: `Cinematic macro shot of a rubber stamp pressing down onto paper, dust particles in a sunbeam, no words visible, warm cohesive colour grade, calm camera, 16:9`
* **Negative Prompt**: `readable words, legible text, logos, emblems, modern office plastic, digital artifacts, watermarks, faces`
* **Execution Result**: Error starting video generation
* **API Error Details**:
  ```json
  {
    "error": {
      "code": 404,
      "message": "models/veo-2.0-generate-001 is not found for API version v1beta, or is not supported for predictLongRunning. Call ModelService.ListModels to see the list of available models and their supported methods.",
      "status": "NOT_FOUND"
    }
  }
  ```

---

### 4. `v4-phone.mp4`
* **Target File**: `C:/Users/shubh/Projects/sewacircle-v3/design/scrolly/media/video/v4-phone.mp4`
* **Tool Used**: Gemini MCP `gemini-generate-video`
* **Underlying Model**: `veo-2.0-generate-001` via `@google/genai`
* **Aspect Ratio**: `16:9`
* **Target Duration**: 5 to 8 seconds
* **Visual Constraints**: Phone on wooden desk lights up with abstract message notification, no app logos, shallow depth of field, warm cohesive colour grade
* **Exact Prompt**: `Cinematic, a phone lying on a wooden desk lights up with an abstract message notification, no app logos, shallow depth of field, warm cohesive colour grade, calm camera, 16:9`
* **Negative Prompt**: `identifiable app logos, recognizable branding, readable text, legible notifications, faces, harsh reflections`
* **Execution Result**: Error starting video generation
* **API Error Details**:
  ```json
  {
    "error": {
      "code": 404,
      "message": "models/veo-2.0-generate-001 is not found for API version v1beta, or is not supported for predictLongRunning. Call ModelService.ListModels to see the list of available models and their supported methods.",
      "status": "NOT_FOUND"
    }
  }
  ```

---

## Root Cause Analysis & Diagnostic Notes
1. **API Tier & Endpoint Availability**: Google's Veo video generation models (`veo-2.0-generate-001`, `veo-3.1-generate-001`) are not available or enabled for `predictLongRunning` on the current Google AI Studio free-tier API key configured for the Gemini MCP server.
2. **Resolution Path**: To enable Veo video generation, the project requires either:
   - A Google Cloud Vertex AI project with the Veo API enabled and quota allocated.
   - An AI Studio API key with access to Google's video generation preview endpoints, with `GEMINI_VIDEO_MODEL` specified in the MCP server configuration.
