"""
Prepara la seccion "Scripts" del sitio web a partir de 04-notebooks/scripts/.

Para cada script (.py / .ps1):
  - copia el archivo tal cual a public/scripts/files/<nombre>
  - extrae una descripcion corta (primer parrafo del docstring en .py,
    primer comentario con contenido real en .ps1)
  - lo agrupa por prefijo de nombre (analyze_/build_/poc_/otros)
  - escribe el indice en public/scripts/manifest.json

No modifica los scripts originales de 04-notebooks/scripts/ -- son la fuente
de verdad. Correr de nuevo cada vez que se agregue/edite un script.
"""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(r"C:\nerfstudio_work\thesis")
SCRIPTS_SRC = ROOT / "04-notebooks" / "scripts"
WEB_DIR = ROOT / "06-sitio-web"
FILES_DIR = WEB_DIR / "public" / "scripts" / "files"
MANIFEST_PATH = WEB_DIR / "public" / "scripts" / "manifest.json"

MAX_DESC_CHARS = 240

DOCSTRING_RE = re.compile(r'^\s*(?:"""|\'\'\')(.*?)(?:"""|\'\'\')', re.DOTALL)

# scripts sin docstring/comentario inicial utilizable -- descripcion a mano.
MANUAL_DESCRIPTIONS = {
    "analyze_dense_clouds.py": "Métricas geométricas de nubes de puntos densas (COLMAP/RealityScan): cantidad de puntos, extensión y densidad espacial.",
    "analyze_textured_meshes.py": "Métricas de mallas texturizadas (.obj) de fotogrametría: vértices, triángulos y resolución de la textura.",
    "check_dense_cloud_logs.ps1": "Recorre los logs de cada caso de estudio para confirmar de qué corrida sale la nube de puntos densa final.",
}

CATEGORIES = [
    ("analyze_", "Análisis", "Calculan métricas a partir de datasets/resultados ya generados (PSNR/SSIM/LPIPS, tiempos, tasas de fallo, geometría de nubes/mallas/splats)."),
    ("build_", "Gráficos y datasets derivados", "Generan las figuras/gráficos/tablas que se citan en los capítulos, o arman datasets intermedios (máscaras, subsets, datasets híbridos)."),
    ("poc_", "Pruebas de concepto", "Exploraciones puntuales (limpieza de floaters, segmentación) que no forman parte del pipeline final pero documentan el proceso."),
]
DEFAULT_CATEGORY = ("Utilidades", "Conversión de formatos, auditoría de logs y otras tareas de soporte del pipeline.")


def clean_paragraph(text: str) -> str:
    # primer parrafo (hasta la primera linea en blanco), lineas unidas con espacio
    para = text.strip().split("\n\n")[0]
    joined = " ".join(line.strip() for line in para.splitlines() if line.strip())
    joined = re.sub(r"\s+", " ", joined).strip()
    if len(joined) > MAX_DESC_CHARS:
        joined = joined[:MAX_DESC_CHARS].rsplit(" ", 1)[0] + "…"
    return joined


def extract_description_py(text: str) -> str:
    m = DOCSTRING_RE.match(text)
    if not m:
        return ""
    return clean_paragraph(m.group(1))


def extract_description_ps1(text: str) -> str:
    lines = text.splitlines()
    collected = []
    for line in lines[:40]:
        stripped = line.strip()
        if not stripped.startswith("#"):
            if collected:
                break
            continue
        content = stripped.lstrip("#").strip()
        # saltea separadores tipo "# ====" o "#!/usr/bin/env" o lineas vacias
        if not content or set(content) <= {"=", "-"}:
            continue
        collected.append(content)
    return clean_paragraph(" ".join(collected)) if collected else ""


def categorize(name: str):
    for prefix, label, blurb in CATEGORIES:
        if name.startswith(prefix):
            return label, blurb
    return DEFAULT_CATEGORY


def main():
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    for old in FILES_DIR.iterdir():
        old.unlink()

    entries = []
    paths = sorted(SCRIPTS_SRC.glob("*.py")) + sorted(SCRIPTS_SRC.glob("*.ps1"))
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix == ".py":
            desc = extract_description_py(text)
            lang = "Python"
        else:
            desc = extract_description_ps1(text)
            lang = "PowerShell"
        if not desc:
            desc = MANUAL_DESCRIPTIONS.get(path.name, "")
        if not desc:
            print(f"  [WARN] sin descripcion detectada: {path.name}")
            desc = "(ver el código para el detalle — sin docstring/comentario inicial)"

        shutil.copy2(path, FILES_DIR / path.name)
        category, category_blurb = categorize(path.name)
        entries.append({
            "name": path.name,
            "lang": lang,
            "description": desc,
            "category": category,
            "categoryBlurb": category_blurb,
            "sizeBytes": path.stat().st_size,
            "url": f"/scripts/files/{path.name}",
        })

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nManifest: {MANIFEST_PATH}")
    print(f"Scripts copiados: {len(entries)}")


if __name__ == "__main__":
    main()
