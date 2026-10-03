"""Render del video "Non Mi Fermo" (BRIEF.md + revisione 2).

Uso:  python3 tools/render.py WORKDIR [--plan] [--preview t1,t2,...]
                                      [--range t0,t1 --out FILE] [--crf N]
WORKDIR contiene audio_cut.wav (traccia tagliata di 4,5 s con fade in),
beats.json (beat e colpi di cassa), Anton-Regular.ttf e Montserrat.ttf (variabile).
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
CRF = int(ARGS[ARGS.index("--crf") + 1]) if "--crf" in ARGS else 20

def arg(name):
    return ARGS[ARGS.index(name) + 1] if name in ARGS else None

def clip(prefix):
    d = os.path.join(ROOT, "clip")
    return os.path.join(d, next(f for f in sorted(os.listdir(d)) if f.startswith(prefix)))

SRC = {
    "corridoio": clip("The-hooded-young-man-keeps-walking-slowl"),
    "studio":    clip("The-hooded-young-man-seen-from-behind"),
    "tv":        clip("The-old-CRT-television-keeps-showing-rea"),
    "strada":    clip("hf_20261003_151301_"),
    "candela":   clip("hf_20261003_154346_"),
    "penna":     clip("Scrittura notturna"),
}

# ---------------------------------------------------------------- dati
sync = json.load(open(os.path.join(ROOT, "out", "sync.json")))
WORDS = sync["parole"]
BEATS = json.load(open(os.path.join(WORK, "beats.json")))
beats = np.array(BEATS["beats"])
DUR = float(subprocess.check_output(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", AUDIO]))
N = int(DUR * FPS)                       # numero di frame (ultimo frame entro la traccia)
DUR_V = N / FPS

def snap(t):
    """beat più vicino (la griglia è estesa all'indietro per l'intro senza batteria)"""
    period = float(np.median(np.diff(beats)))
    grid = np.concatenate([beats[0] - period * np.arange(30, 0, -1), beats])
    return float(grid[np.argmin(np.abs(grid - t))])

def fr(t): return int(round(t * FPS))

def find_line(prefix, occ=None):
    """indici delle parole delle righe che iniziano con prefix (una lista per occorrenza)"""
    groups, cur, last = [], [], None
    for i, w in enumerate(WORDS):
        if w["testo_riga"].lower().startswith(prefix.lower()):
            if last is not None and (w["idx_riga"] != WORDS[last]["idx_riga"]):
                groups.append(cur); cur = []
            cur.append(i); last = i
    if cur: groups.append(cur)
    return groups if occ is None else groups[occ]

def line_span(group):
    """da inizio prima parola a inizio prima parola della riga successiva"""
    a = WORDS[group[0]]["inizio"]
    nxt = group[-1] + 1
    b = WORDS[nxt]["inizio"] if nxt < len(WORDS) else WORDS[group[-1]]["fine"]
    return a, b

def word_t(text, after=0.0):
    for w in WORDS:
        if w["parola"].lower().strip(",.?!") == text.lower() and w["inizio"] >= after:
            return w["inizio"]
    raise KeyError(text)

# ---------------------------------------------------------------- scaletta (invariata)
TORNO = 8.85        # attacco vocale di "Torno" (energia 300-3000 Hz; ASR: 8.80)
CUFFIE = 3.25       # nella clip studio: le cuffie arrivano sulla testa
slots = []          # clip a piena luminosità: (nome, t0, t1, opzioni)

cut1 = snap(TORNO - CUFFIE)                       # cambio corridoio -> studio sul beat
slots.append(("corridoio", 0.0, cut1, {"in": 0.0}))
studio_in = CUFFIE - (TORNO - cut1)               # cuffie in testa esattamente su TORNO
cut2 = snap(word_t("Forse"))                      # fine intro sul beat di "Forse"
slots.append(("studio", cut1, cut2, {"in": studio_in}))

for g in find_line("Prendo la penna"):
    a, b = line_span(g)
    slots.append(("penna", snap(a), snap(b), {}))
SPEGNE = 3.25       # nella clip candela: il soffio spegne la fiamma
for g in find_line("Fino a che non si spegne"):
    a, b = line_span(g)
    t0, t1 = snap(a), snap(b)
    cuore = WORDS[g[-1]]["inizio"]
    cin = max(0.0, SPEGNE - (cuore - t0))
    slots.append(("candela", t0, t1, {"in": cin}))

a = word_t("Cambierò")
b = line_span(find_line("Io Non voglio mai assomigliare", 0))[1]
slots.append(("tv", snap(a), snap(b), {"in": 0.0}))
a, b = line_span(find_line("Giro le strade", 0))
slots.append(("strada", snap(a), snap(b), {"in": 0.0}))
slots.sort(key=lambda s: s[1])

# Ritornelli
chorus = []
idx = [i for i, w in enumerate(WORDS) if w["sezione"] == "rit"]
blocks, cur = [], [idx[0]]
for i in idx[1:]:
    if i == cur[-1] + 1: cur.append(i)
    else: blocks.append(cur); cur = [i]
blocks.append(cur)
for bl in blocks:
    a = snap(WORDS[bl[0]]["inizio"])
    nxt = bl[-1] + 1
    b = WORDS[nxt]["inizio"] if nxt < len(WORDS) else WORDS[bl[-1]]["fine"] + 0.6
    chorus.append((a, b))
def in_chorus(t): return any(a <= t < b for a, b in chorus)

hop = BEATS["hop"]; env = np.array(BEATS["env_kick"])
kicks = [k for k in BEATS["kicks"] if env[min(len(env) - 1, int(k / hop))] > 0.3 or
         env[max(0, int(k / hop) - 2):int(k / hop) + 3].max() > 0.3]

t_tempo = word_t("tempo")
TB = snap(t_tempo)
TB_END = word_t("Sotto", TB)

last_word = WORDS[-1]
coda_hits = [k for k in BEATS["kicks"] if k > last_word["fine"] + 1.5 and
             env[max(0, int(k / hop) - 2):int(k / hop) + 3].max() > 0.6]
HIT1, HIT2 = coda_hits[0], coda_hits[1]
STUDIO_FADE = (float(beats[beats > HIT2 + 0.2][0]), 0.5)   # beat dopo "IPNOS"
CLOSE = chorus[-1][1]                                      # da qui nero fino alla fine

# ---------------------------------------------------------------- sfondi sfocati
# Strofa 1: studio. Ritornelli: candela/penna alternate per riga. Strofa 2: strada/TV
# alternate ogni due righe. Nero solo su TEMPO BASTARDO e nella chiusura.
def line_starts(t0, t1):
    seen, out = set(), []
    for w in WORDS:
        if t0 <= w["inizio"] < t1 and w["idx_riga"] not in seen:
            seen.add(w["idx_riga"]); out.append(w["inizio"])
    return out

bg = []   # (nome, t0, t1)
def add_bg(name, t0, t1):
    if t1 - t0 > 0.05: bg.append((name, t0, t1))
add_bg("studio", cut2, TB)
add_bg("studio", TB_END, chorus[0][0])
for ci, (ca, cb) in enumerate(chorus):
    starts = [snap(s) for s in line_starts(ca, cb)]
    starts[0] = ca
    edges = starts + [cb]
    for k in range(len(starts)):
        add_bg(["candela", "penna"][k % 2], edges[k], edges[k + 1])
s2 = [snap(s) for s in line_starts(chorus[0][1], chorus[1][0])][::2]
s2[0] = chorus[0][1]
edges = s2 + [chorus[1][0]]
for k in range(len(s2)):
    add_bg(["strada", "tv"][k % 2], edges[k], edges[k + 1])

PLAN = {"durata_video": DUR_V, "frames": N, "slots": [(s[0], round(s[1], 3), round(s[2], 3),
        {k: round(v, 3) for k, v in s[3].items()}) for s in slots],
        "sfondi": [(n, round(a, 2), round(b, 2)) for n, a, b in bg],
        "ritornelli": [(round(a, 2), round(b, 2)) for a, b in chorus],
        "tempo_bastardo": [round(TB, 3), round(TB_END, 3)],
        "coda": [round(HIT1, 3), round(HIT2, 3), round(STUDIO_FADE[0], 3)]}

# ---------------------------------------------------------------- frasi
KEY = {"cuore", "tempo", "bastardo", "rischiare", "mente", "buio", "scuro", "eterno",
       "muore", "tradito", "penna", "voce", "respiro"}
GLITCH = {"bastardo", "muore", "tradito", "buio", "scuro"}
def clean(w): return w.lower().strip(",.?!")
red = [clean(w["parola"]) in KEY for w in WORDS]
nmf = [False] * len(WORDS)
for i in range(len(WORDS) - 2):
    if [clean(WORDS[i + k]["parola"]) for k in range(3)] == ["non", "mi", "fermo"]:
        red[i] = red[i + 1] = red[i + 2] = True
        nmf[i + 1] = nmf[i + 2] = True          # non spezzare dentro "non mi fermo"

NO_END = {"il", "la", "lo", "le", "i", "un", "una", "di", "a", "da", "in", "con", "per", "che",
          "e", "ma", "mi", "ti", "ci", "non", "sul", "nel", "nei", "dentro", "sotto", "dell'arte",
          "io", "tu", "è", "sto", "coi", "dalle", "quando", "fino", "al", "sia", "ho"}
BREAK_BEFORE = {"che", "ma", "e", "per", "quando", "fino", "dentro", "sotto", "in", "con", "di"}

def split_phrase(ix):
    """spezza una riga in frasi da 2-4 parole ai respiri (pause più lunghe)"""
    if len(ix) <= 4: return [ix]
    best, bk = -1e9, None
    for k in range(2, len(ix) - 1):
        gap = WORDS[ix[k]]["inizio"] - WORDS[ix[k - 1]]["inizio"]
        sc = gap
        if clean(WORDS[ix[k]]["parola"]) in BREAK_BEFORE: sc += 0.12
        if clean(WORDS[ix[k - 1]]["parola"]) in NO_END: sc -= 0.25
        if nmf[ix[k]]: sc -= 5
        sc -= 0.03 * abs(len(ix) - 2 * k)
        if sc > best: best, bk = sc, k
    return split_phrase(ix[:bk]) + split_phrase(ix[bk:])

lines = {}
for i, w in enumerate(WORDS):
    if w["inizio"] < TORNO - 0.2: continue                   # intro: nessun testo
    if TB - 0.05 <= w["inizio"] < TB_END and clean(w["parola"]) in ("tempo", "bastardo"):
        continue                                              # blocco TEMPO BASTARDO
    lines.setdefault(w["idx_riga"], []).append(i)
phrases = []
for li in sorted(lines):
    phrases += split_phrase(lines[li])
PHR = []   # (indici, frame_inizio, frame_fine)
for p, ix in enumerate(phrases):
    a = WORDS[ix[0]]["inizio"]
    nxt = WORDS[phrases[p + 1][0]]["inizio"] if p + 1 < len(phrases) else WORDS[ix[-1]]["fine"] + 0.6
    end = nxt if nxt - WORDS[ix[-1]]["inizio"] < 1.4 else WORDS[ix[-1]]["inizio"] + 1.0
    if a < TB <= end: end = TB
    end = min(end, CLOSE)
    PHR.append((ix, fr(a), fr(end)))
PLAN["frasi"] = [" ".join(WORDS[i]["parola"] for i in ix) for ix, _, _ in PHR]
if "--plan" in ARGS:
    print(json.dumps(PLAN, indent=1, ensure_ascii=False)); sys.exit()

# ---------------------------------------------------------------- font e testo
_fc = {}
def font(kind, size):
    k = (kind, size)
    if k not in _fc:
        if kind == "anton": _fc[k] = ImageFont.truetype(ANTON, size)
        else:
            f = ImageFont.truetype(MONT, size); f.set_variation_by_name(kind); _fc[k] = f
    return _fc[k]

BASE, KEYF, MAXW, TEXT_Y = 70, 1.4, int(W * 0.8), int(H * 0.58)
GRAY = (128, 128, 128)
SHADOW_PAD = 40

def phrase_layout(ix):
    size = BASE
    while True:
        items = []
        for i in ix:
            t = WORDS[i]["parola"].upper()
            f = font("anton", int(size * KEYF)) if red[i] else font("SemiBold", size)
            items.append((i, t, f, f.getlength(t)))
        sp = size * 0.32
        tw = sum(x[3] for x in items) + sp * (len(items) - 1)
        if tw <= MAXW or size < 30: break
        size -= 2
    return items, sp, tw, size

_lay = {}
def layout(p):
    if p not in _lay: _lay[p] = phrase_layout(PHR[p][0])
    return _lay[p]

def phrase_img(p, cur, typed):
    """premoltiplicato: (C rgb, A alpha) float32. cur = indice parola cantata;
    typed = None oppure {indice parola: lettere visibili} (macchina da scrivere)."""
    items, sp, tw, size = layout(p)
    asc = int(size * KEYF * 1.15)
    w = int(tw) + 2 * SHADOW_PAD
    h = asc + int(size * 0.5) + 2 * SHADOW_PAD
    col = Image.new("RGB", (w, h), 0); mask = Image.new("L", (w, h), 0)
    dc, dm = ImageDraw.Draw(col), ImageDraw.Draw(mask)
    x, base = SHADOW_PAD, SHADOW_PAD + asc
    for (i, t, f, wl) in items:
        n = len(t) if typed is None else typed.get(i, 0)
        if n > 0:
            s = t[:n]
            if red[i]: c = RED if i == cur else tuple(int(v * 0.5) for v in RED)
            else: c = (255, 255, 255) if i == cur else GRAY
            dc.text((x, base), s, font=f, fill=c, anchor="ls")
            dm.text((x, base), s, font=f, fill=255, anchor="ls")
        x += wl + sp
    m = np.asarray(mask, np.float32) / 255
    sh = np.asarray(mask.filter(ImageFilter.GaussianBlur(10)), np.float32) / 255
    A = m + np.clip(sh * 1.5, 0, 1) * 0.75 * (1 - m)
    C = np.asarray(col, np.float32) / 255
    return C, A, base

def blur_ca(C, A, r):
    if r < 0.3: return C, A
    ci = Image.fromarray((C * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))
    ai = Image.fromarray((A * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))
    return np.asarray(ci, np.float32) / 255, np.asarray(ai, np.float32) / 255

def paste_pm(frame, C, A, x0, y0, op=1.0):
    h, w = A.shape
    x0, y0 = int(round(x0)), int(round(y0))
    fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if fx1 <= fx0 or fy1 <= fy0: return
    a = A[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0, None] * op
    c = C[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0] * op
    frame[fy0:fy1, fx0:fx1] = frame[fy0:fy1, fx0:fx1] * (1 - a) + c

# blocchi grandi (TEMPO BASTARDO, chiusura) in Anton, come prima
def block_img(lines_, size, color, maxw=880, tracking=0, alpha=1.0, shadow=True):
    while True:
        f = font("anton", size)
        widths = [(sum(f.getlength(c) for c in ln) + tracking * (len(ln) - 1)) if tracking
                  else f.getlength(ln) for ln in lines_]
        if max(widths) <= maxw or size < 40: break
        size = int(size * 0.97)
    lh = int(size * 1.02); pad = 60
    w = int(max(widths)) + 2 * pad; h = lh * len(lines_) + 2 * pad
    mask = Image.new("L", (w, h), 0); d = ImageDraw.Draw(mask)
    for i, ln in enumerate(lines_):
        x = pad + (max(widths) - widths[i]) / 2; y = pad + i * lh
        if tracking:
            for c in ln: d.text((x, y), c, font=f, fill=255); x += f.getlength(c) + tracking
        else: d.text((x, y), ln, font=f, fill=255)
    m = np.asarray(mask, np.float32) / 255
    A = m.copy()
    if shadow:
        sh = np.asarray(mask.filter(ImageFilter.GaussianBlur(16)), np.float32) / 255
        A = m + np.clip(sh * 1.6, 0, 1) * 0.85 * (1 - m)
    C = (np.array(color, np.float32) / 255) * m[..., None]
    return C * alpha, A * alpha, lh * len(lines_), size

def zoomed(C, A, s):
    if abs(s - 1) < 1e-3: return C, A
    h, w = A.shape; nw, nh = int(w * s), int(h * s)
    ci = Image.fromarray((C * 255).astype(np.uint8)).resize((nw, nh), Image.BICUBIC)
    ai = Image.fromarray((A * 255).astype(np.uint8)).resize((nw, nh), Image.BICUBIC)
    return np.asarray(ci, np.float32) / 255, np.asarray(ai, np.float32) / 255

ZOOM = [1.15, 1.10, 1.05]
def zoom_for(k): return ZOOM[k] if 0 <= k < len(ZOOM) else 1.0

TBimg = block_img(["TEMPO", "BASTARDO"], 230, RED)
NMF = block_img(["NON MI FERMO"], 190, (255, 255, 255))
IP = block_img(["IPNOS"], 300, RED, shadow=False)
# IPNOS CREATIVE STUDIO: circa il doppio di prima, peso pieno (Anton, bianco 85%)
CS = block_img(["IPNOS CREATIVE STUDIO"], 116, (255, 255, 255), maxw=int(W * 0.9),
               tracking=6, alpha=0.85, shadow=False)
gap1, gap2 = 10, 110
nmf_h, ip_h, cs_h = NMF[2], IP[2], CS[2]
blk = nmf_h + gap1 + ip_h + gap2 + cs_h
top = H / 2 - blk / 2
Y_NMF = top + nmf_h / 2
Y_IP = top + nmf_h + gap1 + ip_h / 2
Y_CS = top + nmf_h + gap1 + ip_h + gap2 + cs_h / 2
assert 0.2 * H <= top and top + blk <= 0.8 * H, (top, blk)

_zc = {}
def block_at(key, img, k):
    s = zoom_for(k)
    if (key, s) not in _zc: _zc[(key, s)] = zoomed(img[0], img[1], s)
    return _zc[(key, s)]

# ---------------------------------------------------------------- effetti
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
VIG = np.clip((r - 0.25) / 0.75, 0, 1) ** 1.5
VIG = (VIG / VIG.max()).astype(np.float32)[..., None]
del yy, xx, r
RED_F = np.array(RED, np.float32) / 255
kick_arr = np.array(kicks)

def pulse(t):
    if not in_chorus(t): return 0.0
    past = kick_arr[kick_arr <= t]
    if not len(past): return 0.06
    return 0.06 + 0.29 * math.exp(-(t - past[-1]) / 0.32)

def last_kick_frames(f):
    past = kick_arr[kick_arr <= f / FPS + 1e-6]
    return None if not len(past) else f - fr(past[-1])

# grana leggera: campi di rumore monocromatico a 1/4 di risoluzione, nuovo campo ogni
# 3 frame (look pellicola, e resta comprimibile sotto il limite di peso)
GRAIN_AMP = float(os.environ.get("GRAIN_AMP", "0.010"))
GRAIN_STEP = int(os.environ.get("GRAIN_STEP", "3"))
_rng = np.random.default_rng(7)
GRAIN = []
for _ in range(12):
    g = _rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    g = np.asarray(Image.fromarray(g).resize((W, H), Image.BICUBIC), np.float32)
    GRAIN.append((g * GRAIN_AMP)[..., None])
def grain(f):
    return GRAIN[((f // GRAIN_STEP) * 7) % len(GRAIN)]

# light leak rossi morbidi (bassa risoluzione, poi scalati)
LW, LH = 108, 192
ly, lx = np.mgrid[0:LH, 0:LW].astype(np.float32)
LEAKS = [(0.05, 0.25, 0.11, 0.07, 0.55), (0.95, 0.7, 0.08, 0.13, 0.5), (0.2, 0.9, 0.06, 0.09, 0.45)]
def leak(t, inten):
    v = np.zeros((LH, LW), np.float32)
    for k, (cx, cy, fx, fy, s) in enumerate(LEAKS):
        x = (cx + 0.18 * math.sin(t * fx * 2 * math.pi + k)) * LW
        y = (cy + 0.12 * math.sin(t * fy * 2 * math.pi + 2 * k)) * LH
        v += np.exp(-(((lx - x) / (s * LW)) ** 2 + ((ly - y) / (s * LW)) ** 2))
    v = np.clip(v * inten, 0, 1)
    im = Image.fromarray((v * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
    m = np.asarray(im, np.float32)[..., None] / 255
    return m * np.array([1.0, 0.12, 0.04], np.float32)

def glitch(frame, k, seed):
    """RGB split + shake, ampiezza decrescente su 4 frame"""
    amp = [16, 11, 7, 4][k]
    rng = np.random.default_rng(seed)
    dx, dy = rng.integers(-amp, amp + 1, 2)
    out = np.roll(frame, (int(dy), int(dx)), axis=(0, 1))
    out[..., 0] = np.roll(out[..., 0], amp, axis=1)
    out[..., 2] = np.roll(out[..., 2], -amp, axis=1)
    # qualche banda orizzontale spostata
    for _ in range(3):
        y0 = int(rng.integers(0, H - 40)); hh = int(rng.integers(8, 40))
        out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], int(rng.integers(-3 * amp, 3 * amp)), axis=1)
    return out

GL_FRAMES = []
for i, w in enumerate(WORDS):
    if clean(w["parola"]) in GLITCH and w["inizio"] >= TORNO and w["inizio"] < CLOSE:
        GL_FRAMES.append(fr(w["inizio"]))

# ---------------------------------------------------------------- sorgenti video
CROP = "crop='min(iw,ih*9/16)':'min(ih,iw*16/9)'"

class ClipReader:
    def __init__(self, name, t0, t1, opts):
        self.n = fr(t1) - fr(t0)
        src = SRC[name]
        cin = opts.get("in", 0.0)
        probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of", "json", src]))
        clen = float(probe["format"]["duration"]) - cin
        slot = self.n / FPS
        speed = 1.0 if clen >= slot else max(0.7, clen / slot)
        vf = f"{CROP},scale={W}:{H}:flags=lanczos,setpts=PTS/{speed},fps={FPS}"
        loop = ["-stream_loop", "-1"] if clen / speed < slot else []
        cmd = ["ffmpeg", "-v", "error"] + loop + ["-ss", f"{cin:.3f}", "-i", src, "-vf", vf,
               "-frames:v", str(self.n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.last = None
    def read(self):
        buf = self.p.stdout.read(W * H * 3)
        if len(buf) == W * H * 3:
            self.last = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        return self.last
    def close(self):
        self.p.kill(); self.p.wait()

class PenReader:
    """Immagine ferma: push in lento 1.00 -> 1.08 verso il pennino + tremolio della lampada."""
    NIB = (545, 738)
    def __init__(self, t0, t1, seed):
        self.n = fr(t1) - fr(t0); self.k = 0
        im = Image.open(SRC["penna"]).convert("RGB")
        iw, ih = im.size
        self.im, self.x0, self.cw, self.ih = im, (iw - ih * 9 / 16) / 2, ih * 9 / 16, ih
        rng = np.random.default_rng(seed)
        noise = np.convolve(rng.normal(0, 1, self.n + 8), np.ones(5) / 5, mode="same")[:self.n]
        self.flick = 1 + 0.045 * noise / (np.abs(noise).max() + 1e-6)
    def read(self):
        u = self.k / max(1, self.n - 1)
        s = 1.0 + 0.08 * u
        nx, ny = self.NIB
        fx = (nx - self.x0) / self.cw; fy = ny / self.ih
        w2, h2 = self.cw / s, self.ih / s
        left = nx - fx * w2; top_ = ny - fy * h2
        img = self.im.transform((W, H), Image.EXTENT, (left, top_, left + w2, top_ + h2), Image.BICUBIC)
        a = np.asarray(img, np.float32) * self.flick[min(self.k, self.n - 1)]
        self.k += 1
        return np.clip(a, 0, 255).astype(np.uint8)
    def close(self): pass

# sfondi: versioni a 540x960, sfocate (gaussian 20 px sul 1080), scurite al 28%,
# al 70% di velocità e in avanti/indietro così il loop non salta
BW, BH = 540, 960
def bg_file(name):
    out = os.path.join(WORK, f"bg_{name}.mp4")
    if os.path.exists(out): return out
    post = "gblur=sigma=10,colorchannelmixer=rr=0.28:gg=0.28:bb=0.28"
    if name == "penna":
        cmd = ["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", "4", "-i", SRC[name], "-vf",
               f"{CROP},scale={BW}:{BH},fps={FPS},{post}"]
    else:
        trim = "trim=0:3.0," if name == "candela" else ""    # solo fiamma accesa
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", SRC[name], "-filter_complex",
               f"[0:v]{trim}{CROP},scale={BW}:{BH},setpts=(PTS-STARTPTS)/0.7,fps={FPS},{post},"
               f"split[a][b];[b]reverse[r];[a][r]concat=n=2:v=1:a=0"]
    subprocess.check_call(cmd + ["-c:v", "libx264", "-crf", "12", "-preset", "veryfast",
                                 "-pix_fmt", "yuv420p", out])
    return out

class BgReader:
    def __init__(self, name, t0, t1):
        self.n = fr(t1) - fr(t0); self.k = 0
        src = bg_file(name)
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                    "format=duration", "-of", "csv=p=0", src]))
        off = (t0 * 1.37) % max(0.1, dur - 0.2)          # partenze diverse per ogni segmento
        cmd = ["ffmpeg", "-v", "error", "-stream_loop", "-1", "-ss", f"{off:.2f}", "-i", src,
               "-frames:v", str(self.n + 2), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.last = None
    def read(self, f_in_seg):
        buf = self.p.stdout.read(BW * BH * 3)
        if len(buf) == BW * BH * 3:
            self.last = Image.fromarray(np.frombuffer(buf, np.uint8).reshape(BH, BW, 3))
        s = 1.0 + 0.06 * f_in_seg / max(1, self.n - 1)    # zoom lento 1.00 -> 1.06
        w2, h2 = BW / s, BH / s
        box = ((BW - w2) / 2, (BH - h2) / 2, (BW + w2) / 2, (BH + h2) / 2)
        return np.asarray(self.last.resize((W, H), Image.BILINEAR, box=box))
    def close(self):
        self.p.kill(); self.p.wait()

class Sources:
    def __init__(self): self.fg = (None, None); self.bg = (None, None)
    def _get(self, attr, key, make):
        cur_key, rd = getattr(self, attr)
        if cur_key != key:
            if rd: rd.close()
            rd = make(); setattr(self, attr, (key, rd))
        return rd
    def at(self, f):
        for i, (name, t0, t1, opts) in enumerate(slots):
            if fr(t0) <= f < fr(t1):
                rd = self._get("fg", i, lambda: PenReader(t0, t1, int(t0 * 1000)) if name == "penna"
                               else ClipReader(name, t0, t1, opts))
                return rd.read()
        for i, (name, t0, t1) in enumerate(bg):
            if fr(t0) <= f < fr(t1):
                rd = self._get("bg", i, lambda: BgReader(name, t0, t1))
                return rd.read(f - fr(t0))
        return None

# ---------------------------------------------------------------- render
def typed_state(ix, t):
    """macchina da scrivere: lettere visibili per parola (ogni parola si scrive
    in min(0,35 s, durata parola))"""
    out = {}
    for i in ix:
        w = WORDS[i]; L = len(w["parola"])
        d = max(0.08, min(0.35, w["fine"] - w["inizio"]))
        u = (t - w["inizio"]) / d
        out[i] = 0 if u < 0 else min(L, int(math.ceil(u * L)) if u > 0 else 1)
    return out

_pc = {}
def render_frame(f, src):
    t = f / FPS
    frame = (src.astype(np.float32) / 255) if src is not None else np.zeros((H, W, 3), np.float32)
    p = pulse(t)
    if p > 0.002:
        a = VIG * p
        frame = frame * (1 - a) + RED_F * a
        lk = leak(t, 0.18 + 0.9 * (p - 0.06))
        frame = 1 - (1 - frame) * (1 - lk)

    # frasi
    for pi, (ix, f0, f1) in enumerate(PHR):
        if not (f0 <= f < f1): continue
        cur = max([i for i in ix if fr(WORDS[i]["inizio"]) <= f], default=ix[0])
        chor = in_chorus(t)
        if chor:
            typed = typed_state(ix, t)
            key = (pi, cur, tuple(sorted(typed.items())))
            if key not in _pc: _pc[key] = phrase_img(pi, cur, typed)
            C, A, base = _pc[key]; op = 1.0
        else:
            k = f - f0
            r_ = 12 * max(0, 1 - k / 6); op = min(1.0, (k + 1) / 6)
            key = (pi, cur, round(r_, 1))
            if key not in _pc:
                C0, A0, base = phrase_img(pi, cur, None)
                _pc[key] = (*blur_ca(C0, A0, r_), base)
            C, A, base = _pc[key]
        dx = dy = 0
        if chor:
            kf = last_kick_frames(f)
            if kf is not None and kf < 3:
                amp = [6, 4, 2][kf]
                rng = np.random.default_rng(f)
                dx, dy = rng.integers(-amp, amp + 1, 2)
        h, w = A.shape
        paste_pm(frame, C, A, W / 2 - w / 2 + dx, TEXT_Y - base + dy, op)
    if len(_pc) > 400: _pc.clear()

    # TEMPO BASTARDO (nero)
    if fr(TB) <= f < fr(TB_END):
        C, A = block_at("tb", TBimg, f - fr(TB))
        paste_pm(frame, C, A, W / 2 - A.shape[1] / 2, H / 2 - A.shape[0] / 2)
    # chiusura
    for key, img, f0, y in (("nmf", NMF, fr(HIT1), Y_NMF), ("ip", IP, fr(HIT2), Y_IP)):
        if f >= f0:
            C, A = block_at(key, img, f - f0)
            paste_pm(frame, C, A, W / 2 - A.shape[1] / 2, y - A.shape[0] / 2)
    fs = fr(STUDIO_FADE[0])
    if f >= fs:
        al = min(1.0, (f - fs) / (STUDIO_FADE[1] * FPS))
        C, A = CS[0], CS[1]
        paste_pm(frame, C, A, W / 2 - A.shape[1] / 2, Y_CS - A.shape[0] / 2, al)

    for g0 in GL_FRAMES:
        if g0 <= f < g0 + 4:
            frame = glitch(frame, f - g0, f)
    if fr(TB) <= f < fr(TB) + 2:
        frame[:] = 1.0                                   # flash bianco di 2 frame
    frame = frame + grain(f)
    rem = (N - 1 - f) / FPS
    if rem < 0.5: frame *= max(0.0, rem / 0.5)
    return (np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8)

def frames_range(f0, f1):
    srcs = Sources()
    for f in range(f0, f1):
        yield f, render_frame(f, srcs.at(f))

if "--preview" in ARGS:
    ts = [float(x) for x in arg("--preview").split(",")]
    os.makedirs(os.path.join(WORK, "preview"), exist_ok=True)
    for t in ts:
        f = fr(t)
        # parte dall'inizio del segmento per avere lo stato corretto dei lettori
        st = max([fr(a) for (_, a, b, *_) in slots + bg if fr(a) <= f] + [0])
        for g, img in frames_range(st, f + 1): pass
        Image.fromarray(img).save(os.path.join(WORK, "preview", f"{t:07.2f}.jpg"), quality=88)
    sys.exit()

if "--range" in ARGS:
    t0, t1 = [float(x) for x in arg("--range").split(",")]
    F0, F1 = fr(t0), fr(t1)
    OUT = arg("--out")
    afilter = []
else:
    F0, F1 = 0, N
    OUT = os.path.join(ROOT, "out", "non_mi_fermo_1080x1920.mp4")
    afilter = ["-af", f"afade=t=out:st={DUR_V - 0.5:.3f}:d=0.5"]
for name in ("studio", "candela", "penna", "strada", "tv"): bg_file(name)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-ss", f"{F0 / FPS:.3f}", "-i", AUDIO, "-map", "0:v", "-map", "1:a"] + afilter +
    ["-t", f"{(F1 - F0) / FPS:.3f}",
    "-c:v", "libx264", "-preset", "slow", "-crf", str(CRF), "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for f, img in frames_range(F0, F1):
    enc.stdin.write(img.tobytes())
    if f % 300 == 0: print(f"frame {f}/{F1}", flush=True)
enc.stdin.close(); enc.wait()
json.dump(PLAN, open(os.path.join(WORK, "plan.json"), "w"), indent=1, ensure_ascii=False)
print("ok", OUT)
