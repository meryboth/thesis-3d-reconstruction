"""
Diagrama de vision general del workflow de limpieza de distractores con
ComfyUI (Cap. 5, seccion 5.3.1): deteccion+segmentacion (YOLOv8-seg) -> filtro
de clase (COCO person/bird/car) -> inpainting (LaMa) -> dataset curado.

Version simplificada (4 pasos) del diagrama tecnico de nodos ya existente
(build_comfyui_pipeline_diagram.py, seccion 5.3.3) -- esta es para acompanar
la introduccion del benchmark, esa otra para el detalle de decisiones de diseno.
Mismo estilo visual que ambas (y que build_pipeline_diagram.py, Cap. 6).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

OUT = r"C:\nerfstudio_work\thesis\00-auditoria\preprocesamiento-comfyui\workflow-limpieza-distractores-overview.png"

fig, ax = plt.subplots(figsize=(12.5, 4.6))
ax.set_xlim(0, 12.5)
ax.set_ylim(-0.3, 4.6)
ax.axis("off")


def box(x, y, w, h, text, color="#e8eef7", edge="#2c5282", fontsize=10.5, textcolor="black"):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.07,rounding_size=0.12",
                        linewidth=1.8, edgecolor=edge, facecolor=color)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize,
             color=textcolor, wrap=True)


def arrow(x1, y1, x2, y2, color="#2c5282", lw=1.8):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16,
                          color=color, linewidth=lw)
    ax.add_patch(a)


Y_TOP, Y_BOT, H = 2.3, 0.3, 1.3

box(0.2, Y_TOP, 2.3, H, "Dataset original\n(raw, 1232 imágenes\nDJI)", color="#fdf3e0", edge="#b7791f")

box(2.8, Y_TOP, 2.8, H, "Detección + segmentación\nYOLOv8-seg (Ultralytics)\npor instancia, no por caja", color="#eaf0fb", edge="#2c5282")
arrow(2.5, Y_TOP + H / 2, 2.8, Y_TOP + H / 2)

box(5.9, Y_TOP, 2.8, H, "Filtro de clase COCO\nperson / bird / car\n(descarta el resto)", color="#fdeaea", edge="#9b2c2c")
arrow(5.6, Y_TOP + H / 2, 5.9, Y_TOP + H / 2)

box(5.9, Y_BOT, 2.8, H, "Inpainting — LaMa\nreconstruye la zona\neliminada de la máscara", color="#eaf7ea", edge="#276749")
arrow(7.3, Y_TOP, 7.3, Y_BOT + H)

box(9.0, Y_BOT, 2.5, H, "Dataset B curado\n648/1232 img. con al\nmenos 1 corrección", color="#f5eafd", edge="#6b46c1", fontsize=9.8)
arrow(8.7, Y_BOT + H / 2, 9.0, Y_BOT + H / 2)

ax.text(6.35, 0.05,
        "Corrida local en GPU, sin costo por imagen. Detalle de nodos y decisiones de diseño de ComfyUI: sección 5.3.3.",
        ha="center", va="center", fontsize=8.6, color="#55504a", style="italic")

ax.set_title("Workflow de limpieza de distractores — vista general (Cap. 5, sección 5.3.1)", fontsize=12.5, pad=12)

legend_elements = [
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#fdf3e0", markeredgecolor="#b7791f", markersize=13, label="Entrada / salida"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#eaf0fb", markeredgecolor="#2c5282", markersize=13, label="Detección"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#fdeaea", markeredgecolor="#9b2c2c", markersize=13, label="Filtro de clase (decisión clave)"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#eaf7ea", markeredgecolor="#276749", markersize=13, label="Inpainting"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#f5eafd", markeredgecolor="#6b46c1", markersize=13, label="Output final"),
]
ax.legend(handles=legend_elements, loc="upper left", bbox_to_anchor=(0.0, 1.22), ncol=3, fontsize=8.2, framealpha=0.95)

fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("guardado:", OUT)
