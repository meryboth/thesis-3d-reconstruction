"""
Corrige el Grafico 5.7 de Cap. 5: la nube densa de Los Paraguas sale de
COLMAP nativo (a diferencia de Templete/Panteon, que salen de RealityScan) y
tiene una convencion de ejes distinta -- ahi el "arriba" real es Y, no Z.
analyze_dense_clouds.py asume Z=arriba para los 3 casos por igual, asi que
para este sitio la proyeccion etiquetada "XY (planta)" en realidad mostraba
el perfil, y "XZ (perfil)" mostraba una planta inclinada/no alineada.

Este script nivela la nube (mismo RANSAC-al-piso que poc_segmentation_
multi_site.py) y regenera el mismo archivo -scatter.png en el lugar exacto
que ya referencia Cap. 5, para no tener que tocar el capitulo.
"""
from pathlib import Path
import numpy as np
from plyfile import PlyData

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PLY_PATH = Path(r"C:\nerfstudio_work\thesis\01-paraguas-vicentelopez\02-resultados-finales\colmap-fotogrametria-densa\fused_medium_high_clean.ply")
OUT_PATH = PLY_PATH.parent / f"{PLY_PATH.stem}-scatter.png"

SAMPLE_N = 150_000
RANDOM_SEED = 42


def fit_plane_ransac(points, n_iters=300, dist_threshold=0.03, sample_size=20000, seed=42):
    rng = np.random.default_rng(seed)
    sub = points[rng.choice(len(points), size=min(sample_size, len(points)), replace=False)]
    best_inliers, best_normal, best_d = -1, None, None
    for _ in range(n_iters):
        p0, p1, p2 = sub[rng.choice(len(sub), size=3, replace=False)]
        normal = np.cross(p1 - p0, p2 - p0)
        norm = np.linalg.norm(normal)
        if norm < 1e-9:
            continue
        normal = normal / norm
        d = -normal @ p0
        inliers = int(np.sum(np.abs(sub @ normal + d) < dist_threshold))
        if inliers > best_inliers:
            best_inliers, best_normal, best_d = inliers, normal, d
    print(f"RANSAC piso: {best_inliers:,}/{len(sub):,} inliers ({100*best_inliers/len(sub):.1f}%)")
    return best_normal, best_d


def rotation_to_align(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    v = np.cross(a, b)
    c = np.dot(a, b)
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3) if c > 0 else -np.eye(3)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * (1 / (1 + c))


def main():
    v = PlyData.read(str(PLY_PATH))["vertex"].data
    xyz = np.column_stack([v["x"], v["y"], v["z"]]).astype(np.float64)
    print(f"Puntos: {len(xyz):,}")

    range_per_axis = xyz.max(axis=0) - xyz.min(axis=0)
    rough_up_axis = np.argmin(range_per_axis)
    low_cutoff = np.percentile(xyz[:, rough_up_axis], 20)
    candidates = xyz[xyz[:, rough_up_axis] <= low_cutoff]
    print(f"Eje aproximado 'arriba' (rango minimo): {rough_up_axis} ({'XYZ'[rough_up_axis]})")

    normal, d = fit_plane_ransac(candidates)
    if np.median(xyz @ normal + d) < 0:
        normal, d = -normal, -d
    R = rotation_to_align(normal, np.array([0.0, 0.0, 1.0]))
    xyz_leveled = xyz @ R.T
    ground_z = np.median(xyz_leveled[:, 2][np.abs(xyz @ normal + d) < 0.05])
    xyz_leveled[:, 2] -= ground_z

    rng = np.random.default_rng(RANDOM_SEED)
    sample = xyz_leveled[rng.choice(len(xyz_leveled), size=min(SAMPLE_N, len(xyz_leveled)), replace=False)]

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.5))
    axes[0].scatter(sample[:, 0], sample[:, 1], s=0.15, alpha=0.4, color="#2c3e50")
    axes[0].set_xlabel("X"); axes[0].set_ylabel("Y")
    axes[0].set_title("01-paraguas-vicentelopez — proyeccion XY (muestra, nivelada)")
    axes[0].set_aspect("equal", adjustable="datalim")

    axes[1].scatter(sample[:, 0], sample[:, 2], s=0.15, alpha=0.4, color="#2c3e50")
    axes[1].set_xlabel("X"); axes[1].set_ylabel("Z")
    axes[1].set_title("01-paraguas-vicentelopez — proyeccion XZ (muestra, nivelada)")
    axes[1].set_aspect("equal", adjustable="datalim")

    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=150)
    print(f"[OK] {OUT_PATH}")


if __name__ == "__main__":
    main()
