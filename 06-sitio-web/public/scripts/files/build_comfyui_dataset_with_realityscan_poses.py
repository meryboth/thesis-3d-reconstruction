"""
Arma el dataset Nerfstudio del Dataset B (curado por ComfyUI) reusando las
poses de camara ya resueltas por RealityScan sobre el dataset raw -- en vez
de volver a correr SfM sobre las imagenes limpias (COLMAP nativo no converge
en este dataset, ver 00-auditoria/sfm-registration-comparison).

Justificacion: limpiar distractores con inpainting no mueve la camara, solo
edita contenido de pixeles en regiones puntuales -- la pose de cada toma es
una propiedad de la captura, no de la imagen resultante. Como las 1228
imagenes limpias son un subconjunto exacto (mismos nombres de archivo) de
las 1232 originales, se puede filtrar transforms.json del dataset raw ya
armado y apuntar file_path a las imagenes limpias.

Fuente de poses: thesis/02-templete-central/03-datasets/dji/dataset-splatfacto-1232-full/transforms.json
Fuente de imagenes limpias: panteon-chacarita/templete-central/sfm-de-comfy-ui/images/
"""
import json
import shutil
from pathlib import Path

SRC_TRANSFORMS = Path(r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-splatfacto-1232-full\transforms.json")
SRC_SPARSE_PC = Path(r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-splatfacto-1232-full\sparse_pc.ply")
CLEAN_IMAGES_DIR = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\sfm-de-comfy-ui\images")

OUT_DIR = Path(r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-comfyui-clean-1228-splatfacto")
OUT_IMAGES_DIR = OUT_DIR / "images"


def main():
    OUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    clean_names = {p.name for p in CLEAN_IMAGES_DIR.glob("*.png")}
    print(f"[info] imagenes limpias disponibles: {len(clean_names)}")

    data = json.loads(SRC_TRANSFORMS.read_text(encoding="utf-8"))
    all_frames = data["frames"]
    print(f"[info] frames en dataset raw (poses RealityScan): {len(all_frames)}")

    kept_frames = []
    for frame in all_frames:
        name = Path(frame["file_path"]).name
        if name in clean_names:
            kept_frames.append(frame)

    dropped = len(all_frames) - len(kept_frames)
    print(f"[info] frames conservados: {len(kept_frames)}  (descartados por no tener version limpia: {dropped})")

    for frame in kept_frames:
        name = Path(frame["file_path"]).name
        src = CLEAN_IMAGES_DIR / name
        dst = OUT_IMAGES_DIR / name
        if not dst.exists():
            shutil.copy2(src, dst)

    out_data = {
        "frames": kept_frames,
        "applied_transform": data["applied_transform"],
        "ply_file_path": "sparse_pc.ply",
    }
    (OUT_DIR / "transforms.json").write_text(json.dumps(out_data, indent=2), encoding="utf-8")
    shutil.copy2(SRC_SPARSE_PC, OUT_DIR / "sparse_pc.ply")

    print(f"[OK] dataset armado en {OUT_DIR}")
    print(f"[OK] {len(kept_frames)} imagenes copiadas, transforms.json + sparse_pc.ply listos")


if __name__ == "__main__":
    main()
