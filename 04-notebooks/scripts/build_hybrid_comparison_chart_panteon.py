"""
Comparacion de H4 (dataset multi-dispositivo): DJI solo vs. Insta360 solo vs.
Hibrido DJI+Insta360, sobre el Panteon Asociacion Espanola, por tecnica --
misma logica que build_hybrid_comparison_chart.py (Templete Central),
aplicada al segundo caso de estudio con dataset hibrido, una vez rescatado el
componente COLMAP principal (Capitulo 5, seccion 5.5.1 -- fila que decia
"sin exportar").
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\hibrido-comparison")
OUT_DIR.mkdir(parents=True, exist_ok=True)

DJI_NERFACTO = Path(r"C:\nerfstudio_work\thesis\03-panteon-asociacion-espanola\02-resultados-finales\dji\nerfacto\render\render-benchmark-metadata.json")
DJI_SPLATFACTO = Path(r"C:\nerfstudio_work\thesis\03-panteon-asociacion-espanola\02-resultados-finales\dji\splatfacto\render\render-benchmark-metadata.json")
INSTA_NERFACTO = Path(r"C:\nerfstudio_work\thesis\03-panteon-asociacion-espanola\02-resultados-finales\insta360\nerfacto\render\render-benchmark-metadata.json")
INSTA_SPLATFACTO = Path(r"C:\nerfstudio_work\thesis\03-panteon-asociacion-espanola\02-resultados-finales\insta360\splatfacto\render\render-benchmark-metadata.json")

HIB_NERFACTO = Path(r"C:\nerfstudio_work\thesis\03-panteon-asociacion-espanola\01-experimentos\hybrid-dji-insta360-colmap\run-20260827-163722\training-nerfacto\eval_results.json")
HIB_SPLATFACTO = Path(r"C:\nerfstudio_work\thesis\03-panteon-asociacion-espanola\01-experimentos\hybrid-dji-insta360-colmap\run-20260827-163722\training-splatfacto\eval_results.json")


def load_raw(path):
    d = json.loads(path.read_text(encoding="utf-8"))["summary"]
    return {"psnr": d["psnr"]["mean"], "ssim": d["ssim"]["mean"], "lpips": d["lpips"]["mean"]}


def load_eval(path):
    d = json.loads(path.read_text(encoding="utf-8"))["results"]
    return {"psnr": d["psnr"], "ssim": d["ssim"], "lpips": d["lpips"]}


data = {
    "Nerfacto": {"DJI": load_raw(DJI_NERFACTO), "Insta360": load_raw(INSTA_NERFACTO), "Hibrido": load_eval(HIB_NERFACTO)},
    "Splatfacto": {"DJI": load_raw(DJI_SPLATFACTO), "Insta360": load_raw(INSTA_SPLATFACTO), "Hibrido": load_eval(HIB_SPLATFACTO)},
}

csv_path = OUT_DIR / "hibrido_comparison_panteon.csv"
with open(csv_path, "w", encoding="utf-8") as f:
    f.write("tecnica,dataset,psnr,ssim,lpips\n")
    for tec, d in data.items():
        for ds in ("DJI", "Insta360", "Hibrido"):
            v = d[ds]
            f.write(f"{tec},{ds},{v['psnr']:.3f},{v['ssim']:.4f},{v['lpips']:.4f}\n")
print(f"[OK] {csv_path}")
for tec, d in data.items():
    for ds in ("DJI", "Insta360", "Hibrido"):
        print(f"  {tec:12s} {ds:10s} psnr={d[ds]['psnr']:.3f} ssim={d[ds]['ssim']:.4f} lpips={d[ds]['lpips']:.4f}")

metrics = [("psnr", "PSNR (dB) — mas alto es mejor"), ("ssim", "SSIM — mas alto es mejor"), ("lpips", "LPIPS — mas bajo es mejor")]
techniques = list(data.keys())
datasets = ["DJI", "Insta360", "Hibrido"]
colors = {"DJI": "#2980b9", "Insta360": "#27ae60", "Hibrido": "#c0392b"}
x = np.arange(len(techniques))
width = 0.25

fig, axes = plt.subplots(1, 3, figsize=(14, 4.8))
for ax, (key, label) in zip(axes, metrics):
    for i, ds in enumerate(datasets):
        vals = [data[t][ds][key] for t in techniques]
        offset = (i - 1) * width
        bars = ax.bar(x + offset, vals, width, label=ds, color=colors[ds])
        for xi, v in zip(x + offset, vals):
            ax.text(xi, v, f"{v:.2f}", ha="center", va="bottom", fontsize=7.5)
    ax.set_xticks(x)
    ax.set_xticklabels(techniques)
    ax.set_title(label, fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    vmax = max(data[t][ds][key] for t in techniques for ds in datasets)
    ax.set_ylim(top=vmax * 1.2)

fig.legend(datasets, loc="upper center", ncol=3, fontsize=9, bbox_to_anchor=(0.5, 1.08), frameon=False)
fig.suptitle("Panteón Asociación Española: DJI vs. Insta360 vs. Híbrido, por técnica", fontsize=11.5, y=1.0)
fig.text(0.5, -0.03,
          "DJI/Insta360: analyze_render_benchmark.py. Hibrido: ns-eval (corrida fuera de la estructura curada, en thesis/03-panteon-asociacion-espanola/01-experimentos/) -- mismo tipo de metrica, pipeline de calculo distinto.\n"
          "Nerfacto e Insta360-solo/DJI-solo evaluados en condiciones distintas de resolucion/subset -- ver nota metodologica en el capitulo.",
          ha="center", fontsize=7.5, color="#555", style="italic")
fig.tight_layout()
fig.savefig(OUT_DIR / "hibrido_psnr_ssim_lpips_panteon.png", dpi=150, bbox_inches="tight")
print(f"[OK] {OUT_DIR / 'hibrido_psnr_ssim_lpips_panteon.png'}")
