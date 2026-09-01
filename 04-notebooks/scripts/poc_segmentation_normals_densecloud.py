"""
POC: misma segmentacion por normales locales (ver poc_segmentation_normals.py)
pero sobre la nube de puntos DENSA de SfM (RealityScan, nube-densa.xyz) en vez
de los centros de gaussianas de Splatfacto -- la nube densa no tiene el
problema de floaters ya documentado en Cap. 5, deberia dar un resultado mas
legible.

Formato de nube-densa.xyz: x y z r g b (sin encabezado), ~17.7M puntos --
se subsamplea leyendo 1 de cada N lineas para mantener el costo de estimar
normales (PCA local via KNN) acotado.
"""
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from plyfile import PlyData, PlyElement

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

XYZ_PATH = Path(r"C:\nerfstudio_work\thesis\02-templete-central\02-resultados-finales\dji\colmap-fotogrametria\nube-densa.xyz")
OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\poc-segmentacion")
OUT_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_EVERY_N = 30     # 1 de cada N lineas -> ~590k puntos de 17.7M
K_NEIGHBORS = 20
VERTICAL_THRESHOLD = 0.5


def load_sampled_xyzrgb(path, every_n):
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
    return xyz, rgb


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


def main():
    print(f"Leyendo {XYZ_PATH.name} (1 de cada {SAMPLE_EVERY_N} lineas)...")
    xyz, rgb = load_sampled_xyzrgb(XYZ_PATH, SAMPLE_EVERY_N)
    print(f"Puntos muestreados: {len(xyz):,}")
    print(f"Rango: {xyz.min(axis=0)} a {xyz.max(axis=0)}")

    normals = estimate_normals(xyz)
    verticality = np.abs(normals[:, 2])
    z = xyz[:, 2]

    # Banda de altura de la losa/cubierta: se busca por densidad, no por normal,
    # para que el canto vertical de la losa quede en la misma clase que su cara
    # superior (antes se mezclaba con las columnas por tener normal horizontal).
    z_hist, bin_edges = np.histogram(z, bins=200)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    # punto medio GEOMETRICO del rango de altura (no la mediana de puntos, que
    # queda sesgada hacia el piso porque hay muchisimos mas puntos de piso que de losa)
    z_mid = (z.min() + z.max()) / 2
    upper_half = bin_centers > z_mid
    roof_peak_idx = np.where(upper_half)[0][np.argmax(z_hist[upper_half])]
    roof_peak_z = bin_centers[roof_peak_idx]
    roof_peak_density = z_hist[roof_peak_idx]

    # desde el pico de la losa, bajar hasta que la densidad caiga a una fraccion
    # del pico (o se llegue a un minimo local) -- eso marca el espesor real de la losa
    slab_bottom_idx = roof_peak_idx
    for i in range(roof_peak_idx, 0, -1):
        if z_hist[i] < 0.2 * roof_peak_density:
            slab_bottom_idx = i
            break
    slab_bottom_z = bin_centers[slab_bottom_idx]

    # misma logica para el piso, buscando el pico en la mitad inferior
    lower_half = ~upper_half
    floor_peak_idx = np.where(lower_half)[0][np.argmax(z_hist[lower_half])]
    floor_peak_density = z_hist[floor_peak_idx]
    floor_top_idx = floor_peak_idx
    for i in range(floor_peak_idx, len(z_hist)):
        if z_hist[i] < 0.2 * floor_peak_density:
            floor_top_idx = i
            break
    floor_top_z = bin_centers[floor_top_idx]

    print(f"Losa: pico en z={roof_peak_z:.3f}, banda desde z={slab_bottom_z:.3f}")
    print(f"Piso: pico en z={bin_centers[floor_peak_idx]:.3f}, banda hasta z={floor_top_z:.3f}")

    is_vertical = verticality <= VERTICAL_THRESHOLD

    is_roof = z >= slab_bottom_z
    is_floor = (~is_roof) & (z <= floor_top_z)
    is_wall = (~is_roof) & (~is_floor) & is_vertical

    # Columna (estructural, llega hasta la losa) vs. baranda/pared baja (no
    # estructural, se corta bien antes de la losa) -- se decide por columna XY:
    # se agrupan los puntos "pared/columna" en celdas de planta y se mira hasta
    # que altura llega CADA celda (no cada punto individual), asi todos los
    # puntos de una misma columna fisica quedan clasificados igual.
    CELL_SIZE = 0.4
    COLUMN_HEIGHT_FRAC = 0.7  # una celda que llega a >=70% de la altura hasta la losa se considera columna

    wall_idx = np.where(is_wall)[0]
    cell_x = np.floor(xyz[wall_idx, 0] / CELL_SIZE).astype(np.int64)
    cell_y = np.floor(xyz[wall_idx, 1] / CELL_SIZE).astype(np.int64)
    cell_key = cell_x * 1_000_000 + cell_y  # hash simple para agrupar por celda de planta

    unique_cells, inverse, = np.unique(cell_key, return_inverse=True)
    cell_max_z = np.full(len(unique_cells), -np.inf)
    np.maximum.at(cell_max_z, inverse, xyz[wall_idx, 2])

    column_height_threshold = floor_top_z + COLUMN_HEIGHT_FRAC * (slab_bottom_z - floor_top_z)
    cell_is_column = cell_max_z >= column_height_threshold
    point_is_column = cell_is_column[inverse]

    labels = np.full(len(xyz), "sin clasificar", dtype=object)
    labels[is_floor] = "piso/base"
    labels[is_roof] = "cubierta"
    labels[wall_idx[point_is_column]] = "columna"
    labels[wall_idx[~point_is_column]] = "baranda/pared no estructural"
    # lo que no es techo/piso/pared claro (normal horizontal en la franja media,
    # ni escombro ni columna) se deja del lado del piso por ser la clase por defecto
    # mas segura para una heuristica simple
    unclassified = labels == "sin clasificar"
    labels[unclassified] = "piso/base"

    print(f"Umbral de altura para columna estructural: {column_height_threshold:.3f} "
          f"(celdas de planta: {len(unique_cells):,}, clasificadas como columna: {int(cell_is_column.sum()):,})")

    class_names = ["cubierta", "piso/base", "columna", "baranda/pared no estructural"]
    counts = {lbl: int(np.sum(labels == lbl)) for lbl in class_names}
    print("Conteo por clase:", counts)

    colors = {
        "cubierta": "#e74c3c",
        "piso/base": "#2980b9",
        "columna": "#27ae60",
        "baranda/pared no estructural": "#f1c40f",
    }

    fig, axes = plt.subplots(2, 2, figsize=(13, 12))

    # fila 1: color real (RGB) como referencia
    axes[0, 0].scatter(xyz[:, 0], xyz[:, 1], s=0.3, c=rgb / 255.0)
    axes[0, 0].set_title("Color real — planta (XY)", fontsize=10)
    axes[0, 0].set_aspect("equal", adjustable="datalim")

    axes[0, 1].scatter(xyz[:, 0], xyz[:, 2], s=0.3, c=rgb / 255.0)
    axes[0, 1].set_title("Color real — perfil (XZ)", fontsize=10)
    axes[0, 1].set_aspect("equal", adjustable="datalim")

    # fila 2: segmentacion
    for lbl, color in colors.items():
        m = labels == lbl
        axes[1, 0].scatter(xyz[m, 0], xyz[m, 1], s=0.3, alpha=0.6, color=color, label=f"{lbl} ({counts[lbl]:,})")
    axes[1, 0].set_title("Segmentación por normales — planta (XY)", fontsize=10)
    axes[1, 0].set_aspect("equal", adjustable="datalim")
    axes[1, 0].legend(markerscale=15, fontsize=8)

    for lbl, color in colors.items():
        m = labels == lbl
        axes[1, 1].scatter(xyz[m, 0], xyz[m, 2], s=0.3, alpha=0.6, color=color)
    axes[1, 1].set_title("Segmentación por normales — perfil (XZ)", fontsize=10)
    axes[1, 1].set_aspect("equal", adjustable="datalim")

    fig.suptitle("POC segmentación por normales — Templete Central, nube densa SfM (DJI)", fontsize=13)
    fig.tight_layout()
    out = OUT_DIR / "poc_segmentation_normals_densecloud.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"[OK] {out}")

    # export .ply coloreado por clase, para inspeccionar a mano en SuperSplat/CloudCompare/MeshLab
    class_rgb = {
        "cubierta": (231, 76, 60),
        "piso/base": (41, 128, 185),
        "columna": (39, 174, 96),
        "baranda/pared no estructural": (241, 196, 15),
    }
    seg_rgb = np.zeros((len(xyz), 3), dtype=np.uint8)
    for lbl, color in class_rgb.items():
        seg_rgb[labels == lbl] = color

    vertex = np.zeros(len(xyz), dtype=[
        ("x", "f4"), ("y", "f4"), ("z", "f4"),
        ("red", "u1"), ("green", "u1"), ("blue", "u1"),
    ])
    vertex["x"], vertex["y"], vertex["z"] = xyz[:, 0], xyz[:, 1], xyz[:, 2]
    vertex["red"], vertex["green"], vertex["blue"] = seg_rgb[:, 0], seg_rgb[:, 1], seg_rgb[:, 2]
    el = PlyElement.describe(vertex, "vertex")
    ply_out = OUT_DIR / "poc_segmentation_colored.ply"
    PlyData([el], text=False).write(str(ply_out))
    print(f"[OK] {ply_out} -- rojo=cubierta, azul=piso/base, verde=pared/columna")


if __name__ == "__main__":
    main()
