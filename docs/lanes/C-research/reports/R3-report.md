# R3 audit report — Lane C deep research (credentials, privacy, audit integrity)

Researcher: Hermes subagent, Lane C. Date/time of research: 2026-11-18 (terminal `date` output: `Wed, Nov 18, 2026 11:16:35 PM`). Workdir: `C:/Users/shubh/Projects/sewacircle`. Only lane-owned files were written. No pip/npm install was run. All example people/tasks/hours in the deliverable are SYNTHETIC.

## Deliverable and files written

| Path | Status |
|---|---|
| `docs/research/R3-credentials-privacy.md` | CREATED (32518 bytes; exactly four `##` sections: Findings, Recommendation for our build, Risks, Sources) |
| `docs/lanes/C-research/reports/R3-report.md` | CREATED (this audit report) |
| `C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/strip.py` | THROWAWAY helper (stdlib `HTMLParser` HTML-to-text), not a project file |
| `C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r3_hashchain_demo.py` | THROWAWAY runnable hash-chain demo (stdlib `hashlib` only), not a project file |
| `C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/{ob3,vc20,vc11,ctx_v2,ctx_v1,obctx,obext,obschema,mb_*,dpdpa_*,dpdp_*,commence_*,timeline,rfc6962}.{html,txt,pdf}` | THROWAWAY fetched source copies used for reading/quotes |

No files outside `docs/research/`, `docs/lanes/C-research/` and the Hermes scratch dir were modified.

## Command log (commands actually run, with real output)

### 1. Fetch primary spec HTML

```
curl -sS -L -o "$TMPDIR/ob3.html" -w '%{http_code} %{size_download}\n' 'https://www.imsglobal.org/spec/ob/v3p0/'
curl -sS -L -o "$TMPDIR/vc20.html" -w '%{http_code} %{size_download}\n' 'https://www.w3.org/TR/vc-data-model-2.0/'
curl -sS -L -o "$TMPDIR/vc11.html" -w '%{http_code} %{size_download}\n' 'https://www.w3.org/TR/vc-data-model-1.1/'
```
Output (three commands, exit 0 each):
```
200 3655052
200 1023165
200 746185
```

### 2. Toolchain probes

```
C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -c "import bs4; print('bs4 ok', bs4.__version__)"
```
Output (exit 1):
```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import bs4; print('bs4 ok', bs4.__version__)
ModuleNotFoundError: No module named 'bs4'
```

```
echo TMPDIR=$TMPDIR
```
Output: `TMPDIR=/tmp`

```
ls -l /tmp/ob3.html /tmp/vc20.html /tmp/vc11.html 2>&1
```
Output: `ls: cannot access '/tmp/ob3.html': No such file or directory` (and same for the other two names; files had landed elsewhere, so all later fetches used an explicit scratch path).

```
cygpath -w /tmp 2>/dev/null || true
```
Output: `C:\Users\shubh\AppData\Local\Temp`

```
ls -l 'C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/' | tail -20
```
Output included: `-rw-r--r-- 1 shubh 197610 282 Nov 18 23:12 r1_probe.py` (another lane's scratch file, read-only observation).

### 3. Re-fetch specs into explicit scratch path and strip HTML

```
curl -sS -L -o '<scratch>/ob3.html' -w '%{http_code} %{size_download}\n' 'https://www.imsglobal.org/spec/ob/v3p0/' && C:/.../.venv/Scripts/python.exe '<scratch>/strip.py' '<scratch>/ob3.html' '<scratch>/ob3.txt'
curl -sS -L -o '<scratch>/vc20.html' -w '%{http_code} %{size_download}\n' 'https://www.w3.org/TR/vc-data-model-2.0/' && ... strip.py ...
curl -sS -L -o '<scratch>/vc11.html' -w '%{http_code} %{size_download}\n' 'https://www.w3.org/TR/vc-data-model-1.1/' && ... strip.py ...
```
Output (exit 0 each):
```
200 3655052
C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/ob3.html html_chars 3654717 text_chars 1903073 -> .../ob3.txt
200 1023165
C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/vc20.html html_chars 1021848 text_chars 366232 -> .../vc20.txt
200 746185
C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/vc11.html html_chars 745199 text_chars 257010 -> .../vc11.txt
```
All field tables, MUST statements and the example JSON in the deliverable were read from these extracted text files at specific line numbers (e.g. OB3 lines 2810–2909 for `AchievementCredential`, 2912–2989 for `AchievementSubject`, 13000–13007 for the JSON Schema required list; VC2 lines 742–755, 1811–1815, 2333–2339; VC1.1 lines 859–865, 1277–1278, 1408–1411, 1633–1637, 1748–1758).

### 4. Context and schema files opened

Each command: `curl -sS -L -o '<scratch>/<name>.txt' -w '%{http_code} %{content_type} %{size_download}\n' '<URL>' && head -c 400 '<file>'`. Real output (status / type / bytes, plus first bytes):

```
ctx_v2  https://www.w3.org/ns/credentials/v2
200 application/ld+json 10131
{
  "@context": {
    "@protected": true,
    "id": "@id",
    "type": "@type",
    ...
ctx_v1  https://www.w3.org/2018/credentials/v1
200 application/ld+json 7687
{
  "@context": {
    "@version": 1.1,
    "@protected": true,
    "id": "@id",
    "type": "@type",
    "VerifiableCredential": {
...
obctx  https://purl.imsglobal.org/spec/ob/v3p0/context-3.0.3.json
200 application/json 14565
{
  "@context": {
    "@protected": true,
    "id": "@id",
    "type": "@type",
    "OpenBadgeCredential": {
      "@id": "https://purl.imsglobal.org/spec/vc/ob/vocab.html#OpenBadgeCredential"
...
obext  https://purl.imsglobal.org/spec/ob/v3p0/extensions.json
200 application/json 419
{
  "@context": {
    "id": "@id",
    "type": "@type",
    "1EdTechJsonSchemaValidator2019": "https://purl.imsglobal.org/spec/vccs/v1p0/context.json#1EdTechJsonSchemaValidator2019",
...
obschema  https://purl.imsglobal.org/spec/ob/v3p0/schema/json/ob_v3p0_achievementcredential_schema.json
200 application/json 112790
{
  "$schema" : "https://json-schema.org/draft/2019-09/schema#",
  "$id" : "https://purl.imsglobal.org/spec/ob/v3p0/schema/json/ob_v3p0_achievementcredential_schema.json",
...
```

### 5. MY Bharat official pages opened

Six `curl -sS -L --max-time 60 ... && strip.py` commands. Real output:

```
mb_home: curl printed 200 486381; strip printed html_chars 486312 text_chars 13598 -> .../mb_home.txt
mb_about 200 268251 -> html_chars 268223 text_chars 5194 -> .../mb_about.txt
mb_policy 200 45578 -> html_chars 45568 text_chars 5128 -> .../mb_policy.txt
mb_faq 200 128430 -> html_chars 128425 text_chars 2857 -> .../mb_faq.txt
mb_brics 200 283911 -> html_chars 283887 text_chars 4907 -> .../mb_brics.txt
mb_terms 200 277041 -> html_chars 277005 text_chars 15898 -> .../mb_terms.txt
```
(For `mb_home` the two numbers printed on separate lines were `200 486381` from curl, then the strip line; all six returned HTTP 200.)

Exact MY Bharat quotes were then read from the stripped text (mb_about lines 134–135; mb_home lines 128–129, 295–313; mb_brics line 138) and are reproduced in the deliverable.

### 6. PDF tooling probe and official DPDP texts

```
command -v pdftotext || true
```
Output: `/mingw64/bin/pdftotext 0`

```
C:/.../.venv/Scripts/python.exe -c "import pypdf;print('pypdf',pypdf.__version__)"
... import PyPDF2 ...
... import fitz ...
```
Output (exit 1 each): `ModuleNotFoundError: No module named 'pypdf'` / `'PyPDF2'` / `'fitz'`. No installs were attempted; system `pdftotext -layout` was used.

```
curl -sS -L --max-time 60 -o '<scratch>/meity_rules_page.html' -w '%{http_code} %{size_download}\n' 'https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa'
```
Output: `200 3137` (JS shell only; `__NEXT_DATA__.props` with slug/childslug).

```
grep -oE 'https?://[^"<> ]+\.pdf' '<scratch>/meity_rules_page.html' | sort -u | head -40
```
Output: empty.

```
curl -sS -L --max-time 90 -o '<scratch>/dpdprules_egaz_267649.pdf' ... 'https://egazette.gov.in/WriteReadData/2025/267649.pdf' && pdftotext -layout ... && wc -c ... && head -c 900 ...
```
Output: `200 1819855`, `2462 .../dpdprules_egaz_267649.txt`, then header text (`No. 759] ... G.S.R. 845 (E) ... Data Protection Board of India shall consist of four members`). Identified as the Board-members notification, not the Rules.

```
curl ... 'https://www.meity.gov.in/static/uploads/2025/02/07b7d737f483714eacde37d1a259a6c8.pdf' && pdftotext ... && wc -c ...
curl ... 'https://egazette.gov.in/WriteReadData/2023/248045.pdf' && pdftotext ... && wc -c ...
```
Output: `200 182082`, `83343 .../dpdpa_meity.txt`; `200 182082`, `83343 .../dpdpa_egaz.txt` (byte-identical texts).

```
curl ... 'https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf' && pdftotext ... && wc -c ... && head -c 1200 ...
curl ... 'https://www.meity.gov.in/static/uploads/2025/12/3c7ebbae0e5456f493f486e6845df86b.pdf' && pdftotext ... && wc -c ... && head -c 1200 ...
```
Output: `200 2492944`, `90709 .../dpdp_rules_2025_meity.txt` (G.S.R. 846(E), Gazette 13 Nov 2025); `200 408279`, `2649 .../dpdp_rules_corrigendum.txt` (G.S.R. 892(E), 10 Dec 2025).

```
curl ... 'https://egazette.gov.in/WriteReadData/2025/267647.pdf' && pdftotext ... && wc -c ...
```
Output: `200 1869005`, `3459 .../commence_267647.txt` (Hindi text garbled; English text present further down).

```
curl ... 'https://www.meity.gov.in/static/uploads/2025/11/c56ceae6c383460ca69577428d36828b.pdf' && pdftotext ... && wc -c ... && head -c 3000 ...
```
Output: `200 1869005`, `3459 .../timeline.txt`, containing the full English G.S.R. 843(E) commencement text including clause (c) "eighteen months from the date of publication of this gazette, on which the provision of sections 3 to 5, sub-sections (1) to (8) and (10) of section 6, sections 7 to 10, sections 11 to 17 ... shall come into force."

```
curl -sS -L --max-time 90 -o '<scratch>/rfc6962.html' -w '%{http_code} %{size_download}\n' 'https://www.rfc-editor.org/rfc/rfc6962.html' && <scratch>/strip.py ...
```
Output: `200 68207`, `rfc6962.html html_chars 68207 text_chars 48090 -> .../rfc6962.txt`.

### 7. Hash-chain tamper-detection demo — command and REAL output

Command (exact):
```
C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r3_hashchain_demo.py
```
Exit code: `0`. Output (verbatim):
```
=== A. Synthetic-only hash-chain ledger (stdlib hashlib) ===
appended index=0 prev_hash=0000000000000000... hash=c79ca8bad2a29893...
appended index=1 prev_hash=c79ca8bad2a29893... hash=ce1159ea65ef1361...
appended index=2 prev_hash=ce1159ea65ef1361... hash=e7621d0f342911ad...
verify original: ok=True detail=all 3 entries linked and hashes recompute
tamper attempt: changed index=1 hours 3.0 -> 8.0
verify tampered: ok=False detail=hash mismatch at 1: stored=ce1159ea65ef1361 recomputed=145259e2641c7adf
=== B. Minimal OB3-shaped JSON: required-field presence check ===
  credential: required=['@context', 'id', 'type', 'credentialSubject', 'issuer', 'validFrom'] missing=[]
  issuer: required=['id', 'type'] missing=[]
  achievement: required=['id', 'type', 'criteria', 'description', 'name'] missing=[]
  subject: required=['type', 'achievement'] missing=[]
  evidence: required=['type'] missing=[]
required-field check: ok=True
proof field present: False
=== END ===
```

### 8. Validator probe and deliverable verification

```
C:/.../.venv/Scripts/python.exe -c "import jsonschema; print('jsonschema', jsonschema.__version__)"
```
Output (exit 1):
```
ModuleNotFoundError: No module named 'jsonschema'
```

```
cd 'C:/Users/shubh/Projects/sewacircle' && C:/.../.venv/Scripts/python.exe -c "p='docs/research/R3-credentials-privacy.md'; t=open(p,encoding='utf-8').read(); print('bytes',len(t.encode('utf-8'))); print('H2',[l for l in t.splitlines() if l.startswith('## ')]); print('has_tamper_output','verify tampered: ok=False' in t); print('has_not_accredited','NOT an accredited' in t); print('has_dpdp','Section 9(1)' in t)"
```
Output:
```
bytes 32518
H2 ['## Findings', '## Recommendation for our build', '## Risks', '## Sources']
has_tamper_output True
has_not_accredited True
has_dpdp True
```

### 9. Web searches issued (15 queries; outputs condensed to the URLs actually returned)

1. `site:imsglobal.org Open Badges 3.0 spec educational achievement credential` → imsglobal.org/spec/ob/v3p0/cert, purl.imsglobal.org/spec/ob/vocab.html, imsglobal.org/spec/ob-assessment/v2p0/, imsglobal.org/spec/ob-ace/v1p0, imsglobal.org/spec/ob-accred/v2p0/
2. `site:w3.org/TR/vc-data-model-2.0 Verifiable Credentials Data Model 2.0` → w3.org/TR/vc-data-model-2.0/
3. `site:w3.org/TR/vc-data-model/ Verifiable Credentials Data Model 1.1` → w3.org/TR/vc-data-model-1.1/, w3.org/TR/vc-data-model-threat-model/, w3.org/TR/vc-data-model/all/, w3.org/TR/vc-data-model/
4. `site:mybharat.gov.in digital credentials volunteer hours` → mybharat.gov.in/, /about_mybharat, /elp/listing, /pages/about_mybharat, /pages/brics_2026, /pages/ce?mode=A
5. `site:meity.gov.in DPDP Act 2023 section 9 children verifiable parental consent PDF` → meity.gov.in/static/uploads/2025/02/07b7d737f483714eacde37d1a259a6c8.pdf, /2024/02/177897517eb68c21f247bc3247a2f506.pdf, /2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf, /2024/02/Digital-Personal-Data-Protection-Act-2023.pdf, meity.gov.in/content/digital-personal-data-protection-act-2023
6. `site:egazette.nic.in Digital Personal Data Protection Rules 2025 pdf` → returned HTTP ERROR pages for egazette.nic.in (dead domain); recovered via `egazette.gov.in` in query 12.
7. `site:mybharat.gov.in "digital credential"` → /pages/about_mybharat, /about_mybharat, /, /pages/terms_of_use, /policy, /pages/policy, /faqs, /support
8. `site:mybharat.gov.in "volunteer hours"` → /, /pages/brics_2026, /pages/ce?mode=A, /elp/listing/156898, /mega_events/outreach-program-on-my-bharat, /elp/listing
9. `site:mybharat.gov.in credential volunteering certificate hours` → /, /about_mybharat, /policy, /pages/about_mybharat, /yuva_register, /vo/pages/event_detail?..., /elp/listing/154339
10. `site:mybharat.gov.in "hours" "volunteer" MY Bharat official` → /elp/listing/156898, /mega_events/outreach-program-on-my-bharat, /elp/listing/155685, /Gov/Urban-Local-Body/nagar-palika-parishad-hathras, /elp/listing, /mega_events/tb-mukt-bharat-abhiyaan-mega-event-elp/experiential_learning, /elp/listing/158177, /elp/listing/158170
11. `site:meity.gov.in "Digital Personal Data Protection Rules, 2025" pdf` → meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa (+ pageTitle variants), meity.gov.in/static/uploads/2026/01/a49c50414777afc2af0b8d59dafacd60.pdf, meity.gov.in/content/explanatory-note-digital-personal-data-protection-rules-2025
12. `site:egazette.gov.in "Digital Personal Data Protection Rules, 2025"` → egazette.gov.in/WriteReadData/2025/267647.pdf, /267649.pdf, /2023/248045.pdf, /2025/260852.pdf, /2023/247847.pdf, /2026/269916.pdf
13. `site:mybharat.gov.in "digital badges"` → /pages/about_mybharat, / (quotes used in deliverable)
14. `site:mybharat.gov.in "volunteer" "hours" "certificate"` → /elp/listing, /pages/brics_2026, /faqs, /policy
15. `site:mybharat.gov.in "Volunteer for Bharat" hours geotagging` → /pages/about_mybharat, /mega_events/outreach-program-on-my-bharat, / (no additional credential mechanics found)

## Sources opened (title | URL | date)

1. Open Badges Specification v3.0, Final Release, Doc v1.4.5, 29 June 2026 | https://www.imsglobal.org/spec/ob/v3p0/ | opened 2026-11-18
2. Open Badges vocabulary | https://purl.imsglobal.org/spec/ob/vocab.html | opened 2026-11-18
3. W3C Verifiable Credentials Data Model v2.0, Recommendation 15 May 2025 | https://www.w3.org/TR/vc-data-model-2.0/ | opened 2026-11-18
4. W3C Verifiable Credentials Data Model v1.1, Recommendation 3 March 2022 | https://www.w3.org/TR/vc-data-model-1.1/ | opened 2026-11-18
5. W3C VC v2 context | https://www.w3.org/ns/credentials/v2 | opened 2026-11-18
6. W3C VC v1 context | https://www.w3.org/2018/credentials/v1 | opened 2026-11-18
7. 1EdTech OB 3.0 context 3.0.3 | https://purl.imsglobal.org/spec/ob/v3p0/context-3.0.3.json | opened 2026-11-18
8. 1EdTech OB 3.0 extensions context | https://purl.imsglobal.org/spec/ob/v3p0/extensions.json | opened 2026-11-18
9. 1EdTech OB 3.0 AchievementCredential JSON Schema | https://purl.imsglobal.org/spec/ob/v3p0/schema/json/ob_v3p0_achievementcredential_schema.json | opened 2026-11-18
10. MY Bharat homepage (footer "Last updated: 18-11-2026") | https://mybharat.gov.in/ | opened 2026-11-18
11. About MY Bharat | https://mybharat.gov.in/pages/about_mybharat | opened 2026-11-18
12. MY Bharat Privacy Policy | https://mybharat.gov.in/policy | opened 2026-11-18
13. MY Bharat FAQs | https://mybharat.gov.in/faqs | opened 2026-11-18
14. MY Bharat BRICS 2026 | https://mybharat.gov.in/pages/brics_2026 | opened 2026-11-18
15. MY Bharat Terms of Service | https://mybharat.gov.in/pages/terms_of_use | opened 2026-11-18
16. DPDP Act 2023 (MeitY PDF) | https://www.meity.gov.in/static/uploads/2025/02/07b7d737f483714eacde37d1a259a6c8.pdf | opened 2026-11-18
17. DPDP Act 2023 (Gazette of India) | https://egazette.gov.in/WriteReadData/2023/248045.pdf | opened 2026-11-18
18. DPDP Rules 2025, G.S.R. 846(E), 13 Nov 2025 (MeitY PDF) | https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf | opened 2026-11-18
19. DPDP Act commencement notification, G.S.R. 843(E), 13 Nov 2025 | https://egazette.gov.in/WriteReadData/2025/267647.pdf | opened 2026-11-18
20. MeitY DPDP Rules 2025 documents listing | https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa?pageTitle=Digital-Personal-Data-Protection-Rules-2025686cadad39.pdf | opened 2026-11-18
21. Corrigenda to DPDP Rules 2025, G.S.R. 892(E), 10 Dec 2025 | https://www.meity.gov.in/static/uploads/2025/12/3c7ebbae0e5456f493f486e6845df86b.pdf | opened 2026-11-18
22. Enforcement timeline copy (same notification as #19) | https://www.meity.gov.in/static/uploads/2025/11/c56ceae6c383460ca69577428d36828b.pdf | opened 2026-11-18
23. IETF RFC 6962, Certificate Transparency, June 2013 | https://www.rfc-editor.org/rfc/rfc6962.html | opened 2026-11-18
24. eGazette G.S.R. 845(E), Data Protection Board members (checked, not cited for a claim) | https://egazette.gov.in/WriteReadData/2025/267649.pdf | opened 2026-11-18
25. MeitY explanatory note to DPDP Rules 2025 (returned path only, no usable text) | https://www.meity.gov.in/content/explanatory-note-digital-personal-data-protection-rules-2025 | opened 2026-11-18

## Counts

- Web-search queries: **15** (listed above).
- Distinct URLs opened/fetched: **25** (listed above); **24** yielded usable text, one (#25) did not.
- "Pages opened" in the sense of documents read in full or in relevant sections: **24** (all of #1–#24).
- Distinct sources: **25** URLs; **5 independent primary publishers**: 1EdTech, W3C, IETF, Government of India (MeitY / Gazette of India), MY Bharat (Department of Youth Affairs, Ministry of Youth Affairs and Sports).
- Commands with real output recorded above: **all shell/terminal invocations and the venv-Python script runs used in this research**. HTML-to-text conversion used the venv Python; in-session Python stdlib reads and regex greps over the fetched text files were used for section/quote extraction (their results are the line numbers and quotes in the deliverable).

## UNRESOLVED / NOT FOUND

- `https://www.imsglobal.org/spec/ob/v3p0/html/` → `CRAWL_NOT_FOUND` via `web_extract`; the canonical main page (#1) was used and contains the full spec.
- MeitY explanatory-note page (#25) → extraction returned only `/content/explanatory-note-digital-personal-data-protection-rules-2025`, no content; official Rules PDF (#18) used instead.
- MY Bharat: **NOT FOUND** — no official page opened defines volunteer hours as a portable/verifiable credential; no Open Badges, W3C VC, JSON-LD, credential schema or signed-credential statement; no child/guardian-consent clause in the opened Privacy Policy. Not proof of absence.
- Full JSON Schema / JSON-LD validation of the example credential: **NOT RUN** (`jsonschema` not installed; no install permitted). Required-field presence only was verified by the real script output above.
- Corrigendum #21 was opened and its listed edits recorded; no further legal analysis of its effects was attempted beyond the "of this Gazette" → "in the Official Gazette" correction quoted in the deliverable.
- No field pilot, real volunteer data, or measured fraud-reduction figure exists; all such statements in the deliverable are labelled INFERENCE or excluded.

## Verification statement

The deliverable contains exactly the four required `##` sections (verified by command output above), includes exact field names and opened URLs for OB3/VC1.1/VC2.0, exact official quotes for MY Bharat and DPDP, labelled fraud-rule inferences, the runnable stdlib hash-chain demo with real tamper-detection output, and an explicit final "What we may honestly claim" list that states plainly that a self-issued data-model-shaped JSON is NOT an accredited or verified credential.
