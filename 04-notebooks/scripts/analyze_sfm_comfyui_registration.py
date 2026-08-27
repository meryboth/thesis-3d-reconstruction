"""
Analiza el resultado de COLMAP nativo corrido sobre el Dataset B curado
(ComfyUI: YOLO-seg + LaMa inpaint) del Templete Central -- primer paso real
hacia la comparacion H2 pendiente en el Cap. 5, seccion 5.2.1 ("falta correr
SfM/Nerfacto/Splatfacto sobre este dataset curado").

Lee panteon-chacarita/templete-central/sfm-de-comfy-ui/sparse/0/*.txt
(formato texto de COLMAP) y reporta: cuantas imagenes se registraron sobre
el total del dataset, puntos 3D, longitud de track promedio, error de
reproyeccion promedio -- mismas metricas que
00-auditoria/sfm-registration-comparison/ para poder comparar directo contra
la fila del dataset raw (RealityScan, DJI, 1234 imgenes, 1232 registradas,
99.84%).
"""
import json
from pathlib import Path
from collections import defaultdict

import numpy as np

SPARSE_DIR = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\sfm-de-comfy-ui\sparse\0")
IMAGES_DIR = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\sfm-de-comfy-ui\images")
OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\sfm-registration-comparison")


def parse_cameras(path):
    cameras = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            cameras[int(parts[0])] = {"model": parts[1], "width": int(parts[2]), "height": int(parts[3])}
    return cameras


def parse_images(path):
    """Devuelve lista de dicts: {image_id, name, camera_id, n_points2d, n_points2d_with_3d}."""
    images = []
    with open(path, encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#")]
    i = 0
    while i < len(lines):
        header = lines[i].split()
        image_id = int(header[0])
        camera_id = int(header[8])
        name = header[9]
        points_line = lines[i + 1].split()
        n_entries = len(points_line) // 3
        n_with_3d = sum(1 for k in range(n_entries) if points_line[k * 3 + 2] != "-1")
        images.append({
            "image_id": image_id,
            "name": name,
            "camera_id": camera_id,
            "n_points2d": n_entries,
            "n_points2d_with_3d": n_with_3d,
        })
        i += 2
    return images


def parse_points3d_summary(path):
    n_points = 0
    track_lengths = []
    errors = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            n_points += 1
            error = float(parts[7])
            errors.append(error)
            track_data = parts[8:]
            track_lengths.append(len(track_data) // 2)
    return n_points, np.array(track_lengths), np.array(errors)


def main():
    total_source_images = len(list(IMAGES_DIR.glob("*.png")))
    cameras = parse_cameras(SPARSE_DIR / "cameras.txt")
    images = parse_images(SPARSE_DIR / "images.txt")
    n_points3d, track_lengths, errors = parse_points3d_summary(SPARSE_DIR / "points3D.txt")

    n_registered = len(images)
    pct = n_registered / total_source_images * 100

    print(f"[info] dataset fuente (Dataset B curado, ComfyUI): {total_source_images} imagenes")
    print(f"[info] camaras estimadas: {len(cameras)}")
    print(f"[info] imagenes registradas: {n_registered} ({pct:.2f}%)")
    print(f"[info] puntos 3D: {n_points3d}")
    print(f"[info] longitud de track promedio: {track_lengths.mean():.2f} (mediana {np.median(track_lengths):.1f})")
    print(f"[info] error de reproyeccion promedio: {errors.mean():.3f} px (mediana {np.median(errors):.3f})")

    points2d_counts = np.array([im["n_points2d"] for im in images])
    points2d_with3d = np.array([im["n_points2d_with_3d"] for im in images])
    print(f"[info] keypoints 2D por imagen: promedio {points2d_counts.mean():.0f}, "
          f"de los cuales con punto 3D asociado: {points2d_with3d.mean():.0f} "
          f"({points2d_with3d.mean()/max(points2d_counts.mean(),1)*100:.1f}%)")

    registered_names = {im["name"] for im in images}
    source_names = {p.name for p in IMAGES_DIR.glob("*.png")}
    missing = sorted(source_names - registered_names)
    print(f"[info] imagenes NO registradas ({len(missing)}): {missing[:20]}{'...' if len(missing) > 20 else ''}")

    result = {
        "caso": "02-templete-central",
        "metodo_captura": "DJI (Dataset B curado, ComfyUI YOLO-seg+LaMa)",
        "pipeline_sfm": "COLMAP nativo",
        "imgs_entrada": total_source_images,
        "imgs_registradas": n_registered,
        "tasa_pct": round(pct, 2),
        "n_points3d": n_points3d,
        "track_length_promedio": round(float(track_lengths.mean()), 2),
        "track_length_mediana": float(np.median(track_lengths)),
        "reproj_error_promedio_px": round(float(errors.mean()), 3),
        "reproj_error_mediana_px": round(float(np.median(errors)), 3),
        "keypoints_2d_promedio": round(float(points2d_counts.mean()), 1),
        "keypoints_con_3d_promedio": round(float(points2d_with3d.mean()), 1),
        "imagenes_no_registradas": missing,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "sfm_comfyui_registration.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] guardado: {out_path}")

    print("\n--- comparacion directa contra el dataset raw (misma fila de sfm_registration_comparison.csv) ---")
    print("RAW  (RealityScan): 1234 entrada, 1232 registradas, 99.84%")
    print(f"CLEAN (COLMAP nativo, ComfyUI): {total_source_images} entrada, {n_registered} registradas, {pct:.2f}%")


if __name__ == "__main__":
    main()
