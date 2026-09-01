"""
Arma el subset de 308 frames (cada 4to) del dataset RAW con mascara RMBG,
para Nerfacto -- mismo subset ya usado en el Nerfacto raw y en el Nerfacto
del Dataset B (ComfyUI, H2), para comparabilidad directa frame a frame.

Copia imagenes y mascaras como archivos reales (no junction): un junction,
incluso de un solo salto, resulto no confiable para las lecturas concurrentes
multi-hilo que hace ParallelDataManager via Docker/WSL2 -- fallaba de forma
intermitente con FileNotFoundError sobre archivos que existian perfectamente
bien a nivel de Windows (confirmado leyendolos byte a byte). Para 308 imagenes
(~2.5GB) copiar es barato comparado con duplicar el dataset completo de 1232.
"""
import json
import shutil
from pathlib import Path

MASKED_1232 = Path(r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-masked-raw-1232-splatfacto")
RAW_IMAGES_SOURCE = Path(r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-splatfacto-1232-full\images")
RAW_SUBSET_IMAGES_DIR = Path(r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-nerfacto-308-subset\images")
OUT_DIR = Path(r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-masked-raw-308-nerfacto-subset")


def copy_subset(names, src_dir, dst_dir):
    dst_dir.mkdir(parents=True, exist_ok=True)
    for i, name in enumerate(sorted(names)):
        dst = dst_dir / name
        if not dst.exists():
            shutil.copy2(src_dir / name, dst)
        if (i + 1) % 100 == 0:
            print(f"  [{dst_dir.name}] {i+1}/{len(names)}")
    print(f"[OK] {dst_dir} ({len(names)} archivos)")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for p in (OUT_DIR / "images", OUT_DIR / "masks"):
        if p.is_symlink() or (p.exists() and not p.is_dir()):
            p.unlink()
        elif p.exists():
            # puede ser un junction viejo (reparse point) -- rmdir lo saca sin
            # tocar el contenido real del otro lado
            import os

            try:
                os.rmdir(p)
            except OSError:
                pass

    subset_names = {p.name for p in RAW_SUBSET_IMAGES_DIR.glob("*.png")}
    print(f"[info] subset objetivo: {len(subset_names)}")

    copy_subset(subset_names, RAW_IMAGES_SOURCE, OUT_DIR / "images")
    copy_subset(subset_names, MASKED_1232 / "masks", OUT_DIR / "masks")

    data = json.loads((MASKED_1232 / "transforms.json").read_text(encoding="utf-8"))
    kept_frames = [f for f in data["frames"] if Path(f["file_path"]).name in subset_names]
    print(f"[info] frames con pose+mascara conservados: {len(kept_frames)}")
    assert all("mask_path" in f for f in kept_frames)

    out_data = {
        "frames": kept_frames,
        "applied_transform": data["applied_transform"],
        "ply_file_path": "sparse_pc.ply",
    }
    (OUT_DIR / "transforms.json").write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    shutil.copy2(MASKED_1232 / "sparse_pc.ply", OUT_DIR / "sparse_pc.ply")
    print(f"[OK] dataset armado en {OUT_DIR}")


if __name__ == "__main__":
    main()
