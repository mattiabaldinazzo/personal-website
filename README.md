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

I primi 6 progetti sono visibili, gli altri compaiono con "Mostra tutti i progetti". La soglia è la costante `PROGETTI_VISIBILI` in `build.py`.

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

I primi 4 progressi sono visibili, gli altri compaiono con "Mostra tutti i progressi". La soglia è la costante `PROGRESSI_VISIBILI` in `build.py`.

Tutti i campi sono obbligatori tranne `unita`, che è l'etichetta mostrata accanto ai numeri (lezioni, capitoli, km). `raggiunto` e `totale` sono numeri; `raggiunto` deve stare tra 0 e `totale`. L'esempio sopra mostra "8/10 lezioni" e "80%". Quando finisci, porta `raggiunto` al valore di `totale` oppure elimina il file.

### Dividere un progresso in parti

Quando lo stesso argomento cresce e vuoi tenerne separati i pezzi, non creare un secondo file: aggiungi le parti dentro quello che hai già. Il frontmatter tiene solo il titolo dell'argomento e ogni parte si apre con una riga `--- parte ---`, seguita dagli stessi campi di prima.

```markdown
---
titolo: N8N
titolo_en: N8N
---

--- parte ---
titolo: Parte 1
titolo_en: Part 1
descrizione: Imparare ad automatizzare l'operatività in locale tramite N8N.
descrizione_en: Learning to automate day-to-day work locally with N8N.
raggiunto: 5
totale: 10
unita: lezioni
unita_en: lessons

--- parte ---
titolo: Parte 2
titolo_en: Part 2
descrizione: Collegare N8N ai sistemi aziendali e gestire gli errori.
descrizione_en: Connecting N8N to business systems and handling failures.
raggiunto: 10
totale: 20
unita: lezioni
unita_en: lessons
```

Il sito mostra il titolo dell'argomento con l'avanzamento totale e una barra spessa, poi ogni parte con la sua percentuale, la sua quota e la sua barra sottile.

L'avanzamento totale è la somma dei `raggiunto` diviso la somma dei `totale`, quindi una parte più lunga pesa di più: 2 lezioni su 2 più 0 su 100 danno 2%, non 50%. Se le parti usano unità diverse il build ti avvisa, perché in quel caso la somma mescola grandezze diverse.

Le parti non hanno limite di numero. Una `descrizione` nel frontmatter dell'argomento è facoltativa e compare sopra le parti come introduzione. I file senza `--- parte ---` continuano a funzionare come prima, non c'è niente da convertire.

Se scrivi una sola `--- parte ---`, il sito mostra la forma semplice: il totale coinciderebbe con quella parte e la stessa percentuale comparirebbe due volte. Titolo, numeri e descrizione sono quelli della parte, il titolo mostrato è quello dell'argomento. Aggiungendo la seconda parte compare da sola la vista con l'avanzamento totale.

La riga dell'avanzamento totale mostra soltanto la percentuale, mai una quota o un'unità: le parti possono contare cose diverse (lezioni, video, capitoli) e sommarle in una sola etichetta non avrebbe senso.

### Colore della barra ed etichetta di sforzo

Due campi facoltativi, validi sia nel frontmatter dell'argomento sia dentro una `--- parte ---`.

```markdown
colore: "#7A3E9D"
sforzo: alto
```

`colore` cambia la barra di completamento e si scrive in esadecimale, con o senza abbreviazione (`#7A3E9D` o `#7A9`). Scritto nel frontmatter vale per la barra del totale e per tutte le parti che non ne indicano uno proprio; scritto dentro una parte vale solo per quella. Senza il campo la barra usa il blu del sito. Un valore che non è un esadecimale blocca il build.

`sforzo` aggiunge sotto al titolo una pastiglia colorata e accetta solo `alto`, `medio` o `basso`. I testi sono nei file delle lingue, chiavi `sforzo_alto`, `sforzo_medio` e `sforzo_basso`: oggi dicono "Più difficile del previsto", "Fattibile dai" e "La smarchiamo facilmente", in inglese "High effort", "Moderate effort" e "Low effort". Cambiali lì se vuoi altre formule. Il colore accompagna la lettura ma l'informazione sta nel testo, così resta chiara anche a chi i colori non li distingue.

## Aggiungere un libro

Crea `content/libri/titolo-libro.md`. Il nome del file senza `.md` è il nome del libro: lo usi in `content/libreria.md` per metterlo su una mensola. Usa solo minuscole, numeri e trattini e non cambiarlo dopo la pubblicazione. Il numero iniziale non serve più, perché l'ordine lo decide la libreria. Nei file che lo hanno viene ignorato: `07-greenlights.md` si chiama `greenlights`.

```markdown
---
titolo: Titolo del libro
titolo_en: Book title
autore: Nome Autore
autore_en: Author Name
voto: 4,5
copertina: /images/books/titolo.webp
copertina_en: /images/books/title.webp
pagine: 320
formato: standard
dorso_titolo: Titolo breve
dorso_colore: "#2F4F3E"
dorso_stile: grassetto
---

Nota facoltativa di una o due righe, mostrata sotto l'autore.

--- en ---

Optional one or two line note, shown under the author.
```

`titolo`, `autore`, `voto` e `copertina` sono obbligatori, tutti gli altri campi sono facoltativi.

La sezione Letture mostra i libri su una libreria in legno, disposti come scrivi in `content/libreria.md`. Un clic su un dorso o su una copertina apre la scheda del libro, descritta più sotto.

### Due edizioni, italiana e inglese

Vale la regola del resto del sito: nel sito inglese ogni campo con `_en` sostituisce quello italiano e, se manca, vale quello italiano. Così ogni libro può avere due titoli, due autori, due copertine, due link e due dorsi. Voto, pagine e formato sono unici, quindi la libreria ha la stessa disposizione nelle due lingue.

Il titolo sul dorso ha una regola in più. Nel sito inglese il dorso mostra `dorso_titolo_en`, altrimenti `titolo_en`, altrimenti il titolo italiano. Così un titolo breve scritto per l'edizione italiana non compare sul sito inglese.

Se un libro esiste solo in inglese, scrivi i dati inglesi nei campi senza `_en`: li usano entrambe le lingue. In quel caso aggiungi `dorso_lettura: discendente`.

### Voto

`voto` va da 0 a 5 a mezzi punti. Puoi scriverlo con il punto o con la virgola: `4`, `4.5`, `4,5`. Un valore come `4.3` blocca il build. Nella scheda il voto compare con le stelle, riempite fino alla mezza stella, e con il numero accanto. Il testo per i lettori di schermo riporta il voto esatto, per esempio "Valutazione 4,5 su 5".

### Dorso

`pagine` decide lo spessore del dorso: senza il campo vale 300. `formato` decide l'altezza e accetta `tascabile`, `standard` o `grande`: senza il campo vale `standard`.

`dorso_titolo` è il testo sul dorso: senza il campo compare il titolo. `dorso_colore` è il colore in esadecimale, anche abbreviato come `#7A9`. Senza il campo il build sceglie uno di 8 toni in base al nome del file, sempre lo stesso. Il testo sul dorso diventa chiaro o scuro da solo, quello con più contrasto.

`dorso_stile` accetta `normale`, `grassetto`, `corsivo` o `mono`, con i font del sito: senza il campo vale `grassetto`. `dorso_lettura` accetta `ascendente`, dal basso verso l'alto come nelle edizioni italiane, oppure `discendente`, dall'alto verso il basso come nelle edizioni inglesi. Senza il campo il sito italiano usa `ascendente` e quello inglese `discendente`.

Tutti i campi del dorso hanno la versione `_en` per l'edizione inglese.

### Link ad Amazon

`isbn` e `isbn_en` accettano 10 o 13 cifre, con o senza trattini. Il build controlla la cifra finale, che rileva ogni errore di battitura su una singola cifra: un ISBN sbagliato blocca la pubblicazione.

Dall'ISBN il build crea il link: amazon.it per `isbn`, amazon.com per `isbn_en`. Per i libri stampati il codice Amazon coincide con l'ISBN a 10 cifre, quindi il link si crea dagli ISBN a 10 cifre e da quelli a 13 che iniziano con 978. Per un ISBN che inizia con 979 il build ti avvisa: scrivi il link a mano in `amazon` o `amazon_en`.

Un link scritto a mano vince sempre sull'ISBN e deve iniziare con `https://`. Se c'è `copertina_en` ma manca il link inglese, il build ti avvisa e il sito inglese usa il link italiano.

### Scheda del libro

Ogni libro sulla mensola è un bottone. Il clic apre una scheda con copertina, titolo, autore, stelle, nota e il bottone "Vedi su Amazon". Il bottone compare solo se il libro ha un link, da `amazon` o da `isbn`; il testo del bottone è `libri_amazon` in `content/testi/`. Nel sito inglese la scheda usa titolo, autore, copertina e link dell'edizione inglese, secondo la regola dei campi `_en`.

Su telefono la scheda sale dal basso, da 680 px in su si apre al centro, come le schede dei progetti. Si chiude con la X, con Esc, con un clic fuori o con il tasto indietro del browser.

Aprendo la scheda l'indirizzo diventa `#libro-` più il nome del file, per esempio `mattiabaldinazzo.it/#libro-rework`. Quel link apre direttamente la scheda, con la libreria dietro: puoi mandarlo a qualcuno o metterlo in un post.

## Disporre la libreria

`content/libreria.md` decide come stanno i libri sulle mensole: ordine, vista e decorazioni. Ogni riga `--- mensola ---` apre una mensola nuova, come `--- parte ---` nei progressi.

```markdown
--- mensola ---
rework
scrum
la-mucca-viola: copertina
greenlights: disteso
lunica-regola: disteso
decorazione: vaso.webp, 60%
colloqui-con-se-stesso

--- mensola ---
decorazione: busto.webp, 85%
larte-della-guerra
padre-ricco-padre-povero
```

Una riga con il nome di un libro lo mette sulla mensola con il dorso dritto. Dopo i due punti puoi scrivere `copertina`, per mostrarlo di fronte, oppure `disteso`, per sdraiarlo. Più libri distesi di fila formano una pila e il primo che scrivi sta in cima.

`decorazione: vaso.webp, 60%` mette tra i libri un'immagine di `images/decorazioni/`, alta il 60% della mensola. Le regole per preparare le immagini sono in `images/decorazioni/LEGGIMI.md`.

Le righe che iniziano con `#` sono commenti. Un libro che non compare nel file finisce in fondo all'ultima mensola con il dorso dritto, e il build te lo segnala. Senza il file tutti i libri stanno su una mensola, in ordine di nome file.

Il build si ferma se un nome non corrisponde a nessun libro, se un libro compare due volte, se un'opzione è sconosciuta, se un separatore è scritto male o se manca l'immagine di una decorazione. Il messaggio indica la riga del file.

### Righe, Mostra altro e Mostra meno

All'apertura si vedono 3 righe della libreria. "Mostra altro" ne aggiunge 3 a ogni clic. "Mostra meno" compare dal primo clic, torna subito alle prime 3 righe e riporta in vista l'inizio della libreria. Con 3 righe o meno i bottoni non compaiono. Le soglie sono le costanti `RIGHE_VISIBILI` e `RIGHE_PER_CLIC` in `build.py`.

Su schermo largo una riga è una mensola. Una mensola larga 776 px contiene circa 27 dorsi da 300 pagine. Se scrivi più elementi di quanti ne entrano, la mensola va a capo su una riga in più e il build ti avvisa con la percentuale di riempimento. Una pila più alta della mensola viene divisa in pile vicine, sempre con un avviso. Su schermi più stretti le mensole vanno a capo da sole; senza JavaScript si vede tutta la libreria.

### Misure

Le misure sono costanti in `build.py`, in pixel da schermo largo. `ALTEZZE_FORMATO` dà l'altezza di tascabile, standard e grande. `SPESSORE_PER_PAGINA` trasforma le pagine in spessore, tra `SPESSORE_MINIMO` e `SPESSORE_MASSIMO`: 300 pagine fanno 26 px. Libri dello stesso formato hanno altezze leggermente diverse, calcolate dal nome del file, quindi identiche a ogni build. Una copertina esposta prende le proporzioni dall'immagine italiana, così occupa lo stesso spazio nelle due lingue. I colori del legno sono variabili in testa alla sezione Letture di `styles.css`.

## Cambiare la foto profilo

La foto della sezione "Chi sono" sta in `images/profilo/`, il nome del file è libero: il build usa l'unica immagine presente nella cartella. Per cambiarla elimina quella attuale, aggiungi la nuova e fai commit. Regole e formato consigliato sono in `images/profilo/LEGGIMI.md`. Con zero immagini o più di una il build fallisce e ti avvisa.

## Immagini

Progetti in `images/projects/` (webp, larghezza 880 px). Copertine in `images/books/` (webp, larghezza 440 px). Foto del profilo in `images/profilo/`. Decorazioni della libreria in `images/decorazioni/`, in webp o png con sfondo trasparente: le regole sono nel `LEGGIMI.md` della cartella. `tools/ottimizza-immagini.py` taglia i bordi trasparenti attorno all'oggetto, limita l'altezza a 440 px e converte in webp conservando la trasparenza; se il nome cambia, per esempio da `vaso.png` a `vaso.webp`, te lo scrive e va aggiornato in `content/libreria.md`. Se il markdown punta a un'immagine che non esiste, il build fallisce e te lo dice.

Accanto a ogni immagine c'è una versione ridotta con il suffisso della larghezza, per esempio `spotify-480.webp`: il sito le propone al browser con `srcset`, così su telefono viene scaricata solo la misura che serve. Quando aggiungi o sostituisci un'immagine, rigenera le versioni ridotte:

```bash
pip install pillow
python3 tools/ottimizza-immagini.py
```

Committa i file generati insieme all'originale. Se te ne dimentichi il sito funziona lo stesso, semplicemente scarica l'immagine grande anche sui telefoni. Il build non ha bisogno di Pillow: usa le versioni ridotte se le trova, altrimenti tira dritto.

## Pubblicazione

Push su `main`: il workflow esegue `python3 build.py`, genera `_site/` con le due lingue e pubblica su GitHub Pages. Se un file markdown ha errori (campo mancante, numero non valido, immagine inesistente) il build fallisce con l'elenco dei problemi e il sito online resta quello precedente. In Settings, Pages la source deve essere "GitHub Actions".

## Cose che il build fa da solo

L'anno finale del footer (`2020-...`) è quello del giorno in cui pubblichi, quindi non va aggiornato a mano. Il numero progressivo delle schede progetto, la percentuale dei progressi, la mappa delle lingue e la sitemap sono tutti calcolati dai contenuti.

`cv.pdf` nella radice è un segnaposto: sostituiscilo con il tuo curriculum vero mantenendo il nome del file.

## Anteprima locale

```bash
python3 build.py
python3 -m http.server 8000 --directory _site
```

Poi apri http://localhost:8000. Serve solo Python 3, nessuna dipendenza.

## Struttura

`content/` i contenuti in markdown (progetti, progressi, libri), la disposizione delle mensole in `content/libreria.md` e i testi dell'interfaccia in `content/testi/`. `templates/index.html` la struttura della pagina, unica per entrambe le lingue. `build.py` il generatore (solo libreria standard). `styles.css` e `main.js` stile e comportamenti; il CSS viene compresso e incorporato nella pagina dal build, così il browser non deve scaricare un secondo file prima di disegnare; il sorgente resta commentato, si riduce solo quello che viene spedito. `tools/` gli script di manutenzione. `fonts/` iA Writer Quattro S e Mono S più Parisienne ridotto alle lettere del monogramma M.B., tutti self-hosted con licenza SIL OFL. `images/` le immagini ottimizzate, con `images/profilo/` per la foto e `images/decorazioni/` per gli oggetti della libreria. `jet_converter/` tool indipendente, pubblicato così com'è. `_site/` output generato, non si committa.
