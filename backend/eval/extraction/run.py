"""Extraction eval over 30 labelled synthetic briefs. Run from backend/:
    python -m eval.extraction.run [--model cc/claude-sonnet-5-5] [--out ../docs/extraction_<model>.json]
Scoring: predicted roles are matched to gold roles greedily by skill-set overlap ('any' matches a role with no skills).
Role recall = matched gold roles / gold roles; role precision = matched predicted roles / predicted roles;
count accuracy = matched pairs whose count is within +-1 of gold; exact count = equal counts.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _skills(r: dict) -> set[str]:
    s = set(r.get("skills") or r.get("required_skills") or [])
    return s or {"any"}


def score(gold: list[dict], pred: list[dict]) -> dict:
    used: set[int] = set()
    pairs = []
    for g in gold:
        gs = _skills(g)
        best, best_ov = None, 0
        for j, p in enumerate(pred):
            if j in used:
                continue
            ov = len(gs & _skills(p))
            if ov > best_ov:
                best, best_ov = j, ov
        if best is not None:
            used.add(best)
            pairs.append((g, pred[best]))
    return {"gold": len(gold), "pred": len(pred), "matched": len(pairs),
            "count_within1": sum(1 for g, p in pairs if abs(int(g["count"]) - int(p["count"])) <= 1),
            "count_exact": sum(1 for g, p in pairs if int(g["count"]) == int(p["count"]))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=os.environ.get("SEWA_LLM_MODEL", "cc/claude-sonnet-5-5"))
    ap.add_argument("--out", default="")
    a = ap.parse_args(argv)
    os.environ["SEWA_LLM_MODEL"] = a.model
    os.environ.setdefault("SEWA_LLM_MODE", "record")
    from app.llm import extract  # import after env is set
    data = json.loads((HERE / "briefs.json").read_text(encoding="utf-8"))
    rows = []
    for b in data["briefs"]:
        t0 = time.time()
        try:
            r = extract.extract_roles(b["text"])
            pred = [{"skills": x.required_skills, "count": x.count, "role": x.role, "confidence": x.confidence} for x in r.roles]
            err = ""
        except Exception as e:  # noqa: BLE001 - every failure is counted, never hidden
            pred, err = [], f"{type(e).__name__}: {str(e)[:120]}"
        s = score(b["gold"], pred)
        s.update(id=b["id"], lang=b["lang"], secs=round(time.time() - t0, 1), error=err, predicted_roles=pred)
        rows.append(s)
        print(f"{b['id']:<6} matched {s['matched']}/{s['gold']} gold, {s['pred']} predicted, counts+-1 {s['count_within1']}, {s['secs']}s {err}")

    def agg(rs: list[dict]) -> dict:
        g, p, m = sum(r["gold"] for r in rs), sum(r["pred"] for r in rs), sum(r["matched"] for r in rs)
        return {"briefs": len(rs), "role_recall": round(m / g, 3) if g else 0, "role_precision": round(m / p, 3) if p else 0,
                "count_within1": round(sum(r["count_within1"] for r in rs) / m, 3) if m else 0,
                "count_exact": round(sum(r["count_exact"] for r in rs) / m, 3) if m else 0,
                "failures": sum(1 for r in rs if r["error"]), "median_secs": statistics.median(r["secs"] for r in rs)}
    summary = {"model": a.model, "all": agg(rows), **{lang: agg([r for r in rows if r["lang"] == lang]) for lang in ("hi", "en", "hinglish")}}
    print("\nSUMMARY " + json.dumps(summary, ensure_ascii=False))
    print("MISSES: " + "; ".join(f"{r['id']} {r['matched']}/{r['gold']}" + (f" ({r['error']})" if r['error'] else "") for r in rows if r["matched"] < r["gold"] or r["error"]))
    if a.out:
        Path(a.out).write_text(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
