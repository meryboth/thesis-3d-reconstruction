"""
Prepara el contenido de la tesis para el sitio web (06-sitio-web).

Para cada capitulo en ../05-tesis/capituloN_*/capituloN_*.md:
  - copia las imagenes referenciadas (rutas relativas) a public/content/assets/
    con un nombre plano (sin colisiones), reescribiendo las referencias en el markdown.
  - extrae la seccion de "sintesis"/"cierre" (para el margen derecho) a un JSON.
  - escribe el markdown resultante a public/content/capituloN.md

No modifica los .md originales de 05-tesis/ -- son la fuente de verdad de la tesis.
Correr de nuevo cada vez que cambien los capitulos o sus imagenes.
"""
import re
import json
import shutil
import hashlib
from pathlib import Path

ROOT = Path(r"C:\nerfstudio_work\thesis")
TESIS_DIR = ROOT / "05-tesis"
WEB_DIR = ROOT / "06-sitio-web"
ASSETS_DIR = WEB_DIR / "public" / "content" / "assets"
CONTENT_DIR = WEB_DIR / "public" / "content"

CHAPTERS = [
    ("cap1", 1, "Introducción", "capitulo1_introduccion/capitulo1_introduccion.md"),
    ("cap2", 2, "Marco Teórico", "capitulo2_marco_teorico/capitulo2_marco_teorico.md"),
    ("cap3", 3, "Caso de Estudio", "capitulo3_caso_de_estudio/capitulo3_caso_de_estudio.md"),
    ("cap4", 4, "Diseño Experimental", "capitulo4_diseno_experimental/capitulo4_diseno_experimental.md"),
    ("cap5", 5, "Análisis de Resultados", "capitulo5_analisis_resultados/capitulo5_analisis_resultados.md"),
    ("cap6", 6, "Pipeline Definitivo", "capitulo6_pipeline_definitivo/capitulo6_pipeline_definitivo.md"),
    ("cap7", 7, "Conclusiones", "capitulo7_conclusiones/capitulo7_conclusiones.md"),
]

# paginas de referencia de alcance general (no un capitulo puntual) -- num=None.
# El contenido es un documento propio (thesis/05-tesis/glosario/, .../bibliografia/),
# generado por 04-notebooks/scripts/build_glosario_bibliografia.py a partir del
# glosario/las referencias de Cap. 2 y 3 (correr ESE script primero si cambio algo
# ahi -- este archivo solo copia el resultado, ya no hace la extraccion).
REFERENCE_PAGES = [
    ("glosario", None, "Glosario", "glosario/glosario.md"),
    ("bibliografia", None, "Bibliografía", "bibliografia/bibliografia.md"),
]

IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

# el markdown fuente arranca con "**CAPITULO N**\n\n**Titulo**\n\n" -- lo sacamos
# porque ChapterSection ya renderiza ese encabezado (evita duplicarlo).
LEADING_TITLE_RE = re.compile(
    r"^\*\*CAP[IÍ]TULO\s+\d+\*\*\s*\n+\*\*[^*]+\*\*\s*\n+", re.IGNORECASE
)

# encabezados de seccion del cuerpo del capitulo, en sus 3 formas ya en uso:
#   **<u>5.2 Titulo</u>**            -> seccion de nivel 1 (num N.M)
#   **5.2.1 Titulo**                 -> subseccion de nivel 2 (num N.M.K)
#   **Referencias del Capitulo N**   -> seccion de nivel 1 sin numero
#   **Glosario de terminos ...**     -> seccion de nivel 1 sin numero
# Se transforman a <h2>/<h3> con id (para poder linkear/scrollear desde el
# nav) y se recolectan en un arbol {id, num, title, level, children} para el
# sub-indice de cada capitulo en el manifest.
# nota: los N.M de nivel 1 a veces vienen envueltos en <u> (Cap. 2, 5, 6) y a
# veces sin envolver (Cap. 3) -- el envoltorio se hace opcional en ambos casos.
# El orden de la alternancia (sub_num con 2 puntos antes que top_num con 1) mas
# el \s+ obligatorio despues del numero es lo que evita que "5.2.1" matchee
# como top_num="5.2" seguido de basura.
HEADING_RE = re.compile(
    r"^\*\*(?:<u>)?(?:"
    r"(?P<sub_num>\d+\.\d+\.\d+)\s+(?P<sub_title>.+?)|"
    r"(?P<top_num>\d+\.\d+)\s+(?P<top_title>.+?)|"
    r"(?P<special_title>Referencias del Cap[ií]tulo\s+\d+|Glosario de t[ée]rminos[^*\n]*)"
    # [ \t]* en vez de \s*: \s tambien matchea \n, y en modo MULTILINE eso se
    # come la linea en blanco siguiente (necesaria para que el HTML block de
    # remark no se trague el proximo parrafo).
    r")(?:</u>)?\*\*[ \t]*$",
    re.MULTILINE,
)


def anchor_id(chapter_id: str, key: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")
    return f"{chapter_id}-{slug}"


def extract_and_tag_headings(text: str, chapter_id: str):
    sections = []
    state = {"top": None}

    def repl(m):
        if m.group("top_num"):
            num, title = m.group("top_num"), m.group("top_title").strip()
            hid = anchor_id(chapter_id, num)
            node = {"id": hid, "num": num, "title": title, "children": []}
            sections.append(node)
            state["top"] = node
            return f'<h2 id="{hid}">{num} {title}</h2>'
        if m.group("sub_num"):
            num, title = m.group("sub_num"), m.group("sub_title").strip()
            hid = anchor_id(chapter_id, num)
            node = {"id": hid, "num": num, "title": title}
            if state["top"] is not None:
                state["top"]["children"].append(node)
            else:
                sections.append({**node, "children": []})
                state["top"] = sections[-1]
            return f'<h3 id="{hid}">{num} {title}</h3>'
        title = m.group("special_title").strip()
        hid = anchor_id(chapter_id, title)
        node = {"id": hid, "num": None, "title": title, "children": []}
        sections.append(node)
        state["top"] = node
        return f'<h2 id="{hid}">{title}</h2>'

    new_text = HEADING_RE.sub(repl, text)
    return new_text, sections

# fallback manual para capitulos sin seccion de sintesis/cierre propia, o donde
# la extraccion automatica no da un buen resultado de lectura en el margen
MANUAL_CONCLUSIONS = {
    "cap1": (
        "Esta tesis compara fotogrametría SfM, NeRF y 3D Gaussian Splatting sobre tres edificios "
        "patrimoniales argentinos de complejidad creciente, para sistematizar criterios de selección "
        "de técnica según el objeto a documentar y proponer un pipeline reproducible, desde la "
        "captura hasta un archivo digital publicable en la web."
    ),
    "cap3": (
        "Los tres casos de estudio —Los Paraguas de Amancio Williams, el Templete Central del "
        "Sexto Panteón y el Panteón de la Asociación Española, todos en el Cementerio de la "
        "Chacarita— representan niveles crecientes de complejidad geométrica y ornamental: de "
        "geometría simple y regular, a formas repetitivas de un único material, a ornamentación "
        "densa con deterioro documentado."
    ),
}


def slugify_name(path: Path, used: dict, chapter_id: str) -> str:
    """used: {key -> resolved source path} compartido entre TODOS los capitulos,
    para detectar colisiones entre archivos de distinto capitulo con el mismo
    nombre local (ej. media/image1.png repetido en varios capitulos)."""
    stem = path.stem
    ext = path.suffix
    base = re.sub(r"[^a-zA-Z0-9\-]+", "-", stem).strip("-").lower()
    key = f"{chapter_id}-{base}{ext}"
    resolved = str(path.resolve())
    if key not in used:
        used[key] = resolved
        return key
    if used[key] == resolved:
        return key  # mismo archivo fuente, referenciado 2 veces en el mismo capitulo
    h = hashlib.sha1(resolved.encode()).hexdigest()[:6]
    new_key = f"{chapter_id}-{base}-{h}{ext}"
    used[new_key] = resolved
    return new_key


def find_section(md_text: str, keyword: str):
    pattern = re.compile(
        r"\*\*<u>[\d.]+\s+([^<]*?" + keyword + r"[^<]*)</u>\*\*\s*\n+(.*?)(?=\n\*\*<u>|\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    return pattern.search(md_text)


def extract_conclusion(md_text: str, max_chars: int = 600) -> str:
    # preferimos "cierre del capitulo" (resumen real) por sobre "sintesis"
    # (que en el Cap. 5 es un desglose hipotesis por hipotesis, muy largo)
    m = find_section(md_text, "cierre") or find_section(md_text, "s[ií]ntesis")
    if not m:
        return ""
    body = m.group(2).strip()
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip() and not p.strip().startswith("*—")]

    out = []
    total = 0
    for p in paragraphs:
        # evita incluir un sub-encabezado en negrita sin su cuerpo (parrafo cortado)
        if total >= max_chars:
            break
        out.append(p)
        total += len(p)
    return "\n\n".join(out)


def process_chapter(chapter_id, num, title, rel_md_path, used):
    md_path = TESIS_DIR / rel_md_path
    chapter_dir = md_path.parent
    text = md_path.read_text(encoding="utf-8")
    text = LEADING_TITLE_RE.sub("", text, count=1)

    def replace_img(m):
        alt, src = m.group(1), m.group(2)
        if src.startswith("http://") or src.startswith("https://"):
            return m.group(0)
        resolved = (chapter_dir / src).resolve()
        if not resolved.exists():
            print(f"  [WARN] no existe: {resolved} (referenciado en {chapter_id})")
            return m.group(0)
        new_name = slugify_name(resolved, used, chapter_id)
        dest = ASSETS_DIR / new_name
        if not dest.exists():
            shutil.copy2(resolved, dest)
        return f"![{alt}](/content/assets/{new_name})"

    new_text = IMG_RE.sub(replace_img, text)
    new_text, sections = extract_and_tag_headings(new_text, chapter_id)

    conclusion = MANUAL_CONCLUSIONS.get(chapter_id) or extract_conclusion(text)

    out_md = CONTENT_DIR / f"{chapter_id}.md"
    out_md.write_text(new_text, encoding="utf-8")

    return {
        "id": chapter_id,
        "num": num,
        "title": title,
        "file": f"/content/{chapter_id}.md",
        "conclusion": conclusion,
        "sections": sections,
    }


def main():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for old in ASSETS_DIR.iterdir():
        old.unlink()  # limpieza: evita que queden assets huerfanos de nombres viejos
    manifest = []
    used = {}
    for chapter_id, num, title, rel_md_path in CHAPTERS + REFERENCE_PAGES:
        print(f"Procesando {chapter_id}: {rel_md_path}")
        manifest.append(process_chapter(chapter_id, num, title, rel_md_path, used))

    manifest_path = CONTENT_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nManifest: {manifest_path}")
    print(f"Assets copiados: {len(list(ASSETS_DIR.iterdir()))}")


if __name__ == "__main__":
    main()
