"""Anteprime brevi dei tratti modificati (720p, qualità bassa, con l'audio), 1 s prima e dopo.

Uso: python3 tools/previews.py WORK
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = sys.argv[1]
OUT = os.path.join(ROOT, "out", "preview")
RENDER = [sys.executable, os.path.join(ROOT, "tools", "render.py"), WORK]
AUDIO = os.path.join(WORK, "audio_cut.wav")
os.makedirs(OUT, exist_ok=True)

plan = json.loads(subprocess.check_output(RENDER + ["--plan"]))
DUR = plan["durata_video"]
ins = {d["name"]: d for d in plan["inserti"]}
sez = {s[0]: s for s in plan["sezioni"]}
PAD = 1.0
TRATTI = [
    ("preview_1_intro.mp4", 0.0, sez["intro"][2]),                      # fino a "Torno sul pezzo"
    ("preview_2_specchi.mp4", ins["specchi"]["t0"], ins["specchi"]["t1"]),
    ("preview_3_cervello.mp4", ins["cervello"]["t0"], ins["cervello"]["t1"]),
    ("preview_4_finale.mp4", plan["chiusura"][0], DUR),
]
res = {}
for name, a, b in TRATTI:
    t0, t1 = max(0.0, a - PAD), min(DUR, b + PAD)
    inter = os.path.join(WORK, "prev_" + name)
    subprocess.check_call(RENDER + ["--range", f"{t0:.3f},{t1:.3f}", "--out", inter, "--inter"])
    out = os.path.join(OUT, name)
    af = f"afade=t=out:st={t1 - t0 - 0.5:.3f}:d=0.5" if t1 >= DUR - 1e-3 else "anull"
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", inter, "-ss", f"{t0:.3f}", "-t", f"{t1 - t0:.3f}",
                           "-i", AUDIO, "-map", "0:v", "-map", "1:a", "-af", af, "-vf", "scale=720:1280:flags=lanczos",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "28", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out])
    res[name] = dict(da=round(t0, 2), a=round(t1, 2), tratto=[round(a, 2), round(b, 2)],
                     byte=os.path.getsize(out))
json.dump(res, open(os.path.join(WORK, "previews.json"), "w"), indent=1)
print(json.dumps(res, indent=1))
