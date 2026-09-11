#!/usr/bin/env python3
"""Generate foto realistis via ComfyUI (CPU runner) dari specs/<slug>.assets.json.
Format assets.json:
{
  "assets": [
    {"name": "ocean-surface", "prompt": "aerial photo of deep blue ocean surface ...", "negative": "...", "width": 1024, "height": 1024},
    ...
  ]
}
Output: assets/<slug>/<name>.png (satu per asset), log per-image.
"""
import argparse, base64, glob, json, os, sys, time, urllib.request, urllib.error

HOST = os.environ.get("COMFY_HOST", "http://127.0.0.1:8188")
TURBO_NEG = "text, watermark, blurry, low quality, deformed"

def post(path, payload, timeout=600):
    req = urllib.request.Request(HOST + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def workflow(name, prompt, negative, w, h, seed, steps=6, cfg=1.0, checkpoint="sd_turbo.safetensors"):
    # sd-turbo: cfg 1.0, steps 4-8, tanpa negative efektif (CFG=1 skip). API-format workflow.
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "_meta": {"title": "ckpt"},
              "inputs": {"ckpt_name": checkpoint}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": negative or TURBO_NEG, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {
            "seed": seed, "steps": steps, "cfg": cfg, "sampler_name": "euler",
            "scheduler": "simple", "denoise": 1.0,
            "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0],
            "latent_image": ["4", 0]}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"filename_prefix": name, "images": ["6", 0]}},
    }

def wait_output(prefix, timeout=900):
    t0 = time.time()
    while time.time() - t0 < timeout:
        hits = glob.glob(f"/root/comfy/ComfyUI/output/{prefix}*.png") or \
               glob.glob(os.path.expanduser(f"~/comfy/ComfyUI/output/{prefix}*.png"))
        if hits:
            return sorted(hits, key=os.path.getmtime)[-1]
        time.sleep(5)
    raise TimeoutError(f"output {prefix} tidak muncul dalam {timeout}s")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--steps", type=int, default=6)
    ap.add_argument("--host", default=HOST)
    args = ap.parse_args()

    spec = json.load(open(args.spec))
    assets = spec["assets"]
    os.makedirs(args.output, exist_ok=True)
    print(f"assets: {len(assets)} — host {args.host}")

    for i, a in enumerate(assets):
        name = a["name"]
        prompt = a["prompt"]
        w, h = a.get("width", 1024), a.get("height", 1024)
        seed = a.get("seed", 100000 + i)
        steps = a.get("steps", args.steps)
        out_png = os.path.join(args.output, f"{name}.png")
        if os.path.exists(out_png):
            print(f"[{i+1}/{len(assets)}] {name}: sudah ada, skip")
            continue
        print(f"[{i+1}/{len(assets)}] {name}: {w}x{h} steps={steps} seed={seed}")
        wf = workflow(name, prompt, a.get("negative"), w, h, seed, steps=steps)
        resp = post("/prompt", {"prompt": wf, "client_id": f"ci-{name}"})
        pid = resp["prompt_id"]
        print(f"  queued: {pid}")
        src = wait_output(name)
        # copy hasil
        with open(src, "rb") as f:
            data = f.read()
        with open(out_png, "wb") as f:
            f.write(data)
        print(f"  -> {out_png} ({len(data)//1024} KB)")

    print("SEMUA ASSET SELESAI")

if __name__ == "__main__":
    main()
