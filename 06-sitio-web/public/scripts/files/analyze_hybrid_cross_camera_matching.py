"""
Calidad de matching cruzado entre dispositivos en el dataset hibrido
DJI + Insta360 del Templete Central (H4).

Lee directamente la base de datos de COLMAP (database.db) generada por el
matcher exhaustivo de una corrida nativa de COLMAP sobre el dataset
hibrido (794 imagenes: 487 DJI + 307 Insta360), y compara la fuerza de
los matches geometricamente verificados (inliers tras RANSAC) segun si
el par de imagenes es DJI-DJI, Insta360-Insta360, o cruzado (DJI-Insta360).

No depende de si el proceso de mapping (incremental SfM) llego a
completarse o no -- el matching es una etapa anterior e independiente.
"""
import sqlite3
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DB = r"C:\nerfstudio_work\thesis\02-templete-central\01-experimentos\hybrid-dji-insta360-colmap\run-20260825-183608\colmap\database.db"
OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\hybrid-cross-camera-matching")
OUT_DIR.mkdir(parents=True, exist_ok=True)

DJI_MAX_FRAME = 487  # frame_000001..frame_000487 = DJI; frame_000488..frame_000794 = Insta360


def frame_num(name):
    return int(name.replace("frame_", "").replace(".jpg", ""))


def pair_id_to_image_ids(pair_id, max_image_id=2147483647):
    image_id2 = pair_id % max_image_id
    image_id1 = (pair_id - image_id2) // max_image_id
    return image_id1, image_id2


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("SELECT image_id, name FROM images")
    id_to_name = {r[0]: r[1] for r in cur.fetchall()}

    def is_dji(image_id):
        return frame_num(id_to_name[image_id]) <= DJI_MAX_FRAME

    cur.execute("SELECT pair_id, rows FROM two_view_geometries")
    pairs = cur.fetchall()
    con.close()

    buckets = {"DJI-DJI": [], "Insta360-Insta360": [], "DJI-Insta360": []}
    for pair_id, inliers in pairs:
        id1, id2 = pair_id_to_image_ids(pair_id)
        if id1 not in id_to_name or id2 not in id_to_name:
            continue
        d1, d2 = is_dji(id1), is_dji(id2)
        key = "DJI-DJI" if (d1 and d2) else ("Insta360-Insta360" if (not d1 and not d2) else "DJI-Insta360")
        buckets[key].append(inliers)

    summary = {}
    for k, v in buckets.items():
        v = np.array(v)
        nonzero = v[v > 0]
        summary[k] = {
            "total_pairs_attempted": int(len(v)),
            "pairs_with_any_match": int(len(nonzero)),
            "pairs_with_any_match_pct": round(len(nonzero) / len(v) * 100, 2) if len(v) else 0,
            "matched_pairs_mean_inliers": round(float(nonzero.mean()), 1) if len(nonzero) else 0,
            "matched_pairs_median_inliers": round(float(np.median(nonzero)), 1) if len(nonzero) else 0,
            "matched_pairs_p90_inliers": round(float(np.percentile(nonzero, 90)), 1) if len(nonzero) else 0,
            "matched_pairs_max_inliers": int(nonzero.max()) if len(nonzero) else 0,
            "pairs_with_inliers_gte_200": int((v >= 200).sum()),
            "pairs_with_inliers_gte_200_pct": round(float((v >= 200).sum()) / len(v) * 100, 2) if len(v) else 0,
        }

    meta = {
        "case": "02-templete-central",
        "artifact": "hybrid-cross-camera-matching",
        "source_database": DB,
        "dataset": "dataset-clean (794 img = 487 DJI + 307 Insta360), run-20260825-183608",
        "important_note": (
            "Se analiza la etapa de matching (two_view_geometries), independiente de si el "
            "incremental mapper llego a completar la reconstruccion. 'inliers' = correspondencias "
            "geometricamente verificadas (post-RANSAC) por par de imagenes."
        ),
        "summary": summary,
    }
    (OUT_DIR / "hybrid-cross-camera-matching-metadata.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    with open(OUT_DIR / "hybrid-cross-camera-matching.log", "w", encoding="utf-8") as f:
        f.write("CALIDAD DE MATCHING CRUZADO ENTRE DISPOSITIVOS -- Templete Central (hibrido DJI+Insta360)\n")
        f.write("=" * 100 + "\n\n")
        f.write(f"{'Tipo de par':<20}{'pares intentados':>18}{'con match (>0)':>16}{'% con match':>14}"
                f"{'media inliers':>16}{'mediana':>10}{'p90':>8}{'max':>8}\n")
        f.write("-" * 100 + "\n")
        for k, s in summary.items():
            f.write(f"{k:<20}{s['total_pairs_attempted']:>18}{s['pairs_with_any_match']:>16}"
                     f"{s['pairs_with_any_match_pct']:>13.1f}%{s['matched_pairs_mean_inliers']:>16.1f}"
                     f"{s['matched_pairs_median_inliers']:>10.1f}{s['matched_pairs_p90_inliers']:>8.1f}"
                     f"{s['matched_pairs_max_inliers']:>8}\n")
        f.write("\nNOTA: 'con match' cuenta pares con al menos 1 inlier geometrico verificado.\n")
        f.write("Fuente: database.db de la corrida run-20260825-183608 (COLMAP exhaustive_matcher).\n")

    # chart
    labels = list(summary.keys())
    means = [summary[k]["matched_pairs_mean_inliers"] for k in labels]
    maxes = [summary[k]["matched_pairs_max_inliers"] for k in labels]

    fig, ax = plt.subplots(figsize=(8, 6))
    x = np.arange(len(labels))
    w = 0.35
    ax.bar(x - w / 2, means, w, label="Inliers promedio (pares con match)", color="#2c5282")
    ax.bar(x + w / 2, maxes, w, label="Inliers maximo", color="#9467bd")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Inliers geometricamente verificados")
    ax.set_title("Calidad de matching por tipo de par -- Templete Central (hibrido DJI+Insta360)")
    ax.legend()
    ax.grid(True, alpha=0.3, axis="y")
    for i, (m, mx) in enumerate(zip(means, maxes)):
        ax.annotate(f"{m:.0f}", (i - w / 2, m), textcoords="offset points", xytext=(0, 4), ha="center", fontsize=9)
        ax.annotate(f"{mx:.0f}", (i + w / 2, mx), textcoords="offset points", xytext=(0, 4), ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "hybrid-cross-camera-matching-chart.png", dpi=150)

    print("Guardado en:", OUT_DIR)
    for k, s in summary.items():
        print(k, s)


if __name__ == "__main__":
    main()
