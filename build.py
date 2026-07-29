#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py
Genera il sito statico bilingue in _site/ a partire da:
  - templates/index.html    (struttura della pagina, con segnaposto {{...}})
  - content/testi/it.md     (testi fissi dell'interfaccia in italiano)
  - content/testi/en.md     (gli stessi testi in inglese, stesse chiavi)
  - content/progetti/*.md   (una scheda progetto per file, due lingue nel file)
  - content/libri/*.md      (un libro per file)
  - content/progressi/*.md  (un progresso per file, con barra di avanzamento)
  - images/profilo/         (una sola immagine: la foto in apertura di pagina)

Due lingue nello stesso file di contenuto:
  - nel frontmatter: titolo / titolo_en, descrizione / descrizione_en, ...
  - nel corpo: testo italiano, poi una riga "--- en ---", poi il testo inglese
Se la versione inglese manca, il sito inglese mostra il testo italiano e il
build stampa un avviso (non blocca la pubblicazione).

Risultato:
  _site/index.html          italiano
  _site/en/index.html       inglese

Nessuna dipendenza esterna: solo libreria standard di Python 3.
Uso:  python3 build.py
Anteprima locale:  python3 -m http.server 8000 --directory _site
"""

import datetime
import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
TEMPLATE = ROOT / "templates" / "index.html"
OUT = ROOT / "_site"

SITO = "https://mattiabaldinazzo.it"

# Lingue: (codice, sottocartella in _site). La prima e' quella predefinita.
LINGUE = [("it", ""), ("en", "en")]

# File e cartelle copiati cosi' come sono in _site/
STATIC_FILES = [
    "styles.css", "main.js", "favicon.svg", "favicon.ico",
    "robots.txt", "CNAME", "cv.pdf",
]
STATIC_DIRS = ["images", "fonts", "jet_converter"]

# Quanti elementi restano visibili prima del bottone "Mostra tutti"
LIBRI_VISIBILI = 4
PROGETTI_VISIBILI = 6
PROGRESSI_VISIBILI = 4

# Estensioni ammesse per la foto profilo
ESTENSIONI_FOTO = {".webp", ".jpg", ".jpeg", ".png"}

# Separatore che divide la parte italiana da quella inglese nel corpo
SEPARATORE_EN = re.compile(r"^\s*---\s*en\s*---\s*$", re.MULTILINE)

# Separatore che apre una sotto-parte dentro un progresso
SEPARATORE_PARTE = re.compile(r"^\s*---\s*parte\s*---\s*$", re.MULTILINE)

# Ordine dei filtri per le categorie note; le nuove vengono accodate
CATEGORIE_NOTE = ["personali", "lavorativi", "universitari"]

ERRORI = []
AVVISI = []

SIZES_LAVORI = "(min-width: 920px) 240px, (min-width: 600px) 370px, 92vw"
SIZES_LIBRI = "(min-width: 1024px) 120px, (min-width: 768px) 180px, (min-width: 600px) 240px, 45vw"
SIZES_FOTO = "(min-width: 860px) 244px, (min-width: 600px) 260px, 62vw"

# Larghezze alternative generate da tools/ottimizza-immagini.py, per cartella
VARIANTI = {
    "images/profilo": [480],
    "images/projects": [480],
    "images/books": [220],
}


def errore(msg):
    ERRORI.append(msg)


def avviso(msg):
    AVVISI.append(msg)


def esc(testo):
    return html.escape(str(testo), quote=True)


def comprimi_css(css):
    """Toglie commenti e spazi superflui dal foglio di stile prima di
    incorporarlo nella pagina. Il file sorgente resta commentato: qui si
    riduce solo quello che viene spedito al browser. Volutamente prudente:
    non tocca cio' che sta dentro le parentesi, dove uno spazio in meno
    romperebbe le espressioni calc()."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)      # via i commenti
    css = re.sub(r"\s*\n\s*", " ", css)                  # via gli a capo
    css = re.sub(r" {2,}", " ", css)                      # spazi ripetuti
    css = re.sub(r"\s*([{};,])\s*", r"\1", css)           # spazi attorno ai separatori
    css = re.sub(r";}", "}", css)                         # ultimo punto e virgola
    return css.strip()


# ------------------------------------------------------------------ immagini

def dimensioni_immagine(path):
    """Larghezza e altezza di webp, png o jpeg leggendo l'intestazione del file.
    Serve per scrivere width e height nel markup (evita gli scarti di layout)
    e per costruire il srcset. Nessuna libreria esterna."""
    try:
        with open(path, "rb") as f:
            testa = f.read(32)
            if testa[:4] == b"RIFF" and testa[8:12] == b"WEBP":
                chunk = testa[12:16]
                with open(path, "rb") as f2:
                    dati = f2.read(64)
                if chunk == b"VP8X":
                    larg = int.from_bytes(dati[24:27], "little") + 1
                    alt = int.from_bytes(dati[27:30], "little") + 1
                    return larg, alt
                if chunk == b"VP8L":
                    b = dati[21:26]
                    v = int.from_bytes(b[:4], "little")
                    return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
                if chunk == b"VP8 ":
                    larg = int.from_bytes(dati[26:28], "little") & 0x3FFF
                    alt = int.from_bytes(dati[28:30], "little") & 0x3FFF
                    return larg, alt
            if testa[:8] == b"\x89PNG\r\n\x1a\n":
                return (int.from_bytes(testa[16:20], "big"),
                        int.from_bytes(testa[20:24], "big"))
            if testa[:2] == b"\xff\xd8":
                with open(path, "rb") as f2:
                    f2.read(2)
                    while True:
                        marcatore = f2.read(2)
                        if len(marcatore) < 2 or marcatore[0] != 0xFF:
                            break
                        lunghezza = int.from_bytes(f2.read(2), "big")
                        if marcatore[1] in (0xC0, 0xC1, 0xC2, 0xC3):
                            f2.read(1)
                            alt = int.from_bytes(f2.read(2), "big")
                            larg = int.from_bytes(f2.read(2), "big")
                            return larg, alt
                        f2.read(lunghezza - 2)
    except (OSError, IndexError, ValueError):
        pass
    return 0, 0


def tag_immagine(percorso, alt, sizes, extra=""):
    """<img> con srcset, misure e attributi giusti. Se le varianti ridotte non
    esistono usa semplicemente l'immagine originale."""
    if not percorso:
        return ""
    rel = percorso.lstrip("/")
    file = ROOT / rel
    larg, altezza = dimensioni_immagine(file)
    cartella = str(pathlib_parent(rel))
    fonti = []
    for w in VARIANTI.get(cartella, []):
        variante = file.with_name("%s-%d.webp" % (file.stem, w))
        if variante.exists() and (not larg or w < larg):
            fonti.append(("/%s/%s" % (cartella, variante.name), w))
    attributi = ['src="%s"' % esc(percorso), 'alt="%s"' % esc(alt)]
    if fonti and larg:
        fonti.append((percorso, larg))
        attributi.append('srcset="%s"' % esc(", ".join("%s %dw" % (p, w) for p, w in fonti)))
        attributi.append('sizes="%s"' % esc(sizes))
    if larg and altezza:
        attributi.append('width="%d" height="%d"' % (larg, altezza))
    if extra:
        attributi.append(extra)
    return "<img %s>" % " ".join(attributi)


def pathlib_parent(rel):
    return Path(rel).parent


# ---------------------------------------------------------------- frontmatter

def leggi_md(path):
    """Ritorna (meta: dict, corpo: str) da un file markdown con frontmatter ---.
    Le righe che iniziano con # dentro il frontmatter sono commenti."""
    testo = path.read_text(encoding="utf-8")
    meta, corpo = {}, testo
    if testo.lstrip().startswith("---"):
        parti = testo.lstrip().split("---", 2)
        if len(parti) == 3:
            _, fm, corpo = parti
            for riga in fm.strip().splitlines():
                if riga.strip().startswith("#") or not riga.strip():
                    continue
                if ":" in riga:
                    k, v = riga.split(":", 1)
                    meta[k.strip().lower()] = v.strip().strip('"').strip("'")
    return meta, corpo.strip()


def blocco_campi(testo):
    """Legge righe 'chiave: valore' e le restituisce come dizionario.
    Serve alle sotto-parti dei progressi, scritte con la stessa sintassi
    del frontmatter ma dentro il corpo del file."""
    campi = {}
    for riga in testo.strip().splitlines():
        riga = riga.strip()
        if not riga or riga.startswith("#"):
            continue
        if ":" in riga:
            k, v = riga.split(":", 1)
            campi[k.strip().lower()] = v.strip().strip('"').strip("'")
    return campi


def campo(meta, chiave, lingua):
    """Valore del campo nella lingua richiesta, con ripiego sull'italiano."""
    if lingua == "it":
        return meta.get(chiave, "")
    valore = meta.get(chiave + "_en", "")
    return valore if valore else meta.get(chiave, "")


def manca_traduzione(meta, chiave):
    return bool(meta.get(chiave)) and not meta.get(chiave + "_en")


def dividi_corpo(corpo):
    """Ritorna (corpo_it, corpo_en). Senza separatore, l'inglese ripiega sull'italiano."""
    parti = SEPARATORE_EN.split(corpo, maxsplit=1)
    if len(parti) == 2:
        return parti[0].strip(), parti[1].strip()
    return corpo.strip(), ""


# ------------------------------------------------------------------- markdown

def inline_md(s):
    """Markdown inline: `codice`, **grassetto**, *corsivo*, [testo](url)."""
    s = esc(s)
    scorta = []

    def _code(m):
        scorta.append("<code>" + m.group(1) + "</code>")
        return "\x00%d\x00" % (len(scorta) - 1)

    s = re.sub(r"`([^`]+)`", _code, s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)

    def _link(m):
        url = m.group(2)
        extra = ' target="_blank" rel="noopener"' if url.startswith("http") else ""
        return '<a href="%s"%s>%s</a>' % (url, extra, m.group(1))

    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", _link, s)
    for i, c in enumerate(scorta):
        s = s.replace("\x00%d\x00" % i, c)
    return s


def md_to_html(md):
    """Markdown a blocchi: paragrafi, titoli ##/###, liste - e 1., righe vuote."""
    righe = md.strip().splitlines()
    out, par, lista, tag_lista = [], [], [], None

    def chiudi_par():
        nonlocal par
        if par:
            out.append("<p>" + inline_md(" ".join(par)) + "</p>")
            par = []

    def chiudi_lista():
        nonlocal lista, tag_lista
        if lista:
            voci = "".join("<li>" + inline_md(v) + "</li>" for v in lista)
            out.append("<%s>%s</%s>" % (tag_lista, voci, tag_lista))
            lista, tag_lista = [], None

    for grezza in righe:
        riga = grezza.rstrip()
        if not riga.strip():
            chiudi_par(); chiudi_lista(); continue
        m = re.match(r"^(#{2,4})\s+(.*)", riga)
        if m:
            chiudi_par(); chiudi_lista()
            livello = min(len(m.group(1)) + 1, 5)   # ## -> h3, ### -> h4
            out.append("<h%d>%s</h%d>" % (livello, inline_md(m.group(2)), livello))
            continue
        m = re.match(r"^\s*[-*]\s+(.*)", riga)
        if m:
            chiudi_par()
            if tag_lista not in (None, "ul"):
                chiudi_lista()
            tag_lista = "ul"; lista.append(m.group(1)); continue
        m = re.match(r"^\s*\d+[.)]\s+(.*)", riga)
        if m:
            chiudi_par()
            if tag_lista not in (None, "ol"):
                chiudi_lista()
            tag_lista = "ol"; lista.append(m.group(1)); continue
        chiudi_lista()
        par.append(riga.strip())
    chiudi_par(); chiudi_lista()
    return "\n".join(out)


# ------------------------------------------------------------- testi fissi

def carica_testi():
    """Carica content/testi/<codice>.md e verifica che le chiavi coincidano."""
    testi = {}
    for codice, _ in LINGUE:
        f = CONTENT / "testi" / ("%s.md" % codice)
        if not f.exists():
            errore("manca il file dei testi content/testi/%s.md" % codice)
            continue
        meta, _corpo = leggi_md(f)
        if not meta:
            errore("content/testi/%s.md: frontmatter vuoto o malformato" % codice)
        testi[codice] = meta

    if len(testi) == len(LINGUE):
        base = LINGUE[0][0]
        chiavi_base = set(testi[base])
        for codice, _ in LINGUE[1:]:
            mancanti = sorted(chiavi_base - set(testi[codice]))
            in_piu = sorted(set(testi[codice]) - chiavi_base)
            for k in mancanti:
                errore("content/testi/%s.md: manca la chiave '%s'" % (codice, k))
            for k in in_piu:
                errore("content/testi/%s.md: chiave '%s' assente in %s.md" % (codice, k, base))
    return testi


# ------------------------------------------------------------------ contenuti

def slug_da_file(path):
    base = re.sub(r"^\d+[-_]?", "", path.stem)
    return base.lower()


def verifica_immagine(percorso, origine):
    if not percorso:
        return
    if not (ROOT / percorso.lstrip("/")).exists():
        errore("%s: immagine non trovata: %s" % (origine.name, percorso))


def numero(meta, chiave, origine):
    grezzo = meta.get(chiave, "")
    try:
        return float(grezzo)
    except ValueError:
        errore("%s: '%s' deve essere un numero (trovato: %r)" % (origine.name, chiave, grezzo))
        return None


def testo_numero(x):
    return "%d" % x if float(x).is_integer() else "%g" % x


def carica_progetti():
    cartella = CONTENT / "progetti"
    progetti = []
    if not cartella.exists():
        return progetti
    for f in sorted(cartella.glob("*.md")):
        meta, corpo = leggi_md(f)
        for c in ("titolo", "categoria", "descrizione"):
            if not meta.get(c):
                errore("%s: manca il campo '%s'" % (f.name, c))
        slug = slug_da_file(f)
        if not re.fullmatch(r"[a-z0-9-]+", slug or ""):
            errore("%s: nome file non valido, usa solo minuscole, numeri e trattini" % f.name)
        verifica_immagine(meta.get("immagine"), f)
        corpo_it, corpo_en = dividi_corpo(corpo)
        for c in ("titolo", "descrizione"):
            if manca_traduzione(meta, c):
                avviso("%s: manca '%s_en', in inglese uso il testo italiano" % (f.name, c))
        if corpo_it and not corpo_en:
            avviso("%s: manca la parte dopo '--- en ---', la scheda inglese usa il testo italiano" % f.name)
        progetti.append({
            "slug": slug,
            "meta": meta,
            "categoria": meta.get("categoria", "").lower(),
            "immagine": meta.get("immagine", ""),
            "link": meta.get("link", ""),
            "corpo": {"it": corpo_it, "en": corpo_en or corpo_it},
        })
    visti = set()
    for p in progetti:
        if p["slug"] in visti:
            errore("slug duplicato tra i progetti: %s" % p["slug"])
        visti.add(p["slug"])
    return progetti


def carica_libri():
    cartella = CONTENT / "libri"
    libri = []
    if not cartella.exists():
        return libri
    for f in sorted(cartella.glob("*.md")):
        meta, corpo = leggi_md(f)
        for c in ("titolo", "autore", "voto", "copertina"):
            if not meta.get(c):
                errore("%s: manca il campo '%s'" % (f.name, c))
        try:
            voto = int(meta.get("voto", "0"))
            if not 1 <= voto <= 5:
                raise ValueError
        except ValueError:
            errore("%s: 'voto' deve essere un intero da 1 a 5" % f.name)
            voto = 5
        verifica_immagine(meta.get("copertina"), f)
        nota_it, nota_en = dividi_corpo(corpo)
        if manca_traduzione(meta, "titolo"):
            avviso("%s: manca 'titolo_en', in inglese uso il titolo italiano" % f.name)
        libri.append({
            "meta": meta,
            "autore": meta.get("autore", ""),
            "voto": voto,
            "copertina": meta.get("copertina", ""),
            "nota": {"it": nota_it, "en": nota_en or nota_it},
        })
    return libri


COLORE_HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
SFORZI = ("alto", "medio", "basso")


def leggi_colore(campi, origine, etichetta):
    """Colore della barra, scritto in esadecimale. Vuoto significa: usa il
    colore d'accento del sito."""
    grezzo = campi.get("colore", "").strip()
    if not grezzo:
        return ""
    if not COLORE_HEX.match(grezzo):
        errore("%s%s: 'colore' deve essere un esadecimale tipo #1F3A5F (trovato: %r)"
               % (origine.name, etichetta, grezzo))
        return ""
    return grezzo


def leggi_sforzo(campi, origine, etichetta):
    """Quanto costa fatica: alto, medio o basso. Vuoto significa: nessuna
    etichetta."""
    grezzo = campi.get("sforzo", "").strip().lower()
    if not grezzo:
        return ""
    if grezzo not in SFORZI:
        errore("%s%s: 'sforzo' puo' essere solo %s (trovato: %r)"
               % (origine.name, etichetta, " / ".join(SFORZI), grezzo))
        return ""
    return grezzo


def leggi_avanzamento(campi, origine, etichetta):
    """Valida raggiunto/totale e restituisce (raggiunto, totale) oppure None."""
    raggiunto = numero(campi, "raggiunto", origine)
    totale = numero(campi, "totale", origine)
    if raggiunto is None or totale is None:
        return None
    if totale <= 0:
        errore("%s%s: 'totale' deve essere maggiore di zero" % (origine.name, etichetta))
        return None
    if not 0 <= raggiunto <= totale:
        errore("%s%s: 'raggiunto' deve stare tra 0 e 'totale' (%s)"
               % (origine.name, etichetta, testo_numero(totale)))
        return None
    return raggiunto, totale


def carica_progressi():
    """Un progresso puo' essere semplice oppure diviso in sotto-parti.

    Semplice: descrizione, raggiunto, totale e unita' stanno nel frontmatter,
    esattamente come prima. Nulla da cambiare nei file gia' scritti.

    Con sotto-parti: il frontmatter tiene solo il titolo dell'argomento e ogni
    parte si apre nel corpo con una riga '--- parte ---', seguita dagli stessi
    campi. L'avanzamento complessivo e' la somma dei raggiunti diviso la somma
    dei totali, quindi una parte piu' lunga pesa di piu'.
    """
    cartella = CONTENT / "progressi"
    voci = []
    if not cartella.exists():
        return voci
    for f in sorted(cartella.glob("*.md")):
        meta, corpo = leggi_md(f)
        if not meta.get("titolo"):
            errore("%s: manca il campo 'titolo'" % f.name)
        if manca_traduzione(meta, "titolo"):
            avviso("%s: manca 'titolo_en', in inglese uso il titolo italiano" % f.name)

        pezzi = SEPARATORE_PARTE.split(corpo)
        blocchi_parte = [b for b in pezzi[1:] if b.strip()]

        # ---------------------------------------- progresso con sotto-parti
        if blocchi_parte:
            parti = []
            somma_raggiunto = somma_totale = 0.0
            unita_viste = set()
            for n, grezzo in enumerate(blocchi_parte, start=1):
                campi = blocco_campi(grezzo)
                etichetta = ", parte %d" % n
                for c in ("titolo", "descrizione", "raggiunto", "totale"):
                    if not campi.get(c):
                        errore("%s%s: manca il campo '%s'" % (f.name, etichetta, c))
                valori = leggi_avanzamento(campi, f, etichetta)
                if valori is None:
                    continue
                raggiunto, totale = valori
                for c in ("titolo", "descrizione"):
                    if manca_traduzione(campi, c):
                        avviso("%s%s: manca '%s_en', in inglese uso il testo italiano"
                               % (f.name, etichetta, c))
                somma_raggiunto += raggiunto
                somma_totale += totale
                unita_viste.add(campi.get("unita", ""))
                parti.append({
                    "meta": campi,
                    "percento": round(raggiunto / totale * 100),
                    "quota": "%s/%s" % (testo_numero(raggiunto), testo_numero(totale)),
                    "colore": leggi_colore(campi, f, etichetta) or leggi_colore(meta, f, ""),
                    "sforzo": leggi_sforzo(campi, f, etichetta),
                })
            if not parti or somma_totale <= 0:
                continue
            if len(unita_viste) > 1:
                avviso("%s: le sotto-parti usano unita' diverse (%s), quindi la somma "
                       "che calcolo per l'avanzamento totale mescola grandezze diverse"
                       % (f.name, ", ".join(sorted(u or "senza unita'" for u in unita_viste))))
            # Una sola parte non ha nulla da riassumere: il totale
            # coinciderebbe con la parte stessa e il numero comparirebbe due
            # volte. In quel caso mostro la forma semplice, con il titolo
            # dell'argomento e i dati della parte.
            if len(parti) == 1:
                unica = parti[0]
                unica["meta"]["titolo"] = meta.get("titolo", "")
                unica["meta"]["titolo_en"] = meta.get("titolo_en", "")
                unica["parti"] = []
                voci.append(unica)
                continue
            voci.append({
                "meta": meta,
                "percento": round(somma_raggiunto / somma_totale * 100),
                "quota": "",
                "parti": parti,
                "colore": leggi_colore(meta, f, ""),
                "sforzo": leggi_sforzo(meta, f, ""),
            })
            continue

        # ---------------------------------------- progresso semplice
        for c in ("descrizione", "raggiunto", "totale"):
            if not meta.get(c):
                errore("%s: manca il campo '%s'" % (f.name, c))
        valori = leggi_avanzamento(meta, f, "")
        if valori is None:
            continue
        raggiunto, totale = valori
        if manca_traduzione(meta, "descrizione"):
            avviso("%s: manca 'descrizione_en', in inglese uso il testo italiano" % f.name)
        voci.append({
            "meta": meta,
            "percento": round(raggiunto / totale * 100),
            "quota": "%s/%s" % (testo_numero(raggiunto), testo_numero(totale)),
            "parti": [],
            "colore": leggi_colore(meta, f, ""),
            "sforzo": leggi_sforzo(meta, f, ""),
        })
    return voci


def trova_foto_profilo():
    """In images/profilo deve esserci una sola immagine; il nome e' libero."""
    cartella = ROOT / "images" / "profilo"
    if not cartella.exists():
        errore("manca la cartella images/profilo con la foto in apertura di pagina")
        return ""
    # le versioni ridotte (nome-480.webp) sono generate dal tool, non contano
    foto = sorted(p.name for p in cartella.iterdir()
                  if p.is_file() and p.suffix.lower() in ESTENSIONI_FOTO
                  and not re.search(r"-\d+$", p.stem))
    if not foto:
        errore("images/profilo: nessuna immagine trovata (webp, jpg, jpeg o png)")
        return ""
    if len(foto) > 1:
        errore("images/profilo: piu' di un'immagine (%s). Lasciane una sola." % ", ".join(foto))
    return "/images/profilo/" + foto[0]


# -------------------------------------------------------------------- render

def render_filtri(progetti, T):
    presenti = {p["categoria"] for p in progetti if p["categoria"]}
    ordinate = [c for c in CATEGORIE_NOTE if c in presenti]
    ordinate += sorted(presenti - set(CATEGORIE_NOTE))
    voci = ['<button class="filter is-active" type="button" data-filter="tutti" aria-pressed="true">%s</button>'
            % esc(T["filtro_tutti"])]
    for slug in ordinate:
        voci.append('<button class="filter" type="button" data-filter="%s" aria-pressed="false">%s</button>'
                    % (esc(slug), esc(etichetta_categoria(slug, T))))
    return "\n          ".join(voci)


def etichetta_categoria(slug, T):
    return T.get("categoria_" + slug, slug.capitalize())


def render_progetti(progetti, lingua, T):
    schede = []
    for i, p in enumerate(progetti, start=1):
        titolo = campo(p["meta"], "titolo", lingua)
        descrizione = campo(p["meta"], "descrizione", lingua)
        if p["immagine"]:
            media = ('<span class="work-media">%s</span>'
                     % tag_immagine(p["immagine"], titolo, SIZES_LAVORI,
                                    'loading="lazy" decoding="async"'))
        else:
            media = ('<span class="work-media work-media--text"><span aria-hidden="true">%s</span></span>'
                     % esc(titolo))
        if p["corpo"][lingua]:
            etichetta = T["lavori_dettaglio"]
        else:
            etichetta = campo(p["meta"], "link_testo", lingua) or T["lavori_apri"]
        corpo_scheda = (
            '<span class="work-body">'
            '<span class="work-index" aria-hidden="true">%02d</span>'
            '<span class="work-name">%s</span>'
            '<span class="work-desc">%s</span>'
            '<span class="work-foot"><span class="work-tag">%s</span>'
            '<span class="work-link">%s</span></span>'
            '</span>' % (i, esc(titolo), esc(descrizione),
                         esc(etichetta_categoria(p["categoria"], T)), esc(etichetta))
        )
        if p["corpo"][lingua]:
            scheda = ('<button class="work-card" type="button" data-modal="%s" aria-haspopup="dialog">%s%s</button>'
                      % (esc(p["slug"]), media, corpo_scheda))
        elif p["link"]:
            scheda = ('<a class="work-card" href="%s" target="_blank" rel="noopener">%s%s</a>'
                      % (esc(p["link"]), media, corpo_scheda))
        else:
            scheda = '<div class="work-card work-card--static">%s%s</div>' % (media, corpo_scheda)
        nascosto = " is-hidden" if i > PROGETTI_VISIBILI else ""
        schede.append('<li class="work reveal%s" data-category="%s">%s</li>'
                      % (nascosto, esc(p["categoria"]), scheda))
    return "\n\n          ".join(schede)


def render_modali(progetti, lingua, T):
    modali = []
    for p in progetti:
        if not p["corpo"][lingua]:
            continue
        corpo_html = md_to_html(p["corpo"][lingua])
        if p["link"]:
            testo_link = campo(p["meta"], "link_testo", lingua) or T["lavori_apri"]
            corpo_html += ('\n<p class="modal-cta"><a class="btn btn-primary" href="%s" target="_blank" rel="noopener">%s</a></p>'
                           % (esc(p["link"]), esc(testo_link)))
        modali.append(
            '<div class="modal" id="modal-%(slug)s" hidden>\n'
            '    <div class="modal-backdrop" data-close></div>\n'
            '    <div class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="modal-%(slug)s-title">\n'
            '      <header class="modal-head">\n'
            '        <h2 id="modal-%(slug)s-title">%(titolo)s</h2>\n'
            '        <button class="modal-close" type="button" data-close aria-label="%(chiudi)s">\n'
            '          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>\n'
            '        </button>\n'
            '      </header>\n'
            '      <div class="modal-body">\n%(corpo)s\n      </div>\n'
            '    </div>\n'
            '  </div>' % {"slug": esc(p["slug"]),
                          "titolo": esc(campo(p["meta"], "titolo", lingua)),
                          "chiudi": esc(T["modale_chiudi"]),
                          "corpo": corpo_html}
        )
    return "\n\n  ".join(modali)


def render_toggle_progetti(progetti, T):
    if len(progetti) <= PROGETTI_VISIBILI:
        return ""
    return ('<div class="works-more reveal">\n'
            '          <button class="btn btn-ghost" type="button" data-works-toggle aria-expanded="false"\n'
            '                  data-limite="%d" data-testo-tutti="%s" data-testo-meno="%s">%s</button>\n'
            '        </div>' % (PROGETTI_VISIBILI, esc(T["lavori_mostra_tutti"]),
                                esc(T["lavori_mostra_meno"]), esc(T["lavori_mostra_tutti"])))


def render_libri(libri, lingua, T):
    voci = []
    for i, b in enumerate(libri):
        titolo = campo(b["meta"], "titolo", lingua)
        stelle = "&#9733;" * b["voto"] + "&#9734;" * (5 - b["voto"])
        nascosto = " is-hidden" if i >= LIBRI_VISIBILI else ""
        nota = ('<p class="book-note">%s</p>' % inline_md(b["nota"][lingua])) if b["nota"][lingua] else ""
        voci.append(
            '<li class="book reveal%s">\n'
            '            %s\n'
            '            <div class="book-info">\n'
            '              <p class="book-rating"><span class="visually-hidden">%s</span>'
            '<span aria-hidden="true">%s</span></p>\n'
            '              <h3 class="book-title">%s</h3>\n'
            '              <p class="book-author">%s</p>\n%s'
            '            </div>\n'
            '          </li>' % (nascosto,
                                tag_immagine(b["copertina"],
                                             "%s %s" % (T["libri_copertina"], titolo),
                                             SIZES_LIBRI, 'loading="lazy" decoding="async"'),
                                esc(T["libri_voto"] % b["voto"]), stelle,
                                esc(titolo), esc(b["autore"]), nota)
        )
    return "\n          ".join(voci)


def render_toggle_libri(libri, T):
    if len(libri) <= LIBRI_VISIBILI:
        return ""
    return ('<div class="reads-more reveal">\n'
            '          <button class="btn btn-ghost" type="button" data-books-toggle aria-expanded="false"\n'
            '                  data-testo-tutti="%s" data-testo-meno="%s">%s</button>\n'
            '        </div>' % (esc(T["libri_mostra_tutti"]), esc(T["libri_mostra_meno"]),
                                esc(T["libri_mostra_tutti"])))


def quota_con_unita(voce, lingua):
    """Es. '5/10 lezioni'."""
    quota = voce["quota"]
    unita = campo(voce["meta"], "unita", lingua)
    return quota + " " + unita if unita else quota


def barra(percento, etichetta, colore="", piccola=False):
    stile = "--p:%.2f" % (percento / 100.0)
    if colore:
        stile += ";--barra:%s" % colore
    return ('<div class="progress-track%(sm)s" role="progressbar" aria-valuemin="0" '
            'aria-valuemax="100" aria-valuenow="%(pct)d" aria-label="%(lab)s: %(pct)d%%">'
            '<span class="progress-fill" style="%(stile)s"></span></div>'
            % {"sm": " progress-track--sm" if piccola else "", "pct": percento,
               "lab": esc(etichetta), "stile": esc(stile)})


def etichetta_sforzo(sforzo, T):
    """Pastiglia colorata che dice quanta fatica costa. Il colore da solo non
    basta a chi non lo distingue, quindi l'informazione sta nel testo."""
    if not sforzo:
        return ""
    return ('<p class="progress-effort progress-effort--%s">%s</p>\n'
            % (sforzo, esc(T["sforzo_" + sforzo])))


def render_progressi(voci, lingua, T):
    righe = []
    for i, v in enumerate(voci, start=1):
        titolo = campo(v["meta"], "titolo", lingua)
        nascosto = " is-hidden" if i > PROGRESSI_VISIBILI else ""

        if v["parti"]:
            parti_html = []
            for parte in v["parti"]:
                titolo_parte = campo(parte["meta"], "titolo", lingua)
                parti_html.append(
                    '<li class="progress-part">\n'
                    '                <div class="progress-head">\n'
                    '                  <h4 class="progress-part-title">%(titolo)s</h4>\n'
                    '                  <p class="progress-value"><span class="progress-quota">%(quota)s</span>'
                    '<span class="progress-percent">%(pct)d%%</span></p>\n'
                    '                </div>\n'
                    '                %(sforzo)s'
                    '<p class="progress-desc">%(desc)s</p>\n'
                    '                %(barra)s\n'
                    '              </li>'
                    % {"titolo": esc(titolo_parte),
                       "quota": esc(quota_con_unita(parte, lingua)),
                       "pct": parte["percento"],
                       "sforzo": etichetta_sforzo(parte["sforzo"], T),
                       "desc": esc(campo(parte["meta"], "descrizione", lingua)),
                       "barra": barra(parte["percento"], "%s, %s" % (titolo, titolo_parte),
                                      parte["colore"], piccola=True)}
                )
            intro = campo(v["meta"], "descrizione", lingua)
            righe.append(
                '<li class="progress progress--gruppo reveal%(nascosto)s">\n'
                '            <div class="progress-head">\n'
                '              <h3 class="progress-title">%(titolo)s</h3>\n'
                '              <p class="progress-value"><span class="progress-quota">%(totale)s</span>'
                '<span class="progress-percent">%(pct)d%%</span></p>\n'
                '            </div>\n'
                '            %(sforzo)s'
                '%(intro)s'
                '            %(barra)s\n'
                '            <ol class="progress-parts">\n'
                '              %(parti)s\n'
                '            </ol>\n'
                '          </li>'
                % {"nascosto": nascosto, "titolo": esc(titolo),
                   "totale": esc(T["progressi_totale"]), "pct": v["percento"],
                   "sforzo": etichetta_sforzo(v["sforzo"], T),
                   "intro": ('            <p class="progress-desc">%s</p>\n' % esc(intro)) if intro else "",
                   "barra": barra(v["percento"], "%s, %s" % (titolo, T["progressi_totale"]), v["colore"]),
                   "parti": "\n              ".join(parti_html)}
            )
            continue

        righe.append(
            '<li class="progress reveal%(nascosto)s">\n'
            '            <div class="progress-head">\n'
            '              <h3 class="progress-title">%(titolo)s</h3>\n'
            '              <p class="progress-value"><span class="progress-quota">%(quota)s</span>'
            '<span class="progress-percent">%(pct)d%%</span></p>\n'
            '            </div>\n'
            '            %(sforzo)s'
            '<p class="progress-desc">%(desc)s</p>\n'
            '            %(barra)s\n'
            '          </li>'
            % {"nascosto": nascosto, "titolo": esc(titolo),
               "quota": esc(quota_con_unita(v, lingua)), "pct": v["percento"],
               "sforzo": etichetta_sforzo(v["sforzo"], T),
               "desc": esc(campo(v["meta"], "descrizione", lingua)),
               "barra": barra(v["percento"], titolo, v["colore"])}
        )
    return "\n          ".join(righe)


def render_toggle_progressi(voci, T):
    if len(voci) <= PROGRESSI_VISIBILI:
        return ""
    return ('<div class="progress-more reveal">\n'
            '          <button class="btn btn-ghost" type="button" data-progress-toggle aria-expanded="false"\n'
            '                  data-testo-tutti="%s" data-testo-meno="%s">%s</button>\n'
            '        </div>' % (esc(T["progressi_mostra_tutti"]), esc(T["progressi_mostra_meno"]),
                                esc(T["progressi_mostra_tutti"])))


# --------------------------------------------------------------------- build

def costruisci_pagina(modello, lingua, sottocartella, testi, progetti, libri, progressi, foto):
    T = testi[lingua]
    prefisso = "/" if not sottocartella else "/%s/" % sottocartella
    altro_codice = T["altra_lingua_codice"]
    altro_prefisso = "/" if altro_codice == LINGUE[0][0] else "/%s/" % altro_codice

    stili = comprimi_css((ROOT / "styles.css").read_text(encoding="utf-8"))
    foto_tag = tag_immagine(foto, "Mattia Baldinazzo", SIZES_FOTO,
                            'loading="lazy" decoding="async"')
    # Nessun precaricamento dell'immagine: la foto sta dentro "Chi sono",
    # sotto la prima schermata, quindi anticiparla ruberebbe banda al testo
    # che invece si vede subito.
    preload = ""

    valori = {
        "LANG": lingua,
        "STILI": stili,
        "PRELOAD_FOTO": preload,
        "FOTO_TAG": foto_tag,
        "URL_PAGINA": SITO + prefisso,
        "URL_IT": SITO + "/",
        "URL_EN": SITO + "/en/",
        "URL_ALTRA_LINGUA": altro_prefisso,
        "FOTO_PROFILO": foto,
        "FILTERS": render_filtri(progetti, T),
        "WORKS": render_progetti(progetti, lingua, T),
        "WORKS_MORE": render_toggle_progetti(progetti, T),
        "ANNO": str(datetime.date.today().year),
        "MODALS": render_modali(progetti, lingua, T),
        "PROGRESS": render_progressi(progressi, lingua, T),
        "PROGRESS_MORE": render_toggle_progressi(progressi, T),
        "BOOKS": render_libri(libri, lingua, T),
        "BOOKS_MORE": render_toggle_libri(libri, T),
        "LAVORI_INTRO": inline_md(T["lavori_intro"]),
    }
    # tutte le chiavi dei testi diventano segnaposto in maiuscolo: T_NAV_LAVORI ecc.
    for chiave, testo in T.items():
        valori["T_" + chiave.upper()] = esc(testo)

    pagina = modello
    for chiave, valore in valori.items():
        pagina = pagina.replace("{{%s}}" % chiave, str(valore))

    residui = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", pagina)))
    if residui:
        errore("template: segnaposto senza valore in %s: %s" % (lingua, ", ".join(residui)))
    return pagina


def scrivi_sitemap():
    voci = "\n".join(
        '  <url>\n'
        '    <loc>%s%s</loc>\n'
        '    <xhtml:link rel="alternate" hreflang="it" href="%s/"/>\n'
        '    <xhtml:link rel="alternate" hreflang="en" href="%s/en/"/>\n'
        '    <changefreq>monthly</changefreq>\n'
        '    <priority>1.0</priority>\n'
        '  </url>' % (SITO, "/" if not sub else "/%s/" % sub, SITO, SITO)
        for _, sub in LINGUE
    )
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + voci + "\n</urlset>\n", encoding="utf-8")


def main():
    if not TEMPLATE.exists():
        print("Errore: manca templates/index.html", file=sys.stderr)
        sys.exit(1)

    testi = carica_testi()
    progetti = carica_progetti()
    libri = carica_libri()
    progressi = carica_progressi()
    foto = trova_foto_profilo()

    pagine = {}
    if not ERRORI:
        modello = TEMPLATE.read_text(encoding="utf-8")
        for lingua, sottocartella in LINGUE:
            pagine[lingua] = (sottocartella,
                              costruisci_pagina(modello, lingua, sottocartella, testi,
                                                progetti, libri, progressi, foto))

    if ERRORI:
        print("Build fallita. Correggi questi problemi:", file=sys.stderr)
        for e in ERRORI:
            print("  - " + e, file=sys.stderr)
        sys.exit(1)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    for lingua, (sottocartella, pagina) in pagine.items():
        cartella = OUT / sottocartella if sottocartella else OUT
        cartella.mkdir(parents=True, exist_ok=True)
        (cartella / "index.html").write_text(pagina, encoding="utf-8")

    for nome in STATIC_FILES:
        src = ROOT / nome
        if src.exists():
            shutil.copy2(src, OUT / nome)
    for nome in STATIC_DIRS:
        src = ROOT / nome
        if src.exists():
            shutil.copytree(src, OUT / nome)
    scrivi_sitemap()

    if AVVISI:
        print("Avvisi (il sito viene pubblicato lo stesso):")
        for a in AVVISI:
            print("  ! " + a)

    n_modali = sum(1 for p in progetti if p["corpo"]["it"])
    print("Sito generato in _site/")
    print("  lingue: %s" % ", ".join("%s -> /%s" % (c, s + "/" if s else "") for c, s in LINGUE))
    print("  progetti: %d (%d con scheda di dettaglio)" % (len(progetti), n_modali))
    print("  progressi: %d" % len(progressi))
    print("  libri: %d" % len(libri))
    print("  foto profilo: %s" % foto)


if __name__ == "__main__":
    main()
