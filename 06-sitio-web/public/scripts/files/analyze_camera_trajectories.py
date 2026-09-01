"""
Analiza la trayectoria de camaras de cada dataset Nerfstudio (transforms.json)
presente en thesis/0X-*/03-datasets/.

Replica en Python local (sin pandas/matplotlib, solo numpy+stdlib) la logica del
notebook "Analisis de Trayectoria de Camaras.ipynb" (originalmente corrido en
Colab contra el dataset de Paraguas), generalizada para descubrir y analizar
automaticamente TODOS los datasets de los 3 casos de estudio.

Metricas: cantidad de frames, longitud de trayectoria, bounding box, centroide,
distancia entre camaras consecutivas (min/mean/median/std/percentiles), deteccion
de saltos bruscos (z-score), orientacion aproximada (yaw/pitch).

No modifica ningun archivo de entrada. Escribe, junto a cada transforms.json:
  camera-trajectory-metadata.json
  camera-trajectory-metrics.log
"""

from pathlib import Path
import json
import math
from datetime import datetime

import numpy as np

ROOT = Path(r"C:\nerfstudio_work\thesis")

JUMP_ZSCORE_THRESHOLD = 3.0
TOP_STEPS_K = 20


def find_transforms(root):
    return sorted(root.glob("0*/03-datasets/**/transforms.json"))


def case_and_dataset_label(root, transforms_path):
    rel = transforms_path.relative_to(root)
    parts = rel.parts
    case = parts[0]
    dataset_label = "/".join(parts[2:-1]) if len(parts) > 3 else parts[2]
    return case, dataset_label


def extract_camera_poses(frames):
    rows = []
    bad_frames = 0

    for idx, fr in enumerate(frames):
        T = fr.get("transform_matrix")

        if T is None:
            bad_frames += 1
            continue

        T = np.asarray(T, dtype=np.float64)

        if T.shape != (4, 4):
            bad_frames += 1
            continue

        R = T[:3, :3]
        t = T[:3, 3]

        forward = -R[:, 2]
        up = R[:, 1]

        forward_norm = forward / (np.linalg.norm(forward) + 1e-9)
        up_norm = up / (np.linalg.norm(up) + 1e-9)

        yaw_xz = math.degrees(math.atan2(forward_norm[0], forward_norm[2]))
        pitch_y = math.degrees(math.asin(np.clip(forward_norm[1], -1, 1)))

        rows.append({
            "frame_index": idx,
            "file_path": fr.get("file_path", ""),
            "position": t,
            "yaw_xz_deg": yaw_xz,
            "pitch_y_deg": pitch_y,
        })

    return rows, bad_frames


def analyze_transforms(path):
    with path.open("r", encoding="utf-8") as f:
        transforms = json.load(f)

    frames = transforms.get("frames", [])
    poses, bad_frames = extract_camera_poses(frames)

    if len(poses) < 2:
        raise ValueError(f"Muy pocas poses validas ({len(poses)}) para analizar trayectoria")

    positions = np.asarray([p["position"] for p in poses], dtype=np.float64)
    yaw = np.asarray([p["yaw_xz_deg"] for p in poses], dtype=np.float64)
    pitch = np.asarray([p["pitch_y_deg"] for p in poses], dtype=np.float64)

    steps = np.linalg.norm(np.diff(positions, axis=0), axis=1)
    path_length = float(steps.sum())

    bbox_min = positions.min(axis=0)
    bbox_max = positions.max(axis=0)
    bbox_size = bbox_max - bbox_min
    center = positions.mean(axis=0)

    step_mean = float(np.mean(steps))
    step_std = float(np.std(steps))
    step_zscore = (steps - step_mean) / (step_std + 1e-9)

    jump_mask = np.abs(step_zscore) >= JUMP_ZSCORE_THRESHOLD
    jump_indices = np.where(jump_mask)[0] + 1  # step i corresponde al frame i+1

    top_order = np.argsort(-steps)[:TOP_STEPS_K]

    camera_model = transforms.get("camera_model", "unknown")
    w = transforms.get("w")
    h = transforms.get("h")
    fl_x = transforms.get("fl_x")
    fl_y = transforms.get("fl_y")

    metadata = {
        "artifact": "camera-trajectory",
        "source": "nerfstudio transforms.json",
        "generated_analysis_at": datetime.now().isoformat(),

        "file": {
            "path": str(path),
            "size_bytes": path.stat().st_size,
        },

        "camera_intrinsics": {
            "camera_model": camera_model,
            "width": w,
            "height": h,
            "fl_x": fl_x,
            "fl_y": fl_y,
        },

        "frames": {
            "total_in_json": len(frames),
            "valid_poses": len(poses),
            "invalid_or_missing_matrix": bad_frames,
        },

        "trajectory": {
            "path_length": path_length,
            "bounding_box": {
                "min": bbox_min.tolist(),
                "max": bbox_max.tolist(),
                "size": bbox_size.tolist(),
            },
            "center": center.tolist(),
        },

        "consecutive_camera_distance": {
            "mean": step_mean,
            "median": float(np.median(steps)),
            "std": step_std,
            "min": float(np.min(steps)),
            "p05": float(np.percentile(steps, 5)),
            "p25": float(np.percentile(steps, 25)),
            "p75": float(np.percentile(steps, 75)),
            "p95": float(np.percentile(steps, 95)),
            "max": float(np.max(steps)),
        },

        "orientation": {
            "yaw_xz_deg_range": [float(np.min(yaw)), float(np.max(yaw))],
            "pitch_y_deg_range": [float(np.min(pitch)), float(np.max(pitch))],
        },

        "jump_detection": {
            "method": f"|z-score of consecutive-camera-distance| >= {JUMP_ZSCORE_THRESHOLD}",
            "jumps_detected": int(jump_mask.sum()),
            "jump_frame_indices": jump_indices.tolist(),
        },

        "top_steps": [
            {
                "frame_index": int(i) + 1,
                "file_path": poses[i + 1]["file_path"],
                "step_from_previous": float(steps[i]),
                "step_zscore": float(step_zscore[i]),
            }
            for i in top_order
        ],

        "important_note": (
            "El orden de los frames es el orden en que aparecen en transforms.json, "
            "no necesariamente el orden temporal/espacial real de captura (depende de "
            "como COLMAP/RealityScan/ns-process-data haya ordenado las imagenes). "
            "path_length y la deteccion de saltos deben interpretarse con esa salvedad."
        ),
    }

    return metadata


def write_outputs(path, metadata):
    folder = path.parent

    json_path = folder / "camera-trajectory-metadata.json"
    log_path = folder / "camera-trajectory-metrics.log"

    json_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    d = metadata["consecutive_camera_distance"]
    bbox = metadata["trajectory"]["bounding_box"]
    jd = metadata["jump_detection"]

    lines = [
        "CAMERA TRAJECTORY ANALYSIS",
        "=" * 70,
        "",
        f"File: {path}",
        f"Camera model: {metadata['camera_intrinsics']['camera_model']}",
        f"Resolution: {metadata['camera_intrinsics']['width']} x {metadata['camera_intrinsics']['height']}",
        "",
        "FRAMES",
        "------",
        f"Total in JSON: {metadata['frames']['total_in_json']}",
        f"Valid poses: {metadata['frames']['valid_poses']}",
        f"Invalid/missing matrix: {metadata['frames']['invalid_or_missing_matrix']}",
        "",
        "TRAJECTORY",
        "----------",
        f"Path length: {metadata['trajectory']['path_length']:.6f}",
        f"BBox size X: {bbox['size'][0]:.6f}",
        f"BBox size Y: {bbox['size'][1]:.6f}",
        f"BBox size Z: {bbox['size'][2]:.6f}",
        f"Center: {metadata['trajectory']['center']}",
        "",
        "CONSECUTIVE CAMERA DISTANCE",
        "----------------------------",
        f"Mean: {d['mean']:.6f}",
        f"Median: {d['median']:.6f}",
        f"Std: {d['std']:.6f}",
        f"Min: {d['min']:.6f}",
        f"P05: {d['p05']:.6f}",
        f"P95: {d['p95']:.6f}",
        f"Max: {d['max']:.6f}",
        "",
        "ORIENTATION",
        "-----------",
        f"Yaw XZ range (deg): {metadata['orientation']['yaw_xz_deg_range']}",
        f"Pitch Y range (deg): {metadata['orientation']['pitch_y_deg_range']}",
        "",
        "JUMP DETECTION",
        "---------------",
        f"Method: {jd['method']}",
        f"Jumps detected: {jd['jumps_detected']}",
        f"Jump frame indices: {jd['jump_frame_indices']}",
        "",
        "METHODOLOGICAL NOTE",
        "--------------------",
        metadata["important_note"],
    ]

    log_path.write_text("\n".join(lines), encoding="utf-8")

    return json_path, log_path


def main():
    transforms_files = find_transforms(ROOT)

    if not transforms_files:
        print("No se encontraron transforms.json bajo */03-datasets/")
        return

    print(f"transforms.json encontrados: {len(transforms_files)}")

    for path in transforms_files:
        case, dataset_label = case_and_dataset_label(ROOT, path)

        print()
        print("=" * 75)
        print(f"{case} :: {dataset_label}")
        print(path)
        print("=" * 75)

        try:
            metadata = analyze_transforms(path)
        except Exception as e:
            print(f"[ERROR] {case} :: {dataset_label}: {e}")
            continue

        json_path, log_path = write_outputs(path, metadata)

        print(f"[OK] Frames validos: {metadata['frames']['valid_poses']}")
        print(f"[OK] Path length: {metadata['trajectory']['path_length']:.3f}")
        print(f"[OK] Saltos detectados: {metadata['jump_detection']['jumps_detected']}")
        print(f"[OK] Log:  {log_path}")
        print(f"[OK] JSON: {json_path}")


if __name__ == "__main__":
    main()
