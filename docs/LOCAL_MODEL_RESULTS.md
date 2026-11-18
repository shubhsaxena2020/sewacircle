# Role extraction with a small open model on one free GPU (real output)

Question: if the cloud model is unavailable or a department cannot send text to a cloud API, can a small open model
running on one free GPU do the role extraction step?

Setup: Kaggle notebook `kaggle/gpu-extraction/sewacircle_local_llm_extraction.py` (kernel
`shubhsaxena2008/sewacircle-local-llm-extraction`), **one Tesla T4**, 4-bit quantised weights (bitsandbytes), the **same
`extract_roles` code path, prompt, redaction and scoring** as the API evaluation, the same 30 synthetic briefs
(12 Hindi, 10 English, 8 Hinglish). Raw output: `docs/kaggle_gpu_extraction_results.json`.

| Model | Where | Role recall | Role precision | Exact counts | Failures | Median s/brief |
|---|---|---|---|---|---|---|
| Claude Sonnet 5.5 | cloud API | 1.00 | 1.00 | 1.00 | 0 | (see EVAL) |
| DeepSeek v4.1 Flash | cloud API | 0.983 | - | 1.00 | 0 | - |
| **Qwen2.5-7B-Instruct, 4-bit** | **1x T4** | **0.932** | **0.917** | **1.00** | **0** | **10.7** |
| Qwen2.5-3B-Instruct, 4-bit | 1x T4 | 0.695 | 0.774 | 0.902 | 1 | 12.6 |

Qwen2.5-7B by language: Hindi recall 0.87 / precision 0.87, English 0.95 / 0.95, Hinglish 1.00 / 0.941.
Model load time: 112.8 s (7B), 44.1 s (3B).

## What this means
- A 7B open model on a single free GPU recovers about 93% of roles with exact head counts, so an offline or
  on-premise deployment is plausible. **Hindi is the weak spot** (0.87 recall).
- The 3B model is not good enough (0.70 recall); we would not ship it.
- Every role the model proposes still goes to the organiser for review (step 2 of the app), and a role with a skill we do not
  track is held as unresolved, so a missed or wrong role is visible to the organiser, never silently assigned.

## Caveats
Same as the API evaluation: the briefs were written by the team that wrote the prompt and state counts explicitly, so this is an
easy test. n = 30. No claim about real organiser text until an independently written set is scored.
