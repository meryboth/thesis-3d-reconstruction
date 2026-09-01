"""
POC: limpieza automatica de floaters en un export de Gaussian Splatting
(splat.ply), combinando dos criterios baratos de calcular:

  A) Opacidad baja (alpha < ALPHA_THRESHOLD) -- ya cuantificado en Cap. 5,
     Grafico 5.4 (7,3% de las gaussianas del Templete Central tienen
     opacidad estimada < 0.05).
  B) Aislamiento espacial -- mismo algoritmo que Open3D remove_statistical_
     outlier(): para cada gaussiana, distancia media a sus K vecinos mas
     cercanos; se marca como outlier si esa distancia excede
     mean_global + STD_RATIO * std_global. Implementado a mano con
     scipy.spatial.cKDTree (no hay open3d/sklearn instalados localmente).

No modifica el splat.ply original: escribe una copia "-clean" al lado.
"""
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from plyfile import PlyData, PlyElement

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SPLAT_PATH = Path(r"C:\nerfstudio_work\thesis\02-templete-central\02-resultados-finales\dji\splatfacto\export\splat.ply")
OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\poc-floater-cleanup")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ALPHA_THRESHOLD = 0.10
K_NEIGHBORS = 8
STD_RATIO = 1.3


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def main():
    ply = PlyData.read(str(SPLAT_PATH))
    vertex = ply["vertex"].data
    names = list(vertex.dtype.names)
    n0 = len(vertex)
    print(f"Gaussianas originales: {n0:,}")

    xyz = np.column_stack([vertex[c] for c in ["x", "y", "z"]]).astype(np.float64)

    opacity_col = "opacity" if "opacity" in names else None
    alpha_raw = np.asarray(vertex[opacity_col], dtype=np.float64)
    alpha = sigmoid(alpha_raw) if (alpha_raw.min() < 0 or alpha_raw.max() > 1) else alpha_raw

    # Criterio A: opacidad baja
    mask_low_alpha = alpha < ALPHA_THRESHOLD

    # Criterio B: aislamiento espacial (K-NN mean distance, umbral estadistico global)
    tree = cKDTree(xyz)
    dists, _ = tree.query(xyz, k=K_NEIGHBORS + 1, workers=-1)  # k+1 porque incluye el punto mismo
    knn_mean_dist = dists[:, 1:].mean(axis=1)
    global_mean = knn_mean_dist.mean()
    global_std = knn_mean_dist.std()
    threshold = global_mean + STD_RATIO * global_std
    mask_isolated = knn_mean_dist > threshold

    mask_floater = mask_low_alpha | mask_isolated
    mask_keep = ~mask_floater

    n_low_alpha = int(mask_low_alpha.sum())
    n_isolated = int(mask_isolated.sum())
    n_both = int((mask_low_alpha & mask_isolated).sum())
    n_removed = int(mask_floater.sum())
    n_kept = int(mask_keep.sum())

    print(f"Criterio A (alpha < {ALPHA_THRESHOLD}): {n_low_alpha:,} ({100*n_low_alpha/n0:.2f}%)")
    print(f"Criterio B (aislamiento espacial, KNN dist > {threshold:.5f}): {n_isolated:,} ({100*n_isolated/n0:.2f}%)")
    print(f"Interseccion A y B: {n_both:,}")
    print(f"Total a remover (A o B): {n_removed:,} ({100*n_removed/n0:.2f}%)")
    print(f"Gaussianas resultantes: {n_kept:,}")

    # Escribir el .ply limpio (mismos campos, filas filtradas)
    clean_vertex_data = vertex[mask_keep]
    el = PlyElement.describe(clean_vertex_data, "vertex")
    clean_path = SPLAT_PATH.parent / "splat-clean-poc.ply"
    PlyData([el], text=False).write(str(clean_path))
    print(f"[OK] {clean_path} ({clean_path.stat().st_size / 1024 / 1024:.1f} MB, "
          f"original {SPLAT_PATH.stat().st_size / 1024 / 1024:.1f} MB)")

    # Visual: dispersion espacial XY antes/despues (misma convencion que analyze_gaussian_splats.py)
    rng = np.random.default_rng(42)
    sample_n = min(60_000, n0)
    idx = rng.choice(n0, size=sample_n, replace=False)

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    axes[0].scatter(xyz[idx, 0], xyz[idx, 1], s=0.2, alpha=0.4, color="#34495e")
    axes[0].set_title(f"Original ({n0:,} gaussianas)")
    axes[0].set_xlabel("X"); axes[0].set_ylabel("Y")
    axes[0].set_aspect("equal", adjustable="datalim")

    idx_clean_mask = mask_keep[idx]
    axes[1].scatter(xyz[idx][idx_clean_mask, 0], xyz[idx][idx_clean_mask, 1], s=0.2, alpha=0.4, color="#27ae60")
    axes[1].scatter(xyz[idx][~idx_clean_mask, 0], xyz[idx][~idx_clean_mask, 1], s=1.5, alpha=0.8, color="#e74c3c", label="removido")
    axes[1].set_title(f"Limpio ({n_kept:,} gaussianas, -{100*n_removed/n0:.1f}%)")
    axes[1].set_xlabel("X"); axes[1].set_ylabel("Y")
    axes[1].set_aspect("equal", adjustable="datalim")
    axes[1].legend(markerscale=8, fontsize=8)

    fig.suptitle("POC limpieza de floaters — Templete Central (DJI), vista XY", fontsize=12)
    fig.tight_layout()
    out_png = OUT_DIR / "poc_floater_cleanup_xy.png"
    fig.savefig(out_png, dpi=150, bbox_inches="tight")
    print(f"[OK] {out_png}")


if __name__ == "__main__":
    main()
