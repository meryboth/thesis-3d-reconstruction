"""
Diagrama de arquitectura del experimento de reconstruccion geometrica
asistida por agente de IA (Capitulo 6, seccion 6.3.4): que entra, que
herramientas intervienen, que hace el agente y que sale -- complementa
las capturas de proceso y la Tabla 6.4 (que muestran el "como se ve" y
"que tan ajustado quedo") con el "como esta armado" el experimento.

Mismos helpers y convenciones visuales que build_pipeline_diagram.py
para que ambos diagramas del capitulo se lean como parte de un mismo
lenguaje grafico. Todas las flechas van de borde de caja a borde de
caja, ruteadas para no atravesar ningun nodo por encima.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = r"C:\nerfstudio_work\thesis\05-tesis\capitulo6_pipeline_definitivo\media\mcp-arquitectura.png"

fig, ax = plt.subplots(figsize=(12.4, 13.4))
ax.set_xlim(-3.1, 11.4)
ax.set_ylim(-0.6, 15.4)
ax.axis("off")


def box(x, y, w, h, text, color="#e8eef7", edge="#2c5282", fontsize=9.2,
        textcolor="black", dashed=False):
    ls = "dashed" if dashed else "solid"
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.07,rounding_size=0.1",
                        linewidth=1.5, edgecolor=edge, facecolor=color, linestyle=ls)
    ax.add_patch(b)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize,
            color=textcolor, linespacing=1.5)


def arrow(x1, y1, x2, y2, color="#2c5282", lw=1.6, connectionstyle="arc3,rad=0", style="-|>"):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=14,
                         color=color, linewidth=lw, connectionstyle=connectionstyle)
    ax.add_patch(a)


def label(x, y, text, fontsize=10.5, color="#2c5282", style="normal", ha="center", mask=False):
    # mask=True pone un fondo blanco detras del texto para que una linea que
    # pase por debajo (p.ej. la flecha de fusion de inputs) no lo atraviese
    # visualmente -- el texto "tapa" el tramo de linea, en vez de cruzarlo
    bbox = dict(facecolor="white", edgecolor="none", pad=3) if mask else None
    ax.text(x, y, text, ha=ha, va="center", fontsize=fontsize, color=color, style=style,
            bbox=bbox, zorder=7)


# ---------------------------------------------------------------------
# Iconos -- badges circulares en la esquina superior izquierda de cada
# caja, con un glifo vectorial simple (sin depender de fuentes emoji ni
# de assets externos) que da una pista visual del tipo de nodo: nube de
# puntos, malla, imagen, LLM, terminal, servidor, cubo 3D, calibre y
# archivo exportado. Mismo estilo de trazo que las flechas del diagrama.
# ---------------------------------------------------------------------
def icon_pointcloud(cx, cy, s, color):
    pts = [(-0.6, 0.5), (-0.2, 0.7), (0.3, 0.6), (0.6, 0.2), (0.5, -0.3),
           (0.1, -0.6), (-0.4, -0.5), (-0.7, -0.1), (0.0, 0.1), (-0.3, 0.2),
           (0.3, -0.1), (0.15, 0.35)]
    for dx, dy in pts:
        ax.add_patch(plt.Circle((cx + dx * s, cy + dy * s), s * 0.11,
                                 facecolor=color, edgecolor="none", zorder=6))


def icon_mesh(cx, cy, s, color):
    pts = {"a": (-0.6, -0.5), "b": (0.0, -0.6), "c": (0.6, -0.5),
           "d": (-0.35, 0.1), "e": (0.25, 0.15), "f": (-0.05, 0.65)}
    edges = [("a", "b"), ("b", "c"), ("a", "d"), ("b", "d"), ("b", "e"),
             ("c", "e"), ("d", "e"), ("d", "f"), ("e", "f")]
    for u, v in edges:
        x1, y1 = pts[u]
        x2, y2 = pts[v]
        ax.plot([cx + x1 * s, cx + x2 * s], [cy + y1 * s, cy + y2 * s],
                color=color, linewidth=1.1, zorder=6)


def icon_image(cx, cy, s, color):
    ax.add_patch(plt.Rectangle((cx - 0.7 * s, cy - 0.55 * s), 1.4 * s, 1.1 * s,
                                fill=False, edgecolor=color, linewidth=1.2, zorder=6))
    ax.add_patch(plt.Circle((cx - 0.35 * s, cy + 0.2 * s), 0.13 * s,
                             facecolor=color, edgecolor="none", zorder=6))
    ax.plot([cx - 0.6 * s, cx - 0.1 * s, cx + 0.15 * s, cx + 0.65 * s],
            [cy - 0.4 * s, cy + 0.1 * s, cy - 0.1 * s, cy + 0.35 * s],
            color=color, linewidth=1.2, zorder=6)


def icon_llm(cx, cy, s, color):
    ax.add_patch(FancyBboxPatch((cx - 0.45 * s, cy - 0.45 * s), 0.9 * s, 0.9 * s,
                                 boxstyle="round,pad=0,rounding_size=0.08",
                                 linewidth=1.2, edgecolor=color, facecolor="none", zorder=6))
    for x in (-0.25, 0.0, 0.25):
        ax.plot([cx + x * s, cx + x * s], [cy + 0.45 * s, cy + 0.62 * s], color=color, linewidth=1.1, zorder=6)
        ax.plot([cx + x * s, cx + x * s], [cy - 0.45 * s, cy - 0.62 * s], color=color, linewidth=1.1, zorder=6)
    for y in (-0.25, 0.0, 0.25):
        ax.plot([cx + 0.45 * s, cx + 0.62 * s], [cy + y * s, cy + y * s], color=color, linewidth=1.1, zorder=6)
        ax.plot([cx - 0.45 * s, cx - 0.62 * s], [cy + y * s, cy + y * s], color=color, linewidth=1.1, zorder=6)
    ax.add_patch(plt.Circle((cx, cy), 0.13 * s, facecolor=color, edgecolor="none", zorder=6))


def icon_terminal(cx, cy, s, color):
    ax.add_patch(FancyBboxPatch((cx - 0.65 * s, cy - 0.5 * s), 1.3 * s, 1.0 * s,
                                 boxstyle="round,pad=0,rounding_size=0.06",
                                 linewidth=1.2, edgecolor=color, facecolor="none", zorder=6))
    ax.plot([cx - 0.4 * s, cx - 0.1 * s, cx - 0.4 * s], [cy + 0.15 * s, cy, cy - 0.15 * s],
            color=color, linewidth=1.3, zorder=6)
    ax.plot([cx + 0.0 * s, cx + 0.35 * s], [cy - 0.2 * s, cy - 0.2 * s], color=color, linewidth=1.3, zorder=6)


def icon_server(cx, cy, s, color):
    for dy in (-0.35, 0.05, 0.45):
        ax.add_patch(plt.Rectangle((cx - 0.6 * s, cy + dy * s - 0.15 * s), 1.2 * s, 0.3 * s,
                                    fill=False, edgecolor=color, linewidth=1.1, zorder=6))
        ax.add_patch(plt.Circle((cx + 0.4 * s, cy + dy * s), 0.045 * s, facecolor=color, edgecolor="none", zorder=6))


def icon_cube(cx, cy, s, color):
    top = [(-0.5, 0.15), (0.0, 0.4), (0.5, 0.15), (0.0, -0.1)]
    bot = [(x, y - 0.45) for x, y in top]

    def poly(pts):
        xs = [cx + p[0] * s for p in pts] + [cx + pts[0][0] * s]
        ys = [cy + p[1] * s for p in pts] + [cy + pts[0][1] * s]
        ax.plot(xs, ys, color=color, linewidth=1.1, zorder=6)

    poly(top)
    poly(bot)
    for (tx, ty), (bx, by) in zip(top, bot):
        ax.plot([cx + tx * s, cx + bx * s], [cy + ty * s, cy + by * s], color=color, linewidth=1.1, zorder=6)


def icon_ruler(cx, cy, s, color):
    ax.plot([cx - 0.65 * s, cx + 0.65 * s], [cy, cy], color=color, linewidth=1.4, zorder=6)
    for x in (-0.65, -0.33, 0.0, 0.33, 0.65):
        h = (0.24 if x in (-0.65, 0.65) else 0.13) * s
        ax.plot([cx + x * s, cx + x * s], [cy - h, cy + h], color=color, linewidth=1.2, zorder=6)


def icon_export(cx, cy, s, color):
    ax.add_patch(plt.Rectangle((cx - 0.5 * s, cy - 0.55 * s), 0.75 * s, 1.1 * s,
                                fill=False, edgecolor=color, linewidth=1.2, zorder=6))
    ax.plot([cx - 0.15 * s, cx + 0.55 * s], [cy, cy], color=color, linewidth=1.3, zorder=6)
    ax.plot([cx + 0.3 * s, cx + 0.55 * s, cx + 0.3 * s], [cy + 0.2 * s, cy, cy - 0.2 * s],
            color=color, linewidth=1.3, zorder=6)


def icon_check(cx, cy, s, color):
    ax.add_patch(plt.Circle((cx, cy), 0.62 * s, fill=False, edgecolor=color, linewidth=1.3, zorder=6))
    ax.plot([cx - 0.28 * s, cx - 0.05 * s, cx + 0.35 * s], [cy - 0.02 * s, cy - 0.3 * s, cy + 0.3 * s],
            color=color, linewidth=1.6, zorder=6)


def badge(box_x, box_y, box_h, kind, edge_color, r=0.32):
    cx, cy = box_x, box_y + box_h
    ax.add_patch(plt.Circle((cx, cy), r, facecolor=edge_color, edgecolor="white", linewidth=1.3, zorder=5))
    kind(cx, cy, r * 0.9, "white")


# ---------------------------------------------------------------------
# INPUTS (fila superior)
# ---------------------------------------------------------------------
label(4.55, 15.1, "INPUTS")

box(0.0, 13.3, 3.1, 1.35,
    "Nube densa SfM\n(RealityScan)\nmisma fuente que el\nresto del capitulo",
    color="#eaf0fb", edge="#2c5282")
badge(0.0, 13.3, 1.35, icon_pointcloud, "#2c5282")

box(3.45, 13.3, 3.1, 1.35,
    "Malla Poisson\nsolo referencia visual\n(sus artefactos no pasan\nal modelo final)",
    color="#f7f7f7", edge="#718096", dashed=True)
badge(3.45, 13.3, 1.35, icon_mesh, "#718096")

box(6.9, 13.3, 3.1, 1.35,
    "Dataset original\nde imagenes\npara consultar detalle y\nvalidar visualmente",
    color="#eaf0fb", edge="#2c5282")
badge(6.9, 13.3, 1.35, icon_image, "#2c5282")

CODEX_CX = 3.55 + 2.85 / 2  # 4.975 -- los 3 inputs convergen en Codex, no en
                             # cada columna por separado: es Codex quien tiene
                             # acceso a los archivos y arma el contexto antes
                             # de invocar al modelo, no el LLM ni Blender MCP
arrow(1.55, 13.3, 1.55, 12.75, style="-", lw=1.3)
arrow(5.0, 13.3, 5.0, 12.75, color="#718096", style="-", lw=1.3)
arrow(8.45, 13.3, 8.45, 12.75, style="-", lw=1.3)
arrow(1.55, 12.75, 8.45, 12.75, style="-", lw=1.3)
arrow(CODEX_CX, 12.75, CODEX_CX, 11.5)
label(6.6, 12.45, "los 3 inputs entran por Codex\n(orquestador con acceso a los archivos)",
      fontsize=7.6, color="#2c5282", style="italic", ha="left")

# ---------------------------------------------------------------------
# CADENA DE HERRAMIENTAS (agente -> orquestador -> MCP -> Blender)
# ---------------------------------------------------------------------
label(4.55, 11.9, "AGENTE Y CADENA DE HERRAMIENTAS", mask=True)

box(0.0, 10.1, 2.85, 1.4, "GPT-6 Astra\n(OpenAI)\nrazona sobre\nla geometria",
    color="#fdf2e9", edge="#c9702e", fontsize=8.8)
badge(0.0, 10.1, 1.4, icon_llm, "#c9702e")
arrow(2.85, 10.8, 3.55, 10.8, style="<|-|>")

box(3.55, 10.1, 2.85, 1.4, "Codex\norquesta la sesion,\nejecuta el agente",
    color="#fdf2e9", edge="#c9702e", fontsize=8.8)
badge(3.55, 10.1, 1.4, icon_terminal, "#c9702e")
arrow(6.4, 10.8, 7.1, 10.8)

box(7.1, 10.1, 2.85, 1.4, "Blender MCP\nservidor MCP -- expone\nla API de Python\nde Blender",
    color="#fdf2e9", edge="#c9702e", fontsize=8.8)
badge(7.1, 10.1, 1.4, icon_server, "#c9702e")

arrow(8.525, 10.1, 8.525, 9.1)

box(6.4, 7.35, 4.0, 1.4, "Blender\nejecuta las operaciones:\ncrea/ajusta objetos y\nmateriales, renderiza\nvistas de control",
    color="#eaf0fb", edge="#2c5282", fontsize=8.8)
badge(6.4, 7.35, 1.4, icon_cube, "#2c5282")

# ---------------------------------------------------------------------
# QUE HACE EL AGENTE (detalle del ajuste)
# ---------------------------------------------------------------------
label(4.55, 6.65, "QUE AJUSTA EL AGENTE", color="#2f855a")
label(4.55, 6.2, "(geometria parametrica explicita sobre la nube, no una malla libre)",
      fontsize=8.6, color="#4a5568", style="italic")

box(0.0, 3.6, 5.4, 2.25,
    "Columnas: circunferencia en 9\ncortes de altura; radio final =\nmediana de los cortes; recta\npara el desplazamiento\nde los centros.\n\n"
    "Cubiertas: orientacion por\nrectangulo envolvente robusto;\ngrilla 34x34; superficie suave\npor cuantiles de altura\n(0,18 / 0,82) por celda.",
    color="#eefbf3", edge="#2f855a", fontsize=8.4)
badge(0.0, 3.6, 2.25, icon_ruler, "#2f855a")

arrow(6.4, 7.35, 5.5, 5.1, color="#2c5282")

# flecha de insumo: nube de entrada baja directo a la caja verde, por el
# margen izquierdo, sin cruzar ninguna caja de la cadena de herramientas
arrow(0.0, 13.95, -2.3, 13.95, color="#2c5282", lw=1.3, style="-")
arrow(-2.3, 13.95, -2.3, 4.7, color="#2c5282", lw=1.3, style="-")
arrow(-2.3, 4.7, 0.0, 4.7, color="#2c5282", lw=1.3)
label(-2.55, 9.3, "geometria de partida\n(misma nube de entrada)",
      fontsize=8.0, color="#2c5282", ha="right")

# ---------------------------------------------------------------------
# OUTPUT
# ---------------------------------------------------------------------
label(8.55, 3.0, "OUTPUT")

box(6.4, 1.35, 4.0, 1.4,
    "Escena .blend + export .glb\nobjetos separados por pieza\n(columnas, cubiertas),\nmateriales de interpretacion visual",
    color="#eaf0fb", edge="#2c5282", fontsize=8.6)
badge(6.4, 1.35, 1.4, icon_export, "#2c5282")

arrow(5.4, 4.2, 6.4, 2.4, color="#2c5282")

# ---------------------------------------------------------------------
# VERIFICACION (franja inferior, ancho completo, sin cruzar el output)
# ---------------------------------------------------------------------
box(-2.7, -0.5, 8.7, 1.5,
    "Verificacion: distancia punto-a-superficie\ndel .glb contra la MISMA nube de entrada\n"
    "(verificacion_modelo.json -- mediana / p95,\nTabla 6.4). No es validacion independiente:\n"
    "confirma ajuste a los datos, no precision\nmetrica frente a la obra real.",
    color="#fff5f5", edge="#c53030", fontsize=8.3)
badge(-2.7, -0.5, 1.5, icon_check, "#c53030")

arrow(6.4, 0.25, 6.0, 0.25, color="#c53030")

plt.tight_layout()
plt.savefig(OUT, dpi=200, bbox_inches="tight")
print("guardado:", OUT)
