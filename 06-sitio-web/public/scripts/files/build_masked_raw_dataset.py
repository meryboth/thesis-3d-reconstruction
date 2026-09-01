"""
Arma el dataset "dataset-masked-raw-1232-splatfacto": el dataset RAW del
Templete Central (imagenes originales, sin tocar) + una mascara de
entrenamiento Nerfstudio por frame (RMBG-2.0, ver build_rmbg_masks_full_dataset.py)
para que Splatfacto ignore el fondo (cielo, edificios de contexto, piso)
durante el entrenamiento en vez de reconstruirlo -- ver conversacion sobre
por que el inpainting agresivo con LaMa no funciona para mascaras de ese
tamano (POC en clean_dataset_comfyui_aggressive_poc.py).

No copia las imagenes originales (pesarian ~10GB de nuevo) -- crea una
junction de Windows a la carpeta images/ del dataset raw ya existente, asi
`file_path` en transforms.json puede seguir apuntando a "images/XXXXX.png"
sin cambios.
"""
import json
import subprocess
from pathlib import Path

from PIL import Image

RAW_DATASET = Path(r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-splatfacto-1232-full")
NEW_DATASET = Path(r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-masked-raw-1232-splatfacto")
MASKS_DIR = NEW_DATASET / "masks"  # ya generadas por build_rmbg_masks_full_dataset.py
FACTORS = [2, 4, 8]


def ensure_images_junction():
    link = NEW_DATASET / "images"
    target = RAW_DATASET / "images"
    if link.exists():
        print(f"[skip] {link} ya existe")
        return
    subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], check=True)
    print(f"[OK] junction {link} -> {target}")


def build_transforms():
    raw = json.loads((RAW_DATASET / "transforms.json").read_text(encoding="utf-8"))
    n_masks = len(list(MASKS_DIR.glob("*.png")))
    assert n_masks == len(raw["frames"]), f"{n_masks} mascaras vs {len(raw['frames'])} frames -- deberian ser iguales"

    for frame in raw["frames"]:
        stem = Path(frame["file_path"]).stem
        mask_path = MASKS_DIR / f"{stem}.png"
        assert mask_path.exists(), f"falta mascara para {stem}"
        frame["mask_path"] = f"masks/{stem}.png"

    out_path = NEW_DATASET / "transforms.json"
    out_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
    print(f"[OK] {out_path} ({len(raw['frames'])} frames con mask_path)")
    return raw


def copy_sparse_pc():
    import shutil

    src = RAW_DATASET / "sparse_pc.ply"
    dst = NEW_DATASET / "sparse_pc.ply"
    shutil.copy2(src, dst)
    print(f"[OK] {dst}")


def generate_pyramid(transforms, subdir, resample, src_dir):
    declared_size = {Path(f["file_path"]).name: (f["w"], f["h"]) for f in transforms["frames"]}
    files = sorted(src_dir.glob("*.png"))
    assert len(files) == len(declared_size), f"{len(files)} archivos en {src_dir} vs {len(declared_size)} frames"

    for factor in FACTORS:
        out_dir = NEW_DATASET / f"{subdir}_{factor}"
        out_dir.mkdir(exist_ok=True)
        for i, f in enumerate(files):
            out_path = out_dir / f.name
            if out_path.exists():
                out_path.unlink()
            w, h = declared_size[f.name]
            img = Image.open(f)
            new_size = (w // factor, h // factor)  # floor, igual que Cameras.rescale_output_resolution
            img.resize(new_size, resample).save(out_path)
            if (i + 1) % 300 == 0:
                print(f"  [{subdir}_{factor}] {i+1}/{len(files)}")
        print(f"[OK] {subdir}_{factor}/ lista")


def main():
    NEW_DATASET.mkdir(parents=True, exist_ok=True)
    ensure_images_junction()
    transforms = build_transforms()
    copy_sparse_pc()
    generate_pyramid(transforms, "images", Image.LANCZOS, NEW_DATASET / "images")
    generate_pyramid(transforms, "masks", Image.NEAREST, MASKS_DIR)
    print("\nFINAL: dataset listo en", NEW_DATASET)


if __name__ == "__main__":
    main()
