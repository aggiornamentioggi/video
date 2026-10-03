# BRIEF: video "Non Mi Fermo" (Ipnos)

Lavora in autonomia fino al video finito. Non fermarti a chiedere conferme: dove qualcosa manca, applica la regola di ripiego indicata qui sotto e annotala nel report finale.

## Obiettivo

Video musicale verticale per TikTok, Reels e Shorts. Stile scuro e cinematografico: sfondo nero, testo parola per parola sincronizzato sul rap, rosso che pulsa sui ritornelli. L'artista non si vede mai in faccia.

## File nel repo

```
audio/traccia.mp3      traccia completa (3:04,3)
testo/testo.txt        testo ufficiale, una riga = una riga a schermo
clip/01_corridoio.mp4  intro 1: passi nel corridoio (1080x1916, 6 s)
clip/02_studio.mp4     intro 2: studio, cuffie in mano (1176x1764, 6 s)
clip/tv.mp4            TV CRT con statico (1080x1916, 7 s)
clip/strada.mp4        ragazzo incappucciato per strada (1176x1764, 7 s)
clip/candela.mp4       candela (1176x1764, 5 s)
clip/penna.png         penna sul foglio, immagine ferma
clip/moneta.mp4        moneta che gira (PUÒ MANCARE)
```

## Specifiche di output

- 1080x1920, 30 fps, H.264 yuv420p, CRF 20, preset slow, AAC 192 kbps, `-movflags +faststart`
- File finale sotto i 95 MB (limite GitHub 100 MB). Se lo supera, alza il CRF di 2 e rifai l'export
- Durata sotto i 3:00
- Tutte le clip non 9:16 vanno ritagliate ai lati (crop centrale) e portate a 1080x1920, mai deformate né con bande nere

## Passo 1: audio

Taglia i primi 4,5 secondi della traccia, così la durata scende a circa 2:59,8. Il finale resta intatto. Applica un fade in di 0,3 s sul nuovo inizio.

## Passo 2: sincronizzazione parola per parola

Usa sherpa-onnx con il modello `sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8`, NON Whisper.

- Download: `curl -L -o m.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2` poi `tar xjf` (salva prima il file, il pipe diretto su tar può fallire in silenzio)
- `OfflineRecognizer.from_transducer(..., model_type="nemo_transducer")`, audio mono 16 kHz
- Finestre da 30 s con passo 25 s; tieni solo i token nella zona centrale di ogni finestra (2,5 s di margine per lato) per evitare errori ai bordi
- Allinea i token riconosciuti al testo ufficiale di `testo/testo.txt` (il testo ufficiale vince sempre sulla trascrizione). Le parole non riconosciute vanno interpolate tra le vicine
- Obiettivo: oltre il 90% delle parole agganciate direttamente
- Salva il risultato in `out/sync.json` (parola, inizio, fine, riga) e FAI COMMIT SUBITO, prima di andare avanti. Se la sessione si interrompe, si riparte da qui

## Passo 3: scaletta

| Momento | A schermo |
|---|---|
| Intro | `01_corridoio` poi `02_studio`. Le cuffie devono salire sulla testa esattamente sull'attacco di "Torno sul pezzo". Nessun testo in questa parte |
| Strofa 1 | Nero con testo parola per parola. Clip `moneta` su "Devi rischiare per prendere tutto / Fato farabutto... / Sleghiamo legami", e deve finire su "legami". Se manca la moneta: nero con testo come il resto della strofa |
| "Corsa per il tempo bastardo" | Nero. "TEMPO BASTARDO" entra in rosso a scatto, con un flash bianco di 2 frame, sul colpo del beat. Niente orologio |
| Ritornelli (tutti) | Nero che pulsa rosso a tempo di battito. `penna.png` su "Prendo la penna scrivo in corsivo" e `candela` su "Fino a che non si spegne il cuore" |
| Strofa 2 | `tv` da "Cambierò canale" fino a "assomigliare". `strada` su "Giro le strade vago nei posti" |
| Coda | Nero. Sui colpi finali entra "NON MI FERMO", poi sotto compare "IPNOS". Ancora più sotto, in piccolo, "IPNOS CREATIVE STUDIO". Tutte e tre restano a schermo fino alla fine (vedi Chiusura) |

## Chiusura

Schermata finale su nero, tre righe centrate e impilate, che restano visibili insieme fino all'ultimo frame:

1. **NON MI FERMO**: grande, bianco, stesso font del video, entra a scatto sul colpo finale
2. **IPNOS**: grande, rosso #E10600, entra a scatto sul colpo successivo
3. **IPNOS CREATIVE STUDIO**: piccolo (circa un quarto dell'altezza di "IPNOS"), bianco al 70%, spaziatura tra lettere larga, entra in dissolvenza di 0,5 s dopo "IPNOS"

Il blocco resta centrato in verticale nella fascia sicura (20%–80% dell'altezza). Fade a nero solo negli ultimi 0,5 s, insieme all'audio.

## Animazione della penna

È un'immagine ferma. Animala con un push in lento (1.00 → 1.08) verso il pennino e un leggero tremolio di luminosità tipo lampada. La mano non deve muoversi.

## Stile del testo

- Font bold condensato (Anton o Bebas Neue, scaricabili dal repo GitHub google/fonts), tutto maiuscolo
- Una parola alla volta, entrata a scatto con un micro zoom (1.15 → 1.00 in 4 frame), centrata
- Parole chiave in rosso #E10600, il resto bianco: cuore, tempo, bastardo, rischiare, mente, buio, scuro, eterno, muore, tradito, non mi fermo
- Sopra le clip, testo con ombra nera morbida per la leggibilità
- Tutto il testo resta nella fascia tra il 20% e l'80% dell'altezza, mai oltre i bordi del 9:16 e mai nel 15% inferiore, dove c'è l'interfaccia dei social
- Pulsazione rossa dei ritornelli: vignettatura rossa che cresce e cala sui colpi di cassa, intensità massima 35%

## Tagli

- Cambi di clip sempre secchi, sul beat. Nessuna dissolvenza
- Clip più corte del loro spazio: rallenta fino al 70% prima di ripetere. Clip più lunghe: taglia la fine

## Consegna

1. `out/non_mi_fermo_1080x1920.mp4`
2. `out/sync.json`
3. `out/REPORT.md`: durata finale, peso del file, percentuale di parole agganciate e qualsiasi ripiego applicato (per esempio la moneta mancante)

Fai commit e push di tutto su un branch `video`.
