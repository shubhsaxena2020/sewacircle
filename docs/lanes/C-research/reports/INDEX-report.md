# Audit report — `docs/research/INDEX.md` (Lane C, final synthesis)

Date 2026-11-18. Author: Lane C subagent (INDEX synthesis). All data referenced is SYNTHETIC. No external URL, figure or citation was introduced by this deliverable: every statement points at a section of an existing research file.

## 1. Deliverable

`C:/Users/shubh/Projects/sewacircle/docs/research/INDEX.md` — 8,837 characters, 48 lines. Title: `# INDEX — the ten implementation decisions for the SewaCircle build`. Structure: one-line scope + "How to use this file" line, `## The ten decisions` (10 numbered entries), `## Do not claim` (10 grouped prohibitions).

## 2. Files written

- `docs/research/INDEX.md` (owned deliverable)
- `docs/lanes/C-research/reports/INDEX-report.md` (this report)

Nothing outside `docs/research/` and `docs/lanes/C-research/` was written. One throwaway proof script lives in the Hermes scratch dir: `C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/c_index_proof.py`.

## 3. Files read (source basis)

| File | Use |
|---|---|
| `docs/research/R1-optimization.md` (291 lines) | decisions 1–4 |
| `docs/research/R2-nlp-hindi.md` (189) | decisions 5–6 |
| `docs/research/R3-credentials-privacy.md` (161) | decision 8 |
| `docs/research/R4-up-realism.md` (93) | decision 7 |
| `docs/research/R5-demo-ux.md` (150) | decision 10 |
| `docs/research/R6-eval-responsible-ai.md` (212) | decision 9 |
| `docs/research/up_districts.json` (parsed: 20 districts, 9 top-level keys, `coordinate_caveat` present) | decision 7 |
| `docs/COMMON.md` (21) | flow, integrity rules, U1–U4 framing |
| `docs/lanes/C-research/TASK.md` (15) | mandate for INDEX |
| `docs/lanes/C-research/reports/BATCH1-REVIEW.md` (first 6,000 chars) | timing-variance context (0.0134 s vs 0.0203 s on re-run) |

Nine files read in full; one review file read partially for context. Sources listed inside `INDEX.md`: 6 distinct research files, 0 external URLs (verified: `grep -n "http" docs/research/INDEX.md` → no match, exit 1).

## 4. Proof command and real output

Command (exit 0):

```sh
cd /c/Users/shubh/Projects/sewacircle && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -X utf8 C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/c_index_proof.py; echo "EXIT_CODE=$?"
```

The script parses `INDEX.md`, splits the `## The ten decisions` section, asserts exactly 10 numbered entries numbered 1..10, extracts the single `R*.md` reference from each entry block, asserts that file exists on disk, and prints titles + resolved paths.

```text
INDEX: C:\Users\shubh\Projects\sewacircle\docs\research\INDEX.md
NUMBERED_DECISIONS 10
---- decisions ----
 1. Model the roster as binary `x[v,r]` with skill, availability, commute and headcount as hard constraints, and keep "quality" only in the integer objective.
    -> C:\Users\shubh\Projects\sewacircle\docs\research\R1-optimization.md (exists=True, bytes=25473)
 2. Make single-dropout standby part of the model, not a UI afterthought: add primary `z[v,r]` + standby `s[v,r]` with, for every potential primary `w` on role `r`, `Σ_{u≠w} s[u,r] ≥ z[w,r]`; ship k=1 only and surface an infeasible robust model instead of silently dropping the guarantee.
    -> C:\Users\shubh\Projects\sewacircle\docs\research\R1-optimization.md (exists=True, bytes=25473)
 3. Implement the exposure cap as a Python branch (`prior_exposure >= cap` → `assigned == 0`) and report repeat-pick share and Gini as two separate descriptive metrics, never as one "fairness improved" number.
    -> C:\Users\shubh\Projects\sewacircle\docs\research\R1-optimization.md (exists=True, bytes=25473)
 4. Answer "why not X?" only by re-solving the base model with `Σ_r x[X,r] = 1` forced and reporting the objective delta plus displaced/added names; if the forced model is INFEASIBLE, say "no feasible roster includes X".
    -> C:\Users\shubh\Projects\sewacircle\docs\research\R1-optimization.md (exists=True, bytes=25473)
 5. Extract roles through a closed JSON schema (every property required, `additionalProperties: false`, closed enums, `count` integer ≥ 1, verbatim `evidence_span`) plus a mandatory `needs_review` abstention path, and gate CP-SAT behind our own provider-agnostic validator.
    -> C:\Users\shubh\Projects\sewacircle\docs\research\R2-nlp-hindi.md (exists=True, bytes=23644)
 6. Redact Indian PII before every model call: normalise Devanagari digits, then apply Aadhaar → phone → PAN → email → cue-based name/address patterns, merge overlapping spans, substitute `[REDACTED:CLASS]`, and log counts only — then re-run the same patterns on every emitted string.
    -> C:\Users\shubh\Projects\sewacircle\docs\research\R2-nlp-hindi.md (exists=True, bytes=23644)
 7. Generate every fixture from the verified UP registry: the 20 district points in `up_districts.json` labelled "approximate district point", block/tehsil names only from the lists R4 verified, ages 15–29, languages from the Census categories, and skills drawn from the 24-ID taxonomy (rows whose anchor is marked inferred stay labelled that way).
    -> C:\Users\shubh\Projects\sewacircle\docs\research\R4-up-realism.md (exists=True, bytes=20654)
 8. Emit the portable record with OB 3.0's exact field names, `@context` order and required list but with no `proof` field, labelled "unsigned, data-model-shaped — not a verifiable credential"; treat the hash chain the same way — tamper-evidence of appended bytes, not truth of the hours.
    -> C:\Users\shubh\Projects\sewacircle\docs\research\R3-credentials-privacy.md (exists=True, bytes=32478)
 9. Score all four methods (`cp_sat`, `nearest_skill`, `random_feasible`, `manual_greedy`) with one shared metric implementation, freeze fixtures, seeds and baseline code before the first run, and report paired seeded bootstrap intervals (10,000 resamples) always prefixed "synthetic fixture, descriptive only".
    -> C:\Users\shubh\Projects\sewacircle\docs\research\R6-eval-responsible-ai.md (exists=True, bytes=30459)
10. Rehearse the ten-segment 180-second demo against its own timings and build the UI to GIGW/WCAG basics first — ≥4.5:1 contrast, 200% zoom, 320 px reflow, `lang` per span, Devanagari-capable font stack, icon + Hindi label + English gloss, literal error text — then record at 960×540, 25 fps, one worker.
    -> C:\Users\shubh\Projects\sewacircle\docs\research\R5-demo-ux.md (exists=True, bytes=21743)
---- totals ----
DISTINCT_RESEARCH_FILES_REFERENCED 6 ['R1-optimization.md', 'R2-nlp-hindi.md', 'R3-credentials-privacy.md', 'R4-up-realism.md', 'R5-demo-ux.md', 'R6-eval-responsible-ai.md']
ALL_REFERENCED_FILES_EXIST True
INDEX_TITLE # INDEX — the ten implementation decisions for the SewaCircle build
HAS_DO_NOT_CLAIM_SECTION True
PROOF_STATUS PASS
EXIT_CODE=0
```

Supporting commands and real output:

```text
$ grep -n "http" docs/research/INDEX.md
grep_exit=1            # no match: INDEX.md introduces no external URL
$ wc -l docs/research/INDEX.md
48 docs/research/INDEX.md
$ python -c "... print('CHARS',len(t)); print('R_REFS', ...)"
CHARS 8837
R_REFS 16
```

`R_REFS 16` counts every inline mention of the six filenames: 6 in the scope line that names the source files, plus exactly 1 per decision (10 pointers). The "Do not claim" box names no research file.

## 5. The ten decision titles

1. Binary `x[v,r]` model; skill/availability/commute/headcount hard, quality only in the objective — R1.
2. Single-dropout standby as a model constraint (`z` primary + `s` standby, `Σ_{u≠w} s[u,r] ≥ z[w,r]`), k=1 only, infeasibility surfaced — R1.
3. Exposure cap as a Python branch (`prior ≥ cap` → assigned 0); repeat-pick share and Gini reported as separate descriptive metrics — R1.
4. "Why not X?" answered only by forced re-solve (delta + displaced/added, or "no feasible roster includes X") — R1.
5. Closed JSON schema + `needs_review` abstention + own validator before CP-SAT — R2.
6. PII redaction before model calls, Devanagari-digit normalisation, counts-only logging, re-check emitted strings — R2.
7. Fixtures from the verified UP registry (20 district points as "approximate district point"), verified blocks, ages 15–29, 24-ID taxonomy — R4.
8. OB 3.0 field names/`@context`/required list with no `proof`, labelled unsigned; hash chain = tamper-evidence, not truth — R3.
9. Four methods, one metric implementation, frozen fixtures, paired seeded bootstrap (10,000), "descriptive only" — R6.
10. Ten-segment 180 s demo rehearsal + GIGW/WCAG build requirements before recording at 960×540/25 fps/1 worker — R5.

## 6. Counts

- Files read: 9 in full + 1 partially (BATCH1-REVIEW.md, context only).
- Numbered decisions in INDEX: 10 (asserted by the proof).
- Distinct research files referenced: 6 (all of R1–R6; none unreferenced).
- External sources/URLs added by INDEX: 0.
- Research-topic coverage: 11 topics requested → 10 decisions, one deliberate merge (below).

## 7. UNRESOLVED

1. **11 requested topics vs 10 decision slots.** The brief listed CP-SAT shape, standby, fairness/exposure, counterfactual, schema+abstention, PII redaction, OB3 field set, hash-chain scope, synthetic realism, eval protocol and demo/accessibility = 11. OB 3.0 export honesty and hash-chain scope (both from R3) are merged into decision 8 because they share one rule — the artefact proves syntax/ordering, not accreditation or truth. Both are stated explicitly, not dropped. If the parent prefers 11 entries, the proof and the "exactly 10" requirement would have to change.
2. **R4 internal inconsistency (source-side, not introduced here).** R4's 24-skill table marks three rows `inferred` (`first_aid` #7, `crowd_safety` #14, `translation` #23), while R4's Risks section says "4 rows are explicitly inferred". INDEX therefore states "rows whose anchor is marked inferred" and quotes no count. R4's owner should reconcile 3 vs 4.
3. **Decision 9 is a target, not a current capability.** R6 recorded that `backend/eval/harness.py` raises `NotImplementedError` on 2026-11-18, so the INDEX rule prescribes the protocol the eval lane must implement; no evaluation number may be quoted until a real run prints it.
4. **Pointers are headings, not line numbers.** Sections are cited by quoted heading text (e.g. `Recommendation for our build ("Hard vs soft")`) to survive edits; renaming those headings would break the pointers' precision even though the file still resolves.
5. **No external citation is carried into INDEX by design.** Provenance stays in R1–R6; a reader who needs the URL or the exact quoted spec text must follow the pointer to the section and its Sources list.
