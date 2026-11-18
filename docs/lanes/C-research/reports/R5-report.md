# R5 audit report — Lane C demo/UX research

## Deliverable and files written

- **Deliverable path:** `C:/Users/shubh/Projects/sewacircle/docs/research/R5-demo-ux.md`
- **Files written by this agent:**
  1. `C:/Users/shubh/Projects/sewacircle/docs/research/R5-demo-ux.md` (deliverable; 21,743 bytes, verified by write tool)
  2. `C:/Users/shubh/Projects/sewacircle/docs/lanes/C-research/reports/R5-report.md` (this audit)
  3. `C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r5_timing_proof.py` (throwaway proof script in $TMPDIR; 1,069 bytes)
- Directories created: `docs/research` and `docs/lanes/C-research/reports` (both already existed by the time the write landed; `mkdir -p` was idempotent).
- No other repository files were read-only or modified outside owned lanes; no packages were installed.

## Verification of deliverable structure

Command run (venv python, exact text):

```
C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -c "import re,pathlib; p=pathlib.Path(r'C:/Users/shubh/Projects/sewacircle/docs/research/R5-demo-ux.md'); t=p.read_text(encoding='utf-8'); h2=re.findall(r'^## (.+)$',t,re.M); urls=re.findall(r'https?://[^\s)]+',t); src=t.split('## Sources',1)[1]; rows=[l for l in src.splitlines() if re.match(r'^\|\s*\d+\s*\|',l)]; print('H2_SECTIONS=',h2); print('SOURCE_TABLE_ROWS=',len(rows)); print('URL_MENTIONS_TOTAL=',len(urls)); print('UNIQUE_URLS=',len(set(urls)))"
```

Real output:

```
H2_SECTIONS= ['Findings', 'Recommendation for our build', 'Risks', 'Sources']
SOURCE_TABLE_ROWS= 24
URL_MENTIONS_TOTAL= 61
UNIQUE_URLS= 39
```

The four required sections are the only H2 headings. The 39 unique URLs include 24 source-table URLs plus inline repeats and the explicitly listed blocked URLs.

## Commands run and real output

### Command 1 — directory creation + Python version + 15 MB bitrate arithmetic

```
mkdir -p C:/Users/shubh/Projects/sewacircle/docs/research C:/Users/shubh/Projects/sewacircle/docs/lanes/C-research/reports && C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe -c "import sys; print('python', sys.version.split()[0]); s=180; mb=15; b=mb*1000*1000; mib=mb*1024*1024; print('15 MB =', b, 'bytes ->', round(b*8/s), 'bit/s =', round(b*8/s/1e6,3), 'Mbps'); print('15 MiB =', mib, 'bytes ->', round(mib*8/s), 'bit/s =', round(mib*8/s/1e6,3), 'Mbps')"
```

Real output (exit code 0):

```
python 3.13.14
15 MB = 15000000 bytes -> 666667 bit/s = 0.667 Mbps
15 MiB = 15728640 bytes -> 699051 bit/s = 0.699 Mbps
```

### Command 2 — PROOF COMMAND: parse the demo timings from the deliverable and assert 180 s

Proof script written to `$TMPDIR` (`C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r5_timing_proof.py`). It reads the actual deliverable markdown, regex-parses every row of the demo timing table (`| n | mm:ss-mm:ss | segment | seconds | ... |`), asserts exactly 10 segments, asserts each written time window equals its stated seconds, asserts contiguous start times, then asserts the total is 180.

Key source lines of the proof script:

```python
pattern = re.compile(
    r'^\|\s*(\d+)\s*\|\s*(\d{2}):(\d{2})-(\d{2}):(\d{2})\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|',
    re.MULTILINE,
)
rows = pattern.findall(text)
assert len(rows) == 10, f'expected 10 demo segments, parsed {len(rows)}'
...
assert end - start == seconds, f'{name}: window {sm}:{ss}-{em}:{es} != {seconds}s'
assert start == expected_start, f'{name}: gap/overlap at {sm}:{ss}'
...
assert total == 180, f'segments sum to {total}, not 180'
```

Command run:

```
C:/Users/shubh/Projects/sewacircle/.venv/Scripts/python.exe C:/Users/shubh/AppData/Local/hermes/profiles/researcher/cache/scratch/r5_timing_proof.py
```

Real output (exit code 0):

```
 1. Hook: today's manual roster vs our baseline             00:00-00:15 seconds= 15 cumulative= 15
 2. Hindi task in                                           00:15-00:35 seconds= 20 cumulative= 35
 3. Roles extracted                                         00:35-00:55 seconds= 20 cumulative= 55
 4. CP-SAT roster with reasons                              00:55-01:25 seconds= 30 cumulative= 85
 5. Fairness toggle                                         01:25-01:40 seconds= 15 cumulative=100
 6. Drop-a-volunteer heal                                   01:40-02:00 seconds= 20 cumulative=120
 7. Why-not-X counterfactual                                02:00-02:15 seconds= 15 cumulative=135
 8. Contribution card + rules + host confirm                02:15-02:40 seconds= 25 cumulative=160
 9. Hash-chain ledger + export                              02:40-02:55 seconds= 15 cumulative=175
10. Close: measured outcome + reproducibility               02:55-03:00 seconds=  5 cumulative=180
TOTAL_SECONDS=180
PROOF OK: parsed demo segments sum to 180 seconds
```

### Command 3 — deliverable section/source count check

Command and output are quoted verbatim in the "Verification of deliverable structure" section above.

### Research tooling log (non-shell calls, recorded for completeness)

- `web_search` queries (5): `site:w3.org/WAI low literacy cognitive accessibility tutorial plain language symbols`; `site:w3.org/International Devanagari font size Hindi CSS language tag authoring Indian languages`; `site:playwright.dev/docs/test-cli --video flag playwright test CLI record video`; `site:nngroup.com articles progressive disclosure undo user control system status visibility`; `GIGW 3.0 guidelines Indian government websites Hindi accessibility font size MeitY official`.
- `web_extract` URL attempts: 24 (see count section below).
- `browser_exec` navigations: 16 across five batches (full URLs among the 24 substantive sources and the blocked list below).
- `read_file` (read-only, required): `docs/COMMON.md`, `docs/lanes/C-research/TASK.md`, `C:/Users/shubh/Projects/ai-kaushal-research/lanes/K2-winners/reports/batch1-a-gov-winners.md`, `batch1-b-ai-sponsor-winners.md`. All four were read in the first tool batch.

## Sources opened (title — URL — date)

All 24 below returned substantive content and are cited in the deliverable. "accessed 2026-11-18" means opened in this research pass.

1. Meet the winners of OpenAI Build Week — https://developers.openai.com/blog/build-week-winners — accessed 2026-11-18
2. Meet the winners of India's largest GenAI buildathon at India AI Impact Summit 2026 (India Today) — https://www.indiatoday.in/education-today/news/story/meet-the-winners-of-indias-largest-genai-buildathon-at-india-ai-impact-summit-2026-2870537-2026-02-19 — published 2026-02-19
3. Meet the winners of our Built with Opus 4.6 Claude Code hackathon (Anthropic) — https://claude.com/resources/articles/meet-the-winners-of-our-built-with-opus-4-6-claude-code-hackathon — published 2026-04-20
4. Meet the students that are changing the world through technology (Google) — https://blog.google/innovation-and-ai/technology/developers-tools/meet-the-students-that-are-changing-the-world-through-technology/ — published 2024-07-01
5. Winners — AI Agents Hackathon 2025 (Microsoft) — https://microsoft.github.io/AI_Agents_Hackathon/winners/ — accessed 2026-11-18
6. SIH 2025 Grand Finale Result (official) — https://www.sih.gov.in/sih2025/sih2025-grand-finale-result — accessed 2026-11-18
7. 10 Usability Heuristics Applied to Complex Applications (NN/G) — https://www.nngroup.com/articles/usability-heuristics-complex-applications/ — accessed 2026-11-18
8. Visibility of System Status (NN/G) — https://www.nngroup.com/articles/visibility-system-status/ — accessed 2026-11-18
9. Progressive Disclosure (NN/G) — https://www.nngroup.com/articles/progressive-disclosure/ — accessed 2026-11-18
10. WCAG 2.2 (W3C Recommendation) — https://www.w3.org/TR/WCAG22/ — 2024-12-12
11. GIGW 3.0 Guidelines — https://guidelines.india.gov.in/guidelines/ — accessed 2026-11-18
12. GIGW 3.0 Accessibility: Guidelines and attributes — https://guidelines.india.gov.in/accessibility-guidelines-and-attributes/ — accessed 2026-11-18
13. Devanagari Layout Requirements (W3C i18n) — https://www.w3.org/International/ilreq/devanagari/ — accessed 2026-11-18
14. W3C i18n stylesheet article-2022.css — https://www.w3.org/International/style/article-2022.css — accessed 2026-11-18
15. WAI pattern: Use Icons that Help the User — https://www.w3.org/WAI/WCAG2/supplemental/patterns/o1p07-icons-used/ — content first published 2021-04-29, pattern posted 2022-01
16. WAI pattern: Use Literal Language — https://www.w3.org/WAI/WCAG2/supplemental/patterns/o3p04-literal-language/ — content first published 2021-04-29, pattern posted 2022-01
17. Videos (Playwright) — https://playwright.dev/docs/videos — accessed 2026-11-18
18. TestOptions (Playwright API) — https://playwright.dev/docs/api/class-testoptions — accessed 2026-11-18
19. Browser (Playwright API) — https://playwright.dev/docs/api/class-browser — accessed 2026-11-18
20. Command line (Playwright) — https://playwright.dev/docs/test-cli — accessed 2026-11-18
21. Configuration/use (Playwright) — https://playwright.dev/docs/test-use-options — accessed 2026-11-18
22. Page (Playwright API) — https://playwright.dev/docs/api/class-page — accessed 2026-11-18
23. BrowserContext (Playwright API) — https://playwright.dev/docs/api/class-browsercontext — accessed 2026-11-18
24. FFmpeg Codecs Documentation — https://ffmpeg.org/ffmpeg-codecs.html — accessed 2026-11-18

Blocked / unusable (attempted, not counted as sources): Google Solution Challenge FAQ (fetch timeout, browser redirect to generic page); WAI `tutorials/cognitive/` (404); WCAG 2.2 Understanding "Resize Text" (browser bot check); W3C i18n `qa-html-language-declarations` (browser bot check); WAI `o3p03-familiar-words` (http error).

## Winner claims: re-verified vs not re-verified

Re-verified by opening the primary or the exact source URL named in the inherited reports:

- OpenAI Build Week: judges' four axes; 47,000 builders / 186 countries / 8,000+ projects; 8 winners sharing $100,000; veterinarian and cardiologist winners — **verified** (OpenAI primary).
- Anthropic Opus 4.6: five winner profiles, four of five not professional developers; CrossBeam 20-minute action plan and city interest — **verified** (Anthropic primary).
- Microsoft AI Agents Hackathon 2025: 18,000 registrants / 570 submissions; judging on innovation, impact, usability, solution quality, category alignment; RiskWise Best Overall — **verified** (Microsoft primary).
- Google Solution Challenge 2024: live Demo Day of 10 teams, three top prizes + People's Choice; Indian winners Spoon Share and Saheli — **verified** (Google primary).
- India Today / OpenAI Academy × NxtWave Buildathon: working prototypes rather than presentations; 70,000+ registrants, 90 finalists; LUMOS AI ~Rs 10,000, judges' practical-design quote — **verified at the exact inherited URL** (independent news report, not organiser primary).
- SIH 2025: SIH25001 / CORE_401 / Shubh Sharma / Winner / Rs 1,50,000 — **verified** (official SIH result table in browser). Tech and demo style for that team remain **NOT FOUND**.

Not re-verified and deliberately excluded from the deliverable:

- Google Solution Challenge FAQ scoring split (Impact 25 / Technology 25) — page unreachable.
- UIDAI OPI statistics (Gini 0.707, 33%, 4.35m records, etc.) — underlying page not opened in this pass.
- VYOMA winner names / PIB PRID 2310855 and AB PM-JAY / PIB PRID 2259365 — not opened in this pass.
- IndiaAI–I4C CyberGuard winners and details — not opened in this pass.
- InMobi Hack Day 2016 judging criteria and Glance AI internal hackathon details — not opened in this pass.
- Any claim that a specific SIH team used a specific technology or demo technique — NOT FOUND in the inherited reports themselves.

## Counts

- Web search queries: **5**.
- `web_extract` URL attempts: **24**; substantive content returned for **21**, three failures (Google FAQ timeout, WAI tutorials/cognitive 404, familiar-words pattern http error).
- Browser page navigations: **16** across 5 `browser_exec` calls, covering **13 distinct URLs**; three blocked/redirected (Google FAQ, WCAG Understanding Resize Text, W3C language-declaration FAQ).
- Distinct substantive sources opened: **24** (list above), matching the 24 source-table rows verified by Command 3.
- Independent primary publishers among those 24: **at least 8** (OpenAI, Anthropic, Google, SIH/Government of India, W3C, MeitY/GIGW, NN/G, FFmpeg); Playwright docs are a distinct Microsoft product documentation primary in addition.
- Required primaries threshold (3+ independent primaries) and pages threshold (5+ pages opened) are satisfied.

## UNRESOLVED items

- No normative Devanagari minimum font size was found in opened primary sources; the W3C 18px figure is a site stylesheet choice and is labelled as such.
- No team-level SIH demo descriptions were found; government-panel "demo style" conclusions remain inference from event format and news coverage.
- Google Solution Challenge FAQ scoring (and several other inherited winner details) remain unverified; do not use in the submission.
- Playwright docs opened here do **not** list a `--video` CLI flag; current version uses config `use.video`. Check `npx playwright --help` against the installed build before writing the final README.
- No demo video was recorded in this research lane, so no real file size below 15 MB has been measured yet; the deliverable gives a command to measure it, not a claimed result.
- Low-literacy suitability is inferred from WAI cognitive patterns only; no testing with actual low-literacy users was possible in this pass.
