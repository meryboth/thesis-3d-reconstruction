"""
Convierte un componente/submodelo especifico de una reconstruccion COLMAP
fragmentada (cameras.bin + images.bin + points3D.bin) al formato de dataset
Nerfstudio (transforms.json + sparse_pc.ply), sin necesidad de tener
Nerfstudio ni COLMAP CLI instalados localmente.

Caso de uso concreto: sfm-templete-central-exhaustive/colmap/sparse/1
contiene 794/794 imagenes registradas (el dataset hibrido DJI+Insta360 de
Templete Central), pero el wrapper de Nerfstudio (ns-process-data) escribio
su transforms.json apuntando al componente 0 (solo 3 imagenes), dejando este
componente completo sin exportar. Este script lo exporta directamente.

Uso:
    python colmap_component_to_nerfstudio.py <carpeta_sparse_componente> <carpeta_salida>

Ejemplo:
    python colmap_component_to_nerfstudio.py \
        "C:\\nerfstudio_work\\panteon-chacarita\\templete-central\\sfm-templete-central-exhaustive\\colmap\\sparse\\1" \
        "C:\\nerfstudio_work\\panteon-chacarita\\templete-central\\sfm-templete-central-exhaustive"

No modifica ni borra ningun archivo de entrada. Escribe transforms.json y
sparse_pc.ply en la carpeta de salida (junto a la carpeta images/ ya
existente del dataset).
"""

import json
import struct
import sys
from pathlib import Path

import numpy as np


# ------------------------------------------------------------
# Lectura binaria COLMAP
# ------------------------------------------------------------

CAMERA_MODELS = {
    0: ("SIMPLE_PINHOLE", 3),
    1: ("PINHOLE", 4),
    2: ("SIMPLE_RADIAL", 4),
    3: ("RADIAL", 5),
    4: ("OPENCV", 8),
    5: ("OPENCV_FISHEYE", 8),
    6: ("FULL_OPENCV", 12),
    7: ("FOV", 5),
    8: ("SIMPLE_RADIAL_FISHEYE", 4),
    9: ("RADIAL_FISHEYE", 5),
    10: ("THIN_PRISM_FISHEYE", 12),
}


def read_next_bytes(fid, num_bytes, fmt, endian="<"):
    data = fid.read(num_bytes)
    return struct.unpack(endian + fmt, data)


def read_cameras_bin(path):
    cameras = {}

    with open(path, "rb") as fid:
        num_cameras = read_next_bytes(fid, 8, "Q")[0]

        for _ in range(num_cameras):
            camera_id, model_id, width, height = read_next_bytes(fid, 24, "iiQQ")
            model_name, num_params = CAMERA_MODELS[model_id]
            params = read_next_bytes(fid, 8 * num_params, "d" * num_params)

            cameras[camera_id] = {
                "model": model_name,
                "width": width,
                "height": height,
                "params": list(params),
            }

    return cameras


def read_images_bin(path):
    images = []

    with open(path, "rb") as fid:
        num_reg_images = read_next_bytes(fid, 8, "Q")[0]

        for _ in range(num_reg_images):
            image_id, qw, qx, qy, qz, tx, ty, tz, camera_id = read_next_bytes(
                fid, 64, "idddddddi"
            )

            name = ""
            while True:
                c = fid.read(1)
                if c == b"\x00":
                    break
                name += c.decode("utf-8", errors="replace")

            num_points2d = read_next_bytes(fid, 8, "Q")[0]
            fid.read(24 * num_points2d)  # x, y (double) + point3D_id (int64)

            images.append({
                "image_id": image_id,
                "qvec": (qw, qx, qy, qz),
                "tvec": (tx, ty, tz),
                "camera_id": camera_id,
                "name": name,
            })

    return images


def read_points3d_bin(path):
    xyz = []
    rgb = []

    with open(path, "rb") as fid:
        num_points = read_next_bytes(fid, 8, "Q")[0]

        for _ in range(num_points):
            point3d_id, x, y, z, r, g, b, error = read_next_bytes(
                fid, 43, "QdddBBBd"
            )
            track_len = read_next_bytes(fid, 8, "Q")[0]
            fid.read(8 * track_len)  # image_id (int32) + point2D_idx (int32)

            xyz.append((x, y, z))
            rgb.append((r, g, b))

    return np.asarray(xyz, dtype=np.float64), np.asarray(rgb, dtype=np.uint8)


# ------------------------------------------------------------
# Conversion a formato Nerfstudio
# ------------------------------------------------------------

# Matriz fija de conversion de ejes COLMAP -> Nerfstudio, tomada de un
# transforms.json ya generado por ns-process-data en este mismo proyecto
# (thesis/02-templete-central/03-datasets/dji/dataset-nerfacto-308-subset),
# para que las poses queden en la misma convencion que el resto del dataset.
APPLIED_TRANSFORM = np.array([
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [0.0, -1.0, 0.0, 0.0],
])


def qvec_to_rotmat(qvec):
    qw, qx, qy, qz = qvec
    return np.array([
        [1 - 2 * qy**2 - 2 * qz**2, 2 * qx * qy - 2 * qz * qw, 2 * qx * qz + 2 * qy * qw],
        [2 * qx * qy + 2 * qz * qw, 1 - 2 * qx**2 - 2 * qz**2, 2 * qy * qz - 2 * qx * qw],
        [2 * qx * qz - 2 * qy * qw, 2 * qy * qz + 2 * qx * qw, 1 - 2 * qx**2 - 2 * qy**2],
    ])


def camera_params_to_frame_fields(cam):
    model = cam["model"]
    p = cam["params"]
    w, h = cam["width"], cam["height"]

    # Normalizamos todos los modelos a fl_x/fl_y/cx/cy/k1/k2/p1/p2,
    # dejando en 0 los parametros que el modelo original no define.
    if model == "SIMPLE_PINHOLE":
        f, cx, cy = p
        fl_x = fl_y = f
        k1 = k2 = p1 = p2 = 0.0
    elif model == "PINHOLE":
        fl_x, fl_y, cx, cy = p
        k1 = k2 = p1 = p2 = 0.0
    elif model == "SIMPLE_RADIAL":
        f, cx, cy, k1 = p
        fl_x = fl_y = f
        k2 = p1 = p2 = 0.0
    elif model == "RADIAL":
        f, cx, cy, k1, k2 = p
        fl_x = fl_y = f
        p1 = p2 = 0.0
    elif model in ("OPENCV", "OPENCV_FISHEYE"):
        fl_x, fl_y, cx, cy, k1, k2, p1, p2 = p
    else:
        raise ValueError(f"Modelo de camara no soportado por este script: {model}")

    return {
        "w": w, "h": h,
        "fl_x": fl_x, "fl_y": fl_y, "cx": cx, "cy": cy,
        "k1": k1, "k2": k2, "p1": p1, "p2": p2,
        "camera_model": "OPENCV",
    }


def build_transforms_json(cameras, images, images_subdir="images"):
    frames = []

    for im in sorted(images, key=lambda x: x["name"]):
        R = qvec_to_rotmat(im["qvec"])
        t = np.asarray(im["tvec"], dtype=np.float64)

        # COLMAP guarda world-to-camera (R, t). Nerfstudio necesita
        # camera-to-world.
        R_c2w = R.T
        t_c2w = -R.T @ t

        c2w = np.eye(4)
        c2w[:3, :3] = R_c2w
        c2w[:3, 3] = t_c2w

        # Conversion de convencion de ejes (misma que usa ns-process-data).
        c2w_ns = np.eye(4)
        c2w_ns[:3, :] = APPLIED_TRANSFORM @ c2w

        cam_fields = camera_params_to_frame_fields(cameras[im["camera_id"]])

        frame = {
            "file_path": f"{images_subdir}/{im['name']}",
            "transform_matrix": c2w_ns.tolist(),
            "colmap_im_id": im["image_id"],
            **cam_fields,
        }
        frames.append(frame)

    return {
        "frames": frames,
        "applied_transform": APPLIED_TRANSFORM.tolist(),
        "ply_file_path": "sparse_pc.ply",
    }


def write_ply(path, xyz, rgb):
    n = len(xyz)
    header = (
        "ply\n"
        "format binary_little_endian 1.0\n"
        f"element vertex {n}\n"
        "property float x\n"
        "property float y\n"
        "property float z\n"
        "property uchar red\n"
        "property uchar green\n"
        "property uchar blue\n"
        "end_header\n"
    )

    dtype = np.dtype([
        ("x", "<f4"), ("y", "<f4"), ("z", "<f4"),
        ("red", "u1"), ("green", "u1"), ("blue", "u1"),
    ])

    data = np.zeros(n, dtype=dtype)
    data["x"], data["y"], data["z"] = xyz[:, 0], xyz[:, 1], xyz[:, 2]
    data["red"], data["green"], data["blue"] = rgb[:, 0], rgb[:, 1], rgb[:, 2]

    with open(path, "wb") as f:
        f.write(header.encode("ascii"))
        f.write(data.tobytes())


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():
    if len(sys.argv) != 3:
        print("Uso: python colmap_component_to_nerfstudio.py <carpeta_sparse_componente> <carpeta_salida>")
        sys.exit(1)

    sparse_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Leyendo componente COLMAP: {sparse_dir}")

    cameras = read_cameras_bin(sparse_dir / "cameras.bin")
    images = read_images_bin(sparse_dir / "images.bin")
    xyz, rgb = read_points3d_bin(sparse_dir / "points3D.bin")

    print(f"Camaras: {len(cameras)}")
    print(f"Imagenes registradas: {len(images)}")
    print(f"Puntos 3D: {len(xyz)}")

    transforms = build_transforms_json(cameras, images)

    transforms_path = out_dir / "transforms.json"
    ply_path = out_dir / "sparse_pc.ply"

    transforms_path.write_text(
        json.dumps(transforms, indent=2),
        encoding="utf-8"
    )
    write_ply(ply_path, xyz, rgb)

    print()
    print(f"[OK] transforms.json -> {transforms_path}")
    print(f"[OK] sparse_pc.ply   -> {ply_path}")
    print()
    print("IMPORTANTE: este dataset espera que las imagenes referenciadas en")
    print("'file_path' (images/<nombre>.jpg) existan en la carpeta de salida.")
    print("Si la carpeta images/ ya existe junto a la carpeta de salida, no hace falta copiar nada.")


if __name__ == "__main__":
    main()
