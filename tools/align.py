"""Allinea le parole riconosciute al testo ufficiale (il testo ufficiale vince).
Allineamento globale (Needleman-Wunsch) con somiglianza fuzzy tra parole;
le parole non agganciate vengono interpolate tra le vicine agganciate."""
import json, re, sys, unicodedata
from difflib import SequenceMatcher

ASR, TXT, OUT, AUDIO_DUR = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9']", "", s).replace("'", "")

# --- testo ufficiale: righe, blocchi separati da righe vuote
raw = open(TXT, encoding="utf-8").read().splitlines()
lines = [(i + 1, l.strip()) for i, l in enumerate(raw) if l.strip()]
# Nell'audio ogni ritornello viene cantato due volte di fila: il blocco del
# ritornello (righe "Senti la voce" ... "in cui muore") è ripetuto.
seq_lines = []
i = 0
while i < len(lines):
    n, l = lines[i]
    if l.lower().startswith("senti la voce"):
        block = lines[i:i + 6]
        seq_lines += [(n2, l2, "rit", 1) for n2, l2 in block]
        seq_lines += [(n2, l2, "rit", 2) for n2, l2 in block]
        i += 6
    else:
        seq_lines.append((n, l, "str", 1)); i += 1

ref = []  # parole ufficiali
for li, (n, l, kind, rep) in enumerate(seq_lines):
    for w in l.split():
        ref.append({"parola": w, "riga": n, "testo_riga": l, "idx_riga": li,
                    "sezione": kind, "ripetizione": rep})

hyp = json.load(open(ASR))
R = [norm(r["parola"]) for r in ref]
H = [norm(h["w"]) for h in hyp]

def sim(a, b):
    if not a or not b: return 0.0
    if a == b: return 1.0
    return SequenceMatcher(None, a, b).ratio()

n, m = len(R), len(H)
GAP = -0.4
S = [[0.0] * (m + 1) for _ in range(n + 1)]
P = [[0] * (m + 1) for _ in range(n + 1)]
for i in range(1, n + 1): S[i][0] = i * GAP; P[i][0] = 1
for j in range(1, m + 1): S[0][j] = j * GAP; P[0][j] = 2
for i in range(1, n + 1):
    for j in range(1, m + 1):
        s = sim(R[i-1], H[j-1])
        d = S[i-1][j-1] + (s * 2 - 1 if s >= 0.6 else -1.0)
        u = S[i-1][j] + GAP
        l = S[i][j-1] + GAP
        S[i][j], P[i][j] = max((d, 0), (u, 1), (l, 2))
i, j = n, m
match = {}
while i > 0 or j > 0:
    p = P[i][j]
    if i > 0 and j > 0 and p == 0:
        if sim(R[i-1], H[j-1]) >= 0.6: match[i-1] = hyp[j-1]["t"]
        i, j = i - 1, j - 1
    elif i > 0 and (j == 0 or p == 1): i -= 1
    else: j -= 1

# --- tempi: agganciati diretti, gli altri interpolati
starts = [match.get(k) for k in range(n)]
anch = [k for k in range(n) if starts[k] is not None]
for k in range(n):
    if starts[k] is not None: continue
    prev = max([a for a in anch if a < k], default=None)
    nxt = min([a for a in anch if a > k], default=None)
    if prev is not None and nxt is not None:
        starts[k] = starts[prev] + (starts[nxt] - starts[prev]) * (k - prev) / (nxt - prev)
    elif nxt is not None:      # prima del primo aggancio
        starts[k] = max(0.0, starts[nxt] - 0.35 * (nxt - k))
    else:
        starts[k] = starts[prev] + 0.35 * (k - prev)
out = []
for k, r in enumerate(ref):
    nxt = starts[k + 1] if k + 1 < n else AUDIO_DUR
    end = min(nxt, starts[k] + 0.9)
    out.append({**r, "inizio": round(starts[k], 3), "fine": round(max(end, starts[k] + 0.08), 3),
                "agganciata": k in match})
pct = 100 * len(match) / n
json.dump({"audio": "traccia tagliata di 4,5 s (tempi relativi al nuovo inizio)",
           "modello": "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8",
           "parole_totali": n, "parole_agganciate": len(match),
           "percentuale_agganciate": round(pct, 1), "parole": out},
          open(OUT, "w"), ensure_ascii=False, indent=1)
print(f"{len(match)}/{n} agganciate = {pct:.1f}%")
for r in out:
    if not r["agganciata"]: print("  interp:", r["parola"], r["inizio"], "| riga", r["riga"])
