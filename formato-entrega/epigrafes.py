"""
Epigrafes de los objetos que en los .md de 05-tesis no tenian ninguno.

Son descripciones factuales de lo que muestra cada imagen o tabla, escritas a
partir de la propia imagen y del texto que la rodea en el capitulo. No agregan
interpretacion ni conclusiones: describen el contenido para que la figura pueda
citarse y aparecer en la lista de figuras.

Viven aca y no en los .md para que quede explicito que son texto agregado en la
version de entrega, y para poder revisarlos o corregirlos en un solo lugar.

Claves:
  IMAGENES  -> nombre de archivo de la imagen, tal como se referencia en el .md
  TABLAS    -> "<carpeta del capitulo>|<primeras celdas de la fila de encabezado>"
"""

IMAGENES = {
    # ---------------------------------------------------------------- Cap. 2
    "image3.webp": (
        "Pipeline de fotogrametría SfM+MVS, de las imágenes de entrada a la nube de "
        "puntos densa: detección de puntos de interés con descriptores SIFT o SURF, "
        "emparejamiento de correspondencias entre pares de imágenes, estimación de la "
        "pose relativa de cada cámara con RANSAC, triangulación incremental o global y "
        "ajuste de haces (bundle adjustment); sobre la nube dispersa resultante, "
        "Multi-View Stereo produce la nube densa por correlación fotométrica entre "
        "vistas adyacentes. Elaboración propia a partir de Croce et al. (2024)"
    ),
    "image4.webp": (
        "Pipeline de NeRF, de las imágenes de entrada con poses conocidas a la síntesis "
        "de nuevas vistas: lanzamiento de un rayo por píxel, muestreo de puntos 3D a lo "
        "largo del rayo, predicción de color y densidad volumétrica mediante un MLP, "
        "renderizado volumétrico por integración a lo largo del rayo y optimización del "
        "modelo minimizando el error cuadrático medio contra la imagen real. "
        "Elaboración propia a partir de Mildenhall et al. (2020) y Croce et al. (2024)"
    ),
    "image2.webp": (
        "Pipeline de 3D Gaussian Splatting, de la nube dispersa de SfM al renderizado en "
        "tiempo real: inicialización de una gaussiana 3D por punto (posición, covarianza, "
        "opacidad y color codificado con armónicos esféricos), proyección sobre el plano "
        "de imagen, rasterización diferenciable en GPU, optimización iterativa por pérdida "
        "fotométrica y densificación adaptativa con clonado, división y poda de gaussianas. "
        "Elaboración propia a partir de Westover (1990, 1991), Kerbl et al. (2023), "
        "Chen y Wang (2024) y Lyu et al. (2025)"
    ),

    # ---------------------------------------------------------------- Cap. 3
    "image1.png": (
        "Línea de tiempo de la adopción del DJI Neo y del DJI Neo 2 en la literatura, "
        "entre 2025 y 2026: del lanzamiento del Neo 2 y los primeros usos en vigilancia, "
        "detección e inspección de pavimentos, al ortomosaico para navegación robótica de "
        "PathPainter y a la certificación EASA con la documentación técnica oficial"
    ),
    "image3.jpg": (
        "Esquema de recorrido de captura en tres bucles cerrados y concéntricos, a alturas "
        "crecientes alrededor de la obra, numerados de la más baja a la más alta"
    ),
    "image2.jpg": (
        "Esquema de recorrido de captura alternativo: un único bucle continuo que asciende "
        "en espiral alrededor de la obra, sin altura fija"
    ),

    # ---------------------------------------------------------------- Cap. 5
    "templete-central-sfm-2.gif": (
        "Templete Central, reconstrucción SfM en RealityScan: vista a nivel del suelo de la "
        "nube de puntos junto a las posiciones de cámara recuperadas del recorrido con DJI, "
        "que rodean el edificio en anillos a distinta altura"
    ),
    "2026-09-01-13-31-22-image.png": (
        "Templete Central, malla texturizada obtenida con RealityScan: vista cenital de la "
        "cubierta, donde se aprecian las discontinuidades —zonas sin geometría— sobre la "
        "losa superior"
    ),
    "2026-09-01-13-33-17-image.png": (
        "Templete Central, malla texturizada obtenida con RealityScan: vista desde el nivel "
        "del suelo, con las columnas, la losa nervurada y los carteles y rejas bajo la "
        "cubierta, junto a las posiciones de cámara del recorrido"
    ),
    "templete-central-sfm.gif": (
        "Templete Central, reconstrucción SfM en RealityScan: vista aérea de la nube de "
        "puntos y del anillo de posiciones de cámara que envuelve al edificio"
    ),
    "2026-09-01-13-54-22-image.png": (
        "Workflow de limpieza de distractores en ComfyUI: del dataset original de 1232 "
        "imágenes DJI a la detección y segmentación por instancia con YOLOv8-seg, el filtro "
        "de clases COCO person/bird/car, el inpainting con LaMa y el Dataset B curado"
    ),
    "2026-09-01-16-22-50-image.png": (
        "Panteón Asociación Catalana, nube de puntos densa en RealityScan: vista general del "
        "edificio con las posiciones de cámara del recorrido y la arboleda circundante "
        "reconstruida de forma dispersa"
    ),
    "2026-09-01-16-25-50-image.png": (
        "Panteón Asociación Catalana, nube de puntos densa en RealityScan: plano cercano "
        "sobre el frente, con los frontones ornamentados, la inscripción de la institución "
        "y las puertas de acceso"
    ),
    "2026-09-01-17-19-01-image.png": (
        "Panteón Asociación Catalana, dataset híbrido DJI + Insta360 en RealityScan: los dos "
        "componentes de reconstrucción que el software genera para el mismo edificio, "
        "superpuestos y a escalas distintas"
    ),
    "2026-09-01-17-22-11-image.png": (
        "Templete Central, dataset híbrido en RealityScan: primero de los dos componentes "
        "reconstruidos, con la mayor parte de los puntos sobre el terreno y apenas un "
        "fragmento del edificio resuelto"
    ),
    "2026-09-01-17-23-52-image.png": (
        "Templete Central, dataset híbrido en RealityScan: segundo componente reconstruido, "
        "con la losa y las columnas del templete resueltas y el recorrido de cámaras cerrado "
        "alrededor del edificio"
    ),
}

TABLAS = {
    "capitulo3_caso_de_estudio|Evidencia": (
        "Antecedentes académicos y técnicos del DJI Neo 2 y de sus modelos antecesores, "
        "por año y dominio de aplicación"
    ),
    "capitulo3_caso_de_estudio|Dispositivo": (
        "Parámetros de captura configurados en el DJI Neo 2: navegación manual, salida .mp4 "
        "a 60 fps, formato apaisado y relación de aspecto 16:9"
    ),
}


def para_imagen(src):
    """Descripcion para una imagen, buscada por nombre de archivo."""
    import os
    return IMAGENES.get(os.path.basename(str(src).replace("\\", "/")))


def para_tabla(chapter_dir, first_row):
    """Descripcion para una tabla, buscada por capitulo + primera celda del encabezado."""
    import re
    first = re.sub(r'[*`]', '', (first_row[0] if first_row else "")).strip()
    return TABLAS.get(f"{chapter_dir}|{first}")
