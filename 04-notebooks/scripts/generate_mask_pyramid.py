"""Genera masks_2/4/8 (NEAREST, para mantener el binario limpio) para un
dataset que ya tiene mask_path en transforms.json -- analogo a
generate_downscale_pyramid.py pero para la carpeta masks/."""
import json
import sys
from pathlib import Path

from PIL import Image

DATASET_DIR = Path(sys.argv[1])
FACTORS = [2, 4, 8]

masks_dir = DATASET_DIR / "masks"
files = sorted(masks_dir.glob("*.png"))
print(f"[info] {len(files)} mascaras en {masks_dir}")

transforms = json.loads((DATASET_DIR / "transforms.json").read_text(encoding="utf-8"))
declared_size = {Path(f["file_path"]).name: (f["w"], f["h"]) for f in transforms["frames"]}

for factor in FACTORS:
    out_dir = DATASET_DIR / f"masks_{factor}"
    out_dir.mkdir(exist_ok=True)
    for i, f in enumerate(files):
        out_path = out_dir / f.name
        if out_path.exists():
            out_path.unlink()
        w, h = declared_size[f.name]
        img = Image.open(f)
        new_size = (w // factor, h // factor)
        img.resize(new_size, Image.NEAREST).save(out_path)
        if (i + 1) % 100 == 0:
            print(f"  [{factor}x] {i+1}/{len(files)}")
    print(f"[OK] masks_{factor}/ lista")
