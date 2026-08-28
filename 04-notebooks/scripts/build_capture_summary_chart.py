"""
Resumen de la sesion de captura por caso de estudio y dispositivo -- duracion
de video y fotogramas totales antes del preprocesamiento, para el Capitulo 3
(seccion 3.6.4). Datos crudos: metadata de video (ffprobe) sobre los archivos
originales en las carpetas de trabajo, y conteo de fotogramas ya reportado en
la Tabla 4.6 del Capitulo 4.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\captura-dataset")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# caso -> {dispositivo: (duracion_min, fotogramas)}
data = {
    "Los Paraguas": {"DJI Neo 2": (12.28, 707)},
    "Templete Central": {"DJI Neo 2": (14.40, 1232), "Insta360 X5": (5.46, 306)},
    "Panteón Asociación Española": {"DJI Neo 2": (17.63, 1506), "Insta360 X5": (3.04, 311)},
}

casos = list(data.keys())
device_colors = {"DJI Neo 2": "#2980b9", "Insta360 X5": "#27ae60"}

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

x = np.arange(len(casos))
width = 0.35

for i, dev in enumerate(("DJI Neo 2", "Insta360 X5")):
    durs = [data[c].get(dev, (0, 0))[0] for c in casos]
    offset = (i - 0.5) * width
    bars = ax1.bar(x + offset, durs, width, label=dev, color=device_colors[dev])
    for xi, v in zip(x + offset, durs):
        if v > 0:
            ax1.text(xi, v, f"{v:.1f}", ha="center", va="bottom", fontsize=8)
ax1.set_xticks(x)
ax1.set_xticklabels(casos, fontsize=8)
ax1.set_ylabel("Duración total de video (min)")
ax1.set_title("Duración de captura por caso y dispositivo", fontsize=10)
ax1.grid(axis="y", alpha=0.3)
ax1.legend(fontsize=8)

for i, dev in enumerate(("DJI Neo 2", "Insta360 X5")):
    frames = [data[c].get(dev, (0, 0))[1] for c in casos]
    offset = (i - 0.5) * width
    bars = ax2.bar(x + offset, frames, width, label=dev, color=device_colors[dev])
    for xi, v in zip(x + offset, frames):
        if v > 0:
            ax2.text(xi, v, f"{v}", ha="center", va="bottom", fontsize=8)
ax2.set_xticks(x)
ax2.set_xticklabels(casos, fontsize=8)
ax2.set_ylabel("Fotogramas totales (antes del preprocesamiento)")
ax2.set_title("Fotogramas extraídos por caso y dispositivo", fontsize=10)
ax2.grid(axis="y", alpha=0.3)
ax2.legend(fontsize=8)

fig.suptitle("Resumen de la sesión de captura por caso de estudio", fontsize=11.5)
fig.tight_layout()
out_path = OUT_DIR / "resumen_captura_por_caso.png"
fig.savefig(out_path, dpi=150, bbox_inches="tight")
print(f"[OK] {out_path}")
