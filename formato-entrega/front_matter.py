"""
Front matter (paginas preliminares) exigido por el formato institucional:

  1. Portada
  2. Pagina de aprobacion del comite
  3. Resumen
  4. Tabla de contenido
  5. Lista de tablas
  6. Lista de figuras
  7. Lista de siglas

Los datos de portada salen de TESIS-FORMATO.docx (alumna, tutor, pie institucional)
y del titulo/subtitulo que ya usa la propia tesis en su version web (06-sitio-web,
slide de portada).

Las listas de tablas y figuras se arman con los epigrafes efectivamente emitidos en
el documento (ya renumerados), acortados para que la lista sea legible: se corta en
la primera oracion y se descartan las clausulas de fuente/nota. El epigrafe completo
queda intacto dentro del capitulo.

La lista de siglas se deriva del Glosario (05-tesis/glosario/glosario.md): se toman
las entradas cuyo termino trae una sigla, con su forma desarrollada tal como esta
escrita ahi. No se redacta texto nuevo.

El RESUMEN queda como [PENDIENTE]: no existe en 05-tesis y lo escribe la autora.
Si en algun momento aparece 05-tesis/resumen/resumen.md, se toma automaticamente.
"""

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
THESIS = HERE.parent
SRC = THESIS / "05-tesis"
LOGO = THESIS / "Logo-up.jpg"
RESUMEN_MD = SRC / "resumen" / "resumen.md"
GLOSARIO_MD = SRC / "glosario" / "glosario.md"

# --- Datos de portada -------------------------------------------------------
FACULTAD = "FACULTAD DE INGENIERÍA"
TIPO = "TESIS DE MAESTRÍA"
CARRERA = "Tecnología de la Información"
TITULO = ("Reconstrucción 3D de patrimonio arquitectónico argentino "
          "con técnicas de Computer Vision")
SUBTITULO = ("Comparativa de SfM, NeRF y 3DGS con el fin de obtener un pipeline de "
             "reconstrucción e integración con sistemas HBIM para la conformación "
             "de un archivo digital")
ALUMNA = "Arqta. MARILYN BOTHEATOZ"
TUTOR = "Mg. JUAN MANUEL MIGUEZ"
TUTOR_FIRMA = "Mg. Juan Manuel Miguez"
PIE = "BUENOS AIRES – ARGENTINA 2026"

PENDIENTE_RESUMEN = (
    "[PENDIENTE — el resumen no existe todavía en los .md de 05-tesis. "
    "El formato institucional lo exige en esta posición.]"
)


# --------------------------------------------------------------------------
# Acortado de epigrafes para las listas
# --------------------------------------------------------------------------
ABREV = ("p. ej", "vs", "ej", "cf", "aprox", "seg", "min", "art", "fig", "tab",
         "n°", "nro", "etc", "ver", "ns")


def shorten(caption, limit=140):
    """Rotulo + primera oracion util del epigrafe, sin marcas de markdown.

    En la lista no interesa la negrita ni la cursiva del epigrafe, y dejarlas
    puede cortar un `**` por la mitad al truncar. Se sacan antes de acortar."""
    t = re.sub(r'\s+', ' ', caption).strip()
    # fuera clausulas de procedencia / notas al pie del epigrafe
    t = re.split(r'\s*(?:Fuente:|Fuentes:|†)', t)[0].strip()
    # fuera negritas, cursivas y `code`: la lista va en texto plano
    t = re.sub(r'\*{1,3}|`', '', t)
    # primera oracion: punto y mayuscula, sin cortar abreviaturas ni numeros
    for m in re.finditer(r'\.(?=\s+[A-ZÁÉÍÓÚÑ¿¡])', t):
        prev = t[:m.start()].split(" ")[-1].lower().rstrip(".")
        if prev in ABREV or re.fullmatch(r'\d+', prev):
            continue
        t = t[:m.start() + 1]
        break
    t = t.rstrip(" .;,—–-")
    if len(t) > limit:
        t = t[:limit].rsplit(" ", 1)[0].rstrip(" .;,—–-") + "…"
    return t


# --------------------------------------------------------------------------
# Lista de siglas derivada del glosario
# --------------------------------------------------------------------------
SIGLA_RE = re.compile(
    r'^\*\*\s*(?P<sigla>[A-Z][A-Za-z0-9]*(?:[A-Z0-9]|[A-Z]{2,})[A-Za-z0-9]*)'
    r'(?:\s*\((?P<exp>[^)]+)\))?\s*:?\s*\*\*'
)


def leer_resumen():
    """Texto del resumen, o cadena vacia si todavia no fue escrito.

    El archivo existe desde el principio con un comentario HTML de instrucciones;
    mientras no tenga texto real, el .docx sigue mostrando el [PENDIENTE]."""
    if not RESUMEN_MD.exists():
        return ""
    t = RESUMEN_MD.read_text(encoding="utf-8")
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)      # fuera las instrucciones
    return t.strip()


def collect_siglas():
    """Entradas del glosario cuyo termino es (o contiene) una sigla."""
    if not GLOSARIO_MD.exists():
        return []
    out, seen = [], set()
    for line in GLOSARIO_MD.read_text(encoding="utf-8").split("\n"):
        s = line.strip()
        if not s.startswith("**"):
            continue
        m = SIGLA_RE.match(s)
        if not m:
            continue
        sigla = m.group("sigla").strip()
        exp = (m.group("exp") or "").strip()
        # una sigla real: al menos dos mayusculas o mayuscula+digito
        if len(sigla) < 2 or not re.search(r'[A-Z].*[A-Z0-9]', sigla):
            continue
        if not exp:
            continue
        if sigla in seen:
            continue
        seen.add(sigla)
        out.append(f"{sigla}: {exp}")
    return out


def front_matter_blocks(media, hyperlinks, helpers, captions=None):
    para = helpers["para"]
    run = helpers["run"]
    heading = helpers["heading"]
    empty = helpers["empty_para"]
    page_break = helpers["page_break"]
    image_para = helpers["image_para"]
    toc_field = helpers["toc_field"]
    inline_runs = helpers["inline_runs"]
    BODY = helpers["BODY_SZ"]

    def centered(text, sz=BODY, b=0, i=0, after=0, before=0):
        return para(run(text, sz=sz, b=b, i=i), jc="center", first_line=0,
                    line=240, after=after, before=before)

    def left(text, sz=BODY, b=0):
        return para(run(text, sz=sz, b=b), jc="left", first_line=0, line=240)

    def listed(text, marcador=None):
        """Entrada de la lista de tablas / figuras.

        Con marcador queda igual que el índice: el texto enlaza al epígrafe y a la
        derecha va el número de página como campo, con puntos de relleno. Sin
        marcador (lista de siglas) es una línea común."""
        runs = "".join(inline_runs(text, sz=BODY, hyperlinks=hyperlinks))
        if not marcador:
            return para(runs, jc="left", first_line=0, line=276, after=140)
        cuerpo = (helpers["hyperlink_interno"](marcador, runs)
                  + f'<w:r><w:rPr><w:rFonts {helpers["TNR"]}/></w:rPr><w:tab/></w:r>'
                  + helpers["pageref_field"](marcador, sz=BODY))
        return para(cuerpo, jc="left", first_line=0, line=276, after=140,
                    tabs=[("right", "dot", helpers["TEXT_WIDTH_DXA"])])

    out = []

    # ---------------------------------------------------------------- portada
    if LOGO.exists():
        out.append(image_para(LOGO, media))
    out.append(empty())
    out.append(centered(FACULTAD, sz=36, b=1))
    out.append(empty())
    out.append(centered(TIPO, sz=36, b=1))
    out.append(centered(CARRERA, sz=36, b=1))
    for _ in range(4):
        out.append(empty())
    out.append(centered(TITULO, sz=28))
    out.append(empty())
    out.append(centered(SUBTITULO, sz=28))
    for _ in range(5):
        out.append(empty())
    out.append(left("ALUMNO:"))
    out.append(left(ALUMNA))
    out.append(empty())
    out.append(empty())
    out.append(left("TUTOR DE TESIS:"))
    out.append(left(TUTOR))
    for _ in range(5):
        out.append(empty())
    out.append(centered(PIE))

    # --------------------------------------------- pagina de aprobacion
    out.append(page_break())
    out.append(heading("PÁGINA DE APROBACIÓN DEL COMITÉ", 1, jc="center"))
    for _ in range(5):
        out.append(empty())
    for nombre, cargo in (
        (TUTOR_FIRMA, "Tutor de tesis"),
        ("JURADO INTERNO 1", "Jurado Interno"),
        ("JURADO INTERNO 2", "Jurado Interno"),
        ("JURADO EXTERNO 1", "Jurado Externo"),
    ):
        out.append(centered("__________________________"))
        out.append(centered(nombre))
        out.append(centered(cargo))
        out.append(empty())
        out.append(empty())

    # ---------------------------------------------------------------- resumen
    out.append(page_break())
    out.append(heading("RESUMEN", 1, jc="center"))
    out.append(empty())
    texto_resumen = leer_resumen()
    if texto_resumen:
        for blk in texto_resumen.split("\n"):
            if blk.strip():
                out.append(para("".join(inline_runs(blk.strip(), hyperlinks=hyperlinks)),
                                jc="both", first_line=482, line=480))
    else:
        out.append(para(run(PENDIENTE_RESUMEN, i=1), jc="both", first_line=482, line=480))

    # ------------------------------------------------------ tabla de contenido
    out.append(page_break())
    out.append(heading("TABLA DE CONTENIDO", 1, jc="left"))
    out.append(toc_field())

    # --------------------------------------------- listas de tablas y figuras
    caps = captions or {}

    out.append(page_break())
    out.append(heading("LISTA DE TABLAS", 1, jc="left"))
    for texto, marcador in caps.get("Tabla", []):
        out.append(listed(shorten(texto), marcador))

    out.append(page_break())
    out.append(heading("LISTA DE FIGURAS", 1, jc="left"))
    # el resto de las series (Figura, Gráfico, Imagen) va a la lista de figuras,
    # en el mismo orden en que aparecen en el documento
    for serie in ("Figura", "Gráfico", "Imagen", "Ilustración"):
        for texto, marcador in caps.get(serie, []):
            out.append(listed(shorten(texto), marcador))

    # ------------------------------------------------------- lista de siglas
    out.append(page_break())
    out.append(heading("LISTA DE SIGLAS", 1, jc="left"))
    for s in collect_siglas():
        out.append(listed(s))

    return out
