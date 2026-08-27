"""
Arma el dataset Nerfacto del Dataset B (curado por ComfyUI) sobre el MISMO
subset de 308 frames (cada 4to) que ya se uso para el Nerfacto del dataset
raw -- para que la comparacion H2 sea directa, frame a frame. Reusa las
poses de RealityScan, igual que build_comfyui_dataset_with_realityscan_poses.py.
"""
import json
import shutil
from pathlib import Path

SRC_TRANSFORMS = Path(r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-splatfacto-1232-full\transforms.json")
SRC_SPARSE_PC = Path(r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-splatfacto-1232-full\sparse_pc.ply")
CLEAN_IMAGES_DIR = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\sfm-de-comfy-ui\images")
RAW_SUBSET_IMAGES_DIR = Path(r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-nerfacto-308-subset\images")

OUT_DIR = Path(r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-comfyui-clean-307-nerfacto-subset")
OUT_IMAGES_DIR = OUT_DIR / "images"


def main():
    OUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    subset_names = {p.name for p in RAW_SUBSET_IMAGES_DIR.glob("*.png")}
    clean_names = {p.name for p in CLEAN_IMAGES_DIR.glob("*.png")}
    keep_names = subset_names & clean_names
    print(f"[info] subset raw (Nerfacto ya usado): {len(subset_names)}")
    print(f"[info] disponibles en version limpia: {len(keep_names)}")

    data = json.loads(SRC_TRANSFORMS.read_text(encoding="utf-8"))
    kept_frames = [f for f in data["frames"] if Path(f["file_path"]).name in keep_names]
    print(f"[info] frames con pose conservados: {len(kept_frames)}")

    for frame in kept_frames:
        name = Path(frame["file_path"]).name
        dst = OUT_IMAGES_DIR / name
        if not dst.exists():
            shutil.copy2(CLEAN_IMAGES_DIR / name, dst)

    out_data = {
        "frames": kept_frames,
        "applied_transform": data["applied_transform"],
        "ply_file_path": "sparse_pc.ply",
    }
    (OUT_DIR / "transforms.json").write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    shutil.copy2(SRC_SPARSE_PC, OUT_DIR / "sparse_pc.ply")
    print(f"[OK] dataset armado en {OUT_DIR}")


if __name__ == "__main__":
    main()
