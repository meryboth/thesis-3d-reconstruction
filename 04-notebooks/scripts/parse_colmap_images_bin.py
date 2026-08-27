"""
Lee un archivo images.bin de COLMAP (formato binario nativo) y devuelve:
- cantidad de imagenes registradas (con pose)
- nombre de cada imagen registrada
- cantidad total de observaciones 2D (para referencia)

No requiere pycolmap ni el binario de COLMAP, solo struct + el formato
binario documentado oficialmente por COLMAP.
"""

import struct
import sys
from pathlib import Path


def read_next_bytes(fid, num_bytes, fmt, endian="<"):
    data = fid.read(num_bytes)
    return struct.unpack(endian + fmt, data)


def read_images_bin(path):
    images = []

    with open(path, "rb") as fid:
        num_reg_images = read_next_bytes(fid, 8, "Q")[0]

        for _ in range(num_reg_images):
            image_id, qw, qx, qy, qz, tx, ty, tz, camera_id = read_next_bytes(
                fid, 64, "iddddddd i".replace(" ", "")
            )

            name = ""
            while True:
                c = fid.read(1)
                if c == b"\x00":
                    break
                name += c.decode("utf-8", errors="replace")

            num_points2d = read_next_bytes(fid, 8, "Q")[0]

            # Cada punto2D: x (double), y (double), point3D_id (int64) = 24 bytes
            fid.read(24 * num_points2d)

            images.append({
                "image_id": image_id,
                "camera_id": camera_id,
                "name": name,
                "num_points2d": num_points2d,
            })

    return images


if __name__ == "__main__":
    path = Path(sys.argv[1])
    images = read_images_bin(path)

    print(f"Archivo: {path}")
    print(f"Imagenes registradas: {len(images)}")
    print()

    for im in sorted(images, key=lambda x: x["name"]):
        print(f"  {im['name']}  (points2D: {im['num_points2d']})")
