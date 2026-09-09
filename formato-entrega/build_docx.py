"""
Genera la version .docx de la tesis alineada al formato institucional de entrega
(referencia: TESIS-FORMATO.docx, Universidad de Palermo - Facultad de Ingenieria).

Estrategia: se reutiliza el paquete OOXML de la plantilla de referencia
(styles.xml, fontTable.xml, fonts/ embebidas, footer1.xml, settings.xml, theme/)
y se reemplaza unicamente word/document.xml + word/media/, de modo que el
resultado herede exactamente las mismas definiciones de estilo que la plantilla.

El texto de la tesis sale integro de los .md de 05-tesis: no se reescribe ni se quita
nada. Lo unico que se agrega son los epigrafes de las figuras y tablas que en los .md
no tenian ninguno (ver epigrafes.py y renumeracion.md).

Uso:  python build_docx.py
"""

import os
import re
import shutil
import zipfile
import html
from pathlib import Path

from PIL import Image

import epigrafes

# --------------------------------------------------------------------------
# Rutas
# --------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
THESIS = HERE.parent
SRC = THESIS / "05-tesis"
# Plantilla de formato: version reducida de TESIS-FORMATO.docx que vive en el repo,
# con los estilos, las fuentes embebidas, el pie de pagina y el tema, pero sin el
# contenido ni las imagenes del documento de referencia. Asi el build no depende de
# un archivo suelto en Downloads. Se puede regenerar con reducir_plantilla.py.
TEMPLATE_DOCX = HERE / "plantilla-formato.docx"
TEMPLATE_ORIGINAL = Path(r"C:\Users\mboth\Downloads\TESIS-FORMATO.docx")
if not TEMPLATE_DOCX.exists() and TEMPLATE_ORIGINAL.exists():
    TEMPLATE_DOCX = TEMPLATE_ORIGINAL
BUILD = HERE / "_build"
OUT_DOCX = HERE / "Tesis-Reconstruccion3D-Patrimonio.docx"

# Orden de los archivos fuente
CHAPTERS = [
    ("capitulo1_introduccion/capitulo1_introduccion.md", None),
    ("capitulo2_marco_teorico/capitulo2_marco_teorico.md", None),
    ("capitulo3_caso_de_estudio/capitulo3_caso_de_estudio.md", None),
    ("capitulo4_diseno_experimental/capitulo4_diseno_experimental.md", None),
    ("capitulo5_analisis_resultados/capitulo5_analisis_resultados.md", None),
    ("capitulo6_pipeline_definitivo/capitulo6_pipeline_definitivo.md", None),
    ("capitulo7_conclusiones/capitulo7_conclusiones.md", None),
    ("bibliografia/bibliografia.md", "BIBLIOGRAFÍA"),
    ("glosario/glosario.md", "GLOSARIO"),
]

# --------------------------------------------------------------------------
# Constantes de formato tomadas de la plantilla de referencia
# --------------------------------------------------------------------------
TNR = 'w:ascii="Times New Roman" w:cs="Times New Roman" w:eastAsia="Times New Roman" w:hAnsi="Times New Roman"'
UBU = 'w:ascii="Ubuntu" w:cs="Ubuntu" w:eastAsia="Ubuntu" w:hAnsi="Ubuntu"'

PBDR = ('<w:pBdr><w:top w:space="0" w:sz="0" w:val="nil"/><w:left w:space="0" w:sz="0" w:val="nil"/>'
        '<w:bottom w:space="0" w:sz="0" w:val="nil"/><w:right w:space="0" w:sz="0" w:val="nil"/>'
        '<w:between w:space="0" w:sz="0" w:val="nil"/></w:pBdr>')

TEXT_WIDTH_DXA = 8250          # 11906 - 2188 (izq) - 1468 (der)
EMU_PER_DXA = 635              # 1 dxa (twip) = 635 EMU
MAX_IMG_W_EMU = TEXT_WIDTH_DXA * EMU_PER_DXA
MAX_IMG_H_EMU = 6_800_000      # ~17,8 cm de alto util para que la figura no parta la pagina

BODY_SZ = 24     # 12 pt
CAPTION_SZ = 20  # 10 pt
TABLE_SZ = 16    # 8 pt


# Escapes de markdown que Mark Text deja en los .md (b\) , 1\. , \[Tesis doctoral\]).
# Se deshacen recien al escribir el texto, para que no interfieran con el parseo
# de negritas, cursivas y enlaces.
MD_ESCAPE_RE = re.compile(r'\\([\\`*_{}\[\]()#+\-.!|>~"\'/:;,?=%$&@^])')


def esc(t):
    t = MD_ESCAPE_RE.sub(r'\1', t)
    return html.escape(t, quote=False)


# --------------------------------------------------------------------------
# Runs con formato inline
# --------------------------------------------------------------------------
def run(text, *, font=TNR, sz=BODY_SZ, b=0, i=0, u="none", color="000000"):
    if not text:
        return ""
    return (
        f'<w:r><w:rPr><w:rFonts {font}/><w:b w:val="{b}"/><w:bCs w:val="{b}"/>'
        f'<w:i w:val="{i}"/><w:iCs w:val="{i}"/><w:smallCaps w:val="0"/><w:strike w:val="0"/>'
        f'<w:color w:val="{color}"/><w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
        f'<w:u w:val="{u}"/><w:shd w:fill="auto" w:val="clear"/><w:vertAlign w:val="baseline"/>'
        f'<w:rtl w:val="0"/></w:rPr><w:t xml:space="preserve">{esc(text)}</w:t></w:r>'
    )


INLINE_RE = re.compile(
    r'(?P<link>\[(?P<ltext>[^\]]*)\]\((?P<lhref>[^)\s]+)\))'
    r'|(?P<bold>\*\*(?P<btext>.+?)\*\*)'
    r'|(?P<ital>(?<![\*\w])\*(?P<itext>[^*\n]+?)\*(?!\*))'
    r'|(?P<code>`(?P<ctext>[^`\n]+)`)',
    re.S,
)

# Etiquetas HTML sueltas que aparecen en los .md (Mark Text) y no llevan contenido propio
STRIP_TAGS_RE = re.compile(r'</?(?:u|span|br|sup|sub|em|strong)\b[^>]*>', re.I)


def clean_inline(t):
    t = STRIP_TAGS_RE.sub("", t)
    t = re.sub(r'&nbsp;', ' ', t)
    return t


def inline_runs(text, *, sz=BODY_SZ, base_b=0, base_i=0, font=TNR, color="000000", hyperlinks=None):
    """Convierte texto markdown inline en una lista de runs OOXML."""
    text = clean_inline(text)
    out = []
    pos = 0
    for m in INLINE_RE.finditer(text):
        if m.start() > pos:
            out.append(run(text[pos:m.start()], sz=sz, b=base_b, i=base_i, font=font, color=color))
        if m.group("link"):
            ltext = clean_inline(m.group("ltext"))
            href = m.group("lhref")
            if href.startswith("http") and hyperlinks is not None:
                rid = hyperlinks(href)
                inner = "".join(inline_runs(ltext, sz=sz, base_b=base_b, base_i=base_i,
                                            font=font, color="0563c1", hyperlinks=None))
                inner = inner.replace('<w:u w:val="none"/>', '<w:u w:val="single"/>')
                out.append(f'<w:hyperlink r:id="{rid}">{inner}</w:hyperlink>')
            else:
                # anclas internas (#ref-...) -> solo el texto
                out.extend(inline_runs(ltext, sz=sz, base_b=base_b, base_i=base_i,
                                       font=font, color=color, hyperlinks=hyperlinks))
        elif m.group("bold"):
            out.extend(inline_runs(m.group("btext"), sz=sz, base_b=1, base_i=base_i,
                                   font=font, color=color, hyperlinks=hyperlinks))
        elif m.group("ital"):
            out.extend(inline_runs(m.group("itext"), sz=sz, base_b=base_b, base_i=1,
                                   font=font, color=color, hyperlinks=hyperlinks))
        elif m.group("code"):
            out.append(run(m.group("ctext"), sz=sz, b=base_b, i=base_i,
                           font='w:ascii="Consolas" w:cs="Consolas" w:eastAsia="Consolas" w:hAnsi="Consolas"',
                           color=color))
        pos = m.end()
    if pos < len(text):
        out.append(run(text[pos:], sz=sz, b=base_b, i=base_i, font=font, color=color))
    return out


# --------------------------------------------------------------------------
# Parrafos
# --------------------------------------------------------------------------
def para(runs_xml, *, jc="both", first_line=482, line=480, after=0, before=0,
         style=None, left=0, page_break_before=False, keep_next=False, keep_lines=False,
         tabs=None):
    p = ['<w:p><w:pPr>']
    if style:
        p.append(f'<w:pStyle w:val="{style}"/>')
    p.append(f'<w:keepNext w:val="{1 if keep_next else 0}"/>'
             f'<w:keepLines w:val="{1 if keep_lines else 0}"/>')
    p.append(f'<w:pageBreakBefore w:val="{1 if page_break_before else 0}"/><w:widowControl w:val="1"/>')
    p.append(PBDR)
    p.append('<w:shd w:fill="auto" w:val="clear"/>')
    if tabs:
        p.append('<w:tabs>')
        for val, leader, pos in tabs:
            p.append(f'<w:tab w:val="{val}" w:leader="{leader}" w:pos="{pos}"/>')
        p.append('</w:tabs>')
    p.append(f'<w:spacing w:after="{after}" w:before="{before}" w:line="{line}" w:lineRule="auto"/>')
    p.append(f'<w:ind w:left="{left}" w:right="0" w:firstLine="{first_line}"/>')
    p.append(f'<w:jc w:val="{jc}"/>')
    p.append(f'<w:rPr><w:rFonts {TNR}/></w:rPr>')
    p.append('</w:pPr>')
    p.append(runs_xml)
    p.append('</w:p>')
    return "".join(p)


def body_para(md, hyperlinks):
    return para("".join(inline_runs(md, hyperlinks=hyperlinks)))


def empty_para(line=240):
    return para("", jc="left", first_line=0, line=line)


def heading(text, level, hyperlinks=None, *, jc="left", page_break_before=False):
    """H1 = titulo de capitulo (Ubuntu 16pt, color 2a6099, como en la plantilla).
       H2/H3/H4 = Times New Roman, negrita, 16/14/13 pt (heredado de los estilos)."""
    if level == 1:
        runs = run(clean_inline(text), font=UBU, sz=32, b=0, color="2a6099")
        return para(runs, jc=jc, first_line=0, line=240, after=120, before=240,
                    style="Heading1", page_break_before=page_break_before, keep_next=True)
    style = {2: "Heading2", 3: "Heading3", 4: "Heading4"}[level]
    before = {2: 200, 3: 140, 4: 120}[level]
    runs = "".join(inline_runs(text, sz=None, hyperlinks=hyperlinks)) if False else \
        "".join(_heading_runs(text, level))
    return para(runs, jc="left", first_line=0, line=240, after=120, before=before,
                style=style, keep_next=True)


def chapter_label(text, *, page_break_before=False):
    """Rotulo 'CAPÍTULO N' de apertura de capitulo: mismo aspecto que el titulo
    (Ubuntu 16 pt, color 2a6099) pero sin estilo Heading, para que el indice
    liste una sola entrada por capitulo (el nombre del capitulo)."""
    runs = run(clean_inline(text), font=UBU, sz=32, b=0, color="2a6099")
    return para(runs, jc="left", first_line=0, line=240, after=0, before=240,
                page_break_before=page_break_before, keep_next=True)


def _heading_runs(text, level):
    """Los estilos Heading2/3/4 ya fijan tamaño, negrita y cursiva; aca solo se
    fuerza la tipografia Times New Roman, igual que hace la plantilla."""
    text = clean_inline(text)
    return [f'<w:r><w:rPr><w:rFonts {TNR}/><w:rtl w:val="0"/></w:rPr>'
            f'<w:t xml:space="preserve">{esc(text)}</w:t></w:r>']


def caption_para(md, hyperlinks, marcador=None):
    """Epigrafe. Si se le pasa un marcador, queda referenciable: las entradas de
    la lista de tablas y de figuras enlazan ahi y sacan de ahi el numero de pagina."""
    runs = "".join(inline_runs(md, sz=CAPTION_SZ, base_i=1, hyperlinks=hyperlinks))
    if marcador:
        bid = next_bookmark_id()
        runs = (f'<w:bookmarkStart w:id="{bid}" w:name="{marcador}"/>'
                f'{runs}<w:bookmarkEnd w:id="{bid}"/>')
    return para(runs, jc="center", first_line=0, line=240, after=200, before=60,
                keep_lines=True)


_BOOKMARK_ID = [1000]


def next_bookmark_id():
    _BOOKMARK_ID[0] += 1
    return _BOOKMARK_ID[0]


def nombre_marcador(serie, numero):
    """Nombre de marcador valido para Word: letras, digitos y guion bajo."""
    serie = (serie.replace("á", "a").replace("é", "e").replace("í", "i")
                  .replace("ó", "o").replace("ú", "u"))
    serie = re.sub(r'[^A-Za-z0-9]', '', serie)
    return f"Ep_{serie}_{numero.replace('.', '_')}"


def hyperlink_interno(anchor, runs_xml):
    return f'<w:hyperlink w:anchor="{anchor}" w:history="1">{runs_xml}</w:hyperlink>'


def pageref_field(anchor, sz=BODY_SZ):
    """Numero de pagina del marcador, como campo: se actualiza con el resto."""
    rpr = (f'<w:rPr><w:rFonts {TNR}/><w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
           f'<w:rtl w:val="0"/></w:rPr>')
    return (
        f'<w:r>{rpr}<w:fldChar w:fldCharType="begin"/></w:r>'
        f'<w:r>{rpr}<w:instrText xml:space="preserve"> PAGEREF {anchor} \\h </w:instrText></w:r>'
        f'<w:r>{rpr}<w:fldChar w:fldCharType="separate"/></w:r>'
        f'<w:r>{rpr}<w:t>1</w:t></w:r>'
        f'<w:r>{rpr}<w:fldChar w:fldCharType="end"/></w:r>'
    )


def bullet_para(md, hyperlinks):
    runs = run("\u2022  ") + "".join(inline_runs(md, hyperlinks=hyperlinks))
    return para(runs, jc="both", first_line=0, left=482, line=480, after=60)


def numbered_para(num, md, hyperlinks):
    runs = run(f"{num}.  ") + "".join(inline_runs(md, hyperlinks=hyperlinks))
    return para(runs, jc="both", first_line=0, left=482, line=480, after=60)


def page_break():
    return ('<w:p><w:pPr><w:spacing w:after="0" w:before="0" w:line="240" w:lineRule="auto"/></w:pPr>'
            '<w:r><w:br w:type="page"/></w:r></w:p>')


# --------------------------------------------------------------------------
# Imagenes
# --------------------------------------------------------------------------
class MediaBag:
    def __init__(self, media_dir):
        self.dir = Path(media_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.by_src = {}
        self.rels = []      # (rId, target)
        self.n = 0
        self.ext_links = {}

    def _next_rid(self):
        return f"rIdM{len(self.rels) + len(self.ext_links) + 100}"

    def add_image(self, src_path):
        src_path = str(src_path)
        if src_path in self.by_src:
            return self.by_src[src_path]
        im = Image.open(src_path)
        # webp / gif / modos raros -> PNG (Word no los renderiza de forma fiable)
        ext = Path(src_path).suffix.lower()
        self.n += 1
        if ext in (".webp", ".gif") or im.mode not in ("RGB", "L", "RGBA"):
            im.seek(0) if ext == ".gif" else None
            im = im.convert("RGB")
            name = f"image{self.n}.png"
            im.save(self.dir / name, "PNG")
        elif ext in (".jpg", ".jpeg"):
            name = f"image{self.n}.jpg"
            shutil.copy2(src_path, self.dir / name)
        else:
            name = f"image{self.n}.png"
            if ext == ".png":
                shutil.copy2(src_path, self.dir / name)
            else:
                im.convert("RGB").save(self.dir / name, "PNG")
        rid = f"rIdImg{self.n}"
        self.rels.append((rid, f"media/{name}"))
        info = (rid, im.size, name)
        self.by_src[src_path] = info
        return info

    def add_hyperlink(self, href):
        if href in self.ext_links:
            return self.ext_links[href]
        rid = f"rIdLink{len(self.ext_links) + 1}"
        self.ext_links[href] = rid
        return rid


def image_para(src_path, media: MediaBag):
    rid, (w, h), _ = media.add_image(src_path)
    cw = w * 9525   # px -> EMU a 96 dpi
    ch = h * 9525
    scale = min(MAX_IMG_W_EMU / cw, MAX_IMG_H_EMU / ch, 1.0)
    cw, ch = int(cw * scale), int(ch * scale)
    drawing = (
        f'<w:r><w:rPr><w:rFonts {TNR}/><w:rtl w:val="0"/></w:rPr><w:drawing>'
        f'<wp:inline distT="0" distB="0" distL="0" distR="0">'
        f'<wp:extent cx="{cw}" cy="{ch}"/><wp:effectExtent l="0" t="0" r="0" b="0"/>'
        f'<wp:docPr id="{abs(hash(rid)) % 90000 + 1000}" name="{rid}"/>'
        f'<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        f'<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
        f'<pic:nvPicPr><pic:cNvPr id="0" name="{rid}"/><pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cw}" cy="{ch}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        f'</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>'
    )
    return para(drawing, jc="center", first_line=0, line=240, after=60, before=120, keep_next=True)


# --------------------------------------------------------------------------
# Tablas
# --------------------------------------------------------------------------
def table_xml(rows, hyperlinks):
    ncols = max(len(r) for r in rows)
    rows = [r + [""] * (ncols - len(r)) for r in rows]

    # anchos proporcionales al contenido, con minimo y maximo razonables
    weights = []
    for c in range(ncols):
        longest = max(len(strip_md(rows[r][c])) for r in range(len(rows)))
        weights.append(max(6, min(longest, 60)))
    total = sum(weights)
    widths = [int(TEXT_WIDTH_DXA * w / total) for w in weights]
    widths[-1] += TEXT_WIDTH_DXA - sum(widths)

    out = [f'<w:tbl><w:tblPr><w:tblStyle w:val="Table1"/>'
           f'<w:tblW w:w="{TEXT_WIDTH_DXA}" w:type="dxa"/><w:jc w:val="left"/>'
           f'<w:tblLayout w:type="fixed"/><w:tblLook w:val="0400"/></w:tblPr><w:tblGrid>']
    out += [f'<w:gridCol w:w="{w}"/>' for w in widths]
    out.append('</w:tblGrid>')

    for ri, row in enumerate(rows):
        header = ri == 0
        out.append(f'<w:trPr><w:cantSplit w:val="0"/><w:tblHeader w:val="{1 if header else 0}"/></w:trPr>'
                   if False else '')
        out.append(f'<w:tr><w:trPr><w:cantSplit w:val="0"/>'
                   f'<w:tblHeader w:val="{1 if header else 0}"/></w:trPr>')
        for ci, cell in enumerate(row):
            border_col = "cccccc" if header else "000000"
            shd = '<w:shd w:fill="000000" w:val="clear"/>' if header else ''
            out.append(
                f'<w:tc><w:tcPr><w:tcW w:w="{widths[ci]}" w:type="dxa"/><w:tcBorders>'
                f'<w:top w:color="{border_col}" w:space="0" w:sz="6" w:val="single"/>'
                f'<w:left w:color="{border_col}" w:space="0" w:sz="6" w:val="single"/>'
                f'<w:bottom w:color="000000" w:space="0" w:sz="6" w:val="single"/>'
                f'<w:right w:color="{border_col}" w:space="0" w:sz="6" w:val="single"/>'
                f'</w:tcBorders>{shd}<w:vAlign w:val="center"/></w:tcPr>'
            )
            runs = "".join(inline_runs(cell, sz=TABLE_SZ, base_b=1 if header else 0,
                                       color="ffffff" if header else "000000",
                                       hyperlinks=hyperlinks))
            if not runs:
                runs = run("", sz=TABLE_SZ)
            out.append(para(runs, jc="left", first_line=0, line=331, after=0, before=0))
            out.append('</w:tc>')
        out.append('</w:tr>')
    out.append('</w:tbl>')
    # parrafo vacio despues de la tabla (Word lo requiere entre tablas consecutivas)
    out.append(para("", jc="left", first_line=0, line=240, after=0))
    return "".join(out)


def strip_md(t):
    t = clean_inline(t)
    t = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t)
    return re.sub(r'[*`]', '', t)


# --------------------------------------------------------------------------
# Parser de markdown
# --------------------------------------------------------------------------
FULLBOLD_RE = re.compile(r'^\*\*(.+)\*\*$')


def classify_heading(text):
    """Devuelve (nivel, texto_limpio) o None si no es encabezado."""
    inner = clean_inline(text).strip()
    if not inner:
        return None
    if re.match(r'^CAPÍTULO\s+\d+$', inner, re.I):
        return (1, inner)
    if re.match(r'^\d+\.\d+\.\d+\.?\s', inner):
        return (3, inner)
    if re.match(r'^\d+\.\d+\.?\s', inner):
        return (2, inner)
    # sub-apartados sin numerar (H1 — ..., Criterio 1: ..., B2 — ..., Fuentes sobre ...)
    if len(inner) <= 130 and not inner.endswith((".", ":")):
        return (4, inner)
    if len(inner) <= 130 and inner.endswith(":"):
        return (4, inner)
    return None


# --------------------------------------------------------------------------
# Registro y renumeracion de figuras y tablas
# --------------------------------------------------------------------------
# Los .md numeran a mano solo una parte de las figuras (Cap. 5 y 6) y dejan otras
# sin epigrafe. Aca se recorre cada capitulo en orden, se numera TODO objeto
# (imagen o tabla), se conserva el texto del epigrafe cuando existe y, cuando no,
# se usa el texto alternativo que ya trae la imagen en el markdown. Nada de prosa
# nueva: si la imagen no tiene alt, el epigrafe queda solo con el rotulo.
SERIES = ("Tabla", "Figura", "Gráfico", "Imagen", "Ilustración")
CAPTION_RE = re.compile(r'^\*(?:' + "|".join(SERIES) + r')\s')
CAP_HEAD_RE = re.compile(r'^(' + "|".join(SERIES) + r')\s+(\d+\.\d+)(\s*[—\-–:]?\s*)', re.U)
XREF_RE = re.compile(
    r'\b(Tablas?|Figuras?|Gráficos?|Im[áa]genes|Imagen|Ilustraci(?:ón|ones))\s+'
    r'(\d+\.\d+(?:\s*(?:a|y|,|-|–|—)\s*\d+\.\d+)*)')
XREF_SERIE = {"tabla": "Tabla", "figura": "Figura", "gráfico": "Gráfico",
              "grafico": "Gráfico", "imagen": "Imagen", "imágen": "Imagen",
              "ilustraci": "Ilustración"}

HTML_IMG_RE = re.compile(r'<img\b[^>]*>', re.I)


def html_img_parts(tag):
    src = re.search(r'src="([^"]*)"', tag)
    alt = re.search(r'alt="([^"]*)"', tag)
    return (alt.group(1) if alt else ""), (src.group(1) if src else "")


def images_in_line(s):
    """Imagenes de una linea, en orden: markdown ![alt](src) y <img src alt>."""
    found = []
    for m in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', s):
        found.append((m.start(), m.group(1), m.group(2)))
    for m in HTML_IMG_RE.finditer(s):
        alt, src = html_img_parts(m.group(0))
        if src:
            found.append((m.start(), alt, src))
    found.sort()
    return [(a, b) for _, a, b in found]


def xref_series(word):
    w = word.lower().rstrip("s")
    for k, v in XREF_SERIE.items():
        if w.startswith(k):
            return v
    return "Figura"


# Mapa global de renumeracion: (serie, numero_viejo) -> numero_nuevo.
# Es global (no por capitulo) porque hay referencias cruzadas entre capitulos
# (p. ej. el Cap. 7 cita la Figura 6.2 y la Tabla 6.1).
REMAP = {}

# Epigrafes generados que quedaron solo con el rotulo, porque la imagen no traia
# texto alternativo en el .md. Se listan en renumeracion.md para completarlos.
SIN_TEXTO = []

# Epigrafes agregados por el generador (objetos que no lo tenian en el .md).
AGREGADOS = []


def fix_xrefs(text):
    def sub(m):
        serie = xref_series(m.group(1))
        nums = re.sub(r'\d+\.\d+',
                      lambda n: REMAP.get((serie, n.group(0)), n.group(0)),
                      m.group(2))
        return f"{m.group(1)} {nums}"
    return XREF_RE.sub(sub, text)


class ObjectRegistry:
    """Numeracion correlativa, por serie, de los objetos de un capitulo."""

    def __init__(self, chapter_no, img_series="Figura"):
        self.ch = chapter_no
        self.img_series = img_series
        self.counters = {}
        self.queue = []     # (serie, numero_nuevo, alt, ya_tenia_epigrafe)

    def assign(self, serie, old=None):
        self.counters[serie] = self.counters.get(serie, 0) + 1
        new = f"{self.ch}.{self.counters[serie]}"
        if old:
            REMAP[(serie, old)] = new
        return new


def scan_chapter(path, chapter_no):
    """Primera pasada: numera cada imagen y cada tabla del capitulo, en orden.

    Conserva las cuatro series que ya usa la tesis (Tabla, Figura, Gráfico,
    Imagen) y numera dentro de cada una segun el orden de aparicion, de modo que
    los objetos que hoy no tienen epigrafe queden intercalados donde corresponde.
    """
    lines = Path(path).read_text(encoding="utf-8").split("\n")

    def caption_at(idx, direction=1, span=3):
        if direction > 0:
            rng = range(idx + 1, min(len(lines), idx + 1 + span))
        else:
            rng = range(idx - 1, max(-1, idx - 1 - span), -1)
        for j in rng:
            if lines[j].strip():
                m = CAP_HEAD_RE.match(lines[j].strip().strip("*"))
                return (m.group(1), m.group(2)) if m else None
        return None

    # serie preferida para las imagenes de este capitulo: la que ya se usa mas
    used = {}
    for l in lines:
        m = CAP_HEAD_RE.match(l.strip().strip("*"))
        if m and m.group(1) != "Tabla":
            used[m.group(1)] = used.get(m.group(1), 0) + 1
    img_series = max(used, key=used.get) if used else "Figura"

    reg = ObjectRegistry(chapter_no, img_series)
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("|"):
            start = i
            while i < len(lines) and lines[i].strip().startswith("|"):
                i += 1
            cap = caption_at(i - 1, 1) or caption_at(start, -1)
            serie = cap[0] if cap else "Tabla"
            reg.queue.append((serie, reg.assign(serie, cap[1] if cap else None),
                              None, cap is not None))
            continue
        for alt, _src in images_in_line(s):
            cap = caption_at(i, 1)
            serie = cap[0] if cap else img_series
            reg.queue.append((serie, reg.assign(serie, cap[1] if cap else None),
                              alt, cap is not None))
        i += 1
    return reg


def alt_is_useful(alt):
    """Descarta alts que son solo el nombre del archivo."""
    a = (alt or "").strip()
    return bool(a) and not re.match(r'^[\w\-.]+\.(gif|png|jpe?g|webp)$', a, re.I)



def parse_md(path, media: MediaBag, hyperlinks, reg=None, captions_out=None):
    raw = Path(path).read_text(encoding="utf-8")
    base = Path(path).parent
    lines = raw.split("\n")
    out = []
    i = 0
    chapter_title_pending = False
    num_counter = 0
    qi = 0            # indice sobre reg.queue

    def next_assignment():
        nonlocal qi
        item = reg.queue[qi] if (reg and qi < len(reg.queue)) else None
        qi += 1
        return item

    def emit_caption(text, serie):
        """Registra el epigrafe en la lista correspondiente y lo emite.

        Cada epigrafe lleva un marcador, para que la lista de tablas y la de
        figuras puedan enlazarlo y mostrar su numero de pagina."""
        m = CAP_HEAD_RE.match(text)
        marcador = nombre_marcador(m.group(1), m.group(2)) if m else None
        if captions_out is not None:
            captions_out.setdefault(serie, []).append((text, marcador))
        return caption_para(text, hyperlinks, marcador=marcador)

    def auto_caption(serie, label, alt, descripcion=None):
        """Epigrafe para un objeto que no lo tenia en el .md.

        La descripcion sale de epigrafes.py (escrita mirando la imagen y el texto
        que la rodea); si no hay ninguna, se usa el texto alternativo del propio
        markdown, y si tampoco lo hay queda solo el rotulo y se anota en el
        reporte para completarlo a mano."""
        txt = f"{serie} {label}"
        if descripcion:
            txt += f" — {descripcion}."
        elif alt_is_useful(alt):
            txt += f" — {alt}."
        else:
            SIN_TEXTO.append((Path(path).parent.name, txt))
        if descripcion or alt_is_useful(alt):
            AGREGADOS.append((Path(path).parent.name, txt))
        return txt

    def emit_image(src, media):
        p = Path(src) if (Path(src).is_absolute() or re.match(r'^[A-Za-z]:', src)) \
            else (base / src)
        blocks = [image_para(p, media)]
        a = next_assignment()
        if a and not a[3]:                       # objeto sin epigrafe en el .md
            desc = epigrafes.para_imagen(src)
            blocks.append(emit_caption(auto_caption(a[0], a[1], a[2], desc), a[0]))
        return blocks

    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()

        if not stripped:
            i += 1
            num_counter = 0
            continue

        # ---- tabla markdown ----
        if stripped.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not re.match(r'^[\s:\-|]+$', lines[i].strip().strip("|")):
                    rows.append(cells)
                i += 1
            if rows:
                out.append(table_xml(rows, hyperlinks))
                a = next_assignment()
                if a and not a[3]:                     # tabla sin epigrafe en el .md
                    desc = epigrafes.para_tabla(base.name, rows[0])
                    out.append(emit_caption(auto_caption(a[0], a[1], None, desc), a[0]))
            continue

        # ---- imagen sola en su linea (markdown o <img>) ----
        solo = images_in_line(stripped)
        if solo and not re.sub(r'!\[[^\]]*\]\([^)]+\)|<img[^>]*>', '', stripped).strip():
            for _alt, src in solo:
                out.extend(emit_image(src, media))
            i += 1
            continue

        # ---- epigrafe de figura / tabla / grafico / imagen ----
        if CAPTION_RE.match(stripped) and stripped.endswith("*"):
            txt = stripped.strip("*")
            serie = "Figura"
            m = CAP_HEAD_RE.match(txt)
            if m:
                # el rotulo propio del epigrafe se renumera una sola vez; las
                # citas que aparezcan DENTRO del texto se remapean aparte, para
                # no volver a pisar el numero que se acaba de asignar
                serie = m.group(1)
                new = REMAP.get((serie, m.group(2)), m.group(2))
                txt = f"{serie} {new}{m.group(3)}{fix_xrefs(txt[m.end():])}"
            else:
                txt = fix_xrefs(txt)
            out.append(emit_caption(txt, serie))
            i += 1
            continue

        # ---- encabezado (linea completamente en negrita) ----
        m_h = FULLBOLD_RE.match(stripped)
        if m_h and "**" not in m_h.group(1):
            if chapter_title_pending:
                # nombre del capitulo -> este es el Heading1 que entra en el indice
                out.append(heading(m_h.group(1), 1))
                chapter_title_pending = False
                i += 1
                continue
            cls = classify_heading(m_h.group(1))
            if cls:
                lvl, txt = cls
                if lvl == 1:
                    # "CAPÍTULO N": rotulo de apertura, mismo aspecto que el titulo
                    # pero sin estilo Heading para no duplicar la entrada del indice
                    out.append(chapter_label(txt))
                    chapter_title_pending = True
                else:
                    out.append(heading(txt, lvl))
                i += 1
                continue

        # ---- vinieta ----
        if stripped.startswith("- "):
            out.append(bullet_para(fix_xrefs(stripped[2:]), hyperlinks))
            i += 1
            continue

        m_num = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        if m_num and len(stripped) > 40:
            out.append(numbered_para(m_num.group(1), fix_xrefs(m_num.group(2)), hyperlinks))
            i += 1
            continue

        # ---- separador horizontal ----
        if re.match(r'^-{3,}$|^\*{3,}$|^_{3,}$', stripped):
            i += 1
            continue

        # ---- parrafo (puede tener una imagen inline al final) ----
        buf = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(("|", "- ", "!["))\
                and not FULLBOLD_RE.match(lines[i].strip()):
            buf.append(lines[i].rstrip())
            i += 1
        text = " ".join(x.strip() for x in buf)

        inline_imgs = images_in_line(text)
        if inline_imgs:
            text = re.sub(r'!\[[^\]]*\]\([^)]+\)|<img[^>]*>', '', text).strip()
        if text:
            out.append(body_para(fix_xrefs(text), hyperlinks))
        for _, src in inline_imgs:
            out.extend(emit_image(src, media))

    return out


# --------------------------------------------------------------------------
# Documento
# --------------------------------------------------------------------------
SECT_PR = (
    '<w:sectPr>'
    '<w:footerReference r:id="rIdFooter" w:type="default"/>'
    '<w:pgSz w:h="16838" w:w="11906" w:orient="portrait"/>'
    '<w:pgMar w:bottom="2165" w:top="1468" w:left="2188" w:right="1468" '
    'w:header="0" w:footer="1825"/>'
    '<w:pgNumType w:start="1"/>'
    '</w:sectPr>'
)

DOC_OPEN = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:document '
    'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
    'xmlns:o="urn:schemas-microsoft-com:office:office" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
    'xmlns:v="urn:schemas-microsoft-com:vml" '
    'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
    'xmlns:w10="urn:schemas-microsoft-com:office:word" '
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" '
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
    'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml">'
    '<w:body>'
)


def toc_field():
    """Campo TOC de Word: se rellena al abrir el documento (Actualizar campos)."""
    return (
        '<w:p><w:pPr><w:spacing w:after="0" w:before="0" w:line="360" w:lineRule="auto"/>'
        f'<w:ind w:left="0" w:right="0" w:firstLine="0"/><w:rPr><w:rFonts {TNR}/></w:rPr></w:pPr>'
        f'<w:r><w:rPr><w:rFonts {TNR}/><w:sz w:val="{BODY_SZ}"/></w:rPr>'
        '<w:fldChar w:fldCharType="begin" w:dirty="true"/>'
        '<w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText>'
        '<w:fldChar w:fldCharType="separate"/>'
        '<w:t xml:space="preserve">Actualizar este campo en Word: Ctrl+E, F9 '
        '(o clic derecho &gt; Actualizar campos) para generar la tabla de contenido.</w:t>'
        '<w:fldChar w:fldCharType="end"/></w:r></w:p>'
    )


ESTADO = HERE / ".build-state.json"


def _huella(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def guardar_huella(path):
    """Anota como quedo el .docx recien generado."""
    import json
    from datetime import datetime
    ESTADO.write_text(json.dumps({
        "archivo": path.name,
        "sha256": _huella(path),
        "generado": datetime.now().isoformat(timespec="seconds"),
    }, indent=2), encoding="utf-8")


def resguardar_si_fue_editado(path):
    """Evita pisar en silencio ediciones hechas a mano en el .docx.

    El .docx es una salida: se regenera desde 05-tesis/ y lo que se haya escrito
    directamente en Word se perderia. Si el archivo no es el que dejo el ultimo
    build, se guarda una copia aparte y se avisa, en vez de sobrescribirlo y ya."""
    import json
    from datetime import datetime

    if not path.exists() or not ESTADO.exists():
        return
    try:
        previo = json.loads(ESTADO.read_text(encoding="utf-8")).get("sha256")
    except (ValueError, OSError):
        return
    if not previo or previo == _huella(path):
        return

    sello = datetime.now().strftime("%Y%m%d-%H%M")
    copia = path.with_name(f"{path.stem}--editado-a-mano-{sello}{path.suffix}")
    shutil.copy2(path, copia)
    print()
    print("   [ATENCION] el .docx cambio desde el ultimo build: parece editado a mano.")
    print(f"              Se guardo una copia en {copia.name} antes de regenerarlo.")
    print("              Recordar: el .docx es una salida; el texto se edita en 05-tesis/.")
    print()


def build():
    resguardar_si_fue_editado(OUT_DOCX)
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)

    # 1. desempaquetar la plantilla (aporta estilos, fuentes embebidas, footer, theme)
    with zipfile.ZipFile(TEMPLATE_DOCX) as z:
        z.extractall(BUILD)
    shutil.rmtree(BUILD / "word" / "media", ignore_errors=True)

    media = MediaBag(BUILD / "word" / "media")
    hyperlinks = media.add_hyperlink

    body = []
    captions = {}

    # 2. primera pasada sobre TODOS los capitulos: numeracion global.
    #    Tiene que estar completa antes de emitir nada, porque hay referencias
    #    cruzadas entre capitulos (el Cap. 7 cita figuras y tablas del Cap. 6).
    regs = {}
    for idx, (rel, forced_title) in enumerate(CHAPTERS, start=1):
        if not forced_title:
            regs[rel] = scan_chapter(SRC / rel, idx)

    # ---------------- Cuerpo: capitulos 1-7 + bibliografia + glosario -------
    for rel, forced_title in CHAPTERS:
        path = SRC / rel
        body.append(page_break())          # cada capitulo arranca en pagina nueva
        if forced_title:
            body.append(heading(forced_title, 1))
        body.extend(parse_md(path, media, hyperlinks,
                             reg=regs.get(rel), captions_out=captions))
    write_renumber_report()

    # ---------------- Front matter (se antepone) ---------------------------
    front = build_front_matter(media, hyperlinks, captions=captions)

    doc = DOC_OPEN + "".join(front) + "".join(body) + SECT_PR + "</w:body></w:document>"
    (BUILD / "word" / "document.xml").write_text(doc, encoding="utf-8")

    write_rels(BUILD, media)
    write_content_types(BUILD, media)
    marcar_campos_para_actualizar(BUILD)
    escribir_propiedades(BUILD)

    if OUT_DOCX.exists():
        OUT_DOCX.unlink()
    with zipfile.ZipFile(OUT_DOCX, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(BUILD.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(BUILD).as_posix())

    shutil.rmtree(BUILD, ignore_errors=True)   # el .docx ya contiene todo
    print(f"OK -> {OUT_DOCX}")
    print(f"   imagenes embebidas: {media.n}   hipervinculos: {len(media.ext_links)}")
    actualizar_campos_con_word(OUT_DOCX)
    forzar_actualizacion_al_abrir(OUT_DOCX)


def forzar_actualizacion_al_abrir(path):
    """Reinstala el flag updateFields en el .docx ya terminado.

    Word consume ese flag cuando actualiza los campos y lo borra al guardar, asi que
    hay que reponerlo despues de su pasada. Con el flag puesto, cada vez que se abra
    el documento Word refresca el indice y las listas de tablas y figuras — util si
    alguien escribe directamente en el .docx y cambia la paginacion."""
    import tempfile

    with zipfile.ZipFile(path) as z:
        piezas = {n: z.read(n) for n in z.namelist()}

    xml = piezas["word/settings.xml"].decode("utf-8")
    if "updateFields" not in xml:
        m = re.search(r'(<w:settings\b[^>]*>)', xml)
        if not m:
            return
        xml = xml[:m.end()] + '<w:updateFields w:val="true"/>' + xml[m.end():]
        piezas["word/settings.xml"] = xml.encode("utf-8")

    fd, nombre_tmp = tempfile.mkstemp(suffix=".docx", dir=str(path.parent))
    os.close(fd)                      # mkstemp deja el descriptor abierto y bloquea el archivo
    tmp = Path(nombre_tmp)
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for nombre, datos in piezas.items():
            z.writestr(nombre, datos)
    tmp.replace(path)
    print("   campos marcados para refrescarse al abrir el documento")
    guardar_huella(path)


def actualizar_campos_con_word(path):
    """Deja la tabla de contenido ya calculada dentro del .docx.

    El indice se escribe como campo TOC de Word, y Word no actualiza los campos al
    abrir un documento: hasta que alguien aprieta F9 muestra el resultado cacheado.
    Si el .docx se entrega asi, la tabla de contenido se ve vacia. Por eso, al final
    del build se abre el archivo con Word, se actualizan los campos y se vuelve a
    guardar: queda el indice armado y con numeros de pagina, y sigue siendo un campo
    vivo por si hay que refrescarlo mas adelante.

    Si Word no esta disponible, el .docx igual sirve — solo hay que actualizar los
    campos a mano (Ctrl+E, F9)."""
    import subprocess

    ps = f"""
$ErrorActionPreference = 'Stop'
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {{
    $d = $w.Documents.Open('{path}', $false, $false)
    $d.Fields.Update() | Out-Null
    foreach ($toc in $d.TablesOfContents) {{ $toc.Update() }}
    $d.Repaginate()
    $paginas = $d.ComputeStatistics(2)
    $d.Save()
    $d.Close($false)
    Write-Output "paginas=$paginas"
}} finally {{
    $w.Quit()
}}
"""
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                           capture_output=True, text=True, timeout=300)
    except Exception as e:                                    # noqa: BLE001
        print(f"   [AVISO] no se pudo abrir Word para armar el indice ({e}).")
        print("           El .docx sirve igual: actualizar los campos a mano (Ctrl+E, F9).")
        return

    salida = (r.stdout or "").strip()
    if r.returncode == 0 and "paginas=" in salida:
        paginas = salida.split("paginas=")[-1].split()[0]
        print(f"   tabla de contenido generada; {paginas} paginas")
    else:
        print("   [AVISO] Word no pudo actualizar los campos:",
              (r.stderr or salida or "sin detalle").strip()[:200])
        print("           El .docx sirve igual: actualizar los campos a mano (Ctrl+E, F9).")


# --------------------------------------------------------------------------
# Front matter (portada, aprobacion, resumen, indices)
# --------------------------------------------------------------------------
FRONT = {}   # completado por front_matter.py


def write_renumber_report():
    """Reporte de divergencia entre los .md y el .docx.

    Lo esperable es que este archivo diga que no hay ninguna: los .md son la
    fuente de verdad y el .docx los refleja tal cual. Si aparece algo, es porque
    se agregaron figuras o tablas sin epígrafe a un capítulo — hay que correr
    `propagar_epigrafes.py --aplicar` para volver a alinear."""
    cambios = {k: v for k, v in REMAP.items() if k[1] != v}
    limpio = not cambios and not AGREGADOS and not SIN_TEXTO

    L = ["# Divergencia entre los `.md` y el `.docx`", ""]
    if limpio:
        L += ["**Alineados.** El `.docx` refleja exactamente los `.md` de `05-tesis/`:",
              "todas las figuras y tablas tienen epígrafe ahí y las cuatro series",
              "(`Tabla`, `Figura`, `Gráfico`, `Imagen`) ya están correlativas por",
              "capítulo. El generador no tuvo que renumerar ni agregar nada.", ""]
    else:
        L += ["El generador tuvo que corregir cosas que los `.md` todavía no tienen.",
              "Para volver a alinear las tres versiones (capítulos, sitio web y `.docx`),",
              "correr:", "",
              "```bash",
              "python propagar_epigrafes.py --aplicar",
              "```", "",
              "y después regenerar el sitio y el `.docx`.", ""]

    L += ["## Epígrafes que cambiaron de número", ""]
    if cambios:
        L += ["| Serie | En el `.md` | En el `.docx` |", "|---|---|---|"]
        for (serie, old), new in sorted(
                cambios.items(), key=lambda x: (x[0][0], int(x[0][1].split('.')[0]),
                                                int(x[0][1].split('.')[1]))):
            L.append(f"| {serie} | {serie} {old} | **{serie} {new}** |")
    else:
        L.append("Ninguno.")
    L.append("")

    L += ["## Epígrafes agregados sobre la marcha", "",
          "Objetos sin epígrafe en el `.md`, a los que el generador les puso uno usando",
          "[`epigrafes.py`](epigrafes.py) o el texto alternativo de la propia imagen.",
          "Sólo viven en el `.docx` hasta que se corra `propagar_epigrafes.py`.", ""]
    if AGREGADOS:
        L += ["| Capítulo | Epígrafe |", "|---|---|"]
        for cap, txt in AGREGADOS:
            L.append(f"| {cap} | {txt} |")
    else:
        L.append("Ninguno.")
    L.append("")

    if SIN_TEXTO:
        L += ["", "## Epígrafes que quedaron sin descripción", "",
              "No había ni epígrafe ni texto alternativo, y tampoco hay entrada en",
              "`epigrafes.py`: quedó sólo el rótulo. Hay que completarlos.", "",
              "| Capítulo | Epígrafe |", "|---|---|"]
        for cap, txt in SIN_TEXTO:
            L.append(f"| {cap} | {txt} |")
        L.append("")
    (HERE / "renumeracion.md").write_text("\n".join(L), encoding="utf-8")


def build_front_matter(media, hyperlinks, captions=None):
    from front_matter import front_matter_blocks
    return front_matter_blocks(media, hyperlinks, captions=captions, helpers=dict(
        para=para, run=run, heading=heading, empty_para=empty_para,
        page_break=page_break, image_para=image_para, toc_field=toc_field,
        inline_runs=inline_runs, TNR=TNR, UBU=UBU, BODY_SZ=BODY_SZ,
        hyperlink_interno=hyperlink_interno, pageref_field=pageref_field,
        TEXT_WIDTH_DXA=TEXT_WIDTH_DXA,
    ))


# --------------------------------------------------------------------------
# Relationships / content types
# --------------------------------------------------------------------------
def marcar_campos_para_actualizar(build_dir):
    """Pide a Word que refresque los campos al abrir el documento.

    Con esto, si alguien escribe en el .docx y lo vuelve a abrir, Word ofrece
    actualizar el índice, la lista de tablas y la de figuras (números de página
    incluidos) en vez de dejarlos desfasados."""
    p = build_dir / "word" / "settings.xml"
    xml = p.read_text(encoding="utf-8")
    if "updateFields" in xml:
        return
    # updateFields va al principio del cuerpo de settings, el esquema es estricto
    m = re.search(r'(<w:settings\b[^>]*>)', xml)
    if not m:
        return
    xml = xml[:m.end()] + '<w:updateFields w:val="true"/>' + xml[m.end():]
    p.write_text(xml, encoding="utf-8")


def escribir_propiedades(build_dir):
    """Titulo y autoria del archivo, para que Word y el explorador los muestren."""
    import front_matter as fm
    p = build_dir / "docProps" / "core.xml"
    if not p.exists():
        return
    xml = p.read_text(encoding="utf-8")

    def poner(tag, valor):
        nonlocal xml
        valor = html.escape(valor, quote=False)
        if re.search(rf'<{tag}[^>]*>.*?</{tag}>', xml, re.S):
            xml = re.sub(rf'<{tag}([^>]*)>.*?</{tag}>', rf'<{tag}\1>{valor}</{tag}>',
                         xml, flags=re.S)
        else:
            xml = xml.replace('</cp:coreProperties>',
                              f'<{tag}>{valor}</{tag}></cp:coreProperties>')

    poner("dc:title", fm.TITULO)
    poner("dc:subject", fm.SUBTITULO)
    poner("dc:creator", fm.ALUMNA.replace("Arqta. ", "").title())
    poner("cp:keywords", "fotogrametría; SfM; NeRF; Gaussian Splatting; "
                         "patrimonio arquitectónico; HBIM")
    p.write_text(xml, encoding="utf-8")


def write_rels(build_dir, media: MediaBag):
    R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    rels.append(f'<Relationship Id="rIdStyles" Type="{R}/styles" Target="styles.xml"/>')
    rels.append(f'<Relationship Id="rIdSettings" Type="{R}/settings" Target="settings.xml"/>')
    rels.append(f'<Relationship Id="rIdFontTable" Type="{R}/fontTable" Target="fontTable.xml"/>')
    rels.append(f'<Relationship Id="rIdTheme" Type="{R}/theme" Target="theme/theme1.xml"/>')
    rels.append(f'<Relationship Id="rIdNumbering" Type="{R}/numbering" Target="numbering.xml"/>')
    rels.append(f'<Relationship Id="rIdFooter" Type="{R}/footer" Target="footer1.xml"/>')
    for rid, target in media.rels:
        rels.append(f'<Relationship Id="{rid}" Type="{R}/image" Target="{target}"/>')
    for href, rid in media.ext_links.items():
        rels.append(f'<Relationship Id="{rid}" Type="{R}/hyperlink" '
                    f'Target="{html.escape(href, quote=True)}" TargetMode="External"/>')
    rels.append('</Relationships>')
    (build_dir / "word" / "_rels" / "document.xml.rels").write_text("".join(rels), encoding="utf-8")


def write_content_types(build_dir, media: MediaBag):
    p = build_dir / "[Content_Types].xml"
    xml = p.read_text(encoding="utf-8")
    anchor = '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    extra = ""
    for ext, ct in (("png", "image/png"), ("jpg", "image/jpeg"),
                    ("jpeg", "image/jpeg"), ("gif", "image/gif")):
        if f'Extension="{ext}"' not in xml:
            extra += f'<Default ContentType="{ct}" Extension="{ext}"/>'
    xml = xml.replace(anchor, anchor + extra, 1)
    p.write_text(xml, encoding="utf-8")


if __name__ == "__main__":
    build()
