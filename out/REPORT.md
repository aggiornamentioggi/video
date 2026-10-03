# Report: "Non Mi Fermo" (Ipnos)

## Risultato

| | |
|---|---|
| File | `out/non_mi_fermo_1080x1920.mp4` |
| Durata finale | **2:59,70** (179,70 s, 5391 frame) |
| Peso | **27,1 MB** (27 141 231 byte), sotto il limite di 95 MB: nessun rifacimento a CRF più alto |
| Video | 1080x1920, 30 fps, H.264 yuv420p, CRF 20, preset slow, `+faststart` |
| Audio | AAC 192 kbps, traccia tagliata dei primi 4,5 s, fade in 0,3 s, fade out 0,5 s finale |
| Parole agganciate | **484 / 497 = 97,4 %** (obiettivo > 90 %) |

## Sincronizzazione (`out/sync.json`)

- sherpa-onnx `sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8`, `nemo_transducer`, audio mono 16 kHz.
- Finestre da 30 s con passo 25 s; tenute solo le parole nella zona centrale (2,5 s di margine per lato).
- Allineamento globale (Needleman-Wunsch con somiglianza fuzzy) al testo ufficiale, che vince sempre sulla trascrizione. Le 13 parole non agganciate sono interpolate tra le vicine.
- Campi per parola: `parola`, `inizio`, `fine`, `riga` (numero di riga in `testo/testo.txt`), `testo_riga`, `sezione`, `ripetizione`, `agganciata`.
- Tempi relativi alla traccia già tagliata di 4,5 s.

## Scaletta realizzata

| Momento | Tempo | A schermo |
|---|---|---|
| Intro | 0,00–5,71 | `01_corridoio` (fine tagliata) |
| Intro | 5,71–9,92 | `02_studio`, attacco a 0,11 s nella clip: le cuffie arrivano in testa (3,25 s di clip) esattamente sull'attacco di "Torno" (8,85 s) |
| Strofa 1 | 9,92– | nero, testo parola per parola |
| Tempo bastardo | 56,80 | flash bianco di 2 frame, poi "TEMPO / BASTARDO" in rosso a scatto sul beat |
| Ritornello 1 (×2) | 63,13–90,12 | nero con pulsazione rossa sui colpi di cassa; `penna` 66,06–69,47 e 79,62–82,97; `candela` 71,56–73,31 e 85,12–86,84 |
| Strofa 2 | | `tv` 110,43–116,80 ("Cambierò canale" → "assomigliare"); `strada` 120,19–122,21 ("Giro le strade vago nei posti") |
| Ritornello 2 (×2) | 143,85–172,38 | come sopra; `penna` 147,22–150,61 e 160,75–164,54; `candela` 152,72–154,44 e 166,26–167,97 |
| Coda | 174,01 / 174,65 / 175,13 | "NON MI FERMO" (bianco) e "IPNOS" (rosso #E10600) a scatto sui due colpi finali dopo la pausa; "IPNOS CREATIVE STUDIO" (bianco 70 %, spaziato) in dissolvenza di 0,5 s dal beat successivo. Restano tutte e tre fino alla fine; fade a nero negli ultimi 0,5 s |

Tutti i cambi di clip sono secchi e agganciati al beat (griglia a ~143,5 BPM). Testo con font Anton, tutto maiuscolo, micro zoom 1.15 → 1.00 in 4 frame, centrato al 50 % dell'altezza. La chiusura sta nella fascia 20–80 % (verificato da un assert nel renderer). Le clip non 9:16 sono ritagliate al centro e scalate a 1080x1920, senza deformazioni né bande.

## Ripieghi e scelte annotate

1. **Moneta mancante**: `clip/moneta.mp4` non c'è. Come da ripiego del brief, la parte "Devi rischiare per prendere tutto / Fato farabutto… / Sleghiamo legami" è su nero con testo, come il resto della strofa.
2. **Nomi dei file**: le clip sono state riconosciute per prefisso del nome (corrispondenza indicata dall'utente); i file non sono stati rinominati.
3. **Ritornelli cantati due volte**: nell'audio ogni ritornello è ripetuto due volte di fila, mentre `testo.txt` lo riporta una volta sola. Per l'allineamento e la grafica il blocco del ritornello è stato duplicato (stesso testo ufficiale, `ripetizione` 1 e 2 in `sync.json`). Penna e candela compaiono quindi in tutti e quattro i passaggi.
4. **"Ipnos Ehi"** (riga 1) non viene riconosciuto nell'audio tagliato. I tempi sono interpolati prima di "Torno"; cade comunque nell'intro, dove per brief non c'è testo.
5. **Candela**: la clip è più lunga dello spazio. Invece di partire dall'inizio e tagliare la fine, l'attacco è spostato (circa 2,0 s) in modo che il soffio che spegne la fiamma cada su "cuore" ("si spegne il cuore"). La parte dopo è comunque tagliata.
6. **Studio**: la clip resta a schermo fino al beat di "Forse" (9,92 s) perché si veda il gesto delle cuffie completato; "TORNO SUL PEZZO" compare sopra la clip con ombra.
7. **Pulsazione dei ritornelli**: la cassa è sparsa (trap), quindi la vignettatura ha un fondo rosso del 6 % e picchi fino al 35 % sui colpi di cassa, con discesa esponenziale di ~0,3 s.
8. **Clip più corte dello spazio**: nessuna (rallentamento al 70 % e loop implementati nel renderer ma non necessari).
9. **Coda**: "colpi finali" interpretati come i due colpi che rientrano dopo la pausa (174,01 e 174,65 s); in questo modo il blocco finale resta leggibile per circa 5 s.

## Riprodurre

```
# setup: sherpa-onnx, librosa, pillow; modello parakeet e Anton-Regular.ttf in WORK
python3 tools/asr.py   MODEL WORK/audio16k.wav WORK/asr_words.json
python3 tools/align.py WORK/asr_words.json testo/testo.txt out/sync.json 179.725
python3 tools/render.py WORK            # --plan per la scaletta, --preview t1,t2 per i fotogrammi
```
