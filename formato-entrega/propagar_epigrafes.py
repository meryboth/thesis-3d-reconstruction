"""
Propaga a los .md de 05-tesis la numeracion y los epigrafes que hasta ahora vivian
solo en el .docx de entrega, para que capitulos, sitio web y .docx digan lo mismo.

Hace tres cosas sobre cada capitulo:

  1. Renumera los epigrafes existentes para que cada serie (Tabla, Figura, Grafico,
     Imagen) quede correlativa por orden de aparicion dentro del capitulo.
  2. Reescribe las citas del cuerpo del texto ("ver Figura 5.16") con el numero nuevo.
  3. Inserta el epigrafe de los objetos que no tenian ninguno, con el texto de
     epigrafes.py.

Es idempotente: una vez propagado, volver a correrlo no cambia nada, porque la
numeracion de los .md ya coincide con la que calcula el escaneo.

Uso:
    python propagar_epigrafes.py            # dry-run: muestra el diff, no escribe
    python propagar_epigrafes.py --aplicar  # escribe los .md

Despues de aplicar hay que regenerar el sitio web y el .docx (ver la skill
sync-tesis).
"""

import argparse
import re
import sys
from pathlib import Path

import build_docx as B
import epigrafes

HERE = Path(__file__).resolve().parent
SRC = B.SRC


def leer(path):
    """Devuelve (lineas, terminador) preservando el fin de linea del archivo."""
    raw = path.read_bytes().decode("utf-8")
    eol = "\r\n" if "\r\n" in raw else "\n"
    return raw.replace("\r\n", "\n").split("\n"), eol


def escribir(path, lineas, eol):
    path.write_bytes(eol.join(lineas).encode("utf-8"))


def caption_serie_num(linea):
    """Si la linea es un epigrafe, devuelve (serie, numero, separador, resto)."""
    s = linea.strip()
    if not (s.startswith("*") and s.endswith("*") and not s.startswith("**")):
        return None
    inner = s.strip("*")
    m = B.CAP_HEAD_RE.match(inner)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3), inner[m.end():]


def procesar(path, reg):
    """Devuelve las lineas nuevas del capitulo y el resumen de cambios."""
    lineas, eol = leer(path)
    out = []
    cambios = {"renumerados": 0, "citas": 0, "insertados": []}
    qi = 0
    i = 0

    def siguiente():
        nonlocal qi
        item = reg.queue[qi] if qi < len(reg.queue) else None
        qi += 1
        return item

    def insertar_epigrafe(serie, num, desc, alt):
        texto = desc or (alt if B.alt_is_useful(alt) else None)
        if not texto:
            return None
        texto = texto.rstrip(" .")
        return f"*{serie} {num} — {texto}.*"

    while i < len(lineas):
        linea = lineas[i]
        s = linea.strip()

        # ---- bloque de tabla ----
        if s.startswith("|"):
            filas = []
            while i < len(lineas) and lineas[i].strip().startswith("|"):
                celdas = [c.strip() for c in lineas[i].strip().strip("|").split("|")]
                if not re.match(r'^[\s:\-|]+$', lineas[i].strip().strip("|")):
                    filas.append(celdas)
                out.append(lineas[i])
                i += 1
            a = siguiente()
            if a and not a[3]:
                desc = epigrafes.para_tabla(path.parent.name, filas[0] if filas else [])
                nuevo = insertar_epigrafe(a[0], a[1], desc, None)
                if nuevo:
                    out.append("")
                    out.append(nuevo)
                    cambios["insertados"].append(nuevo)
                    if i < len(lineas) and lineas[i].strip():
                        out.append("")
            continue

        # ---- epigrafe existente ----
        cap = caption_serie_num(linea)
        if cap:
            serie, num, sep, resto = cap
            nuevo_num = B.REMAP.get((serie, num), num)
            resto_fix = B.fix_xrefs(resto)
            if nuevo_num != num:
                cambios["renumerados"] += 1
            if resto_fix != resto:
                cambios["citas"] += 1
            sangria = linea[:len(linea) - len(linea.lstrip())]
            out.append(f"{sangria}*{serie} {nuevo_num}{sep}{resto_fix}*")
            i += 1
            continue

        # ---- linea con imagen(es) ----
        imgs = B.images_in_line(s)
        if imgs:
            # la linea puede llevar citas ademas de la imagen
            fix = B.fix_xrefs(linea)
            if fix != linea:
                cambios["citas"] += 1
            out.append(fix)
            i += 1
            pendientes = []
            for alt, _src in imgs:
                a = siguiente()
                if a and not a[3]:
                    desc = epigrafes.para_imagen(_src)
                    nuevo = insertar_epigrafe(a[0], a[1], desc, alt)
                    if nuevo:
                        pendientes.append(nuevo)
            for nuevo in pendientes:
                out.append("")
                out.append(nuevo)
                cambios["insertados"].append(nuevo)
            if pendientes and i < len(lineas) and lineas[i].strip():
                out.append("")
            continue

        # ---- texto normal: solo se remapean las citas ----
        fix = B.fix_xrefs(linea)
        if fix != linea:
            cambios["citas"] += 1
        out.append(fix)
        i += 1

    return out, eol, cambios


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aplicar", action="store_true",
                    help="escribe los .md (por defecto solo muestra que cambiaria)")
    args = ap.parse_args()

    # 1. escaneo global primero: hay citas cruzadas entre capitulos
    regs = {}
    for idx, (rel, forzado) in enumerate(B.CHAPTERS, start=1):
        if not forzado:
            regs[rel] = B.scan_chapter(SRC / rel, idx)

    total = {"renumerados": 0, "citas": 0, "insertados": 0}
    for rel in regs:
        path = SRC / rel
        nuevas, eol, cambios = procesar(path, regs[rel])
        originales, _ = leer(path)

        n_ins = len(cambios["insertados"])
        total["renumerados"] += cambios["renumerados"]
        total["citas"] += cambios["citas"]
        total["insertados"] += n_ins

        if nuevas == originales:
            print(f"= {path.name}: sin cambios")
            continue

        print(f"~ {path.name}: {cambios['renumerados']} epígrafes renumerados, "
              f"{cambios['citas']} líneas con citas actualizadas, "
              f"{n_ins} epígrafes insertados")
        for nuevo in cambios["insertados"]:
            print(f"    + {nuevo[:120]}")

        if args.aplicar:
            escribir(path, nuevas, eol)

    print()
    print(f"TOTAL: {total['renumerados']} renumerados, {total['citas']} líneas con "
          f"citas actualizadas, {total['insertados']} epígrafes insertados")
    if args.aplicar:
        print("Aplicado. Regenerar ahora el sitio web y el .docx.")
    else:
        print("Dry-run: no se escribió nada. Volver a correr con --aplicar.")


if __name__ == "__main__":
    main()
