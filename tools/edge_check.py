"""Controllo dei bordi: per ogni fotogramma confronta le 4 colonne di pixel a sinistra e a
destra con il contenuto vicino (colonne 4-11). Una banda (chiara o nera), un bordo o pixel
ripetuti da una traslazione fanno differire le colonne di bordo dalle vicine molto più di
quanto le vicine differiscano tra loro.

Uso: python3 tools/edge_check.py VIDEO [VIDEO ...]   -> JSON con l'esito per file
"""
import json, subprocess, sys
import numpy as np

H = 1920
STRIP = 12

def strips(path):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-filter_complex",
           f"[0:v]split[a][b];[a]crop={STRIP}:ih:0:0[l];[b]crop={STRIP}:ih:iw-{STRIP}:0,hflip[r];"
           "[l][r]hstack", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = H * STRIP * 2
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n: break
        a = np.frombuffer(buf, np.uint8).reshape(H, 2 * STRIP).astype(np.float32)
        yield a[:, :STRIP], a[:, STRIP:]           # sinistra, destra (destra specchiata: col 0 = bordo)
    p.wait()

def score(s):
    """diff = bordo (col 0-3) contro vicine (4-7); ref = vicine (4-7) contro più interne (8-11)"""
    e, n1, n2 = s[:, 0:4].mean(1), s[:, 4:8].mean(1), s[:, 8:12].mean(1)
    return float(np.abs(e - n1).mean()), float(np.abs(n1 - n2).mean())

def check(path):
    bad = []; n = 0
    for f, (l, r) in enumerate(strips(path)):
        n += 1
        for side, s in (("sx", l), ("dx", r)):
            d, ref = score(s)
            if d > 2.5 * ref + 3.0: bad.append((f, side, round(d, 1), round(ref, 1)))
    frames = sorted({b[0] for b in bad})
    ranges = []
    for g in frames:
        if ranges and g == ranges[-1][1] + 1: ranges[-1][1] = g
        else: ranges.append([g, g])
    return dict(fotogrammi=n, fuori_soglia=len(frames),
                tratti=[(round(a / 30, 2), round(b / 30, 2)) for a, b in ranges][:50],
                esempi=bad[:10])

if __name__ == "__main__":
    res = {p.split("/")[-1]: check(p) for p in sys.argv[1:]}
    print(json.dumps(res, indent=1))
