"""
Benchmark cuantitativo de fidelidad visual: compara, para cada metodo (Nerfacto,
Splatfacto) de cada sitio y captura, los frames renderizados contra su ground
truth (imagen original de esa misma pose de camara).

Replica el notebook "Benchmark de Frames de Renders.ipynb" (corrido originalmente
en Colab contra Paraguas), generalizado para los 3 sitios y ambos metodos de
captura (DJI / Insta360) donde corresponde.

A diferencia del notebook original (que emparejaba 3 carpetas sueltas
original/splatfacto/nerfacto por orden de archivo), este script usa los pares
gt-rgb/rgb que Nerfstudio ya genera pareados 1:1 por nombre de archivo dentro de
cada carpeta de render -- mas confiable que emparejar por orden.

Metricas: PSNR, SSIM, LPIPS (AlexNet), MSE, MAE, sobre una muestra aleatoria
reproducible de frames (no todos, para mantener el tiempo de corrida acotado en
CPU).

No modifica ningun archivo de entrada. Escribe, por cada render:
  thesis/0X-<caso>/02-resultados-finales/[dji|insta360]/<metodo>/render/render-benchmark-metadata.json
  thesis/0X-<caso>/02-resultados-finales/[dji|insta360]/<metodo>/render/render-benchmark-metrics.log

y un resumen comparativo por sitio en:
  thesis/0X-<caso>/02-resultados-finales/benchmark-comparison.log
"""

from pathlib import Path
import json
import re
from datetime import datetime

import numpy as np
from PIL import Image
from skimage.metrics import peak_signal_noise_ratio, structural_similarity

import torch
import lpips

THESIS = Path(r"C:\nerfstudio_work\thesis")
RAW = Path(r"C:\nerfstudio_work")

N_SAMPLES = 100
RANDOM_SEED = 42
RESIZE_TO = (960, 540)

RENDERS = {
    "01-paraguas-vicentelopez": {
        "nerfacto": {
            # NOTA: "renders/original_train_exact" estaba mal alineado (renombrado
            # secuencialmente 1..637, mientras nerfacto/train/rgb conserva la
            # numeracion original con huecos donde se saco frames para eval).
            # El ground truth correcto son las imagenes originales del dataset
            # (ns-data-drone/images), que comparten exactamente los mismos nombres
            # de archivo que nerfacto/train/rgb (637/637 coinciden, verificado).
            "gt": RAW / "paraguas-vicentelopez/ns-data-drone/images",
            "pred": RAW / "paraguas-vicentelopez/renders/nerfacto/train/rgb",
            "out": THESIS / "01-paraguas-vicentelopez/02-resultados-finales/nerfacto/renders",
        },
        "splatfacto": {
            "gt": RAW / "paraguas-vicentelopez/renders/splatfacto/train/gt-rgb",
            "pred": RAW / "paraguas-vicentelopez/renders/splatfacto/train/rgb",
            "out": THESIS / "01-paraguas-vicentelopez/02-resultados-finales/splatfacto/renders",
        },
    },

    "02-templete-central": {
        "dji/nerfacto": {
            # NOTA: el gt-rgb generado por el render de hoy quedo con un bug de
            # falso color (misma composicion, colores corruptos - verificado
            # visualmente). Se usa en su lugar el dataset fuente real
            # (ns-from-realityscan-nerf308/images), que comparte la misma
            # indexacion sparse (00000..01228, 308 archivos) que el render.
            "gt": RAW / "panteon-chacarita/templete-central/ns-from-realityscan-nerf308/images",
            "pred": RAW / "panteon-chacarita/templete-central/renders/nerf/templete-central-nerfacto-train/train/rgb",
            "out": THESIS / "02-templete-central/02-resultados-finales/dji/nerfacto/render",
        },
        "dji/splatfacto": {
            # Mismo bug de falso color en el gt-rgb de este render; se usa el
            # dataset fuente completo (ns-from-realityscan/images, 1232
            # archivos, indices 00000..01231) que coincide con el render (1109).
            "gt": RAW / "panteon-chacarita/templete-central/ns-from-realityscan/images",
            "pred": RAW / "panteon-chacarita/templete-central/renders-templete-splat-ds8/templete-splat-dataset-train.mp4/train/rgb",
            "out": THESIS / "02-templete-central/02-resultados-finales/dji/splatfacto/render",
        },
        "insta360/nerfacto": {
            "gt": RAW / "panteon-chacarita/templete-central/renders/templete-central-insta360-nerfacto-dataset-traj/train/gt-rgb",
            "pred": RAW / "panteon-chacarita/templete-central/renders/templete-central-insta360-nerfacto-dataset-traj/train/rgb",
            "out": THESIS / "02-templete-central/02-resultados-finales/insta360/nerfacto/render",
        },
        "insta360/splatfacto": {
            "gt": RAW / "panteon-chacarita/templete-central/renders/templete-central-insta360-splatfacto-dataset-traj/train/gt-rgb",
            "pred": RAW / "panteon-chacarita/templete-central/renders/templete-central-insta360-splatfacto-dataset-traj/train/rgb",
            "out": THESIS / "02-templete-central/02-resultados-finales/insta360/splatfacto/render",
        },
    },

    "03-panteon-asociacion-catalana": {
        "dji/nerfacto": {
            "gt": RAW / "panteon-chacarita/panteon-asociacion-catalana/renders/nerf/panteon-catalan-nerfacto-train/train/gt-rgb",
            "pred": RAW / "panteon-chacarita/panteon-asociacion-catalana/renders/nerf/panteon-catalan-nerfacto-train/train/rgb",
            "out": THESIS / "03-panteon-asociacion-catalana/02-resultados-finales/dji/nerfacto/render",
        },
        "dji/splatfacto": {
            "gt": RAW / "panteon-chacarita/panteon-asociacion-catalana/renders/splat/panteon-catalan-splat-ds8-train/train/gt-rgb",
            "pred": RAW / "panteon-chacarita/panteon-asociacion-catalana/renders/splat/panteon-catalan-splat-ds8-train/train/rgb",
            "out": THESIS / "03-panteon-asociacion-catalana/02-resultados-finales/dji/splatfacto/render",
        },
        "insta360/nerfacto": {
            "gt": RAW / "panteon-chacarita/panteon-asociacion-catalana/renders/panteon-catalana-insta360-nerfacto-dataset-traj/train/gt-rgb",
            "pred": RAW / "panteon-chacarita/panteon-asociacion-catalana/renders/panteon-catalana-insta360-nerfacto-dataset-traj/train/rgb",
            "out": THESIS / "03-panteon-asociacion-catalana/02-resultados-finales/insta360/nerfacto/render",
        },
        "insta360/splatfacto": {
            "gt": RAW / "panteon-chacarita/panteon-asociacion-catalana/renders/panteon-catalana-insta360-splatfacto-dataset-traj/train/gt-rgb",
            "pred": RAW / "panteon-chacarita/panteon-asociacion-catalana/renders/panteon-catalana-insta360-splatfacto-dataset-traj/train/rgb",
            "out": THESIS / "03-panteon-asociacion-catalana/02-resultados-finales/insta360/splatfacto/render",
        },
    },
}


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", str(s))]


def list_images(folder):
    exts = {".jpg", ".jpeg", ".png"}
    return sorted(
        (p for p in folder.iterdir() if p.suffix.lower() in exts),
        key=lambda p: natural_key(p.name)
    )


def load_rgb(path, resize_to):
    img = Image.open(path).convert("RGB")
    if resize_to is not None:
        img = img.resize(resize_to, Image.BICUBIC)
    return np.asarray(img).astype(np.float32) / 255.0


def to_lpips_tensor(img):
    t = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).float()
    return t * 2.0 - 1.0


def compute_pair_metrics(gt_path, pred_path, lpips_model):
    gt = load_rgb(gt_path, RESIZE_TO)
    pred = load_rgb(pred_path, RESIZE_TO)

    mse = float(np.mean((gt - pred) ** 2))
    mae = float(np.mean(np.abs(gt - pred)))
    psnr = float(peak_signal_noise_ratio(gt, pred, data_range=1.0))
    ssim = float(structural_similarity(gt, pred, channel_axis=2, data_range=1.0))

    with torch.no_grad():
        t_gt = to_lpips_tensor(gt)
        t_pred = to_lpips_tensor(pred)
        lp = float(lpips_model(t_gt, t_pred).item())

    return {"psnr": psnr, "ssim": ssim, "lpips": lp, "mse": mse, "mae": mae}


def summarize(values):
    arr = np.asarray(values, dtype=np.float64)
    return {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "median": float(np.median(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
    }


def analyze_render(gt_dir, pred_dir, lpips_model):
    gt_files = list_images(gt_dir)
    pred_files = list_images(pred_dir)

    # Se empareja por stem (nombre sin extension) para permitir formatos distintos
    # entre gt y pred (p.ej. dataset fuente en .png, render en .jpg).
    gt_map = {p.stem: p for p in gt_files}
    pred_map = {p.stem: p for p in pred_files}

    common_names = sorted(set(gt_map) & set(pred_map), key=natural_key)

    if not common_names:
        raise ValueError(f"Sin nombres de archivo en comun entre {gt_dir} y {pred_dir}")

    rng = np.random.default_rng(RANDOM_SEED)
    sample_n = min(N_SAMPLES, len(common_names))
    idx = rng.choice(len(common_names), size=sample_n, replace=False)
    idx.sort()
    sampled_names = [common_names[i] for i in idx]

    rows = []
    for i, name in enumerate(sampled_names):
        m = compute_pair_metrics(gt_map[name], pred_map[name], lpips_model)
        m["file_name"] = name
        rows.append(m)

        if (i + 1) % 20 == 0 or (i + 1) == len(sampled_names):
            print(f"    ... {i + 1}/{len(sampled_names)}")

    summary = {
        metric: summarize([r[metric] for r in rows])
        for metric in ["psnr", "ssim", "lpips", "mse", "mae"]
    }

    return {
        "total_paired_frames": len(common_names),
        "gt_only_frames": len(set(gt_map) - set(pred_map)),
        "pred_only_frames": len(set(pred_map) - set(gt_map)),
        "sampled_frames": sample_n,
        "random_seed": RANDOM_SEED,
        "resize_to": list(RESIZE_TO),
        "summary": summary,
        "per_frame": rows,
    }


def write_outputs(case, label, cfg, result):
    out_dir = cfg["out"]
    out_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "case": case,
        "method": label,
        "artifact": "render-benchmark",
        "generated_analysis_at": datetime.now().isoformat(),
        "gt_dir": str(cfg["gt"]),
        "pred_dir": str(cfg["pred"]),
        **result,
        "important_note": (
            "Metricas calculadas sobre una muestra aleatoria reproducible de "
            "frames (no todos), emparejados por nombre de archivo entre gt-rgb "
            "y rgb de la carpeta de render de Nerfstudio. PSNR/SSIM: mas alto "
            "es mejor. LPIPS/MSE/MAE: mas bajo es mejor."
        ),
    }

    json_path = out_dir / "render-benchmark-metadata.json"
    log_path = out_dir / "render-benchmark-metrics.log"

    json_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    s = result["summary"]
    lines = [
        "RENDER FIDELITY BENCHMARK",
        "=" * 70,
        "",
        f"Case: {case}",
        f"Method: {label}",
        f"GT dir: {cfg['gt']}",
        f"Pred dir: {cfg['pred']}",
        "",
        f"Total paired frames: {result['total_paired_frames']}",
        f"Sampled frames: {result['sampled_frames']} (seed={RANDOM_SEED})",
        "",
        "METRICS (mean / std / median / min / max)",
        "-------------------------------------------",
    ]

    for metric in ["psnr", "ssim", "lpips", "mse", "mae"]:
        m = s[metric]
        lines.append(
            f"{metric.upper():6s}: {m['mean']:.6f} / {m['std']:.6f} / {m['median']:.6f} / {m['min']:.6f} / {m['max']:.6f}"
        )

    lines += [
        "",
        "METHODOLOGICAL NOTE",
        "--------------------",
        metadata["important_note"],
    ]

    log_path.write_text("\n".join(lines), encoding="utf-8")

    return json_path, log_path


def main():
    print("Cargando modelo LPIPS (AlexNet, CPU)...")
    lpips_model = lpips.LPIPS(net="alex")
    lpips_model.eval()

    all_results = {}

    for case, methods in RENDERS.items():
        print()
        print("#" * 80)
        print(case)
        print("#" * 80)

        case_results = {}

        for label, cfg in methods.items():
            print()
            print("=" * 75)
            print(f"{case} :: {label}")
            print(f"  GT:   {cfg['gt']}")
            print(f"  Pred: {cfg['pred']}")
            print("=" * 75)

            if not cfg["gt"].exists() or not cfg["pred"].exists():
                print("[SKIP] carpeta gt o pred no existe")
                continue

            try:
                result = analyze_render(cfg["gt"], cfg["pred"], lpips_model)
            except Exception as e:
                print(f"[ERROR] {case} :: {label}: {e}")
                continue

            json_path, log_path = write_outputs(case, label, cfg, result)
            case_results[label] = result["summary"]

            s = result["summary"]
            print(f"[OK] PSNR: {s['psnr']['mean']:.3f}  SSIM: {s['ssim']['mean']:.4f}  LPIPS: {s['lpips']['mean']:.4f}")
            print(f"[OK] Log:  {log_path}")
            print(f"[OK] JSON: {json_path}")

        all_results[case] = case_results

        # Resumen comparativo por sitio
        comparison_path = THESIS / case / "02-resultados-finales" / "benchmark-comparison.log"
        lines = [
            f"RENDER BENCHMARK COMPARISON — {case}",
            "=" * 70,
            "",
            f"{'method':22s} {'PSNR':>8s} {'SSIM':>8s} {'LPIPS':>8s} {'MSE':>10s} {'MAE':>10s}",
            "-" * 70,
        ]
        for label, summ in case_results.items():
            lines.append(
                f"{label:22s} {summ['psnr']['mean']:8.3f} {summ['ssim']['mean']:8.4f} "
                f"{summ['lpips']['mean']:8.4f} {summ['mse']['mean']:10.6f} {summ['mae']['mean']:10.6f}"
            )
        lines += [
            "",
            "PSNR/SSIM: mas alto es mejor. LPIPS/MSE/MAE: mas bajo es mejor.",
        ]
        comparison_path.write_text("\n".join(lines), encoding="utf-8")
        print()
        print(f"[OK] Comparacion del sitio: {comparison_path}")

    print()
    print("Listo.")


if __name__ == "__main__":
    main()
