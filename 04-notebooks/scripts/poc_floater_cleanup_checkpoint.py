"""
POC (parte 2): aplica el mismo criterio de limpieza de floaters (opacidad baja
+ aislamiento espacial via KNN, igual que poc_floater_cleanup.py) directamente
sobre los tensores del checkpoint entrenado de Splatfacto (no sobre el .ply ya
exportado, que tiene menos gaussianas por el recorte que hace el exportador),
para poder correr ns-eval sobre el modelo limpio y obtener PSNR/SSIM/LPIPS
reales -- no solo una impresion visual.

Escribe un checkpoint nuevo en una carpeta de salida separada, con la misma
estructura que espera Nerfstudio (config.yml + nerfstudio_models/*.ckpt),
lista para levantar por Docker.
"""
from pathlib import Path
import shutil
import numpy as np
import torch
from scipy.spatial import cKDTree

SRC_RUN_DIR = Path(r"C:\nerfstudio_work\thesis\02-templete-central\02-resultados-finales\dji\splatfacto\2026-08-24_232220")
SRC_CKPT = SRC_RUN_DIR / "nerfstudio_models" / "step-000029999.ckpt"

DST_RUN_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\poc-floater-cleanup\checkpoint-clean\templete-central-realityscan-splat-ds8-clean-poc\splatfacto\2026-08-24_232220")
DST_CKPT = DST_RUN_DIR / "nerfstudio_models" / "step-000029999.ckpt"

ALPHA_THRESHOLD = 0.10
K_NEIGHBORS = 8
STD_RATIO = 1.3


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
    threshold = knn_mean_dist.mean() + STD_RATIO * knn_mean_dist.std()
    mask_isolated = knn_mean_dist > threshold

    mask_floater = mask_low_alpha | mask_isolated
    mask_keep = ~mask_floater
    n_kept = int(mask_keep.sum())

    print(f"Criterio A (alpha < {ALPHA_THRESHOLD}): {int(mask_low_alpha.sum()):,}")
    print(f"Criterio B (aislamiento, KNN dist > {threshold:.5f}): {int(mask_isolated.sum()):,}")
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
    print(f"[OK] checkpoint limpio: {DST_CKPT}")

    # copiar config.yml y dataparser_transforms.json tal cual (misma escena/dataset)
    for fname in ["config.yml", "dataparser_transforms.json"]:
        src = SRC_RUN_DIR / fname
        if src.exists():
            shutil.copy2(src, DST_RUN_DIR / fname)
            print(f"[OK] copiado: {fname}")


if __name__ == "__main__":
    main()
