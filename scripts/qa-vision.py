#!/usr/bin/env python3
"""Vision QA: kirim frame qa/*.png ke model vision, tulis qa-report.md.
Exit 1 jika ada ISSUE (gagal CI). Env: VISION_API_KEY, VISION_BASE_URL, VISION_MODEL.
"""
import base64, glob, json, os, sys, urllib.request

KEY = os.environ["VISION_API_KEY"]
BASE = os.environ.get("VISION_BASE_URL", "https://ruter.dapzero.me/v1")
MODEL = os.environ.get("VISION_MODEL", "or/inclusionai/ling-3.0-flash-vl:free")
PROMPT = ("Frame 720x1280 dari animasi edukasi. Tugas QA visual: "
          "1) teks bertabrakan dengan teks/gambar? 2) teks/gambar terpotong tepi frame secara salah? "
          "3) ilustrasi tidak jelas, ngasal, atau tidak sesuai tema? "
          "Jika bersih jawab persis: OK. Jika ada masalah, satu baris per masalah, awali 'ISSUE: '.")

def ask(path):
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    body = {"model": MODEL, "messages": [
        {"role": "system", "content": "Anda QA visual. Jawab HANYA: OK, atau baris 'ISSUE: <masalah>'. Maksimal 3 baris, tanpa penjelasan."},
        {"role": "user", "content": [
            {"type": "text", "text": PROMPT},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + b64}}]}],
        "max_tokens": 2500}
    req = urllib.request.Request(BASE + "/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0 Chrome/126"})
    raw = urllib.request.urlopen(req, timeout=170).read().decode()
    # gateway kadang output bukan JSON murni; robust: cari objek chat.completion
    d = None
    try:
        dec = json.JSONDecoder(); pos = 0
        while pos < len(raw):
            while pos < len(raw) and raw[pos] in " \n\r\t": pos += 1
            if pos >= len(raw): break
            o, pos = dec.raw_decode(raw, pos)
            if isinstance(o, dict) and "choices" in o: d = o
    except Exception:
        pass
    if d is None:
        raise RuntimeError("bad gateway response: " + raw[:120])
    m = d["choices"][0]["message"]
    c = (m.get("content") or "").strip()
    if not c and m.get("reasoning"):
        # model habis di reasoning: anggap perlu review manual
        c = "ISSUE: (model reasoning tidak selesai — review manual) " + m["reasoning"][-200:]
    return c

lines, issues = [], 0
for f in sorted(glob.glob("qa/*.png")):
    out = "[QA-ERROR] request gagal"
    for i in range(5):  # retry rate-limit / jaringan / 503
        try:
            out = ask(f); break
        except Exception as e:
            out = f"[QA-ERROR] {str(e)[:120]}"
            import time; time.sleep(20)
    frame_issues = [l for l in out.splitlines() if l.strip().startswith("ISSUE:")] if not out.startswith("[QA-ERROR]") else [out]
    issues += len(frame_issues)
    lines.append(f"## {f}\n{out}\n")

verdict = "FAIL" if issues else "PASS"
report = f"# QA Report — vision\n\nModel: {MODEL}\nFrames: {len(lines)}\nIssues: {issues}\n\nVerdict: **{verdict}**\n\n" + "\n".join(lines)
open("qa-report.md", "w").write(report)
print(report[:900])
sys.exit(1 if issues else 0)
