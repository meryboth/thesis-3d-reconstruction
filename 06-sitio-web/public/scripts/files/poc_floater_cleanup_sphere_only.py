"""
POC (parte 5): replica el metodo real que uso la usuaria en SuperSplat --
una esfera simple que contiene al edificio, borrando todo lo de afuera.
Sin criterios de opacidad ni aislamiento, solo distancia al centro.

Radio calibrado por barrido directo en el espacio del checkpoint (sin pasar
por la alineacion cross-coordenadas, que resulto poco precisa para esto)
para reproducir el mismo porcentaje removido que la edicion manual (~54.7%).
"""
from pathlib import Path
import shutil
import numpy as np
import torch

SRC_RUN_DIR = Path(r"C:\nerfstudio_work\thesis\02-templete-central\02-resultados-finales\dji\splatfacto\2026-08-24_232220")
SRC_CKPT = SRC_RUN_DIR / "nerfstudio_models" / "step-000029999.ckpt"

DST_RUN_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\poc-floater-cleanup\checkpoint-clean-sphere\templete-central-realityscan-splat-ds8-clean-sphere\splatfacto\2026-08-24_232220")
DST_CKPT = DST_RUN_DIR / "nerfstudio_models" / "step-000029999.ckpt"

CORE_ALPHA = 0.5
SPHERE_RADIUS = 0.68  # calibrado por barrido para reproducir el ~54.7% removido de la edicion manual


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
    centroid = np.median(means[alpha > CORE_ALPHA], axis=0)
    dists = np.linalg.norm(means - centroid, axis=1)

    mask_keep = dists <= SPHERE_RADIUS
    n_kept = int(mask_keep.sum())
    print(f"Centro: {centroid}, radio: {SPHERE_RADIUS}")
    print(f"Gaussianas conservadas: {n_kept:,} ({100*n_kept/n0:.2f}%, removido {100*(1-n_kept/n0):.2f}%)")
    print("Referencia -- edicion manual: 143,136 de 315,787 (45.32% conservado, 54.68% removido)")

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
    print(f"[OK] checkpoint (esfera pura): {DST_CKPT}")

    for fname in ["config.yml", "dataparser_transforms.json"]:
        src = SRC_RUN_DIR / fname
        if src.exists():
            shutil.copy2(src, DST_RUN_DIR / fname)
            print(f"[OK] copiado: {fname}")


if __name__ == "__main__":
    main()
