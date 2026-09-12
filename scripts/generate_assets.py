#!/usr/bin/env python3
"""Generate foto realistis dari specs/<slug>.assets.json.

Backend (auto-pilih):
  - REPLICATE_API_TOKEN ada  -> Replicate (Flux Schnell, fotorealistik, ~$0.01/img)
  - else                      -> ComfyUI lokal (sd-turbo, CPU)

Format specs/<slug>.assets.json:
{
  "model": "replicate",            # opsional: paksa backend
  "assets": [
    {"name":"ocean-surface","prompt":"...","negative":"...","width":1024,"height":576,"seed":100000},
    ...
  ]
}
Output: assets/<slug>/<name>.png
"""
import argparse, base64, glob, io, json, os, sys, time, urllib.request, urllib.error

HOST = os.environ.get("COMFY_HOST", "http://127.0.0.1:8188")
REPLICATE = "https://api.replicate.com/v1"
TURBO_NEG = "text, watermark, blurry, low quality, deformed, illustration, cartoon, 3d render"

# Flux Schnell via model API (auto-resolve latest version) — cepat & murah
REPLICATE_MODEL = os.environ.get("REPLICATE_MODEL", "black-forest-labs/flux-schnell")


def backend():
    spec_model = _SPEC_MODEL
    if spec_model == "comfy":
        return "comfy"
    if spec_model == "replicate":
        return "replicate"
    return "replicate" if os.environ.get("REPLICATE_API_TOKEN") else "comfy"


# ---------- ComfyUI ----------
def comfy_workflow(name, prompt, negative, w, h, seed, steps=6, cfg=1.0,
                   checkpoint="sd_turbo.safetensors"):
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


def comfy_wait_output(prefix, timeout=900):
    t0 = time.time()
    while time.time() - t0 < timeout:
        hits = (glob.glob(f"/root/comfy/ComfyUI/output/{prefix}*.png") or
                glob.glob(os.path.expanduser(f"~/comfy/ComfyUI/output/{prefix}*.png")))
        if hits:
            return sorted(hits, key=os.path.getmtime)[-1]
        time.sleep(5)
    raise TimeoutError(f"output {prefix} tidak muncul dalam {timeout}s")


def gen_comfy(a, out_png):
    name = a["name"]
    prompt = a["prompt"]
    w, h = a.get("width", 1024), a.get("height", 1024)
    seed = a.get("seed", 100000)
    steps = a.get("steps", 6)
    wf = comfy_workflow(name, prompt, a.get("negative"), w, h, seed, steps=steps)
    resp = comfy_post("/prompt", {"prompt": wf, "client_id": f"ci-{name}"})
    print(f"  queued: {resp['prompt_id']}")
    src = comfy_wait_output(name)
    with open(src, "rb") as f:
        data = f.read()
    with open(out_png, "wb") as f:
        f.write(data)
    print(f"  -> {out_png} ({len(data)//1024} KB)")


def comfy_post(path, payload, timeout=600):
    req = urllib.request.Request(HOST + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


# ---------- Replicate ----------
def ar_ratio(w, h):
    r = w / h
    if abs(r - 1) < 0.05:
        return "1:1"
    if abs(r - 16/9) < 0.05:
        return "16:9"
    if abs(r - 9/16) < 0.05:
        return "9:16"
    if abs(r - 4/3) < 0.05:
        return "4:3"
    if abs(r - 3/2) < 0.05:
        return "3:2"
    return "1:1"


def gen_replicate(a, out_png):
    name = a["name"]
    token = os.environ["REPLICATE_API_TOKEN"]
    ratio = ar_ratio(a.get("width", 1024), a.get("height", 1024))
    payload = {"input": {
        "prompt": a["prompt"],
        "aspect_ratio": ratio,
        "num_outputs": 1,
        "output_format": "png",
        "num_inference_steps": a.get("steps", 4),
    }}
    if a.get("negative"):
        payload["input"]["negative_prompt"] = a["negative"]
    if a.get("seed"):
        payload["input"]["seed"] = a["seed"]
    hdrs = {"Authorization": f"Token {token}", "Content-Type": "application/json",
            "Prefer": "wait"}
    url = f"{REPLICATE}/models/{REPLICATE_MODEL}/predictions"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=hdrs)
    with urllib.request.urlopen(req, timeout=300) as r:
        pred = json.loads(r.read())
    # Prefer: wait -> langsung succeeded
    if pred.get("status") != "succeeded":
        # poll
        pid = pred["id"]
        for _ in range(120):
            time.sleep(3)
            req = urllib.request.Request(f"{REPLICATE}/predictions/{pid}", headers=hdrs)
            with urllib.request.urlopen(req, timeout=60) as r:
                pred = json.loads(r.read())
            if pred.get("status") == "succeeded":
                break
            if pred.get("status") in ("failed", "canceled"):
                raise RuntimeError(f"replicate gagal: {pred.get('error')}")
    out_url = pred["output"]
    if isinstance(out_url, list):
        out_url = out_url[0]
    with urllib.request.urlopen(out_url, timeout=120) as r:
        data = r.read()
    with open(out_png, "wb") as f:
        f.write(data)
    print(f"  -> {out_png} ({len(data)//1024} KB)")


# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--steps", type=int, default=6)
    ap.add_argument("--host", default=HOST)
    args = ap.parse_args()

    spec = json.load(open(args.spec))
    assets = spec["assets"]
    _SPEC_MODEL = spec.get("model")
    be = backend()
    os.makedirs(args.output, exist_ok=True)
    print(f"backend: {be} | assets: {len(assets)}")

    for i, a in enumerate(assets):
        name = a["name"]
        out_png = os.path.join(args.output, f"{name}.png")
        if os.path.exists(out_png):
            print(f"[{i+1}/{len(assets)}] {name}: sudah ada, skip")
            continue
        print(f"[{i+1}/{len(assets)}] {name}: {a.get('width',1024)}x{a.get('height',1024)}")
        try:
            if be == "replicate":
                gen_replicate(a, out_png)
            else:
                gen_comfy(a, out_png)
        except Exception as e:
            print(f"  GAGAL {name}: {e}")
            if be == "replicate" and os.environ.get("REPLICATE_API_TOKEN"):
                print("  fallback ke ComfyUI...")
                _SPEC_MODEL = "comfy"
                gen_comfy(a, out_png)
            else:
                raise

    print("SEMUA ASSET SELESAI")


if __name__ == "__main__":
    main()
