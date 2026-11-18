# SewaCircle - can an OPEN-WEIGHTS model on one GPU do the role extraction? (Kaggle GPU notebook)
# Why: a UP department may not be allowed to send youth/task data to a cloud LLM. If a 3B-7B Apache-2.0 model running on
# a single T4 reaches usable accuracy on our extraction eval, SewaCircle has an on-premise path.
# Method: clone the public repo, run the EXACT production extract_roles() code path, swapping only the model call for a
# local transformers model. Same 30 labelled synthetic briefs and the same scorer as backend/eval/extraction/run.py.
# All data is synthetic. Results are printed and saved to /kaggle/working/results.json.
import json, os, subprocess, sys, time

subprocess.run(["git", "clone", "--depth", "1", "https://github.com/shubhsaxena2020/sewacircle", "/kaggle/working/sewacircle"], check=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pydantic>=2.6", "httpx", "bitsandbytes>=0.43", "accelerate"], check=True)
sys.path.insert(0, "/kaggle/working/sewacircle/backend")

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

from app.llm import extract
from app.llm.client import extract_json
from eval.extraction.run import score

print("GPU:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "none", flush=True)
briefs = json.load(open("/kaggle/working/sewacircle/backend/eval/extraction/briefs.json", encoding="utf-8"))["briefs"]
MODELS = ["Qwen/Qwen2.5-3B-Instruct", "Qwen/Qwen2.5-7B-Instruct"]
results = {}

for model_id in MODELS:
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id, device_map="auto",
        quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16))
    load_s = time.time() - t0

    def local_complete_json(purpose, system, user, max_tokens=3000, retries=2):
        msgs = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        ids = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt").to(model.device)
        s = time.time()
        with torch.no_grad():
            out = model.generate(ids, max_new_tokens=900, do_sample=False)
        text = tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)
        return extract_json(text), {"cached": False, "model": model_id, "ms": int((time.time() - s) * 1000), "purpose": purpose}

    extract.client.complete_json = local_complete_json      # only the model call changes
    rows = []
    for b in briefs:
        s = time.time()
        try:
            r = extract.extract_roles(b["text"])
            pred = [{"skills": x.required_skills, "count": x.count} for x in r.roles]
            err = ""
        except Exception as e:  # every failure is counted
            pred, err = [], f"{type(e).__name__}: {str(e)[:100]}"
        sc = score(b["gold"], pred)
        sc.update(id=b["id"], lang=b["lang"], secs=round(time.time() - s, 1), error=err)
        rows.append(sc)
        print(model_id, b["id"], f"{sc['matched']}/{sc['gold']}", f"{sc['secs']}s", err, flush=True)

    def agg(rs):
        g, p, m = sum(r["gold"] for r in rs), sum(r["pred"] for r in rs), sum(r["matched"] for r in rs)
        return {"briefs": len(rs), "role_recall": round(m / g, 3) if g else 0, "role_precision": round(m / p, 3) if p else 0,
                "count_exact": round(sum(r["count_exact"] for r in rs) / m, 3) if m else 0,
                "failures": sum(1 for r in rs if r["error"]),
                "median_secs": sorted(r["secs"] for r in rs)[len(rs) // 2]}
    results[model_id] = {"load_secs": round(load_s, 1), "all": agg(rows),
                         **{lg: agg([r for r in rows if r["lang"] == lg]) for lg in ("hi", "en", "hinglish")}, "rows": rows}
    print("SUMMARY", model_id, json.dumps({k: v for k, v in results[model_id].items() if k != "rows"}), flush=True)
    del model
    torch.cuda.empty_cache()

json.dump(results, open("/kaggle/working/results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("DONE")
