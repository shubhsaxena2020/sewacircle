#!/usr/bin/env python3
"""Pass 3: cross-file numeric consistency + up_districts.json bbox/label checks."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"C:/Users/shubh/Projects/sewacircle")
DOCS = ROOT / "docs" / "research"
REP = ROOT / "docs" / "lanes" / "C-research" / "reports"
URL_RE = re.compile(r"https?://[^\s<>\"'`\)\]\|]+")

print("=" * 78)
print("A. distinct URL counts: Sources section vs whole file vs stated count")
print("=" * 78)
stated = {
    "R1-optimization.md": None,
    "R2-nlp-hindi.md": 20,          # R2-report: "20 distinct URLs successfully opened"
    "R3-credentials-privacy.md": 25,  # md line 159 + R3-report line 302
    "R4-up-realism.md": 28,          # R4-report: "Distinct URLs with usable content 28"
    "R5-demo-ux.md": None,
    "R6-eval-responsible-ai.md": 16,  # md line 210: "16 distinct URLs attempted"
}
print(f"{'file':26} {'srcEntries':>10} {'srcURLs':>8} {'srcUniq':>8} {'fileUniq':>9} {'stated':>7} {'match':>6}")
print("-" * 78)
for f in sorted(DOCS.glob("*.md")):
    text = f.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    idx = next((i for i, l in enumerate(lines) if l.strip() == "## Sources"), None)
    src = "\n".join(lines[idx + 1:]) if idx is not None else ""
    src_urls = [u.rstrip(".,;:") for u in URL_RE.findall(src)]
    entries = [l for l in src.splitlines()
               if re.match(r"^\s*(?:\d+[\.\)]|[-*])\s+\S", l)
               or re.match(r"^\s*\|\s*\d+\s*\|", l)]
    file_uniq = {u.rstrip(".,;:") for u in URL_RE.findall(text)}
    st = stated.get(f.name)
    ok = "n/a" if st is None else ("YES" if st == len(set(src_urls)) else "NO")
    print(f"{f.name:26} {len(entries):10d} {len(src_urls):8d} {len(set(src_urls)):8d} "
          f"{len(file_uniq):9d} {str(st):>7} {ok:>6}")

print()
print("=" * 78)
print("B. R5 demo timing sum")
print("=" * 78)
r5 = (DOCS / "R5-demo-ux.md").read_text(encoding="utf-8")
rows = re.findall(r"^\|\s*(\d+)\s*\|\s*(\d\d:\d\d)-(\d\d:\d\d)\s*\|[^|]*\|\s*(\d+)\s*\|", r5, re.M)
secs = [int(s) for *_x, s in rows]
print(f"rows parsed: {len(rows)}  seconds: {secs}")
print(f"sum = {sum(secs)} s   claimed = 180 s   match = {sum(secs) == 180}")
# check each row's HH:MM window width equals its seconds
bad = []
for n, t0, t1, s in rows:
    m0 = int(t0[:2]) * 60 + int(t0[3:])
    m1 = int(t1[:2]) * 60 + int(t1[3:])
    if m1 - m0 != int(s):
        bad.append((n, t0, t1, s, m1 - m0))
print(f"rows whose clock window != stated seconds: {bad if bad else 'none'}")

print()
print("=" * 78)
print("C. up_districts.json validation")
print("=" * 78)
d = json.loads((DOCS / "up_districts.json").read_text(encoding="utf-8"))
ds = d["districts"]
print(f"synthetic_data_label present: {'synthetic_data_label' in d} / non-empty: {bool(d.get('synthetic_data_label'))}")
print(f"coordinate_source_url present: {bool(d.get('coordinate_source_url'))}")
print(f"retrieved_date: {d.get('retrieved_date')}")
print(f"district count: {len(ds)}")
LAT = (23.5, 30.5)   # R4-report asserted bbox
LON = (77.0, 84.5)
oob, nosrc, badtype = [], [], []
for r in ds:
    lat, lon = r.get("lat"), r.get("lon")
    if not (isinstance(lat, (int, float)) and isinstance(lon, (int, float))):
        badtype.append(r.get("name"))
        continue
    if not (LAT[0] <= lat <= LAT[1] and LON[0] <= lon <= LON[1]):
        oob.append((r.get("name"), lat, lon))
    if not r.get("source"):
        nosrc.append(r.get("name"))
print(f"lat bbox {LAT} lon bbox {LON}")
print(f"out of bbox: {oob if oob else 'none (0)'}")
print(f"rows missing per-row source: {nosrc if nosrc else 'none'}")
print(f"non-numeric coords: {badtype if badtype else 'none'}")
print(f"all rows have source_record_id: {all(r.get('source_record_id') for r in ds)}")

# duplicate coordinate pairs
pairs = [(r['lat'], r['lon']) for r in ds]
dupepairs = {p for p in pairs if pairs.count(p) > 1}
print(f"duplicate coordinate pairs: {sorted(dupepairs) if dupepairs else 'none'}")

print()
print("=" * 78)
print("D. named districts vs R4 report's expected 20")
print("=" * 78)
names = [r["name"] for r in ds]
print("names:", ", ".join(names))
print(f"count={len(names)} unique={len(set(names))}")

print()
print("=" * 78)
print("E. key cross-file numbers")
print("=" * 78)
checks = [
    ("R1 Gini base 0.2338", "R1-optimization.md", r"0\.2338"),
    ("R1 Gini cap 0.3117", "R1-optimization.md", r"0\.3117"),
    ("R6 repeats 0.2338 -> 0.3117", "R6-eval-responsible-ai.md", r"0\.2338 to 0\.3117"),
    ("R1 base runtime 0.0134", "R1-optimization.md", r"0\.0134"),
    ("R6 cites 0.0134 as R1 original", "R6-eval-responsible-ai.md", r"0\.0134"),
    ("R1 fairness runtime 0.0213", "R1-optimization.md", r"0\.0213"),
    ("R4 exactly 20 districts", "R4-up-realism.md", r"exactly 20 real Uttar Pradesh"),
    ("R6 10 tasks", "R6-eval-responsible-ai.md", r"10 labelled tasks"),
    ("R2 10-task guide", "R2-nlp-hindi.md", r"\*\*10-task annotation guide"),
]
for label, fname, pat in checks:
    hit = re.search(pat, (DOCS / fname).read_text(encoding="utf-8"))
    print(f"{'FOUND' if hit else 'MISSING':8} {label:34} ({fname})")

# volunteer-count mentions
print()
for fname in sorted(p.name for p in DOCS.glob("*.md")):
    txt = (DOCS / fname).read_text(encoding="utf-8")
    for m in re.finditer(r"[^\n.]{0,90}\b(9|30|40)\b[^\n.]{0,40}volunteers?[^\n.]{0,40}", txt):
        print(f"{fname}: ...{m.group(0).strip()[:150]}")
