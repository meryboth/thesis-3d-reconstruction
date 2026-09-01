"""
PRUEBA EXPLORATORIA v3: segmentar una nube de puntos densa en elementos
(cilindros / planos-caja) via RANSAC iterativo, usando las normales que ya
trae la nube (exportadas por CloudCompare junto con x,y,z,r,g,b), en vez de
estimarlas.

Historial de esta prueba (para que quede el porque de este diseno):
  v1: clustering por conectividad espacial de TODA la nube -> 1 solo cluster
      (una columna y la cubierta que sostiene son un unico objeto fisico
      conectado, conectividad espacial no las separa).
  v2: clasificacion local por punto (linealidad/planaridad via PCA de
      vecinos, features de Weinmann et al.) + region growing -> fragmento
      una columna real en 275 pedazos; el pedazo que paso el filtro de
      tamano tenia elongacion 3.48 (mediocre), mientras pedazos de 50-90
      puntos llegaban a elongacion 40+ pero quedaban afuera por chicos.
      El cilindro resultante no coincidia con la columna real.
  v3 (este archivo): se probo pyransac3d.Cylinder, pero su propia
      documentacion advierte "does NOT present good results on real data",
      y ademas se colgo (bucle sin cota clara en el caso de 3 puntos
      cuasi-colineales de la muestra minima). Se descarto.
      Se implementa un RANSAC de cilindro propio, usando el metodo estandar
      de 2 puntos + sus normales (el eje del cilindro es perpendicular a
      ambas normales; el centro/radio salen de intersectar los dos rayos
      radiales en el plano perpendicular al eje) -- es el metodo clasico
      (Chaperon & Goulette 2001) para RANSAC de cilindros con normales
      disponibles, numericamente estable y con cota de iteraciones estricta
      (nunca puede colgarse: cada iteracion es O(N) vectorizado y las
      muestras degeneradas simplemente se descartan con continue).

Metodo general (greedy iterativo, "Efficient RANSAC" a lo Schnabel et al.
2007): en cada paso, probar el mejor plano y el mejor cilindro sobre los
puntos que quedan, quedarse con el que junte mas inliers, sacarlo del
conjunto, repetir. Lo que sobra es "freeform".

Corre con el Python del sistema (numpy/scipy/plyfile), no con el de Blender.
"""
import json
import sys
from pathlib import Path

import numpy as np
from plyfile import PlyData

PLY_PATH = sys.argv[1] if len(sys.argv) > 1 else r"C:\nerfstudio_work\thesis\01-paraguas-vicentelopez\02-resultados-finales\colmap-fotogrametria-densa\fused_medium_high_clean.ply"
OUT_JSON = sys.argv[2] if len(sys.argv) > 2 else r"C:\nerfstudio_work\thesis\00-auditoria\blender-pointcloud-test\primitives.json"

MAX_SHAPES = 12
RANSAC_MAX_POINTS = 80000
MIN_INLIERS_CYLINDER = 150
MIN_INLIERS_PLANE = 250
RANSAC_ITERATIONS = 800
PLANAR_RESIDUAL_RATIO = 0.06
MIN_NORMAL_SEPARATION = 0.15  # dos normales casi paralelas no definen bien un eje de cilindro


def load_points_and_normals(path):
    ply = PlyData.read(path)
    v = ply["vertex"]
    pts = np.stack([v["x"], v["y"], v["z"]], axis=1).astype(np.float64)
    names = v.data.dtype.names
    if "nx" in names:
        normals = np.stack([v["nx"], v["ny"], v["nz"]], axis=1).astype(np.float64)
        norms = np.linalg.norm(normals, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normals = normals / norms
    else:
        normals = None
    return pts, normals


def maybe_subsample(pts, normals, max_points, seed=0):
    if len(pts) <= max_points:
        return pts, normals
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(pts), size=max_points, replace=False)
    return pts[idx], (normals[idx] if normals is not None else None)


def ransac_plane(pts, thresh, max_iter, rng):
    n = len(pts)
    best_inliers = np.array([], dtype=np.int64)
    for _ in range(max_iter):
        i, j, k = rng.choice(n, size=3, replace=False)
        p0, p1, p2 = pts[i], pts[j], pts[k]
        v1, v2 = p1 - p0, p2 - p0
        normal = np.cross(v1, v2)
        norm_len = np.linalg.norm(normal)
        if norm_len < 1e-9:
            continue
        normal /= norm_len
        dist = np.abs((pts - p0) @ normal)
        inliers = np.where(dist <= thresh)[0]
        if len(inliers) > len(best_inliers):
            best_inliers = inliers
    return best_inliers


def ransac_cylinder(pts, normals, thresh, max_iter, rng):
    n = len(pts)
    best_inliers = np.array([], dtype=np.int64)
    best_axis = None
    for _ in range(max_iter):
        i, j = rng.choice(n, size=2, replace=False)
        n1, n2 = normals[i], normals[j]
        axis = np.cross(n1, n2)
        axis_len = np.linalg.norm(axis)
        if axis_len < MIN_NORMAL_SEPARATION:
            continue  # normales casi paralelas: no definen un eje confiable
        axis /= axis_len

        # proyectar todo al plano perpendicular al eje (2D local) para
        # intersectar los 2 rayos radiales p_i + t*n_i_proj
        u = pts[j] - pts[i]
        u = u - (u @ axis) * axis  # por si p_i/p_j no estan exactamente en el mismo plano perpendicular
        if np.linalg.norm(u) < 1e-9:
            ref = np.array([1.0, 0.0, 0.0]) if abs(axis[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
        e1 = n1 - (n1 @ axis) * axis
        if np.linalg.norm(e1) < 1e-9:
            continue
        e1 /= np.linalg.norm(e1)
        e2 = np.cross(axis, e1)

        def to_local(p):
            d = p - pts[i]
            return np.array([d @ e1, d @ e2])

        p1_local = np.array([0.0, 0.0])
        p2_local = to_local(pts[j])
        d1_local = np.array([n1 @ e1, n1 @ e2])
        d2_local = np.array([n2 @ e1, n2 @ e2])

        # resolver p1 + t1*d1 = p2 + t2*d2
        A = np.array([[d1_local[0], -d2_local[0]], [d1_local[1], -d2_local[1]]])
        det = np.linalg.det(A)
        if abs(det) < 1e-6:
            continue
        rhs = p2_local - p1_local
        t1, _ = np.linalg.solve(A, rhs)
        center_local = p1_local + t1 * d1_local
        radius = float(np.linalg.norm(center_local - p1_local))
        # una columna/viga real de este monumento no deberia tener un radio
        # de varios metros -- sin este tope, una superficie casi-plana se
        # ajusta con un cilindro de radio gigante (un plano ES el limite de
        # un cilindro cuando el radio -> infinito) y le compite de forma
        # espuria a los planos genuinos por cantidad de inliers.
        if radius < 0.03 or radius > 1.2:
            continue
        center = pts[i] + center_local[0] * e1 + center_local[1] * e2

        radial_vec = (pts - center) - (((pts - center) @ axis)[:, None] * axis)
        radial_dist = np.linalg.norm(radial_vec, axis=1)
        dist_hull = np.abs(radial_dist - radius)
        inliers = np.where(dist_hull <= thresh)[0]
        if len(inliers) > len(best_inliers):
            best_inliers = inliers
            best_axis = axis
    return best_inliers, best_axis


def refine_cylinder(pts):
    centroid = pts.mean(axis=0)
    centered = pts - centroid
    cov = (centered.T @ centered) / len(pts)
    eigvals, eigvecs = np.linalg.eigh(cov)
    order = np.argsort(eigvals)[::-1]
    axis = eigvecs[:, order[0]]
    proj_axis = centered @ axis
    radial = centered - np.outer(proj_axis, axis)
    radii = np.linalg.norm(radial, axis=1)
    radius = float(np.percentile(radii, 90))
    p_min = centroid + axis * proj_axis.min()
    p_max = centroid + axis * proj_axis.max()
    return {
        "type": "cylinder",
        "n_points": int(len(pts)),
        "centroid": centroid.tolist(),
        "axis": axis.tolist(),
        "radius": radius,
        "length": float(proj_axis.max() - proj_axis.min()),
        "endpoint_a": p_min.tolist(),
        "endpoint_b": p_max.tolist(),
    }


def refine_plane(pts):
    centroid = pts.mean(axis=0)
    centered = pts - centroid
    cov = (centered.T @ centered) / len(pts)
    eigvals, eigvecs = np.linalg.eigh(cov)
    order = np.argsort(eigvals)[::-1]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]
    L2 = max(eigvals[2], 1e-12)
    normal = eigvecs[:, 2]
    residual_rms = float(np.sqrt(np.mean((centered @ normal) ** 2)))
    proj0 = centered @ eigvecs[:, 0]
    proj1 = centered @ eigvecs[:, 1]
    size0 = float(proj0.max() - proj0.min())
    size1 = float(proj1.max() - proj1.min())
    thickness = max(float(4 * np.sqrt(L2)), 0.02)
    base = {
        "n_points": int(len(pts)),
        "centroid": centroid.tolist(),
        "axis_u": eigvecs[:, 0].tolist(),
        "axis_v": eigvecs[:, 1].tolist(),
        "normal": normal.tolist(),
        "size_u": size0,
        "size_v": size1,
        "thickness": thickness,
        "planar_residual_rms": residual_rms,
    }
    if residual_rms / max(size0, size1) <= PLANAR_RESIDUAL_RATIO:
        base["type"] = "box"
    else:
        base["type"] = "freeform_shell"
        base["note"] = "parche localmente plano pero con curvatura real a escala completa -- cascara, no placa"
    return base


def main():
    pts_full, normals_full = load_points_and_normals(PLY_PATH)
    if normals_full is None:
        print("[ERROR] la nube no trae normales (nx,ny,nz) -- el RANSAC de cilindro las necesita")
        sys.exit(1)

    bbox_diag = float(np.linalg.norm(pts_full.max(axis=0) - pts_full.min(axis=0)))
    thresh = bbox_diag * 0.003
    pts, normals = maybe_subsample(pts_full, normals_full, RANSAC_MAX_POINTS)
    print(f"[info] {len(pts_full)} puntos -> {len(pts)} para RANSAC, bbox diagonal {bbox_diag:.2f} m, umbral {thresh:.4f} m")

    rng = np.random.default_rng(42)
    remaining_pts = pts.copy()
    remaining_normals = normals.copy()
    results = []

    for step in range(MAX_SHAPES):
        if len(remaining_pts) < min(MIN_INLIERS_CYLINDER, MIN_INLIERS_PLANE):
            break

        plane_inliers = ransac_plane(remaining_pts, thresh, RANSAC_ITERATIONS, rng)
        cyl_inliers, cyl_axis = ransac_cylinder(remaining_pts, remaining_normals, thresh, RANSAC_ITERATIONS, rng)
        n_plane, n_cyl = len(plane_inliers), len(cyl_inliers)
        print(f"[step {step}] restantes={len(remaining_pts)}  plano={n_plane} inliers  cilindro={n_cyl} inliers")

        if n_cyl >= MIN_INLIERS_CYLINDER and n_cyl >= n_plane:
            prim = refine_cylinder(remaining_pts[cyl_inliers])
            results.append(prim)
            print(f"  -> CILINDRO: {prim['n_points']} pts, radio {prim['radius']:.3f} m, largo {prim['length']:.3f} m")
            mask = np.ones(len(remaining_pts), dtype=bool)
            mask[cyl_inliers] = False
        elif n_plane >= MIN_INLIERS_PLANE:
            prim = refine_plane(remaining_pts[plane_inliers])
            results.append(prim)
            print(f"  -> {prim['type'].upper()}: {prim['n_points']} pts, {prim['size_u']:.2f} x {prim['size_v']:.2f} m")
            mask = np.ones(len(remaining_pts), dtype=bool)
            mask[plane_inliers] = False
        else:
            print("  -> ningun candidato supera el minimo de inliers, se corta la extraccion")
            break

        remaining_pts = remaining_pts[mask]
        remaining_normals = remaining_normals[mask]

    by_type = {}
    for r in results:
        by_type[r["type"]] = by_type.get(r["type"], 0) + 1
    classified_pts = sum(r["n_points"] for r in results)
    print(f"\n[info] primitivas detectadas: {by_type}")
    print(f"[info] puntos explicados: {classified_pts} / {len(pts)} ({classified_pts/len(pts)*100:.1f}%)")

    Path(OUT_JSON).parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "source_ply": PLY_PATH,
            "method": "ransac_propio_con_normales_v3",
            "n_points_full": int(len(pts_full)),
            "ransac_threshold": thresh,
            "primitives": results,
        }, f, indent=2)
    print(f"[OK] guardado: {OUT_JSON}")


if __name__ == "__main__":
    main()
