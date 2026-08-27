"""
Comparacion H2: metricas de render (PSNR/SSIM/LPIPS) de Nerfacto y Splatfacto
sobre el Templete Central (DJI), dataset raw vs. Dataset B (curado con
ComfyUI, reusando las poses de RealityScan -- ver Cap. 5, seccion 5.2.1/5.2.4).

Fuentes:
  raw:  02-templete-central/02-resultados-finales/{nerfacto,splatfacto}/render/render-benchmark-metadata.json
  B:    ns-eval corrido sobre las corridas de Docker (ver logs de esta sesion),
        volcado a mano aca porque las corridas viven en panteon-chacarita/ (carpeta cruda)

Nota metodologica IMPORTANTE: la corrida de Nerfacto sobre Dataset B se hizo
a downscale_factor=4 (memoria del sistema), mientras que la corrida raw de
Nerfacto fue a resolucion completa (downscale_factor=null) -- no es una
comparacion apples-to-apples, el downscale por si solo tiende a FACILITAR
PSNR/SSIM (menos detalle de alta frecuencia que acertar). La de Splatfacto
si es comparable 1:1 (downscale_factor=8 en ambas).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\h2-comfyui-comparison")
OUT_DIR.mkdir(parents=True, exist_ok=True)

RAW_NERFACTO = Path(r"C:\nerfstudio_work\thesis\02-templete-central\02-resultados-finales\dji\nerfacto\render\render-benchmark-metadata.json")
RAW_SPLATFACTO = Path(r"C:\nerfstudio_work\thesis\02-templete-central\02-resultados-finales\dji\splatfacto\render\render-benchmark-metadata.json")

B_SPLATFACTO = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\splatfacto-comfyui-clean-training\templete-central-comfyui-clean-splat-ds8\splatfacto\2026-08-26_205516\eval_results.json")
B_NERFACTO = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\nerfacto-comfyui-clean-training\templete-central-comfyui-clean-nerfacto-subset\nerfacto\2026-08-26_235802\eval_results.json")


def load_raw(path):
    d = json.loads(path.read_text(encoding="utf-8"))["summary"]
    return {"psnr": d["psnr"]["mean"], "ssim": d["ssim"]["mean"], "lpips": d["lpips"]["mean"]}


def load_b(path):
    d = json.loads(path.read_text(encoding="utf-8"))["results"]
    return {"psnr": d["psnr"], "ssim": d["ssim"], "lpips": d["lpips"]}


data = {
    "Nerfacto": {"raw": load_raw(RAW_NERFACTO), "b": load_b(B_NERFACTO)},
    "Splatfacto": {"raw": load_raw(RAW_SPLATFACTO), "b": load_b(B_SPLATFACTO)},
}

# --- CSV ---
csv_path = OUT_DIR / "h2_comparison.csv"
with open(csv_path, "w", encoding="utf-8") as f:
    f.write("tecnica,dataset,psnr,ssim,lpips\n")
    for tec, d in data.items():
        f.write(f"{tec},raw,{d['raw']['psnr']:.3f},{d['raw']['ssim']:.4f},{d['raw']['lpips']:.4f}\n")
        f.write(f"{tec},Dataset B (ComfyUI),{d['b']['psnr']:.3f},{d['b']['ssim']:.4f},{d['b']['lpips']:.4f}\n")
print(f"[OK] {csv_path}")

# --- chart: 3 subplots (PSNR, SSIM, LPIPS), grouped bars raw vs B, x=tecnica ---
metrics = [("psnr", "PSNR (dB) — mas alto es mejor"), ("ssim", "SSIM — mas alto es mejor"), ("lpips", "LPIPS — mas bajo es mejor")]
techniques = list(data.keys())
x = np.arange(len(techniques))
width = 0.35

fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
for ax, (key, label) in zip(axes, metrics):
    raw_vals = [data[t]["raw"][key] for t in techniques]
    b_vals = [data[t]["b"][key] for t in techniques]
    ax.bar(x - width / 2, raw_vals, width, label="Raw", color="#7f8c8d")
    ax.bar(x + width / 2, b_vals, width, label="Dataset B (ComfyUI)", color="#2980b9")
    ax.set_xticks(x)
    ax.set_xticklabels(techniques)
    ax.set_title(label, fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    for i, v in enumerate(raw_vals):
        ax.text(i - width / 2, v, f"{v:.2f}", ha="center", va="bottom", fontsize=8)
    for i, v in enumerate(b_vals):
        ax.text(i + width / 2, v, f"{v:.2f}", ha="center", va="bottom", fontsize=8)

axes[0].legend(fontsize=8, loc="lower right")
fig.suptitle("H2 — Templete Central (DJI): dataset raw vs. Dataset B (ComfyUI), por técnica", fontsize=11.5)
fig.text(0.5, -0.02,
          "Nerfacto/Dataset B corrió a downscale×4 por limitación de memoria (Nerfacto/raw fue a resolución completa) — no es 1:1.\n"
          "Splatfacto sí es comparable 1:1 (downscale×8 en ambas corridas).",
          ha="center", fontsize=8, color="#555", style="italic")
fig.tight_layout()
fig.savefig(OUT_DIR / "h2_psnr_ssim_lpips_raw_vs_clean.png", dpi=150, bbox_inches="tight")
print(f"[OK] {OUT_DIR / 'h2_psnr_ssim_lpips_raw_vs_clean.png'}")
