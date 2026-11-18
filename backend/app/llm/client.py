"""LLM provider interface with record/replay cache. OWNED BY HEAD. Lane B builds extraction/drafting on top of complete_json().

Modes (env SEWA_LLM_MODE): record (default: cache hit else live call then store), live (always call), replay (cache only, error on miss).
Default model: Claude Sonnet 5.5 via 9Router (OpenAI-compatible). DeepSeek via Nilabh is a reasoning model and returns empty
content at low max_tokens, so it is NOT used by the app.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any

import httpx

CACHE_DIR = Path(__file__).resolve().parents[2] / "data" / "llm_cache"


class LLMError(RuntimeError):
    pass


def _cfg() -> dict[str, str]:
    return {
        "base": os.environ.get("SEWA_LLM_BASE_URL", "http://127.0.0.1:20128/v1"),
        "key": os.environ.get("SEWA_LLM_API_KEY") or os.environ.get("NINEROUTER_API_KEY", ""),
        "model": os.environ.get("SEWA_LLM_MODEL", "cc/claude-sonnet-5-5"),
        "mode": os.environ.get("SEWA_LLM_MODE", "record"),
    }


def extract_json(text: str) -> Any:
    """Tolerant JSON extraction: strips code fences and surrounding prose."""
    if text is None:
        raise LLMError("empty content (reasoning model out of tokens?)")
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t, flags=re.S)
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass
    start = min([i for i in (t.find("{"), t.find("[")) if i != -1], default=-1)
    if start == -1:
        raise LLMError(f"no JSON found in: {t[:120]!r}")
    for end in range(len(t), start, -1):
        if t[end - 1] in "}]":
            try:
                return json.loads(t[start:end])
            except json.JSONDecodeError:
                continue
    raise LLMError(f"unparseable JSON: {t[:120]!r}")


def _key(model: str, system: str, user: str, max_tokens: int) -> str:
    return hashlib.sha256(json.dumps([model, system, user, max_tokens], ensure_ascii=False).encode()).hexdigest()


def complete_json(purpose: str, system: str, user: str, max_tokens: int = 3000, retries: int = 2) -> tuple[Any, dict[str, Any]]:
    """Return (parsed_json, meta). meta: {cached, model, ms, purpose}."""
    c = _cfg()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    k = _key(c["model"], system, user, max_tokens)
    path = CACHE_DIR / f"{purpose}-{k[:24]}.json"
    if c["mode"] in ("record", "replay") and path.exists():
        d = json.loads(path.read_text(encoding="utf-8"))
        return d["json"], {"cached": True, "model": d.get("model", c["model"]), "ms": 0, "purpose": purpose}
    if c["mode"] == "replay":
        raise LLMError(f"replay mode: cache miss for {purpose}")
    body = {
        "model": c["model"], "stream": False, "max_tokens": max_tokens, "temperature": 0,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
    }
    last: Exception | None = None
    for attempt in range(retries + 1):
        t0 = time.time()
        try:
            r = httpx.post(f"{c['base']}/chat/completions", json=body, timeout=120,
                           headers={"Authorization": f"Bearer {c['key']}"})
            r.raise_for_status()
            content = r.json()["choices"][0]["message"].get("content")
            parsed = extract_json(content)
            ms = int((time.time() - t0) * 1000)
            path.write_text(json.dumps({"json": parsed, "model": c["model"], "purpose": purpose}, ensure_ascii=False), encoding="utf-8")
            return parsed, {"cached": False, "model": c["model"], "ms": ms, "purpose": purpose}
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise LLMError(f"LLM call failed after {retries + 1} attempts: {last}")
