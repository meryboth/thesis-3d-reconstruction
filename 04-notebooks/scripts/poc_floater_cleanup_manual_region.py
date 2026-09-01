"""
POC (parte 4b): en vez de matchear gaussiana-por-gaussiana (fallo por
colision de vecinos, ver poc_floater_cleanup_manual_match.py), usa la nube
de puntos editada a mano (ya alineada al espacio del checkpoint) como
PLANTILLA DE REGION: cualquier gaussiana del checkpoint que caiga cerca de
algun punto conservado por la usuaria se retiene; el resto se descarta.
Esto reproduce la FORMA de la edicion manual sin depender de una
correspondencia exacta punto a punto.
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

DST_RUN_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\poc-floater-cleanup\checkpoint-clean-manual-region\templete-central-realityscan-splat-ds8-clean-manual-region\splatfacto\2026-08-24_232220")
DST_CKPT = DST_RUN_DIR / "nerfstudio_models" / "step-000029999.ckpt"

REGION_RADIUS = 1.75  # calibrado por barrido para reproducir el ~54.7% removido de la edicion manual


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

    region_tree = cKDTree(edited_aligned)
    dists, _ = region_tree.query(means, k=1, workers=-1)
    mask_keep = dists < REGION_RADIUS
    n_kept = int(mask_keep.sum())

    print(f"Region radius: {REGION_RADIUS}")
    print(f"Gaussianas dentro de la region (conservadas): {n_kept:,} ({100*n_kept/n0:.2f}%, "
          f"removido {100*(1-n_kept/n0):.2f}%)")
    print(f"Referencia -- edicion manual original: 143,136 de 315,787 en el .ply exportado (54.68% removido)")

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
    print(f"[OK] checkpoint (region de la edicion manual): {DST_CKPT}")

    for fname in ["config.yml", "dataparser_transforms.json"]:
        src = SRC_RUN_DIR / fname
        if src.exists():
            shutil.copy2(src, DST_RUN_DIR / fname)
            print(f"[OK] copiado: {fname}")


if __name__ == "__main__":
    main()
