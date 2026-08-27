"""
Analiza cada splat.ply (export de Gaussian Splatting / Splatfacto) presente en
thesis/0X-*/02-resultados-finales/.

Replica en Python local (sin pandas/matplotlib, solo numpy+scipy+plyfile) la
logica del notebook "Analisis del GaussianSplat.ipynb" (originalmente corrido
en Colab contra el splat.ply de Paraguas), generalizada para descubrir y
analizar automaticamente TODOS los exports de los 3 casos de estudio (DJI e
Insta360 donde corresponda).

Metricas: cantidad de gaussianas, propiedades detectadas, bounding box,
centroide, opacidad (con deteccion de logit-space), escala (con deteccion de
log-space), distancia a gaussianas vecinas mas cercanas (muestreada). Si existe
un log de exportacion (05_export_gaussian_splat_ply.log / *export*gaussian*.log)
en los logs del caso, intenta extraer cantidad de gaussianas exportadas/
descartadas para cruzar contra lo ya reportado en 00-resumen/.

No modifica ningun archivo de entrada. Escribe, junto a cada splat.ply:
  gaussian-splat-metadata.json
  gaussian-splat-metrics.log
"""

from pathlib import Path
import json
import re
from datetime import datetime

import numpy as np
from scipy.spatial import cKDTree
from plyfile import PlyData

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(r"C:\nerfstudio_work\thesis")

NN_SAMPLE_POINTS = 50_000
RANDOM_SEED = 42


def find_splats(root):
    return sorted(root.glob("0*/02-resultados-finales/**/splatfacto/export/splat.ply"))


def case_and_method_label(root, splat_path):
    rel = splat_path.relative_to(root)
    parts = rel.parts
    case = parts[0]
    # 0X-caso/02-resultados-finales/[dji|insta360]/splatfacto/export/splat.ply
    # o 0X-caso/02-resultados-finales/splatfacto/export/splat.ply (paraguas)
    method_parts = parts[2:-3]
    method_label = "/".join(method_parts) if method_parts else "default"
    return case, method_label


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def first_existing(names, candidates):
    for c in candidates:
        if c in names:
            return c
    return None


# NOTA: se intento cruzar cada splat.ply contra su log de exportacion
# (05_export_gaussian_splat_ply.log / 10_export_gaussian_splat_ply.log) para
# extraer gaussianas exportadas/descartadas por regex, pero en sitios con DJI
# e Insta360 los logs numerados en 01-logs/ no distinguen de forma confiable
# a que metodo de captura pertenece cada uno (la numeracion se reutiliza entre
# pipelines). Un match por nombre genérico terminó cruzando datos de un método
# con el splat.ply del otro. Se descarto ese cruce automatico: los conteos de
# gaussianas exportadas/descartadas ya estan documentados a mano en cada
# 00-resumen/experiment-summary*.txt, verificados contra el .ply (coinciden).


def analyze_splat(path):
    ply = PlyData.read(str(path))
    vertex = ply["vertex"].data
    prop_names = list(vertex.dtype.names)

    gaussian_count = len(vertex)
    file_size = path.stat().st_size

    pos_cols = [c for c in ["x", "y", "z"] if c in prop_names]
    if len(pos_cols) != 3:
        raise ValueError(f"No se detectaron columnas x/y/z: {prop_names}")

    opacity_col = first_existing(prop_names, ["opacity", "alpha", "opacity_0"])
    scale_cols = sorted([c for c in prop_names if re.fullmatch(r"scale[_-]?\d+", c)])
    rot_cols = sorted([
        c for c in prop_names
        if re.fullmatch(r"rot[_-]?\d+", c) or "quat" in c.lower()
    ])
    color_cols = [c for c in prop_names if c in ["red", "green", "blue", "r", "g", "b"]]
    sh_cols = [c for c in prop_names if c.startswith("f_dc_") or c.startswith("f_rest_")]

    xyz = np.column_stack([vertex[c] for c in pos_cols]).astype(np.float64)
    mins = xyz.min(axis=0)
    maxs = xyz.max(axis=0)
    centroid = xyz.mean(axis=0)
    extents = maxs - mins
    bbox_volume = float(np.prod(extents))

    opacity_metrics = None
    if opacity_col is not None:
        opacity_raw = np.asarray(vertex[opacity_col], dtype=np.float64)
        raw_min, raw_max = float(np.min(opacity_raw)), float(np.max(opacity_raw))

        if raw_min < 0 or raw_max > 1:
            alpha = sigmoid(opacity_raw)
            opacity_mode = "logit_detected__sigmoid_applied"
        else:
            alpha = opacity_raw
            opacity_mode = "already_in_0_1"

        opacity_metrics = {
            "column": opacity_col,
            "mode": opacity_mode,
            "raw_min": raw_min,
            "raw_max": raw_max,
            "alpha_mean": float(np.mean(alpha)),
            "alpha_median": float(np.median(alpha)),
            "alpha_std": float(np.std(alpha)),
            "alpha_p05": float(np.percentile(alpha, 5)),
            "alpha_p95": float(np.percentile(alpha, 95)),
            "alpha_below_0_05": int(np.sum(alpha < 0.05)),
            "alpha_below_0_10": int(np.sum(alpha < 0.10)),
            "alpha_above_0_50": int(np.sum(alpha > 0.50)),
        }

    scale_metrics = None
    if scale_cols:
        scale_raw = np.column_stack([vertex[c] for c in scale_cols]).astype(np.float64)
        scale_exp = np.exp(scale_raw)

        scale_metrics = [
            {
                "column": c,
                "raw_mean": float(np.mean(scale_raw[:, i])),
                "raw_std": float(np.std(scale_raw[:, i])),
                "exp_mean": float(np.mean(scale_exp[:, i])),
                "exp_median": float(np.median(scale_exp[:, i])),
                "exp_p95": float(np.percentile(scale_exp[:, i], 95)),
            }
            for i, c in enumerate(scale_cols)
        ]

    rng = np.random.default_rng(RANDOM_SEED)
    sample_n = min(NN_SAMPLE_POINTS, gaussian_count)
    idx = rng.choice(gaussian_count, size=sample_n, replace=False)
    xyz_sample = xyz[idx]

    nn_metrics = None
    if len(xyz_sample) >= 2:
        tree = cKDTree(xyz_sample)
        dists, _ = tree.query(xyz_sample, k=2, workers=-1)
        nn = dists[:, 1]

        nn_metrics = {
            "sample_size": int(len(xyz_sample)),
            "mean": float(np.mean(nn)),
            "median": float(np.median(nn)),
            "std": float(np.std(nn)),
            "p05": float(np.percentile(nn, 5)),
            "p95": float(np.percentile(nn, 95)),
        }

    raw = {
        "alpha": alpha if opacity_col is not None else None,
        "scale_exp": scale_exp if scale_cols else None,
        "scale_cols": scale_cols,
        "xyz_sample": xyz_sample,
    }

    metadata = {
        "artifact": "gaussian-splat",
        "source": "nerfstudio splatfacto export (splat.ply)",
        "generated_analysis_at": datetime.now().isoformat(),

        "file": {
            "path": str(path),
            "size_bytes": file_size,
            "size_mb": file_size / (1024 ** 2),
        },

        "gaussian_count": int(gaussian_count),
        "property_names": prop_names,

        "detected_attributes": {
            "position": pos_cols,
            "opacity": opacity_col,
            "scale": scale_cols,
            "rotation": rot_cols,
            "rgb": color_cols,
            "spherical_harmonics_count": len(sh_cols),
        },

        "geometry": {
            "bounding_box": {
                "min": mins.tolist(),
                "max": maxs.tolist(),
                "extent": extents.tolist(),
                "volume": bbox_volume,
            },
            "centroid": centroid.tolist(),
            "gaussians_per_bbox_unit": gaussian_count / bbox_volume if bbox_volume > 0 else None,
        },

        "opacity": opacity_metrics,
        "scale": scale_metrics,
        "nearest_neighbor_sample": nn_metrics,

        "important_note": (
            "Las metricas de opacidad y escala aplican sigmoid()/exp() automaticamente "
            "cuando los valores crudos sugieren estar en logit/log-space (convencion "
            "habitual de los exporters de Gaussian Splatting). La distancia a vecinos "
            "mas cercanos se calculo sobre una muestra aleatoria reproducible, no sobre "
            "todas las gaussianas, para mantener acotado el uso de memoria."
        ),
    }

    return metadata, raw


def make_plots(path, metadata, raw):
    folder = path.parent
    saved = []

    if raw["alpha"] is not None:
        fig, ax = plt.subplots(figsize=(7, 4.5))
        ax.hist(raw["alpha"], bins=60, color="#2980b9")
        ax.set_xlabel("Opacidad estimada (alpha, 0-1)")
        ax.set_ylabel("Cantidad de gaussianas")
        ax.set_title(f"Distribucion de opacidad — {metadata['gaussian_count']:,} gaussianas")
        fig.tight_layout()
        out = folder / "gaussian-splat-opacity-histogram.png"
        fig.savefig(out, dpi=140)
        plt.close(fig)
        saved.append(out)

    if raw["scale_exp"] is not None:
        fig, ax = plt.subplots(figsize=(7, 4.5))
        for i, c in enumerate(raw["scale_cols"][:3]):
            ax.hist(raw["scale_exp"][:, i], bins=60, alpha=0.6, label=c)
        ax.set_xlabel("Escala estimada (exp(scale_raw))")
        ax.set_ylabel("Cantidad de gaussianas")
        ax.set_title("Distribucion de escalas estimadas")
        ax.legend()
        fig.tight_layout()
        out = folder / "gaussian-splat-scale-histogram.png"
        fig.savefig(out, dpi=140)
        plt.close(fig)
        saved.append(out)

    xyz_sample = raw["xyz_sample"]
    if xyz_sample is not None and len(xyz_sample) > 0:
        fig, axes = plt.subplots(1, 2, figsize=(11, 5))
        axes[0].scatter(xyz_sample[:, 0], xyz_sample[:, 1], s=0.15, alpha=0.4, color="#34495e")
        axes[0].set_xlabel("X")
        axes[0].set_ylabel("Y")
        axes[0].set_title("Distribucion espacial XY (muestra)")
        axes[0].set_aspect("equal", adjustable="datalim")

        axes[1].scatter(xyz_sample[:, 0], xyz_sample[:, 2], s=0.15, alpha=0.4, color="#34495e")
        axes[1].set_xlabel("X")
        axes[1].set_ylabel("Z")
        axes[1].set_title("Distribucion espacial XZ (muestra)")
        axes[1].set_aspect("equal", adjustable="datalim")

        fig.tight_layout()
        out = folder / "gaussian-splat-spatial-scatter.png"
        fig.savefig(out, dpi=140)
        plt.close(fig)
        saved.append(out)

    return saved


def write_outputs(path, metadata):
    folder = path.parent

    json_path = folder / "gaussian-splat-metadata.json"
    log_path = folder / "gaussian-splat-metrics.log"

    json_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    op = metadata.get("opacity") or {}
    sc = metadata.get("scale") or []
    nn = metadata.get("nearest_neighbor_sample") or {}
    bbox = metadata["geometry"]["bounding_box"]

    lines = [
        "GAUSSIAN SPLAT ANALYSIS",
        "=" * 70,
        "",
        f"File: {path}",
        f"Size MB: {metadata['file']['size_mb']:.3f}",
        f"Gaussian count: {metadata['gaussian_count']:,}",
        "",
        "DETECTED ATTRIBUTES",
        "--------------------",
        f"Position: {metadata['detected_attributes']['position']}",
        f"Opacity: {metadata['detected_attributes']['opacity']}",
        f"Scale: {metadata['detected_attributes']['scale']}",
        f"Rotation: {metadata['detected_attributes']['rotation']}",
        f"RGB: {metadata['detected_attributes']['rgb']}",
        f"Spherical harmonics columns: {metadata['detected_attributes']['spherical_harmonics_count']}",
        "",
        "BOUNDING BOX",
        "------------",
        f"Extent: {bbox['extent']}",
        f"Centroid: {metadata['geometry']['centroid']}",
        f"Gaussians per bbox unit: {metadata['geometry']['gaussians_per_bbox_unit']}",
        "",
    ]

    if op:
        lines += [
            "OPACITY",
            "-------",
            f"Mode: {op['mode']}",
            f"Alpha mean: {op['alpha_mean']:.6f}",
            f"Alpha median: {op['alpha_median']:.6f}",
            f"Alpha < 0.05: {op['alpha_below_0_05']:,}",
            f"Alpha < 0.10: {op['alpha_below_0_10']:,}",
            f"Alpha > 0.50: {op['alpha_above_0_50']:,}",
            "",
        ]

    if sc:
        lines += ["SCALE", "-----"]
        for row in sc:
            lines.append(
                f"{row['column']}: exp_mean={row['exp_mean']:.6f} exp_median={row['exp_median']:.6f} exp_p95={row['exp_p95']:.6f}"
            )
        lines.append("")

    if nn:
        lines += [
            "NEAREST NEIGHBOR (sample)",
            "--------------------------",
            f"Sample size: {nn['sample_size']:,}",
            f"NN mean: {nn['mean']:.6f}",
            f"NN median: {nn['median']:.6f}",
            "",
        ]

    lines += [
        "METHODOLOGICAL NOTE",
        "--------------------",
        metadata["important_note"],
    ]

    log_path.write_text("\n".join(lines), encoding="utf-8")

    return json_path, log_path


def main():
    splat_files = find_splats(ROOT)

    if not splat_files:
        print("No se encontraron splat.ply bajo */02-resultados-finales/")
        return

    print(f"splat.ply encontrados: {len(splat_files)}")

    for path in splat_files:
        case, method_label = case_and_method_label(ROOT, path)

        print()
        print("=" * 75)
        print(f"{case} :: {method_label}")
        print(path)
        print("=" * 75)

        try:
            metadata, raw = analyze_splat(path)
        except Exception as e:
            print(f"[ERROR] {case} :: {method_label}: {e}")
            continue

        json_path, log_path = write_outputs(path, metadata)
        plot_paths = make_plots(path, metadata, raw)

        print(f"[OK] Gaussianas: {metadata['gaussian_count']:,}")
        print(f"[OK] Log:  {log_path}")
        print(f"[OK] JSON: {json_path}")
        for p in plot_paths:
            print(f"[OK] PNG:  {p}")


if __name__ == "__main__":
    main()
