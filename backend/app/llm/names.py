"""Person-name protection before any text reaches a language model.

Two layers:
1. pseudonymise(): names of people we KNOW (the roster) are replaced by their volunteer id token, e.g. "Asha K." -> "[v-008]".
   The model works with ids only; results are mapped back by id. Exact, so it never misses a rostered person.
2. mask_names(): any other Title-Case word found in a ~61k-entry Indian name gazetteer (3 Kaggle datasets; see data/README.md)
   becomes "[NAME]". A small stop-list keeps common words that are also names (ASHA workers, Seva, Bharat ...) intact.
Limits (stated, measured in tests/eval): Latin script only, so Devanagari names are not masked; names outside the list
are missed; lower-case names are not masked (to avoid hitting ordinary words).
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

_STOP = {"Asha", "Seva", "Sewa", "Bharat", "Shanti", "Jai", "Will", "May", "Mark", "Rose", "Grace", "Hope", "Joy",
         "Sunny", "Deep", "Saturday", "Sunday", "Monday", "Camp", "Team", "Health", "Ganga", "Ram",
         "Sadar", "Pali", "Tehsil", "Block", "Nagar", "Ganj", "Pur", "Bazar", "Mandi", "Chowk", "Gali", "Ward"}  # UP admin/place words


@lru_cache(maxsize=1)
def gazetteer() -> frozenset[str]:
    p = Path(__file__).with_name("data") / "indian_names_merged.txt"
    return frozenset(w.strip() for w in p.read_text(encoding="utf-8").splitlines() if w.strip() and w.strip() not in _STOP)


def pseudonymise(text: str, known: dict[str, str]) -> tuple[str, int]:
    """known: display name -> token. Replaces the full display name and its first word (longest first). Returns (text, count)."""
    n = 0
    variants: list[tuple[str, str]] = []
    for name, token in known.items():
        variants.append((name, token))
        first = name.split()[0]
        if len(first) >= 3:
            variants.append((first, token))
    for name, token in sorted(variants, key=lambda kv: -len(kv[0])):
        pattern = re.compile(rf"(?<![\w\[]){re.escape(name)}(?![\w\]])")
        text, k = pattern.subn(f"[{token}]", text)
        n += k
    return text, n


def mask_names(text: str) -> tuple[str, int]:
    g = gazetteer()
    count = 0

    def sub(m: re.Match[str]) -> str:
        nonlocal count
        if m.group(0) in g:
            count += 1
            return "[NAME]"
        return m.group(0)
    return re.sub(r"(?<![\w\[])[A-Z][a-z]{2,}(?![\w\]])", sub, text), count
