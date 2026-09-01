"""
POC (parte 3): version mucho mas agresiva de la limpieza de floaters, sobre
el checkpoint completo. Suma un tercer criterio a los dos anteriores
(opacidad baja + aislamiento KNN): distancia al centroide de la "masa
densa" (el edificio real) -- la evidencia visual en SuperSplat muestra que
el edificio ocupa una fraccion minuscula del volumen total de gaussianas.

Criterio C: se estima el centroide con las gaussianas de mayor confianza
(alpha > CORE_ALPHA), se mide su dispersion (percentil de distancia al
centroide) y se recorta todo lo que este mas lejos que RADIUS_FACTOR veces
ese percentil.
"""
from pathlib import Path
import shutil
import numpy as np
import torch
from scipy.spatial import cKDTree

SRC_RUN_DIR = Path(r"C:\nerfstudio_work\thesis\02-templete-central\02-resultados-finales\dji\splatfacto\2026-08-24_232220")
SRC_CKPT = SRC_RUN_DIR / "nerfstudio_models" / "step-000029999.ckpt"

DST_RUN_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\poc-floater-cleanup\checkpoint-clean-aggressive\templete-central-realityscan-splat-ds8-clean-aggressive\splatfacto\2026-08-24_232220")
DST_CKPT = DST_RUN_DIR / "nerfstudio_models" / "step-000029999.ckpt"

ALPHA_THRESHOLD = 0.10
K_NEIGHBORS = 8
STD_RATIO = 1.3

CORE_ALPHA = 0.5
FIXED_RADIUS = 6.0  # calibrado a mano: p50 de distancia al centroide es 0.76, p75 es 7.6 -- hay un salto abrupto


def sigmoid_np(x):
    return 1.0 / (1.0 + np.exp(-x))


def main():
    ckpt = torch.load(str(SRC_CKPT), map_location="cpu", weights_only=False)
    gp = ckpt["pipeline"]

    means = gp["_model.gauss_params.means"].detach().numpy().astype(np.float64)
    opacities_raw = gp["_model.gauss_params.opacities"].detach().numpy().astype(np.float64).reshape(-1)
    n0 = len(means)
    print(f"Gaussianas en el checkpoint: {n0:,}")

    alpha = sigmoid_np(opacities_raw) if (opacities_raw.min() < 0 or opacities_raw.max() > 1) else opacities_raw

    mask_low_alpha = alpha < ALPHA_THRESHOLD

    tree = cKDTree(means)
    dists, _ = tree.query(means, k=K_NEIGHBORS + 1, workers=-1)
    knn_mean_dist = dists[:, 1:].mean(axis=1)
    iso_threshold = knn_mean_dist.mean() + STD_RATIO * knn_mean_dist.std()
    mask_isolated = knn_mean_dist > iso_threshold

    # Criterio C: distancia al centroide de la masa densa/confiable
    core_mask = alpha > CORE_ALPHA
    core_centroid = np.median(means[core_mask], axis=0)
    radius = FIXED_RADIUS
    all_dists = np.linalg.norm(means - core_centroid, axis=1)
    mask_far = all_dists > radius

    print(f"Centroide del nucleo (alpha>{CORE_ALPHA}): {core_centroid}")
    print(f"Radio de corte: {radius:.3f}")

    mask_floater = mask_low_alpha | mask_isolated | mask_far
    mask_keep = ~mask_floater
    n_kept = int(mask_keep.sum())

    print(f"Criterio A (alpha < {ALPHA_THRESHOLD}): {int(mask_low_alpha.sum()):,}")
    print(f"Criterio B (aislamiento): {int(mask_isolated.sum()):,}")
    print(f"Criterio C (distancia > {radius:.2f}): {int(mask_far.sum()):,}")
    print(f"Total removido: {n0 - n_kept:,} ({100*(n0-n_kept)/n0:.2f}%)")
    print(f"Gaussianas resultantes: {n_kept:,}")

    keep_idx = torch.from_numpy(mask_keep)
    gauss_keys = [
        "_model.gauss_params.features_dc",
        "_model.gauss_params.features_rest",
        "_model.gauss_params.means",
        "_model.gauss_params.opacities",
        "_model.gauss_params.quats",
        "_model.gauss_params.scales",
    ]
    for k in gauss_keys:
        before = gp[k].shape
        gp[k] = gp[k][keep_idx]
        print(f"  {k}: {tuple(before)} -> {tuple(gp[k].shape)}")

    DST_CKPT.parent.mkdir(parents=True, exist_ok=True)
    torch.save(ckpt, str(DST_CKPT))
    print(f"[OK] checkpoint limpio (agresivo): {DST_CKPT}")

    for fname in ["config.yml", "dataparser_transforms.json"]:
        src = SRC_RUN_DIR / fname
        if src.exists():
            shutil.copy2(src, DST_RUN_DIR / fname)
            print(f"[OK] copiado: {fname}")

    # tambien exportamos un .ply liviano para poder verla en SuperSplat, igual que la POC anterior
    from plyfile import PlyData
    orig_ply_path = SRC_RUN_DIR.parent / "export" / "splat.ply"
    if orig_ply_path.exists():
        ply = PlyData.read(str(orig_ply_path))
        vertex = ply["vertex"].data
        n_ply = len(vertex)
        print(f"[nota] el .ply exportado tiene {n_ply:,} filas (el exportador ya recorta algunas respecto al checkpoint) "
              f"-- no se puede aplicar la misma mascara indice a indice, se omite el .ply de esta version agresiva.")


if __name__ == "__main__":
    main()
