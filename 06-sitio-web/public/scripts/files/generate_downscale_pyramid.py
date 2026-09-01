"""
Genera las carpetas images_2/ images_4/ images_8/ (piramide de resolucion)
que Nerfstudio espera de antemano cuando se usa --downscale-factor con la
FullImageDatamanager -- normalmente las genera ns-process-data, pero este
dataset se armo a mano (build_comfyui_dataset_with_realityscan_poses.py),
asi que hay que generarlas aparte.
"""
import json
import sys
from pathlib import Path

from PIL import Image

DATASET_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-comfyui-clean-1228-splatfacto")
FACTORS = [2, 4, 8]

images_dir = DATASET_DIR / "images"
files = sorted(list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg")))
print(f"[info] {len(files)} imagenes en {images_dir}")

# El w/h DECLARADO en transforms.json por frame no siempre coincide exacto con
# el tamaño real del archivo .png (RealityScan varia 1px entre fotos) -- hay
# que redimensionar en base al w/h declarado (lo que arma la camara de
# Nerfstudio), no al tamaño real leido del archivo, si no el floor(w/factor)
# calculado ahi puede terminar 1px distinto del que calculamos aca.
transforms = json.loads((DATASET_DIR / "transforms.json").read_text(encoding="utf-8"))
declared_size = {Path(f["file_path"]).name: (f["w"], f["h"]) for f in transforms["frames"]}

for factor in FACTORS:
    out_dir = DATASET_DIR / f"images_{factor}"
    out_dir.mkdir(exist_ok=True)
    for i, f in enumerate(files):
        out_path = out_dir / f.name
        if out_path.exists():
            out_path.unlink()  # se regenera siempre: el tamaño puede haber cambiado con el fix
        w, h = declared_size[f.name]
        img = Image.open(f)
        # Nerfstudio usa scale_rounding_mode="floor" (Cameras.rescale_output_resolution)
        new_size = (w // factor, h // factor)
        img.resize(new_size, Image.LANCZOS).save(out_path)
        if (i + 1) % 200 == 0:
            print(f"  [{factor}x] {i+1}/{len(files)}")
    print(f"[OK] images_{factor}/ lista")
