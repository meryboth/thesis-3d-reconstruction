"""
Diagrama del pipeline de limpieza de distractores ejecutado con ComfyUI
(deteccion YOLO-seg + filtro de clase + inpainting LaMa), documentado en el
Capitulo 5, seccion 5.2. Mismo estilo que build_pipeline_diagram.py (Cap. 6).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

OUT = r"C:\nerfstudio_work\thesis\00-auditoria\preprocesamiento-comfyui\pipeline-comfyui-limpieza.png"

fig, ax = plt.subplots(figsize=(13, 6.2))
ax.set_xlim(0, 13)
ax.set_ylim(-0.3, 6.2)
ax.axis("off")


def box(x, y, w, h, text, color="#e8eef7", edge="#2c5282", fontsize=9.5, textcolor="black"):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.07,rounding_size=0.1",
                        linewidth=1.6, edgecolor=edge, facecolor=color)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize,
             color=textcolor, wrap=True)


def arrow(x1, y1, x2, y2, color="#2c5282", lw=1.6):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14,
                          color=color, linewidth=lw)
    ax.add_patch(a)


# fila 1: entrada
box(0.2, 4.9, 2.0, 1.0, "LoadImage\n(dataset raw,\n1 x 1232)", color="#fdf3e0", edge="#b7791f")

# deteccion
box(2.6, 4.9, 2.5, 1.0, "UltralyticsDetectorProvider\nYOLOv8m-seg (COCO, 80 clases)", color="#eaf0fb", edge="#2c5282")
arrow(2.2, 5.4, 2.6, 5.4)

box(5.5, 4.9, 2.7, 1.0, "ImpactSimpleDetectorSEGS\numbral 0.12 (capta aves\nchicas/lejanas)", color="#eaf0fb", edge="#2c5282")
arrow(5.1, 5.4, 5.5, 5.4)

box(8.6, 4.9, 2.8, 1.0, "ImpactSEGSLabelFilter\nlabels: person, bird, car\n(descarta las otras 77 clases)", color="#fdeaea", edge="#9b2c2c")
arrow(8.2, 5.4, 8.6, 5.4)

# fila 2: mascara
box(8.6, 3.3, 2.8, 1.0, "SegsToCombinedMask\nune todas las detecciones\nen 1 mascara binaria", color="#eaf0fb", edge="#2c5282")
arrow(10.0, 4.9, 10.0, 4.3)

box(5.5, 3.3, 2.7, 1.0, "INPAINT_ExpandMask\ngrow 10px / blur 6px\n(transicion sin borde duro)", color="#eaf0fb", edge="#2c5282")
arrow(8.6, 3.8, 8.2, 3.8)

# fila 3: inpainting
box(2.6, 1.7, 2.5, 1.0, "INPAINT_LoadInpaintModel\nLaMa (big-lama.pt)\nlocal, sin costo por imagen", color="#eaf7ea", edge="#276749")
box(5.5, 1.7, 2.7, 1.0, "INPAINT_InpaintWithModel\nreconstruye la zona\nborrada", color="#eaf0fb", edge="#2c5282")
arrow(6.85, 3.3, 6.85, 2.7)
arrow(5.1, 2.2, 5.5, 2.2)

# salida
box(8.9, 1.7, 2.5, 1.0, "SaveImage\nmismo nombre de archivo\nque el original", color="#f5eafd", edge="#6b46c1")
arrow(8.2, 2.2, 8.9, 2.2)

box(0.2, 1.7, 2.0, 1.0, "Imagen original\n(pasa sin cambios si\nno hay deteccion)", color="#fdf3e0", edge="#b7791f", fontsize=8.7)
arrow(1.2, 4.9, 1.2, 2.7)
arrow(2.2, 2.2, 5.5, 1.9)

# nota inferior
ax.text(6.5, 0.5,
        "648 / 1232 imagenes (52,6%) tuvieron al menos una deteccion. Cobertura de mascara promedio: 0,22% del cuadro.\n"
        "Alternativas probadas para el paso de inpainting (MAT, SDXL+Fooocus) — ver seccion 5.2.3.",
        ha="center", va="center", fontsize=8.3, color="#55504a", style="italic")

ax.set_title("Pipeline de limpieza de distractores — ComfyUI local (Cap. 5, sección 5.2)", fontsize=12.5, pad=10)

legend_elements = [
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#fdf3e0", markeredgecolor="#b7791f", markersize=13, label="Entrada / salida"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#eaf0fb", markeredgecolor="#2c5282", markersize=13, label="Detección / máscara / inpainting"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#eaf7ea", markeredgecolor="#276749", markersize=13, label="Modelo (peso descargado)"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#fdeaea", markeredgecolor="#9b2c2c", markersize=13, label="Filtro de clase (decisión clave)"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="#f5eafd", markeredgecolor="#6b46c1", markersize=13, label="Output final"),
]
ax.legend(handles=legend_elements, loc="upper left", bbox_to_anchor=(0.0, 1.18), ncol=3, fontsize=8, framealpha=0.95)

fig.tight_layout()
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print("guardado:", OUT)
