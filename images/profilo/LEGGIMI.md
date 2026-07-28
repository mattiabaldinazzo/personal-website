# Foto del profilo

Questa cartella contiene la foto mostrata nella sezione "Chi sono", accanto al testo su schermo largo e sopra il testo su telefono.

Per sostituirla: elimina l'immagine attuale e metti qui la nuova, poi fai commit. Il nome del file è libero, il build usa in automatico l'unica immagine presente nella cartella.

Regole.
Una sola immagine nella cartella: con zero o più di una il build fallisce e ti avvisa. Le versioni ridotte generate da `tools/ottimizza-immagini.py` (per esempio `fotoprofilo-480.webp`) non contano, il build le riconosce dal suffisso numerico.
Formati accettati: webp, jpg, jpeg, png.
Proporzione consigliata 4:5 verticale, per esempio 760x950 px: è esattamente il formato usato dal sito, quindi non viene ritagliato nulla. Con altre proporzioni il sito ritaglia al centro per arrivare a 4:5.
La foto viene mostrata intera, con angoli arrotondati e senza cornice. Uno sfondo chiaro e uniforme, vicino al colore della carta del sito (#FAF9F5), fa sparire i bordi; uno sfondo scuro o molto contrastato disegna invece un rettangolo netto.
Larghezza consigliata 760 px e peso sotto i 150 KB; webp è il formato più leggero.

Dopo averla sostituita, rigenera le versioni ridotte con `python3 tools/ottimizza-immagini.py` e committa anche quelle.

Questo file può restare qui, viene ignorato dal build.
