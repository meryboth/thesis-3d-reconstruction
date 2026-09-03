"""
POC: segmentacion asistida por un modelo de vision (Moondream2, via un nodo
de ComfyUI expuesto por su API HTTP) para refinar la distincion columna
estructural vs. baranda/pared no estructural de poc_segmentation_multi_site.py
-- ahi esa distincion se resuelve con un umbral geometrico fijo (altura
maxima de la celda, COLUMN_HEIGHT_FRAC), esta POC prueba si un VLM liviano,
mirando la forma de cada fragmento, puede tomar la misma decision con
evidencia visual en vez de un umbral fijo.

Pipeline:
  1. Corre la MISMA segmentacion geometrica (nivelado, normales, bandas de
     altura) que poc_segmentation_multi_site.py -- reusa sus funciones.
  2. Junta los puntos clasificados como pared (columna + baranda, sin
     distinguir todavia) y los agrupa en fragmentos discretos conectados
     espacialmente (una columna real, o un tramo de baranda, deberian caer
     cada uno en su propio fragmento).
  3. Por cada fragmento con suficientes puntos, renderiza una vista 3D del
     fragmento aislado (proporciones reales, sin deformar alto/ancho -- es
     la senal visual que separa columna de baranda) y se la manda a
     Moondream2 a traves de la API de ComfyUI (nodo MoondreamClassifyThesis),
     pidiendole que elija entre COLUMN y RAILING.
  4. Recolorea cada fragmento segun la respuesta del modelo. Los fragmentos
     chicos (ruido) y los puntos de cubierta/piso quedan con la clasificacion
     geometrica original, sin pasar por el VLM.
  5. Exporta un .ply nuevo (sufijo -vlm) al lado del geometrico, para
     comparar los dos en el mismo visor web.

ComfyUI tiene que estar corriendo (puerto 8000, ver moondream_infer.py y
custom_nodes/comfyui-thesis-moondream/ para el detalle de por que la
inferencia corre en un venv aislado).
"""
import json
import shutil
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import requests
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).parent))
from poc_segmentation_multi_site import (  # noqa: E402
    CLASS_RGB, SITES, detect_vegetation, estimate_normals, level, load_ply,
    load_xyz_text, segment,
)

THESIS_ROOT = Path(r"C:\nerfstudio_work\thesis")
WEB_DIR = THESIS_ROOT / "06-sitio-web" / "public" / "segmentacion"
RENDERS_DIR = THESIS_ROOT / "00-auditoria" / "poc-segmentacion-vlm"
RENDERS_DIR.mkdir(parents=True, exist_ok=True)

COMFY_URL = "http://localhost:8000"
COMFY_INPUT_DIR = Path(r"C:\Users\mboth\Documents\ComfyUI\input")

CLUSTER_RADIUS = 0.8       # unidades de la nube, ~2x CELL_SIZE del script geometrico
MIN_CLUSTER_POINTS = 150   # fragmentos mas chicos que esto se consideran ruido
MAX_RENDER_POINTS = 8000   # sample para que el render no tarde en fragmentos grandes

QUESTION = (
    "This image has two panels of the same 3D point-cloud fragment from an "
    "architectural heritage building. The LEFT panel shows the fragment "
    "isolated and zoomed in, with its true height-to-width proportions -- "
    "use this panel to judge its shape. The RIGHT panel shows the same "
    "fragment (in red) in context within the full gray building, just to "
    "show where it sits. Based on the LEFT panel's proportions -- tall and "
    "slender extending mostly vertically like a supporting post or pillar, "
    "versus short and elongated mostly horizontally like a railing, "
    "parapet or low wall -- classify this fragment. Answer with exactly "
    "one word: COLUMN or RAILING."
)


def cluster_points(xyz, radius=CLUSTER_RADIUS):
    """Componentes conexas via grilla de vecindad (mismo criterio de radio
    que el CELL_SIZE geometrico, pero en continuo -- no atado a la grilla de
    celdas cuadradas del script original)."""
    n = len(xyz)
    tree = cKDTree(xyz)
    pairs = tree.query_pairs(r=radius, output_type="ndarray")

    parent = np.arange(n)

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for a, b in pairs:
        union(a, b)

    roots = np.array([find(i) for i in range(n)])
    _, cluster_id = np.unique(roots, return_inverse=True)
    return cluster_id


def _scatter_leveled(ax, xyz, s, c, alpha=1.0):
    ax.scatter(xyz[:, 0], xyz[:, 1], xyz[:, 2], s=s, c=c, alpha=alpha)


def _set_equal_bounds(ax, xyz):
    ranges = xyz.max(axis=0) - xyz.min(axis=0)
    max_range = ranges.max() / 2
    mid = (xyz.max(axis=0) + xyz.min(axis=0)) / 2
    ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
    ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
    ax.set_zlim(mid[2] - max_range, mid[2] + max_range)


def render_fragment_in_context(xyz_context, xyz_frag, out_path):
    """Dos paneles en una sola imagen: izquierda = fragmento aislado, con
    sus propias proporciones reales (alto vs. ancho -- la senal que decide
    columna vs. baranda; se pierde si se lo ve a la escala del edificio
    completo). Derecha = edificio completo en gris con el fragmento
    resaltado en rojo, para dar contexto de que es un elemento arquitectonico
    y donde esta ubicado."""
    if len(xyz_context) > MAX_RENDER_POINTS:
        idx = np.random.default_rng(0).choice(len(xyz_context), MAX_RENDER_POINTS, replace=False)
        xyz_context = xyz_context[idx]

    fig = plt.figure(figsize=(8, 4), dpi=100)
    fig.patch.set_facecolor("white")

    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    _scatter_leveled(ax1, xyz_frag, s=4, c="#2c3e50")
    _set_equal_bounds(ax1, xyz_frag)
    ax1.view_init(elev=15, azim=45)
    ax1.set_axis_off()
    ax1.set_title("Fragmento aislado (proporciones reales)", fontsize=8)

    ax2 = fig.add_subplot(1, 2, 2, projection="3d")
    _scatter_leveled(ax2, xyz_context, s=1.5, c="#c8c8c8", alpha=0.5)
    _scatter_leveled(ax2, xyz_frag, s=5, c="#e60000")
    _set_equal_bounds(ax2, xyz_context)
    ax2.view_init(elev=20, azim=45)
    ax2.set_axis_off()
    ax2.set_title("Contexto (edificio completo, fragmento en rojo)", fontsize=8)

    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def classify_via_comfyui(image_path):
    comfy_name = f"vlmpoc_{image_path.stem}.png"
    shutil.copy2(image_path, COMFY_INPUT_DIR / comfy_name)

    workflow = {
        "prompt": {
            "1": {"class_type": "LoadImage", "inputs": {"image": comfy_name}},
            "2": {
                "class_type": "MoondreamClassifyThesis",
                "inputs": {"image": ["1", 0], "question": QUESTION},
            },
        }
    }
    r = requests.post(f"{COMFY_URL}/prompt", json=workflow, timeout=15)
    r.raise_for_status()
    prompt_id = r.json()["prompt_id"]

    for _ in range(60):  # hasta 2 minutos (carga del modelo en cada llamada)
        time.sleep(2)
        h = requests.get(f"{COMFY_URL}/history/{prompt_id}", timeout=15).json()
        if prompt_id in h and h[prompt_id]["status"]["completed"]:
            answer = h[prompt_id]["outputs"]["2"]["text"][0]
            return answer
    raise TimeoutError(f"ComfyUI no completo la clasificacion para {image_path.name}")


def run_site(site):
    print(f"\n=== {site['label']} ===")
    if site["format"] == "xyz_text":
        xyz, rgb, normals = load_xyz_text(site["path"], site["sample_every_n"])
    else:
        xyz, rgb, normals = load_ply(site["path"])
    print(f"  Puntos: {len(xyz):,}")

    veg_mask = detect_vegetation(rgb, exg_max=site["exg_max"]) if "exg_max" in site else np.zeros(len(xyz), dtype=bool)
    xyz_l, normals_l = level(xyz, normals, veg_mask)
    if normals_l is None:
        normals_l = estimate_normals(xyz_l)
    labels = segment(xyz_l, normals_l, veg_mask)

    keep = ~veg_mask
    xyz_l, labels = xyz_l[keep], labels[keep]

    wall_mask = (labels == "columna") | (labels == "baranda/pared no estructural")
    wall_idx = np.where(wall_mask)[0]
    print(f"  Puntos de pared/columna a reclasificar: {len(wall_idx):,}")

    # el contexto para el render es toda la estructura (sin vegetacion, ya
    # excluida arriba) -- no solo los puntos de pared -- para que el modelo
    # vea que es un edificio completo, no una nube de puntos abstracta.
    context_xyz = xyz_l

    new_labels = labels.copy()
    site_render_dir = RENDERS_DIR / site["id"]
    site_render_dir.mkdir(parents=True, exist_ok=True)
    log = []

    # se agrupa por separado dentro de cada etiqueta geometrica (columna /
    # baranda) en vez de sobre todos los puntos de pared juntos -- una
    # columna real siempre toca fisicamente la baranda en su base (estan
    # soldadas/coladas juntas en la obra real), asi que agrupar por
    # conectividad espacial pura las fusiona en un solo fragmento mixto
    # (ver hallazgo de la corrida anterior, fragmento con 42mil puntos).
    # Separar primero por la etiqueta geometrica evita esa fusion y le manda
    # al VLM un fragmento "puro" de un solo tipo para validar o corregir.
    frag_specs = []  # (label_de_origen, frag_global_idx)
    for source_label in ("columna", "baranda/pared no estructural"):
        label_idx = np.where(labels == source_label)[0]
        if len(label_idx) == 0:
            continue
        cluster_id = cluster_points(xyz_l[label_idx])
        counts = np.bincount(cluster_id)
        for c in np.where(counts >= MIN_CLUSTER_POINTS)[0]:
            frag_local_idx = np.where(cluster_id == c)[0]
            frag_specs.append((source_label, label_idx[frag_local_idx]))

    print(f"  Fragmentos puros (>= {MIN_CLUSTER_POINTS} puntos, separados por etiqueta de origen) a consultar: {len(frag_specs)}")

    for i, (source_label, frag_global_idx) in enumerate(frag_specs):
        frag_xyz = xyz_l[frag_global_idx]

        img_path = site_render_dir / f"frag_{i:04d}_{source_label.split('/')[0]}.png"
        render_fragment_in_context(context_xyz, frag_xyz, img_path)

        try:
            answer = classify_via_comfyui(img_path)
        except Exception as e:
            print(f"    [{i+1}/{len(frag_specs)}] fragmento ({source_label}): ERROR ({e}), se deja la clasificacion geometrica")
            continue

        answer_norm = answer.strip().upper()
        if "COLUMN" in answer_norm:
            new_labels[frag_global_idx] = "columna"
        elif "RAILING" in answer_norm:
            new_labels[frag_global_idx] = "baranda/pared no estructural"
        else:
            answer_norm = f"AMBIGUO({answer_norm})"

        new_lbl = new_labels[frag_global_idx[0]]
        changed = " <-- CAMBIO" if source_label != new_lbl else ""
        print(f"    [{i+1}/{len(frag_specs)}] origen={source_label} ({len(frag_xyz)} pts, altura {np.ptp(frag_xyz[:, 2]):.2f}m): "
              f"VLM={answer_norm} -> {new_lbl}{changed}")
        log.append({
            "n_points": int(len(frag_xyz)),
            "height_m": float(np.ptp(frag_xyz[:, 2])),
            "vlm_answer": answer, "geometric_label": source_label, "final_label": new_lbl,
        })

    n_changed = int(np.sum(new_labels[wall_idx] != labels[wall_idx]))
    print(f"  Puntos reclasificados por el VLM (distinto de la etiqueta geometrica): {n_changed:,} de {len(wall_idx):,}")

    from poc_segmentation_multi_site import export_colored_ply
    out_path = WEB_DIR / f"{site['id']}-vlm.ply"
    export_colored_ply(xyz_l, new_labels, out_path)
    print(f"  [OK] {out_path}")

    log_path = site_render_dir / "log.json"
    log_path.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  [OK] {log_path}")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default="templete-central-dji", help="id del sitio (ver SITES en poc_segmentation_multi_site.py), o 'all'")
    args = ap.parse_args()

    targets = SITES if args.site == "all" else [s for s in SITES if s["id"] == args.site]
    if not targets:
        print(f"Sitio desconocido: {args.site}. Opciones: {[s['id'] for s in SITES]}")
        return
    for site in targets:
        run_site(site)


if __name__ == "__main__":
    main()
