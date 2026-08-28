"""
Comparacion Nerfacto vs. Splatfacto sobre el experimento adicional de la Torre
Tanque (Mar del Plata) -- dataset construido a partir de material audiovisual
de terceros (YouTube), no de un registro propio. Capitulo 5, seccion 5.11.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\torre-mardel-eval")

NERF = json.loads((OUT_DIR / "nerfacto_eval_results.json").read_text(encoding="utf-8"))["results"]
SPLAT = json.loads((OUT_DIR / "splatfacto_eval_results.json").read_text(encoding="utf-8"))["results"]

metrics = [("psnr", "PSNR (dB) — más alto es mejor"), ("ssim", "SSIM — más alto es mejor"), ("lpips", "LPIPS — más bajo es mejor")]
techniques = ["Nerfacto", "Splatfacto"]
values = {"Nerfacto": NERF, "Splatfacto": SPLAT}
colors = {"Nerfacto": "#e67e22", "Splatfacto": "#8e44ad"}

fig, axes = plt.subplots(1, 3, figsize=(11, 4.2))
for ax, (key, label) in zip(axes, metrics):
    vals = [values[t][key] for t in techniques]
    bars = ax.bar(techniques, vals, color=[colors[t] for t in techniques])
    for xi, v in zip(techniques, vals):
        ax.text(xi, v, f"{v:.3f}" if key != "psnr" else f"{v:.2f}", ha="center", va="bottom", fontsize=9)
    ax.set_title(label, fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(top=max(vals) * 1.2)

fig.suptitle("Torre Tanque (Mar del Plata) — Nerfacto vs. Splatfacto\nsobre dataset de terceros (YouTube)", fontsize=11.5)
fig.tight_layout()
out_path = OUT_DIR / "torre_mardel_psnr_ssim_lpips.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight")
print(f"[OK] {out_path}")
