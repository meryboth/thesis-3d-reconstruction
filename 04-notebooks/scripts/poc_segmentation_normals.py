"""
POC: segmentacion semantica basica de una nube de gaussianas por geometria
local, sin modelos de deep learning -- heuristica sobre normales estimadas
(PCA local via k vecinos cercanos, con scipy.cKDTree) y altura relativa.

Idea: en una obra arquitectonica, las superficies horizontales (cubierta,
piso) tienen normal casi paralela al eje Z; las superficies verticales
(columnas, fachada) tienen normal casi perpendicular a Z. Combinado con la
posicion en altura (Z), esto separa razonablemente cubierta / piso / columnas
o fachada sin necesidad de un modelo entrenado.

Corre sobre el checkpoint de Templete Central (DJI, Splatfacto), filtrando
primero por opacidad para reducir ruido de floaters antes de estimar normales
(un floater aislado no tiene una superficie local coherente).
"""
from pathlib import Path
import numpy as np
import torch
from scipy.spatial import cKDTree

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CKPT_PATH = Path(r"C:\nerfstudio_work\thesis\02-templete-central\02-resultados-finales\dji\splatfacto\2026-08-24_232220\nerfstudio_models\step-000029999.ckpt")
OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\poc-segmentacion")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ALPHA_MIN = 0.3       # descarta gaussianas de opacidad muy baja antes de estimar normales
CORE_RADIUS = 8.0      # restringe al nucleo denso (edificio real), ver poc_floater_cleanup_*.py
K_NEIGHBORS = 20       # vecinos usados para estimar el plano local (PCA)
VERTICAL_THRESHOLD = 0.5   # |normal . Z| por encima de esto => "horizontal" (cubierta/piso)


def sigmoid_np(x):
    return 1.0 / (1.0 + np.exp(-x))


def estimate_normals(points, k=K_NEIGHBORS):
    tree = cKDTree(points)
    _, idx = tree.query(points, k=k, workers=-1)
    neighbors = points[idx]  # (N, k, 3)
    centered = neighbors - neighbors.mean(axis=1, keepdims=True)
    cov = np.einsum("nki,nkj->nij", centered, centered) / k
    eigvals, eigvecs = np.linalg.eigh(cov)  # ascendente: [:,0] = normal (menor varianza)
    normals = eigvecs[:, :, 0]
    # orientar todas "hacia arriba" (Z positivo) por convencion, no afecta la clasificacion
    flip = normals[:, 2] < 0
    normals[flip] *= -1
    return normals


def main():
    ckpt = torch.load(str(CKPT_PATH), map_location="cpu", weights_only=False)
    gp = ckpt["pipeline"]
    means = gp["_model.gauss_params.means"].detach().numpy().astype(np.float64)
    op_raw = gp["_model.gauss_params.opacities"].detach().numpy().astype(np.float64).reshape(-1)
    alpha = sigmoid_np(op_raw) if (op_raw.min() < 0 or op_raw.max() > 1) else op_raw

    core_centroid = np.median(means[alpha > 0.5], axis=0)
    dist_from_core = np.linalg.norm(means - core_centroid, axis=1)
    mask = (alpha > ALPHA_MIN) & (dist_from_core < CORE_RADIUS)
    pts = means[mask]
    print(f"Gaussianas totales: {len(means):,}, usadas (alpha>{ALPHA_MIN}, dist<{CORE_RADIUS}): {len(pts):,}")

    normals = estimate_normals(pts)
    verticality = np.abs(normals[:, 2])  # 1 = horizontal (normal || Z), 0 = vertical (normal perp. Z)

    z = pts[:, 2]
    z_low, z_high = np.percentile(z, [15, 85])

    is_horizontal = verticality > VERTICAL_THRESHOLD
    is_roof = is_horizontal & (z > (z_low + z_high) / 2)
    is_floor = is_horizontal & (z <= (z_low + z_high) / 2)
    is_wall = ~is_horizontal

    labels = np.full(len(pts), "pared/columna", dtype=object)
    labels[is_roof] = "cubierta"
    labels[is_floor] = "piso/base"

    counts = {lbl: int(np.sum(labels == lbl)) for lbl in ["cubierta", "piso/base", "pared/columna"]}
    print("Conteo por clase:", counts)

    colors = {"cubierta": "#e74c3c", "piso/base": "#2980b9", "pared/columna": "#27ae60"}

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    for lbl, color in colors.items():
        m = labels == lbl
        axes[0].scatter(pts[m, 0], pts[m, 1], s=0.6, alpha=0.5, color=color, label=f"{lbl} ({counts[lbl]:,})")
    axes[0].set_title("Vista en planta (XY)", fontsize=10)
    axes[0].set_xlabel("X"); axes[0].set_ylabel("Y")
    axes[0].set_aspect("equal", adjustable="datalim")
    axes[0].legend(markerscale=15, fontsize=8, loc="upper right")

    for lbl, color in colors.items():
        m = labels == lbl
        axes[1].scatter(pts[m, 0], pts[m, 2], s=0.6, alpha=0.5, color=color, label=lbl)
    axes[1].set_title("Vista de perfil (XZ)", fontsize=10)
    axes[1].set_xlabel("X"); axes[1].set_ylabel("Z")
    axes[1].set_aspect("equal", adjustable="datalim")

    fig.suptitle("POC segmentación por normales locales — Templete Central (DJI)", fontsize=12)
    fig.tight_layout()
    out = OUT_DIR / "poc_segmentation_normals.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"[OK] {out}")


if __name__ == "__main__":
    main()
