"""
Arma los datasets Nerfstudio del componente principal (972 registradas en el
pico, 910 tras el filtrado final -- ver colmap_component_to_nerfstudio.py)
del COLMAP nativo hibrido DJI+Insta360 de Panteon Asociacion Espanola
(run-20260827-163722), siguiendo el mismo criterio ya aplicado en Templete
Central (thesis/02-templete-central/03-datasets/hibrido/):

- Splatfacto: dataset completo (910 imagenes) -- toleró datasets grandes sin
  ajuste en los otros dos casos de estudio (downscale factor 8 al entrenar).
- Nerfacto: subset de 1 cada 4 imagenes (~227) -- el ParallelDataManager de
  Nerfstudio se queda sin memoria sobre datasets de 1000+ imagenes.

Copia las imagenes como archivos reales, no junction/symlink: un junction
resulto no confiable para las lecturas concurrentes multi-hilo que hace
ParallelDataManager via Docker/WSL2 (ver build_masked_raw_nerfacto_subset.py,
que documenta el mismo hallazgo para Templete Central).
"""
import json
import shutil
from pathlib import Path

RAW_IMAGES_SOURCE = Path(r"C:\nerfstudio_work\panteon-chacarita\panteon-asociacion-catalana\dataset-clean")
NERFSTUDIO_EXPORT = Path(r"C:\nerfstudio_work\thesis\03-panteon-asociacion-espanola\01-experimentos\hybrid-dji-insta360-colmap\run-20260827-163722\nerfstudio")

OUT_ROOT = Path(r"C:\nerfstudio_work\thesis\03-panteon-asociacion-espanola\03-datasets\hibrido")


def copy_images(names, src_dir, dst_dir):
    dst_dir.mkdir(parents=True, exist_ok=True)
    names = sorted(names)
    for i, name in enumerate(names):
        dst = dst_dir / name
        if not dst.exists():
            shutil.copy2(src_dir / name, dst)
        if (i + 1) % 100 == 0:
            print(f"  [{dst_dir.parent.name}] {i + 1}/{len(names)}")
    print(f"[OK] {dst_dir} ({len(names)} archivos)")


def main():
    data = json.loads((NERFSTUDIO_EXPORT / "transforms.json").read_text(encoding="utf-8"))
    frames = data["frames"]
    print(f"[info] frames en el componente principal: {len(frames)}")

    # ---- Splatfacto: dataset completo ----
    full_dir = OUT_ROOT / f"dataset-splatfacto-{len(frames)}-full"
    copy_images(
        {Path(f["file_path"]).name for f in frames},
        RAW_IMAGES_SOURCE,
        full_dir / "images",
    )
    (full_dir / "transforms.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    shutil.copy2(NERFSTUDIO_EXPORT / "sparse_pc.ply", full_dir / "sparse_pc.ply")
    print(f"[OK] dataset Splatfacto completo -> {full_dir}")

    # ---- Nerfacto: subset de 1 cada 4 (ordenado por nombre de archivo) ----
    frames_sorted = sorted(frames, key=lambda f: Path(f["file_path"]).name)
    subset_frames = frames_sorted[::4]
    subset_dir = OUT_ROOT / f"dataset-nerfacto-{len(subset_frames)}-subset"
    copy_images(
        {Path(f["file_path"]).name for f in subset_frames},
        RAW_IMAGES_SOURCE,
        subset_dir / "images",
    )
    subset_data = {
        "frames": subset_frames,
        "applied_transform": data["applied_transform"],
        "ply_file_path": "sparse_pc.ply",
    }
    (subset_dir / "transforms.json").write_text(json.dumps(subset_data, indent=2), encoding="utf-8")
    shutil.copy2(NERFSTUDIO_EXPORT / "sparse_pc.ply", subset_dir / "sparse_pc.ply")
    print(f"[OK] dataset Nerfacto subset -> {subset_dir} ({len(subset_frames)} imagenes)")


if __name__ == "__main__":
    main()
