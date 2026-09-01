"""
Nivela una nube de puntos cruda de RealityScan (sin gravity-alignment, a
diferencia de los datasets procesados por Nerfstudio que si tienen ese ajuste
via dataparser_transforms.json) ajustando un plano por RANSAC al piso/
pavimento -- la superficie planar dominante de la escena -- y rotando toda la
nube para que ese plano quede horizontal (normal = +Z).

Uso como modulo: `level_points(xyz) -> (xyz_leveled, R, ground_z)`.
"""
import numpy as np


def fit_plane_ransac(points, n_iters=300, dist_threshold=0.03, sample_size=20000, seed=42):
    """Ajusta un plano (normal, punto) por RANSAC. Devuelve la normal orientada
    hacia +Z (arriba) del lado que tenga mas puntos."""
    rng = np.random.default_rng(seed)
    n = len(points)
    sub_idx = rng.choice(n, size=min(sample_size, n), replace=False)
    sub = points[sub_idx]

    best_inliers = -1
    best_normal = None
    best_d = None

    for _ in range(n_iters):
        idx3 = rng.choice(len(sub), size=3, replace=False)
        p0, p1, p2 = sub[idx3]
        normal = np.cross(p1 - p0, p2 - p0)
        norm = np.linalg.norm(normal)
        if norm < 1e-9:
            continue
        normal = normal / norm
        d = -normal @ p0

        dist = np.abs(sub @ normal + d)
        inliers = int(np.sum(dist < dist_threshold))
        if inliers > best_inliers:
            best_inliers = inliers
            best_normal = normal
            best_d = d

    print(f"Mejor plano RANSAC: {best_inliers:,}/{len(sub):,} inliers ({100*best_inliers/len(sub):.1f}%)")
    return best_normal, best_d


def rotation_to_align(a, b):
    """Matriz de rotacion que lleva el vector unitario `a` a coincidir con `b`."""
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    v = np.cross(a, b)
    c = np.dot(a, b)
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3) if c > 0 else -np.eye(3)
    vx = np.array([
        [0, -v[2], v[1]],
        [v[2], 0, -v[0]],
        [-v[1], v[0], 0],
    ])
    R = np.eye(3) + vx + vx @ vx * (1 / (1 + c))
    return R


def level_points(points):
    normal, d = fit_plane_ransac(points)
    # asegurar que la normal apunte "hacia arriba" (del lado donde hay menos puntos,
    # asumiendo que la mayoria de la escena esta por ENCIMA del piso, no por debajo)
    signed_dist = points @ normal + d
    if np.median(signed_dist) < 0:
        normal = -normal
        d = -d

    R = rotation_to_align(normal, np.array([0.0, 0.0, 1.0]))
    leveled = points @ R.T

    ground_z = np.median(leveled[:, 2][np.abs((points @ normal + d)) < 0.05])
    leveled[:, 2] -= ground_z

    print(f"Normal del piso (original): {normal}")
    print(f"Altura del piso tras nivelar (deberia ser ~0): {np.median(leveled[:, 2][np.abs((points @ normal + d)) < 0.05]) - ground_z:.4f}")
    return leveled, R, ground_z


if __name__ == "__main__":
    from pathlib import Path

    XYZ_PATH = Path(r"C:\nerfstudio_work\thesis\02-templete-central\02-resultados-finales\dji\colmap-fotogrametria\nube-densa.xyz")

    xs, ys, zs = [], [], []
    with open(XYZ_PATH, "r") as f:
        for i, line in enumerate(f):
            if i % 30 != 0:
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            xs.append(float(parts[0])); ys.append(float(parts[1])); zs.append(float(parts[2]))
    xyz = np.column_stack([xs, ys, zs]).astype(np.float64)
    print(f"Puntos: {len(xyz):,}")

    leveled, R, ground_z = level_points(xyz)
    print("R =", R.tolist())
    print("ground_z (offset restado) =", ground_z)
    np.savez(
        Path(r"C:\nerfstudio_work\thesis\00-auditoria\poc-segmentacion\leveling_transform.npz"),
        R=R, ground_z=ground_z,
    )
    print("[OK] guardado leveling_transform.npz")
