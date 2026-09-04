"""
Diagrama del pipeline definitivo unico propuesto en el Capitulo 6,
seccion 6.2: un tronco comun (captura + SfM) que se bifurca en dos
ramas -- integracion HBIM (izquierda) y archivo digital web (derecha)
-- y converge de nuevo en la descarga dual del archivo digital.

Reemplaza los diagramas separados build_pipeline_diagram_hbim.py y
build_pipeline_diagram_web.py (retirados), que mostraban cada rama
como un "pipeline" aparte.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

OUT = r"C:\nerfstudio_work\thesis\05-tesis\capitulo6_pipeline_definitivo\media\pipeline-definitivo.png"

fig, ax = plt.subplots(figsize=(12.1, 12.6))
ax.set_xlim(-0.6, 11.5)
ax.set_ylim(-0.4, 14.6)
ax.axis("off")


def box(x, y, w, h, text, color="#e8eef7", edge="#2c5282", fontsize=9.5,
        textcolor="black", dashed=False):
    ls = "dashed" if dashed else "solid"
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.07,rounding_size=0.1",
                        linewidth=1.5, edgecolor=edge, facecolor=color, linestyle=ls)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize,
            color=textcolor, wrap=True)


def arrow(x1, y1, x2, y2, color="#2c5282", lw=1.6, connectionstyle="arc3,rad=0"):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                         color=color, linewidth=lw, connectionstyle=connectionstyle)
    ax.add_patch(a)


TRUNK_CX, TRUNK_W = 5.75, 4.6  # tronco comun, centrado

# --- Tronco comun (6.2.1) ---
box(TRUNK_CX - TRUNK_W / 2, 13.2, TRUNK_W, 1.0, "Captura — un único dispositivo\n(DJI Neo 2 o Insta360 X5, nunca combinados)",
    color="#fdf3e0", edge="#b7791f")
box(TRUNK_CX - TRUNK_W / 2, 11.8, TRUNK_W, 1.0, "SfM con verificación binaria\n(RealityScan / COLMAP nativo) — sin preprocesamiento",
    color="#eaf0fb", edge="#2c5282")
arrow(TRUNK_CX, 13.2, TRUNK_CX, 12.8)

box(TRUNK_CX - TRUNK_W / 2, 10.4, TRUNK_W, 1.0, "Nube de puntos (densa + dispersa) + malla texturizada",
    color="#eaf0fb", edge="#2c5282")
arrow(TRUNK_CX, 11.8, TRUNK_CX, 11.4)

# Bifurcacion
ax.text(TRUNK_CX, 9.95, "▽  bifurca según el destino  ▽", ha="center", va="center",
        fontsize=8.5, color="#4a5568", style="italic")

LX, LW = 0.3, 5.0    # rama HBIM (izquierda)
RX, RW = 6.2, 5.0    # rama archivo digital web (derecha)
LCX, RCX = LX + LW / 2, RX + RW / 2

arrow(TRUNK_CX - 0.3, 10.4, LCX, 9.5, color="#276749", connectionstyle="arc3,rad=0.15")
arrow(TRUNK_CX + 0.3, 10.4, RCX, 9.5, color="#2c5282", connectionstyle="arc3,rad=-0.15")

# --- Rama HBIM (6.2.2), izquierda ---
ax.text(LCX, 9.7, "Rama HBIM (6.2.2)", ha="center", fontsize=10.5, weight="bold", color="#276749")

box(LX, 8.4, LW, 1.0, "Segmentación geométrica automática\n(cubierta / columna / baranda / piso)",
    color="#eaf7ea", edge="#276749")
arrow(LCX, 9.5, LCX, 9.4)

box(LX, 7.0, LW, 1.0, "Control de calidad humano\n(editor manual, visor /segmentador)",
    color="#eaf7ea", edge="#276749")
arrow(LCX, 8.4, LCX, 8.0)

box(LX, 5.6, LW, 1.0, "Nube segmentada por clase (.ply)\n→ descarga en el archivo digital web",
    color="#f5eafd", edge="#6b46c1")
arrow(LCX, 7.0, LCX, 6.6)

ax.plot([LX - 0.1, LX + LW + 0.1], [5.35, 5.35], color="#a0aec0", linewidth=1.1, linestyle=(0, (4, 3)))
ax.text(LCX, 5.35, "implementado ↑  ↓ conceptual", ha="center", va="center", fontsize=7,
        color="#718096", style="italic", backgroundcolor="white")

box(LX, 4.1, LW, 1.0, "Importación a Revit / Recap Photo\n— nube YA CLASIFICADA como referencia scan-to-BIM",
    color="#f7f7f7", edge="#718096", dashed=True, fontsize=8.5)
arrow(LCX, 5.6, LCX, 5.1, color="#718096")

box(LX, 2.6, LW, 1.0, "Modelado paramétrico manual / semiautomático\n(cada clase → categoría Revit, LOD HBIM)",
    color="#f7f7f7", edge="#718096", dashed=True, fontsize=8.5)
arrow(LCX, 4.1, LCX, 3.6, color="#718096")

box(LX, 1.1, LW, 1.0, "Vínculo documental bidireccional\n(malla + SfM original como respaldo)",
    color="#f7f7f7", edge="#718096", dashed=True, fontsize=8.5)
arrow(LCX, 2.6, LCX, 2.1, color="#718096")

# --- Rama archivo digital web (6.2.3), derecha ---
ax.text(RCX, 9.7, "Rama archivo digital web (6.2.3)", ha="center", fontsize=10.5, weight="bold", color="#2c5282")

box(RX, 8.4, RW, 1.0, "Entrenamiento Splatfacto (3DGS)\n— sin preprocesamiento, sin Nerfacto",
    color="#eaf0fb", edge="#2c5282")
arrow(RCX, 9.5, RCX, 9.4)

box(RX, 7.0, RW, 1.0, "Edición en SuperSplat\n(recorte de outliers y gaussianas de baja opacidad)",
    color="#eaf7ea", edge="#276749")
arrow(RCX, 8.4, RCX, 8.0)

box(RX, 5.6, RW, 1.0, "Exportación .splat / .ply",
    color="#f5eafd", edge="#6b46c1")
arrow(RCX, 7.0, RCX, 6.6)

# --- Convergencia: descarga dual ---
box(1.9, 0.1, 7.7, 1.1, "Archivo digital web — descarga dual\n.splat limpio (rama web) + .ply segmentado (rama HBIM)\n(visor `/segmentador`, sección 6.4)",
    color="#fdf3e0", edge="#b7791f", fontsize=9)
arrow(RCX, 5.6, RCX, 1.5, color="#6b46c1")

# la nube segmentada baja por el margen izquierdo, afuera de la columna
# de recuadros conceptuales, para no cruzarlos visualmente
MARGIN_X = LX - 0.5
arrow(LX, 6.0, MARGIN_X, 6.0, color="#6b46c1")
arrow(MARGIN_X, 6.0, MARGIN_X, 0.65, color="#6b46c1")
arrow(MARGIN_X, 0.65, 1.9, 0.65, color="#6b46c1")

ax.set_title("Pipeline definitivo: tronco común, rama HBIM y rama archivo digital web\n(Capítulo 6, sección 6.2)",
             fontsize=13, pad=16)

legend_elements = [
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#fdf3e0", markeredgecolor="#b7791f", markersize=12, label="Captura / publicación"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#eaf0fb", markeredgecolor="#2c5282", markersize=12, label="SfM / reconstrucción"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#eaf7ea", markeredgecolor="#276749", markersize=12, label="Implementado y validado"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#f5eafd", markeredgecolor="#6b46c1", markersize=12, label="Output / descarga"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#f7f7f7", markeredgecolor="#718096", markersize=12, label="Propuesta conceptual"),
]
ax.legend(handles=legend_elements, loc="lower center", bbox_to_anchor=(0.5, -0.055),
          fontsize=8, framealpha=0.95, ncol=3)

fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("guardado:", OUT)
