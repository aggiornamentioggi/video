import librosa, numpy as np, json
y, sr = librosa.load("audio_cut.wav", sr=22050, mono=True)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time", tightness=200)
# cassa: energia passa-basso
yl = librosa.effects.preemphasis(y, coef=-0.97)  # enfasi sui bassi
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=256))
freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
low = S[(freqs > 30) & (freqs < 150)].sum(0)
env = np.maximum(0, np.diff(low, prepend=low[0]))
env /= env.max()
times = librosa.frames_to_time(np.arange(len(env)), sr=sr, hop_length=256)
kicks = librosa.onset.onset_detect(onset_envelope=env, sr=sr, hop_length=256, units="time", backtrack=False, delta=0.08, wait=8)
on = librosa.onset.onset_strength(y=y, sr=sr, hop_length=256)
on /= on.max()
json.dump({"tempo": float(np.atleast_1d(tempo)[0]), "beats": [round(float(b),3) for b in beats],
           "kicks": [round(float(k),3) for k in kicks],
           "env_kick": [round(float(v),3) for v in env], "onset": [round(float(v),3) for v in on],
           "hop": 256/sr}, open("beats.json","w"))
print("tempo", tempo, "beats", len(beats), "kicks", len(kicks))
print("beats 0-12:", [round(b,2) for b in beats if b<12])
print("beats 165-180:", [round(b,2) for b in beats if b>165])
rms = librosa.feature.rms(y=y, hop_length=256)[0]
for t0 in np.arange(168, 180, 0.25):
    i=int(t0*sr/256); print(f"{t0:6.2f} rms={rms[i:i+21].max():.3f} on={on[i:i+21].max():.2f} kick={env[i:i+21].max():.2f}")
