"""Anteprime brevi dei tratti modificati (720p, qualità bassa, con l'audio), 1 s prima e dopo.

Uso: python3 tools/previews.py WORK [nome ...]   (solo le anteprime indicate, es. specchi)
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
WORDS = json.load(open(os.path.join(ROOT, "out", "sync.json")))["parole"]
PAD = 1.0
TRATTI = [
    ("preview_1_intro.mp4", 0.0, sez["intro"][2]),                      # fino a "Torno sul pezzo"
    ("preview_2_specchi.mp4", ins["specchi"]["t0"], ins["specchi"]["t1"]),
    ("preview_3_cervello.mp4", ins["cervello"]["t0"], ins["cervello"]["t1"]),
    ("preview_4_finale.mp4", plan["chiusura"][0], DUR),
    ("preview_5_fiches.mp4", [d for d in plan["inserti"] if d["name"] == "strada"][0]["t0"],
     [d for d in plan["inserti"] if d["name"] == "fiches" and not d.get("zoom")][0]["map"][1][0] + 0.75),
    # v7: intro multicamera, dall'inizio fino alla fine di "con il mio accento" (senza margine)
    ("preview_intro.mp4", 0.0, [d for d in plan["inserti"] if d["name"] == "tramonto"][0]["t0"], 0.0),
    # v8: cestino, da "quello che ho fatto" a fine "lavorare per vivere" (senza margine)
    ("preview_cestino.mp4", next(w["inizio"] for w in WORDS if w["parola"] == "quello" and 38 < w["inizio"] < 39),
     next(w["inizio"] for w in WORDS if w["parola"] == "Vivere" and 44 < w["inizio"] < 45), 0.0),    # v9: senza flash bianchi
    ("preview_corda.mp4", ins["corda"]["t0"], ins["corda"]["t1"]),
    ("preview_lampione.mp4", ins["lampione"]["t0"], ins["lampione"]["t1"]),    # v10: "Corsa per il tempo bastardo" con i sottotitoli normali
    ("preview_tempo_bastardo.mp4", ins["orologi"]["t0"], ins["orologi"]["t1"]),    # v11: dalla porta fino a "Torno sul pezzo" (senza margine)
    ("preview_vinile.mp4", ins["porta"]["t0"], sez["intro"][2], 0.0),    # v13: da "Torno sul pezzo" a fine "Vorrei non ci fosse un domani" (senza margine)
    ("preview_quaderno.mp4", next(w["inizio"] for w in WORDS if w["parola"] == "Torno" and w["inizio"] < 9),
     next(w["inizio"] for w in WORDS if w["parola"] == "Che" and 16.5 < w["inizio"] < 17.5), 0.0),
]
ONLY = sys.argv[2:]
res = json.load(open(os.path.join(WORK, "previews.json"))) if ONLY and os.path.exists(
    os.path.join(WORK, "previews.json")) else {}
for name, a, b, *pad in TRATTI:
    if ONLY and name not in ONLY and not any(o in name for o in ONLY): continue
    pd = pad[0] if pad else PAD
    t0, t1 = max(0.0, a - pd), min(DUR, b + pd)
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
