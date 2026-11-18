# R2 audit report — Lane C research

Date/time of run (command output): `Wed, Nov 18, 2026 11:18:53 PM` (from `date`). All data used in tests is **SYNTHETIC**, invented for this report; no real person, minor or identity document.

## Deliverable and files written

- Deliverable: `C:/Users/shubh/Projects/sewacircle/docs/research/R2-nlp-hindi.md` (189 lines, 23,644 bytes; exactly four `##` sections: Findings, Recommendation for our build, Risks, Sources — verified by `grep -n '^#'`).
- Audit: `C:/Users/shubh/Projects/sewacircle/docs/lanes/C-research/reports/R2-report.md` (this file; directory created with `mkdir -p`).
- Throwaway test harness (outside repo, in `$TMPDIR`): `C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r2_tests.py`; captured stdout: `.../scratch/r2_tests_output.txt`.
- Read-only inputs: `docs/COMMON.md`; `docs/lanes/C-research/TASK.md`; `C:/Users/shubh/Projects/ai-kaushal-research/submission/answers_v2.py`; `.../submission/assets/onepager.html`. No files outside Lane C ownership were modified. No pip/npm install was run.

## Commands run and real output

1. Read-only prerequisite reads (`read_file` on the four files listed above). Output: all four read successfully; `COMMON.md` 21 lines, `TASK.md` 15 lines, `answers_v2.py` 11 lines, `onepager.html` 43 lines. Key constraint extracted: 'Write only files your lane owns… Never pip install or npm install… Use only C:\...\sewacircle\.venv\Scripts\python.exe'; 'No double quote characters inside prompt files for the runner'.

2. `$ "C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe" --version`
```
Python 3.13.14
exit: 0
```

3. `$ mkdir -p "C:/Users/shubh/Projects/sewacircle/docs/research" "C:/Users/shubh/Projects/sewacircle/docs/lanes/C-research/reports"` → no output, `exit: 0`.

4. `$ ls -la "C:/Users/shubh/Projects/sewacircle/docs/research"` (at that time, before writing the deliverable)
```
total 0
drwxr-xr-x 1 shubh 197610 0 Nov 18 23:08 .
drwxr-xr-x 1 shubh 197610 0 Nov 18 23:08 ..
exit: 0
```

5. Web queries issued (15 total). Exact query strings, in order:
   1. `OpenAI structured outputs guide json schema strict` → 5 results incl. https://platform.openai.com/docs/guides/structured-outputs/handling-mistakes, https://platform.openai.com/docs/guides/json-mode, https://developers.openai.com/cookbook/examples/structured_outputs_intro.
   2. `Gemini API structured output JSON schema documentation` → 5 results incl. https://aistudio.google.com/docs/structured-output, https://ai.google.dev/gemini-api/docs/structured-output?lang=rest.
   3. `UIDAI Aadhaar number 12 digits format official FAQ` → 5 results incl. https://uidai.gov.in/en/about-aadhaar, https://uidai.gov.in/images/LR_Aadhaar_Handbook_2026.pdf, https://uidai.gov.in/en/your-aadhaar.
   4. `Hinglish code mixing Hindi English NLP LLM extraction ACL paper` → 5 results incl. https://aclanthology.org/2025.findings-emnlp.422/.
   5. `Devanagari digits Unicode U0966 U096F code chart` → 5 results incl. https://www.unicode.org/Public/18.0.0/charts/nameslist/0900/, https://www.unicode.org/Public/UCD/latest/charts/PDF/U0900.pdf.
   6. `site:uidai.gov.in Verhoeff check digit Aadhaar last digit PDF` → 5 results, no official Verhoeff statement in titles/snippets.
   7. `site:uidai.gov.in Aadhaar number format 12 digit checksum Verhoeff` → 5 results, same: no official Verhoeff statement found.
   8. `PAN card number format 5 letters 4 digits 1 letter official incometax India` → 5 results incl. https://www.incometaxindia.gov.in/documents/d/guest/1-permanent-account-number-pan-pdf.
   9. `Hindi negation handling NLP nahin mat negation detection paper ACL` → 5 results incl. https://aclanthology.org/2026.chipsal-1.3.pdf, https://aclanthology.org/2026.dravidianlangtech-1.2.pdf.
   10. `Awadhi Bhojpuri Hindi dialect NLP resource paper ACL LREC` → 5 results incl. https://aclanthology.org/2023.jeptalnrecital-long.3/.
   11. `LLM confidence calibration abstention selective prediction paper arxiv` → 5 results incl. https://arxiv.org/html/2502.06884, https://arxiv.org/html/2607.04430.
   12. `Indic languages LLM evaluation Hindi code switching robustness paper arxiv` → 5 results incl. https://arxiv.org/html/2501.13912v1.
   13. `Verhoeff algorithm Aadhaar check digit wikipedia` → 5 results incl. https://en.wikipedia.org/wiki/Verhoeff_algorithm.
   14. `site:dot.gov.in 10 digit mobile number India numbering plan` → 5 results incl. https://www.dot.gov.in/static/uploads/2026/05/9ed5f19dbf38307edc38a54377d82cd5.pdf.
   15. `site:trai.gov.in 10 digit mobile number India` → 5 results (TRAI PDFs); none opened for claims.

6. Page-open requests via `web_extract`: **31 requests, 20 distinct URLs successfully opened, 2 failed**. Every opened page's title/URL/date is in the Sources table below. Key failures with real output:
```
URL: https://platform.openai.com/docs/guides/structured-outputs/handling-mistakes
ERR: Keyless Keenable extract failed: HTTP 404: {"error":"Not found","message":"The page does not exist at this URL. ..."}
URL: https://dot.gov.in/access-services/national-numbering-plan-2003
ERR: Keyless Keenable extract failed: HTTP 422: {"error":"Unprocessable entity","message":"The page was reached but content could not be extracted", ...}
```
Recovery: for the OpenAI page, the second route `https://developers.openai.com/api/docs/guides/structured-outputs.md` was opened successfully; for DoT, the direct PDF URL above was opened successfully. No claim relies on the two failed pages.

7. `$ "C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe" -c "import importlib.util; print(importlib.util.find_spec('jsonschema')); print(importlib.util.find_spec('pydantic'))"`
```
jsonschema None
pydantic ModuleSpec(name='pydantic', ... origin='C:\\Users\\shubh\\Projects\\sewacircle\\.venv\\Lib\\site-packages\\pydantic\\__init__.py', ...)
exit: 0
```
Consequence: no install permitted; validation was implemented with a stdlib recursive validator.

8. `$ "C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe" -c "import unicodedata; print(unicodedata.digit('१'), unicodedata.digit('९'))"`
```
1 9
exit: 0
```

9. First run of the test harness (before fixing a `str.maketrans` length bug) — real output:
```
EXIT=1
PYTHON: 3.13.14
Traceback (most recent call last):
  File "C:\Users\shubh\AppData\Local\hermes\profiles\researcher\cache\scratch\r2_tests.py", line 8, in <module>
    DEV_TO_ASCII = str.maketrans("〇०१२३४५६७८९", "0123456789")
                   ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: the first two maketrans arguments must have equal length
```
Fixed by using the 10 Devanagari digits only. Second run succeeded (with a cosmetic label typo, later fixed). Final run below.

10. **Final test command and full real output** (`$ "C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe" "C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r2_tests.py"`, stdout redirected to `r2_tests_output.txt`, `EXIT=0`):
```
PYTHON: 3.13.14
DEVANAGARI->ASCII normalization: 10 (from U+0967 U+0966)
Synthetic checksum-valid Aadhaar generated: 999999999999

=== PII MATCHES (real regex output) ===
AADHAAR  count=3
   [167:181] 9999 9999 9999 verhoeff=PASS
   [216:228] 999999999990 verhoeff=FAIL
   [263:275] 999999999999 verhoeff=PASS
PHONE    count=3
   [100:115] +91 99999 12345
   [119:130] 99999-12345
   [134:144] 9999912345
PAN      count=1
   [286:296] AABBC1234D
EMAIL    count=1
   [304:339] synthetic.volunteer@example.invalid
NAME     count=2
   [345:359] राम कुमार यादव
   [371:380] Asha Devi
ADDRESS  count=1
   [381:457] Address: House 999, Synthetic Nagar, Kanpur Dehat, Uttar Pradesh, PIN 999999
merged non-overlapping redaction spans: 11

=== REDACTED SYNTHETIC SAMPLE (real output) ===
SYNTHETIC SAMPLE - NOT REAL DATA - invented numbers only
Task: १० volunteers for shramdaan. Contact [REDACTED:PHONE] or [REDACTED:PHONE] or [REDACTED:PHONE].
Aadhaar-spaced-fake: [REDACTED:AADHAAR]
Aadhaar-contiguous-fake-badcheck: [REDACTED:AADHAAR]
Aadhaar-checksum-valid-synthetic: [REDACTED:AADHAAR]
PAN-fake: [REDACTED:PAN]
Email: [REDACTED:EMAIL]
नाम: [REDACTED:NAME]
Organiser: [REDACTED:NAME]
[REDACTED:ADDRESS]
Negation probes: first-aider nahin chahiye; mat bhejo; not required.


=== NEGATIVE CONTROLS (should all be 0) ===
9-digit not phone                      matches=0
11-digit not phone                     matches=0
11-digit not Aadhaar                   matches=0
13-digit not Aadhaar                   matches=0
lower-case PAN not matched             matches=0
free-text name not matched (no cue)    matches=0

=== NEGATION CUE PROBES (synthetic) ===
  cue: NOT at (19, 22)
  cue: nahin at (487, 492)
  cue: mat at (502, 505)
  cue: not at (513, 516)

=== SCHEMA VALIDATION (real output) ===
strict-shape problems: NONE -> PASS
schema objects checked: 2, enum fields: 2, required properties total: 8
VALID     : PASS
BAD_COUNT : REJECT -> $.roles[0].count: 0 below minimum 1
BAD_LEVEL : REJECT -> $.roles[0].level: 'guru' not in enum
BAD_EXTRA : REJECT -> $: unexpected property 'guessed'
evidence_span in redacted input? True (app-level check, not JSON Schema)
```
Per-class result: PHONE 3/3 matched and redacted (prefixed `+91` with spaces, hyphenated 5+5, plain 10-digit); AADHAAR 3/3 (spaced 4-4-4, contiguous with failing Verhoeff, contiguous with passing Verhoeff); PAN 1/1; EMAIL 1/1; NAME 2/2 (Hindi cue `नाम:` and English cue `Organiser:`); ADDRESS 1/1. Schema: strict shape PASS; one valid payload PASS; three invalid payloads REJECTED with the exact messages above.

11. `$ date` → `Wed, Nov 18, 2026 11:18:53 PM` (exit 0).

12. Devanagari digit regex probe (`python.exe -c ...`; emitted a harmless `SyntaxWarning: invalid escape sequence '\d'` because of shell escaping in the one-liner) — real output:
```
python-re-digit-devanagari: []
python-re-\\d-devanagari: ['१२३']
int-devanagari: 12
exit: 0
```

13. Deliverable verification: `$ grep -n "^#" ".../docs/research/R2-nlp-hindi.md"` →
```
1:## Findings
82:## Recommendation for our build
159:## Risks
171:## Sources
```
`$ wc -l -c ".../R2-nlp-hindi.md"` → `189 23644 C:/Users/shubh/Projects/sewacircle/docs/research/R2-nlp-hindi.md`.

## Sources opened (title — URL — date)

| # | Title | URL | Date / accessed |
|---|---|---|---|
| 1 | Structured model outputs (OpenAI Developers) | https://developers.openai.com/api/docs/guides/structured-outputs.md | accessed 2026-11-18 |
| 2 | Structured model outputs (OpenAI Developers, HTML form) | https://developers.openai.com/api/docs/guides/structured-outputs | accessed 2026-11-18 |
| 3 | Introduction to Structured Outputs (OpenAI cookbook) | https://developers.openai.com/cookbook/examples/structured_outputs_intro | accessed 2026-11-18 |
| 4 | Structured outputs — Gemini API (Google AI for Developers) | https://ai.google.dev/gemini-api/docs/structured-output?lang=rest | accessed 2026-11-18 |
| 5 | Structured outputs — Gemini API (Google AI Studio) | https://aistudio.google.com/docs/structured-output | accessed 2026-11-18 |
| 6 | Unicode 18.0 Devanagari nameslist | https://www.unicode.org/Public/18.0.0/charts/nameslist/0900/ | Unicode 18.0; accessed 2026-11-18 |
| 7 | The Unicode Standard 18.0, Devanagari chart U0900 | https://www.unicode.org/Public/UCD/latest/charts/PDF/U0900.pdf | Unicode 18.0; accessed 2026-11-18 |
| 8 | About Your Aadhaar — UIDAI | https://uidai.gov.in/en/about-aadhaar | published 17 Apr 2026, last updated 16 Jun 2026 |
| 9 | Understand your Aadhaar — UIDAI (thin content; not cited for claims) | https://uidai.gov.in/en/understand-your-aadhaar | accessed 2026-11-18 |
| 10 | Aadhaar Online Services — UIDAI | https://uidai.gov.in/en/aadhaar-online-services | accessed 2026-11-18 |
| 11 | PAN — Income Tax India | https://www.incometaxindia.gov.in/en/pan | accessed 2026-11-18 |
| 12 | Permanent Account Number (PAN) PDF — Income Tax India | https://www.incometaxindia.gov.in/documents/d/guest/1-permanent-account-number-pan-pdf | as amended by Finance Act, 2025; accessed 2026-11-18 |
| 13 | National Numbering Plan (PDF) — DoT, Government of India | https://www.dot.gov.in/static/uploads/2026/05/9ed5f19dbf38307edc38a54377d82cd5.pdf | April 2003; accessed 2026-11-18 |
| 14 | COMI-LINGUA (Findings of EMNLP 2025) | https://aclanthology.org/2025.findings-emnlp.422/ | 2025-11 |
| 15 | Beyond Benchmark Accuracy: Robustness Evaluation of Hinglish Sentiment Models | https://aclanthology.org/2026.dravidianlangtech-1.2.pdf | 2026; accessed 2026-11-18 |
| 16 | Cross-lingual Strategies for Low-resource Language Modeling: Five Indic Dialects | https://aclanthology.org/2023.jeptalnrecital-long.3/ | 2023; accessed 2026-11-18 |
| 17 | Lost the Negation or Lost in Negation (CHiPSAL@LREC 2026) | https://aclanthology.org/2026.chipsal-1.3.pdf | 16 May 2026 |
| 18 | Analysis of Indic Language Capabilities in LLMs | https://arxiv.org/html/2501.13912v1 | 2025-01; accessed 2026-11-18 |
| 19 | Learning Conformal Abstention Policies for Adaptive Risk Management in LLMs/VLMs | https://arxiv.org/html/2502.06884 | 08 Feb 2025 |
| 20 | Verhoeff algorithm (secondary source) | https://en.wikipedia.org/wiki/Verhoeff_algorithm | accessed 2026-11-18 |

Failed opens (not used as sources): OpenAI `handling-mistakes` URL (404), DoT National Numbering Plan landing page (422).

## Counts

- Web search queries: **15** (verbatim list in §5).
- `web_extract` page-open requests: **31**; distinct URLs successfully opened: **20**; failed URLs: **2**.
- Distinct sources cited in the deliverable: **17 numbered entries** covering **19** of the 20 opened URLs (entries 1 and 15 each combine two URLs). The one opened-but-uncited page is the thin 'Understand your Aadhaar' UIDAI page; the 404/422 pages were not counted as opened.
- Primary publishers among opened sources: **8** — UIDAI, Income Tax India, Unicode Consortium, OpenAI, Google, Department of Telecommunications (India), arXiv authors (2 papers), ACL/ELRA paper authors (4 papers). Wikipedia (Verhoeff/Aadhaar link) is the single **secondary** source and is labelled as such in the deliverable.
- Local commands executed with the mandated venv Python: **7** (version, importlib probe, unicodedata probe, first failing harness run, two passing harness runs, digit-regex probe). Additional shell commands: `date`, `mkdir -p`, `ls -la`, `grep -n`, `wc -l -c` (real outputs above).

## Unresolved items

1. **Verhoeff ↔ Aadhaar official spec: NOT FOUND.** Two `site:uidai.gov.in` searches and three UIDAI pages opened did not state the checksum rule. The deliverable cites Wikipedia as secondary and labels the claim accordingly; no official UIDAI URL is asserted for it.
2. **10-digit Indian mobile rule: NOT FOUND in the opened DoT text.** The PDF extract exposed the title, April 2003 date and Annex VIII 'Numbering for Cellular Mobile', but not the extracted rule sentence. The phone regex is therefore explicitly labelled an engineering convention, not a quoted DoT requirement.
3. **No model API calls were made.** The task is prompt/schema design plus local regex/validator tests; no provider credentials or integration are in scope. No extraction-accuracy, latency or calibration number is claimed — the 10-task design is a proposal only.
4. **Name/address recall unmeasured.** Only cue-prefixed names/addresses were tested (2 names, 1 address); the negative control shows unlabelled free-text names are deliberately not matched. This is documented as a limitation, not a solved capability.
5. **Synthetic all-9s Aadhaar passes Verhoeff** in our own run (`verhoeff=PASS`), because the generated synthetic check digit was 9. Flagged in the deliverable: checksum validity is not authenticity and must never suppress redaction.
6. **`jsonschema` absent from the venv**; no installs allowed, so the schema validator used is a small stdlib implementation written for this test. It validates the structural subset used by the proposed schema; it is not a full JSON Schema implementation.
7. **Live docs without version dates.** OpenAI and Google structured-output pages carry no visible version date; all are recorded as 'accessed 2026-11-18' and flagged for re-check before implementation.
