"""
Graficos de las estadisticas del batch de limpieza ComfyUI sobre el dataset DJI
completo del Templete Central (1232 imagenes), documentado en el Capitulo 5,
seccion 5.2.3: cuantas imagenes tuvieron deteccion vs. no, y como se distribuye
la cobertura de mascara entre las que si tuvieron deteccion.

Fuente de datos: panteon-chacarita/templete-central/dataset-dji-comfyui-clean/logs/batch_log.csv
Mismo estilo que build_psnr_vs_complejidad.py / build_pipeline_diagram.py.
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

LOG_PATH = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\dataset-dji-comfyui-clean\logs\batch_log.csv")
OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\preprocesamiento-comfyui")

COLOR_DETECTED = "#2c5282"
COLOR_CLEAN = "#a0aec0"
COLOR_BAR = "#2c5282"

with open(LOG_PATH, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

# El log tiene 1217 filas "OK" (con mascara/cobertura calculada) + 15 filas
# "EXCEPTION" (fallos transitorios durante el calculo de cobertura o el
# logging, no durante la limpieza en si: los 1232 archivos de salida existen
# igual en dataset-dji-comfyui-clean/images/, verificado por diff de nombres
# de archivo contra el dataset raw). Esas 15 se cuentan como "sin deteccion"
# igual que las que dieron cobertura 0 -- es el criterio ya usado en el texto
# del Cap. 5 (648 con deteccion / 584 sin deteccion, sobre 1232 totales).
coverages = []
n_detected = 0
n_clean = 0
for row in rows:
    if row["result"] != "OK":
        n_clean += 1
        continue
    cov = float(row["mask_coverage_pct"])
    if cov > 0:
        n_detected += 1
        coverages.append(cov)
    else:
        n_clean += 1

total = n_detected + n_clean
print(f"total={total} detected={n_detected} ({n_detected/total*100:.1f}%) clean={n_clean}")
print(f"cobertura promedio (detectadas): {sum(coverages)/len(coverages):.3f}%  max={max(coverages):.2f}%")

# ---- Grafico 1: barras -- imagenes con/sin deteccion ----
fig1, ax1 = plt.subplots(figsize=(6.2, 4.2))
labels = [f"Con detección\n{n_detected} ({n_detected/total*100:.1f}%)",
          f"Sin detección\n{n_clean} ({n_clean/total*100:.1f}%)"]
values = [n_detected, n_clean]
bars = ax1.bar(labels, values, color=[COLOR_DETECTED, COLOR_CLEAN], width=0.55, edgecolor="white")
for b, v in zip(bars, values):
    ax1.text(b.get_x() + b.get_width() / 2, v + 15, str(v), ha="center", fontsize=11, fontweight="bold")
ax1.set_ylabel("Cantidad de imágenes")
ax1.set_title(f"Detección de distractores — dataset DJI completo (n={total})", fontsize=11.5)
ax1.set_ylim(0, max(values) * 1.18)
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)
fig1.tight_layout()
out1 = OUT_DIR / "batch_deteccion_conteo.png"
fig1.savefig(out1, dpi=150, bbox_inches="tight")
print("guardado:", out1)

# ---- Grafico 2: histograma -- distribucion de cobertura de mascara ----
fig2, ax2 = plt.subplots(figsize=(7.2, 4.2))
bins = [0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.75, 1.0, 1.25]
ax2.hist(coverages, bins=bins, color=COLOR_BAR, edgecolor="white")
mean_cov = sum(coverages) / len(coverages)
ax2.axvline(mean_cov, color="#c05621", linestyle="--", linewidth=1.6,
            label=f"Promedio: {mean_cov:.2f}%")
ax2.set_xlabel("Cobertura de máscara (% del cuadro)")
ax2.set_ylabel("Cantidad de imágenes")
ax2.set_title(f"Distribución de cobertura de máscara — {n_detected} imágenes con detección", fontsize=11.5)
ax2.legend(fontsize=9.5)
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)
fig2.tight_layout()
out2 = OUT_DIR / "batch_cobertura_mascara_histograma.png"
fig2.savefig(out2, dpi=150, bbox_inches="tight")
print("guardado:", out2)
