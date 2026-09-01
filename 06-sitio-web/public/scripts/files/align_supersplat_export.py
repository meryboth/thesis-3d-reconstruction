"""
Resuelve la transformacion de similitud (rotacion + escala uniforme +
traslacion) que aplica SuperSplat al cargar/exportar un splat.ply, comparado
contra el espacio de coordenadas original de Nerfstudio (el mismo que usan
el checkpoint y el splat.ply que exporta `ns-export gaussian-splat`).

No hay transform.json ni metadata compartida entre ambos -- se resuelve de
forma puramente geometrica (ICP con escala), aprovechando que un splat.ply
editado en SuperSplat es un SUBCONJUNTO del splat.ply original (mismos
puntos, algunos borrados), nunca puntos movidos.

Uso como modulo: `align_points(source_xyz, target_xyz) -> (R, s, t, rmse)`
tal que `target_approx = s * (source_xyz @ R.T) + t`.

Corrido como script standalone: alinea SRC_PLY (espacio SuperSplat) contra
REF_PLY (espacio Nerfstudio/checkpoint) y reporta el error residual.
"""
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from plyfile import PlyData

REF_PLY = Path(r"C:\nerfstudio_work\thesis\02-templete-central\02-resultados-finales\dji\splatfacto\export\splat.ply")
SRC_PLY = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\splat-editado.ply")

MAX_ITERS = 60
SUBSAMPLE = 40_000
RANDOM_SEED = 42


def load_xyz(path):
    v = PlyData.read(str(path))["vertex"].data
    return np.column_stack([v["x"], v["y"], v["z"]]).astype(np.float64)


def umeyama(src, dst):
    """Similarity transform (R, s, t) que minimiza ||s*R@src + t - dst||^2, con
    correspondencia 1:1 ya dada (src[i] <-> dst[i]). Metodo estandar de Umeyama (1991)."""
    mu_src = src.mean(axis=0)
    mu_dst = dst.mean(axis=0)
    src_c = src - mu_src
    dst_c = dst - mu_dst

    cov = (dst_c.T @ src_c) / len(src)
    U, D, Vt = np.linalg.svd(cov)
    S = np.eye(3)
    if np.linalg.det(U) * np.linalg.det(Vt) < 0:
        S[-1, -1] = -1

    R = U @ S @ Vt
    var_src = (src_c ** 2).sum() / len(src)
    s = np.trace(np.diag(D) @ S) / var_src
    t = mu_dst - s * (R @ mu_src)
    return R, s, t


def pca_axes(points):
    c = points - points.mean(axis=0)
    cov = (c.T @ c) / len(points)
    eigvals, eigvecs = np.linalg.eigh(cov)
    order = np.argsort(-eigvals)
    return eigvecs[:, order]  # columnas = ejes principales, de mayor a menor varianza


def coarse_align(src, dst):
    """Alineacion inicial: centra, escala por RMS de distancia al centroide, y
    prueba las 8 combinaciones de signo de los ejes principales (PCA) para
    resolver la ambiguedad de reflexion/orientacion antes de afinar con ICP."""
    src_c = src - src.mean(axis=0)
    dst_c = dst - dst.mean(axis=0)

    scale = np.sqrt((dst_c ** 2).sum(axis=1).mean()) / np.sqrt((src_c ** 2).sum(axis=1).mean())

    axes_src = pca_axes(src_c)
    axes_dst = pca_axes(dst_c)

    best = None
    tree_dst = cKDTree(dst_c)
    rng = np.random.default_rng(RANDOM_SEED)
    probe_idx = rng.choice(len(src_c), size=min(3000, len(src_c)), replace=False)

    for sx in (1, -1):
        for sy in (1, -1):
            for sz in (1, -1):
                signs = np.array([sx, sy, sz])
                R = axes_dst @ np.diag(signs) @ axes_src.T
                if np.linalg.det(R) < 0:
                    continue  # solo rotaciones propias, sin reflexion (la escala ya es positiva)
                transformed = scale * (src_c[probe_idx] @ R.T)
                d, _ = tree_dst.query(transformed, k=1, workers=-1)
                err = np.median(d)
                if best is None or err < best[0]:
                    best = (err, R)

    _, R = best
    t = dst.mean(axis=0) - scale * (R @ src.mean(axis=0))
    return R, scale, t


def icp_refine(src, dst_tree, R, s, t, iters=MAX_ITERS, sample=SUBSAMPLE):
    rng = np.random.default_rng(RANDOM_SEED)
    idx = rng.choice(len(src), size=min(sample, len(src)), replace=False)
    src_sample = src[idx]

    for i in range(iters):
        transformed = s * (src_sample @ R.T) + t
        dists, nn_idx = dst_tree.query(transformed, k=1, workers=-1)

        # descarta el 10% de peores matches (probables puntos sin correspondencia real)
        cutoff = np.percentile(dists, 90)
        good = dists < cutoff

        dst_matched = dst_tree.data[nn_idx[good]]
        R, s, t = umeyama(src_sample[good], dst_matched)

        rmse = np.sqrt(np.mean(dists[good] ** 2))
        if i % 10 == 0 or i == iters - 1:
            print(f"  iter {i:>3}: rmse={rmse:.6f}  matched<{cutoff:.4f}: {good.sum()}/{len(good)}")

    return R, s, t, rmse


def align_points(source_xyz, target_xyz):
    tree = cKDTree(target_xyz)
    R0, s0, t0 = coarse_align(source_xyz, target_xyz)
    print(f"Alineacion inicial (PCA): escala={s0:.6f}")
    R, s, t, rmse = icp_refine(source_xyz, tree, R0, s0, t0)
    return R, s, t, rmse


def main():
    src = load_xyz(SRC_PLY)
    dst = load_xyz(REF_PLY)
    print(f"Fuente (SuperSplat): {len(src):,} puntos, rango {src.min(axis=0)} a {src.max(axis=0)}")
    print(f"Referencia (Nerfstudio): {len(dst):,} puntos, rango {dst.min(axis=0)} a {dst.max(axis=0)}")

    R, s, t, rmse = align_points(src, dst)
    print()
    print("Transformacion resuelta: target = s * (source @ R.T) + t")
    print("R =", R.tolist())
    print("s =", s)
    print("t =", t.tolist())
    print(f"RMSE final: {rmse:.6f} (comparar contra la escala de la escena, ~{dst.std():.2f})")

    np.savez(
        Path(r"C:\nerfstudio_work\thesis\00-auditoria\poc-floater-cleanup\supersplat_alignment.npz"),
        R=R, s=s, t=t, rmse=rmse,
    )
    print("[OK] Transformacion guardada en 00-auditoria/poc-floater-cleanup/supersplat_alignment.npz")


if __name__ == "__main__":
    main()
