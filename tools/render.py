"""Render del video "Non Mi Fermo" secondo BRIEF.md.

Uso:  python3 tools/render.py WORKDIR [--plan] [--preview t1,t2,...] [--crf N]
WORKDIR contiene audio_cut.wav (traccia tagliata di 4,5 s con fade in),
beats.json (beat e colpi di cassa) e Anton-Regular.ttf.
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = sys.argv[1]
ARGS = sys.argv[2:]
W, H, FPS = 1080, 1920, 30
RED = (225, 6, 0)            # #E10600
FONT = os.path.join(WORK, "Anton-Regular.ttf")
AUDIO = os.path.join(WORK, "audio_cut.wav")
CRF = int(ARGS[ARGS.index("--crf") + 1]) if "--crf" in ARGS else 20

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

# ---------------------------------------------------------------- scaletta
TORNO = 8.85        # attacco vocale di "Torno" (energia 300-3000 Hz; ASR: 8.80)
CUFFIE = 3.25       # nella clip studio: le cuffie arrivano sulla testa
slots = []          # (nome, t0, t1, opzioni)

cut1 = snap(TORNO - CUFFIE)                       # cambio corridoio -> studio sul beat
slots.append(("corridoio", 0.0, cut1, {"in": 0.0}))
studio_in = CUFFIE - (TORNO - cut1)               # cuffie in testa esattamente su TORNO
cut2 = snap(word_t("Forse"))                      # fine intro sul beat di "Forse"
slots.append(("studio", cut1, cut2, {"in": studio_in}))

# Ritornelli: penna e candela (ogni passaggio del ritornello)
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

# Strofa 2
a = word_t("Cambierò")
b = line_span(find_line("Io Non voglio mai assomigliare", 0))[1]
slots.append(("tv", snap(a), snap(b), {"in": 0.0}))
a, b = line_span(find_line("Giro le strade", 0))
slots.append(("strada", snap(a), snap(b), {"in": 0.0}))
slots.sort(key=lambda s: s[1])

# Ritornelli: intervalli per la pulsazione rossa
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

# Kick per la pulsazione: solo colpi forti
hop = BEATS["hop"]; env = np.array(BEATS["env_kick"])
kicks = [k for k in BEATS["kicks"] if env[min(len(env) - 1, int(k / hop))] > 0.3 or
         env[max(0, int(k / hop) - 2):int(k / hop) + 3].max() > 0.3]

# TEMPO BASTARDO
t_tempo = word_t("tempo")
TB = snap(t_tempo)
TB_END = word_t("Sotto", TB)

# Coda: colpi finali dopo la pausa
last_word = WORDS[-1]
coda_hits = [k for k in BEATS["kicks"] if k > last_word["fine"] + 1.5 and
             env[max(0, int(k / hop) - 2):int(k / hop) + 3].max() > 0.6]
HIT1, HIT2 = coda_hits[0], coda_hits[1]
STUDIO_FADE = (float(beats[beats > HIT2 + 0.2][0]), 0.5)   # beat dopo "IPNOS"

PLAN = {"durata_video": DUR_V, "frames": N, "slots": [(s[0], round(s[1], 3), round(s[2], 3),
        {k: round(v, 3) for k, v in s[3].items()}) for s in slots],
        "ritornelli": [(round(a, 2), round(b, 2)) for a, b in chorus],
        "tempo_bastardo": round(TB, 3), "coda": [round(HIT1, 3), round(HIT2, 3), round(STUDIO_FADE[0], 3)]}
if "--plan" in ARGS:
    print(json.dumps(PLAN, indent=1, ensure_ascii=False)); sys.exit()

# ---------------------------------------------------------------- testo
KEY = {"cuore", "tempo", "bastardo", "rischiare", "mente", "buio", "scuro", "eterno",
       "muore", "tradito"}
def clean(w): return w.lower().strip(",.?!")
red = [clean(w["parola"]) in KEY for w in WORDS]
for i in range(len(WORDS) - 2):
    if [clean(WORDS[i + k]["parola"]) for k in range(3)] == ["non", "mi", "fermo"]:
        red[i] = red[i + 1] = red[i + 2] = True

_font_cache = {}
def font(size):
    if size not in _font_cache: _font_cache[size] = ImageFont.truetype(FONT, size)
    return _font_cache[size]

def text_img(lines, size, color, maxw=880, tracking=0, alpha=1.0, shadow=True):
    """RGBA (numpy float 0-1, premoltiplicato) con il testo e un'ombra morbida."""
    while True:
        f = font(size)
        widths = []
        for ln in lines:
            if tracking:
                widths.append(sum(f.getlength(c) for c in ln) + tracking * (len(ln) - 1))
            else:
                widths.append(f.getlength(ln))
        if max(widths) <= maxw or size < 40: break
        size = int(size * 0.95)
    asc, desc = f.getmetrics()
    lh = int(size * 1.02)
    pad = 60
    w = int(max(widths)) + 2 * pad
    h = lh * len(lines) + 2 * pad
    mask = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(mask)
    for i, ln in enumerate(lines):
        x = pad + (max(widths) - widths[i]) / 2
        y = pad + i * lh
        if tracking:
            for c in ln:
                d.text((x, y), c, font=f, fill=255); x += f.getlength(c) + tracking
        else:
            d.text((x, y), ln, font=f, fill=255)
    m = np.asarray(mask, dtype=np.float32) / 255 * alpha
    rgba = np.zeros((h, w, 4), np.float32)
    if shadow:
        sh = np.asarray(mask.filter(ImageFilter.GaussianBlur(16)), np.float32) / 255
        sh = np.clip(sh * 1.6, 0, 1) * 0.85 * alpha
        rgba[..., 3] = sh
    col = np.array(color, np.float32) / 255
    rgba[..., :3] = rgba[..., :3] * (1 - m[..., None]) + col * m[..., None]
    rgba[..., 3] = rgba[..., 3] * (1 - m) + m
    # bounding box utile (righe/colonne con alpha) per il centraggio
    return rgba, lh * len(lines)

def scale_rgba(img, s):
    if abs(s - 1) < 1e-3: return img
    h, w = img.shape[:2]
    out = []
    pil = Image.fromarray((img * 255).astype(np.uint8), "RGBA")
    pil = pil.resize((max(1, int(w * s)), max(1, int(h * s))), Image.BICUBIC)
    return np.asarray(pil, np.float32) / 255

def paste(frame, rgba, cx, cy):
    h, w = rgba.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    fx0, fy0 = max(0, x0), max(0, y0)
    fx1, fy1 = min(W, x0 + w), min(H, y0 + h)
    if fx1 <= fx0 or fy1 <= fy0: return
    sub = rgba[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0]
    a = sub[..., 3:4]
    region = frame[fy0:fy1, fx0:fx1]
    frame[fy0:fy1, fx0:fx1] = region * (1 - a) + sub[..., :3] * a

ZOOM = [1.15, 1.10, 1.05]      # 1.15 -> 1.00 in 4 frame
def zoom_for(k): return ZOOM[k] if 0 <= k < len(ZOOM) else 1.0

_img_cache = {}
def cached(key, fn):
    if key not in _img_cache: _img_cache[key] = fn()
    return _img_cache[key]

def scaled(key, fn, s):
    return cached((key, round(s, 3)), lambda: scale_rgba(cached(key, fn), s))

# eventi di testo: (frame_inizio, frame_fine, chiave, funzione_immagine, cy)
events = []
for i, w in enumerate(WORDS):
    if w["inizio"] < TORNO - 0.2: continue                  # intro: nessun testo
    if TB - 0.05 <= w["inizio"] < TB_END and clean(w["parola"]) in ("tempo", "bastardo"):
        continue                                             # gestite dal blocco TEMPO BASTARDO
    nxt = WORDS[i + 1]["inizio"] if i + 1 < len(WORDS) else w["fine"] + 0.6
    end = nxt if nxt - w["inizio"] < 1.4 else w["inizio"] + 1.0
    if w["inizio"] < TB <= end: end = TB                     # flash: schermo pulito
    txt = w["parola"].upper()
    color = RED if red[i] else (255, 255, 255)
    key = ("w", txt, color)
    events.append((fr(w["inizio"]), fr(end), key,
                   (lambda t=txt, c=color: text_img([t], 210, c)[0]), H / 2))
events.append((fr(TB), fr(TB_END), ("tb",),
               lambda: text_img(["TEMPO", "BASTARDO"], 230, RED)[0], H / 2))
FLASH = (fr(TB), fr(TB) + 2)

# Chiusura: tre righe centrate e impilate (fascia 20%-80%)
nmf, nmf_h = text_img(["NON MI FERMO"], 190, (255, 255, 255))
ip, ip_h = text_img(["IPNOS"], 300, RED, shadow=False)
cs_size = 58                                      # ~1/4 dell'altezza di "IPNOS"
cs_track = int(cs_size * 0.45)
gap1, gap2 = 10, 50
blk = nmf_h + gap1 + ip_h + gap2 + int(cs_size * 1.02)
top = H / 2 - blk / 2
Y_NMF = top + nmf_h / 2
Y_IP = top + nmf_h + gap1 + ip_h / 2
Y_CS = top + nmf_h + gap1 + ip_h + gap2 + cs_size * 0.51
assert 0.2 * H <= top and top + blk <= 0.8 * H, (top, blk)
events.append((fr(HIT1), N, ("nmf",), lambda: nmf, Y_NMF))
events.append((fr(HIT2), N, ("ip",), lambda: ip, Y_IP))

# ---------------------------------------------------------------- vignettatura rossa
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
VIG = np.clip((r - 0.25) / 0.75, 0, 1) ** 1.5
VIG = (VIG / VIG.max()).astype(np.float32)[..., None]
RED_F = np.array(RED, np.float32) / 255
kick_arr = np.array(kicks)

def pulse(t):
    if not any(a <= t < b for a, b in chorus): return 0.0
    past = kick_arr[kick_arr <= t]
    if not len(past): return 0.06
    dt = t - past[-1]
    # fondo rosso leggero + picco sul colpo di cassa con discesa esponenziale (max 35%)
    return 0.06 + 0.29 * math.exp(-dt / 0.32)

# ---------------------------------------------------------------- sorgenti video
class ClipReader:
    def __init__(self, name, t0, t1, opts):
        self.n = fr(t1) - fr(t0)
        src = SRC[name]
        cin = opts.get("in", 0.0)
        probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of", "json", src]))
        clen = float(probe["format"]["duration"]) - cin
        slot = self.n / FPS
        if clen >= slot: speed = 1.0                     # più lunga: si taglia la fine
        else: speed = max(0.7, clen / slot)              # più corta: rallenta fino al 70%
        self.speed = speed
        vf = (f"crop='min(iw,ih*9/16)':'min(ih,iw*16/9)',scale={W}:{H}:flags=lanczos,"
              f"setpts=PTS/{speed},fps={FPS}")
        loop = ["-stream_loop", "-1"] if clen / speed < slot else []
        cmd = ["ffmpeg", "-v", "error"] + loop + ["-ss", f"{cin:.3f}", "-i", src, "-vf", vf,
               "-frames:v", str(self.n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
        self.p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        self.last = None
    def read(self):
        buf = self.p.stdout.read(W * H * 3)
        if len(buf) == W * H * 3:
            self.last = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        return self.last

class PenReader:
    """Immagine ferma: push in lento 1.00 -> 1.08 verso il pennino + tremolio della lampada."""
    NIB = (545, 738)
    def __init__(self, t0, t1, seed):
        self.n = fr(t1) - fr(t0); self.k = 0
        im = Image.open(SRC["penna"]).convert("RGB")
        iw, ih = im.size
        cw = ih * 9 / 16
        x0 = (iw - cw) / 2
        self.im, self.x0, self.cw, self.ih = im, x0, cw, ih
        rng = np.random.default_rng(seed)
        noise = rng.normal(0, 1, self.n + 8)
        noise = np.convolve(noise, np.ones(5) / 5, mode="same")[:self.n]
        self.flick = 1 + 0.045 * noise / (np.abs(noise).max() + 1e-6)
    def read(self):
        u = self.k / max(1, self.n - 1)
        s = 1.0 + 0.08 * u
        nx, ny = self.NIB
        # finestra sorgente (larghezza cw/s) che tiene il pennino nello stesso punto
        cx0, cw, chh = self.x0, self.cw, self.ih
        fx = (nx - cx0) / cw; fy = ny / chh
        w2, h2 = cw / s, chh / s
        left = nx - fx * w2; top = ny - fy * h2
        box = (left, top, left + w2, top + h2)
        fr_img = self.im.transform((W, H), Image.EXTENT, box, Image.BICUBIC)
        a = np.asarray(fr_img, np.float32) * self.flick[min(self.k, self.n - 1)]
        self.k += 1
        return np.clip(a, 0, 255).astype(np.uint8)

# ---------------------------------------------------------------- render
def render_frame(f, src_frame):
    t = f / FPS
    frame = (src_frame.astype(np.float32) / 255) if src_frame is not None else np.zeros((H, W, 3), np.float32)
    p = pulse(t)
    if p > 0.002:
        a = VIG * p
        frame = frame * (1 - a) + RED_F * a
    for (f0, f1, key, fn, cy) in events:
        if f0 <= f < f1:
            img = scaled(key, fn, zoom_for(f - f0))
            paste(frame, img, W / 2, cy)
    # IPNOS CREATIVE STUDIO in dissolvenza
    fs = fr(STUDIO_FADE[0])
    if f >= fs:
        al = min(1.0, (f - fs) / (STUDIO_FADE[1] * FPS))
        img = cached(("cs", round(al, 2)), lambda: text_img(["IPNOS CREATIVE STUDIO"], cs_size,
                     (255, 255, 255), tracking=cs_track, alpha=0.7 * round(al, 2), shadow=False, maxw=1000)[0])
        paste(frame, img, W / 2, Y_CS)
    if FLASH[0] <= f < FLASH[1]:
        frame[:] = 1.0
    # fade a nero negli ultimi 0,5 s
    rem = (N - 1 - f) / FPS
    if rem < 0.5: frame *= max(0.0, rem / 0.5)
    return (np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8)

def source_at(f, readers):
    t = f / FPS
    for i, (name, t0, t1, opts) in enumerate(slots):
        if fr(t0) <= f < fr(t1):
            if i not in readers:
                readers.clear()
                seed = int(t0 * 1000)
                readers[i] = PenReader(t0, t1, seed) if name == "penna" else ClipReader(name, t0, t1, opts)
            return readers[i].read()
    return None

if "--preview" in ARGS:
    ts = [float(x) for x in ARGS[ARGS.index("--preview") + 1].split(",")]
    os.makedirs(os.path.join(WORK, "preview"), exist_ok=True)
    for t in ts:
        f = fr(t)
        src = None
        for (name, t0, t1, opts) in slots:
            if fr(t0) <= f < fr(t1):
                rd = PenReader(t0, t1, int(t0 * 1000)) if name == "penna" else ClipReader(name, t0, t1, opts)
                for _ in range(f - fr(t0) + 1): src = rd.read()
        Image.fromarray(render_frame(f, src)).save(os.path.join(WORK, "preview", f"{t:07.2f}.jpg"), quality=85)
    sys.exit()

OUT = os.path.join(ROOT, "out", "non_mi_fermo_1080x1920.mp4")
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-i", AUDIO, "-map", "0:v", "-map", "1:a",
    "-af", f"afade=t=out:st={DUR_V - 0.5:.3f}:d=0.5", "-t", f"{DUR_V:.3f}",
    "-c:v", "libx264", "-preset", "slow", "-crf", str(CRF), "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
readers = {}
for f in range(N):
    enc.stdin.write(render_frame(f, source_at(f, readers)).tobytes())
    if f % 300 == 0: print(f"frame {f}/{N}", flush=True)
enc.stdin.close(); enc.wait()
json.dump(PLAN, open(os.path.join(WORK, "plan.json"), "w"), indent=1, ensure_ascii=False)
print("ok", OUT)
