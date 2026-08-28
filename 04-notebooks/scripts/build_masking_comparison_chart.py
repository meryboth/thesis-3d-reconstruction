"""
Comparacion del experimento de mascara de entrenamiento (RMBG-2.0) sobre el
Templete Central (DJI): raw (sin mascara) vs. con mascara, para Nerfacto y
Splatfacto. Complementa (no reemplaza) el experimento de H2 con ComfyUI --
esta es una variable independiente distinta (mascara vs. inpainting).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\masking-comparison")
OUT_DIR.mkdir(parents=True, exist_ok=True)

RAW_NERFACTO = Path(r"C:\nerfstudio_work\thesis\02-templete-central\02-resultados-finales\dji\nerfacto\render\render-benchmark-metadata.json")
RAW_SPLATFACTO = Path(r"C:\nerfstudio_work\thesis\02-templete-central\02-resultados-finales\dji\splatfacto\render\render-benchmark-metadata.json")

MASKED_SPLATFACTO = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\splatfacto-masked-raw-training\eval_results.json")
MASKED_NERFACTO = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\nerfacto-masked-raw-training\eval_results.json")


def load_raw(path):
    d = json.loads(path.read_text(encoding="utf-8"))["summary"]
    return {"psnr": d["psnr"]["mean"], "ssim": d["ssim"]["mean"], "lpips": d["lpips"]["mean"]}


def load_masked(path):
    d = json.loads(path.read_text(encoding="utf-8"))["results"]
    return {"psnr": d["psnr"], "ssim": d["ssim"], "lpips": d["lpips"]}


data = {
    "Nerfacto": {"raw": load_raw(RAW_NERFACTO), "masked": load_masked(MASKED_NERFACTO)},
    "Splatfacto": {"raw": load_raw(RAW_SPLATFACTO), "masked": load_masked(MASKED_SPLATFACTO)},
}

csv_path = OUT_DIR / "masking_comparison.csv"
with open(csv_path, "w", encoding="utf-8") as f:
    f.write("tecnica,dataset,psnr,ssim,lpips\n")
    for tec, d in data.items():
        f.write(f"{tec},raw,{d['raw']['psnr']:.3f},{d['raw']['ssim']:.4f},{d['raw']['lpips']:.4f}\n")
        f.write(f"{tec},con mascara,{d['masked']['psnr']:.3f},{d['masked']['ssim']:.4f},{d['masked']['lpips']:.4f}\n")
print(f"[OK] {csv_path}")

metrics = [("psnr", "PSNR (dB) — mas alto es mejor"), ("ssim", "SSIM — mas alto es mejor"), ("lpips", "LPIPS — mas bajo es mejor")]
techniques = list(data.keys())
x = np.arange(len(techniques))
width = 0.35

fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
for ax, (key, label) in zip(axes, metrics):
    raw_vals = [data[t]["raw"][key] for t in techniques]
    masked_vals = [data[t]["masked"][key] for t in techniques]
    ax.bar(x - width / 2, raw_vals, width, label="Raw (sin mascara)", color="#7f8c8d")
    ax.bar(x + width / 2, masked_vals, width, label="Con mascara de entrenamiento", color="#c0392b")
    ax.set_xticks(x)
    ax.set_xticklabels(techniques)
    ax.set_title(label, fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(top=max(raw_vals + masked_vals) * 1.18)
    for i, v in enumerate(raw_vals):
        ax.text(i - width / 2, v, f"{v:.2f}", ha="center", va="bottom", fontsize=8)
    for i, v in enumerate(masked_vals):
        ax.text(i + width / 2, v, f"{v:.2f}", ha="center", va="bottom", fontsize=8)

fig.legend(["Raw (sin mascara)", "Con mascara de entrenamiento"], loc="upper center", ncol=2, fontsize=9, bbox_to_anchor=(0.5, 1.06), frameon=False)
fig.suptitle("Templete Central (DJI): raw vs. mascara de entrenamiento RMBG, por tecnica", fontsize=11.5)
fig.text(0.5, -0.02,
          "Ground truth de evaluacion = foto completa (con fondo); el modelo con mascara no compite por esa region, por eso cae en las 3 metricas.\n"
          "Nerfacto/con mascara corrio ademas a downscale x4 (limitacion de memoria) -- confound adicional sobre esta comparacion.",
          ha="center", fontsize=8, color="#555", style="italic")
fig.tight_layout()
fig.savefig(OUT_DIR / "masking_psnr_ssim_lpips_raw_vs_masked.png", dpi=150, bbox_inches="tight")
print(f"[OK] {OUT_DIR / 'masking_psnr_ssim_lpips_raw_vs_masked.png'}")
