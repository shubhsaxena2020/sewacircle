#!/usr/bin/env python3
"""PROOF COMMAND: URL + section-heading extractor for docs/research/*.md.

Walks docs/research/*.md, regex-extracts http(s) URLs (code fences excluded from
heading scan but URLs are taken from the whole file), prints per-file URL counts,
duplicate count, and any URL not matching ^https?://[^ ]+\\.[a-z]{2,}, plus counts
of the four required sections per file.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(r"C:/Users/shubh/Projects/sewacircle")
RESEARCH = ROOT / "docs" / "research"

URL_RE = re.compile(r"https?://[^\s<>\"'`\)\]\|]+")
VALID_RE = re.compile(r"^https?://[^ ]+\.[a-z]{2,}")
REQUIRED = [
    "## Findings",
    "## Recommendation for our build",
    "## Risks",
    "## Sources",
]


def strip_fences(text: str) -> list[tuple[int, str]]:
    """Return (raw_lineno, line) pairs with fenced code blocks removed.

    Line numbers stay TRUE to the file on disk so findings can be cited.
    """
    out: list[tuple[int, str]] = []
    in_fence = False
    for i, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append((i, line))
    return out


def main() -> int:
    files = sorted(RESEARCH.glob("*.md"))
    if not files:
        print("NO FILES FOUND under", RESEARCH)
        return 1

    print(f"root: {RESEARCH}")
    print(f"files: {len(files)}")
    print()
    hdr = f"{'file':28} {'URLs':>5} {'uniq':>5} {'dupes':>6} {'malformed':>10}  sections"
    print(hdr)
    print("-" * len(hdr))

    total_urls = total_dupes = total_bad = 0
    problems: list[str] = []
    section_map: dict[str, list[str]] = {}

    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")

        urls = [u.rstrip(".,;:") for u in URL_RE.findall(text)]
        seen: dict[str, int] = {}
        for u in urls:
            seen[u] = seen.get(u, 0) + 1
        dupes = {u: c for u, c in seen.items() if c > 1}
        bad = [u for u in urls if not VALID_RE.match(u)]

        # heading order check (fence-aware, exact-line match, raw line numbers)
        pairs = strip_fences(text)
        found_order: list[str] = []
        positions: dict[str, list[int]] = {s: [] for s in REQUIRED}
        for lineno, line in pairs:
            s = line.strip()
            if s in REQUIRED:
                positions[s].append(lineno)
                if s not in found_order:
                    found_order.append(s)
        for s in REQUIRED:
            if len(positions[s]) > 1:
                problems.append(
                    f"{f.name}: duplicate heading {s!r} at lines {positions[s]}"
                )

        missing = [s for s in REQUIRED if s not in found_order]
        in_order = found_order == [s for s in REQUIRED if s in found_order]
        if missing:
            sec_stat = "MISSING:" + ",".join(m.replace("## ", "") for m in missing)
        elif in_order:
            sec_stat = "OK 4/4 in order"
        else:
            sec_stat = "ALL4 OUT OF ORDER:" + ">".join(
                s.replace("## ", "") for s in found_order
            )

        section_map[f.name] = [
            f"{s.replace('## ', '')} @L{positions[s][0]}" for s in REQUIRED
            if positions[s]
        ]

        print(
            f"{f.name:28} {len(urls):5d} {len(seen):5d} {len(dupes):6d} "
            f"{len(bad):10d}  {sec_stat}"
        )

        if dupes:
            for u, c in sorted(dupes.items()):
                problems.append(f"{f.name}: DUPLICATE URL x{c}: {u}")
                # locate first line
                for i, line in enumerate(text.splitlines(), start=1):
                    if u in line:
                        problems.append(f"    first at L{i}: {line.strip()[:140]}")
                        break
        for u in bad:
            problems.append(f"{f.name}: MALFORMED URL: {u}")

        total_urls += len(urls)
        total_dupes += len(dupes)
        total_bad += len(bad)

    print()
    print(f"TOTALS: urls={total_urls} duplicate_urls={total_dupes} malformed={total_bad}")
    print()
    print("SECTION HEADINGS (line numbers):")
    for name, secs in section_map.items():
        print(f"  {name}: {' | '.join(secs)}")

    print()
    if problems:
        print(f"PROBLEMS ({len(problems)}):")
        for p in problems:
            print("  -", p)
    else:
        print("PROBLEMS: none")

    return 0


if __name__ == "__main__":
    sys.exit(main())
