# mattiabaldinazzo.it

Sito statico bilingue generato da file markdown. Per aggiungere un progetto, un progresso o un libro basta creare un file in `content/` e fare commit su `main`: il workflow rigenera e pubblica il sito nelle due lingue. Funziona da qualunque editor di testo, anche dall'interfaccia web di GitHub (Add file, Create new file).

## Le due lingue

Italiano su `https://mattiabaldinazzo.it/`, inglese su `https://mattiabaldinazzo.it/en/`. Il selettore in alto è un link tra le due pagine, quindi funziona anche senza JavaScript e ogni lingua ha un indirizzo indicizzabile.

Ogni contenuto tiene le due lingue nello stesso file: nel frontmatter i campi inglesi hanno il suffisso `_en` (`titolo_en`, `descrizione_en`), nel corpo la parte inglese va dopo una riga con scritto `--- en ---`. Se una traduzione manca, il sito inglese mostra il testo italiano e il build stampa un avviso senza bloccare la pubblicazione.

I testi fissi dell'interfaccia (menu, bottoni, titoli di sezione) stanno in `content/testi/it.md` e `content/testi/en.md`. I due file devono avere le stesse chiavi: se ne manca una il build fallisce e ti dice quale. Le due scritte del selettore sono le chiavi `etichetta_it` e `etichetta_en`: per passare da IT/EN a ITA/ENG le cambi in entrambi i file.

## Aggiungere un progetto

Crea `content/progetti/12-nome-progetto.md`. Nome file solo con minuscole, numeri e trattini; il numero iniziale decide l'ordine.

```markdown
---
titolo: Nome del progetto
titolo_en: Project name
categoria: personali
descrizione: Una riga che descrive il progetto.
descrizione_en: One line describing the project.
immagine: /images/projects/nome.webp
link: https://esempio.com
link_testo: Apri progetto
link_testo_en: Open project
---

Testo facoltativo della scheda di dettaglio, in markdown.
Se presente, la card apre una scheda invece del link.

## Un sottotitolo

- una lista
- **grassetto**, *corsivo*, [link](https://esempio.com)

--- en ---

Optional detail card text, in markdown.

## A subheading

- a list
- **bold**, *italic*, [link](https://example.com)
```

Regole:

`titolo`, `categoria`, `descrizione` sono obbligatori. `categoria` può essere `personali`, `lavorativi`, `universitari` o una nuova: i filtri si aggiornano da soli. `immagine` è facoltativa: senza, la card mostra il titolo su fondo scuro. Se il file ha un corpo sotto il secondo `---`, la card apre la scheda di dettaglio (il `link` compare come bottone in fondo). Se non ha corpo, la card apre direttamente il `link`. Ogni scheda di dettaglio ha un URL diretto: `https://mattiabaldinazzo.it/#progetto-nome-progetto`.

## Aggiungere un progresso

Crea `content/progressi/02-nome.md`. Compare nella sezione Progressi con una barra di avanzamento; la percentuale viene calcolata in automatico da `raggiunto` e `totale`.

```markdown
---
titolo: N8N
titolo_en: N8N
descrizione: Imparare ad automatizzare l'operatività in locale tramite N8N.
descrizione_en: Learning to automate day-to-day work locally with N8N.
raggiunto: 8
totale: 10
unita: lezioni
unita_en: lessons
---
```

Tutti i campi sono obbligatori tranne `unita`, che è l'etichetta mostrata accanto ai numeri (lezioni, capitoli, km). `raggiunto` e `totale` sono numeri; `raggiunto` deve stare tra 0 e `totale`. L'esempio sopra mostra "8/10 lezioni" e "80%". Quando finisci, porta `raggiunto` al valore di `totale` oppure elimina il file.

## Aggiungere un libro

Crea `content/libri/09-titolo-libro.md`.

```markdown
---
titolo: Titolo del libro
titolo_en: Book title
autore: Nome Autore
voto: 5
copertina: /images/books/titolo.webp
---

Nota facoltativa di una o due righe, mostrata sotto l'autore.

--- en ---

Optional one or two line note, shown under the author.
```

Tutti e quattro i campi sono obbligatori, `voto` da 1 a 5. I primi 4 libri sono visibili, gli altri compaiono con "Mostra tutti i libri".

## Cambiare la foto profilo

La foto della sezione Chi sono sta in `images/profilo/`, il nome del file è libero: il build usa l'unica immagine presente nella cartella. Per cambiarla elimina quella attuale, aggiungi la nuova e fai commit. Regole e formato consigliato sono in `images/profilo/LEGGIMI.md`. Con zero immagini o più di una il build fallisce e ti avvisa.

## Immagini

Progetti in `images/projects/` (webp, larghezza 880 px). Copertine in `images/books/` (webp, larghezza 440 px). Foto del profilo in `images/profilo/`. Se il markdown punta a un'immagine che non esiste, il build fallisce e te lo dice.

Accanto a ogni immagine c'è una versione ridotta con il suffisso della larghezza, per esempio `spotify-480.webp`: il sito le propone al browser con `srcset`, così su telefono viene scaricata solo la misura che serve. Quando aggiungi o sostituisci un'immagine, rigenera le versioni ridotte:

```bash
pip install pillow
python3 tools/ottimizza-immagini.py
```

Committa i file generati insieme all'originale. Se te ne dimentichi il sito funziona lo stesso, semplicemente scarica l'immagine grande anche sui telefoni. Il build non ha bisogno di Pillow: usa le versioni ridotte se le trova, altrimenti tira dritto.

## Pubblicazione

Push su `main`: il workflow esegue `python3 build.py`, genera `_site/` con le due lingue e pubblica su GitHub Pages. Se un file markdown ha errori (campo mancante, numero non valido, immagine inesistente) il build fallisce con l'elenco dei problemi e il sito online resta quello precedente. In Settings, Pages la source deve essere "GitHub Actions".

## Anteprima locale

```bash
python3 build.py
python3 -m http.server 8000 --directory _site
```

Poi apri http://localhost:8000. Serve solo Python 3, nessuna dipendenza.

## Struttura

`content/` i contenuti in markdown (progetti, progressi, libri) e i testi dell'interfaccia in `content/testi/`. `templates/index.html` la struttura della pagina, unica per entrambe le lingue. `build.py` il generatore (solo libreria standard). `styles.css` e `main.js` stile e comportamenti; il CSS viene incorporato nella pagina dal build, così il browser non deve scaricare un secondo file prima di disegnare. `tools/` gli script di manutenzione. `fonts/` iA Writer Quattro S e Mono S più Parisienne ridotto alle lettere del monogramma M.B., tutti self-hosted con licenza SIL OFL. `images/` le immagini ottimizzate, con `images/profilo/` per la foto. `jet_converter/` tool indipendente, pubblicato così com'è. `_site/` output generato, non si committa.
