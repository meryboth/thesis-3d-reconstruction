"""
Diagrama de flujo del pipeline definitivo propuesto en el Capitulo 6.
Generado con matplotlib (sin dependencias graficas adicionales).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

OUT = r"C:\nerfstudio_work\thesis\05-tesis\capitulo6_pipeline_definitivo\media\pipeline-definitivo.png"

fig, ax = plt.subplots(figsize=(13, 8))
ax.set_xlim(0, 13)
ax.set_ylim(-4.2, 8)
ax.axis("off")

def box(x, y, w, h, text, color="#e8eef7", edge="#2c5282", fontsize=10, textcolor="black"):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                        linewidth=1.6, edgecolor=edge, facecolor=color)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize,
             color=textcolor, wrap=True)

def arrow(x1, y1, x2, y2, color="#2c5282", style="-|>", lw=1.8, connectionstyle="arc3,rad=0"):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=16,
                          color=color, linewidth=lw, connectionstyle=connectionstyle)
    ax.add_patch(a)

# Fila 1 -- Captura
box(0.3, 6.6, 2.7, 1.0, "Captura\nDJI Neo 2 (drone)", color="#fdf3e0", edge="#b7791f")
box(3.3, 6.6, 2.7, 1.0, "Captura\nInsta360 X5 (360°)", color="#fdf3e0", edge="#b7791f")
box(1.8, 5.2, 2.7, 1.0, "Extracción de fotogramas\n(cadencia fija)", color="#fdf3e0", edge="#b7791f")

arrow(1.65, 6.6, 2.7, 6.2)
arrow(4.65, 6.6, 3.7, 6.2)

# Preprocesamiento
box(1.8, 3.8, 2.7, 1.0, "Preprocesamiento\nComfyUI (curado)", color="#eaf7ea", edge="#276749")
arrow(3.15, 5.2, 3.15, 4.8)

# SfM
box(1.8, 2.4, 2.7, 1.0, "SfM\nCOLMAP / RealityCapture\n(mejor registro)", color="#eaf0fb", edge="#2c5282")
arrow(3.15, 3.8, 3.15, 3.4)

# Verificacion de registro (hallazgo metodologico)
box(5.0, 2.4, 3.0, 1.0, "Verificación binaria\n(cameras/images/points3D)\nno solo el log del wrapper", color="#fdeaea", edge="#9b2c2c", fontsize=9)
arrow(4.5, 2.9, 5.0, 2.9, color="#9b2c2c", style="-|>")

# Nerfstudio unificado -> dos ramas
box(1.0, 1.0, 2.2, 1.0, "Nerfacto (NeRF)\nsíntesis de vistas", color="#eaf0fb", edge="#2c5282")
box(3.6, 1.0, 2.2, 1.0, "Splatfacto (3DGS)\ntiempo real", color="#eaf0fb", edge="#2c5282")
arrow(2.8, 2.4, 2.1, 2.0)
arrow(3.5, 2.4, 4.7, 2.0)

# SfM output propio (malla)
box(6.4, 1.0, 2.2, 1.0, "Malla texturizada\n(.obj → .glTF)\nSfM / BIM", color="#eaf0fb", edge="#2c5282")
arrow(6.5, 2.4, 7.4, 2.0)

# SuperSplat
box(3.6, -0.4, 2.2, 1.0, "SuperSplat\nedición y exportación\n(.splat / .ply)", color="#eaf7ea", edge="#276749")
arrow(4.7, 1.0, 4.7, 0.6)

# Salidas finales
box(0.4, -1.8, 2.6, 1.0, "MLP entrenado\n(síntesis de vistas /\nrender de video)", color="#f5eafd", edge="#6b46c1", fontsize=9)
box(3.4, -1.8, 2.6, 1.0, ".splat / .ply\n(visor web,\nrenderizado en vivo)", color="#f5eafd", edge="#6b46c1", fontsize=9)
box(6.4, -1.8, 2.6, 1.0, ".glTF\n(visor web,\nintegración BIM/Revit)", color="#f5eafd", edge="#6b46c1", fontsize=9)

arrow(1.7, 1.0, 1.7, -0.8)
arrow(4.7, -0.4, 4.7, -0.8)
arrow(7.5, 1.0, 7.5, -0.8)

# Archivo digital web
box(2.0, -3.4, 6.0, 1.0, "Archivo digital de patrimonio arquitectónico\n(Potree / Sketchfab / Three.js / visor SuperSplat)", color="#fdf3e0", edge="#b7791f")
arrow(1.7, -1.8, 3.5, -2.4)
arrow(4.7, -1.8, 4.9, -2.4)
arrow(7.5, -1.8, 6.5, -2.4)

ax.set_title("Pipeline definitivo propuesto — captura a archivo digital web / BIM", fontsize=13, pad=14)

legend_elements = [
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#fdf3e0", markeredgecolor="#b7791f", markersize=14, label="Captura / publicación"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#eaf7ea", markeredgecolor="#276749", markersize=14, label="Preprocesamiento / edición"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#eaf0fb", markeredgecolor="#2c5282", markersize=14, label="Reconstrucción 3D"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#f5eafd", markeredgecolor="#6b46c1", markersize=14, label="Output final"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#fdeaea", markeredgecolor="#9b2c2c", markersize=14, label="Control de calidad (hallazgo metodológico)"),
]
ax.legend(handles=legend_elements, loc="upper right", fontsize=8, framealpha=0.95)

fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("guardado:", OUT)
