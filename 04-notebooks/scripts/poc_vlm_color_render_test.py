"""
Prueba ACOTADA: en vez de tocar la malla texturizada de RealityScan (4 GB,
demasiado pesada para esta maquina -- ver notas), se prueba primero algo
mucho mas barato: la nube de puntos que ya usamos (nube-densa.xyz) YA TIENE
color real por punto (columnas R,G,B), pero render_fragment_in_context()
en poc_segmentation_vlm.py lo descarta y pinta todo con un color plano
("#2c3e50" el fragmento, gris el contexto). Esta prueba solo cambia eso:
mismo pipeline, mismos fragmentos, pero con el color real del punto en vez
de plano, para ver si eso ya mueve la aguja antes de invertir en cargar/
renderizar la malla texturizada completa.

Sitio: Templete Central (dji). Fragmentos elegidos del log.json ya
existente (00-auditoria/poc-segmentacion-vlm/templete-central-dji/log.json):
  - 0, 2, 4: origen "columna" (columnas reales, ~2.2m), el VLM dijo RAILING
    (mal) en la corrida anterior con color plano.
  - 8, 11: origen "baranda", el VLM dijo RAILING (bien) antes -- se incluyen
    como control, para confirmar que el cambio de color no rompe lo que ya
    andaba bien.
"""
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import requests
import shutil

sys.path.insert(0, r"C:\nerfstudio_work\thesis\04-notebooks\scripts")
from poc_segmentation_multi_site import (  # noqa: E402
    SITES, estimate_normals, level, load_xyz_text, segment,
)
from poc_segmentation_vlm import (  # noqa: E402
    CLUSTER_RADIUS, MAX_RENDER_POINTS, MIN_CLUSTER_POINTS, QUESTION,
    _set_equal_bounds, cluster_points,
)

COMFY_URL = "http://localhost:8000"
COMFY_INPUT_DIR = Path(r"C:\Users\mboth\Documents\ComfyUI\input")
OUT_DIR = Path(__file__).parent / "color_render_test"
OUT_DIR.mkdir(exist_ok=True)

TARGET_FRAG_INDICES = [0, 2, 4, 8, 11]  # dentro de frag_specs, mismo orden que la corrida original


def render_fragment_colored(xyz_context, rgb_context, xyz_frag, rgb_frag, out_path):
    if len(xyz_context) > MAX_RENDER_POINTS:
        idx = np.random.default_rng(0).choice(len(xyz_context), MAX_RENDER_POINTS, replace=False)
        xyz_context, rgb_context = xyz_context[idx], rgb_context[idx]

    fig = plt.figure(figsize=(8, 4), dpi=100)
    fig.patch.set_facecolor("white")

    ax1 = fig.add_subplot(1, 2, 1, projection="3d")
    ax1.scatter(xyz_frag[:, 0], xyz_frag[:, 1], xyz_frag[:, 2], s=6, c=rgb_frag / 255.0)
    _set_equal_bounds(ax1, xyz_frag)
    ax1.view_init(elev=15, azim=45)
    ax1.set_axis_off()
    ax1.set_title("Fragmento aislado (color real, proporciones reales)", fontsize=8)

    ax2 = fig.add_subplot(1, 2, 2, projection="3d")
    ax2.scatter(xyz_context[:, 0], xyz_context[:, 1], xyz_context[:, 2], s=1.5, c=rgb_context / 255.0, alpha=0.6)
    ax2.scatter(xyz_frag[:, 0], xyz_frag[:, 1], xyz_frag[:, 2], s=5, c="#e60000")
    _set_equal_bounds(ax2, xyz_context)
    ax2.view_init(elev=20, azim=45)
    ax2.set_axis_off()
    ax2.set_title("Contexto (edificio completo, fragmento en rojo)", fontsize=8)

    fig.tight_layout(pad=0.5)
    fig.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def classify_via_comfyui(image_path):
    comfy_name = f"colortest_{image_path.stem}.png"
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
    for _ in range(60):
        time.sleep(2)
        h = requests.get(f"{COMFY_URL}/history/{prompt_id}", timeout=15).json()
        if prompt_id in h and h[prompt_id]["status"]["completed"]:
            return h[prompt_id]["outputs"]["2"]["text"][0]
    raise TimeoutError(f"ComfyUI no completo para {image_path.name}")


def main():
    site = [s for s in SITES if s["id"] == "templete-central-dji"][0]
    print(f"Cargando {site['label']}...")
    xyz, rgb, normals = load_xyz_text(site["path"], site["sample_every_n"])
    print(f"  Puntos: {len(xyz):,}")

    xyz_l, normals_l = level(xyz, normals, None)
    if normals_l is None:
        normals_l = estimate_normals(xyz_l)
    labels = segment(xyz_l, normals_l, None)
    context_xyz, context_rgb = xyz_l, rgb

    frag_specs = []
    for source_label in ("columna", "baranda/pared no estructural"):
        label_idx = np.where(labels == source_label)[0]
        if len(label_idx) == 0:
            continue
        cluster_id = cluster_points(xyz_l[label_idx])
        counts = np.bincount(cluster_id)
        for c in np.where(counts >= MIN_CLUSTER_POINTS)[0]:
            frag_local_idx = np.where(cluster_id == c)[0]
            frag_specs.append((source_label, label_idx[frag_local_idx]))
    print(f"  Total fragmentos disponibles: {len(frag_specs)} (se prueban {len(TARGET_FRAG_INDICES)})")

    results = []
    for i in TARGET_FRAG_INDICES:
        source_label, frag_global_idx = frag_specs[i]
        frag_xyz = xyz_l[frag_global_idx]
        frag_rgb = rgb[frag_global_idx]

        img_path = OUT_DIR / f"frag_{i:04d}_{source_label.split('/')[0]}_color.png"
        render_fragment_colored(context_xyz, context_rgb, frag_xyz, frag_rgb, img_path)

        try:
            answer = classify_via_comfyui(img_path)
        except Exception as e:
            print(f"  [{i}] ERROR: {e}")
            continue

        answer_norm = answer.strip().upper()
        expected = "COLUMN" if source_label == "columna" else "RAILING"
        hit = expected in answer_norm
        print(f"  [{i}] origen={source_label}: VLM={answer_norm} (esperado {expected}) -> {'OK' if hit else 'MISS'}")
        results.append({"frag": i, "source_label": source_label, "vlm_answer": answer, "expected": expected, "hit": hit})

    n_hits = sum(r["hit"] for r in results)
    print(f"\nResultado: {n_hits}/{len(results)} aciertos con color real (vs. la corrida anterior con color plano, ver log.json)")
    import json
    (OUT_DIR / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
