# REPORT v8 (intro v7 e cestino in anteprima) / v6 (video completo): "Non Mi Fermo" (Ipnos)

Render completo con `tools/build.py` dalla timeline v6 di `tools/render.py` (esportato dopo "ok export"): è la v5 con main unito (cervello, corridoio di specchi, logo) e solo le modifiche richieste. Il file completo si chiama ancora `non_mi_fermo_v3_1080x1920.mp4` per non rompere i link.

## v8: cestino su "Solo soldato … ma sono tornato" (in anteprima, export completo dopo "ok export")

Modificato solo il blocco "Solo soldato / le barre ho buttato / pacato, svogliato / ma sono tornato". L'intro resta quella multicamera della v7. Il video completo in `out/` è ancora la v6. Anteprima: `out/preview/preview_cestino.mp4` (da "quello che ho fatto", 38,44 s, a fine "lavorare per vivere", 44,52 s; 720p, CRF 28, con l'audio). Controllo dei bordi: 0 fotogrammi fuori soglia su 183.

- Clip "A-single-crumpled-paper-ball-falls-from.mp4". Uso solo la prima caduta: da 0 s al primo contatto della palla con il cestino (0,75 s di clip; la palla entra in campo dall'alto a 0,54 s). Scartati il rimbalzo dei fogli, il rimbalzo alto e la seconda caduta.
- Rallenty fluido: versione della clip interpolata a 60 fps con `minterpolate` (mci, aobmc), così a 0.54x ogni fotogramma è diverso.
- **"Solo soldato / le barre ho buttato"** (39.06–40.44 s): in avanti a 0.54x (sopra 0,5x), con il contatto esattamente su "buttato" (40,44 s). Il tempo bastava, quindi non è servito tenere fermi i primi fotogrammi.
- **"Pacato, svogliato"** (40.44–41.81 s): fermo sul fotogramma del contatto (palla appoggiata sul cestino), primo fotogramma del reverse.
- **"Ma sono tornato"** (41.81–42.86 s): lo stesso tratto al contrario, alla stessa velocità. La palla si stacca e risale, uscendo dall'inquadratura in alto esattamente su "tornato" (42,20 s). Poi resta il cestino senza palla fino allo stacco.
- Stacchi sul beat ai due estremi del blocco: 39,06 s (prima era a "Solo", 39,24 s, quindi il microfono finisce 0,18 s prima) e 42,86 s (l'ufficio parte 0,02 s dopo). Dentro il blocco nessuno stacco.
- Tolta la clip della mano (era su "Solo soldato").
- **Raffica su "Pacato" tolta del tutto.** Nel video non restano sequenze di clip rapide di fila. Restano solo gli stacchi sul beat dell'intro multicamera v7 su "Forse ci resto" (stessa clip, crop diversi), che avevi chiesto tu.
- "Clip del cono" e "teaser a raffica": nella repo non c'è nessuna clip del cono e non è usata nel video; il teaser a raffica era il montaggio su "Pacato", ora tolto.
- Niente flash, tremolio o bande.

## v7: intro multicamera (in anteprima, export completo dopo "ok export")

Modificato solo il tratto dalla fine della porta (5,29 s) a "con il mio accento" (15,72 s). Il video completo in `out/` è ancora la v6. Anteprima: `out/preview/preview_intro.mp4` (0–15,73 s, 720p, CRF 28, con l'audio). Controllo dei bordi: 0 fotogrammi fuori soglia su 472.

La clip dello studio è montata come una ripresa multicamera: stessa clip, tempo continuo senza salti (le cuffie arrivano in testa su "Torno" come prima), solo il crop cambia, con stacco sul beat. Niente tremolio, flash o bande.

| Tempo (s) | Inquadratura | Crop / effetto | Tempo di clip |
|---|---|---|---|
| 5.29–5.71 | studio, larga (come prima) | crop 1.35x | 0.00–0.41 s |
| 5.71–6.55 | studio, stretta sulle cuffie in mano | crop 2.0x | 0.41–1.22 s |
| 6.55–9.91 | studio, media spalle e testa | crop 1.5x, punch-in 1,00 → 1,12 in 3 fotogrammi su "Torno" (8,80 s), poi tiene | 1.22–4.45 s |
| 9.91–10.31 | studio, stretta sul cappuccio da dietro | crop 2.0x | 4.45–4.81 s |
| 10.31–10.70 | studio, media | crop 1.4x | 4.81–5.18 s |
| 10.70–11.15 | studio, stretta sul cappuccio da dietro | crop 2.0x | 5.18–5.58 s |
| 11.15–11.59 | studio, media | crop 1.4x | 5.58–5.99 s |
| 11.59–15.72 | microfono con la griglia | intero, zoom lento 1,00 → 1,15 | 0–4.13 s |

- Dall'ingresso a "Torno": larga per un beat; stretta sulle cuffie in mano per due beat (si vedono in mano solo fino a ~1,2 s di clip, poi le alza); media su spalle e testa mentre le porta alla testa.
- "Torno sul pezzo": la media continua con il punch-in sul colpo.
- "Forse ci resto, nemmeno lo so": a ogni beat si alterna stretta sul cappuccio (2x) e media (1,4x).
- "Dico le cose quelle che sento": stacco sul beat (11,59 s) al microfono con la griglia, che parte da qui (prima partiva su "Confesso") e prosegue su "Confesso i peccati con il mio accento" con zoom lento in avanti fino a "Vorrei".
- Lo studio dopo le cuffie ora va a 0,92x (prima 0,61x), perché finisce prima.
- Nitidezza: i crop a 2x sulla clip dello studio (1176x1764) restano nitidi, quindi non è servito ridurli. Il microfono è a 1080x1920 nativo.
- La raffica su "Pacato" usa le stesse inquadrature di studio e microfono di prima: è identica alla v6.

## v6

Prima dell'export completo ho preparato le anteprime dei tratti modificati in `out/preview/`: 720p, CRF 28, audio AAC 128 kbps, 1 s prima e dopo ogni tratto. Il video completo corrisponde alle anteprime approvate (stesso piano).

| Anteprima | Tratto modificato | Contenuto | Peso |
|---|---|---|---|
| `preview/preview_1_intro.mp4` | 0.00–9.91 s | 0.00–10.91 s | 0.82 MB |
| `preview/preview_2_specchi.mp4` | 22.55–24.66 s | 21.55–25.66 s | 0.61 MB |
| `preview/preview_3_cervello.mp4` | 139.57–143.85 s | 138.57–144.85 s | 0.52 MB |
| `preview/preview_4_finale.mp4` | 172.38–179.70 s | 171.38–179.70 s | 0.29 MB |
| `preview/preview_5_fiches.mp4` | 24.66–29.26 s | 23.66–30.26 s | 0.91 MB |

Controllo dei bordi (`tools/edge_check.py`, ora legge l'altezza reale del video) su tutte e cinque le anteprime: 0 fotogrammi fuori soglia.

**1. Inizio**
- Niente fermo immagine: il corridoio parte da 0 s, in movimento, dal primo fotogramma (crop 1,25x come prima).
- Speed ramp: 1,0x per il primo 30% del tratto, poi rallenta in modo continuo (smoothstep) fino a 0,5x sul taglio alla porta. Usa 0–2.64 s di clip.
- Interpolazione: versione del corridoio a 60 fps fatta con `minterpolate` (mci, aobmc), quindi anche a 0,5x ogni fotogramma è diverso, senza scatti.
- Porta (3,20 s) e cuffie su "Torno" (8,80 s) restano dov'erano.
- IPNOS: bianca #FFFFFF, al ~25% della larghezza sul primo colpo (0,165 s), centrata al 68% dell'altezza, sopra il corridoio in movimento. Si rimpicciolisce di scatto sui due colpi (0,82 e 0,65) e sfuma sulla coda (1,15–1,85 s) come prima.

**2. Corridoio degli specchi**
- Su "Torno fresco ma non torno quello / ma non torno questo e domani resto" (22.55–25.96 s), al posto di muro.mp4, l'immagine del corridoio di specchi, con la stessa color grading.
- Carrello in avanti: zoom centrato sul punto di fuga da 1,00 a 1,20 con ease-in-out per tutto il tratto, senza traslazioni né rotazioni. L'immagine è preparata a 1,2x della risoluzione, così lo zoom resta nitido.
- Su "quello" (23,68 s) luminosità +10% per 4 fotogrammi.
- Stacco sul beat al primo piano della fiche su "Dico solo" (25,96 s).
- Nella raffica su "Pacato" l'inquadratura del muro è diventata quella degli specchi (il muro non si vede più prima).

**3. Cervello che si crepa**
- Su "Ma tanto ho capito / è la mente mia / che m'ha tradito" (139.57–143.85 s), al posto del pozzo.
- Il pezzo di gesso inizia a staccarsi a 4,08 s di clip e cade esattamente su "tradito" (142,84 s): 1,20x prima, 0,90x dopo. Nessuno zoom aggiunto.
- Stacco netto sul beat del ritornello (143,85 s). La waveform del terzo ritornello ora parte da quel beat invece che da "Senti" (144,04 s), così non resta un buco.

**4. Finale con il logo**
- "NON MI FERMO" resta com'era. Al posto di "IPNOS" rosso e "IPNOS CREATIVE STUDIO" c'è il logo, ritagliato sul contenuto, al 60% della larghezza, centrato sotto "NON MI FERMO".
- Fusione in screen sul nero, quindi il riquadro non si vede. Il blocco sta tra il 42% e il 58% circa dell'altezza, dentro la fascia 20–80%.
- Entra a scatto (micro zoom 1,15 → 1,00 in 4 fotogrammi, come le altre scritte) sul colpo dove entrava IPNOS (174,65 s) e resta fino alla fine, con il fade a nero di 0,5 s insieme all'audio.

**5. Fiches su due versi**
- "E domani resto": restano gli specchi (vedi punto 2); la strada qui non c'è più.
- "Dico solo che non voglio il resto" (25,96–27,24 s): primo piano sulla fiche rossa in piedi al centro in primo piano. Primi 1,28 s della clip, prima del crollo (la pila resta ferma fino a 1,58 s), quindi niente fermo immagine. Crop centrato sulla fiche (0,47; 0,57) con zoom lentissimo 1,00 → 1,05.
- "Voglio tutto quello che voglio investo" (da 27,24 s): stacco sul beat alla clip intera, inquadratura completa, dall'inizio, con il crollo sul beat di "investo" come prima.
- Nitidezza: con la fiche a metà larghezza (crop 2,85x) il dettaglio è troppo morbido (sorgente 720 px). Ho allargato il crop a 2,3x: la fiche occupa circa il 42% della larghezza e resta nitida.
- La raffica su "Pacato" non include il primo piano della fiche. Ha perso la strada (non più vista prima di quel punto), quindi le clip scorrono una posizione prima.

**Ripieghi v6**
- **Immagine degli specchi**: "1000322517.png" non c'è su main. L'unica immagine nuova che corrisponde alla descrizione (corridoio buio con specchi ai lati e il ragazzo incappucciato riflesso di spalle) è "Corridoio infinito di specchi e ombre.png": ho usato quella. L'altro file nuovo è il logo ("Logo IPNOS Creative Studio in bianco e nero.png").
- **Specchi e "e domani resto"**: come richiesto, gli specchi arrivano fino a "Dico solo" (25,96 s). Su questo verso quindi non c'è più la strada di Ruoti, che resta solo nella strofa 2 ("Giro le strade"), e nemmeno nella raffica su "Pacato".
- **Cervello**: per far cadere il pezzo su "tradito" usando la clip intera servirebbe 1,25x. Per restare entro 1,2x ho saltato i primi 0,16 s della clip, in cui il cervello è fermo.

## File (video completo v6)

| File | Durata | Peso | CRF | Note |
|---|---|---|---|---|
| `non_mi_fermo_v3_1080x1920.mp4` | 179.70 s | 82.9 MB | 22 | CRF 20 → 114.3 MB (oltre 95 MB), riesportato a CRF 22 |
| `taglio_ritornello.mp4` | 29.00 s | 12.9 MB | 20 | CRF 20 al primo tentativo; segmento 63.13–90.12 s del video completo |
| `taglio_strofa.mp4` | 33.73 s | 25.4 MB | 20 | CRF 20 al primo tentativo; segmento 99.03–130.75 s del video completo |
| `taglio_finale.mp4` | 35.87 s | 16.7 MB | 20 | CRF 20 al primo tentativo; segmento 143.85–179.70 s del video completo |
| `anteprima_ritornello.mp4` | 20.00 s | 9.1 MB | 20 | 20 s dal primo ritornello |
| `anteprima_sheet.jpg` | — | — | — | foglio 6x4 di fotogrammi dell'anteprima |
| `preview/*.mp4` | — | — | 28 | anteprime v6 dei tratti modificati (720p) |
| `check/*.jpg` | — | — | — | fotogrammi di controllo della v5 |

Verifica ffprobe: tutti 1080x1920, 30 fps, H.264 yuv420p, AAC 192 kbps (nominali; ffprobe ne misura ~200), una sola traccia audio (il brano), `+faststart`, sotto i 95 MB.

Controllo dei bordi sul video completo v6 (`tools/edge_check.py`):

| File | Fotogrammi | Fuori soglia |
|---|---|---|
| `non_mi_fermo_v3_1080x1920.mp4` | 5391 | 0 |
| `taglio_ritornello.mp4` | 870 | 0 |
| `taglio_strofa.mp4` | 1012 | 0 |
| `taglio_finale.mp4` | 1076 | 0 |
| `anteprima_ritornello.mp4` | 600 | 0 |

### Storico v5

### Controllo dei bordi (v5) (`tools/edge_check.py`)

Per ogni fotogramma confronta le 4 colonne di pixel a sinistra e a destra con le colonne vicine (4-11). Un fotogramma è fuori soglia se il bordo differisce dalle vicine più di 2,5 volte quanto le vicine differiscono tra loro, +3 livelli. Sulla v4 lo stesso controllo trovava 275 fotogrammi fuori soglia nel solo taglio della strofa (il tremolio).

- **Primo export v5**: 17 fotogrammi fuori soglia, tutti nella waveform: l'onda arrivava al bordo dello schermo con picchi netti (contenuto vero, non bande). Corretto sfumando l'onda negli ultimi 60 px ai lati; ho rifatto i due blocchi con la waveform e riesportato.
- **Export finale**:

| File | Fotogrammi | Fuori soglia |
|---|---|---|
| `non_mi_fermo_v3_1080x1920.mp4` | 5391 | 0 |
| `taglio_ritornello.mp4` | 870 | 0 |
| `taglio_strofa.mp4` | 1012 | 0 |
| `taglio_finale.mp4` | 1076 | 0 |
| `anteprima_ritornello.mp4` | 600 | 0 |

## Modifiche v5

**1. Tremolio e bande ai lati**
- Tolta la scossa continua nelle strofe (`np.roll`, che ripeteva ai lati i pixel del lato opposto) e lo schermo che tremava nel testo grande.
- Tolto anche il jitter dei sottotitoli sui colpi nei ritornelli.
- Restano solo zoom centrati in avanti: zoom sul beat, zoom lenti, avvicinamento sulla penna.
- Glitch rifatto senza traslazione: separazione RGB e fasce spostate prese da una copia del fotogramma ingrandita dell'8% (spostamento massimo 39 px su 43 di margine), quindi mai pixel ripetuti o bande ai lati.

**2. Intro IPNOS**
- Sfondo: primo fotogramma del corridoio (crop 1,25x come nel resto del corridoio), fermo.
- IPNOS rosso #E10600, Anton, al ~35% della larghezza sul primo colpo (0,165 s), centrata al 60% dell'altezza; si rimpicciolisce di scatto sui due colpi (0,82 e 0,65) e sfuma da 1,15 a 1,85 s.
- Il corridoio parte da quel fotogramma sul beat a 1,95 s, senza stacco. Porta e cuffie come prima.

**3. Scritte giganti tolte**
- "Morite contenti / sono il salvatore / fatevi onore": nero con i sottotitoli normali.
- "Non mi fotte… / che sia chiaro giuro": continua il mare (clip intera a 0,84x, da "Dentro la testa" a "Vedo il chiaro scuro").
- "Vedo il chiaro scuro / che diventa sempre un po' più scuro": lampione da qui. Luce accesa (0-1,5 s di clip, a 0,68x), sfarfallio e spegnimento su "più" (101,24 s), penombra su "un giorno tutto", buio pieno su "buio" (102,56 s) come prima.
- Sottotitoli identici al resto (font, dimensione, fascia 70-80%, karaoke).

**4. Waveform nel ritornello**
- Stem vocale estratto da `audio_cut.wav` (lo stesso audio del video) con UVR MDX-NET Kim_Vocal_2 (audio-separator). La correlazione con la traccia dà offset 0 campioni.
- La waveform è generata a ogni fotogramma: 360 px al secondo (12 px a fotogramma), da destra a sinistra, puntina verde fissa al centro. Sotto la puntina c'è sempre il suono dell'istante del fotogramma, per costruzione.
- Verifica con `out/sync.json`: all'inizio di "voce" e di "respiro" la puntina è sopra il suono in tutti e quattro i ritornelli (livello alla puntina 0,22-0,54 contro ~0,01 del silenzio). Nel primo ritornello la voce riparte a 63,52 s, esattamente su "voce" in sync.json. Sfasamento tra waveform e audio: nessuno. Fotogrammi in `check/03_rit*_waveform_su_voce|respiro.jpg`.

**5. Cuore nel ritornello**
- Clip del cuore di vetro al posto del corridoio rosso, da "Battico cardiaco" alla riga dopo, in tutti e quattro i ritornelli.
- Al 55%, su nero pieno: bordi della clip sfumati e il nero della clip (0,0,7 dopo la grading) portato a 0, così il raccordo non si vede. Centrato in orizzontale, centro del cuore al 40% dell'altezza. Durante il cuore niente bagliore rosso del ritornello, per tenere il nero pieno.
- I picchi di luce della clip (1,08 e 2,81 s) cadono su due colpi di cassa; lo spegnimento (3,98 s) cade esattamente su "muore"; dopo resta spento fino allo stacco.
- Su ogni colpo di cassa: scatto di scala 1,00 → 1,04 → 1,00 in 6 fotogrammi, centrato sul cuore.

  - Ritornello 1: 73.31–76.64 s, picchi sui colpi a 73.91 e 75.36 s, "muore" a 76.16 s; velocità dei tratti 1.00x, 1.19x, 1.25x, 1.25x, 1.00x; salto nel tratto piatto 0.17 s.
  - Ritornello 2: 86.84–90.12 s, picchi sui colpi a 87.42 e 88.87 s, "muore" a 89.72 s; velocità dei tratti 1.00x, 1.19x, 1.25x, 1.25x, 1.00x; salto nel tratto piatto 0.11 s.
  - Ritornello 3: 154.44–157.68 s, picchi sui colpi a 155.03 e 156.48 s, "muore" a 157.28 s; velocità dei tratti 1.00x, 1.19x, 1.25x, 1.25x, 1.00x; salto nel tratto piatto 0.17 s.
  - Ritornello 4: 167.97–172.38 s, picchi sui colpi a 168.55 e 170.00 s, "muore" a 170.88 s; velocità dei tratti 1.00x, 1.19x, 1.25x, 1.25x, 0.67x; salto nel tratto piatto 0.08 s.

## Ripieghi v5

- **Cuore, tratto dopo il secondo picco**: tra l'ultimo colpo di cassa utile e "muore" ci sono solo 0,8-0,9 s, mentre la clip ha 1,17 s tra il picco e lo spegnimento: servirebbe 1,3-1,46x. Per restare entro 1,25x ho saltato 0,08-0,17 s nel tratto in cui la luce è bassa e ferma (3,4-3,8 s di clip); il salto non si vede.
- **Cuore, colpi deboli**: in quei punti del brano le casse forti sono poche. Per agganciare il primo picco ho usato anche le casse deboli (forza ≥ 0,15, per esempio 73,91 s), e gli stessi colpi danno gli scatti di scala.
- **Cuore, dopo "muore" nell'ultimo ritornello**: la clip finisce prima dello stacco, quindi la coda spenta va a 0,67x (resta comunque spenta).
- **Lampione**: la parte accesa (1,5 s di clip) copre 2,2 s di versi, quindi 0,68x ("rallentala quanto serve").
- **Strobo su "chiaro scuro"**: lasciato com'era (immagine invertita per 2 fotogrammi sui beat e mezzi beat). Ora inverte il lampione invece del testo gigante.
- **Stem vocale**: il modello Demucs non si poteva scaricare da questo ambiente (host bloccato). Ho usato UVR MDX-NET Kim_Vocal_2, scaricato da GitHub.

## Verso → clip (v6)

Dal `--plan`; nessuna sovrapposizione e nessun buco tra gli inserti.

| Verso | Clip | Inizio (s) | Fine (s) | Velocità / note |
|---|---|---|---|---|
| — | corridoio_hfr | 0.00 | 3.20 | speed ramp 1,0x → 0,5x (interpolato a 60 fps) |
| — | porta | 3.20 | 5.29 | 1.15x |
| Ipnos Ehi / Torno sul pezzo / Forse ci resto nemmeno lo so / Dico le cose quelle che sento | studio | 5.29 | 13.04 | 0.98x, 0.61x, crop 1.35x |
| Confesso i peccati con il mio accento / Vorrei non ci fosse un domani | microfono | 13.04 | 15.72 | 1.00x |
| Vorrei non ci fosse un domani / Che tutto finisse oggi / La mente che vede il futuro e perde il presente scava nel niente | tramonto | 15.72 | 19.18 | 0.80x |
| La mente che vede il futuro e perde il presente scava nel niente / Torno fresco ma non torno quello | pozzo | 19.18 | 22.55 | 0.89x |
| Torno fresco ma non torno quello / Ma non torno questo e domani resto | specchi | 22.55 | 25.96 | carrello 1,00 → 1,20, ease-in-out |
| Dico solo che non voglio il resto | fiches | 25.96 | 27.24 | 1.00x, crop 2.3x |
| Dico solo che non voglio il resto / Voglio tutto quello che voglio investo / Non voglio fare la fine di questi | fiches | 27.24 | 30.84 | 1.24x, 0.75x, fermo |
| Finire dentro una bara coi resti | scatola | 30.84 | 32.28 | 0.97x |
| Finire dentro una bara coi resti | nero | 32.28 | 32.68 |  |
| Voglio lasciare una parte di me | vetro | 32.68 | 34.04 | 1.88x, 1.00x |
| In nome dell'arte di quello che faccio / Per sta roba è una cifra che sbatto | studio | 34.04 | 36.11 | 1.00x, crop 2.2x |
| Per sta roba è una cifra che sbatto / Tu non capisci quello che ho fatto | microfono | 36.11 | 39.24 | 0.91x, crop 1.25x |
| Solo soldato le barre ho buttato | mano | 39.24 | 40.84 | 1.00x |
| Pacato, svogliato ma sono tornato | raffica | 40.84 | 42.84 |  |
| Lavorare per vivere mica / Vivere per lavorare | ufficio | 42.84 | 45.64 | 1.00x |
| Dentro la brocca cade la goccia | brocca | 45.64 | 47.40 | 1.00x |
| Gioco di carte e il vaso scompare | carte | 47.40 | 49.40 | 1.50x |
| Devi rischiare per prendere tutto / Fato farabutto ti tolgo il mio dalle mani | moneta | 49.40 | 53.92 | 0.50x, fermo immagine |
| Sleghiamo legami stupidi umani | corda | 53.92 | 56.08 | 1.00x |
| Corsa per il tempo bastardo | orologi | 56.08 | 57.52 | 1.00x |
| Sotto sto mondo ci metto un petardo | mappamondo | 57.52 | 59.36 | 1.00x |
| Morite contenti / Sono il salvatore Fatevi onore | nero | 59.36 | 62.96 |  |
| Senti la voce senti il respiro | wave | 62.96 | 66.06 | generata dallo stem vocale |
| Prendo la penna scrivo in corsivo / Sai che non mi fermo scrivo in eterno | penna | 66.06 | 71.56 |  |
| Fino a che non si spegne il cuore / Battico cardiaco conta le ore | candela | 71.56 | 73.31 |  |
| Battico cardiaco conta le ore / Fino al momento in cui muore | cuore | 73.31 | 76.64 | 1.00x, 1.19x, 1.25x, 1.25x, 1.00x, salto 0.17 s |
| Senti la voce senti il respiro | wave | 76.64 | 79.62 | generata dallo stem vocale |
| Prendo la penna scrivo in corsivo / Sai che non mi fermo scrivo in eterno | penna | 79.62 | 85.12 |  |
| Fino a che non si spegne il cuore / Battico cardiaco conta le ore | candela | 85.12 | 86.84 |  |
| Battico cardiaco conta le ore / Fino al momento in cui muore | cuore | 86.84 | 90.12 | 1.00x, 1.19x, 1.25x, 1.25x, 1.00x, salto 0.112 s |
| Quando mi ascolti rimani connesso | studio | 90.12 | 93.07 | 0.75x, fermo |
| Dentro la testa bro ho un mare diverso / Non mi fotte un cazzo di nessuno / Che sia chiaro giuro | mare | 93.07 | 99.03 | 0.84x |
| Vedo il chiaro scuro / Che diventa sempre un po più scuro / Un giorno tutto sarà buio | lampione | 99.03 | 103.36 | 0.68x, 1.07x, 0.73x, 1.00x |
| Non pensare io sia pessimista | brocca | 103.36 | 105.81 | 1.00x, crop 2.3x |
| Sono un artista / Senza un po di male la mia arte non ha vista / Quindi chi l'ha vista / Cambierò canale quando cambierò modo di pensare | specchio | 105.81 | 110.43 | 0.75x, fermo |
| Cambierò canale quando cambierò modo di pensare | tv | 110.43 | 113.43 |  |
| Ma è troppo banale / Io Non voglio mai assomigliare | tv | 113.43 | 116.80 | crop 1.45x |
| Odio lo standard / Mi prende male / Voglio le robe più strane | maschera | 116.80 | 120.19 | ≤0.80x |
| Voglio le robe più strane / Giro le strade vago nei posti / Cerco i dettagli nascosti | strada | 120.19 | 122.21 | ≤0.80x |
| Cerco i dettagli nascosti / Fino a trovare quello che cerco | torcia | 122.21 | 125.18 | 1.00x |
| Fino a trovare quello che cerco / Ma dubito sempre lo stesso / Adesso per me è già passato | clessidra | 125.18 | 128.15 | 0.48x |
| Adesso per me è già passato / L'istante presente l'ho già scordato / Non lo ricordo davvero non lo ricordo | foto | 128.15 | 133.61 | 0.91x |
| Cosa è successo? / Pensavo a domani ho perso qualcosa | specchio | 133.61 | 135.74 | 1.00x, crop 1.7x |
| Pensavo a domani ho perso qualcosa / Qui dalle mie mani / Aspetto il domani | sabbia | 135.74 | 137.44 | 1.00x |
| Aspetto il domani / Avrò schemi più chiari | tramonto | 137.44 | 139.57 | 1.00x al contrario |
| Ma tanto ho capito / È la mente mia che m'ha tradito | cervello | 139.57 | 143.85 | 1.20x, 0.90x |
| Senti la voce senti il respiro | wave | 143.85 | 147.22 | generata dallo stem vocale |
| Prendo la penna scrivo in corsivo / Sai che non mi fermo scrivo in eterno | penna | 147.22 | 152.72 |  |
| Fino a che non si spegne il cuore / Battico cardiaco conta le ore | candela | 152.72 | 154.44 |  |
| Battico cardiaco conta le ore / Fino al momento in cui muore | cuore | 154.44 | 157.68 | 1.00x, 1.19x, 1.25x, 1.25x, 1.00x, salto 0.169 s |
| Senti la voce senti il respiro | wave | 157.68 | 160.75 | generata dallo stem vocale |
| Prendo la penna scrivo in corsivo / Sai che non mi fermo scrivo in eterno | penna | 160.75 | 166.25 |  |
| Fino a che non si spegne il cuore / Battico cardiaco conta le ore | candela | 166.25 | 167.97 |  |
| Battico cardiaco conta le ore / Fino al momento in cui muore | cuore | 167.97 | 172.38 | 1.00x, 1.19x, 1.25x, 1.25x, 0.67x, salto 0.076 s |

## Storico v4 (ancora valido, salvo i punti superati dalla v5)

Superati dalla v5: scritte giganti e schermo che trema, corridoio rosso nei ritornelli, soundwave in clip, sfondo nero dell'intro, mare e lampione nella strofa 2.

### Modifiche v4

**Regole generali**
- Nessuno sfondo scurito o sfocato: ogni tratto ha la sua clip, oppure nero con testo grande.
- Clip 720x1280 ritagliate al centro e portate a 1080x1920 con lanczos, senza audio e con la stessa color grading.
- Nessun loop. Il riuso di una clip ha sempre un crop e/o un punto di partenza diversi.
- I tagli nuovi cadono sul beat più vicino. Quando confinano con un inserto della v3 rimasto uguale, usano il suo bordo.

**Intro**
- Tolta la candela con NON MI FERMO.
- IPNOS rosso (#E10600, Anton come nel finale) su nero. Attacchi trovati nell'audio: **0,165 s** (transiente acuto 4-12 kHz) e **0,655 s** (risalita della voce dopo la pausa 0,60-0,64 s). Coda d'eco fino a ~1,85 s.
- La scritta entra al ~70% della larghezza e si rimpicciolisce di scatto (ease-out in 0,15 s) a 0,82; sul secondo colpo passa a 0,65; sfuma da 1,15 a 1,85 s.
- Corridoio dal beat a 1,95 s (1,25 s, prima ~6,4 s), porta da 3,20 s (prima 6,94 s), taglio sul beat sullo studio a 5,29 s, senza flash.
- Studio: le cuffie arrivano sulla testa a 3,42 s di clip, allineate a "Torno" (8,80 s). La clip parte da 0 a ~0,98x. Lo studio resta fino a "Confesso" (13,04 s).

**Strofa 1**
- Pozzo da "La mente" con zoom lento in avanti.
- Muro su "Torno fresco".
- Strada di Ruoti su "e domani resto" (crop 1,5x sul ragazzo, partenza a 3,2 s; nella strofa 2 è intera da 0).
- Fiches su "Voglio tutto…": il crollo (1,58 s di clip) cade sul beat di "investo".
- Studio stretto sull'attrezzatura (zoom 2,2 su scrivania e monitor, tratto 0,3-2,4 s, prima delle cuffie) su "In nome dell'arte".
- Microfono/grata su "Per sta roba…": partenza a 1,6 s, crop diverso e zoom lento 1,0→1,15.
- Raffica su "Pacato": 14 clip già viste, 2-3 fotogrammi l'una, con un cambio di clip su ogni beat.
- Carte usate per intero (3 s su 2 s di verso, quindi 1,5x) al posto del nero.
- Moneta continua fino a "Sleghiamo": fotogrammi 22-72 senza 26, 34, 41, 42, a metà velocità. Fermo immagine e flash bianco su "tolgo".
- "Morite contenti / Sono il salvatore / Fatevi onore": nero, testo grande al centro, una frase alla volta.

**Strofa 2**
- Studio con le cuffie su "Quando mi ascolti" (inquadratura larga).
- Da "Non mi fotte" a "che diventa": nero con testo grande, glitch a ogni frase e sui beat, schermo che trema (±12 px). Su "chiaro scuro" strobo bianco/nero (immagine invertita) sui beat e mezzi beat: 4 lampi da 2 fotogrammi.
- Brocca stretta sul livello dell'acqua (zoom 2,3, tratto 2,2-4,65 s).
- Specchio allungato su "Quindi chi l'ha vista".
- Torcia allungata su "Fino a trovare".
- Clessidra: solo 0-1,42 s (finché scende la sabbia), a 0,48x.
- Foto fino alla fine della clip.
- Specchio con crop 1,7x sulle crepe su "Cosa è successo".
- Sabbia nelle mani su "Ho perso qualcosa / qui dalle mie mani".
- Tramonto al contrario (alba) su "Aspetto il domani".
- Pozzo con zoom fino a 2,4x dentro il buio fino al ritornello.

### Ripieghi

- **Studio nell'intro**: dopo le cuffie la clip ha solo 2,6 s per 4,24 s di versi, quindi 0,61x ("rallentala se non basta").
- **Studio su "Quando mi ascolti"**: le cuffie in testa esistono solo da 3,42 s a 6,04 s di clip e l'intro le usa tutte. Ho usato 3,8-6,0 s con un crop diverso (largo invece che stretto sulla testa), a 0,75x. Il tratto quindi si sovrappone in parte a quello dell'intro.
- **Fiches**: "Non voglio fare la fine di questi" non aveva indicazioni ed era sfondo. La clip continua dopo il crollo a 0,75x; finita la clip, l'ultimo fotogramma resta 0,44 s con uno zoom lento.
- **Specchio su "Quindi chi l'ha vista"**: 3 s di clip per 4,62 s, quindi 0,75x e poi ultimo fotogramma tenuto 0,63 s con zoom lento (la clip è quasi ferma).
- **Pozzo finale**: 0,75x, poi ultimo fotogramma tenuto 0,48 s mentre lo zoom continua nel buio.
- **Clessidra**: 0,48x, sotto la soglia di 0,75x, come richiesto ("rallentata quanto serve").
- **Carte**: per usarla tutta sul verso ho dovuto accelerarla (1,5x).
- **Foto**: nella clip la foto non brucia mai del tutto, quindi l'ho usata fino all'ultimo fotogramma.
- **Ritornelli** (nessuna indicazione, prima c'erano sfondi sfocati): soundwave allungata fino alla penna; penna (nitida) fino alla candela; corridoio rosso da "Battico cardiaco" alla riga successiva, come già nell'ultimo ritornello, con un punto di partenza e un crop diversi ogni volta.
- **Microfono su "Confesso"**: allungato fino a "Vorrei" (prima c'erano 0,4 s di sfondo).
- **sedia.mp4**: non più usata (su "Pacato" ora c'è la raffica). **muro.mp4**: ora usato.
