"""
Renderiza el turntable de un modelo de 07-modelado/ para usarlo como preview.gif
de su card en el Archivo Digital del sitio web.

Reusa la escena del .blend tal cual esta —camara, luz "PC sol", mundo "PC ambiente"
y materiales—, asi el resultado queda igual que los renders fijos de ese proyecto y
que los preview.gif de los otros dos sitios. Lo unico que se cambia es la posicion
de la camara, que gira 360 grados alrededor del edificio.

Para encuadrar se ignora el plano de piso (llega a +/-100 en X/Y y arruinaria el
centro y el radio); se usa solo la geometria del edificio.

Uso (desde Blender, en segundo plano):

    "C:\\Program Files\\Blender Foundation\\Blender 5.1\\blender.exe" -b <archivo.blend> ^
        -P render_turntable.py -- <cuadros> <muestras> <carpeta_salida>

Ejemplo real, el que genero el preview del Panteon (48 cuadros, ~4 s cada uno):

    blender.exe -b 07-modelado/03-panteon-asociacion-catalana/panteon_catalan_reconstruido.blend ^
        -P render_turntable.py -- 48 24 salida/

Y despues, para armar el .gif (4 fps, igual que los otros dos):

    ffmpeg -framerate 4 -i f%03d.png -vf "scale=480:-1:flags=lanczos,split[a][b];\\
        [a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=4" \\
        -loop 0 preview.gif
"""

import math
import os
import sys

import bpy
import mathutils

# el plano de piso de estas escenas se extiende hasta +/-100; el edificio es mucho
# mas chico. Todo lo que caiga fuera de este radio no cuenta para encuadrar.
LIMITE_PISO = 60.0

ANCHO, ALTO = 640, 480   # 4:3, la proporcion de la card en el Archivo Digital
DISTANCIA = 2.7      # radio de la orbita, en radios del edificio
ELEVACION = 1.05     # altura de la camara sobre el centro, idem
ANGULO_INICIAL = 215  # grados; arranca en una vista parecida a los renders fijos


def caja_del_edificio(escena):
    """Bounding box de la geometria visible, sin el plano de piso."""
    minimo = [float("inf")] * 3
    maximo = [float("-inf")] * 3
    for objeto in escena.objects:
        if objeto.type != "MESH" or not objeto.visible_get():
            continue
        for esquina in objeto.bound_box:
            punto = objeto.matrix_world @ mathutils.Vector(esquina)
            if abs(punto.x) > LIMITE_PISO or abs(punto.y) > LIMITE_PISO:
                continue
            for eje in range(3):
                minimo[eje] = min(minimo[eje], punto[eje])
                maximo[eje] = max(maximo[eje], punto[eje])
    centro = mathutils.Vector([(minimo[i] + maximo[i]) / 2 for i in range(3)])
    radio = max(maximo[i] - minimo[i] for i in range(3)) / 2
    return centro, radio


def usar_gpu(escena):
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        prefs.get_devices()
        for dispositivo in prefs.devices:
            dispositivo.use = dispositivo.type != "CPU"
        escena.cycles.device = "GPU"
    except Exception as error:                                   # noqa: BLE001
        print("Sin GPU, se renderiza por CPU:", error)


def main():
    argumentos = sys.argv[sys.argv.index("--") + 1:]
    cuadros = int(argumentos[0])
    muestras = int(argumentos[1])
    salida = argumentos[2]

    escena = bpy.context.scene
    escena.render.resolution_x, escena.render.resolution_y = ANCHO, ALTO
    escena.render.resolution_percentage = 100
    escena.render.film_transparent = False
    escena.cycles.samples = muestras
    escena.cycles.use_denoising = True
    usar_gpu(escena)

    centro, radio = caja_del_edificio(escena)
    print(f"CENTRO {[round(v, 2) for v in centro]}  RADIO {radio:.2f}")

    # la camara mira siempre al edificio, un poco por encima de su centro
    objetivo = bpy.data.objects.new("PC objetivo turntable", None)
    escena.collection.objects.link(objetivo)
    objetivo.location = centro + mathutils.Vector((0, 0, radio * 0.12))

    camara = escena.camera
    for restriccion in list(camara.constraints):
        camara.constraints.remove(restriccion)
    seguir = camara.constraints.new("TRACK_TO")
    seguir.target = objetivo
    seguir.track_axis = "TRACK_NEGATIVE_Z"
    seguir.up_axis = "UP_Y"

    # el encuadre se ajusta a la altura, no al ancho: el edificio es mas alto que
    # ancho y con el ajuste automatico (que usa el lado mayor) al pasar a 4:3 se
    # perdian la base y la escalera.
    camara.data.sensor_fit = "VERTICAL"

    orbita = radio * DISTANCIA
    altura = centro.z + radio * ELEVACION
    os.makedirs(salida, exist_ok=True)
    for indice in range(cuadros):
        angulo = 2 * math.pi * indice / cuadros + math.radians(ANGULO_INICIAL)
        camara.location = (
            centro.x + orbita * math.cos(angulo),
            centro.y + orbita * math.sin(angulo),
            altura,
        )
        escena.render.filepath = os.path.join(salida, f"f{indice:03d}.png")
        bpy.ops.render.render(write_still=True)
        print("CUADRO", indice, "listo")


if __name__ == "__main__":
    main()
