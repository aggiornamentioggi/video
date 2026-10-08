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
             "moneta": "The-old-coin-spins",
             # v4
             "muro": "muro", "fiches": "The-tall-stack-of-poker", "sabbia": "Fine-sand-keeps",
             "clessidra": "The-thin-stream-of-sand",
             # v5
             "cuore": "The-glass-heart",
             # v6
             "cervello": "The-existing-crack-on-the-plaster", "specchi": "Corridoio infinito di specchi",
             "logo": "Logo IPNOS Creative Studio",
             # v8
             "cestino": "A-single-crumpled-paper-ball-falls"}
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

# ---------------------------------------------------------------- v4
# Tagli nuovi sul beat (S = beat più vicino); dove un taglio confina con un inserto v3
# rimasto uguale si usa il suo bordo.
S = snap
def clipend(name): return clip_len(name) - 0.05

def fit(name, t0, t1, c0, c1, minsp=0.75, **o):
    """c0 -> c1 (al più) su [t0, t1]. Clip lunga: velocità 1x. Corta: rallentata fino a
    minsp; se non basta, a minsp fino alla fine e poi ultimo fotogramma tenuto, con uno
    zoom lento lungo tutto l'inserto (mai in loop)."""
    slot, avail = t1 - t0, c1 - c0
    if avail >= slot:
        ins(name, t0, t1, map=[(t0, t1, c0, c0 + slot)], **o); return
    if avail / slot >= minsp - 1e-6:
        ins(name, t0, t1, map=[(t0, t1, c0, c1)], **o); return
    te = t0 + avail / minsp
    o.setdefault("zoomramp", (1.0, 1.10))
    ins(name, t0, t1, map=[(t0, te, c0, c1), (te, t1, c1, c1)], tenuta=round(t1 - te, 2), **o)

# --- intro: IPNOS su nero (due colpi dall'audio) -> corridoio -> porta -> studio, cuffie su "Torno"
IP_A, IP_B = 0.165, 0.655          # attacchi dei due "IPNOS" (banda 4-12 kHz e 400-1000 Hz)
IP_FADE = (1.15, 1.85)             # coda d'eco: la scritta sfuma
TORNO_T = wt("Torno")                                     # 8.80
CUFFIE_C = 3.42                                           # clip studio: cuffie sulla testa
CORR0 = float(GRID[GRID >= IP_FADE[1] - 0.05][0])         # primo beat dopo la coda
STUDIO0 = S(TORNO_T - CUFFIE_C)                           # clip studio da 0 a velocità ~1x
DOOR0 = S(STUDIO0 - 2.1)
DOOR_LEN = 2.4                                            # porta: solo 0-2,4 s (dopo c'è fumo)
ce = clipend("corridoio")
# v6: il corridoio parte subito dal primo fotogramma, in movimento; speed ramp 1,0x -> 0,5x
# verso la porta (versione interpolata a 60 fps, corridoio_hfr: niente scatti). Porta e cuffie fisse.
def corr_speed(u): return 1.0 - 0.5 * (lambda x: x * x * (3 - 2 * x))(min(1.0, max(0.0, (u - 0.30) / 0.70)))
_cm, _c, _n = [], 0.0, 96
for _k in range(_n):
    _a, _b = DOOR0 * _k / _n, DOOR0 * (_k + 1) / _n
    _c1 = _c + (_b - _a) * corr_speed((_k + 0.5) / _n)
    _cm.append((_a, _b, _c, _c1)); _c = _c1
ins("corridoio_hfr", 0.0, DOOR0, map=_cm, zoom=1.25, cx=0.5, cy=0.45, ramp_fine=round(_c, 3))
ins("porta", DOOR0, STUDIO0, map=[(DOOR0, STUDIO0, 0.0, DOOR_LEN)], zoomramp=(1.0, 1.10))
CONF = wt("Confesso")
# v7: studio montato come multicamera: stessa clip, tempo continuo, crop diversi con stacco sul beat
T_DICO1 = S(L("Dico le cose"))                            # qui parte il microfono
_se = clipend("studio")
def studio_c(t):                                          # tempo di clip continuo (cuffie su "Torno")
    if t <= TORNO_T: return CUFFIE_C * (t - STUDIO0) / (TORNO_T - STUDIO0)
    return CUFFIE_C + (_se - CUFFIE_C) * (t - TORNO_T) / (T_DICO1 - TORNO_T)
_g = [float(g) for g in GRID if STUDIO0 + 0.05 < g < T_DICO1 - 0.05]
B1 = _g[0]                                                # 1 beat larga
B2 = [g for g in _g if studio_c(g) <= 1.25][-1]           # stretta sulle cuffie finché sono in mano
CUT_F = CUT_S1                                            # "Forse": beat dopo "Torno sul pezzo"
SHOTS = [(STUDIO0, B1, dict(zoom=1.35, cx=0.48, cy=0.30)),            # 1) larga come prima
         (B1, B2, dict(zoom=2.0, cx=0.47, cy=0.54)),                  # 2) stretta sulle cuffie in mano
         (B2, CUT_F, dict(zoom=1.5, cx=0.40, cy=0.30,                 # 3) media spalle e testa
                         punchin=(TORNO_T, 1.12, 3)))]                # punch-in sul colpo di "Torno"
_fg = [g for g in _g if CUT_F - 0.05 <= g] + [T_DICO1]
for k, (a_, b_) in enumerate(zip(_fg[:-1], _fg[1:])):     # "Forse ci resto": alterna sul beat
    SHOTS.append((a_, b_, dict(zoom=2.0, cx=0.37, cy=0.20) if k % 2 == 0 else dict(zoom=1.4, cx=0.42, cy=0.32)))
for k, (a_, b_, o_) in enumerate(SHOTS):          # la raffica su "Pacato" usa l'inquadratura di prima
    rf = dict(raffica_as=("studio", CUFFIE_C / 2, 1.35, 0.48, 0.30)) if k == 0 else dict(no_raffica=True)
    ins("studio", a_, b_, map=[(a_, b_, studio_c(a_), studio_c(b_))], **o_, **rf)
FLASHES = {}

# --- strofa 1
T_VOR = S(L("Vorrei non ci fosse")); T_MENTE = S(L("La mente"))
fit("microfono", T_DICO1, T_VOR, 0.0, clipend("microfono"), zoomramp=(1.0, 1.15),   # v7: da "Dico le cose"
    raffica_as=("microfono", (T_VOR - CONF) / 2, 1.0, 0.5, 0.5))
ins("tramonto", T_VOR, T_MENTE, map=[(T_VOR, T_MENTE, 0.0, 0.8 * (T_MENTE - T_VOR))])
T_FRESCO = S(L("Torno fresco"))
fit("pozzo", T_MENTE, T_FRESCO, 0.0, clipend("pozzo"), zoomramp=(1.0, 1.18))
T_DOM = S(L("Dico solo che non"))              # v6: specchi anche su "e domani resto"
QUELLO = wt("quello", T_FRESCO)                 # v6: corridoio degli specchi, carrello in avanti
ins("specchi", T_FRESCO, T_DOM, pulse_at=QUELLO)
T_INV = S(L("Voglio tutto quello")); CROLLO_PRIMA = 1.50
T_DICO = T_DOM                                  # v6: la strada qui non c'è più (resta nella strofa 2)
# v6: "Dico solo che non voglio il resto": stretto sulla fiche rossa in piedi in primo piano, dai
# primi fotogrammi (prima del crollo, a 1,58 s); zoom 2,3x (a 2,85x il dettaglio si sgrana)
ins("fiches", T_DICO, T_INV, map=[(T_DICO, T_INV, 0.0, min(CROLLO_PRIMA, T_INV - T_DICO))],
    zoom=2.3, cx=0.468, cy=0.573, zoomramp=(1.0, 1.05), no_raffica=True)
T_FIN = wt("Finire")                                      # scatola (v3)
CROLLO = 1.58                                             # la pila inizia a cadere
TC = S(wt("investo"))
fe = clipend("fiches"); tail = (fe - CROLLO) / 0.75
if T_FIN - TC <= tail + 1e-6:
    fmap = [(T_INV, TC, 0.0, CROLLO), (TC, T_FIN, CROLLO, CROLLO + max(0.75, (fe - CROLLO) / (T_FIN - TC)) * (T_FIN - TC))]
else:
    fmap = [(T_INV, TC, 0.0, CROLLO), (TC, TC + tail, CROLLO, fe), (TC + tail, T_FIN, fe, fe)]
ins("fiches", T_INV, T_FIN, map=fmap, zoomramp=(1.0, 1.06))
a = T_FIN; r = wt("resti", a)
mapped("scatola", a, r, 0.0, 1.40); black(r, wt("Voglio", r))
a = wt("Voglio", r); p = wt("parte", a); e = wt("In", p)
ins("vetro", a, e, map=[(a, p, 0.0, 1.5), (p, e, 1.5, 1.5 + e - p)])   # B: 1,9x fino all'impronta
T_ARTE = e; T_SBATTO = S(L("Per sta roba"))
fit("studio", T_ARTE, T_SBATTO, 0.3, 2.6, zoom=2.2, cx=0.80, cy=0.36)       # stretto sull'attrezzatura
a = L("Solo soldato"); bt = wt("buttato", a); e = L("Pacato")
# v8: "Solo soldato ... ma sono tornato": cestino, solo la prima caduta (0 -> contatto a 0,75 s).
# Avanti rallentata (>= 0,5x, interpolata a 60 fps) con il contatto su "buttato"; poi al contrario,
# palla ferma sul cestino e risalita fuori campo su "tornato". Stacchi sul beat ai due estremi.
CB0, CB1 = S(a), S(wt("Lavorare", a))
CEST_HIT, CEST_OUT = 0.75, 0.54                           # contatto; ingresso in campo dall'alto
TORN = wt("tornato", e)
fit("microfono", T_SBATTO, CB0, 1.6, clipend("microfono"), zoom=1.25, cx=0.6, cy=0.5, zoomramp=(1.0, 1.15))
sp_c = max(0.5, CEST_HIT / (bt - CB0))
t_in = bt - CEST_HIT / sp_c                               # se serve, prima i fotogrammi fermi
t_up = TORN - (CEST_HIT - CEST_OUT) / sp_c                # inizio della risalita al contrario
cmap = ([(CB0, t_in, 0.0, 0.0)] if t_in > CB0 + 1e-3 else []) + [
    (max(CB0, t_in), bt, 0.0, CEST_HIT), (bt, t_up, CEST_HIT, CEST_HIT),
    (t_up, CB1, CEST_HIT, max(0.0, CEST_HIT - (CB1 - t_up) * sp_c))]
ins("cestino_hfr", CB0, CB1, map=cmap, velocita=round(sp_c, 3))
T_LAV = CB1
a = T_LAV; e = wt("Dentro", a); mapped("ufficio", a, e, 0.0, e - a)
a = e; e = wt("Gioco", a); mapped("brocca", a, e, 0.0, e - a)
a = e; e = wt("Devi", a); mapped("carte", a, e, 0.0, clipend("carte"))   # tutta la clip
a = e; e = wt("Sleghiamo", a); TOLGO = wt("tolgo", a)
COIN_BAD = {26, 34, 41, 42}                                # fotogrammi deformati (a 24 fps)
COIN = [k for k in range(22, 73) if k not in COIN_BAD]
ins("moneta", a, e, frames=COIN, speed=0.5, ferma=TOLGO)  # metà velocità, fermo su "tolgo"
FLASHES.update({fr(TOLGO) + k: v for k, v in enumerate([1.0, 0.85, 0.6, 0.35, 0.15])})
a = wt("Sleghiamo"); u = wt("umani", a); e = wt("Corsa", a)
mapped("corda", a, e, 2.0 - (u - a), 2.0 + (e - u))        # flash dello strappo su "umani"
a = e; e = wt("Sotto", a); oe = clip_len("orologi") - 0.04; mapped("orologi", a, e, oe - (e - a), oe)   # taglio in testa
a = e; pt = wt("petardo", a); e = wt("Morite", a)
mapped("mappamondo", a, e, 2.79 - (pt - a), 2.79 + (e - pt))    # esplosione su "petardo"
T_MOR = e; T_RIT1 = wt("Senti", T_MOR)
black(T_MOR, T_RIT1)

# v5: niente scritte giganti; su nero i sottotitoli normali
BIG = []

# --- ritornelli: waveform della voce fino alla penna, penna fino alla candela,
# cuore di vetro da "Battico" alla riga dopo
PEN = [snap(line_span(g)[0]) for g in find_line("Prendo la penna")]
CAND = []
for g in find_line("Fino a che non si spegne"):
    a, b = line_span(g); t0, t1 = snap(a), snap(b)
    cuore = WORDS[g[-1]]["inizio"]
    ins("candela", t0, t1, inp=max(0.0, SPEGNE - content(cuore - t0, t0)), ramp=True)
    CAND.append((t0, t1))
SW = [WORDS[g[0]]["inizio"] for g in find_line("Senti la voce")]
for k, a in enumerate(SW):
    if k == 2: a = chorus[1][0]                   # v6: dal beat dello stacco dopo il cervello
    b = PEN[k]; ins("wave", a, b)                 # v5: generata dallo stem vocale
for k, t0 in enumerate(PEN):
    ins("penna", t0, CAND[k][0])
T_STR2 = chorus[0][1]
NEXT = [SW[1], T_STR2, SW[3], CLOSE]
# cuore: picchi di luce della clip sui colpi di cassa (tratti tra 0,75x e 1,25x), spegnimento su "muore"
HEART_PEAKS = [1.08, 2.81]                        # massimi della luce interna (s di clip)
HEART_OFF = 3.98                                  # la luce si spegne
HEART_KICKS = [k for k, s_ in KICKS if s_ >= 0.15]          # colpi di cassa (anche deboli)
HEART = []
HEART_FLAT = (3.40, 3.80)                         # luce bassa e ferma: si può saltarne un pezzo
def heart_map(t0, m, t1):
    """P1 e P2 su due colpi di cassa, spegnimento su "muore", ogni tratto tra 0,75x e 1,25x;
    se dopo P2 il tempo non basta, si salta il minimo indispensabile del tratto piatto"""
    ks = [k for k in HEART_KICKS if t0 + 0.05 < k < m - 0.3]
    P1, P2 = HEART_PEAKS
    best = None
    for i, k1 in enumerate(ks):
        for k2 in ks[i + 1:]:
            s12 = (P2 - P1) / (k2 - k1)
            skip = max(0.0, (HEART_OFF - P2) - 1.25 * (m - k2))
            s2m = (HEART_OFF - P2 - skip) / (m - k2)
            c0 = max(0.0, P1 - (k1 - t0)); s0 = (P1 - c0) / (k1 - t0)
            if skip > HEART_FLAT[1] - HEART_FLAT[0] or not all(0.75 <= v <= 1.25 for v in (s12, s2m, s0)):
                continue
            cost = max(abs(math.log(v)) for v in (s12, s2m, s0)) + skip
            if best is None or cost < best[0]: best = (cost, k1, k2, c0, skip)
    if best is None: return None
    _, k1, k2, c0, skip = best
    ce_ = clipend("cuore")
    mp = [(t0, k1, c0, P1), (k1, k2, P1, P2)]
    if skip > 0:
        f0 = sum(HEART_FLAT) / 2 - skip / 2; f1 = f0 + skip
        tm = k2 + (f0 - P2) * (m - k2) / (HEART_OFF - P2 - skip)
        mp += [(k2, tm, P2, f0), (tm, m, f1, HEART_OFF)]
    else:
        mp += [(k2, m, P2, HEART_OFF)]
    mp += [(m, t1, HEART_OFF, min(ce_, HEART_OFF + t1 - m))]
    return mp, (k1, k2), skip
for k in range(len(CAND)):
    a, b = CAND[k][1], NEXT[k]
    g = [gg for gg in find_line("Fino al momento in cui muore") if a <= WORDS[gg[0]]["inizio"] < b][0]
    m = WORDS[g[-1]]["inizio"]                    # "muore"
    hm = heart_map(a, m, b)
    if hm is None: raise SystemExit(f"cuore: nessuna coppia di colpi compatibile ({a:.2f}-{m:.2f})")
    ins("cuore", a, b, map=hm[0], heart=True, picchi=[round(x, 3) for x in hm[1]], muore=round(m, 3),
        salto=round(hm[2], 3))
    HEART.append((a, b, m))

# --- strofa 2
VERSI = [("maschera", "Odio lo standard", "Voglio le robe"),
         ("strada", "Giro le strade", None)]
for name, first, last in VERSI:                 # come nella v3 (sul beat, fino a 0,8x)
    g0 = find_line(first)[0]; g1 = find_line(last)[0] if last else g0
    a = snap(WORDS[g0[0]]["inizio"]); b = snap(line_span(g1)[1])
    f_ = a + clip_len(name) / 0.8
    if f_ < b: b = float(GRID[GRID <= f_ + 1e-6][-1])
    ins(name, a, b, inp=0.0, ramp=False, slow08=True)
T_MARE = S(L("Dentro la testa")); T_VEDO = S(L("Vedo il chiaro"))
fit("studio", T_STR2, T_MARE, 3.8, clipend("studio"), zoom=1.0)      # cuffie, inquadratura larga
fit("mare", T_MARE, T_VEDO, 0.0, clipend("mare"))        # v5: continua fino a "Vedo il chiaro scuro"
c = L("Vedo il chiaro"); d_ = L("Che diventa")
STROBE = (wt("chiaro", c), d_)                            # "chiaro scuro": lampi sul beat
# lampione da "Vedo il chiaro scuro": luce accesa, si spegne su "più scuro", buio pieno su "buio"
T_LAMP = L("Un giorno tutto"); PIU = wt("più", d_); bu = wt("buio", T_LAMP); e = wt("Non", bu)
ins("lampione", T_VEDO, e, map=[(T_VEDO, PIU, 0.0, 1.50), (PIU, T_LAMP, 1.50, 1.93),
                                (T_LAMP, bu, 1.93, 2.60), (bu, e, 2.60, 2.60 + e - bu)])
T_SPEC = S(L("Sono un artista")); T_TV = S(word_t("Cambierò"))
fit("brocca", e, T_SPEC, 2.2, clipend("brocca"), zoom=2.3, cx=0.5, cy=0.47)   # livello dell'acqua
fit("specchio", T_SPEC, T_TV, 0.0, clipend("specchio"))
a = T_TV; b = snap(line_span(find_line("Io Non voglio mai assomigliare")[0])[1])
mid = snap((a + b) / 2)                          # mai la stessa inquadratura > 4 s
ins("tv", a, mid, inp=0.0, ramp=True)
ins("tv", mid, b, inp=content(mid - a, a), ramp=False, zoom=1.45, cx=0.48, cy=0.47)
T_CERCO = S(L("Cerco i dettagli")); T_DUB = S(L("Ma dubito")); T_IST = S(L("L'istante"))
fit("torcia", T_CERCO, T_DUB, 0.0, clipend("torcia"))
ins("clessidra", T_DUB, T_IST, map=[(T_DUB, T_IST, 0.0, 1.42)])   # solo la prima metà, rallentata
T_COSA = S(L("Cosa è successo")); T_PERSO = S(wt("ho", L("Pensavo a domani")))
fit("foto", T_IST, T_COSA, 0.0, clipend("foto"))         # fino alla foto bruciata (fine clip)
fit("specchio", T_COSA, T_PERSO, 0.8, clipend("specchio"), zoom=1.7, cx=0.30, cy=0.5)
T_ASP = S(L("Aspetto il domani")); T_CAP = S(L("Ma tanto ho capito"))
fit("sabbia", T_PERSO, T_ASP, 0.0, clipend("sabbia"))
te_ = clipend("tramonto")
ins("tramonto", T_ASP, T_CAP, map=[(T_ASP, T_CAP, te_, te_ - (T_CAP - T_ASP))])   # al contrario: alba
# v6: cervello di gesso; il pezzo si stacca (4,08 s di clip) su "tradito"; stacco sul beat al ritornello
TRAD = wt("tradito", T_CAP); CRACK = 4.08; BRAIN_IN = 0.16
ins("cervello", T_CAP, chorus[1][0], map=[(T_CAP, TRAD, BRAIN_IN, CRACK),
                                          (TRAD, chorus[1][0], CRACK, clipend("cervello"))])

# v8: raffica su "Pacato" tolta (nessuna sequenza di clip rapide)

# niente sovrapposizioni: ogni inserto finisce dove inizia il successivo
inserts.sort(key=lambda d: d["t0"])

# ---------------------------------------------------------------- sfondi sfocati in movimento
# v4: nessuno sfondo scurito o sfocato; ogni tratto ha la sua clip (o nero con testo grande)
POOLS = {}
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
    if any(b0 - 0.05 <= a < b1 for b0, b1, _ in BIG): continue         # lì c'è il testo grande
    for b0, b1, _ in BIG:
        if a < b0 < end: end = b0
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
# testo grande della strofa 2: glitch a ogni frase e sui beat
STROBE_F = set()
for g in GRID[(GRID >= STROBE[0] - 0.12) & (GRID < STROBE[1])]:         # lampi sul beat
    for h in (g, g + PERIOD / 2):
        if STROBE[0] - 0.12 <= h < STROBE[1]: STROBE_F |= {fr(h), fr(h) + 1}

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
        if name == "specchi":                      # 1,2x della risoluzione: lo zoom resta nitido
            out = os.path.join(PREP, "specchi.png")
            if not os.path.exists(out):
                subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf",
                    f"{CROP},scale={int(W * 1.2)}:{int(H * 1.2)}:flags=lanczos,{GRADE}", "-frames:v", "1", out])
            continue
        if name == "logo": continue                # usato così com'è (bianco su nero)
        if name == "penna":
            out = os.path.join(PREP, "penna.png")
            subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf",
                                   f"{CROP},{GRADE}", "-frames:v", "1", out])
            im = Image.open(out).convert("RGB").resize((BW, BH), Image.LANCZOS)
            np.save(os.path.join(PREP, "bg_penna.npy"), np.asarray(im)[None])
            continue
        out = os.path.join(PREP, f"{name}.mp4")
        if name in ("corridoio", "cestino") and not os.path.exists(os.path.join(PREP, f"{name}_hfr.mp4")) \
                and os.path.exists(out):
            subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-i", out, "-vf",
                "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1", "-an",
                "-c:v", "libx264", "-crf", "10", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                os.path.join(PREP, f"{name}_hfr.mp4")])
        if os.path.exists(out) and "--force" not in ARGS: continue
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
            pass                                       # v5: niente jitter sui colpi
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
TEMPO_IMG = block_img(["TEMPO"], 120, RED)
BAST_IMG = block_img(["BASTARDO"], 120, RED)
_tbh = TEMPO_IMG["h"] + 16 + BAST_IMG["h"]
Y_TEMPO = H / 2 - _tbh / 2 + TEMPO_IMG["h"] / 2
Y_BAST = H / 2 + _tbh / 2 - BAST_IMG["h"] / 2
TB2 = next_beat(TB)                               # BASTARDO sul beat dopo TEMPO
NMF = block_img(["NON MI FERMO"], 190, (255, 255, 255))
IP = block_img(["IPNOS"], 300, RED, shadow=False)
CS = block_img(["IPNOS CREATIVE STUDIO"], 40, (255, 255, 255), kind="SemiBold", maxw=1000,
               tracking=0.20, alpha=0.85, shadow=False)
# v6: sotto NON MI FERMO il logo IPNOS CREATIVE STUDIO (fuso in screen sul nero), 60% della larghezza
_lg = np.asarray(Image.open(SRC["logo"]).convert("RGB"), np.float32) / 255
_ys, _xs = np.where(_lg.max(2) > 0.15)
_pad = int(0.02 * _lg.shape[1])
_lg = _lg[max(0, _ys.min() - _pad):_ys.max() + _pad, max(0, _xs.min() - _pad):_xs.max() + _pad]
_lw = int(W * 0.60); _lh = int(round(_lg.shape[0] * _lw / _lg.shape[1]))
LOGO = np.asarray(Image.fromarray((_lg * 255).astype(np.uint8)).resize((_lw, _lh), Image.LANCZOS), np.float32) / 255
G_LOGO = 70
_blk = NMF["h"] + G_LOGO + _lh
Y_NMF_V6 = H / 2 - _blk / 2 + NMF["h"] / 2
Y_LOGO = H / 2 - _blk / 2 + NMF["h"] + G_LOGO + _lh / 2
def paste_logo(frame, k):
    s_ = [1.15, 1.10, 1.05, 1.0][k] if 0 <= k < 4 else 1.0   # entra a scatto come le altre scritte
    lg = LOGO if s_ == 1.0 else np.asarray(Image.fromarray((LOGO * 255).astype(np.uint8)).resize(
        (int(_lw * s_), int(_lh * s_)), Image.BICUBIC), np.float32) / 255
    h_, w_ = lg.shape[:2]; x0 = int(round(W / 2 - w_ / 2)); y0 = int(round(Y_LOGO - h_ / 2))
    reg = frame[y0:y0 + h_, x0:x0 + w_]
    frame[y0:y0 + h_, x0:x0 + w_] = 1 - (1 - reg) * (1 - lg)   # screen: il nero del logo sparisce
G1, G2 = 40, 60                                   # IPNOS -> studio: almeno 50 px
blk = NMF["h"] + G1 + IP["h"] + G2 + CS["h"]
top = H / 2 - blk / 2
Y_NMF = top + NMF["h"] / 2
Y_IP = top + NMF["h"] + G1 + IP["h"] / 2
Y_CS = top + NMF["h"] + G1 + IP["h"] + G2 + CS["h"] / 2

# intro v4: IPNOS rosso su nero, stesso font della chiusura. Entra a ~70% della larghezza sul
# primo colpo e si rimpicciolisce di scatto (ease-out); di nuovo sul secondo; sfuma sulla coda
IP_INTRO = block_img(["IPNOS"], 400, (255, 255, 255), maxw=int(W * 0.25))   # v6: bianca, ~25%
IP_Y = 0.68 * H
_ipc = {}
def ipnos_intro(frame, t):
    if not (IP_A <= t < IP_FADE[1]): return
    s = 1.0 - 0.18 * ease((t - IP_A) / 0.15)
    if t >= IP_B: s = 0.82 - 0.17 * ease((t - IP_B) / 0.15)
    op = 1.0 if t < IP_FADE[0] else max(0.0, 1 - (t - IP_FADE[0]) / (IP_FADE[1] - IP_FADE[0]))
    key = round(s, 3)
    if key not in _ipc: _ipc[key] = zoomed(IP_INTRO, key)
    C, A = _ipc[key]
    bx0, by0, bx1, by1 = IP_INTRO["bbox"]
    paste_pm(frame, C, A, W / 2 - (bx0 + bx1) / 2 * key, IP_Y - (by0 + by1) / 2 * key, op)

# testo grande al centro (una frase alla volta)
BIG_IMG = []
for b0, b1, rows in BIG:
    imgs = [block_img([t], 230, col, maxw=960) for t, col in rows]
    gap = 22; tot = sum(im["h"] for im in imgs) + gap * (len(imgs) - 1)
    y = H / 2 - tot / 2; ys = []
    for im in imgs: ys.append(y + im["h"] / 2); y += im["h"] + gap
    BIG_IMG.append((fr(b0), fr(b1), list(zip(imgs, ys))))

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

GW, GH = int(round(W * 1.08)), int(round(H * 1.08))      # copia ingrandita dell'8%
GMX, GMY = (GW - W) // 2, (GH - H) // 2
def glitch(frame, k, amp0, seed):
    """v5: separazione RGB e fasce spostate prese da una copia ingrandita dell'8%: niente
    traslazione dell'immagine e mai pixel ripetuti o bande ai lati"""
    amp = max(2, int(min(amp0, 13) * (1 - k / 4)))
    rng = np.random.default_rng(seed)
    big = np.asarray(Image.fromarray((np.clip(frame, 0, 1) * 255).astype(np.uint8)).resize(
        (GW, GH), Image.BILINEAR), np.float32) / 255
    out = big[GMY:GMY + H, GMX:GMX + W].copy()
    out[..., 0] = big[GMY:GMY + H, GMX + amp:GMX + amp + W, 0]
    out[..., 2] = big[GMY:GMY + H, GMX - amp:GMX - amp + W, 2]
    for _ in range(3):
        y0 = int(rng.integers(0, H - 40)); hh = int(rng.integers(8, 40))
        sh = int(rng.integers(-3 * amp, 3 * amp + 1))
        out[y0:y0 + hh] = big[GMY + y0:GMY + y0 + hh, GMX + sh:GMX + sh + W]
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
                kk = min(k, fr(d["ferma"]) - fr(d["t0"])) if "ferma" in d else k   # fermo immagine
                j = int(math.floor(kk * sf * d["speed"] / FPS + 1e-6))
                idx.append(d["frames"][j] if j < len(d["frames"]) else None)
                continue
            c = None
            for (a, b, c0, c1) in d["map"]:
                if a - 1e-6 <= t < b + 1e-6:
                    c = c0 + (t - a) * (c1 - c0) / max(1e-6, b - a); break
            if c is None:                      # fr(t0)/FPS può cadere pochi ms prima di t0
                c = d["map"][0][2] if t < d["map"][0][0] else d["map"][-1][3]
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
        self.red = d.get("grade") == "red"
        live = [j for j in idx[skip:] if j is not None]
        self.cache = None
        if any(b < a for a, b in zip(live, live[1:])):     # clip al contrario: fotogrammi in memoria
            need, self.cache = set(live), {}
            while self.pos < max(need):
                buf = self.p.stdout.read(W * H * 3)
                if len(buf) < W * H * 3: break
                self.pos += 1
                if self.pos in need: self.cache[self.pos] = buf
    def _seek(self, j):
        if self.cache is not None:
            self.cur = self.cache.get(j, self.cache.get(min(self.cache, key=lambda x: abs(x - j)))); return
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
        pi = self.d.get("punchin")                 # punch-in: 1,0 -> scala in n fotogrammi, poi tiene
        if pi:
            j = fr(self.d["t0"]) + k - fr(pi[0])
            if j >= 0: a = punch(a, 1 + (pi[1] - 1) * min(1.0, (j + 1) / pi[2]))
        if self.d.get("heart"): a = heart_frame(a, fr(self.d["t0"]) + k)
        return to_red(a) if self.red else a
    def close(self): self.p.kill(); self.p.wait()

# cuore: clip al 55% su nero pieno (bordi sfumati), centro del cuore a metà larghezza e al 40%
# dell'altezza; su ogni colpo di cassa scatto di scala 1.00 -> 1.04 -> 1.00 in 6 fotogrammi
HEART_C = (0.495, 0.48)                           # centro del cuore nella clip
HEART_BUMP = [0.5, 1.0, 0.75, 0.5, 0.25, 0.0]
HEART_BLACK = np.array([0.0, 0.0, 8 / 255], np.float32)    # fondo della clip graduata: (0, 0, 7)
_HK = np.array(HEART_KICKS)
_hmask = {}
def heart_frame(a, f):
    dk = last_event(_HK, f / FPS)
    j = int(round(dk * FPS)) if dk is not None else 99
    sc = 0.55 * (1 + 0.04 * (HEART_BUMP[j] if j < len(HEART_BUMP) else 0.0))
    w, h = int(round(W * sc)), int(round(H * sc))
    im = np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS),
                    np.float32) / 255
    if (w, h) not in _hmask:
        fx = np.clip(np.minimum(np.arange(w), w - 1 - np.arange(w)) / (0.14 * w), 0, 1)
        fy = np.clip(np.minimum(np.arange(h), h - 1 - np.arange(h)) / (0.10 * h), 0, 1)
        _hmask[(w, h)] = ((fy[:, None] * fx[None, :]) ** 1.5)[..., None].astype(np.float32)
    im = np.clip(im - HEART_BLACK, 0, 1) / (1 - HEART_BLACK)   # nero della clip -> nero pieno
    im = im * _hmask[(w, h)]
    out = np.zeros((H, W, 3), np.float32)
    x0 = int(round(W / 2 - HEART_C[0] * w)); y0 = int(round(0.40 * H - HEART_C[1] * h))
    sx0, sy0 = max(0, -x0), max(0, -y0)
    dx0, dy0 = max(0, x0), max(0, y0)
    dx1, dy1 = min(W, x0 + w), min(H, y0 + h)
    out[dy0:dy1, dx0:dx1] = im[sy0:sy0 + dy1 - dy0, sx0:sx0 + dx1 - dx0]
    return out

# waveform dello stem vocale (WORK/vocals.wav, stesso tratto dell'audio): scorre da destra a
# sinistra sotto la puntina verde fissa; sotto la puntina c'è sempre il suono di quell'istante
WAVE_PPS = 360                                    # px al secondo (12 px a fotogramma)
WAVE_XN, WAVE_Y, WAVE_AMP = W // 2, int(H * 0.47), 170
WAVE_EDGE = np.clip(np.minimum(np.arange(W), W - 1 - np.arange(W)) / 60.0, 0, 1) ** 1.5
_VOC = []
def vocal_peaks():
    if not _VOC:
        sr = WAVE_PPS * 60
        raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", os.path.join(WORK, "vocals.wav"),
                                       "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"])
        x = np.abs(np.frombuffer(raw, np.float32))
        pk = x[:len(x) // 60 * 60].reshape(-1, 60).max(1)
        _VOC.append(pk / max(1e-6, np.percentile(pk, 99.5)))
    return _VOC[0]
class WaveReader:
    def __init__(self, d, skip):
        self.f = fr(d["t0"]) + skip; self.pk = vocal_peaks()
        self.yy = np.abs(np.arange(H) - WAVE_Y)[:, None]
    def read(self):
        t = self.f / FPS; self.f += 1
        b = int(round(t * WAVE_PPS)) - WAVE_XN + np.arange(W)
        v = np.where((b >= 0) & (b < len(self.pk)), self.pk[np.clip(b, 0, len(self.pk) - 1)], 0.0)
        a = np.minimum(v * WAVE_AMP, WAVE_AMP * 1.15) * WAVE_EDGE   # sfuma verso i bordi
        m = (self.yy <= a[None, :]) | (self.yy < 1)
        out = np.zeros((H, W, 3), np.float32)
        out[m] = (0.88, 0.85, 0.80)
        out[:, WAVE_XN - 2:WAVE_XN + 2] = (0.25, 0.95, 0.30)          # puntina verde fissa
        for r in range(30):
            hw = int((30 - r) * 0.6)
            out[r, WAVE_XN - hw:WAVE_XN + hw + 1] = (0.25, 0.95, 0.30)
        return out
    def close(self): pass

class MontageReader:
    """raffica: seq = [(fotogramma d'inizio, n fotogrammi, clip, s di clip, zoom, cx, cy)]"""
    def __init__(self, d, skip):
        self.seq = d["seq"]; self.k = skip; self.buf = {}
    def _load(self, i):
        k0, n, name, c, z, cx, cy = self.seq[i]
        if name == "specchi":
            im = Image.open(os.path.join(PREP, "specchi.png")).convert("RGB")
            iw, ih = im.size; w2, h2 = iw / 1.2 / z, ih / 1.2 / z
            a = np.asarray(im.resize((W, H), Image.LANCZOS, box=((iw - w2) / 2, (ih - h2) / 2,
                                                                (iw + w2) / 2, (ih + h2) / 2)))
            self.buf = {i: np.repeat(a[None], n, 0)}; return
        vf = "null"
        if z > 1.001:
            vf = (f"crop=iw/{z}:ih/{z}:'min(max(iw*{cx}-iw/{2*z},0),iw-iw/{z})':"
                  f"'min(max(ih*{cy}-ih/{2*z},0),ih-ih/{z})',scale={W}:{H}:flags=lanczos")
        raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", f"{c:.3f}", "-i",
              os.path.join(PREP, f"{name}.mp4"), "-vf", f"{vf},fps={FPS}", "-frames:v", str(n),
              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
        fr_ = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
        self.buf = {i: fr_}
    def read(self):
        k = self.k; self.k += 1
        i = max(j for j, s_ in enumerate(self.seq) if s_[0] <= k)
        if i not in self.buf: self._load(i)
        arr = self.buf[i]; j = min(len(arr) - 1, k - self.seq[i][0])
        return arr[j].astype(np.float32) / 255
    def close(self): pass

class MirrorReader:
    """corridoio degli specchi: carrello in avanti, zoom 1,00 -> 1,20 sul centro (punto di fuga)
    con ease-in-out; su "quello" luminosità +10% per 4 fotogrammi"""
    def __init__(self, d, skip):
        self.n = fr(d["t1"]) - fr(d["t0"]); self.k = skip; self.f0 = fr(d["t0"])
        self.pf = fr(d["pulse_at"])
        self.im = Image.open(os.path.join(PREP, "specchi.png")).convert("RGB")   # 1,2x di W x H
    def read(self):
        u = self.k / max(1, self.n - 1); e = u * u * (3 - 2 * u)
        s_ = 1.0 + 0.20 * e
        iw, ih = self.im.size; w2, h2 = iw / 1.2 / s_, ih / 1.2 / s_
        box = ((iw - w2) / 2, (ih - h2) / 2, (iw + w2) / 2, (ih + h2) / 2)
        a = np.asarray(self.im.resize((W, H), Image.LANCZOS, box=box), np.float32) / 255
        if 0 <= self.f0 + self.k - self.pf < 4: a = np.clip(a * 1.10, 0, 1)
        self.k += 1
        return a
    def close(self): pass

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
                    R = {"aggancio": HookReader, "penna": PenReader, "specchi": MirrorReader}.get(d["name"], ClipReader)
                    if d["name"] == "nero": R = BlackReader
                    elif d["name"] == "raffica": R = MontageReader
                    elif d["name"] == "wave": R = WaveReader
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
    # v5: immagine ferma (niente scossa / camera a mano); solo zoom centrati in avanti
    p = pulse(t)
    if any(fr(h0) <= f < fr(h1) for h0, h1, _ in HEART): p = 0.0       # cuore su nero pieno
    if p > 0.002:
        frame = frame * (1 - VIG * p) + RED_F * (VIG * p)
        lk = leak(t, (0.10 if sec[3] == 2 else 0.16) + 0.6 * (p - 0.04))
        frame = 1 - (1 - frame) * (1 - lk)
    if f >= fr(HOOK): draw_phrases(frame, f)
    ipnos_intro(frame, t)
    if f in STROBE_F: frame = 1.0 - frame                  # strobo bianco/nero, 2 fotogrammi
    if fr(TB) <= f < fr(TB_END): paste_block(frame, TEMPO_IMG, Y_TEMPO, f - fr(TB))
    if fr(TB2) <= f < fr(TB_END): paste_block(frame, BAST_IMG, Y_BAST, f - fr(TB2))
    if f >= fr(HIT1): paste_block(frame, NMF, Y_NMF_V6, f - fr(HIT1))
    if f >= fr(HIT2): paste_logo(frame, f - fr(HIT2))           # v6: logo dove entrava IPNOS
    for g0, amp in GL_FRAMES:
        if g0 <= f < g0 + (4 if amp > 10 else 2): frame = glitch(frame, f - g0, amp, f)
    # zoom punch sulle casse (+4% e ritorno in 4 frame); sobrio nella strofa 1
    if sec[3] >= 1 and sec[0] not in ("tempo_bastardo",):
        arr = KICK_STRONG if sec[3] == 1 else KICK_T
        dk = last_event(arr, t)
        if dk is not None and dk < 4 / FPS:
            amp = {1: 0.025, 2: 0.04, 3: 0.04, 4: 0.05}[sec[3]]
            frame = punch(frame, 1 + amp * [1, 0.75, 0.5, 0.25][min(3, int(dk * FPS))])
    if f in FLASHES:                                   # flash bianco (moneta su "tolgo")
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
