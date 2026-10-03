"""Trascrizione a finestre con sherpa-onnx (parakeet-tdt-0.6b-v3-int8).
Finestre 30 s, passo 25 s, si tengono solo le parole nella zona centrale
(2,5 s di margine per lato). Output: lista di parole con tempo d'inizio."""
import json, sys
import numpy as np, soundfile as sf, sherpa_onnx

MODEL, WAV, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
WIN, HOP, MARGIN = 30.0, 25.0, 2.5

rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=f"{MODEL}/encoder.int8.onnx", decoder=f"{MODEL}/decoder.int8.onnx",
    joiner=f"{MODEL}/joiner.int8.onnx", tokens=f"{MODEL}/tokens.txt",
    model_type="nemo_transducer", num_threads=4)

audio, sr = sf.read(WAV, dtype="float32")
assert sr == 16000 and audio.ndim == 1
total = len(audio) / sr
words = []
start = 0.0
while True:
    end = min(start + WIN, total)
    s = rec.create_stream()
    s.accept_waveform(sr, audio[int(start * sr):int(end * sr)])
    rec.decode_stream(s)
    r = s.result
    # zona utile: margine interno tranne al primo/ultimo bordo della traccia
    lo = start + (MARGIN if start > 0 else 0)
    hi = end - (MARGIN if end < total else 0)
    # la finestra successiva parte da start+HOP: la sua zona inizia a start+HOP+MARGIN
    # = start+27.5 = hi -> nessuna sovrapposizione né buco
    cur = None
    for tok, ts in zip(r.tokens, r.timestamps):
        t = start + ts
        if tok.startswith("▁") or tok.startswith(" ") or cur is None:
            if cur: words.append(cur)
            cur = {"w": tok.lstrip("▁ "), "t": t}
        else:
            cur["w"] += tok
    if cur: words.append(cur)
    words = [w for w in words if not (w["t"] >= start and (w["t"] < lo or w["t"] >= hi)) or w.get("keep")]
    for w in words: w["keep"] = True
    print(f"[{start:6.1f}-{end:6.1f}] {r.text}", file=sys.stderr)
    if end >= total: break
    start += HOP
words = [w for w in words if w["w"]]
for w in words: w.pop("keep", None)
words.sort(key=lambda w: w["t"])
json.dump(words, open(OUT, "w"), ensure_ascii=False, indent=0)
print(len(words), "parole", file=sys.stderr)
