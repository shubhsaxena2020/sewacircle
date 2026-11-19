# Wan 2.2 TI2V-5B smoke test on a Kaggle GPU: measures load time, generation time and peak VRAM for one short clip.
import os, subprocess, sys, time, json
os.environ["HF_HOME"] = "/tmp/hf"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-U", "diffusers>=0.35.1", "transformers>=4.55", "accelerate", "ftfy", "imageio[ffmpeg]", "bitsandbytes>=0.45"], check=True)
import torch
from diffusers import WanPipeline, AutoencoderKLWan, PipelineQuantizationConfig
from diffusers.utils import export_to_video
report = {"gpu": torch.cuda.get_device_name(0), "bf16_supported": torch.cuda.is_bf16_supported()}
print(report, flush=True)
dtype = torch.bfloat16 if report["bf16_supported"] else torch.float16
mid = "Wan-AI/Wan2.2-TI2V-5B-Diffusers"
t0 = time.time()
vae = AutoencoderKLWan.from_pretrained(mid, subfolder="vae", torch_dtype=torch.float32)
quant = PipelineQuantizationConfig(quant_backend="bitsandbytes_4bit", quant_kwargs={"load_in_4bit": True, "bnb_4bit_quant_type": "nf4", "bnb_4bit_compute_dtype": dtype}, components_to_quantize=["transformer"])
pipe = WanPipeline.from_pretrained(mid, vae=vae, torch_dtype=dtype, quantization_config=quant)
pipe.enable_model_cpu_offload()
pipe.vae.enable_tiling()
report["load_s"] = round(time.time() - t0, 1)
prompt = ("Handcrafted layered paper-cut diorama of a small village in Uttar Pradesh at golden dawn, terracotta tiled roofs, "
          "mustard field, paper river, a wooden notice board, faceless paper figures walking in, soft shadows between paper layers, "
          "visible paper fibre, slow cinematic dolly forward, stop-motion feel, warm light")
neg = "photorealistic, plastic, 3d render, text, watermark, blurry, distorted faces"
for name, (w, h, frames, steps) in {"small": (704, 384, 33, 30), "short": (832, 480, 49, 30)}.items():
    torch.cuda.reset_peak_memory_stats(); t1 = time.time()
    try:
      out = pipe(prompt=prompt, negative_prompt=neg, width=w, height=h, num_frames=frames, num_inference_steps=steps, guidance_scale=5.0).frames[0]
    except torch.OutOfMemoryError as e:
      report[name] = {"oom": str(e)[:200]}; print(report, flush=True); torch.cuda.empty_cache(); continue
    report[name] = {"size": f"{w}x{h}", "frames": frames, "steps": steps, "gen_s": round(time.time() - t1, 1),
                    "peak_vram_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2)}
    export_to_video(out, f"/kaggle/working/wan_{name}.mp4", fps=24)
    print(report, flush=True)
json.dump(report, open("/kaggle/working/report.json", "w"), indent=1)
