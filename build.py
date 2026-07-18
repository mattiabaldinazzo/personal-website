#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py
Genera il sito statico in _site/ a partire da:
  - templates/index.html    (struttura della pagina, con segnaposto {{...}})
  - content/progetti/*.md   (una scheda progetto per file)
  - content/libri/*.md      (un libro per file)
  - content/progressi/*.md  (un progresso per file, con barra di avanzamento)
  - images/profilo/         (una sola immagine: la foto della sezione Chi sono)

Nessuna dipendenza esterna: solo libreria standard di Python 3.
Uso:  python3 build.py
Anteprima locale:  python3 -m http.server 8000 --directory _site
"""

import html
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
TEMPLATE = ROOT / "templates" / "index.html"
OUT = ROOT / "_site"

# File e cartelle copiati cosi' come sono in _site/
STATIC_FILES = [
    "styles.css", "main.js", "favicon.svg", "favicon.ico",
    "robots.txt", "sitemap.xml", "CNAME", "cv.pdf",
]
STATIC_DIRS = ["images", "fonts", "jet_converter"]

# Quanti libri restano visibili prima del bottone "Mostra tutti"
LIBRI_VISIBILI = 4

# Estensioni ammesse per la foto profilo
ESTENSIONI_FOTO = {".webp", ".jpg", ".jpeg", ".png"}

# Ordine e etichette delle categorie note; le nuove vengono accodate
CATEGORIE_NOTE = [("personali", "Personali"), ("lavorativi", "Lavorativi"), ("universitari", "Universitari")]

ERRORI = []


def errore(msg):
    ERRORI.append(msg)


def esc(testo):
    return html.escape(str(testo), quote=True)


# ---------------------------------------------------------------- frontmatter

def leggi_md(path):
    """Ritorna (meta: dict, corpo: str) da un file markdown con frontmatter ---."""
    testo = path.read_text(encoding="utf-8")
    meta, corpo = {}, testo
    if testo.lstrip().startswith("---"):
        parti = testo.lstrip().split("---", 2)
        if len(parti) == 3:
            _, fm, corpo = parti
            for riga in fm.strip().splitlines():
                if ":" in riga:
                    k, v = riga.split(":", 1)
                    meta[k.strip().lower()] = v.strip().strip('"').strip("'")
    return meta, corpo.strip()


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


# ------------------------------------------------------------------ contenuti

def slug_da_file(path):
    base = path.stem
    base = re.sub(r"^\d+[-_]?", "", base)
    return base.lower()


def verifica_immagine(percorso, origine):
    if not percorso:
        return
    rel = percorso.lstrip("/")
    if not (ROOT / rel).exists():
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
        for campo in ("titolo", "categoria", "descrizione"):
            if not meta.get(campo):
                errore("%s: manca il campo '%s'" % (f.name, campo))
        slug = slug_da_file(f)
        if not re.fullmatch(r"[a-z0-9-]+", slug or ""):
            errore("%s: nome file non valido, usa solo minuscole, numeri e trattini" % f.name)
        verifica_immagine(meta.get("immagine"), f)
        progetti.append({
            "slug": slug,
            "titolo": meta.get("titolo", ""),
            "categoria": meta.get("categoria", "").lower(),
            "descrizione": meta.get("descrizione", ""),
            "immagine": meta.get("immagine", ""),
            "link": meta.get("link", ""),
            "link_testo": meta.get("link_testo", ""),
            "corpo": corpo,
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
        for campo in ("titolo", "autore", "voto", "copertina"):
            if not meta.get(campo):
                errore("%s: manca il campo '%s'" % (f.name, campo))
        try:
            voto = int(meta.get("voto", "0"))
            if not 1 <= voto <= 5:
                raise ValueError
        except ValueError:
            errore("%s: 'voto' deve essere un intero da 1 a 5" % f.name)
            voto = 5
        verifica_immagine(meta.get("copertina"), f)
        libri.append({
            "titolo": meta.get("titolo", ""),
            "autore": meta.get("autore", ""),
            "voto": voto,
            "copertina": meta.get("copertina", ""),
            "nota": corpo,
        })
    return libri


def carica_progressi():
    cartella = CONTENT / "progressi"
    voci = []
    if not cartella.exists():
        return voci
    for f in sorted(cartella.glob("*.md")):
        meta, _ = leggi_md(f)
        for campo in ("titolo", "descrizione", "raggiunto", "totale"):
            if not meta.get(campo):
                errore("%s: manca il campo '%s'" % (f.name, campo))
        raggiunto = numero(meta, "raggiunto", f)
        totale = numero(meta, "totale", f)
        if raggiunto is None or totale is None:
            continue
        if totale <= 0:
            errore("%s: 'totale' deve essere maggiore di zero" % f.name)
            continue
        if not 0 <= raggiunto <= totale:
            errore("%s: 'raggiunto' deve stare tra 0 e 'totale' (%s)" % (f.name, testo_numero(totale)))
            continue
        percento = round(raggiunto / totale * 100)
        quota = "%s/%s" % (testo_numero(raggiunto), testo_numero(totale))
        unita = meta.get("unita", "").strip()
        if unita:
            quota += " " + unita
        voci.append({
            "titolo": meta.get("titolo", ""),
            "descrizione": meta.get("descrizione", ""),
            "quota": quota,
            "percento": percento,
        })
    return voci


def trova_foto_profilo():
    """In images/profilo deve esserci una sola immagine; il nome e' libero."""
    cartella = ROOT / "images" / "profilo"
    if not cartella.exists():
        errore("manca la cartella images/profilo con la foto della sezione Chi sono")
        return ""
    foto = sorted(p.name for p in cartella.iterdir()
                  if p.is_file() and p.suffix.lower() in ESTENSIONI_FOTO)
    if not foto:
        errore("images/profilo: nessuna immagine trovata (webp, jpg, jpeg o png)")
        return ""
    if len(foto) > 1:
        errore("images/profilo: piu' di un'immagine (%s). Lasciane una sola." % ", ".join(foto))
    return "/images/profilo/" + foto[0]


# -------------------------------------------------------------------- render

def render_filtri(progetti):
    presenti = {p["categoria"] for p in progetti if p["categoria"]}
    ordinate = [(s, l) for s, l in CATEGORIE_NOTE if s in presenti]
    extra = sorted(presenti - {s for s, _ in CATEGORIE_NOTE})
    ordinate += [(s, s.capitalize()) for s in extra]
    voci = ['<button class="filter is-active" type="button" data-filter="tutti" aria-pressed="true">Tutti</button>']
    for slug, label in ordinate:
        voci.append('<button class="filter" type="button" data-filter="%s" aria-pressed="false">%s</button>'
                    % (esc(slug), esc(label)))
    return "\n          ".join(voci)


def render_progetti(progetti):
    schede = []
    for i, p in enumerate(progetti, start=1):
        indice = "%02d" % i
        if p["immagine"]:
            media = ('<span class="work-media"><img src="%s" alt="%s" loading="lazy" decoding="async"></span>'
                     % (esc(p["immagine"]), esc(p["titolo"])))
        else:
            media = ('<span class="work-media work-media--text"><span aria-hidden="true">%s</span></span>'
                     % esc(p["titolo"]))
        if p["corpo"]:
            etichetta = "Scopri di più"
        else:
            etichetta = p["link_testo"] or "Apri progetto"
        corpo_scheda = (
            '<span class="work-body">'
            '<span class="work-index" aria-hidden="true">%s</span>'
            '<span class="work-name">%s</span>'
            '<span class="work-desc">%s</span>'
            '<span class="work-foot"><span class="work-tag">%s</span>'
            '<span class="work-link">%s</span></span>'
            '</span>' % (indice, esc(p["titolo"]), esc(p["descrizione"]),
                         esc(p["categoria"].capitalize()), esc(etichetta))
        )
        if p["corpo"]:
            scheda = ('<button class="work-card" type="button" data-modal="%s" aria-haspopup="dialog">%s%s</button>'
                      % (esc(p["slug"]), media, corpo_scheda))
        elif p["link"]:
            scheda = ('<a class="work-card" href="%s" target="_blank" rel="noopener">%s%s</a>'
                      % (esc(p["link"]), media, corpo_scheda))
        else:
            scheda = '<div class="work-card work-card--static">%s%s</div>' % (media, corpo_scheda)
        schede.append('<li class="work reveal" data-category="%s">%s</li>'
                      % (esc(p["categoria"]), scheda))
    return "\n\n          ".join(schede)


def render_modali(progetti):
    modali = []
    for p in progetti:
        if not p["corpo"]:
            continue
        corpo_html = md_to_html(p["corpo"])
        if p["link"]:
            testo_link = p["link_testo"] or "Apri il progetto"
            corpo_html += ('\n<p class="modal-cta"><a class="btn btn-primary" href="%s" target="_blank" rel="noopener">%s</a></p>'
                           % (esc(p["link"]), esc(testo_link)))
        modali.append(
            '<div class="modal" id="modal-%(slug)s" hidden>\n'
            '    <div class="modal-backdrop" data-close></div>\n'
            '    <div class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="modal-%(slug)s-title">\n'
            '      <header class="modal-head">\n'
            '        <h2 id="modal-%(slug)s-title">%(titolo)s</h2>\n'
            '        <button class="modal-close" type="button" data-close aria-label="Chiudi">\n'
            '          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>\n'
            '        </button>\n'
            '      </header>\n'
            '      <div class="modal-body">\n%(corpo)s\n      </div>\n'
            '    </div>\n'
            '  </div>' % {"slug": esc(p["slug"]), "titolo": esc(p["titolo"]), "corpo": corpo_html}
        )
    return "\n\n  ".join(modali)


def render_libri(libri):
    voci = []
    for i, b in enumerate(libri):
        stelle = "&#9733;" * b["voto"] + "&#9734;" * (5 - b["voto"])
        nascosto = " is-hidden" if i >= LIBRI_VISIBILI else ""
        nota = ('<p class="book-note">%s</p>' % inline_md(b["nota"])) if b["nota"] else ""
        voci.append(
            '<li class="book reveal%s">\n'
            '            <img src="%s" alt="Copertina di %s" loading="lazy" decoding="async">\n'
            '            <div class="book-info">\n'
            '              <p class="book-rating" aria-label="Valutazione %d su 5"><span aria-hidden="true">%s</span></p>\n'
            '              <h3 class="book-title">%s</h3>\n'
            '              <p class="book-author">%s</p>\n%s'
            '            </div>\n'
            '          </li>' % (nascosto, esc(b["copertina"]), esc(b["titolo"]),
                                b["voto"], stelle, esc(b["titolo"]), esc(b["autore"]), nota)
        )
    return "\n          ".join(voci)


def render_toggle_libri(libri):
    if len(libri) <= LIBRI_VISIBILI:
        return ""
    return ('<div class="reads-more reveal">\n'
            '          <button class="btn btn-ghost" type="button" data-books-toggle aria-expanded="false">Mostra tutti i libri</button>\n'
            '        </div>')


def render_progressi(voci):
    righe = []
    for v in voci:
        righe.append(
            '<li class="progress reveal">\n'
            '            <div class="progress-head">\n'
            '              <h3 class="progress-title">%(titolo)s</h3>\n'
            '              <p class="progress-value"><span class="progress-quota">%(quota)s</span><span class="progress-percent">%(pct)d%%</span></p>\n'
            '            </div>\n'
            '            <p class="progress-desc">%(desc)s</p>\n'
            '            <div class="progress-track" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="%(pct)d" aria-label="%(titolo)s: %(pct)d per cento">\n'
            '              <span class="progress-fill" style="--p:%(pct)d%%"></span>\n'
            '            </div>\n'
            '          </li>' % {"titolo": esc(v["titolo"]), "quota": esc(v["quota"]),
                                "desc": esc(v["descrizione"]), "pct": v["percento"]}
        )
    return "\n          ".join(righe)


# --------------------------------------------------------------------- build

def main():
    if not TEMPLATE.exists():
        print("Errore: manca templates/index.html", file=sys.stderr)
        sys.exit(1)

    progetti = carica_progetti()
    libri = carica_libri()
    progressi = carica_progressi()
    foto_profilo = trova_foto_profilo()

    if ERRORI:
        print("Build fallita. Correggi questi problemi:", file=sys.stderr)
        for e in ERRORI:
            print("  - " + e, file=sys.stderr)
        sys.exit(1)

    pagina = TEMPLATE.read_text(encoding="utf-8")
    pagina = pagina.replace("{{FOTO_PROFILO}}", foto_profilo)
    pagina = pagina.replace("{{FILTERS}}", render_filtri(progetti))
    pagina = pagina.replace("{{WORKS}}", render_progetti(progetti))
    pagina = pagina.replace("{{MODALS}}", render_modali(progetti))
    pagina = pagina.replace("{{PROGRESS}}", render_progressi(progressi))
    pagina = pagina.replace("{{BOOKS}}", render_libri(libri))
    pagina = pagina.replace("{{BOOKS_MORE}}", render_toggle_libri(libri))

    residui = re.findall(r"\{\{[A-Z_]+\}\}", pagina)
    if residui:
        print("Errore: segnaposto non sostituiti nel template: %s" % ", ".join(set(residui)), file=sys.stderr)
        sys.exit(1)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    (OUT / "index.html").write_text(pagina, encoding="utf-8")
    for nome in STATIC_FILES:
        src = ROOT / nome
        if src.exists():
            shutil.copy2(src, OUT / nome)
    for nome in STATIC_DIRS:
        src = ROOT / nome
        if src.exists():
            shutil.copytree(src, OUT / nome)

    n_modali = sum(1 for p in progetti if p["corpo"])
    print("Sito generato in _site/")
    print("  progetti: %d (%d con dettaglio)" % (len(progetti), n_modali))
    print("  progressi: %d" % len(progressi))
    print("  libri: %d" % len(libri))
    print("  foto profilo: %s" % foto_profilo)


if __name__ == "__main__":
    main()
