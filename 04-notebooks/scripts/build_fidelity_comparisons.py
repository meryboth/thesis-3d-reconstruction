"""
Material de apoyo para el analisis cualitativo de fidelidad geometrica
(Cap. 4, seccion 4.8): grillas comparativas Foto original | Nerfacto |
Splatfacto, en la MISMA pose de camara, para que la inspeccion visual
(zonas bien/mal reproducidas, por sitio y tecnica) se haga sobre imagenes
ya alineadas en vez de tener que buscarlas a mano.

No cubre SfM/fotogrametria clasica (mallas .obj) porque este entorno no
tiene un renderer 3D disponible (ni trimesh ni matplotlib instalados, sin
Nerfstudio/Blender). Para esa tecnica hace falta un screenshot manual desde
RealityScan/CloudCompare/MeshLab -- ver el archivo LEEME.txt que este script
deja en cada carpeta de salida con instrucciones de donde guardarlo.

Para cada sitio/metodo de captura, se eligen N frames espaciados a lo largo
del recorrido (no solo el primero) usando el conjunto de nombres en comun
entre foto-original, render-nerfacto y render-splatfacto.

Escribe en thesis/00-auditoria/fidelidad-geometrica/<caso>/<metodo>/:
  comparacion_<frame>.jpg   (Foto | Nerfacto | Splatfacto, con etiquetas)
  LEEME.txt                 (instrucciones para agregar el screenshot de SfM)
"""

import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAW = Path(r"C:\nerfstudio_work")
OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\fidelidad-geometrica")

N_FRAMES = 5
PANEL_WIDTH = 900  # cada panel se redimensiona a este ancho antes de pegar
LABEL_HEIGHT = 34

# (caso, metodo_captura): { "foto": dir, "nerfacto": dir, "splatfacto": dir }
CASES = {
    ("01-paraguas-vicentelopez", "dji"): {
        "foto": RAW / "paraguas-vicentelopez/ns-data-drone/images",
        "nerfacto": RAW / "paraguas-vicentelopez/renders/nerfacto/train/rgb",
        "splatfacto": RAW / "paraguas-vicentelopez/renders/splatfacto/train/rgb",
    },
    ("02-templete-central", "dji"): {
        "foto": RAW / "panteon-chacarita/templete-central/ns-from-realityscan-nerf308/images",
        "nerfacto": RAW / "panteon-chacarita/templete-central/renders/nerf/templete-central-nerfacto-train/train/rgb",
        "splatfacto": RAW / "panteon-chacarita/templete-central/renders-templete-splat-ds8/templete-splat-dataset-train.mp4/train/rgb",
    },
    ("02-templete-central", "insta360"): {
        "foto": RAW / "panteon-chacarita/templete-central/renders/templete-central-insta360-nerfacto-dataset-traj/train/gt-rgb",
        "nerfacto": RAW / "panteon-chacarita/templete-central/renders/templete-central-insta360-nerfacto-dataset-traj/train/rgb",
        "splatfacto": RAW / "panteon-chacarita/templete-central/renders/templete-central-insta360-splatfacto-dataset-traj/train/rgb",
    },
    ("03-panteon-asociacion-catalana", "dji"): {
        "foto": RAW / "panteon-chacarita/panteon-asociacion-catalana/renders/nerf/panteon-catalan-nerfacto-train/train/gt-rgb",
        "nerfacto": RAW / "panteon-chacarita/panteon-asociacion-catalana/renders/nerf/panteon-catalan-nerfacto-train/train/rgb",
        "splatfacto": RAW / "panteon-chacarita/panteon-asociacion-catalana/renders/splat/panteon-catalan-splat-ds8-train/train/rgb",
    },
    ("03-panteon-asociacion-catalana", "insta360"): {
        "foto": RAW / "panteon-chacarita/panteon-asociacion-catalana/renders/panteon-catalana-insta360-nerfacto-dataset-traj/train/gt-rgb",
        "nerfacto": RAW / "panteon-chacarita/panteon-asociacion-catalana/renders/panteon-catalana-insta360-nerfacto-dataset-traj/train/rgb",
        "splatfacto": RAW / "panteon-chacarita/panteon-asociacion-catalana/renders/panteon-catalana-insta360-splatfacto-dataset-traj/train/rgb",
    },
}

IMG_EXTS = {".jpg", ".jpeg", ".png"}


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", str(s))]


def index_by_stem(folder):
    if not folder.exists():
        return {}
    return {p.stem: p for p in folder.iterdir() if p.suffix.lower() in IMG_EXTS}


def pick_spread_frames(names, n):
    names = sorted(names, key=natural_key)
    if len(names) <= n:
        return names
    idx = np.linspace(0, len(names) - 1, n).round().astype(int)
    return [names[i] for i in sorted(set(idx))]


def load_panel(path, width):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    new_h = int(h * width / w)
    return img.resize((width, new_h), Image.BICUBIC)


def make_comparison(paths_and_labels, width):
    # apilados uno abajo del otro (no lado a lado) para que cada panel se
    # pueda ver a un tamano legible, en vez de quedar chico por dividir el
    # ancho entre 3.
    panels = [load_panel(p, width) for p, _ in paths_and_labels]
    row_h = LABEL_HEIGHT + max(p.height for p in panels)

    canvas = Image.new("RGB", (width, row_h * len(panels)), "white")
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except Exception:
        font = ImageFont.load_default()

    for i, (panel, (_, label)) in enumerate(zip(panels, paths_and_labels)):
        y = i * row_h
        draw.rectangle([0, y, width, y + LABEL_HEIGHT], fill=(30, 30, 30))
        draw.text((10, y + 6), label, fill="white", font=font)
        canvas.paste(panel, (0, y + LABEL_HEIGHT))

    return canvas


def write_leeme(out_dir, caso, metodo):
    text = f"""LEEME — material de apoyo para fidelidad geometrica ({caso} / {metodo})

Las imagenes comparacion_*.jpg de esta carpeta muestran, en la misma pose de
camara: Foto original | Render Nerfacto | Render Splatfacto.

FALTA la comparacion con SfM (fotogrametria clasica / malla texturizada):
este entorno no tiene un renderer 3D disponible para generar automaticamente
una vista de la malla .obj desde la misma pose de camara.

Para completar la comparacion de 3 tecnicas, abrir la malla correspondiente
en RealityScan, CloudCompare o MeshLab, ubicar (aproximadamente) el mismo
punto de vista que las fotos de esta carpeta, y guardar un screenshot como:
  malla_sfm_<nombre_del_frame>.jpg

en esta misma carpeta, para poder armar la comparacion completa de a 4
paneles (Foto | SfM | Nerfacto | Splatfacto) durante la redaccion del
Capitulo 5.
"""
    (out_dir / "LEEME.txt").write_text(text, encoding="utf-8")


def main():
    for (caso, metodo), dirs in CASES.items():
        foto_idx = index_by_stem(dirs["foto"])
        nerf_idx = index_by_stem(dirs["nerfacto"])
        splat_idx = index_by_stem(dirs["splatfacto"])

        common = set(foto_idx) & set(nerf_idx) & set(splat_idx)

        print(f"\n{caso} :: {metodo} — foto:{len(foto_idx)} nerf:{len(nerf_idx)} "
              f"splat:{len(splat_idx)} comunes:{len(common)}")

        if not common:
            print("  [SKIP] sin frames en comun entre las 3 fuentes")
            continue

        frames = pick_spread_frames(common, N_FRAMES)

        out_dir = OUT_DIR / caso / metodo
        out_dir.mkdir(parents=True, exist_ok=True)
        write_leeme(out_dir, caso, metodo)

        for name in frames:
            paths_and_labels = [
                (foto_idx[name], "Foto original"),
                (nerf_idx[name], "Nerfacto"),
                (splat_idx[name], "Splatfacto"),
            ]
            canvas = make_comparison(paths_and_labels, PANEL_WIDTH)
            out_path = out_dir / f"comparacion_{name}.jpg"
            canvas.save(out_path, quality=90)
            print(f"  [OK] {out_path.name}")


if __name__ == "__main__":
    main()
