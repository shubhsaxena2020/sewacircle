#!/usr/bin/env python3
"""Pass 2: split Sources section from body; count source entries, check each has
a date, detect duplicates INSIDE the Sources section (real defect) vs
body+sources pairing (expected cross-reference style). Also audit up_districts.json.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(r"C:/Users/shubh/Projects/sewacircle")
RESEARCH = ROOT / "docs" / "research"

URL_RE = re.compile(r"https?://[^\s<>\"'`\)\]\|]+")
DATE_RE = re.compile(
    r"(?:\b(?:19|20)\d{2}-\d{2}-\d{2}\b)"
    r"|(?:\b\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (?:19|20)\d{2}\b)"
    r"|(?:\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.? \d{1,2},? (?:19|20)\d{2}\b)"
    r"|(?:\b(?:19|20)\d{2}\b)"
)


def split_sources(text: str):
    lines = text.splitlines()
    idx = None
    for i, line in enumerate(lines):
        if line.strip() == "## Sources":
            idx = i
            break
    if idx is None:
        return text, "", 0
    return "\n".join(lines[:idx]), "\n".join(lines[idx + 1:]), idx + 1


print("=" * 78)
print("PASS 2 — Sources-section integrity")
print("=" * 78)
print(f"{'file':26} {'body':>5} {'srcSec':>6} {'entries':>7} {'dup-in-src':>10} {'no-date':>7}")
print("-" * 78)

details: dict[str, dict] = {}
for f in sorted(RESEARCH.glob("*.md")):
    text = f.read_text(encoding="utf-8", errors="replace")
    body, src, src_line = split_sources(text)
    body_urls = [u.rstrip(".,;:") for u in URL_RE.findall(body)]
    src_urls = [u.rstrip(".,;:") for u in URL_RE.findall(src)]

    # source entries = numbered / bulleted lines, plus markdown table data rows
    entries = []
    for ln in src.splitlines():
        if re.match(r"^\s*(?:\d+[\.\)]|[-*])\s+\S", ln):
            entries.append(ln.strip())
        elif re.match(r"^\s*\|\s*\d+\s*\|", ln):
            entries.append(ln.strip())

    seen: dict[str, int] = {}
    for u in src_urls:
        seen[u] = seen.get(u, 0) + 1
    dup_in_src = {u: c for u, c in seen.items() if c > 1}

    no_date = [e for e in entries if not DATE_RE.search(e)]

    print(
        f"{f.name:26} {len(body_urls):5d} {len(src_urls):6d} {len(entries):7d} "
        f"{len(dup_in_src):10d} {len(no_date):7d}"
    )

    details[f.name] = {
        "body_urls": len(body_urls),
        "src_urls": len(src_urls),
        "entries": len(entries),
        "entries_no_date": no_date,
        "entries_no_url": [e for e in entries if not URL_RE.search(e)],
        "dup_in_src": dup_in_src,
        "src_line": src_line,
        "body_only": sorted(set(body_urls) - set(src_urls)),
        "src_only": sorted(set(src_urls) - set(body_urls)),
    }

print()
for name, d in details.items():
    print(f"--- {name} (Sources @L{d['src_line']}) entries={d['entries']}")
    if d["dup_in_src"]:
        for u, c in d["dup_in_src"].items():
            print(f"    DUP-IN-SOURCES x{c}: {u}")
    if d["entries_no_date"]:
        for e in d["entries_no_date"]:
            print(f"    ENTRY WITHOUT DATE: {e[:170]}")
    if d["entries_no_url"]:
        for e in d["entries_no_url"]:
            print(f"    ENTRY WITHOUT URL:  {e[:170]}")
    if d["body_only"]:
        for u in d["body_only"]:
            print(f"    BODY-ONLY URL (not in Sources): {u}")
    print()

print("=" * 78)
print("up_districts.json AUDIT")
print("=" * 78)
p = RESEARCH / "up_districts.json"
raw = p.read_text(encoding="utf-8")
print(f"bytes={len(raw)}")
data = json.loads(raw)
print(f"top-level type: {type(data).__name__}")
print(f"top-level keys: {list(data.keys()) if isinstance(data, dict) else 'n/a'}")

if isinstance(data, dict):
    meta = {k: v for k, v in data.items() if not isinstance(v, list)}
    print("non-list keys:")
    for k, v in meta.items():
        print(f"  {k} = {v!r}")
    lists = [k for k, v in data.items() if isinstance(v, list)]
    print(f"list keys: {lists}")
    for k in lists:
        print(f"  {k}: {len(data[k])} items")
    dlist = data[lists[0]] if lists else []
else:
    dlist = data
    print(f"items: {len(dlist)}")

print()
print(f"district count: {len(dlist)}")
print("sample record:", json.dumps(dlist[0], ensure_ascii=False)[:400])
print()
print("ALL KEYS across records:", sorted({k for r in dlist if isinstance(r, dict) for k in r}))

print()
print(f"{'#':>3} {'district':22} {'lat':>9} {'lon':>9}  coord_source")
for i, r in enumerate(dlist, 1):
    nm = r.get("district") or r.get("name") or "?"
    lat = r.get("lat", r.get("latitude"))
    lon = r.get("lon", r.get("lng", r.get("longitude")))
    cs = r.get("coord_source") or r.get("source") or r.get("coordinate_source") or "MISSING"
    print(f"{i:3d} {nm:22} {str(lat):>9} {str(lon):>9}  {cs}")

names = [(r.get("district") or r.get("name")) for r in dlist if isinstance(r, dict)]
print()
print(f"unique names: {len(set(names))} / {len(names)}")
dupes = {n for n in names if names.count(n) > 1}
print(f"duplicate names: {sorted(dupes) if dupes else 'none'}")
missing_cs = [n for n, r in zip(names, dlist) if not (r.get("coord_source") or r.get("source") or r.get("coordinate_source"))]
print(f"records missing coord source: {missing_cs if missing_cs else 'none'}")
