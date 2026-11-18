# Idea form — SewaCircle Mission Assurance

Draft for the five fields shown on the [official AI Kaushal form](https://www.inmobi.com/ai-kaushal). Each answer is a single paragraph to paste without the heading or count. Counts are Unicode code points via Python `len()` after NFC normalization, including spaces/punctuation and excluding headings. The form displays a 500-character limit; this draft targets at most 480. No form has been submitted by this document.

**Project name:** SewaCircle Mission Assurance

## Q1. How does your solution address UC16? — 434 characters

A district organiser turns a Hindi or English community task into required roles, then reviews an AI draft before assigning opt-in volunteers by skill, availability and area. SewaCircle checks if the crew still covers those roles after one person drops out and shows any unmet role. After the activity, a host reviews each contribution claim against attendance. The demo uses synthetic adults and complements existing youth platforms.

## Q2. What makes it unique? Call out two features. — 420 characters

1) Mission preflight: AI extracts roles from a messy brief; a constraint solver builds a complementary crew, tests a one-person dropout and names the exact missing skill or qualified standby. 2) Role-linked closeout: a host sees the planned role, note, claimed hours and attendance together, then corrects a discrepancy before export. The distinction is the explainable decision loop, not a new directory or certificate.

## Q3. How will you build it? — 409 characters

A language model proposes structured roles with source spans and uncertainty; the organiser confirms them. OR-Tools CP-SAT assigns qualified adults under availability, area and checked-skill rules, then re-solves a dropout. A FastAPI and React app shows reasons, shortages, a host-reviewed evidence card and JSON/CSV export. Model failure opens manual entry. Synthetic data only; no government API is assumed.

## Q4. What MVP will you build in 24 hours? — 424 characters

One organiser, one community task and 20 synthetic adult profiles: edit AI-drafted roles, approve a qualified roster, drop one person to test a standby or expose a shortage, then correct one conflicting contribution card and export the record. Show a small, clearly labelled synthetic comparison with a backup-aware manual baseline and the misses. No marketplace, live youth data, minors, WhatsApp or government integration.

## Q5. Why shortlist it? — 469 characters

UC16 asks for complementary teams and contribution records. Existing portals already list opportunities and track participation; our focus is the harder organiser decision: whether a crew is ready despite a dropout, with a visible reason when it is not. AI reads field-language briefs; constrained planning and human review make the result inspectable. We will show a working synthetic end-to-end flow, baseline ties and failures, then seek a permitted programme pilot.

Character-count command, run from `docs/v2` after any edit:

```powershell
@'
from pathlib import Path
import re, unicodedata
s = Path('IDEA-ANSWERS-v3.md').read_text(encoding='utf-8')
for n, answer in re.findall(r'^## Q([1-5])[^\n]*\n\n([^\n]+)', s, re.M):
    print(f'Q{n}: {len(unicodedata.normalize("NFC", answer))}')
'@ | & '..\..\.venv\Scripts\python.exe' -
```
