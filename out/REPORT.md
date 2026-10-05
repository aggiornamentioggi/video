# Report v2: "Non Mi Fermo" (Ipnos)

Eseguito `BRIEF.md` v2, che sostituisce completamente il precedente. `out/sync.json` è stato riusato senza rifare la trascrizione.

## Aggiornamento: nuove clip e ritornello più leggibile

**Dieci clip nuove** sono state portate dal branch main (merge). Ognuna è inserita a piena luminosità sul suo verso, con i tempi presi da `out/sync.json` e i tagli sul beat:

| Clip | Verso | Inserto |
|---|---|---|
| `tramonto.mp4` | "Vorrei non ci fosse un domani / Che tutto finisse oggi" | 15,72–19,18 s |
| `ufficio.mp4` | "Lavorare per vivere mica / Vivere per lavorare" | 42,86–45,77 s |
| `brocca.mp4` | "Dentro la brocca cade la goccia" | 45,77–47,42 s |
| `carte.mp4` | "Gioco di carte e il vaso scompare" | 47,42–49,58 s |
| `mare.mp4` | "Dentro la testa bro ho un mare diverso" | 93,07–96,46 s |
| `specchio.mp4` | "Sono un artista / Senza un po di male…" | 105,81–109,20 s |
| `maschera.mp4` | "Odio lo standard / Mi prende male / Voglio le robe più strane" | 116,80–120,19 s |
| `muro.mp4` | "Giro le strade vago nei posti" | 120,19–122,21 s |
| `torcia nel buio.mp4` | "Cerco i dettagli nascosti" | 122,21–123,90 s |
| `foto.mp4` | "L'istante presente l'ho già scordato" | 128,15–130,75 s |

- Le clip 720x1280 sono portate a 1080x1920 con scala lanczos, senza deformazioni né bande; brocca e foto (1080x1916) sono ritagliate al centro. Stessa correzione colore del resto del video.
- L'audio è tolto da tutte le clip (aveva una traccia solo `tramonto.mp4`): si sente solo la musica.
- Le clip più corte del verso sono rallentate fino a un minimo di 0,8x, mai in loop. Tutte coprono il verso intero a 0,8x o più, quindi nessun inserto è stato accorciato. Per queste clip non c'è lo speed ramp al 60%, che le avrebbe rallentate sotto lo 0,8x.
- `muro.mp4` su "Giro le strade" prende il posto della clip `strada`, che resta come sfondo sfocato nella strofa 2.
- `carte` e `mare`, che il brief v2 elencava tra le opzionali, ora ci sono.

**Correzione del ritornello** (prima e dopo in `confronto_ritornello_prima/dopo.jpg` a 64,6 s, tra due casse, e in `confronto_ritornello_cassa_prima/dopo.jpg` a 65,9 s, sul colpo di cassa):

- Oscuramento dello sfondo dimezzato: la luminosità della clip passa dal 28% al 64%.
- Sfocatura dello sfondo più leggera nei ritornelli (~12 px invece di ~20 px), perché i dettagli si leggano.
- Vignettatura rossa più leggera: parte più verso i bordi e lascia libero il centro. La pulsazione sulla cassa resta, sempre con il massimo al 35%.
- Light leak più tenui, grana pellicola dimezzata (rumore allo 0,5%) su tutto il video.
- Con meno grana il video completo sta sotto i 95 MB già a CRF 22 (prima serviva 24).

## File consegnati

| File | Durata | Peso | CRF |
|---|---|---|---|
| `non_mi_fermo_v2_1080x1920.mp4` | 2:59,70 | 75,2 MB (75 235 243 byte) | **22**: a CRF 20 pesava 103,9 MB, oltre i 95 MB, quindi CRF alzato di 2 come da brief |
| `anteprima_ritornello.mp4` | 0:20,00 | 12,0 MB | 20 |
| `taglio_ritornello.mp4` | 0:29,00 | 17,2 MB | 20 |
| `taglio_strofa.mp4` | 0:33,73 | 21,3 MB | 20 |
| `taglio_finale.mp4` | 0:35,87 | 22,0 MB | 20 |
| `confronto_ritornello_*.jpg` | fotogrammi prima/dopo la correzione del ritornello | | |
| `anteprima_sheet.jpg` | foglio di 24 fotogrammi del primo ritornello | | |
| `beats.json` | 402 beat (~143,5 BPM) e 299 colpi di cassa con la loro forza | | |

Tutti i file sono 1080x1920, 30 fps, H.264 yuv420p, preset slow, AAC 192 kbps, `+faststart`, sotto i 95 MB. Il video v1 (`non_mi_fermo_1080x1920.mp4`) resta nella cartella come riferimento.

## Clip opzionali

Prima versione v2: nessuna trovata. Con l'aggiornamento sono arrivate `carte` e `mare` (vedi sopra); le altre mancano ancora.

| Clip | Esito e ripiego |
|---|---|
| `moneta` | mancante: "Devi rischiare… / Sleghiamo legami" restano sullo sfondo sfocato dello studio/corridoio |
| `goccia` | mancante, ma sul verso ora c'è `brocca.mp4` |
| `carte` | **trovata**: inserita su "Gioco di carte e il vaso scompare" |
| `petardo` | mancante: "Sotto sto mondo ci metto un petardo" sullo sfondo sfocato |
| `mare` | **trovata**: inserita su "Dentro la testa bro ho un mare diverso" (come sfondo sfocato la strofa 2 alterna sempre strada e TV) |
| `lampione` | mancante: niente taglio a nero di 1 s su "Un giorno tutto sarà buio" (resta il glitch su "buio") |
| `personaggio` | mancante: nell'ultimo ritornello l'incappucciato in luce rossa è ricavato dalle clip esistenti: studio (cuffie in testa) e corridoio, regradati in rosso, su "Senti la voce…" e "Battico cardiaco…" |
| `performance` | mancante: nessuna ripresa dell'artista |

## Cosa è stato fatto

- **Aggancio 0–0,5 s**: candela a piena luce con "NON MI FERMO" rosso al centro, poi stacco secco.
- **Intro**: corridoio ridotto a 1,9 s, poi studio. Un dettaglio stretto su mani e cuffie, quindi l'inquadratura larga con speed ramp, con l'attacco calcolato perché le cuffie arrivino in testa esattamente sull'attacco di "Torno" (8,85 s). Lì c'è uno stacco su un'inquadratura stretta e "TORNO SUL PEZZO" entra in basso.
- **Sottotitoli**: 172 frasi da 2 a 4 parole, spezzate alle pause del rap, senza parole vuote da sole o in coda. Stanno nella fascia 70–80% dell'altezza, larghezza massima 80% (due righe se serve), con variazioni orizzontali di ±40 px.
  - Karaoke: parola cantata bianca piena, le altre grigio 50%.
  - Montserrat SemiBold 64 px maiuscolo con spaziatura +2%; parole chiave in Anton rosso #E10600 a 1,4 volte, con pulsazione di scala ±6% sul beat. Ombra morbida (blur 12 px, 70%).
  - Entrate a rotazione, mai uguali di seguito: blur 12→0, scivolata dal basso, scivolata laterale, scatto con micro zoom.
  - Nei ritornelli macchina da scrivere lettera per lettera, con micro scossa sui colpi di cassa.
  - Glitch RGB e tremolio su bastardo, muore, tradito, buio, scuro, più glitch brevi aggiuntivi nella strofa 2 e nell'ultimo ritornello (27 glitch in tutto).
- **Sfondi**: 104 segmenti tagliati sul beat. Ognuno ha una porzione ingrandita diversa della clip, pan, rotazione ±1,5° e zoom lento 1,00→1,06. Nelle strofe sfocatura ~20 px e luminosità al 28%; nei ritornelli ~12 px e 64%.
  - Strofa 1: studio e corridoio, cambio ogni 6 battiti (~2,5 s), scossa leggera.
  - Ritornelli: candela e penna alternate, cambio ogni 4 battiti; nell'ultimo ritornello ogni 2.
  - Strofa 2: strada e TV, cambio ogni 4 battiti (~1,7 s), scossa più forte.
- **Nero pieno** solo su "TEMPO BASTARDO" (rosso al centro, a scatto, con glitch sul colpo) e nella chiusura.
- **Clip inserite** a piena luminosità: penna (push in 1,00→1,08 verso il pennino e tremolio di lampada, la mano ferma), candela (spegnimento allineato su "cuore"), TV da "Cambierò canale" ad "assomigliare" (spezzata in due inquadrature per non superare i 4 s), più le dieci clip nuove sui versi (vedi sopra). Penna, candela e TV hanno lo speed ramp: entrano al 60% e tornano al 100% sul beat successivo.
- **Dinamica e crescendo**: zoom punch sulla cassa. Nella strofa 1 è +2,5% e solo sulle casse forti; nei ritornelli e nella strofa 2 +4%; nell'ultimo ritornello +5%. Pulsazione rossa a vignettatura (massimo 35%) e light leak rossi nei ritornelli, più intensi nell'ultimo. Grana pellicola leggera su tutto (dimezzata nell'aggiornamento).
- **Colore**: tutte le clip uniformate (neri profondi, mezzitoni caldi, ombre leggermente fredde, saturazione all'82%).
- **Chiusura**: nero. "NON MI FERMO" (Anton, bianco) entra sul colpo finale a 174,01 s, "IPNOS" (Anton, rosso) su quello dopo a 174,65 s. "IPNOS CREATIVE STUDIO" (Montserrat SemiBold 40 px, bianco 85%, spaziatura +20%, 60 px sotto IPNOS) entra in dissolvenza di 0,5 s dal beat successivo. Fade a nero e audio negli ultimi 0,5 s.

## Tagli brevi

Ognuno è ricavato dal video completo, con l'aggancio di 0,5 s all'inizio (sopra l'audio del segmento) e la chiusura IPNOS di 2 s alla fine.

- `taglio_ritornello.mp4`: primo ritornello completo, 63,13–90,12 s.
- `taglio_strofa.mp4`: strofa 2 da "Vedo il chiaro scuro" fino a "…l'ho già scordato" (99,03–130,75 s): buio/scuro con glitch, TV, strada.
- `taglio_finale.mp4`: ultimo ritornello e chiusura vera del brano, 143,85 s–fine. Non c'è una chiusura di 2 s aggiunta, perché quella completa è già inclusa.

## Ripieghi e scelte

1. **Flash bianchi tolti del tutto** su richiesta (troppo forti). Il brief li chiedeva su ogni cambio di sezione, sulle parole chiave rosse, su "TEMPO BASTARDO" e su "petardo". L'aggancio iniziale non è un flash bianco ed è rimasto.
2. **CRF del video completo a 22**: la grana pellicola si comprime poco. Per stare sotto i 95 MB è stata applicata la regola del brief (20 → 22). La grana è leggera (rumore allo 0,5%, rinnovato ogni 3 fotogrammi).
3. **Ritornelli cantati due volte**: come in v1, il blocco del ritornello di `testo.txt` è ripetuto per seguire l'audio.
4. **Candela**: l'attacco è spostato in modo che il soffio che spegne la fiamma cada su "cuore". Negli sfondi sfocati si usa solo la parte con la fiamma accesa.
5. **Corridoio di 1,9 s e studio**: per arrivare con le cuffie in testa su "Torno" lo studio occupa 2,4–8,85 s in due inquadrature (dettaglio e larga) che mostrano in parte lo stesso gesto da due angoli.
6. **Chiusura nei tagli da 2 s**: la finestra 174,0–176,0 s contiene l'ingresso di NON MI FERMO e di IPNOS; "IPNOS CREATIVE STUDIO" compare nell'ultimo secondo.

## Riprodurre

```
python3 tools/beats.py                                  # (in WORK) beat e casse
python3 tools/render.py WORK --prep                     # clip graduate, sfondi, out/beats.json
python3 tools/build.py WORK                             # render, anteprima, video completo, tagli
```
