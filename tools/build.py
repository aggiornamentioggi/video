"""Build completo v2: render parallelo a blocchi -> intermedio -> export finale con la
regola del peso (CRF +2 finché sotto 95 MB) -> 3 tagli brevi ricavati dal video completo.

Uso: python3 tools/build.py WORK
"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = sys.argv[1]
OUT = os.path.join(ROOT, "out")
RENDER = [sys.executable, os.path.join(ROOT, "tools", "render.py"), WORK]
AUDIO = os.path.join(WORK, "audio_cut.wav")
LIMIT = 95_000_000
plan = json.loads(subprocess.check_output(RENDER + ["--plan"]))
DUR = plan["durata_video"]
sez = {s[0]: s for s in plan["sezioni"]}

def run(cmd): subprocess.check_call(cmd)

def probe(path):
    d = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                   "format=duration,size", "-of", "json", path]))["format"]
    return round(float(d["duration"]), 2), int(d["size"])

# 1. render a blocchi in parallelo (4 core) verso un intermedio quasi senza perdite
inter = os.path.join(WORK, "inter.mp4")
if not os.path.exists(inter):
    cuts = [0, 45, 90, 135, DUR]
    parts = []
    def chunk(k):
        p = os.path.join(WORK, f"inter_{k}.mp4")
        run(RENDER + ["--range", f"{cuts[k]},{cuts[k + 1]}", "--out", p, "--inter"])
        return p
    with ThreadPoolExecutor(4) as ex:
        parts = list(ex.map(chunk, range(4)))
    lst = os.path.join(WORK, "inter_list.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", inter])

ENC = ["-c:v", "libx264", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
       "-movflags", "+faststart"]

def encode_until_fits(make_cmd, out):
    """regola del brief: se il file supera 95 MB alza il CRF di 2 e rifai l'export"""
    crf, tries = 20, []
    while True:
        run(make_cmd(crf, out))
        size = os.path.getsize(out); tries.append((crf, size))
        if size < LIMIT: return crf, tries
        crf += 2

# anteprima 20 s del primo ritornello + foglio di fotogrammi (dallo stesso intermedio)
a0 = plan["sezioni"][5][1]
prev = os.path.join(OUT, "anteprima_ritornello.mp4")
run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a0:.3f}", "-t", "20", "-i", inter, "-ss", f"{a0:.3f}", "-t", "20",
     "-i", AUDIO, "-map", "0:v", "-map", "1:a", "-crf", "20"] + [
     "-c:v", "libx264", "-preset", "slow", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", prev])
run(["ffmpeg", "-v", "error", "-y", "-i", prev, "-vf",
     "fps=1.2,scale=270:480,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:"
     f"text='%{{eif\\:t+{int(a0)}\\:d}}s':x=6:y=6:fontsize=16:fontcolor=yellow:box=1:boxcolor=black@0.6,"
     "tile=6x4:padding=4", "-frames:v", "1", os.path.join(OUT, "anteprima_sheet.jpg")])

# 2. video completo
full = os.path.join(OUT, "non_mi_fermo_v2_1080x1920.mp4")
crf_full, tries_full = encode_until_fits(lambda crf, out: [
    "ffmpeg", "-v", "error", "-y", "-i", inter, "-i", AUDIO, "-map", "0:v", "-map", "1:a",
    "-af", f"afade=t=out:st={DUR - 0.5:.3f}:d=0.5", "-t", f"{DUR:.3f}", "-crf", str(crf)] + ENC + [out], full)

# 3. tagli brevi: aggancio (0,5 s del video completo) + segmento + chiusura IPNOS di 2 s
words = json.load(open(os.path.join(OUT, "sync.json")))["parole"]
beats = json.load(open(os.path.join(OUT, "beats.json")))["beats"]
def snap(t): return min(beats, key=lambda b: abs(b - t))
def wt(text, after):
    return next(w["inizio"] for w in words if w["parola"].lower().strip(",.?!") == text and w["inizio"] >= after)
r1, r2 = sez["ritornello1"], sez["ritornello2"]
s2 = sez["strofa2"]
CL0 = plan["chiusura"][1] - 0.01                  # chiusura: NON MI FERMO, IPNOS, studio in 2 s
SHORTS = [
    ("taglio_ritornello.mp4", r1[1], r1[2], True),
    ("taglio_strofa.mp4", snap(wt("vedo", s2[1])), snap(wt("non", wt("scordato", s2[1]))), True),
    ("taglio_finale.mp4", r2[1], DUR, False),     # contiene già la chiusura completa
]
def short_cmd(a, b, add_close):
    def make(crf, out):
        seg = b - a
        v = (f"[0:v]trim=0:{0.5},setpts=PTS-STARTPTS[h];"
             f"[0:v]trim={a + 0.5:.3f}:{b:.3f},setpts=PTS-STARTPTS[s];")
        au = f"[1:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS"
        if add_close:
            v += (f"[0:v]trim={CL0:.3f}:{CL0 + 2:.3f},setpts=PTS-STARTPTS,fade=t=out:st=1.7:d=0.3[c];"
                  f"[h][s][c]concat=n=3:v=1:a=0[v]")
            au += (f",afade=t=out:st={seg - 0.03:.3f}:d=0.03[a1];"
                   f"[1:a]atrim={CL0:.3f}:{CL0 + 2:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,"
                   f"afade=t=out:st=1.7:d=0.3[a2];[a1][a2]concat=n=2:v=0:a=1[a]")
        else:
            v += "[h][s]concat=n=2:v=1:a=0[v]"
            au += f",afade=t=out:st={seg - 0.5:.3f}:d=0.5[a]"
        return ["ffmpeg", "-v", "error", "-y", "-i", inter, "-i", AUDIO, "-filter_complex", v + ";" + au,
                "-map", "[v]", "-map", "[a]", "-r", "30", "-crf", str(crf)] + ENC + [out]
    return make

results = {"video_completo": dict(file=os.path.basename(full), crf=crf_full, tentativi=tries_full,
                                  durata=probe(full)[0], byte=probe(full)[1])}
for name, a, b, close in SHORTS:
    out = os.path.join(OUT, name)
    crf, tries = encode_until_fits(short_cmd(a, b, close), out)
    d, s = probe(out)
    results[name] = dict(da=round(a, 2), a=round(b, 2), crf=crf, tentativi=tries, durata=d, byte=s)
json.dump(results, open(os.path.join(WORK, "build_results.json"), "w"), indent=1)
print(json.dumps(results, indent=1))
