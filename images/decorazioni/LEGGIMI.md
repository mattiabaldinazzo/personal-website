# Decorazioni della libreria

Questa cartella contiene gli oggetti da mettere sulle mensole della sezione Letture: vasi, lampade, statue, piante. Li posizioni in `content/libreria.md` con una riga come `decorazione: vaso.webp, 60%`, dove il numero è l'altezza in percentuale della mensola.

Regole.
Formato png o webp con sfondo trasparente. Un jpg ha sempre lo sfondo pieno: il build lo accetta ma ti avvisa.
Il bordo inferiore dell'immagine è la base che poggia sulla mensola: anche pochi pixel vuoti sotto l'oggetto lo fanno sembrare sospeso.
Nome del file con lettere, numeri, trattini e punti, senza spazi. Se il nome in `content/libreria.md` non corrisponde a un file di questa cartella, il build fallisce e ti dice quale.

Dopo aver aggiunto un'immagine lancia `python3 tools/ottimizza-immagini.py`. Lo script taglia i bordi trasparenti attorno all'oggetto, porta l'altezza a 440 px se è più alta e salva in webp conservando la trasparenza. Se il file era un png, il nome diventa .webp: lo script te lo scrive e in `content/libreria.md` usi il nome nuovo. Lanciarlo più volte non cambia più nulla.

Per scontornare una foto con iPhone apri l'app Foto, tieni premuto sull'oggetto e scegli Condividi: ottieni un png con lo sfondo trasparente.

Questo file può restare qui, viene ignorato dal build.
