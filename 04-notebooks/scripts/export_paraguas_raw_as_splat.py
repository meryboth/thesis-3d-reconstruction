"""
Exporta la nube densa CRUDA (sin nivelar, color real) de Los Paraguas como un
.ply de gaussian splat minimo (gaussianas chicas y opacas, mismo truco que
export_segmentation_as_splat.py) para que se pueda abrir y reorientar a mano
en el editor de SuperSplat.
"""
from pathlib import Path
import numpy as np
from plyfile import PlyData, PlyElement

SRC_PLY = Path(r"C:\nerfstudio_work\thesis\01-paraguas-vicentelopez\02-resultados-finales\colmap-fotogrametria-densa\fused_medium_high_clean.ply")
OUT_PLY = Path(r"C:\nerfstudio_work\thesis\00-auditoria\poc-segmentacion\paraguas_raw_as_splat.ply")

SH_C0 = 0.28209479177387814
POINT_SCALE = 0.015
OPACITY_RAW = 6.0


def main():
    src = PlyData.read(str(SRC_PLY))["vertex"].data
    n = len(src)
    print(f"Puntos: {n:,}")

    rgb01 = np.column_stack([src["red"], src["green"], src["blue"]]).astype(np.float64) / 255.0
    f_dc = (rgb01 - 0.5) / SH_C0
    scale_raw = np.log(POINT_SCALE)

    dtype = [
        ("x", "f4"), ("y", "f4"), ("z", "f4"),
        ("f_dc_0", "f4"), ("f_dc_1", "f4"), ("f_dc_2", "f4"),
        ("opacity", "f4"),
        ("scale_0", "f4"), ("scale_1", "f4"), ("scale_2", "f4"),
        ("rot_0", "f4"), ("rot_1", "f4"), ("rot_2", "f4"), ("rot_3", "f4"),
    ]
    vertex = np.zeros(n, dtype=dtype)
    vertex["x"], vertex["y"], vertex["z"] = src["x"], src["y"], src["z"]
    vertex["f_dc_0"], vertex["f_dc_1"], vertex["f_dc_2"] = f_dc[:, 0], f_dc[:, 1], f_dc[:, 2]
    vertex["opacity"] = OPACITY_RAW
    vertex["scale_0"] = scale_raw
    vertex["scale_1"] = scale_raw
    vertex["scale_2"] = scale_raw
    vertex["rot_0"] = 1.0

    el = PlyElement.describe(vertex, "vertex")
    PlyData([el], text=False).write(str(OUT_PLY))
    print(f"[OK] {OUT_PLY} ({OUT_PLY.stat().st_size / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
