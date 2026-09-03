"""
Diagrama de flujo del Pipeline B (archivo digital web) propuesto en el
Capitulo 6, seccion 6.2.3. Generado con matplotlib (sin dependencias
graficas adicionales), mismo estilo visual que build_pipeline_diagram_hbim.py.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

OUT = r"C:\nerfstudio_work\thesis\05-tesis\capitulo6_pipeline_definitivo\media\pipeline-b-web.png"

fig, ax = plt.subplots(figsize=(7.5, 9.6))
ax.set_xlim(0, 7.5)
ax.set_ylim(-0.4, 12.4)
ax.axis("off")


def box(x, y, w, h, text, color="#e8eef7", edge="#2c5282", fontsize=10, textcolor="black"):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                        linewidth=1.6, edgecolor=edge, facecolor=color)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize,
             color=textcolor, wrap=True)


def arrow(x1, y1, x2, y2, color="#2c5282", lw=1.8, connectionstyle="arc3,rad=0"):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16,
                         color=color, linewidth=lw, connectionstyle=connectionstyle)
    ax.add_patch(a)


CW, CX = 4.4, 1.55  # ancho y x comun de las cajas centrales

# Tronco comun (6.2.1) -- identico al Pipeline A
box(CX, 11.2, CW, 1.0, "Captura — un único dispositivo\n(DJI Neo 2 o Insta360 X5, nunca combinados)",
    color="#fdf3e0", edge="#b7791f")
box(CX, 9.8, CW, 1.0, "SfM con verificación binaria\n(RealityScan / COLMAP nativo)",
    color="#eaf0fb", edge="#2c5282")
arrow(3.75, 11.2, 3.75, 10.8)

box(CX, 8.4, CW, 1.0, "Nube de puntos dispersa +\nposes de cámara (SfM)",
    color="#eaf0fb", edge="#2c5282")
arrow(3.75, 9.8, 3.75, 9.4)

# Entrenamiento Splatfacto
box(CX, 6.9, CW, 1.1, "Entrenamiento Splatfacto (3DGS)\n— sin preprocesamiento, sin Nerfacto",
    color="#eaf0fb", edge="#2c5282")
arrow(3.75, 8.4, 3.75, 8.0)

# Edicion en SuperSplat
box(CX, 5.4, CW, 1.1, "Edición en SuperSplat\n(recorte de outliers y gaussianas de baja opacidad)",
    color="#eaf7ea", edge="#276749")
arrow(3.75, 6.9, 3.75, 6.5)

# Exportacion
box(CX, 3.9, CW, 1.1, "Exportación .splat / .ply",
    color="#f5eafd", edge="#6b46c1")
arrow(3.75, 5.4, 3.75, 5.0)

# Confluencia con el .ply segmentado del Pipeline A
box(0.2, 2.3, 3.0, 1.1, "Nube segmentada (.ply)\n← Pipeline A, sección 6.2.2",
    color="#f5eafd", edge="#6b46c1", fontsize=9)
arrow(3.75, 3.9, 3.75, 3.55)
arrow(1.7, 3.9, 1.7, 3.4, color="#6b46c1")

# Publicacion web (descarga dual)
box(1.55, 0.6, 4.4, 1.3, "Archivo digital web\ndescarga dual: .splat limpio + .ply segmentado\n(visor `/segmentador`, sección 6.4)",
    color="#fdf3e0", edge="#b7791f", fontsize=9.5)
arrow(3.75, 3.9, 3.75, 1.9)
arrow(1.7, 2.3, 3.0, 1.9, color="#6b46c1")

ax.set_title("Pipeline B — Archivo digital web\n(Capítulo 6, sección 6.2.3)", fontsize=13, pad=14)

legend_elements = [
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#fdf3e0", markeredgecolor="#b7791f", markersize=13, label="Captura / publicación"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#eaf0fb", markeredgecolor="#2c5282", markersize=13, label="SfM / reconstrucción"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#eaf7ea", markeredgecolor="#276749", markersize=13, label="Edición"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#f5eafd", markeredgecolor="#6b46c1", markersize=13, label="Output / descarga"),
]
ax.legend(handles=legend_elements, loc="lower center", bbox_to_anchor=(0.5, -0.09),
          fontsize=8, framealpha=0.95, ncol=2)

fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("guardado:", OUT)
