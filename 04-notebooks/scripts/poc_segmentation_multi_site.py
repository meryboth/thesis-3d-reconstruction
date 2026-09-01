"""
Segmentacion semantica basica (cubierta / columna / baranda-no-estructural /
piso-base) por geometria local, corrida sobre los 3 casos de estudio. Version
consolidada de poc_segmentation_normals_densecloud.py + level_point_cloud.py.

Pipeline por sitio:
  1. Cargar la nube densa (texto x,y,z,r,g,b o .ply binario, con o sin normales
     precalculadas).
  2. Nivelar: ajustar un plano al piso por RANSAC y rotar la nube para que
     quede horizontal (normal = +Z) -- necesario porque ni RealityScan ni
     COLMAP garantizan que el eje Z crudo sea el "arriba" real.
  3. Normales locales: si el archivo ya las trae (Los Paraguas, via COLMAP/
     CloudCompare) se usan directamente (rotadas con el mismo nivelado); si
     no (Templete, Panteon) se estiman por PCA sobre los k vecinos mas
     cercanos.
  4. Clasificar por bandas de altura (techo/piso, detectados por picos de
     densidad en el histograma de Z) + agrupamiento por celda de planta para
     separar columna estructural (llega hasta el techo) de baranda/pared no
     estructural (se corta antes).
  5. Exportar .ply coloreado por clase para el visor web.
"""
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from plyfile import PlyData, PlyElement

THESIS_ROOT = Path(r"C:\nerfstudio_work\thesis")
OUT_DIR = THESIS_ROOT / "00-auditoria" / "poc-segmentacion"
WEB_DIR = THESIS_ROOT / "06-sitio-web" / "public" / "segmentacion"
OUT_DIR.mkdir(parents=True, exist_ok=True)
WEB_DIR.mkdir(parents=True, exist_ok=True)

SITES = [
    {
        "id": "templete-central-dji",
        "label": "Templete Central (DJI)",
        "path": THESIS_ROOT / "02-templete-central/02-resultados-finales/dji/colmap-fotogrametria/nube-densa.xyz",
        "format": "xyz_text",
        "sample_every_n": 30,
    },
    {
        "id": "panteon-asociacion-espanola-dji",
        "label": "Panteón Asociación Española (DJI)",
        "path": THESIS_ROOT / "03-panteon-asociacion-espanola/02-resultados-finales/dji/colmap-fotogrametria/nube-densa.xyz",
        "format": "xyz_text",
        "sample_every_n": 30,
        "exg_max": 5,  # arboledas cercanas (Cap. 3): filtra vegetacion por color antes de nivelar/segmentar
    },
    {
        "id": "los-paraguas-dron",
        "label": "Los Paraguas (dron)",
        "path": THESIS_ROOT / "01-paraguas-vicentelopez/02-resultados-finales/colmap-fotogrametria-densa/fused_medium_high_clean.ply",
        "format": "ply_binary",
        "sample_every_n": 1,
    },
]

K_NEIGHBORS = 20
VERTICAL_THRESHOLD = 0.5
CELL_SIZE = 0.4
COLUMN_HEIGHT_FRAC = 0.7

CLASS_RGB = {
    "cubierta": (231, 76, 60),
    "piso/base": (41, 128, 185),
    "columna": (39, 174, 96),
    "baranda/pared no estructural": (241, 196, 15),
}


# ---------- carga ----------

def load_xyz_text(path, every_n):
    xs, ys, zs, rs, gs, bs = [], [], [], [], [], []
    with open(path, "r") as f:
        for i, line in enumerate(f):
            if i % every_n != 0:
                continue
            parts = line.split()
            if len(parts) < 6:
                continue
            xs.append(float(parts[0])); ys.append(float(parts[1])); zs.append(float(parts[2]))
            rs.append(int(parts[3])); gs.append(int(parts[4])); bs.append(int(parts[5]))
    xyz = np.column_stack([xs, ys, zs]).astype(np.float64)
    rgb = np.column_stack([rs, gs, bs]).astype(np.uint8)
    return xyz, rgb, None


def load_ply(path):
    v = PlyData.read(str(path))["vertex"].data
    names = v.dtype.names
    xyz = np.column_stack([v["x"], v["y"], v["z"]]).astype(np.float64)
    rgb = np.column_stack([v["red"], v["green"], v["blue"]]).astype(np.uint8)
    normals = None
    if "nx" in names and "ny" in names and "nz" in names:
        normals = np.column_stack([v["nx"], v["ny"], v["nz"]]).astype(np.float64)
    return xyz, rgb, normals


# ---------- nivelado (RANSAC al piso) ----------

def fit_plane_ransac(points, n_iters=300, dist_threshold=0.03, sample_size=20000, seed=42):
    rng = np.random.default_rng(seed)
    n = len(points)
    sub = points[rng.choice(n, size=min(sample_size, n), replace=False)]
    best_inliers, best_normal, best_d = -1, None, None
    for _ in range(n_iters):
        p0, p1, p2 = sub[rng.choice(len(sub), size=3, replace=False)]
        normal = np.cross(p1 - p0, p2 - p0)
        norm = np.linalg.norm(normal)
        if norm < 1e-9:
            continue
        normal = normal / norm
        d = -normal @ p0
        inliers = int(np.sum(np.abs(sub @ normal + d) < dist_threshold))
        if inliers > best_inliers:
            best_inliers, best_normal, best_d = inliers, normal, d
    print(f"  RANSAC piso: {best_inliers:,}/{len(sub):,} inliers ({100*best_inliers/len(sub):.1f}%)")
    return best_normal, best_d


def rotation_to_align(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    v = np.cross(a, b)
    c = np.dot(a, b)
    if np.linalg.norm(v) < 1e-9:
        return np.eye(3) if c > 0 else -np.eye(3)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * (1 / (1 + c))


def level(xyz, normals, veg_mask=None):
    # limitar el pool de candidatos de RANSAC a la franja baja de altura (percentil
    # 20 del eje de menor rango, que es casi siempre el "arriba" real aunque este
    # sin nivelar): en sitios altos (Panteon, ~17m) el piso es una fraccion chica
    # del total de puntos, y muestrear 3 puntos de toda la nube rara vez cae los
    # 3 en el piso real. Se excluye vegetacion del pool para que copas de arbol
    # no compitan por el ajuste del plano.
    range_per_axis = xyz.max(axis=0) - xyz.min(axis=0)
    rough_up_axis = np.argmin(range_per_axis)
    low_cutoff = np.percentile(xyz[:, rough_up_axis], 20)
    candidate_mask = xyz[:, rough_up_axis] <= low_cutoff
    if veg_mask is not None:
        candidate_mask &= ~veg_mask
    candidates = xyz[candidate_mask]
    print(f"  Candidatos para RANSAC de piso (banda baja, eje {rough_up_axis}): {len(candidates):,} de {len(xyz):,}")

    normal, d = fit_plane_ransac(candidates)

    # Orientar la normal "hacia arriba": si hay normales precalculadas (MVS/
    # CloudCompare), se usan directamente -- por convencion esas normales
    # apuntan hacia afuera de la superficie solida (para el piso, hacia
    # arriba), y es mucho mas confiable que contar de que lado esta la
    # mediana de los puntos. Ese criterio de mediana falla cuando el pasto/
    # piso domina tanto el conteo de puntos que la mediana global queda
    # practicamente encima del plano (caso real: Los Paraguas).
    if normals is not None:
        dist_to_plane = np.abs(xyz @ normal + d)
        ground_inliers = dist_to_plane < 0.05
        mean_normal_dir = normals[ground_inliers].mean(axis=0)
        if mean_normal_dir @ normal < 0:
            normal, d = -normal, -d
        print(f"  Signo de 'arriba' resuelto con normales precalculadas ({int(ground_inliers.sum()):,} puntos de piso).")
    elif np.median(xyz @ normal + d) < 0:
        normal, d = -normal, -d

    R = rotation_to_align(normal, np.array([0.0, 0.0, 1.0]))
    xyz_leveled = xyz @ R.T
    ground_z = np.median(xyz_leveled[:, 2][np.abs(xyz @ normal + d) < 0.05])
    xyz_leveled[:, 2] -= ground_z
    normals_leveled = (normals @ R.T) if normals is not None else None
    return xyz_leveled, normals_leveled


# ---------- normales (si no vienen en el archivo) ----------

def estimate_normals(points, k=K_NEIGHBORS):
    tree = cKDTree(points)
    _, idx = tree.query(points, k=k, workers=-1)
    neighbors = points[idx]
    centered = neighbors - neighbors.mean(axis=1, keepdims=True)
    cov = np.einsum("nki,nkj->nij", centered, centered) / k
    eigvals, eigvecs = np.linalg.eigh(cov)
    normals = eigvecs[:, :, 0]
    flip = normals[:, 2] < 0
    normals[flip] *= -1
    return normals


# ---------- segmentacion ----------

def segment(xyz, normals, veg_mask=None):
    verticality = np.abs(normals[:, 2])
    z = xyz[:, 2]
    if veg_mask is None:
        veg_mask = np.zeros(len(xyz), dtype=bool)

    # localizar los picos de techo/piso solo con los puntos mas densos (ruido
    # de reconstruccion disperso -- ej. pasto mal triangulado -- puede tener
    # una masa de puntos comparable a la estructura real y confundir la
    # deteccion del pico si se usan todos los puntos por igual), y nunca con
    # vegetacion (copas de arbol dispersas en un rango de altura enorme).
    non_veg_idx = np.where(~veg_mask)[0]
    tree_all = cKDTree(xyz)
    sample_n = min(len(non_veg_idx), 150_000)
    rng = np.random.default_rng(0)
    sample_idx = rng.choice(non_veg_idx, size=sample_n, replace=False)
    sample_dists, _ = tree_all.query(xyz[sample_idx], k=9, workers=-1)
    sample_density = sample_dists[:, 1:].mean(axis=1)
    dense_cutoff = np.percentile(sample_density, 50)
    z_for_peaks = z[sample_idx][sample_density <= dense_cutoff]
    print(f"  Puntos densos usados para ubicar picos: {len(z_for_peaks):,} de {sample_n:,} muestreados")

    z_hist, bin_edges = np.histogram(z_for_peaks, bins=200)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    z_mid = (z.min() + z.max()) / 2
    upper_half = bin_centers > z_mid
    lower_half = ~upper_half

    roof_peak_idx = np.where(upper_half)[0][np.argmax(z_hist[upper_half])]
    roof_peak_density = z_hist[roof_peak_idx]
    slab_bottom_idx = roof_peak_idx
    for i in range(roof_peak_idx, 0, -1):
        if z_hist[i] < 0.2 * roof_peak_density:
            slab_bottom_idx = i
            break
    slab_bottom_z = bin_centers[slab_bottom_idx]

    floor_peak_idx = np.where(lower_half)[0][np.argmax(z_hist[lower_half])]
    floor_peak_density = z_hist[floor_peak_idx]
    floor_top_idx = floor_peak_idx
    for i in range(floor_peak_idx, len(z_hist)):
        if z_hist[i] < 0.2 * floor_peak_density:
            floor_top_idx = i
            break
    floor_top_z = bin_centers[floor_top_idx]

    print(f"  Losa: pico z={bin_centers[roof_peak_idx]:.3f}, banda desde z={slab_bottom_z:.3f}")
    print(f"  Piso: pico z={bin_centers[floor_peak_idx]:.3f}, banda hasta z={floor_top_z:.3f}")

    is_vertical = verticality <= VERTICAL_THRESHOLD
    is_roof = z >= slab_bottom_z
    is_floor = (~is_roof) & (z <= floor_top_z)

    # superficies con doble curvatura (ej. cubiertas tipo "hongo" de Los
    # Paraguas) tienen puntos horizontales que se curvan por debajo del corte
    # de techo sin llegar a ser piso real -- sin este ajuste caian en el
    # fallback por defecto ("piso/base") solo por no calificar ni como techo
    # ni como pared. Se reasignan a cubierta si estan mas cerca en altura de
    # la banda de techo que de la de piso.
    mid_threshold = (floor_top_z + slab_bottom_z) / 2
    is_horizontal_midband = (~is_roof) & (~is_floor) & (~is_vertical) & (~veg_mask)
    is_roof = is_roof | (is_horizontal_midband & (z > mid_threshold))

    is_wall = (~is_roof) & (~is_floor) & is_vertical & (~veg_mask)

    wall_idx = np.where(is_wall)[0]
    if len(wall_idx) > 0:
        cell_x = np.floor(xyz[wall_idx, 0] / CELL_SIZE).astype(np.int64)
        cell_y = np.floor(xyz[wall_idx, 1] / CELL_SIZE).astype(np.int64)
        cell_key = cell_x * 1_000_000 + cell_y
        unique_cells, inverse = np.unique(cell_key, return_inverse=True)
        cell_max_z = np.full(len(unique_cells), -np.inf)
        np.maximum.at(cell_max_z, inverse, xyz[wall_idx, 2])
        column_height_threshold = floor_top_z + COLUMN_HEIGHT_FRAC * (slab_bottom_z - floor_top_z)
        cell_is_column = cell_max_z >= column_height_threshold
        point_is_column = cell_is_column[inverse]
        print(f"  Umbral columna: {column_height_threshold:.3f} "
              f"({len(unique_cells):,} celdas, {int(cell_is_column.sum()):,} columna)")
    else:
        point_is_column = np.zeros(0, dtype=bool)

    labels = np.full(len(xyz), "piso/base", dtype=object)
    labels[is_roof] = "cubierta"
    labels[wall_idx[point_is_column]] = "columna"
    labels[wall_idx[~point_is_column]] = "baranda/pared no estructural"

    return labels


# ---------- export ----------

def export_colored_ply(xyz, labels, out_path):
    seg_rgb = np.zeros((len(xyz), 3), dtype=np.uint8)
    for lbl, color in CLASS_RGB.items():
        seg_rgb[labels == lbl] = color
    vertex = np.zeros(len(xyz), dtype=[
        ("x", "f4"), ("y", "f4"), ("z", "f4"),
        ("red", "u1"), ("green", "u1"), ("blue", "u1"),
    ])
    vertex["x"], vertex["y"], vertex["z"] = xyz[:, 0], xyz[:, 1], xyz[:, 2]
    vertex["red"], vertex["green"], vertex["blue"] = seg_rgb[:, 0], seg_rgb[:, 1], seg_rgb[:, 2]
    PlyData([PlyElement.describe(vertex, "vertex")], text=False).write(str(out_path))


def detect_vegetation(rgb, exg_max=10):
    """Detecta puntos vegetales por color (indice ExG = 2G-R-B, estandar en
    vision agricola para detectar follaje). Se usan para excluirlos del
    calculo geometrico (picos de altura, ajuste de plano, deteccion de
    columnas) y del export final -- los sitios con arboledas cercanas (ver
    Panteon, Capitulo 3) tienen puntos de copa de arbol dispersos en un
    rango de altura enorme que arruina esa deteccion, y mostrarlos con su
    propio color (probado en esta sesion) termino ensuciando la lectura del
    edificio: parte de la vegetacion real cuelga directamente sobre la
    cupula en las fotos, asi que aparecia superpuesta a la arquitectura sin
    importar que tan bien se la clasificara."""
    r = rgb[:, 0].astype(np.int32)
    g = rgb[:, 1].astype(np.int32)
    b = rgb[:, 2].astype(np.int32)
    exg = 2 * g - r - b
    veg_mask = exg > exg_max
    print(f"  Vegetacion detectada por color (ExG>{exg_max}): {int(veg_mask.sum()):,} de {len(rgb):,} puntos")
    return veg_mask




def main():
    for site in SITES:
        print(f"\n=== {site['label']} ===")
        if site["format"] == "xyz_text":
            xyz, rgb, normals = load_xyz_text(site["path"], site["sample_every_n"])
        else:
            xyz, rgb, normals = load_ply(site["path"])
        print(f"  Puntos: {len(xyz):,} (normales {'precalculadas' if normals is not None else 'a estimar'})")

        if "exg_max" in site:
            veg_mask = detect_vegetation(rgb, exg_max=site["exg_max"])
        else:
            veg_mask = np.zeros(len(xyz), dtype=bool)

        xyz_l, normals_l = level(xyz, normals, veg_mask)
        if normals_l is None:
            normals_l = estimate_normals(xyz_l)

        labels = segment(xyz_l, normals_l, veg_mask)

        keep = ~veg_mask
        xyz_out, labels_out = xyz_l[keep], labels[keep]
        counts = {lbl: int(np.sum(labels_out == lbl)) for lbl in CLASS_RGB}
        print("  Conteo:", counts, f"(vegetacion excluida: {int(veg_mask.sum()):,})")

        out_path = WEB_DIR / f"{site['id']}.ply"
        export_colored_ply(xyz_out, labels_out, out_path)
        print(f"  [OK] {out_path}")


if __name__ == "__main__":
    main()
