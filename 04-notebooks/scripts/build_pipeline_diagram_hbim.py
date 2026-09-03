"""
Diagrama de flujo del Pipeline A (integracion HBIM) propuesto en el
Capitulo 6, seccion 6.2.2. Generado con matplotlib (sin dependencias
graficas adicionales), mismo estilo visual que build_pipeline_diagram.py
(retirado) y build_comfyui_pipeline_diagram.py.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

OUT = r"C:\nerfstudio_work\thesis\05-tesis\capitulo6_pipeline_definitivo\media\pipeline-a-hbim.png"

fig, ax = plt.subplots(figsize=(7.5, 11.8))
ax.set_xlim(0, 7.5)
ax.set_ylim(-0.4, 15.6)
ax.axis("off")


def box(x, y, w, h, text, color="#e8eef7", edge="#2c5282", fontsize=10,
        textcolor="black", dashed=False):
    ls = "dashed" if dashed else "solid"
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                        linewidth=1.6, edgecolor=edge, facecolor=color, linestyle=ls)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize,
             color=textcolor, wrap=True)


def arrow(x1, y1, x2, y2, color="#2c5282", lw=1.8):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16,
                         color=color, linewidth=lw)
    ax.add_patch(a)


CW, CX = 4.4, 1.55  # ancho y x comun de las cajas centrales

# Tronco comun (6.2.1)
box(CX, 14.4, CW, 1.0, "Captura — un único dispositivo\n(DJI Neo 2 o Insta360 X5, nunca combinados)",
    color="#fdf3e0", edge="#b7791f")
box(CX, 13.0, CW, 1.0, "SfM con verificación binaria\n(RealityScan / COLMAP nativo)",
    color="#eaf0fb", edge="#2c5282")
arrow(3.75, 14.4, 3.75, 14.0)

box(CX, 11.6, CW, 1.0, "Malla texturizada (.obj) +\nnube de puntos densa",
    color="#eaf0fb", edge="#2c5282")
arrow(3.75, 13.0, 3.75, 12.6)

# --- Implementado y validado ---
box(CX, 10.0, CW, 1.1, "Segmentación geométrica automática\n(cubierta / columna / baranda / piso)",
    color="#eaf7ea", edge="#276749")
arrow(3.75, 11.6, 3.75, 11.1)

box(CX, 8.5, CW, 1.1, "Control de calidad humano\n(editor manual, visor /segmentador)",
    color="#eaf7ea", edge="#276749")
arrow(3.75, 10.0, 3.75, 9.6)

box(CX, 7.0, CW, 1.1, "Nube segmentada por clase (.ply)\n→ descarga en el archivo digital web",
    color="#f5eafd", edge="#6b46c1")
arrow(3.75, 8.5, 3.75, 8.1)
arrow(3.75, 7.0, 3.75, 6.55, color="#718096")

# Separador implementado / conceptual
ax.plot([0.3, 7.2], [6.3, 6.3], color="#a0aec0", linewidth=1.2, linestyle=(0, (4, 3)))
ax.text(3.75, 6.3, "  implementado y validado ↑     ↓ propuesta conceptual  ",
        ha="center", va="center", fontsize=7.5, color="#718096", style="italic",
        backgroundcolor="white")

# --- Propuesta conceptual (no implementada) ---
box(CX, 5.1, CW, 1.1, "Decimación y limpieza topológica\nde la malla SfM",
    color="#f7f7f7", edge="#718096", dashed=True)
arrow(3.75, 6.05, 3.75, 5.7, color="#718096")

box(CX, 3.6, CW, 1.1, "Importación a entorno de modelado\n(Recap Photo / Revit) como referencia\nscan-to-BIM",
    color="#f7f7f7", edge="#718096", dashed=True, fontsize=9)
arrow(3.75, 5.1, 3.75, 4.7, color="#718096")

box(CX, 2.1, CW, 1.1, "Modelado paramétrico\nmanual / semiautomático (LOD HBIM)",
    color="#f7f7f7", edge="#718096", dashed=True)
arrow(3.75, 3.6, 3.75, 3.2, color="#718096")

box(CX, 0.6, CW, 1.1, "Vínculo documental bidireccional\n(SfM original como respaldo del modelo BIM)",
    color="#f7f7f7", edge="#718096", dashed=True)
arrow(3.75, 2.1, 3.75, 1.7, color="#718096")

ax.set_title("Pipeline A — Integración HBIM\n(Capítulo 6, sección 6.2.2)", fontsize=13, pad=14)

legend_elements = [
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#fdf3e0", markeredgecolor="#b7791f", markersize=13, label="Captura"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#eaf0fb", markeredgecolor="#2c5282", markersize=13, label="SfM"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#eaf7ea", markeredgecolor="#276749", markersize=13, label="Implementado y validado"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#f5eafd", markeredgecolor="#6b46c1", markersize=13, label="Output / descarga"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#f7f7f7", markeredgecolor="#718096", markersize=13, label="Propuesta conceptual (sin implementar)"),
]
ax.legend(handles=legend_elements, loc="lower center", bbox_to_anchor=(0.5, -0.06),
          fontsize=8, framealpha=0.95, ncol=2)

fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("guardado:", OUT)
