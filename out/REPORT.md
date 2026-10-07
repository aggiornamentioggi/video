# REPORT v3: "Non Mi Fermo" (Ipnos)

Render con `tools/build.py` (timeline v3 di `tools/render.py`, tempi invariati). Audio: traccia tagliata di 4,5 s con fade in di 0,3 s.

## File

| File | Durata | Peso | CRF | Note |
|---|---|---|---|---|
| `non_mi_fermo_v3_1080x1920.mp4` | 179.70 s | 72.4 MB | 22 | CRF 20 → 101.9 MB (oltre 95 MB), riesportato a CRF 22 |
| `taglio_ritornello.mp4` | 29.00 s | 13.0 MB | 20 | CRF 20 al primo tentativo; segmento 63.13–90.12 s del video completo |
| `taglio_strofa.mp4` | 33.73 s | 22.7 MB | 20 | CRF 20 al primo tentativo; segmento 99.03–130.75 s del video completo |
| `taglio_finale.mp4` | 35.87 s | 17.1 MB | 20 | CRF 20 al primo tentativo; segmento 143.85–179.70 s del video completo |
| `anteprima_ritornello.mp4` | 20.00 s | 9.0 MB | 20 | 20 s dal primo ritornello (63,13 s) |
| `anteprima_sheet.jpg` | — | 0.14 MB | — | foglio 6x4 di fotogrammi dell'anteprima |

Verifica ffprobe su tutti i video: 1080x1920, 30 fps, H.264 yuv420p, AAC 192 kbps (nominali; ffprobe ne misura ~200), una sola traccia audio (il brano), `+faststart`, tutti sotto i 95 MB.

## Verso → clip

Dal `--plan` (inserti; fuori da questi intervalli ci sono gli sfondi sfocati in movimento). Nessuna sovrapposizione tra inserti.

| Verso | Clip | Inizio (s) | Fine (s) |
|---|---|---|---|
| — | aggancio | 0.00 | 0.50 |
| — | corridoio | 0.50 | 3.30 |
| — | corridoio | 3.30 | 5.72 |
| — | corridoio | 5.72 | 6.94 |
| Ipnos Ehi / Torno sul pezzo | porta | 6.94 | 9.36 |
| Torno sul pezzo / Forse ci resto nemmeno lo so | studio | 9.36 | 9.91 |
| Confesso i peccati con il mio accento | microfono | 13.04 | 15.30 |
| Vorrei non ci fosse un domani / Che tutto finisse oggi / La mente che vede il futuro e perde il presente scava nel niente | tramonto | 15.72 | 19.18 |
| La mente che vede il futuro e perde il presente scava nel niente | pozzo | 21.04 | 22.40 |
| Finire dentro una bara coi resti | scatola | 30.84 | 32.28 |
| Finire dentro una bara coi resti | nero | 32.28 | 32.68 |
| Voglio lasciare una parte di me | vetro | 32.68 | 34.04 |
| Solo soldato le barre ho buttato | mano | 39.24 | 40.84 |
| Pacato, svogliato ma sono tornato | sedia | 40.84 | 42.84 |
| Lavorare per vivere mica / Vivere per lavorare | ufficio | 42.84 | 45.64 |
| Dentro la brocca cade la goccia | brocca | 45.64 | 47.40 |
| Gioco di carte e il vaso scompare | carte | 47.40 | 48.12 |
| Gioco di carte e il vaso scompare | nero | 48.12 | 49.40 |
| Devi rischiare per prendere tutto | moneta | 49.40 | 51.72 |
| Sleghiamo legami stupidi umani | corda | 53.92 | 56.08 |
| Corsa per il tempo bastardo | orologi | 56.08 | 57.52 |
| Sotto sto mondo ci metto un petardo | mappamondo | 57.52 | 59.36 |
| Senti la voce senti il respiro | soundwave | 62.96 | 65.94 |
| Prendo la penna scrivo in corsivo | penna | 66.06 | 69.47 |
| Fino a che non si spegne il cuore / Battico cardiaco conta le ore | candela | 71.56 | 73.31 |
| Senti la voce senti il respiro | soundwave | 76.64 | 79.50 |
| Prendo la penna scrivo in corsivo | penna | 79.62 | 82.97 |
| Fino a che non si spegne il cuore / Battico cardiaco conta le ore | candela | 85.12 | 86.84 |
| Dentro la testa bro ho un mare diverso | mare | 93.07 | 96.46 |
| Un giorno tutto sarà buio | lampione | 101.64 | 103.36 |
| Sono un artista / Senza un po di male la mia arte non ha vista / Quindi chi l'ha vista | specchio | 105.81 | 109.20 |
| Cambierò canale quando cambierò modo di pensare | tv | 110.43 | 113.43 |
| Ma è troppo banale / Io Non voglio mai assomigliare | tv | 113.43 | 116.80 |
| Odio lo standard / Mi prende male / Voglio le robe più strane | maschera | 116.80 | 120.19 |
| Voglio le robe più strane / Giro le strade vago nei posti / Cerco i dettagli nascosti | strada | 120.19 | 122.21 |
| Cerco i dettagli nascosti / Fino a trovare quello che cerco | torcia | 122.21 | 123.90 |
| Adesso per me è già passato / L'istante presente l'ho già scordato / Non lo ricordo davvero non lo ricordo | foto | 128.15 | 130.75 |
| Senti la voce senti il respiro | soundwave | 144.04 | 147.10 |
| Prendo la penna scrivo in corsivo | penna | 147.22 | 150.60 |
| Fino a che non si spegne il cuore / Battico cardiaco conta le ore | candela | 152.72 | 154.44 |
| Battico cardiaco conta le ore | corridoio | 154.44 | 156.11 |
| Senti la voce senti il respiro | soundwave | 157.68 | 160.58 |
| Prendo la penna scrivo in corsivo / Sai che non mi fermo scrivo in eterno | penna | 160.75 | 164.54 |
| Fino a che non si spegne il cuore / Battico cardiaco conta le ore | candela | 166.25 | 167.97 |
| Battico cardiaco conta le ore | corridoio | 167.97 | 169.65 |

Sezioni: aggancio 0–0.5, intro 0.5–9.91, strofa1 9.91–56.8, tempo_bastardo 56.8–57.52, strofa1 57.52–63.13, ritornello1 63.13–90.12, strofa2 90.12–143.85, ritornello2 143.85–172.38, chiusura 172.38–179.7.

## Scelte

- **Vetro**: opzione B, 1,9x fino all'impronta ("parte"), poi velocità normale; nessun taglio in testa.
- **Moneta**: tolti i fotogrammi 26, 34, 41, 42 (deformati), a metà velocità, 0,07 s di nero finale.
- **Orologi**: tagliati in testa, così la fine della clip cade su "Sotto" e TEMPO BASTARDO compare in rosso sugli orologi. Scritta TEMPO BASTARDO a 120 px (commit 50f46ba), integrata prima del render finale.
- **Grana nei ritornelli** dimezzata: 0,25% (0,5% nel resto del video).
- **muro.mp4**: non usato, tenuto come riserva.

## Correzione durante il render

Il primo render mostrava 14 inserti su 22 fermi sull'ultimo fotogramma della clip (porta, microfono, pozzo, scatola, vetro, mano, sedia, ufficio, brocca, orologi, lampione e tre soundwave). Causa: in `MapReader` il primo fotogramma d'uscita (`fr(t0)/30`) può cadere pochi millisecondi prima di `t0`. Nessun tratto della mappa lo copriva, quindi veniva preso l'ultimo fotogramma della clip, e il lettore, che va solo avanti, restava bloccato lì. Nelle anteprime a fotogramma singolo non si vedeva. Correzione: un fotogramma prima del primo tratto usa l'inizio del tratto. Il `--plan` è identico al byte prima e dopo (tempi invariati). Dopo il nuovo render tutti gli inserti si muovono e i fotogrammi di controllo (8.0, 9.25, 9.45, 21.5, 32.4, 33.5, 40.45, 48.08, 48.16, 50.5, 55.47, 57.3, 58.8, 63.5, 66.5, 72.5, 102.62, 121.0, 175.5) corrispondono.
