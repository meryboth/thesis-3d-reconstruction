"""Corre el mismo analisis de analyze_gaussian_splats.py sobre el export de
Splatfacto entrenado con mascara de entrenamiento RMBG, para comparar contra
el export raw ya documentado (315,787 gaussianas, Cap.5 5.3.1)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analyze_gaussian_splats import analyze_splat, write_outputs, make_plots  # noqa: E402

SPLAT_PATH = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\splatfacto-masked-raw-training\export\splat.ply")
OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\masking-comparison")
OUT_DIR.mkdir(parents=True, exist_ok=True)

metadata, raw = analyze_splat(SPLAT_PATH)

# escribir junto al export original (igual que el resto del proyecto) y
# tambien copiar a 00-auditoria para tenerlo cross-referenciable sin salir
# de la estructura de carpetas crudas
json_path, log_path = write_outputs(SPLAT_PATH, metadata)
plot_paths = make_plots(SPLAT_PATH, metadata, raw)

import shutil
for p in [json_path, log_path] + plot_paths:
    shutil.copy2(p, OUT_DIR / p.name)

print(f"Gaussianas: {metadata['gaussian_count']:,}")
print(f"Bounding box extent: {metadata['geometry']['bounding_box']['extent']}")
print(f"Bounding box volume: {metadata['geometry']['bounding_box']['volume']:,.0f}")
print(f"Centroide: {metadata['geometry']['centroid']}")
print(f"Gaussianas/unidad bbox: {metadata['geometry']['gaussians_per_bbox_unit']}")
print(f"Opacidad alpha_mean: {metadata['opacity']['alpha_mean']:.4f}")
print(f"Copiado a: {OUT_DIR}")
