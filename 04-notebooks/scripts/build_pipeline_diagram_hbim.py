"""
Diagrama de flujo del Pipeline A (integracion HBIM) propuesto en el
Capitulo 6, seccion 6.2.2. Generado con matplotlib (sin dependencias
graficas adicionales), mismo estilo visual que build_pipeline_diagram.py
(retirado) y build_comfyui_pipeline_diagram.py.

El pipeline parte de la NUBE DE PUNTOS densa de SfM (no de la malla):
la nube es la que se segmenta y se propone como referencia scan-to-BIM.
La malla texturizada queda como respaldo documental aparte (conecta
directo al paso de vinculo documental, sin pasar por la segmentacion).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

OUT = r"C:\nerfstudio_work\thesis\05-tesis\capitulo6_pipeline_definitivo\media\pipeline-a-hbim.png"

fig, ax = plt.subplots(figsize=(7.8, 10.6))
ax.set_xlim(0, 7.8)
ax.set_ylim(-0.4, 14.0)
ax.axis("off")


def box(x, y, w, h, text, color="#e8eef7", edge="#2c5282", fontsize=10,
        textcolor="black", dashed=False):
    ls = "dashed" if dashed else "solid"
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                        linewidth=1.6, edgecolor=edge, facecolor=color, linestyle=ls)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize,
             color=textcolor, wrap=True)


def arrow(x1, y1, x2, y2, color="#2c5282", lw=1.8, connectionstyle="arc3,rad=0"):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16,
                         color=color, linewidth=lw, connectionstyle=connectionstyle)
    ax.add_patch(a)


CW, CX = 4.4, 1.55  # ancho y x comun de las cajas centrales

# Tronco comun (6.2.1)
box(CX, 12.8, CW, 1.0, "Captura — un único dispositivo\n(DJI Neo 2 o Insta360 X5, nunca combinados)",
    color="#fdf3e0", edge="#b7791f")
box(CX, 11.4, CW, 1.0, "SfM con verificación binaria\n(RealityScan / COLMAP nativo)",
    color="#eaf0fb", edge="#2c5282")
arrow(3.75, 12.8, 3.75, 12.4)

# Nube de puntos (principal) + malla (respaldo, caja lateral aparte)
box(CX, 10.0, CW, 1.0, "Nube de puntos densa de SfM\n(input del Pipeline A)",
    color="#eaf0fb", edge="#2c5282")
arrow(3.75, 11.4, 3.75, 11.0)

box(0.15, 10.0, 1.9, 1.0, "Malla\ntexturizada\n(.obj)", color="#f0f0f0", edge="#a0aec0", fontsize=8)
arrow(1.55, 11.4, 1.1, 11.0, color="#a0aec0")

# --- Implementado y validado ---
box(CX, 8.5, CW, 1.1, "Segmentación geométrica automática\n(cubierta / columna / baranda / piso)",
    color="#eaf7ea", edge="#276749")
arrow(3.75, 10.0, 3.75, 9.6)

box(CX, 7.0, CW, 1.1, "Control de calidad humano\n(editor manual, visor /segmentador)",
    color="#eaf7ea", edge="#276749")
arrow(3.75, 8.5, 3.75, 8.1)

box(CX, 5.5, CW, 1.1, "Nube segmentada por clase (.ply)\n→ descarga en el archivo digital web",
    color="#f5eafd", edge="#6b46c1")
arrow(3.75, 7.0, 3.75, 6.6)
arrow(3.75, 5.5, 3.75, 5.05, color="#718096")

# Separador implementado / conceptual
ax.plot([0.3, 7.5], [4.8, 4.8], color="#a0aec0", linewidth=1.2, linestyle=(0, (4, 3)))
ax.text(3.75, 4.8, "  implementado y validado ↑     ↓ propuesta conceptual  ",
        ha="center", va="center", fontsize=7.5, color="#718096", style="italic",
        backgroundcolor="white")

# --- Propuesta conceptual (no implementada) ---
box(CX, 3.55, CW, 1.1, "Importación a entorno de modelado\n(Recap Photo / Revit) — nube YA CLASIFICADA\ncomo referencia scan-to-BIM",
    color="#f7f7f7", edge="#718096", dashed=True, fontsize=9)
arrow(3.75, 5.05, 3.75, 4.65, color="#718096")

box(CX, 2.05, CW, 1.1, "Modelado paramétrico manual / semiautomático\n(cada clase → categoría Revit, LOD HBIM)",
    color="#f7f7f7", edge="#718096", dashed=True, fontsize=9)
arrow(3.75, 3.55, 3.75, 3.15, color="#718096")

box(CX, 0.4, CW, 1.1, "Vínculo documental bidireccional\n(malla + SfM original como respaldo del modelo BIM)",
    color="#f7f7f7", edge="#718096", dashed=True, fontsize=9)
arrow(3.75, 2.05, 3.75, 1.5, color="#718096")

# La malla conecta directo al vinculo documental, sin pasar por la segmentacion
arrow(1.1, 10.0, 1.1, 0.95, color="#a0aec0", connectionstyle="arc3,rad=-0.15")
arrow(1.1, 0.95, 1.55, 0.95, color="#a0aec0")

ax.set_title("Pipeline A — Integración HBIM\n(Capítulo 6, sección 6.2.2)", fontsize=13, pad=14)

legend_elements = [
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#fdf3e0", markeredgecolor="#b7791f", markersize=13, label="Captura"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#eaf0fb", markeredgecolor="#2c5282", markersize=13, label="SfM"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#eaf7ea", markeredgecolor="#276749", markersize=13, label="Implementado y validado"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#f5eafd", markeredgecolor="#6b46c1", markersize=13, label="Output / descarga"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#f7f7f7", markeredgecolor="#718096", markersize=13, label="Propuesta conceptual (sin implementar)"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#f0f0f0", markeredgecolor="#a0aec0", markersize=13, label="Respaldo documental (fuera del flujo principal)"),
]
ax.legend(handles=legend_elements, loc="lower center", bbox_to_anchor=(0.5, -0.08),
          fontsize=8, framealpha=0.95, ncol=2)

fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("guardado:", OUT)
