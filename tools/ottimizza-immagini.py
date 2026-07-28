#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/ottimizza-immagini.py

Genera le versioni ridotte delle immagini, quelle che il sito propone al
browser tramite srcset. Il browser scarica solo la misura che gli serve,
quindi su telefono non si porta a casa un'immagine grande il doppio.

Uso:
    python3 tools/ottimizza-immagini.py

Serve Pillow (pip install pillow). Va lanciato solo quando aggiungi o
sostituisci un'immagine; i file generati vanno committati insieme
all'originale. Se te ne dimentichi il sito funziona lo stesso: senza le
varianti usa semplicemente l'immagine grande.

Convenzione dei nomi: accanto a nome.webp vengono creati nome-480.webp,
nome-880.webp e cosi' via. I file che finiscono con -numero vengono
ignorati come sorgente, altrimenti si genererebbero varianti di varianti.
"""

import re
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Serve Pillow: pip install pillow", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent

# cartella: (larghezze da generare, larghezza massima dell'originale, qualita')
REGOLE = {
    "images/profilo":  ([480], 760, 86),
    "images/projects": ([480], 880, 82),
    "images/books":    ([220], 440, 82),
}

ESTENSIONI = {".webp", ".jpg", ".jpeg", ".png"}
VARIANTE = re.compile(r"-\d+$")


def ridimensiona(im, larghezza):
    if im.width <= larghezza:
        return im.copy()
    altezza = round(im.height * larghezza / im.width)
    return im.resize((larghezza, altezza), Image.LANCZOS)


def main():
    creati = aggiornati = 0
    for cartella, (larghezze, massimo, qualita) in REGOLE.items():
        base = ROOT / cartella
        if not base.exists():
            continue
        for src in sorted(base.iterdir()):
            if not src.is_file() or src.suffix.lower() not in ESTENSIONI:
                continue
            if VARIANTE.search(src.stem):
                continue

            im = Image.open(src)
            if im.mode in ("RGBA", "P", "LA"):
                sfondo = Image.new("RGB", im.size, (255, 255, 255))
                im = im.convert("RGBA")
                sfondo.paste(im, mask=im.split()[-1])
                im = sfondo
            else:
                im = im.convert("RGB")

            # l'originale non deve superare la misura massima utile
            if im.width > massimo:
                ridotta = ridimensiona(im, massimo)
                dst = src.with_suffix(".webp")
                ridotta.save(dst, "WEBP", quality=qualita, method=6)
                if dst != src:
                    src.unlink()
                im = ridotta
                aggiornati += 1
                print("  ridotto  %s -> %dpx" % (dst.relative_to(ROOT), massimo))

            for larghezza in larghezze:
                if im.width <= larghezza:
                    continue
                dst = src.with_name("%s-%d.webp" % (src.stem, larghezza))
                ridimensiona(im, larghezza).save(dst, "WEBP", quality=qualita, method=6)
                creati += 1
                print("  variante %s" % dst.relative_to(ROOT))

    print("\nFatto: %d varianti generate, %d originali ridotti." % (creati, aggiornati))
    print("Ricordati di committare i file nuovi insieme all'immagine originale.")


if __name__ == "__main__":
    main()
