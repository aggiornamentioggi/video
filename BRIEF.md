# BRIEF v2: video "Non Mi Fermo" (Ipnos)

Questo brief SOSTITUISCE completamente il precedente. Lavora in autonomia fino alla consegna: non fermarti a chiedere conferme. Dove manca qualcosa applica il ripiego indicato e annotalo nel report.

## Obiettivo

Video musicale verticale 9:16 per YouTube, TikTok, Reels e Shorts. Il primo render era troppo statico: due terzi su nero pieno, una parola enorme alla volta al centro. Questa versione deve essere **densa, dinamica e con un crescendo**, per tenere attaccato chi guarda dall'inizio alla fine. Stile scuro e cinematografico, rosso come colore d'accento. Il personaggio incappucciato non mostra mai il volto.

## Cosa riusare dal lavoro precedente

- `out/sync.json` (tempi di ogni parola): riusalo, non rifare la trascrizione. Se manca o è corrotto, rifallo con sherpa-onnx e il modello `sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8` (finestre da 30 s, passo 25 s, solo i token centrali con 2,5 s di margine), allineando sempre al testo ufficiale.
- Audio: traccia con i primi 4,5 s tagliati e fade in di 0,3 s. Durata sotto i 3:00.

## File nella repo

I nomi non sono quelli "puliti": cerca per inizio del nome, in qualsiasi cartella.

| Inizia con | Ruolo |
|---|---|
| `Ipnos_-_Non_Mi_Fermo` (.mp3) | traccia |
| `testo` (.txt) | testo ufficiale |
| `The-hooded-young-man-keeps-walking` | corridoio |
| `The-hooded-young-man-seen-from-behind` | studio, cuffie |
| `The-old-CRT-television` | tv |
| `hf_20261003_151301` | strada (Ruoti) |
| `hf_20261003_154346` | candela |
| `Scrittura` / `penna` (immagine) | penna |

**Clip opzionali** (usale se ci sono, altrimenti salta quel punto senza fermarti): `moneta`, `goccia`, `carte`, `petardo`, `mare`, `lampione`, qualsiasi file che inizia con `personaggio` (nuove scene dell'incappucciato) e qualsiasi file che inizia con `performance` (riprese reali dell'artista che rappa).

Tutte le clip non 9:16 vanno ritagliate al centro e portate a 1080x1920, mai deformate né con bande nere. Uniforma il colore di tutte le clip: neri profondi, mezzitoni caldi, ombre leggermente fredde, saturazione contenuta.

## Specifiche di output

1080x1920, 30 fps, H.264 yuv420p, CRF 20, preset slow, AAC 192 kbps, `-movflags +faststart`. Ogni file sotto i 95 MB: se il video lo supera, alza il CRF di 2 e rifai l'export.

---

## 1. SOTTOTITOLI

### Posizione
- **Tutti i sottotitoli stanno nella parte inferiore del video**, nella fascia tra il **70% e l'80% dell'altezza** (y da 1344 a 1536 px)
- Mai sotto l'80%: lì ci sono descrizione e pulsanti di TikTok e Reels
- Centrati in orizzontale, larghezza massima 80% (864 px). Se una frase non ci sta, va su due righe dentro la fascia
- Eccezioni: "TEMPO BASTARDO" e la chiusura finale restano al centro dello schermo (vedi sotto)

### Contenuto
- **Non più una parola alla volta.** Frasi da 2 a 4 parole, spezzando le righe del testo ai respiri naturali del rap
- La parola cantata in quel momento è **bianca piena**, le altre della frase sono grigio al 50% (effetto karaoke)
- Nessuna parola vuota da sola a schermo ("A", "È", "IL", "LA"): sempre attaccata alla parola dopo

### Font e dimensione
- Frasi: **Montserrat SemiBold**, maiuscolo, corpo circa 64 px, spaziatura tra lettere +2%
- Parole chiave: **Anton**, rosso #E10600, corpo circa 1,4 volte le altre
- Parole chiave: cuore, tempo, bastardo, rischiare, mente, buio, scuro, eterno, muore, tradito, penna, voce, respiro, non mi fermo
- Font da scaricare dal repo GitHub `google/fonts`
- Ombra morbida nera (blur 12 px, opacità 70%) sotto tutto il testo, per la leggibilità su qualsiasi sfondo

### Effetti sul testo
- Entrate a rotazione, mai la stessa due volte di seguito: blur da 12 px a 0 con opacità 0→1 in 6 frame, scivolata dal basso di 30 px, scivolata laterale di 30 px, a scatto con micro zoom 1.15→1.00 in 4 frame
- **Glitch RGB split + tremolio** per 3–4 frame su: bastardo, muore, tradito, buio, scuro
- Parole chiave rosse: pulsazione di scala ±6% sul beat finché restano a schermo
- **Ritornelli**: effetto macchina da scrivere lettera per lettera, più micro scossa sui colpi di cassa
- Piccole variazioni orizzontali (±40 px) da una frase all'altra, sempre dentro la fascia inferiore

---

## 2. SFONDO

- **Niente nero pieno**, tranne su "TEMPO BASTARDO" e nella chiusura finale. Quei due momenti spiccano proprio perché sono gli unici neri
- Quando non c'è una clip inserita, dietro al testo va una clip **sfocata (gaussian 20 px) e scurita al 25–30%**, con zoom lento 1.00→1.06:
  - strofa 1: studio e corridoio
  - ritornelli: candela e penna, alternate
  - strofa 2: strada, tv e (se ci sono) mare e lampione
- Usa anche porzioni diverse e ingrandite della stessa clip per variare
- **Grana pellicola** leggera su tutto il video
- **Light leak rossi** morbidi nei ritornelli, insieme alla pulsazione rossa (vignettatura che cresce e cala sulla cassa, intensità massima 35%)

---

## 3. DINAMICA (priorità alta)

- Rileva i colpi di cassa dall'audio (onset detection sulle basse frequenze) e salvali in `out/beats.json`
- **Regola della densità: ogni 1,5–3 secondi deve cambiare qualcosa** (taglio, inquadratura, porzione della clip, colore, posizione). Mai la stessa inquadratura ferma per più di 4 secondi
- **Zoom punch** su ogni cassa: scala +4% e ritorno in 4 frame, su tutto il frame
- Sfondo che cambia clip o inquadratura ogni 2 battute
- Movimento continuo dello sfondo: pan lento, rotazione ±1,5°, drift. Nelle strofe aggiungi una scossa leggera costante
- **Flash bianco** di 2 frame su ogni cambio di sezione e sulle parole chiave rosse
- Clip inserite con **speed ramp**: entrano al 60% della velocità e tornano al 100% sul beat successivo
- Tagli sempre secchi, sul beat. Nessuna dissolvenza tra le clip
- Clip più corte del loro spazio: rallenta fino al 70% prima di ripetere. Clip più lunghe: taglia la fine

### Crescendo
L'intensità deve salire durante il video, non restare uguale:
- **Strofa 1**: sobria, tagli ogni 2–3 s, effetti contenuti
- **Primo ritornello**: primo salto, con rosso, pulsazione e macchina da scrivere
- **Strofa 2**: nervosa, tagli ogni 1,5–2 s, scossa più forte, più glitch
- **Ultimo ritornello**: massimo assoluto di tagli, rosso, zoom punch e flash
- Chiusura: stacco netto sul nero e calma

---

## 4. STRUTTURA E STORIA

L'incappucciato è il filo del video: arriva, scrive, esce nella notte, torna.

| Momento | A schermo |
|---|---|
| **Aggancio (0:00–0:00,5)** | Flash di mezzo secondo dell'immagine più forte: candela con "NON MI FERMO" rosso al centro. Poi stacco secco |
| **Intro** | Corridoio **ridotto a circa 2 s**, poi studio: le cuffie salgono sulla testa esattamente sull'attacco di "Torno sul pezzo". Le parole "TORNO SUL PEZZO" compaiono in basso su quel colpo |
| **Strofa 1** | Sfondi: studio e corridoio sfocati. Clip inserite: `moneta` da "Devi rischiare per prendere tutto" fino a "legami"; `goccia` su "Dentro la brocca cade la goccia"; `carte` su "Gioco di carte e il vaso scompare"; `petardo` su "Sotto sto mondo ci metto un petardo", con flash bianco su "petardo" |
| **"Corsa per il tempo bastardo"** | Nero pieno. "TEMPO BASTARDO" rosso **al centro**, a scatto, con flash bianco e glitch sul colpo |
| **Ritornelli** | `penna` su "Prendo la penna scrivo in corsivo" (push in lento 1.00→1.08 verso il pennino e tremolio di luce tipo lampada, la mano non si muove). `candela` su "Fino a che non si spegne il cuore" |
| **Strofa 2** | `mare` su "Dentro la testa bro ho un mare diverso". `lampione` su "Un giorno tutto sarà buio", con taglio a nero di 1 secondo quando si spegne. `tv` da "Cambierò canale" fino a "assomigliare". `strada` su "Giro le strade vago nei posti" |
| **Ultimo ritornello** | Massima intensità. Se c'è, usa un'inquadratura dell'incappucciato in luce rossa |
| **Chiusura** | Vedi sotto |

Riprese `performance` (se ci sono): distribuiscile in tutto il video come tagli di 1–2 s sui versi più forti e soprattutto nei ritornelli, a piena luminosità. Hanno la priorità sugli sfondi sfocati.

Clip `personaggio` (se ci sono): usale dove la storia le richiede (tetto e strada nella strofa 2, studio rosso nell'ultimo ritornello).

---

## 5. CHIUSURA

Nero pieno, tre righe centrate al centro dello schermo, che restano visibili insieme fino all'ultimo frame:

1. **NON MI FERMO**: bianco, Anton, entra a scatto sul colpo finale
2. **IPNOS**: grande, rosso #E10600, Anton, entra a scatto sul colpo successivo
3. **IPNOS CREATIVE STUDIO**: Montserrat SemiBold, bianco al 85%, corpo circa 40 px (**il doppio della versione precedente**), spaziatura tra lettere +20%, staccato da IPNOS di almeno 50 px, entra in dissolvenza di 0,5 s dopo IPNOS

Fade a nero solo negli ultimi 0,5 s, insieme all'audio.

---

## 6. ORDINE DI LAVORO E CONSEGNA

1. Prepara le clip (crop, colore), rileva i beat, costruisci la timeline
2. Renderizza un'**anteprima di 20 secondi** del primo ritornello in `out/anteprima_ritornello.mp4` e un foglio di fotogrammi in `out/anteprima_sheet.jpg`. Fai commit e push. **Poi prosegui senza aspettare**
3. Renderizza il video completo: `out/non_mi_fermo_v2_1080x1920.mp4`
4. Ricava dal video completo **3 tagli brevi per TikTok e Reels**, ciascuno con un flash di aggancio all'inizio e la chiusura IPNOS di 2 s alla fine:
   - `out/taglio_ritornello.mp4`: primo ritornello completo (circa 25–35 s)
   - `out/taglio_strofa.mp4`: le barre più forti della strofa 2 (circa 25–35 s)
   - `out/taglio_finale.mp4`: ultimo ritornello e chiusura (circa 30–40 s)
5. `out/REPORT.md`: durata e peso di ogni file, quali clip opzionali hai trovato e usato, quali sono mancate, ogni ripiego applicato
6. Commit e push di tutto sul branch di lavoro della sessione
