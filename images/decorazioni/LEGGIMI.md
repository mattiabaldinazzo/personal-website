# Decorazioni della libreria

Questa cartella contiene gli oggetti da mettere sulle mensole della sezione Letture: vasi, lampade, statue, piante. Li posizioni in `content/libreria.md` con una riga come `decorazione: vaso.webp, 60%`, dove il numero è l'altezza in percentuale della mensola.

Regole.
Formato webp o png con sfondo trasparente. Un jpg ha sempre lo sfondo pieno: il build lo accetta ma ti avvisa.
Ritaglio stretto attorno all'oggetto, soprattutto in basso. Il bordo inferiore dell'immagine è la base che poggia sulla mensola: anche pochi pixel trasparenti sotto l'oggetto lo fanno sembrare sospeso.
Almeno 440 px di altezza, così l'oggetto resta nitido sugli schermi ad alta densità. Peso consigliato sotto i 100 KB.
Nome del file con lettere, numeri, trattini e punti, senza spazi. Se il nome in `content/libreria.md` non corrisponde a un file di questa cartella, il build fallisce e ti dice quale.

Per scontornare una foto con iPhone apri l'app Foto, tieni premuto sull'oggetto e scegli Condividi: ottieni un png con lo sfondo trasparente.

Questo file può restare qui, viene ignorato dal build.
