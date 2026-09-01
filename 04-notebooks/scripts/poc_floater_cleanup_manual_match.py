"""
POC (parte 4, con alineacion): mapea la edicion manual de la usuaria en
SuperSplat (splat-editado.ply, en el espacio de coordenadas propio de
SuperSplat) contra el checkpoint original de Nerfstudio, usando la
transformacion resuelta por align_supersplat_export.py, para poder evaluarla
con ns-eval igual que las otras versiones de la POC.
"""
from pathlib import Path
import shutil
import numpy as np
import torch
from scipy.spatial import cKDTree
from plyfile import PlyData

SRC_RUN_DIR = Path(r"C:\nerfstudio_work\thesis\02-templete-central\02-resultados-finales\dji\splatfacto\2026-08-24_232220")
SRC_CKPT = SRC_RUN_DIR / "nerfstudio_models" / "step-000029999.ckpt"

EDITED_PLY = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\splat-editado.ply")
ALIGNMENT_NPZ = Path(r"C:\nerfstudio_work\thesis\00-auditoria\poc-floater-cleanup\supersplat_alignment.npz")

DST_RUN_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\poc-floater-cleanup\checkpoint-clean-manual\templete-central-realityscan-splat-ds8-clean-manual\splatfacto\2026-08-24_232220")
DST_CKPT = DST_RUN_DIR / "nerfstudio_models" / "step-000029999.ckpt"

MATCH_TOLERANCE = 1.0  # ~3x el RMSE de la alineacion (0.316)


def main():
    ckpt = torch.load(str(SRC_CKPT), map_location="cpu", weights_only=False)
    gp = ckpt["pipeline"]
    means = gp["_model.gauss_params.means"].detach().numpy().astype(np.float64)
    n0 = len(means)
    print(f"Gaussianas en el checkpoint original: {n0:,}")

    edited = PlyData.read(str(EDITED_PLY))["vertex"].data
    edited_xyz = np.column_stack([edited[c] for c in ["x", "y", "z"]]).astype(np.float64)
    print(f"Gaussianas en el editado a mano: {len(edited_xyz):,}")

    align = np.load(ALIGNMENT_NPZ)
    R, s, t = align["R"], float(align["s"]), align["t"]
    edited_aligned = s * (edited_xyz @ R.T) + t

    tree = cKDTree(means)
    dists, idx = tree.query(edited_aligned, k=1, workers=-1)

    matched = dists < MATCH_TOLERANCE
    n_matched = int(matched.sum())
    print(f"Matcheadas (tolerancia {MATCH_TOLERANCE}): {n_matched:,} de {len(edited_xyz):,} "
          f"({100*n_matched/len(edited_xyz):.2f}%) -- distancia mediana: {np.median(dists):.4f}")

    mask_keep = np.zeros(n0, dtype=bool)
    mask_keep[idx[matched]] = True
    n_kept = int(mask_keep.sum())
    print(f"Gaussianas a conservar en el checkpoint (via match): {n_kept:,} ({100*n_kept/n0:.2f}%, "
          f"removido {100*(1-n_kept/n0):.2f}%)")

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
    print(f"[OK] checkpoint (edicion manual replicada): {DST_CKPT}")

    for fname in ["config.yml", "dataparser_transforms.json"]:
        src = SRC_RUN_DIR / fname
        if src.exists():
            shutil.copy2(src, DST_RUN_DIR / fname)
            print(f"[OK] copiado: {fname}")


if __name__ == "__main__":
    main()
