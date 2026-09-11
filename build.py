#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py
Genera il sito statico bilingue in _site/ a partire da:
  - templates/index.html    (struttura della pagina, con segnaposto {{...}})
  - content/testi/it.md     (testi fissi dell'interfaccia in italiano)
  - content/testi/en.md     (gli stessi testi in inglese, stesse chiavi)
  - content/progetti/*.md   (una scheda progetto per file, due lingue nel file)
  - content/libri/*.md      (un libro per file, edizione inglese con i campi _en)
  - content/libreria.md     (disposizione dei libri sulle mensole)
  - content/progressi/*.md  (un progresso per file, con barra di avanzamento)
  - images/profilo/         (una sola immagine: la foto in apertura di pagina)
  - images/decorazioni/     (oggetti tra i libri, citati in content/libreria.md)

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
import zlib
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
PROGETTI_VISIBILI = 6
PROGRESSI_VISIBILI = 4

# Libreria: righe visibili all'apertura e righe aggiunte da ogni "Mostra altro".
# Su schermo largo una riga e' una mensola.
RIGHE_VISIBILI = 3
RIGHE_PER_CLIC = 3

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

# Icona della X nelle modali, uguale per progetti e libri
ICONA_CHIUDI = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                'stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>')
# Copertina nella scheda del libro: 140px nel pannello dal basso, 180px nella finestra centrata
SIZES_SCHEDA_LIBRO = "(min-width: 680px) 180px, 140px"

SIZES_LAVORI = "(min-width: 920px) 240px, (min-width: 600px) 370px, 92vw"
SIZES_FOTO = "(min-width: 860px) 244px, (min-width: 600px) 260px, 62vw"

# Larghezze alternative generate da tools/ottimizza-immagini.py, per cartella
VARIANTI = {
    "images/profilo": [480],
    "images/projects": [480],
    "images/books": [220],
}

# Libreria della sezione Letture: valori ammessi nei file dei libri e in
# content/libreria.md.
SEPARATORE_MENSOLA = re.compile(r"^\s*---\s*mensola\s*---\s*$")
VISTE_LIBRO = ("dorso", "copertina", "disteso")
FORMATI = ("tascabile", "standard", "grande")
STILI_DORSO = ("normale", "grassetto", "corsivo", "mono")
LETTURE_DORSO = ("ascendente", "discendente")
PAGINE_PREDEFINITE = 300
FORMATO_PREDEFINITO = "standard"
STILE_DORSO_PREDEFINITO = "grassetto"
# Verso del titolo sul dorso quando il file non lo indica: le edizioni
# italiane si leggono dal basso verso l'alto, quelle inglesi dall'alto in basso.
LETTURA_PREDEFINITA = {"it": "ascendente", "en": "discendente"}
# Dorsi senza colore: uno di questi toni, scelto dal nome del file e quindi
# sempre lo stesso a ogni build.
TAVOLOZZA_DORSI = ("#2F4F3E", "#7A2E3B", "#2B4A6B", "#A8803F",
                   "#4A5561", "#E8DFC8", "#3F5E5A", "#C9B79C")
# Testo sul dorso: carta o inchiostro del sito, quello con piu' contrasto.
TESTO_DORSO_CHIARO = "#FAF9F5"
TESTO_DORSO_SCURO = "#1C1B18"
# Link costruiti dall'ISBN: amazon.it per i campi base, amazon.com per quelli _en.
NEGOZI_AMAZON = {"": "https://www.amazon.it/dp/%s", "_en": "https://www.amazon.com/dp/%s"}
CARTELLA_DECORAZIONI = "images/decorazioni"
ESTENSIONI_DECORAZIONI = (".webp", ".png", ".jpg", ".jpeg")
# Misure della libreria in pixel sullo schermo largo. Il CSS le moltiplica per
# --u, quindi cambiando --u si riduce tutto in proporzione. Altezza della riga
# e spessore dell'asse arrivano al CSS come variabili, da qui.
LARGHEZZA_MENSOLA = 776       # colonna da 832px meno cornice (14+14) e margini interni (14+14)
ALTEZZA_LIBERA = 224          # spazio utile sopra ogni mensola
ALTEZZA_ASSE = 14             # spessore della mensola
ALTEZZE_FORMATO = {"tascabile": 172, "standard": 194, "grande": 214}
SPESSORE_PER_PAGINA = 0.085   # 300 pagine, 26px
SPESSORE_MINIMO = 24          # misura minima di un bersaglio da toccare secondo le WCAG 2.2
SPESSORE_MASSIMO = 58
MARGINE_DORSO = 1             # per lato: 2px tra due dorsi vicini
MARGINE_OGGETTO = 8           # per lato, attorno a copertine, pile e decorazioni
# Sotto i 680px la libreria si riduce di questo fattore. Dorsi e libri distesi
# restano comunque larghi o alti almeno LARGHEZZA_TOCCO, cosi' si toccano bene.
SCALA_MOBILE = 0.8
LARGHEZZA_TOCCO = 24
# Titolo sul dorso. iA Writer Quattro ha solo quattro larghezze di carattere e
# nessuna crenatura, quindi la lunghezza di un titolo e' la somma esatta delle
# larghezze, lette dai file dei font. I caratteri non elencati sono larghi
# 0,6 em. Lo spazio e' largo 0,45 em nel tondo e nel grassetto e 0,6 nel
# corsivo. In iA Writer Mono ogni carattere e' largo 0,6 em.
LARGHEZZE_QUATTRO = {0.3: "IijlÌÍÎÏìíîïĨĩĪīĬĭįİıĵĺļľ", 0.45: "frtŕŗřţť", 0.9: "%@MWmw©ÆæŒœŴŵ—…"}
LARGHEZZA_CARATTERE = {c: em for em, caratteri in LARGHEZZE_QUATTRO.items() for c in caratteri}
MARGINE_TESTO_DORSO = 10      # spazio alle due estremita' del titolo, uguale al padding del CSS
CORPO_MINIMO_TELEFONO = 11    # corpo pieno del titolo su telefono
CORPO_MINIMO_UNA_RIGA = 9.5   # sotto questo corpo il titolo va su due righe
CORPO_MINIMO_DUE_RIGHE = 9    # sotto questo corpo neanche due righe bastano e il titolo resta tagliato
INTERLINEA_TITOLO = 1.05      # uguale al line-height di .libro-titolo
SICUREZZA_TITOLO = 1.03       # piccolo margine sulle misure, per non sfiorare i bordi


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


def leggi_voto(meta, origine):
    """Voto da 0 a 5 a mezzi punti. Accetta anche la virgola: 4,5."""
    grezzo = meta.get("voto", "").strip()
    if not grezzo:
        return 5.0  # il campo mancante e' gia' segnalato come errore
    try:
        voto = float(grezzo.replace(",", "."))
    except ValueError:
        voto = -1.0
    if not 0 <= voto <= 5 or voto * 2 != int(voto * 2):
        errore("%s: 'voto' va da 0 a 5 a mezzi punti, per esempio 4 o 4,5 (trovato: %r)"
               % (origine.name, grezzo))
        return 5.0
    return voto


def formatta_voto(voto, lingua):
    """4 resta 4; 4.5 diventa 4,5 in italiano e 4.5 in inglese."""
    testo = "%d" % voto if float(voto).is_integer() else "%.1f" % voto
    return testo.replace(".", ",") if lingua == "it" else testo


def testo_voto(T, voto, lingua):
    """Frase del voto per i lettori di schermo. Accetta sia %s sia il vecchio
    %d nei file dei testi, cosi' un file dei testi non aggiornato non rompe
    il build."""
    return T["libri_voto"].replace("%d", "%s") % formatta_voto(voto, lingua)


def leggi_intero_positivo(meta, chiave, origine, predefinito):
    grezzo = meta.get(chiave, "").strip()
    if not grezzo:
        return predefinito
    if not re.fullmatch(r"\d+", grezzo) or int(grezzo) == 0:
        errore("%s: '%s' deve essere un numero intero maggiore di zero (trovato: %r)"
               % (origine.name, chiave, grezzo))
        return predefinito
    return int(grezzo)


def leggi_scelta(meta, chiave, ammessi, origine, predefinito):
    """Campo che accetta solo alcune parole, per esempio formato o dorso_stile."""
    grezzo = meta.get(chiave, "").strip().lower()
    if not grezzo:
        return predefinito
    if grezzo not in ammessi:
        errore("%s: '%s' accetta solo %s (trovato: %r)"
               % (origine.name, chiave, ", ".join(ammessi), grezzo))
        return predefinito
    return grezzo


def leggi_esadecimale(meta, chiave, origine):
    grezzo = meta.get(chiave, "").strip()
    if not grezzo:
        return ""
    if not COLORE_HEX.match(grezzo):
        errore("%s: '%s' deve essere un esadecimale tipo #2F4F3E (trovato: %r)"
               % (origine.name, chiave, grezzo))
        return ""
    cifre = grezzo.lstrip("#")
    if len(cifre) == 3:
        cifre = "".join(c * 2 for c in cifre)
    return "#" + cifre.upper()


def luminanza(colore):
    """Luminanza relativa secondo le WCAG: 0 e' il nero, 1 il bianco."""
    cifre = colore.lstrip("#")
    canali = []
    for i in (0, 2, 4):
        c = int(cifre[i:i + 2], 16) / 255
        canali.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * canali[0] + 0.7152 * canali[1] + 0.0722 * canali[2]


def colore_testo_dorso(sfondo):
    """Carta o inchiostro del sito: sceglie quello con piu' contrasto sul dorso."""
    base = luminanza(sfondo)

    def contrasto(colore):
        altra = luminanza(colore)
        return (max(base, altra) + 0.05) / (min(base, altra) + 0.05)

    return max((TESTO_DORSO_CHIARO, TESTO_DORSO_SCURO), key=contrasto)


def indice_stabile(testo, quanti):
    """Numero da 0 a quanti-1 ricavato dal testo, uguale a ogni build.
    hash() di Python cambia a ogni avvio, zlib.crc32 no."""
    return zlib.crc32(testo.encode("utf-8")) % quanti


def isbn_valido(isbn):
    """Controlla la cifra finale. Rileva ogni errore di battitura su una cifra."""
    if re.fullmatch(r"\d{13}", isbn):
        somma = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(isbn[:12]))
        return (10 - somma % 10) % 10 == int(isbn[12])
    if re.fullmatch(r"\d{9}[\dX]", isbn):
        somma = sum((10 - i) * int(c) for i, c in enumerate(isbn[:9]))
        finale = 10 if isbn[9] == "X" else int(isbn[9])
        return (somma + finale) % 11 == 0
    return False


def isbn10_da_13(isbn13):
    """ISBN a 10 cifre ricavato da quello a 13. Esiste solo per i codici 978."""
    if not isbn13.startswith("978"):
        return ""
    corpo = isbn13[3:12]
    somma = sum((10 - i) * int(c) for i, c in enumerate(corpo))
    finale = (11 - somma % 11) % 11
    return corpo + ("X" if finale == 10 else str(finale))


def leggi_isbn(meta, chiave, origine):
    """ISBN a 10 o 13 cifre, con o senza trattini e spazi."""
    grezzo = meta.get(chiave, "").strip()
    if not grezzo:
        return ""
    isbn = re.sub(r"[\s-]", "", grezzo).upper()
    if not isbn_valido(isbn):
        errore("%s: '%s' non e' un ISBN valido, controlla le cifre (trovato: %r)"
               % (origine.name, chiave, grezzo))
        return ""
    return isbn


def link_amazon(meta, suffisso, origine):
    """Link al libro su Amazon per i campi base (suffisso "") o inglesi ("_en").
    Un link scritto a mano vince; altrimenti lo costruisce dall'ISBN, perche'
    per i libri stampati il codice Amazon coincide con l'ISBN a 10 cifre."""
    isbn = leggi_isbn(meta, "isbn" + suffisso, origine)
    manuale = meta.get("amazon" + suffisso, "").strip()
    if manuale:
        if not manuale.startswith("https://"):
            errore("%s: 'amazon%s' deve iniziare con https:// (trovato: %r)"
                   % (origine.name, suffisso, manuale))
            return ""
        return manuale
    if not isbn:
        return ""
    if len(isbn) == 13:
        isbn10 = isbn10_da_13(isbn)
        if not isbn10:
            avviso("%s: 'isbn%s' inizia con 979 e non ha un codice a 10 cifre, "
                   "scrivi il link in 'amazon%s'" % (origine.name, suffisso, suffisso))
            return ""
        isbn = isbn10
    return NEGOZI_AMAZON[suffisso] % isbn


def titolo_dorso(meta, lingua):
    """Testo sul dorso. Nel sito inglese preferisce un titolo inglese:
    dorso_titolo_en, poi titolo_en, poi dorso_titolo e titolo. Cosi' un
    titolo breve scritto per l'edizione italiana non compare sul sito inglese
    quando esiste il titolo inglese."""
    if lingua == "it":
        return meta.get("dorso_titolo", "") or meta.get("titolo", "")
    return (meta.get("dorso_titolo_en", "") or meta.get("titolo_en", "")
            or meta.get("dorso_titolo", "") or meta.get("titolo", ""))


def edizione_libro(meta, controllati, slug, lingua):
    """Quello che il sito mostra di un libro in una lingua.

    Stessa regola del resto del sito: nel sito inglese ogni campo _en
    sostituisce quello base e, se manca, vale quello base. Cosi' un libro
    ha due titoli, due autori, due copertine, due link e due dorsi, mentre
    voto, pagine e formato restano unici e la disposizione non cambia tra
    le lingue. Unica eccezione il titolo sul dorso, vedi titolo_dorso()."""
    def controllato(chiave):
        if lingua != "it" and controllati["_en"][chiave]:
            return controllati["_en"][chiave]
        return controllati[""][chiave]

    colore = (controllato("colore")
              or TAVOLOZZA_DORSI[indice_stabile(slug, len(TAVOLOZZA_DORSI))])
    return {
        "titolo": campo(meta, "titolo", lingua),
        "autore": campo(meta, "autore", lingua),
        "copertina": campo(meta, "copertina", lingua),
        "link": controllato("link"),
        "dorso_titolo": titolo_dorso(meta, lingua),
        "dorso_colore": colore,
        "dorso_testo": colore_testo_dorso(colore),
        "dorso_stile": controllato("stile") or STILE_DORSO_PREDEFINITO,
        "dorso_lettura": controllato("lettura") or LETTURA_PREDEFINITA.get(lingua, "discendente"),
    }


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
        slug = slug_da_file(f)
        if not re.fullmatch(r"[a-z0-9-]+", slug or ""):
            errore("%s: nome file non valido, usa solo minuscole, numeri e trattini" % f.name)
        if slug == "decorazione":
            errore("%s: 'decorazione' e' una parola riservata di libreria.md, rinomina il file" % f.name)
        voto = leggi_voto(meta, f)
        pagine = leggi_intero_positivo(meta, "pagine", f, PAGINE_PREDEFINITE)
        formato = leggi_scelta(meta, "formato", FORMATI, f, FORMATO_PREDEFINITO)
        verifica_immagine(meta.get("copertina"), f)
        verifica_immagine(meta.get("copertina_en"), f)

        # Ogni campo si controlla una volta sola: "" sono i campi base, "_en"
        # quelli inglesi. Le edizioni delle due lingue si compongono sotto.
        controllati = {}
        for suffisso in ("", "_en"):
            controllati[suffisso] = {
                "colore": leggi_esadecimale(meta, "dorso_colore" + suffisso, f),
                "stile": leggi_scelta(meta, "dorso_stile" + suffisso, STILI_DORSO, f, ""),
                "lettura": leggi_scelta(meta, "dorso_lettura" + suffisso, LETTURE_DORSO, f, ""),
                "link": link_amazon(meta, suffisso, f),
            }
        if meta.get("copertina_en") and controllati[""]["link"] and not controllati["_en"]["link"]:
            avviso("%s: c'e' 'copertina_en' ma mancano 'amazon_en' e 'isbn_en', "
                   "il sito inglese usa il link italiano" % f.name)

        nota_it, nota_en = dividi_corpo(corpo)
        if manca_traduzione(meta, "titolo"):
            avviso("%s: manca 'titolo_en', in inglese uso il titolo italiano" % f.name)
        libri.append({
            "slug": slug,
            "meta": meta,
            "voto": voto,
            "pagine": pagine,
            "formato": formato,
            "nota": {"it": nota_it, "en": nota_en or nota_it},
            "edizioni": {lingua: edizione_libro(meta, controllati, slug, lingua)
                         for lingua, _ in LINGUE},
        })
    visti = set()
    for b in libri:
        if b["slug"] in visti:
            errore("due file dei libri hanno lo stesso nome senza numero: %s" % b["slug"])
        visti.add(b["slug"])
    return libri


# ------------------------------------------------------------------ libreria

def carica_libreria(libri):
    """Legge content/libreria.md e ritorna la lista delle mensole.

    Ogni mensola e' una lista di elementi, nell'ordine del file:
      {"tipo": "libro", "slug": "rework", "vista": "dorso"}      (o "copertina")
      {"tipo": "pila", "libri": ["greenlights", "scrum"]}        il primo in cima
      {"tipo": "decorazione", "immagine": "/images/decorazioni/vaso.webp", "altezza": 60}
    I libri che non compaiono nel file finiscono in fondo all'ultima mensola."""
    per_nome = {b["slug"]: b for b in libri}
    f = CONTENT / "libreria.md"
    mensole = []
    usati = {}
    if not f.exists():
        avviso("manca content/libreria.md: metto tutti i libri su una mensola, in ordine di nome file")
    else:
        corrente = None
        righe = f.read_text(encoding="utf-8-sig").splitlines()
        for numero_riga, riga in enumerate(righe, 1):
            testo = riga.strip()
            if not testo or testo.startswith("#"):
                continue
            dove = "libreria.md, riga %d" % numero_riga
            if SEPARATORE_MENSOLA.match(testo):
                corrente = []
                mensole.append(corrente)
                continue
            if testo.startswith("---"):
                errore("%s: separatore non riconosciuto, per una mensola nuova scrivi --- mensola ---"
                       % dove)
                continue
            if corrente is None:
                # righe scritte prima del primo separatore: aprono comunque una mensola
                corrente = []
                mensole.append(corrente)
            nome, _, opzione = testo.partition(":")
            nome = nome.strip().lower()
            opzione = opzione.strip()
            if nome == "decorazione":
                elemento = leggi_decorazione(opzione, dove)
                if elemento:
                    corrente.append(elemento)
                continue
            if nome not in per_nome:
                errore("%s: nessun libro si chiama '%s'. Usa il nome del file senza numero e senza .md; "
                       "per una decorazione scrivi decorazione: vaso.webp, 60%%" % (dove, nome))
                continue
            if nome in usati:
                errore("%s: '%s' compare gia' alla riga %d" % (dove, nome, usati[nome]))
                continue
            vista = opzione.lower() or "dorso"
            if vista not in VISTE_LIBRO:
                errore("%s: opzione '%s' sconosciuta, scrivi copertina oppure disteso" % (dove, opzione))
                continue
            usati[nome] = numero_riga
            corrente.append({"tipo": "libro", "slug": nome, "vista": vista})

    vuote = sum(1 for m in mensole if not m)
    if vuote:
        avviso("libreria.md: ignoro le mensole senza elementi (%d)" % vuote)
        mensole = [m for m in mensole if m]

    mancanti = [b["slug"] for b in libri if b["slug"] not in usati]
    if mancanti:
        if not mensole:
            mensole.append([])
        for nome in mancanti:
            mensole[-1].append({"tipo": "libro", "slug": nome, "vista": "dorso"})
        if f.exists():
            avviso("libreria.md: questi libri non compaiono nel file e vanno in fondo "
                   "all'ultima mensola: %s" % ", ".join(mancanti))
    return [raggruppa_pile(m) for m in mensole]


def leggi_decorazione(valore, dove):
    """decorazione: vaso.webp, 60%  diventa l'immagine images/decorazioni/vaso.webp,
    alta il 60% della mensola."""
    parti = [p.strip() for p in valore.split(",")]
    if len(parti) != 2 or not parti[0]:
        errore("%s: scrivi la decorazione cosi': decorazione: vaso.webp, 60%%" % dove)
        return None
    nome_file, altezza = parti
    estensione = Path(nome_file).suffix.lower()
    if (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", nome_file)
            or estensione not in ESTENSIONI_DECORAZIONI):
        errore("%s: '%s' non va bene, usa un file webp, png o jpg con un nome senza spazi"
               % (dove, nome_file))
        return None
    misura = re.fullmatch(r"(\d{1,3})\s*%?", altezza)
    if not misura or not 1 <= int(misura.group(1)) <= 100:
        errore("%s: l'altezza della decorazione va da 1%% a 100%% (trovato: %r)" % (dove, altezza))
        return None
    percorso = "/%s/%s" % (CARTELLA_DECORAZIONI, nome_file)
    if not (ROOT / CARTELLA_DECORAZIONI / nome_file).is_file():
        errore("%s: immagine non trovata: %s" % (dove, percorso))
        return None
    if estensione in (".jpg", ".jpeg"):
        avviso("%s: %s e' un jpg e ha lo sfondo pieno, per scontornarla usa webp o png"
               % (dove, nome_file))
    return {"tipo": "decorazione", "immagine": percorso, "altezza": int(misura.group(1))}


def raggruppa_pile(elementi):
    """Libri distesi uno dopo l'altro diventano una pila; il primo scritto sta in cima."""
    risultato = []
    for el in elementi:
        if el["tipo"] == "libro" and el["vista"] == "disteso":
            if risultato and risultato[-1]["tipo"] == "pila":
                risultato[-1]["libri"].append(el["slug"])
            else:
                risultato.append({"tipo": "pila", "libri": [el["slug"]]})
        else:
            risultato.append(el)
    return risultato


def riepilogo_libreria(mensole):
    libri = pile = decorazioni = 0
    for mensola in mensole:
        for el in mensola:
            if el["tipo"] in ("libro", "dorso", "copertina"):
                libri += 1
            elif el["tipo"] == "pila":
                pile += 1
                libri += len(el["libri"])
            else:
                decorazioni += 1
    return "mensole %d, libri %d, pile %d, decorazioni %d" % (len(mensole), libri, pile, decorazioni)


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
            '          %(icona)s\n'
            '        </button>\n'
            '      </header>\n'
            '      <div class="modal-body">\n%(corpo)s\n      </div>\n'
            '    </div>\n'
            '  </div>' % {"slug": esc(p["slug"]),
                          "titolo": esc(campo(p["meta"], "titolo", lingua)),
                          "chiudi": esc(T["modale_chiudi"]),
                          "icona": ICONA_CHIUDI,
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


def spessore_dorso(pagine):
    """Spessore del dorso in pixel ricavato dalle pagine: 300 pagine, 26px."""
    return max(SPESSORE_MINIMO, min(SPESSORE_MASSIMO, round(pagine * SPESSORE_PER_PAGINA)))


def altezza_libro(libro):
    """Altezza dal formato, con una piccola differenza stabile tra libri dello
    stesso formato (da -3% a +3%): la mensola sembra vera e non cambia a ogni build."""
    base = ALTEZZE_FORMATO[libro["formato"]]
    scarto = indice_stabile("altezza:" + libro["slug"], 7) - 3
    return min(ALTEZZA_LIBERA, round(base * (100 + scarto) / 100))


def corpo_testo_dorso(spessore):
    """Corpo pieno del titolo sul dorso: cresce con lo spessore, da 11 a 15px.
    Per i titoli lunghi render_dorso lo riduce o manda il titolo su due righe."""
    return max(11, min(15, round(spessore * 0.44)))


def proporzione_immagine(percorso):
    """Larghezza divisa altezza di un'immagine del sito, 0 se non leggibile."""
    if not percorso:
        return 0
    larg, alt = dimensioni_immagine(ROOT / percorso.lstrip("/"))
    return larg / alt if larg and alt else 0


def misura_libreria(mensole, libri):
    """Aggiunge a ogni elemento della libreria le misure in pixel e controlla
    lo spazio. Una mensola troppo piena va a capo su piu' righe, una pila
    piu' alta della mensola viene divisa. Le misure dipendono solo dai campi
    comuni alle due lingue, cosi' la disposizione e' identica in italiano e
    in inglese e gli avvisi escono una volta sola."""
    per_nome = {b["slug"]: b for b in libri}
    misurate = []
    for numero, mensola in enumerate(mensole, 1):
        elementi = []
        for el in mensola:
            if el["tipo"] == "pila":
                elementi.extend(misura_pila(el, per_nome, numero))
            elif el["tipo"] == "decorazione":
                altezza = round(ALTEZZA_LIBERA * el["altezza"] / 100)
                proporzione = proporzione_immagine(el["immagine"])
                if not proporzione:
                    avviso("libreria.md: non riesco a leggere le misure di %s, la considero quadrata"
                           % el["immagine"])
                    proporzione = 1
                elementi.append({"tipo": "decorazione", "immagine": el["immagine"],
                                 "w": round(altezza * proporzione), "h": altezza,
                                 "margine": MARGINE_OGGETTO})
            elif el["vista"] == "copertina":
                libro = per_nome[el["slug"]]
                altezza = altezza_libro(libro)
                # la proporzione viene dalla copertina italiana: quella inglese
                # riempie lo stesso spazio, cosi' la mensola non cambia tra le lingue
                proporzione = proporzione_immagine(libro["meta"].get("copertina", "")) or 2 / 3
                elementi.append({"tipo": "copertina", "slug": el["slug"],
                                 "w": min(altezza, round(altezza * proporzione)), "h": altezza,
                                 "margine": MARGINE_OGGETTO})
            else:
                libro = per_nome[el["slug"]]
                spessore = spessore_dorso(libro["pagine"])
                elementi.append({"tipo": "dorso", "slug": el["slug"],
                                 "w": spessore, "h": altezza_libro(libro),
                                 "fs": corpo_testo_dorso(spessore), "margine": MARGINE_DORSO})
        occupato = sum(e["w"] + 2 * e["margine"] for e in elementi)
        if occupato > LARGHEZZA_MENSOLA:
            avviso("libreria.md: la mensola %d e' piena al %d%%, su schermo largo va a capo su piu' righe"
                   % (numero, round(occupato * 100 / LARGHEZZA_MENSOLA)))
        misurate.append(elementi)
    return misurate


def misura_pila(pila, per_nome, numero):
    """Libri distesi uno sopra l'altro. Se superano l'altezza della mensola
    la pila si divide in pile vicine."""
    # Il controllo usa le misure da telefono: ridotte, ma mai sotto la misura
    # minima da toccare. Se la pila entra su telefono entra anche su schermo
    # largo, quindi la divisione e' la stessa ovunque.
    limite = ALTEZZA_LIBERA * SCALA_MOBILE
    pile = [[]]
    altezza = 0
    for slug in pila["libri"]:
        libro = per_nome[slug]
        spessore = spessore_dorso(libro["pagine"])
        spessore_mobile = max(LARGHEZZA_TOCCO, spessore * SCALA_MOBILE)
        if pile[-1] and altezza + spessore_mobile > limite:
            pile.append([])
            altezza = 0
        pile[-1].append({"slug": slug, "w": altezza_libro(libro), "h": spessore,
                         "fs": corpo_testo_dorso(spessore),
                         "sposta": indice_stabile("pila:" + slug, 9)})
        altezza += spessore_mobile
    if len(pile) > 1:
        avviso("libreria.md: una pila della mensola %d e' piu' alta della mensola, la divido in %d pile"
               % (numero, len(pile)))
    return [{"tipo": "pila", "libri": p, "w": max(x["w"] + x["sposta"] for x in p),
             "h": sum(x["h"] for x in p), "margine": MARGINE_OGGETTO} for p in pile]


def descrizione_libro(libro, lingua, T):
    """Testo per i lettori di schermo: titolo, autore e voto."""
    ed = libro["edizioni"][lingua]
    return "%s, %s. %s" % (ed["titolo"], ed["autore"], testo_voto(T, libro["voto"], lingua))


def apri_scheda(libro, lingua, T, contenuto):
    """Bottone che apre la scheda del libro: il dorso o la copertina sono il
    contenuto visibile, titolo, autore e voto il nome letto dai lettori di schermo."""
    return ('<button class="libro-apri" type="button" data-modal="libro-%s" aria-haspopup="dialog">'
            '%s<span class="visually-hidden">%s</span></button>'
            % (esc(libro["slug"]), contenuto, esc(descrizione_libro(libro, lingua, T))))


def lunghezza_titolo(testo, stile):
    """Lunghezza del titolo in em: moltiplicata per il corpo da' i pixel."""
    if stile == "mono":
        return max(0.1, len(testo) * 0.6)
    spazio = 0.6 if stile == "corsivo" else 0.45
    return max(0.1, sum(spazio if c == " " else LARGHEZZA_CARATTERE.get(c, 0.6) for c in testo))


def dividi_titolo(testo, stile):
    """Divide il titolo in due righe a uno spazio, nel punto che rende piu'
    corta la riga piu' lunga. None se il titolo e' una parola sola."""
    parole = testo.split()
    if len(parole) < 2:
        return None
    migliore = None
    for i in range(1, len(parole)):
        righe = (" ".join(parole[:i]), " ".join(parole[i:]))
        piu_lunga = max(lunghezza_titolo(r, stile) for r in righe)
        if migliore is None or piu_lunga < migliore[0]:
            migliore = (piu_lunga, righe)
    return migliore[1]


def impagina_titolo(testo, stile, lunghezza, spessore, corpo_pieno):
    """Corpo e righe del titolo in uno spazio lungo `lunghezza` e largo
    `spessore` pixel. Prima riduce il corpo su una riga fino a
    CORPO_MINIMO_UNA_RIGA; se non basta prova due righe. Ritorna (corpo, righe):
    righe vale 1 o 2, oppure 0 se il titolo non entra e resta tagliato."""
    corpo = min(corpo_pieno, lunghezza / (lunghezza_titolo(testo, stile) * SICUREZZA_TITOLO))
    if corpo >= CORPO_MINIMO_UNA_RIGA:
        return corpo, 1
    divise = dividi_titolo(testo, stile)
    if divise:
        piu_lunga = max(lunghezza_titolo(r, stile) for r in divise) * SICUREZZA_TITOLO
        corpo = min(corpo_pieno, lunghezza / piu_lunga, (spessore - 2) / (2 * INTERLINEA_TITOLO))
        if corpo >= CORPO_MINIMO_DUE_RIGHE:
            return corpo, 2
    return corpo_pieno, 0


def render_dorso(libro, lingua, T, classe, w, h, fs, extra_stile=""):
    ed = libro["edizioni"][lingua]
    testo, stile = ed["dorso_titolo"], ed["dorso_stile"]
    # il titolo corre lungo l'altezza del libro: per un dorso dritto e' h,
    # per un libro disteso e' w; l'altra misura e' lo spessore
    lunghezza, spessore = (w, h) if classe == "libro--disteso" else (h, w)
    spazio = lunghezza - 2 * MARGINE_TESTO_DORSO
    largo = impagina_titolo(testo, stile, spazio, spessore, fs)
    telefono = impagina_titolo(testo, stile, spazio * SCALA_MOBILE,
                               max(LARGHEZZA_TOCCO, spessore * SCALA_MOBILE),
                               max(CORPO_MINIMO_TELEFONO, fs * SCALA_MOBILE))
    tagliato = [nome for nome, (_, righe) in (("schermo largo", largo), ("telefono", telefono)) if righe == 0]
    classi = "libro-titolo"
    if tagliato:
        # un titolo che non entra da qualche parte si comporta ovunque allo
        # stesso modo: corpo pieno, una riga, puntini
        inglese = lingua != "it"
        avviso("libreria: il titolo sul dorso di %s%s non entra neanche su due righe (%s) e resta "
               "tagliato, accorcialo con 'dorso_titolo%s'"
               % (libro["slug"], " nel sito inglese" if inglese else "", ", ".join(tagliato),
                  "_en" if inglese else ""))
        largo, telefono = (fs, 1), (max(CORPO_MINIMO_TELEFONO, fs * SCALA_MOBILE), 1)
        classi += " libro-titolo--taglia"
    if largo[1] == 2:
        classi += " libro-titolo--due"
    if telefono[1] == 2:
        classi += " libro-titolo--due-m"
    divise = dividi_titolo(testo, stile) if 2 in (largo[1], telefono[1]) else None
    titolo = ('<span class="riga">%s</span> <span class="riga">%s</span>' % (esc(divise[0]), esc(divise[1]))
              if divise else esc(testo))
    dorso = ('<span class="libro-dorso libro-dorso--%s libro-dorso--%s" aria-hidden="true">'
             '<span class="%s">%s</span></span>' % (stile, ed["dorso_lettura"], classi, titolo))
    return ('<li class="libro %s" style="--w:%d;--h:%d;--t:%g;--tm:%g;--colore:%s;--testo:%s%s">%s</li>'
            % (classe, w, h, round(largo[0], 2), round(telefono[0], 2), ed["dorso_colore"],
               ed["dorso_testo"], extra_stile, apri_scheda(libro, lingua, T, dorso)))


def render_elemento_libreria(el, per_nome, lingua, T):
    if el["tipo"] == "dorso":
        return render_dorso(per_nome[el["slug"]], lingua, T, "libro--dorso", el["w"], el["h"], el["fs"])
    if el["tipo"] == "pila":
        distesi = [render_dorso(per_nome[x["slug"]], lingua, T, "libro--disteso",
                                x["w"], x["h"], x["fs"], ";--sposta:%d" % x["sposta"])
                   for x in el["libri"]]
        return ('<li class="pila" style="--w:%d"><ul class="pila-libri" role="list">%s</ul></li>'
                % (el["w"], "".join(distesi)))
    if el["tipo"] == "copertina":
        libro = per_nome[el["slug"]]
        immagine = tag_immagine(libro["edizioni"][lingua]["copertina"], "", "%dpx" % el["w"],
                                'loading="lazy" decoding="async"')
        return ('<li class="libro libro--copertina" style="--w:%d;--h:%d">%s</li>'
                % (el["w"], el["h"], apri_scheda(libro, lingua, T, immagine)))
    immagine = tag_immagine(el["immagine"], "", "", 'loading="lazy" decoding="async"')
    return ('<li class="decorazione" aria-hidden="true" style="--w:%d;--h:%d">%s</li>'
            % (el["w"], el["h"], immagine))


def render_modali_libri(libri, lingua, T):
    """Una scheda per ogni libro, aperta dal clic sul dorso o sulla copertina.
    Stessa struttura delle schede dei progetti, cosi' riusa stili, focus e
    chiusura di main.js. data-hash e' l'indirizzo #libro-<nome>: il tasto
    indietro chiude la scheda e il link si puo' condividere."""
    schede = []
    for b in libri:
        ed = b["edizioni"][lingua]
        copertina = tag_immagine(ed["copertina"], "%s %s" % (T["libri_copertina"], ed["titolo"]),
                                 SIZES_SCHEDA_LIBRO, 'loading="lazy" decoding="async"')
        nota = ('\n          <p class="libro-scheda-nota">%s</p>' % inline_md(b["nota"][lingua])
                if b["nota"][lingua] else "")
        link = ('\n          <p class="modal-cta"><a class="btn btn-primary" href="%s" target="_blank" '
                'rel="noopener">%s</a></p>' % (esc(ed["link"]), esc(T["libri_amazon"]))
                if ed["link"] else "")
        schede.append(
            '<div class="modal modal--libro" id="modal-libro-%(slug)s" data-hash="libro-%(slug)s" hidden>\n'
            '    <div class="modal-backdrop" data-close></div>\n'
            '    <div class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="modal-libro-%(slug)s-title">\n'
            '      <header class="modal-head">\n'
            '        <h2 id="modal-libro-%(slug)s-title">%(titolo)s</h2>\n'
            '        <button class="modal-close" type="button" data-close aria-label="%(chiudi)s">\n'
            '          %(icona)s\n'
            '        </button>\n'
            '      </header>\n'
            '      <div class="modal-body libro-scheda">\n'
            '        <div class="libro-scheda-copertina">%(copertina)s</div>\n'
            '        <div class="libro-scheda-info">\n'
            '          <p class="libro-scheda-autore">%(autore)s</p>\n'
            '          <p class="libro-scheda-voto"><span class="stelle" style="--voto:%(voto_css)s" aria-hidden="true"></span>'
            '<span class="libro-scheda-numero" aria-hidden="true">%(voto)s</span>'
            '<span class="visually-hidden">%(voto_testo)s</span></p>%(nota)s%(link)s\n'
            '        </div>\n'
            '      </div>\n'
            '    </div>\n'
            '  </div>' % {"slug": esc(b["slug"]), "titolo": esc(ed["titolo"]), "autore": esc(ed["autore"]),
                          "chiudi": esc(T["modale_chiudi"]), "icona": ICONA_CHIUDI, "copertina": copertina,
                          "voto_css": "%g" % b["voto"], "voto": formatta_voto(b["voto"], lingua),
                          "voto_testo": esc(testo_voto(T, b["voto"], lingua)), "nota": nota, "link": link}
        )
    return "\n\n  ".join(schede)


def render_libreria(misurate, libri, lingua, T):
    """La libreria con le mensole, i bottoni "Mostra altro" e "Mostra meno" e
    l'annuncio per i lettori di schermo. I bottoni nascono nascosti: li mostra
    main.js solo se le righe sono piu' di RIGHE_VISIBILI, quindi senza
    JavaScript si vede tutta la libreria."""
    if not misurate:
        return ""
    per_nome = {b["slug"]: b for b in libri}
    mensole = []
    for elementi in misurate:
        voci = "\n            ".join(render_elemento_libreria(el, per_nome, lingua, T) for el in elementi)
        mensole.append('<ul class="mensola" role="list">\n            %s\n          </ul>' % voci)
    return ('<div class="libreria reveal" data-libreria data-righe="%d" data-righe-clic="%d"'
            ' style="--riga:%d;--asse:%d;--scala-mobile:%g;--tocco:%d">\n'
            '          <div class="libreria-interno">\n'
            '          %s\n'
            '          </div>\n'
            '        </div>\n'
            '        <div class="libreria-azioni" data-libreria-azioni hidden>\n'
            '          <button class="btn btn-ghost" type="button" data-libreria-altro>%s</button>\n'
            '          <button class="btn btn-ghost" type="button" data-libreria-meno hidden>%s</button>\n'
            '        </div>\n'
            '        <p class="visually-hidden" aria-live="polite" data-libreria-annuncio data-testo="%s"></p>'
            % (RIGHE_VISIBILI, RIGHE_PER_CLIC, ALTEZZA_LIBERA + ALTEZZA_ASSE, ALTEZZA_ASSE,
               SCALA_MOBILE, LARGHEZZA_TOCCO,
               "\n          ".join(mensole),
               esc(T["libri_mostra_altro"]), esc(T["libri_mostra_meno"]), esc(T["libri_aggiunti"])))


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

def costruisci_pagina(modello, lingua, sottocartella, testi, progetti, libri, libreria, progressi, foto):
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
        "MODALS": "\n\n  ".join(m for m in (render_modali(progetti, lingua, T),
                                             render_modali_libri(libri, lingua, T)) if m),
        "PROGRESS": render_progressi(progressi, lingua, T),
        "PROGRESS_MORE": render_toggle_progressi(progressi, T),
        "BOOKS": render_libreria(libreria, libri, lingua, T),
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
    libreria = misura_libreria(carica_libreria(libri), libri)
    progressi = carica_progressi()
    foto = trova_foto_profilo()

    pagine = {}
    if not ERRORI:
        modello = TEMPLATE.read_text(encoding="utf-8")
        for lingua, sottocartella in LINGUE:
            pagine[lingua] = (sottocartella,
                              costruisci_pagina(modello, lingua, sottocartella, testi,
                                                progetti, libri, libreria, progressi, foto))

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
    print("  libreria: %s" % riepilogo_libreria(libreria))
    print("  foto profilo: %s" % foto)


if __name__ == "__main__":
    main()
