"""Render del video "Non Mi Fermo" (Ipnos) secondo BRIEF.md v2.

Uso:
  python3 tools/render.py WORK --plan                    scaletta in JSON
  python3 tools/render.py WORK --prep                    clip graduate, sfondi, out/beats.json
  python3 tools/render.py WORK --range t0,t1 --out F [--inter] [--crf N]
        --inter: intermedio senza audio ad alta qualità; altrimenti export finale con audio
  python3 tools/render.py WORK --preview t1,t2,...       fotogrammi singoli in WORK/preview

WORK contiene audio_cut.wav (traccia tagliata di 4,5 s con fade in 0,3 s),
beats.json (beat e colpi di cassa, da tools/beats.py), Anton-Regular.ttf e
Montserrat.ttf (variabile, google/fonts).
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = sys.argv[1]
ARGS = sys.argv[2:]
W, H, FPS = 1080, 1920, 30
RED = (225, 6, 0)            # #E10600
ANTON = os.path.join(WORK, "Anton-Regular.ttf")
MONT = os.path.join(WORK, "Montserrat.ttf")
AUDIO = os.path.join(WORK, "audio_cut.wav")
PREP = os.path.join(WORK, "prep")

def arg(name, default=None):
    return ARGS[ARGS.index(name) + 1] if name in ARGS else default

def find_src(prefixes):
    """cerca per inizio del nome in qualsiasi cartella (esclusi .git, out, tools)"""
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in (".git", "out", "tools")]
        for f in sorted(fns):
            if any(f.lower().startswith(p.lower()) for p in prefixes):
                return os.path.join(dp, f)
    return None

SRC = {
    "corridoio": find_src(["The-hooded-young-man-keeps-walking"]),
    "studio":    find_src(["The-hooded-young-man-seen-from-behind"]),
    "tv":        find_src(["The-old-CRT-television"]),
    "strada":    find_src(["hf_20261003_151301"]),
    "candela":   find_src(["hf_20261003_154346"]),
    "penna":     find_src(["Scrittura", "penna"]),
}
# clip aggiunte (caricate su main): nome -> inizio del nome del file
NEW_CLIPS = {"tramonto": "tramonto", "ufficio": "ufficio", "brocca": "brocca", "carte": "carte",
             "mare": "mare", "specchio": "specchio", "maschera": "maschera",
             "torcia": "torcia", "foto": "foto",
             # v3
             "porta": "The-door-slowly-swings", "mano": "The-hand-slowly-squeezes",
             "scatola": "The-wooden-lid", "pozzo": "A-small-pebble", "mappamondo": "Cinematic-dark-moody",
             "microfono": "microfono", "vetro": "vetro", "corda": "corda", "sedia": "sedia",
             "lampione": "lampione", "soundwave": "soundwave", "orologi": "All-the-clock-hands",
             "moneta": "The-old-coin-spins"}
# muro.mp4: riserva, non usato
for _k, _p in NEW_CLIPS.items():
    if find_src([_p]): SRC[_k] = find_src([_p])
OPTIONAL = ["moneta", "goccia", "carte", "petardo", "mare", "lampione", "personaggio", "performance"]
OPT_FOUND = {k: find_src([k]) for k in OPTIONAL}

# ---------------------------------------------------------------- dati
sync = json.load(open(os.path.join(ROOT, "out", "sync.json")))
WORDS = sync["parole"]
BEATS = json.load(open(os.path.join(WORK, "beats.json")))
beats = np.array(BEATS["beats"])
PERIOD = float(np.median(np.diff(beats)))
GRID = np.concatenate([beats[0] - PERIOD * np.arange(30, 0, -1), beats])
DUR = float(subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", AUDIO]))
N = int(DUR * FPS)
DUR_V = N / FPS

def snap(t): return float(GRID[np.argmin(np.abs(GRID - t))])
def next_beat(t): return float(GRID[GRID > t + 0.05][0])
def fr(t): return int(round(t * FPS))
def clean(w): return w.lower().strip(",.?!")

def find_line(prefix):
    groups, cur, last = [], [], None
    for i, w in enumerate(WORDS):
        if w["testo_riga"].lower().startswith(prefix.lower()):
            if last is not None and w["idx_riga"] != WORDS[last]["idx_riga"]:
                groups.append(cur); cur = []
            cur.append(i); last = i
    if cur: groups.append(cur)
    return groups

def line_span(g):
    a = WORDS[g[0]]["inizio"]; nxt = g[-1] + 1
    return a, (WORDS[nxt]["inizio"] if nxt < len(WORDS) else WORDS[g[-1]]["fine"])

def word_t(text, after=0.0):
    for w in WORDS:
        if clean(w["parola"]) == text.lower() and w["inizio"] >= after: return w["inizio"]
    raise KeyError(text)

hop = BEATS["hop"]; env = np.array(BEATS["env_kick"])
def kick_strength(k): return float(env[max(0, int(k / hop) - 2):int(k / hop) + 3].max())
KICKS = [(k, kick_strength(k)) for k in BEATS["kicks"]]

# ---------------------------------------------------------------- sezioni
TORNO = 8.85        # attacco vocale di "Torno"
CUFFIE = 3.25       # clip studio: cuffie sulla testa
SPEGNE = 3.25       # clip candela: il soffio spegne la fiamma
HOOK = 0.5

chorus = []
idx = [i for i, w in enumerate(WORDS) if w["sezione"] == "rit"]
blocks, cur = [], [idx[0]]
for i in idx[1:]:
    if i == cur[-1] + 1: cur.append(i)
    else: blocks.append(cur); cur = [i]
blocks.append(cur)
for bl in blocks:
    a = snap(WORDS[bl[0]]["inizio"]); nxt = bl[-1] + 1
    b = WORDS[nxt]["inizio"] if nxt < len(WORDS) else WORDS[bl[-1]]["fine"] + 0.6
    chorus.append((a, b))
CLOSE = chorus[-1][1]
TB = snap(word_t("tempo")); TB_END = word_t("Sotto", TB)
CUT_S1 = snap(word_t("Forse"))
last_word = WORDS[-1]
coda_hits = [k for k, s in KICKS if k > last_word["fine"] + 1.5 and s > 0.6]
HIT1, HIT2 = coda_hits[0], coda_hits[1]
STUDIO_FADE = float(beats[beats > HIT2 + 0.2][0])

# (nome, t0, t1, livello di intensità 0-4)
SECTIONS = [("aggancio", 0, HOOK, 0), ("intro", HOOK, CUT_S1, 0), ("strofa1", CUT_S1, TB, 1),
            ("tempo_bastardo", TB, TB_END, 1), ("strofa1", TB_END, chorus[0][0], 1),
            ("ritornello1", chorus[0][0], chorus[0][1], 2), ("strofa2", chorus[0][1], chorus[1][0], 3),
            ("ritornello2", chorus[1][0], chorus[1][1], 4), ("chiusura", CLOSE, DUR_V + 1, 0)]
def section(t):
    for s in SECTIONS:
        if s[1] <= t < s[2]: return s
    return SECTIONS[-1]
def in_chorus(t): return section(t)[0].startswith("ritornello")

# ---------------------------------------------------------------- clip inserite
# opzioni: in (s di clip), ramp (entra al 60% e torna al 100% sul beat dopo),
# zoom/cx/cy (porzione della clip), grade "red" (luce rossa)
inserts = []
def ins(name, t0, t1, **o): inserts.append(dict(name=name, t0=t0, t1=t1, **o))

ins("aggancio", 0.0, HOOK)

def content(tau, t0, ramp=True, sp=1.0):
    """secondi di clip consumati dopo tau secondi di inserto (speed ramp 60% -> 100%)"""
    if not ramp: return tau * sp
    tb = next_beat(t0) - t0
    return 0.6 * tau if tau < tb else 0.6 * tb + (tau - tb) * sp

def clip_len(name):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", SRC[name]]))

# v3: inserti a tempo esatto. map = [(t_out0, t_out1, clip0, clip1)]: tempo di clip lineare
# in ogni tratto (velocità = (clip1-clip0)/(t_out1-t_out0)), mai in loop.
def mapped(name, t0, t1, c0, c1, **o):
    ins(name, t0, t1, map=[(t0, t1, c0, c1)], **o)
def black(t0, t1): ins("nero", t0, t1)

def wt(text, after=0.0): return word_t(text, after)
def L(prefix): return WORDS[find_line(prefix)[0][0]]["inizio"]     # inizio della riga

# --- intro: corridoio -> porta (zoom lento + flash 4 frame) -> cuffie su "pezzo"
PEZZO = wt("pezzo")                                       # 9.36
KICKS0 = [k for k, s in KICKS if k < PEZZO]
DOOR_IN = float(min(KICKS0, key=lambda k: abs((PEZZO - k) - 2.4)))   # cassa a ~2,4 s da "pezzo"
DOOR_LEN = 2.4                                            # solo 0-2,4 s: dopo c'è fumo
cl = clip_len("corridoio") - 0.04
corr = lambda t: (t - HOOK) * cl / (DOOR_IN - HOOK)
CA, CB = 3.3, (DOOR_IN + 3.3) / 2 + 0.6                   # tre inquadrature del corridoio
for (a, b, z, cx, cy) in [(HOOK, CA, 1.0, 0.5, 0.5), (CA, CB, 1.25, 0.5, 0.45), (CB, DOOR_IN, 1.5, 0.5, 0.42)]:
    ins("corridoio", a, b, map=[(a, b, corr(a), corr(b))], zoom=z, cx=cx, cy=cy)
ins("porta", DOOR_IN, PEZZO, map=[(DOOR_IN, PEZZO, 0.0, DOOR_LEN)], zoomramp=(1.0, 1.10))
FLASHES = {fr(PEZZO) - 4 + k: v for k, v in enumerate([0.55, 1.0, 1.0, 0.75])}
STUDIO_IN = 3.0                                           # cuffie in testa a 3,25 di clip
ins("studio", PEZZO, CUT_S1, map=[(PEZZO, CUT_S1, STUDIO_IN, STUDIO_IN + CUT_S1 - PEZZO)],
    zoom=1.35, cx=0.48, cy=0.30)

# --- strofa 1
a = wt("Confesso"); mapped("microfono", a, a + 2.26, 0.0, 2.26)
a = wt("scava"); b = WORDS[[i for i, w in enumerate(WORDS) if clean(w["parola"]) == "niente"][0]]["fine"]
mapped("pozzo", a, b, 0.70, 2.30)                         # il sasso cade da "scava" a fine "niente"
a = wt("Finire"); r = wt("resti", a)
mapped("scatola", a, r, 0.0, 1.40); black(r, wt("Voglio", r))
a = wt("Voglio", r); p = wt("parte", a); e = wt("In", p)
ins("vetro", a, e, map=[(a, p, 0.0, 1.5), (p, e, 1.5, 1.5 + e - p)])   # B: niente taglio in testa
a = L("Solo soldato"); bt = wt("buttato", a); e = L("Pacato")
mapped("mano", a, e, 3.0 - (bt - a), 3.0 + (e - bt))       # stretta (3,0 s di clip) su "buttato"
a = e; tn = wt("tornato", a); e = wt("Lavorare", a)
mapped("sedia", a, e, 1.5 - (tn - a), 1.5 + (e - tn))      # lampada (1,5) su "tornato"
a = e; e = wt("Dentro", a); mapped("ufficio", a, e, 0.0, e - a)
a = e; e = wt("Gioco", a); mapped("brocca", a, e, 0.0, e - a)
a = e; v = wt("il", a); mapped("carte", a, v, 0.0, v - a); e = wt("Devi", a); black(v, e)
a = e; e = wt("Fato", a)
COIN_BAD = {26, 34, 41, 42}                                # fotogrammi deformati (a 24 fps)
COIN = [k for k in range(22, 53) if k not in COIN_BAD]     # 0,9-2,2 s
ins("moneta", a, e, frames=COIN, speed=0.5)               # metà velocità, poi nero se serve
a = wt("Sleghiamo"); u = wt("umani", a); e = wt("Corsa", a)
mapped("corda", a, e, 2.0 - (u - a), 2.0 + (e - u))        # flash dello strappo su "umani"
a = e; e = wt("Sotto", a); oe = clip_len("orologi") - 0.04; mapped("orologi", a, e, oe - (e - a), oe)   # taglio in testa
a = e; pt = wt("petardo", a); e = wt("Morite", a)
mapped("mappamondo", a, e, 2.79 - (pt - a), 2.79 + (e - pt))    # esplosione su "petardo"

# --- ritornelli
for g in find_line("Prendo la penna"):
    a, b = line_span(g); ins("penna", snap(a), snap(b))
for g in find_line("Fino a che non si spegne"):
    a, b = line_span(g); t0, t1 = snap(a), snap(b)
    cuore = WORDS[g[-1]]["inizio"]
    ins("candela", t0, t1, inp=max(0.0, SPEGNE - content(cuore - t0, t0)), ramp=True)
for g in find_line("Senti la voce"):                       # soundwave: "Senti" -> fine "respiro"
    a = WORDS[g[0]]["inizio"]; b = WORDS[g[-1]]["fine"]
    mapped("soundwave", a, b, 0.0, b - a)
for g in find_line("Battico cardiaco"):                    # ultimo ritornello: corridoio in rosso
    a = snap(WORDS[g[0]]["inizio"])
    if a >= chorus[1][0]:
        ins("corridoio", a, a + 4 * PERIOD, inp=2.0, ramp=True, zoom=1.3, cx=0.5, cy=0.45, grade="red")

# --- strofa 2
a = snap(word_t("Cambierò")); b = snap(line_span(find_line("Io Non voglio mai assomigliare")[0])[1])
mid = snap((a + b) / 2)                          # mai la stessa inquadratura > 4 s
ins("tv", a, mid, inp=0.0, ramp=True)
ins("tv", mid, b, inp=content(mid - a, a), ramp=False, zoom=1.45, cx=0.48, cy=0.47)
a = L("Un giorno tutto"); bu = wt("buio", a); e = wt("Non", bu)
mapped("lampione", a, e, 1.87 - (bu - a), 1.87 + (e - bu))  # spegnimento su "buio"
# Clip sui versi come nella v2 (inizio e fine sul beat, rallentate fino a 0,8x, mai in loop)
VERSI = [("tramonto", "Vorrei non ci fosse", "Che tutto finisse"),
         ("mare", "Dentro la testa", None), ("specchio", "Sono un artista", "Senza un po"),
         ("maschera", "Odio lo standard", "Voglio le robe"), ("strada", "Giro le strade", None),
         ("torcia", "Cerco i dettagli", None), ("foto", "L'istante presente", None)]
for name, first, last in VERSI:
    if name not in SRC: continue
    g0 = find_line(first)[0]; g1 = find_line(last)[0] if last else g0
    a = snap(WORDS[g0[0]]["inizio"]); b = snap(line_span(g1)[1])
    fit = a + clip_len(name) / 0.8
    if fit < b: b = float(GRID[GRID <= fit + 1e-6][-1])
    ins(name, a, b, inp=0.0, ramp=False, slow08=True)

inserts.sort(key=lambda d: d["t0"])

# ---------------------------------------------------------------- sfondi sfocati in movimento
POOLS = {"strofa1": ["studio", "corridoio"], "ritornello1": ["candela", "penna"],
         "strofa2": ["strada", "tv"], "ritornello2": ["candela", "penna"]}
SEG_BEATS = {"strofa1": 6, "ritornello1": 4, "strofa2": 4, "ritornello2": 2}
bg = []
_brng = np.random.default_rng(11)
for name, t0, t1, lvl in SECTIONS:
    if name not in POOLS: continue
    g = GRID[(GRID >= t0 - 0.01) & (GRID < t1 - 0.2)]
    edges = list(g[::SEG_BEATS[name]]) if len(g) else [t0]
    edges[0] = t0; edges.append(t1)
    for k in range(len(edges) - 1):
        z = float(_brng.uniform(1.10, 1.55))
        bg.append(dict(clip=POOLS[name][k % 2], t0=float(edges[k]), t1=float(edges[k + 1]), lvl=lvl,
                       zoom=z, cx=float(_brng.uniform(0.3, 0.7)), cy=float(_brng.uniform(0.3, 0.7)),
                       pan=(float(_brng.uniform(-0.04, 0.04)), float(_brng.uniform(-0.04, 0.04))),
                       rot=(float(_brng.uniform(-1.5, 1.5)), float(_brng.uniform(-1.5, 1.5))),
                       off=int(_brng.integers(0, 10_000))))

# ---------------------------------------------------------------- frasi
KEY = {"cuore", "tempo", "bastardo", "rischiare", "mente", "buio", "scuro", "eterno",
       "muore", "tradito", "penna", "voce", "respiro"}
GLITCH = {"bastardo", "muore", "tradito", "buio", "scuro"}
red = [clean(w["parola"]) in KEY for w in WORDS]
nmf = [False] * len(WORDS)
for i in range(len(WORDS) - 2):
    if [clean(WORDS[i + k]["parola"]) for k in range(3)] == ["non", "mi", "fermo"]:
        red[i] = red[i + 1] = red[i + 2] = True
        nmf[i + 1] = nmf[i + 2] = True
NO_END = {"il", "la", "lo", "le", "i", "un", "una", "di", "a", "da", "in", "con", "per", "che",
          "e", "ma", "mi", "ti", "ci", "non", "sul", "nel", "nei", "dentro", "sotto", "io", "tu",
          "è", "sto", "coi", "dalle", "quando", "fino", "al", "sia", "ho", "se", "mica", "chi"}
BREAK_BEFORE = {"che", "ma", "e", "per", "quando", "fino", "dentro", "sotto", "in", "con", "di"}

def split_phrase(ix):
    """frasi da 2-4 parole spezzate ai respiri; mai una parola vuota da sola o in coda"""
    if len(ix) <= 4: return [ix]
    best, bk = -1e9, None
    for k in range(2, len(ix) - 1):
        sc = WORDS[ix[k]]["inizio"] - WORDS[ix[k - 1]]["inizio"]
        if clean(WORDS[ix[k]]["parola"]) in BREAK_BEFORE: sc += 0.12
        if clean(WORDS[ix[k - 1]]["parola"]) in NO_END: sc -= 1.0
        if nmf[ix[k]]: sc -= 5
        sc -= 0.03 * abs(len(ix) - 2 * k)
        if sc > best: best, bk = sc, k
    return split_phrase(ix[:bk]) + split_phrase(ix[bk:])

lines = {}
for i, w in enumerate(WORDS):
    if w["inizio"] < TORNO - 0.2: continue
    if TB - 0.05 <= w["inizio"] < TB_END and clean(w["parola"]) in ("tempo", "bastardo"): continue
    lines.setdefault(w["idx_riga"], []).append(i)
phrases = []
for li in sorted(lines): phrases += split_phrase(lines[li])
PHR = []
_prng = np.random.default_rng(5)
ENTRIES = ["blur", "su", "lato", "scatto"]
for p, ix in enumerate(phrases):
    a = WORDS[ix[0]]["inizio"]
    nxt = WORDS[phrases[p + 1][0]]["inizio"] if p + 1 < len(phrases) else WORDS[ix[-1]]["fine"] + 0.6
    end = nxt if nxt - WORDS[ix[-1]]["inizio"] < 1.4 else WORDS[ix[-1]]["inizio"] + 1.0
    if a < TB <= end: end = TB
    end = min(end, CLOSE)
    PHR.append(dict(ix=ix, f0=fr(a), f1=fr(end), entry=ENTRIES[p % 4],
                    side=1 if (p // 4) % 2 == 0 else -1, xoff=float(_prng.uniform(-40, 40))))

GL_FRAMES = [(fr(w["inizio"]), 16) for w in WORDS
             if clean(w["parola"]) in GLITCH and TORNO <= w["inizio"] < CLOSE]
GL_FRAMES.append((fr(TB), 16))
GL_FRAMES.append((fr(next_beat(TB)), 16))
# più glitch nella strofa 2 e nell'ultimo ritornello: piccoli glitch su colpi forti ogni ~2 battute
for name, t0, t1, lvl in SECTIONS:
    if lvl >= 3:
        last = -9
        for k, s in KICKS:
            if t0 <= k < t1 and s > 0.6 and k - last > 8 * PERIOD * (0.5 if lvl == 4 else 1):
                GL_FRAMES.append((fr(k), 7)); last = k
# Nessun flash bianco: tolti su richiesta (troppo forti)

PLAN = {"durata_video": DUR_V, "frames": N,
        "sezioni": [(s[0], round(s[1], 2), round(min(s[2], DUR_V), 2), s[3]) for s in SECTIONS],
        "inserti": [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in d.items()} for d in inserts],
        "sfondi": len(bg), "frasi": len(PHR), "glitch": len(GL_FRAMES),
        "tempo_bastardo": [round(TB, 3), round(TB_END, 3)],
        "chiusura": [round(CLOSE, 2), round(HIT1, 3), round(HIT2, 3), round(STUDIO_FADE, 3)],
        "opzionali": {k: bool(v) for k, v in OPT_FOUND.items()}}
if "--plan" in ARGS:
    PLAN["testo_frasi"] = [" ".join(WORDS[i]["parola"] for i in d["ix"]) for d in PHR]
    PLAN["sfondi_dettaglio"] = [(d["clip"], round(d["t0"], 2), round(d["t1"], 2)) for d in bg]
    print(json.dumps(PLAN, indent=1, ensure_ascii=False)); sys.exit()

# ---------------------------------------------------------------- preparazione
GRADE = ("curves=master='0/0 0.10/0.04 0.5/0.49 1/0.97',"
         "colorbalance=rs=-0.03:gs=-0.01:bs=0.05:rm=0.05:gm=0.01:bm=-0.04,eq=saturation=0.82")
CROP = "crop='min(iw,ih*9/16)':'min(ih,iw*16/9)'"
BW, BH = 360, 640                                  # sfondi a 1/3 di risoluzione (poi sfocati)

def prep():
    os.makedirs(PREP, exist_ok=True)
    for name, src in SRC.items():
        if name == "penna":
            out = os.path.join(PREP, "penna.png")
            subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf",
                                   f"{CROP},{GRADE}", "-frames:v", "1", out])
            im = Image.open(out).convert("RGB").resize((BW, BH), Image.LANCZOS)
            np.save(os.path.join(PREP, "bg_penna.npy"), np.asarray(im)[None])
            continue
        out = os.path.join(PREP, f"{name}.mp4")
        subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf",
            f"{CROP},scale={W}:{H}:flags=lanczos,{GRADE}", "-an", "-c:v", "libx264", "-crf", "10",
            "-preset", "veryfast", "-pix_fmt", "yuv420p", out])
        if name not in ("studio", "corridoio", "candela", "strada", "tv"): continue
        trim = "trim=0:3.0," if name == "candela" else ""          # sfondo: solo fiamma accesa
        raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", out, "-filter_complex",
            f"[0:v]{trim}scale={BW}:{BH},setpts=(PTS-STARTPTS)/0.7,fps={FPS},"
            f"split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1:a=0", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
        arr = np.frombuffer(raw, np.uint8).reshape(-1, BH, BW, 3)
        np.save(os.path.join(PREP, f"bg_{name}.npy"), arr)
    # out/beats.json: beat e colpi di cassa (onset sulle basse frequenze)
    json.dump({"tempo_bpm": round(60 / PERIOD, 2), "nota": "tempi relativi alla traccia tagliata di 4,5 s",
               "beats": [round(float(b), 3) for b in beats],
               "casse": [{"t": round(k, 3), "forza": round(s, 2)} for k, s in KICKS]},
              open(os.path.join(ROOT, "out", "beats.json"), "w"), indent=1)
    print("prep ok")

if "--prep" in ARGS:
    prep(); sys.exit()

# ---------------------------------------------------------------- testo
_fc = {}
def font(kind, size):
    k = (kind, size)
    if k not in _fc:
        if kind == "anton": _fc[k] = ImageFont.truetype(ANTON, size)
        else:
            f = ImageFont.truetype(MONT, size); f.set_variation_by_name(kind); _fc[k] = f
    return _fc[k]

BASE = 64; KEYS = int(BASE * 1.4); TRACK = BASE * 0.02
MAXW = int(W * 0.8); BAND = (int(H * 0.70), int(H * 0.80))
GRAY = (128, 128, 128); REDDIM = tuple(int(v * 0.55) for v in RED)
SPAD = 30

def word_font(i): return font("anton", KEYS) if red[i] else font("SemiBold", BASE)
def word_text(i): return WORDS[i]["parola"].upper()
def text_len(f, t, track):
    return sum(f.getlength(c) for c in t) + track * max(0, len(t) - 1) if track else f.getlength(t)

def draw_text(d, xy, t, f, track, fill):
    if not track:
        d.text(xy, t, font=f, fill=fill, anchor="ls"); return
    x, y = xy
    for c in t:
        d.text((x, y), c, font=f, fill=fill, anchor="ls"); x += f.getlength(c) + track

_sc = {}
def sprite(i, n, color, blur=0.0, scale=1.0):
    """parola (prime n lettere) come sprite premoltiplicato con ombra morbida.
    Ritorna (C, A, ox, oy): ox, oy = origine (sinistra, linea di base) dentro lo sprite."""
    key = (i, n, color, round(blur, 1), round(scale, 2))
    if key in _sc: return _sc[key]
    t = word_text(i)[:n]
    f = word_font(i); track = 0 if red[i] else TRACK
    asc, desc = f.getmetrics()
    w = int(text_len(f, word_text(i), track)) + 2 * SPAD; h = asc + desc + 2 * SPAD
    mask = Image.new("L", (w, h), 0)
    draw_text(ImageDraw.Draw(mask), (SPAD, SPAD + asc), t, f, track, 255)
    m = np.asarray(mask, np.float32) / 255
    sh = np.asarray(mask.filter(ImageFilter.GaussianBlur(12)), np.float32) / 255 * 0.7
    A = m + np.clip(sh * 1.4, 0, 0.7) * (1 - m)
    C = (np.array(color, np.float32) / 255) * m[..., None]
    ox, oy = SPAD, SPAD + asc
    if blur > 0.3 or abs(scale - 1) > 0.005:
        ci = Image.fromarray((np.clip(C, 0, 1) * 255).astype(np.uint8))
        ai = Image.fromarray((A * 255).astype(np.uint8))
        if abs(scale - 1) > 0.005:
            nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
            ci, ai = ci.resize((nw, nh), Image.BICUBIC), ai.resize((nw, nh), Image.BICUBIC)
            ox, oy = ox * scale, oy * scale
        if blur > 0.3:
            ci, ai = ci.filter(ImageFilter.GaussianBlur(blur)), ai.filter(ImageFilter.GaussianBlur(blur))
        C = np.asarray(ci, np.float32) / 255; A = np.asarray(ai, np.float32) / 255
    if len(_sc) > 3000: _sc.clear()
    _sc[key] = (C, A, ox, oy)
    return _sc[key]

def paste_pm(frame, C, A, x0, y0, op=1.0):
    h, w = A.shape
    x0, y0 = int(round(x0)), int(round(y0))
    fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if fx1 <= fx0 or fy1 <= fy0: return
    a = A[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0, None] * op
    c = C[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0] * op
    frame[fy0:fy1, fx0:fx1] = frame[fy0:fy1, fx0:fx1] * (1 - a) + c

_lay = {}
def layout(p):
    """posizioni (x sinistra, linea di base) di ogni parola; una o due righe nella fascia 70-80%"""
    if p in _lay: return _lay[p]
    ix = PHR[p]["ix"]
    ws = [(i, text_len(word_font(i), word_text(i), 0 if red[i] else TRACK)) for i in ix]
    sp = BASE * 0.30
    total = sum(w for _, w in ws) + sp * (len(ws) - 1)
    rows = [ws]
    if total > MAXW:                                  # due righe, taglio più bilanciato
        best = None
        for k in range(1, len(ws)):
            a_ = sum(w for _, w in ws[:k]) + sp * (k - 1); b_ = sum(w for _, w in ws[k:]) + sp * (len(ws) - k - 1)
            if best is None or max(a_, b_) < best[0]: best = (max(a_, b_), k)
        rows = [ws[:best[1]], ws[best[1]:]]
    lh = int(KEYS * 1.02)
    cy = (BAND[0] + BAND[1]) / 2
    widths = [sum(w for _, w in r) + sp * (len(r) - 1) for r in rows]
    xoff = PHR[p]["xoff"]                             # variazione orizzontale ±40 px
    pos = {}
    for r, row in enumerate(rows):
        base = cy + KEYS * 0.36 + (r - (len(rows) - 1) / 2) * lh
        x = W / 2 - widths[r] / 2 + xoff
        x = min(max(x, (W - MAXW) / 2), (W + MAXW) / 2 - widths[r])
        for i, w in row:
            pos[i] = (x, base, w); x += w + sp
    _lay[p] = pos
    return pos

def ease(u): return 1 - (1 - min(1, max(0, u))) ** 3

def typed(i, t):
    w = WORDS[i]; L = len(w["parola"])
    d = max(0.08, min(0.35, w["fine"] - w["inizio"]))
    u = (t - w["inizio"]) / d
    return 0 if u < 0 else max(1, min(L, int(math.ceil(u * L))))

def last_event(arr, t):
    j = np.searchsorted(arr, t + 1e-6) - 1
    return None if j < 0 else t - arr[j]

def draw_phrases(frame, f):
    t = f / FPS
    sec = section(t)
    for p, ph in enumerate(PHR):
        if not (ph["f0"] <= f < ph["f1"]): continue
        ix = ph["ix"]; pos = layout(p); k = f - ph["f0"]
        cur = max([i for i in ix if fr(WORDS[i]["inizio"]) <= f], default=ix[0])
        chor = in_chorus(t)
        dx = dy = 0.0; op = 1.0; blur = 0.0; zs = 1.0
        if chor:
            dk = last_event(KICK_T, t)
            if dk is not None and dk < 3 / FPS:
                amp = [6, 4, 2][min(2, int(dk * FPS))] * (1.4 if sec[3] == 4 else 1)
                rng = np.random.default_rng(f + 17)
                dx, dy = rng.uniform(-amp, amp, 2)
        else:
            e = ph["entry"]
            if e == "blur" and k < 6: blur = 12 * (1 - k / 6); op = (k + 1) / 6
            elif e == "su" and k < 6: dy = 30 * (1 - ease((k + 1) / 6)); op = (k + 1) / 6
            elif e == "lato" and k < 6: dx = 30 * ph["side"] * (1 - ease((k + 1) / 6)); op = (k + 1) / 6
            elif e == "scatto" and k < 4: zs = [1.15, 1.10, 1.05, 1.0][k]
        cxp = np.mean([pos[i][0] + pos[i][2] / 2 for i in ix]); cyp = np.mean([pos[i][1] for i in ix])
        db = last_event(beats, t)
        for i in ix:
            x, base, wl = pos[i]
            n = typed(i, t) if chor else len(word_text(i))
            if n <= 0: continue
            if red[i]: col = RED if i == cur else REDDIM
            else: col = (255, 255, 255) if i == cur else GRAY
            s = zs
            if red[i] and db is not None:                     # pulsazione ±6% sul beat
                s *= 1 + 0.06 * (2 * math.exp(-db / 0.10) - 1) * (1 if db < 0.5 else 0)
            C, A, ox, oy = sprite(i, n, col, blur, s)
            # scala attorno al centro parola (pulsazione) e al centro frase (scatto)
            wx = cxp + (x + wl / 2 - cxp) * zs; wy = cyp + (base - cyp) * zs
            sw = wl * s
            paste_pm(frame, C, A, wx - sw / 2 - ox + dx, wy - oy + dy, op)

# blocchi centrali (TEMPO BASTARDO, aggancio, chiusura)
def block_img(lines_, size, color, kind="anton", maxw=900, tracking=0.0, alpha=1.0, shadow=True):
    while True:
        f = font(kind, size)
        widths = [text_len(f, ln, tracking * size) for ln in lines_]
        if max(widths) <= maxw or size < 30: break
        size = int(size * 0.97)
    asc, desc = f.getmetrics(); lh = int(size * 1.02) if kind == "anton" else asc + desc
    pad = 60
    w = int(max(widths)) + 2 * pad; h = lh * (len(lines_) - 1) + asc + desc + 2 * pad
    mask = Image.new("L", (w, h), 0); d = ImageDraw.Draw(mask)
    for i, ln in enumerate(lines_):
        draw_text(d, (pad + (max(widths) - widths[i]) / 2, pad + asc + i * lh), ln, f, tracking * size, 255)
    m = np.asarray(mask, np.float32) / 255
    A = m.copy()
    if shadow:
        sh = np.asarray(mask.filter(ImageFilter.GaussianBlur(16)), np.float32) / 255
        A = m + np.clip(sh * 1.6, 0, 1) * 0.8 * (1 - m)
    C = (np.array(color, np.float32) / 255) * m[..., None]
    bbox = mask.getbbox()
    return dict(C=C * alpha, A=A * alpha, bbox=bbox, h=bbox[3] - bbox[1])

def zoomed(img, s):
    if abs(s - 1) < 1e-3: return img["C"], img["A"]
    h, w = img["A"].shape; nw, nh = int(w * s), int(h * s)
    ci = Image.fromarray((img["C"] * 255).astype(np.uint8)).resize((nw, nh), Image.BICUBIC)
    ai = Image.fromarray((img["A"] * 255).astype(np.uint8)).resize((nw, nh), Image.BICUBIC)
    return np.asarray(ci, np.float32) / 255, np.asarray(ai, np.float32) / 255

def paste_block(frame, img, cy, k, op=1.0):
    """centra il contenuto visibile (bbox) in cy, con micro zoom 1.15 -> 1.00 in 4 frame"""
    s = [1.15, 1.10, 1.05, 1.0][k] if 0 <= k < 4 else 1.0
    C, A = zoomed(img, s)
    bx0, by0, bx1, by1 = img["bbox"]
    ccx, ccy = (bx0 + bx1) / 2 * s, (by0 + by1) / 2 * s
    paste_pm(frame, C, A, W / 2 - ccx, cy - ccy, op)

HOOK_TXT = block_img(["NON MI FERMO"], 170, RED)
TEMPO_IMG = block_img(["TEMPO"], 230, RED)
BAST_IMG = block_img(["BASTARDO"], 230, RED)
_tbh = TEMPO_IMG["h"] + 30 + BAST_IMG["h"]
Y_TEMPO = H / 2 - _tbh / 2 + TEMPO_IMG["h"] / 2
Y_BAST = H / 2 + _tbh / 2 - BAST_IMG["h"] / 2
TB2 = next_beat(TB)                               # BASTARDO sul beat dopo TEMPO
NMF = block_img(["NON MI FERMO"], 190, (255, 255, 255))
IP = block_img(["IPNOS"], 300, RED, shadow=False)
CS = block_img(["IPNOS CREATIVE STUDIO"], 40, (255, 255, 255), kind="SemiBold", maxw=1000,
               tracking=0.20, alpha=0.85, shadow=False)
G1, G2 = 40, 60                                   # IPNOS -> studio: almeno 50 px
blk = NMF["h"] + G1 + IP["h"] + G2 + CS["h"]
top = H / 2 - blk / 2
Y_NMF = top + NMF["h"] / 2
Y_IP = top + NMF["h"] + G1 + IP["h"] / 2
Y_CS = top + NMF["h"] + G1 + IP["h"] + G2 + CS["h"] / 2

# ---------------------------------------------------------------- effetti di frame
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
VIG = np.clip((_r - 0.45) / 0.55, 0, 1) ** 1.5          # più leggera: centro libero
VIG = (VIG / VIG.max()).astype(np.float32)[..., None]
del yy, xx, _r
RED_F = np.array(RED, np.float32) / 255
KICK_T = np.array([k for k, s in KICKS if s > 0.3])
KICK_STRONG = np.array([k for k, s in KICKS if s > 0.6])

def pulse(t):
    if not in_chorus(t): return 0.0
    dt = last_event(KICK_T, t)
    return 0.04 if dt is None else min(0.35, 0.04 + 0.31 * math.exp(-dt / 0.32))

GRAIN_AMP, GRAIN_STEP = float(os.environ.get("GRAIN_AMP", "0.005")), int(os.environ.get("GRAIN_STEP", "3"))
_g = np.random.default_rng(7)
GRAIN = []
for _ in range(12):
    g = _g.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    GRAIN.append((np.asarray(Image.fromarray(g).resize((W, H), Image.BICUBIC), np.float32) * GRAIN_AMP)[..., None])

LW, LH = 108, 192
_ly, _lx = np.mgrid[0:LH, 0:LW].astype(np.float32)
LEAKS = [(0.05, 0.25, 0.11, 0.07, 0.55), (0.95, 0.7, 0.08, 0.13, 0.5), (0.2, 0.9, 0.06, 0.09, 0.45)]
def leak(t, inten):
    v = np.zeros((LH, LW), np.float32)
    for k, (cx, cy, fx, fy, s) in enumerate(LEAKS):
        x = (cx + 0.18 * math.sin(t * fx * 2 * math.pi + k)) * LW
        y = (cy + 0.12 * math.sin(t * fy * 2 * math.pi + 2 * k)) * LH
        v += np.exp(-(((_lx - x) / (s * LW)) ** 2 + ((_ly - y) / (s * LW)) ** 2))
    im = Image.fromarray((np.clip(v * inten, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    return (np.asarray(im, np.float32) / 255)[..., None] * np.array([1.0, 0.12, 0.04], np.float32)

def glitch(frame, k, amp0, seed):
    amp = max(2, int(amp0 * (1 - k / 4)))
    rng = np.random.default_rng(seed)
    dx, dy = rng.integers(-amp, amp + 1, 2)
    out = np.roll(frame, (int(dy), int(dx)), axis=(0, 1))
    out[..., 0] = np.roll(out[..., 0], amp, axis=1)
    out[..., 2] = np.roll(out[..., 2], -amp, axis=1)
    for _ in range(3):
        y0 = int(rng.integers(0, H - 40)); hh = int(rng.integers(8, 40))
        out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], int(rng.integers(-3 * amp, 3 * amp + 1)), axis=1)
    return out

def punch(frame, s):
    if s <= 1.001: return frame
    im = Image.fromarray((np.clip(frame, 0, 1) * 255).astype(np.uint8))
    w2, h2 = W / s, H / s
    im = im.resize((W, H), Image.BILINEAR, box=((W - w2) / 2, (H - h2) / 2, (W + w2) / 2, (H + h2) / 2))
    return np.asarray(im, np.float32) / 255

def to_red(a):
    l = a[..., 0] * 0.35 + a[..., 1] * 0.5 + a[..., 2] * 0.15
    return np.clip(l[..., None] * np.array([1.45, 0.20, 0.14], np.float32) + a * 0.08, 0, 1)

# ---------------------------------------------------------------- sorgenti
class ClipReader:
    """clip inserita: porzione (zoom), speed ramp 60% -> 100% fino al beat successivo,
    più corta dello spazio: rallenta fino al 70% poi ripete; più lunga: si taglia la fine"""
    def __init__(self, d, skip):
        self.n = fr(d["t1"]) - fr(d["t0"])
        src = os.path.join(PREP, f"{d['name']}.mp4")
        clen = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                     "format=duration", "-of", "csv=p=0", src])) - d.get("inp", 0.0)
        slot = self.n / FPS; ramp = d.get("ramp", False)
        tb = (next_beat(d["t0"]) - d["t0"]) if ramp else 0.0
        need = content(slot, d["t0"], ramp)
        minsp = 0.8 if d.get("slow08") else 0.7
        sp = 1.0 if need <= clen else max(minsp, (clen - 0.6 * tb) / max(0.01, slot - tb))
        a = 0.6 * tb
        expr = f"if(lt(T,{a:.4f}),T/0.6,{tb:.4f}+(T-{a:.4f})/{sp:.4f})" if ramp else f"T/{sp:.4f}"
        z = d.get("zoom", 1.0)
        vf = ""
        if z > 1.001:
            cx, cy = d.get("cx", 0.5), d.get("cy", 0.5)
            vf = (f"crop=iw/{z}:ih/{z}:'min(max(iw*{cx}-iw/{2*z},0),iw-iw/{z})':"
                  f"'min(max(ih*{cy}-ih/{2*z},0),ih-ih/{z})',scale={W}:{H}:flags=lanczos,")
        vf += f"setpts=PTS-STARTPTS,setpts='({expr})/TB',fps={FPS}"
        loop = ["-stream_loop", "-1"] if content(slot, d["t0"], ramp, sp) > clen + 0.05 \
            and not d.get("slow08") else []
        cmd = ["ffmpeg", "-v", "error"] + loop + ["-ss", f"{d.get('inp', 0.0):.3f}", "-i", src, "-vf", vf,
               "-frames:v", str(self.n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.red = d.get("grade") == "red"; self.last = None
        for _ in range(skip): self.read()
    def read(self):
        buf = self.p.stdout.read(W * H * 3)
        if len(buf) == W * H * 3:
            a = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
            self.last = to_red(a) if self.red else a
        return self.last
    def close(self): self.p.kill(); self.p.wait()

class BlackReader:
    def __init__(self, d, skip): pass
    def read(self): return np.zeros((H, W, 3), np.float32)
    def close(self): pass

class MapReader:
    """v3: ogni fotogramma d'uscita prende il fotogramma di clip più vicino al tempo voluto
    (map: tratti lineari, mai in loop). frames+speed: lista di fotogrammi sorgente (per
    escludere quelli difettosi) a velocità fissa; finita la lista, nero.
    zoom/cx/cy: porzione fissa; zoomramp: zoom lento lungo l'inserto."""
    def __init__(self, d, skip):
        self.d = d; self.n = fr(d["t1"]) - fr(d["t0"]); self.k = skip
        src = os.path.join(PREP, f"{d['name']}.mp4")
        r = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
             "-show_entries", "stream=r_frame_rate,nb_read_frames", "-of", "csv=p=0", src]).decode().strip()
        rate, nb = r.split(","); a_, b_ = rate.split("/"); sf = float(a_) / float(b_); nb = int(nb)
        idx = []
        for k in range(self.n):
            t = (fr(d["t0"]) + k) / FPS
            if "frames" in d:
                j = int(math.floor(k * sf * d["speed"] / FPS + 1e-6))
                idx.append(d["frames"][j] if j < len(d["frames"]) else None)
                continue
            c = None
            for (a, b, c0, c1) in d["map"]:
                if a - 1e-6 <= t < b + 1e-6:
                    c = c0 + (t - a) * (c1 - c0) / max(1e-6, b - a); break
            if c is None: c = d["map"][-1][3]
            idx.append(min(nb - 1, max(0, int(round(c * sf)))))
        self.idx = idx
        z = d.get("zoom", 1.0); vf = "null"
        if z > 1.001:
            cx, cy = d.get("cx", 0.5), d.get("cy", 0.5)
            vf = (f"crop=iw/{z}:ih/{z}:'min(max(iw*{cx}-iw/{2*z},0),iw-iw/{z})':"
                  f"'min(max(ih*{cy}-ih/{2*z},0),ih-ih/{z})',scale={W}:{H}:flags=lanczos")
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-vf", vf, "-f", "rawvideo",
                                   "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.pos = -1; self.cur = None
    def _seek(self, j):
        while self.pos < j:
            buf = self.p.stdout.read(W * H * 3)
            if len(buf) < W * H * 3: break
            self.cur = buf; self.pos += 1
    def read(self):
        k = min(self.k, self.n - 1); self.k += 1
        j = self.idx[k]
        if j is None: return np.zeros((H, W, 3), np.float32)
        self._seek(j)
        a = np.frombuffer(self.cur, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
        zr = self.d.get("zoomramp")
        if zr:
            s = zr[0] + (zr[1] - zr[0]) * k / max(1, self.n - 1)
            if s > 1.001: a = punch(a, s)
        return a
    def close(self): self.p.kill(); self.p.wait()

class PenReader:
    """immagine ferma: push in 1.00 -> 1.08 verso il pennino e tremolio di luce (la mano è ferma)"""
    NIB = (545, 738)
    def __init__(self, d, skip):
        self.n = fr(d["t1"]) - fr(d["t0"]); self.k = skip
        im = Image.open(os.path.join(PREP, "penna.png")).convert("RGB")   # già ritagliata 9:16
        src = Image.open(SRC["penna"]); self.sx = im.size[0] / (src.size[1] * 9 / 16)
        self.x0 = (src.size[0] - src.size[1] * 9 / 16) / 2
        self.im = im
        rng = np.random.default_rng(fr(d["t0"]))
        noise = np.convolve(rng.normal(0, 1, self.n + 8), np.ones(5) / 5, mode="same")[:self.n]
        self.flick = 1 + 0.045 * noise / (np.abs(noise).max() + 1e-6)
    def read(self):
        u = self.k / max(1, self.n - 1); s = 1.0 + 0.08 * u
        iw, ih = self.im.size
        nx = (self.NIB[0] - self.x0) * self.sx; ny = self.NIB[1] * self.sx
        fx, fy = nx / iw, ny / ih
        w2, h2 = iw / s, ih / s
        l, t = nx - fx * w2, ny - fy * h2
        img = self.im.transform((W, H), Image.EXTENT, (l, t, l + w2, t + h2), Image.BICUBIC)
        a = np.asarray(img, np.float32) / 255 * self.flick[min(self.k, self.n - 1)]
        self.k += 1
        return np.clip(a, 0, 1)
    def close(self): pass

class HookReader:
    def __init__(self, d, skip):
        p = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", "1.0", "-i",
                                     os.path.join(PREP, "candela.mp4"), "-frames:v", "1",
                                     "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
        a = np.frombuffer(p, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
        paste_block(a, HOOK_TXT, H / 2, 99)
        self.a = a
    def read(self): return self.a.copy()
    def close(self): pass

_bgcache = {}
def bg_frames(clip):
    if clip not in _bgcache:
        _bgcache[clip] = np.load(os.path.join(PREP, f"bg_{clip}.npy"), mmap_mode="r")
    return _bgcache[clip]

def bg_frame(d, f):
    """sfondo: porzione ingrandita, pan, rotazione ±1,5°, zoom lento 1.00 -> 1.06,
    sfocato (gaussian ~20 px su 1080) e scurito al 28%"""
    arr = bg_frames(d["clip"])
    n = fr(d["t1"]) - fr(d["t0"]); k = f - fr(d["t0"]); u = k / max(1, n - 1)
    src = Image.fromarray(np.asarray(arr[(d["off"] + k) % len(arr)]))
    s = d["zoom"] * (1.0 + 0.06 * u)
    ang = math.radians(d["rot"][0] + (d["rot"][1] - d["rot"][0]) * u)
    cx = BW * (0.5 + (d["cx"] - 0.5) * (1 - 1 / s) + d["pan"][0] * u)
    cy = BH * (0.5 + (d["cy"] - 0.5) * (1 - 1 / s) + d["pan"][1] * u)
    shake = {1: 1.0, 3: 3.0}.get(d["lvl"], 0.0)          # scossa costante nelle strofe (px a 1/3)
    if shake:
        rng = np.random.default_rng(f * 3 + 1)
        cx += rng.uniform(-shake, shake) / 3; cy += rng.uniform(-shake, shake) / 3
    ca, sa = math.cos(ang) / s, math.sin(ang) / s
    # mappa uscita -> ingresso: p_in = c + R(ang)/s * (p_out - centro_out)
    a, b = ca, -sa; c = cx - ca * BW / 2 + sa * BH / 2
    d_, e = sa, ca; g = cy - sa * BW / 2 - ca * BH / 2
    im = src.transform((BW, BH), Image.AFFINE, (a, b, c, d_, e, g), Image.BILINEAR)
    chor = d["lvl"] in (2, 4)
    # ritornelli: oscuramento dimezzato (luminosità 64% invece di 28%) e sfocatura più leggera
    im = im.filter(ImageFilter.GaussianBlur(4.0 if chor else 6.7)).resize((W, H), Image.BILINEAR)
    return np.asarray(im, np.float32) / 255 * (0.64 if chor else 0.28)

class Sources:
    def __init__(self): self.cur = (None, None)
    def at(self, f):
        for j, d in enumerate(inserts):
            if fr(d["t0"]) <= f < fr(d["t1"]):
                if self.cur[0] != j:
                    if self.cur[1]: self.cur[1].close()
                    R = {"aggancio": HookReader, "penna": PenReader}.get(d["name"], ClipReader)
                    if d["name"] == "nero": R = BlackReader
                    elif "map" in d or "frames" in d: R = MapReader
                    self.cur = (j, R(d, f - fr(d["t0"])))
                return self.cur[1].read()
        for d in bg:
            if fr(d["t0"]) <= f < fr(d["t1"]):
                return bg_frame(d, f)
        return None

# ---------------------------------------------------------------- frame
def render_frame(f, src):
    t = f / FPS; sec = section(t)
    frame = src.copy() if src is not None else np.zeros((H, W, 3), np.float32)
    if sec[0] in ("strofa1", "strofa2") and src is not None and not any(
            fr(d["t0"]) <= f < fr(d["t1"]) for d in bg):   # scossa leggera anche sulle clip in strofa
        a = 2 if sec[3] == 1 else 5
        rng = np.random.default_rng(f * 7 + 3)
        frame = np.roll(frame, tuple(int(v) for v in rng.integers(-a, a + 1, 2)), axis=(0, 1))
    p = pulse(t)
    if p > 0.002:
        frame = frame * (1 - VIG * p) + RED_F * (VIG * p)
        lk = leak(t, (0.10 if sec[3] == 2 else 0.16) + 0.6 * (p - 0.04))
        frame = 1 - (1 - frame) * (1 - lk)
    if f >= fr(HOOK): draw_phrases(frame, f)
    if fr(TB) <= f < fr(TB_END): paste_block(frame, TEMPO_IMG, Y_TEMPO, f - fr(TB))
    if fr(TB2) <= f < fr(TB_END): paste_block(frame, BAST_IMG, Y_BAST, f - fr(TB2))
    if f >= fr(HIT1): paste_block(frame, NMF, Y_NMF, f - fr(HIT1))
    if f >= fr(HIT2): paste_block(frame, IP, Y_IP, f - fr(HIT2))
    if f >= fr(STUDIO_FADE):
        paste_block(frame, CS, Y_CS, 99, min(1.0, (f - fr(STUDIO_FADE)) / (0.5 * FPS)))
    for g0, amp in GL_FRAMES:
        if g0 <= f < g0 + (4 if amp > 10 else 2): frame = glitch(frame, f - g0, amp, f)
    # zoom punch sulle casse (+4% e ritorno in 4 frame); sobrio nella strofa 1
    if sec[3] >= 1 and sec[0] not in ("tempo_bastardo",):
        arr = KICK_STRONG if sec[3] == 1 else KICK_T
        dk = last_event(arr, t)
        if dk is not None and dk < 4 / FPS:
            amp = {1: 0.025, 2: 0.04, 3: 0.04, 4: 0.05}[sec[3]]
            frame = punch(frame, 1 + amp * [1, 0.75, 0.5, 0.25][min(3, int(dk * FPS))])
    if f in FLASHES:                                   # flash bianco (porta -> cuffie)
        frame = frame * (1 - FLASHES[f]) + FLASHES[f]
    # grana: nei ritornelli al massimo metà di quella del resto del video
    frame = frame + GRAIN[((f // GRAIN_STEP) * 7) % len(GRAIN)] * (0.5 if in_chorus(t) else 1.0)
    rem = (N - 1 - f) / FPS
    if rem < 0.5: frame *= max(0.0, rem / 0.5)
    return (np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8)

def frames_range(f0, f1):
    srcs = Sources()
    for f in range(f0, f1):
        yield f, render_frame(f, srcs.at(f))

if "--preview" in ARGS:
    os.makedirs(os.path.join(WORK, "preview"), exist_ok=True)
    for t in [float(x) for x in arg("--preview").split(",")]:
        f = fr(t)
        img = render_frame(f, Sources().at(f))
        Image.fromarray(img).save(os.path.join(WORK, "preview", f"{t:07.2f}.jpg"), quality=88)
    sys.exit()

t0, t1 = [float(x) for x in arg("--range", f"0,{DUR_V}").split(",")]
F0, F1 = fr(t0), min(N, fr(t1))
OUT = arg("--out")
if "--inter" in ARGS:
    enc_args = ["-c:v", "libx264", "-preset", "ultrafast", "-crf", "8", "-pix_fmt", "yuv420p", OUT]
    inputs = []
else:
    fade = ["-af", f"afade=t=out:st={DUR_V - 0.5 - F0 / FPS:.3f}:d=0.5"] if F1 == N else []
    inputs = ["-ss", f"{F0 / FPS:.3f}", "-i", AUDIO, "-map", "0:v", "-map", "1:a"] + fade
    enc_args = ["-t", f"{(F1 - F0) / FPS:.3f}", "-c:v", "libx264", "-preset", "slow",
                "-crf", arg("--crf", "20"), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", OUT]
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"] + inputs + enc_args, stdin=subprocess.PIPE)
for f, img in frames_range(F0, F1):
    enc.stdin.write(img.tobytes())
    if f % 300 == 0: print(f"frame {f}/{F1}", flush=True)
enc.stdin.close(); enc.wait()
print("ok", OUT)
