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
    "This image shows an isolated fragment of a 3D point cloud scan of a "
    "heritage building, viewed from an angle. Based ONLY on its overall "
    "shape and proportions -- tall and slender extending mostly vertically "
    "like a supporting post or pillar, versus short and elongated "
    "horizontally like a railing, parapet or low wall -- classify this "
    "fragment. Answer with exactly one word: COLUMN or RAILING."
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


def render_fragment(xyz_frag, out_path):
    if len(xyz_frag) > MAX_RENDER_POINTS:
        idx = np.random.default_rng(0).choice(len(xyz_frag), MAX_RENDER_POINTS, replace=False)
        xyz_frag = xyz_frag[idx]

    fig = plt.figure(figsize=(4, 4), dpi=100)
    ax = fig.add_subplot(projection="3d")
    ax.scatter(xyz_frag[:, 0], xyz_frag[:, 1], xyz_frag[:, 2], s=3, c="#2c3e50")
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    # proporciones reales (sin esto matplotlib estira cada eje para llenar
    # el cuadro, y la senal alto/ancho -- la que decide columna vs baranda --
    # se pierde)
    ranges = xyz_frag.max(axis=0) - xyz_frag.min(axis=0)
    max_range = ranges.max() / 2
    mid = (xyz_frag.max(axis=0) + xyz_frag.min(axis=0)) / 2
    ax.set_xlim(mid[0] - max_range, mid[0] + max_range)
    ax.set_ylim(mid[1] - max_range, mid[1] + max_range)
    ax.set_zlim(mid[2] - max_range, mid[2] + max_range)

    ax.view_init(elev=15, azim=45)
    ax.set_axis_off()
    fig.tight_layout(pad=0)
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

    cluster_id = cluster_points(xyz_l[wall_idx])
    n_clusters = cluster_id.max() + 1
    print(f"  Fragmentos conectados detectados: {n_clusters}")

    new_labels = labels.copy()
    site_render_dir = RENDERS_DIR / site["id"]
    site_render_dir.mkdir(parents=True, exist_ok=True)
    log = []

    counts = np.bincount(cluster_id)
    big_clusters = np.where(counts >= MIN_CLUSTER_POINTS)[0]
    print(f"  Fragmentos con >= {MIN_CLUSTER_POINTS} puntos (se consultan al VLM): {len(big_clusters)}")

    for i, c in enumerate(big_clusters):
        frag_local_idx = np.where(cluster_id == c)[0]
        frag_global_idx = wall_idx[frag_local_idx]
        frag_xyz = xyz_l[frag_global_idx]

        img_path = site_render_dir / f"frag_{c:04d}.png"
        render_fragment(frag_xyz, img_path)

        try:
            answer = classify_via_comfyui(img_path)
        except Exception as e:
            print(f"    [{i+1}/{len(big_clusters)}] fragmento {c}: ERROR ({e}), se deja la clasificacion geometrica")
            continue

        answer_norm = answer.strip().upper()
        if "COLUMN" in answer_norm:
            new_labels[frag_global_idx] = "columna"
        elif "RAILING" in answer_norm:
            new_labels[frag_global_idx] = "baranda/pared no estructural"
        else:
            answer_norm = f"AMBIGUO({answer_norm})"

        old_lbl = labels[frag_global_idx[0]]
        new_lbl = new_labels[frag_global_idx[0]]
        changed = " <-- CAMBIO" if old_lbl != new_lbl else ""
        print(f"    [{i+1}/{len(big_clusters)}] fragmento {c} ({len(frag_xyz)} pts, altura {np.ptp(frag_xyz[:, 2]):.2f}m): "
              f"VLM={answer_norm} -> {new_lbl}{changed}")
        log.append({
            "cluster": int(c), "n_points": int(len(frag_xyz)),
            "height_m": float(np.ptp(frag_xyz[:, 2])),
            "vlm_answer": answer, "geometric_label": old_lbl, "final_label": new_lbl,
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
