# mattiabaldinazzo.it

Sito statico generato da file markdown. Per aggiungere un progetto, un progresso o un libro basta creare un file in `content/` e fare commit su `main`: il workflow rigenera e pubblica il sito. Funziona da qualunque editor di testo, anche dall'interfaccia web di GitHub (Add file, Create new file).

## Aggiungere un progetto

Crea `content/progetti/12-nome-progetto.md`. Nome file solo con minuscole, numeri e trattini; il numero iniziale decide l'ordine.

```markdown
---
titolo: Nome del progetto
categoria: personali
descrizione: Una riga che descrive il progetto.
immagine: /images/projects/nome.webp
link: https://esempio.com
link_testo: Apri progetto
---

Testo facoltativo della scheda di dettaglio, in markdown.
Se presente, la card apre una scheda invece del link.

## Un sottotitolo

- una lista
- **grassetto**, *corsivo*, [link](https://esempio.com)
```

Regole:

`titolo`, `categoria`, `descrizione` sono obbligatori. `categoria` può essere `personali`, `lavorativi`, `universitari` o una nuova: i filtri si aggiornano da soli. `immagine` è facoltativa: senza, la card mostra il titolo su fondo scuro. Se il file ha un corpo sotto il secondo `---`, la card apre la scheda di dettaglio (il `link` compare come bottone in fondo). Se non ha corpo, la card apre direttamente il `link`. Ogni scheda di dettaglio ha un URL diretto: `https://mattiabaldinazzo.it/#progetto-nome-progetto`.

## Aggiungere un progresso

Crea `content/progressi/02-nome.md`. Compare nella sezione Progressi con una barra di avanzamento; la percentuale viene calcolata in automatico da `raggiunto` e `totale`.

```markdown
---
titolo: N8N
descrizione: Imparare ad automatizzare l'operatività in locale tramite N8N.
raggiunto: 8
totale: 10
unita: lezioni
---
```

Tutti i campi sono obbligatori tranne `unita`, che è l'etichetta mostrata accanto ai numeri (lezioni, capitoli, km). `raggiunto` e `totale` sono numeri; `raggiunto` deve stare tra 0 e `totale`. L'esempio sopra mostra "8/10 lezioni" e "80%". Quando finisci, porta `raggiunto` al valore di `totale` oppure elimina il file.

## Aggiungere un libro

Crea `content/libri/09-titolo-libro.md`.

```markdown
---
titolo: Titolo del libro
autore: Nome Autore
voto: 5
copertina: /images/books/titolo.webp
---

Nota facoltativa di una o due righe, mostrata sotto l'autore.
```

Tutti e quattro i campi sono obbligatori, `voto` da 1 a 5. I primi 4 libri sono visibili, gli altri compaiono con "Mostra tutti i libri".

## Cambiare la foto profilo

La foto della sezione Chi sono sta in `images/profilo/`, il nome del file è libero: il build usa l'unica immagine presente nella cartella. Per cambiarla elimina quella attuale, aggiungi la nuova e fai commit. Regole e formato consigliato sono in `images/profilo/LEGGIMI.md`. Con zero immagini o più di una il build fallisce e ti avvisa.

## Immagini

Progetti in `images/projects/` (webp, larghezza 880 px). Copertine in `images/books/` (webp, larghezza 440 px). Se il markdown punta a un'immagine che non esiste, il build fallisce e te lo dice.

## Pubblicazione

Push su `main`: il workflow esegue `python3 build.py`, genera `_site/` e pubblica su GitHub Pages. Se un file markdown ha errori (campo mancante, numero non valido, immagine inesistente) il build fallisce con l'elenco dei problemi e il sito online resta quello precedente. In Settings, Pages la source deve essere "GitHub Actions".

## Anteprima locale

```bash
python3 build.py
python3 -m http.server 8000 --directory _site
```

Poi apri http://localhost:8000. Serve solo Python 3, nessuna dipendenza.

## Struttura

`content/` i contenuti in markdown (progetti, progressi, libri). `templates/index.html` la struttura della pagina. `build.py` il generatore (solo libreria standard). `styles.css` e `main.js` stile e comportamenti. `fonts/` iA Writer Quattro S e Mono S più Caveat ridotto alle lettere del monogramma MB, tutti self-hosted con licenza SIL OFL. `images/` le immagini ottimizzate, con `images/profilo/` per la foto. `jet_converter/` tool indipendente, pubblicato così com'è. `_site/` output generato, non si committa.
