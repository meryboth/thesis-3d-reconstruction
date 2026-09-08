# Templete Central — modelo geométrico documentado

Reconstrucción interpretativa realizada en Blender mediante MCP a partir de la nube densa RealityScan y fotografías del dataset DJI.

## Archivos

- `templete_central_reconstruido.blend`: modelo editable, materiales procedurales, cámaras y nubes de referencia en una colección oculta. Abrir la escena `Templete Central | modelo documentado`.
- `templete_central_reconstruido.glb`: únicamente arquitectura y detalles, con colores base portables. Las texturas procedurales de Blender no están horneadas en este archivo.
- `templete_perspectiva.png`: render general.
- `templete_vista_acceso.png`: render desde una cámara más baja.
- `referencias_dji.jpg`, `referencia_cubierta.jpg`, `referencia_accesos.jpg`: vistas fotográficas utilizadas para interpretar la obra.
- `proyecciones_nube.jpg`: planta y alzados de una región central de la nube, usados durante la inspección inicial.
- `referencia_densa_muestreada.ply`, `nube_muestreada.npy`: muestra determinista de la nube (una fila de cada 24; 737.007 puntos). El PLY conserva las coordenadas originales; la transformación está guardada en el JSON y aplicada al objeto de Blender.
- `parametros_ajuste.json`: orientación, traslación, dimensiones de columnas, pendientes de fachadas y cotas principales.
- `verificacion_modelo.json`: comprobación de topología y comparación de la cubierta contra 10.000 puntos de la nube utilizada como referencia.
- `reconstruir_templete_blender.py`: generador para ejecutar con Python de Blender en un archivo nuevo. Lee el JSON de esta carpeta e importa el PLY muestreado; crea estructura, detalles y escena de presentación. Para ejecución mediante `exec`, usar el mismo diccionario para globals y locals. El script guarda el `.blend`; el render y la exportación GLB se hicieron después durante la sesión MCP.

## Capturas del proceso

1. `proceso/01_nube_densa_alineada.png`: nube importada y orientada para modelar.
2. `proceso/02_estructura_ajustada.png`: losa, seis columnas y cuatro frentes inclinados, antes de añadir relieves y accesos.
3. `proceso/03_superposicion_nube_modelo.png`: recorte de la nube en naranja y geometría reconstruida en alambre. Permite inspeccionar la coincidencia de la envolvente.
4. `proceso/04_modelo_con_relieves_y_accesos.png`: geometría con detalles interpretados de las fotografías.

5. `proceso/05_modelo_final_blender.png`: escena final revisada.

Estas capturas registran etapas reales del trabajo. No son imágenes sintéticas de un proceso inexistente.

## Referencias y ajuste

Fuente: `../../02-templete-central/02-resultados-finales/dji/colmap-fotogrametria/nube-densa.xyz` (17.688.149 puntos según los metadatos existentes). Fotografías: `../../02-templete-central/03-datasets/dji/dataset-splatfacto-1232-full/images/`. Preparación de referencias: `../../04-notebooks/scripts/preparar_templete_modelado.py`.

Se orientó la nube por el rectángulo envolvente robusto de los puntos altos. Se identificaron seis grupos correspondientes a columnas y se estimaron sus envolventes en cortes entre z=1,75 y z=2,3. Los dos grupos planos restantes correspondían a elementos delgados, no a columnas, y no se incorporaron como soportes.

Se ajustaron cuatro planos inclinados con ponderación robusta y se estimaron las cotas de la cara inferior y superior de la losa mediante medianas de puntos. La coronación se regularizó en z=4,08. El modelo conserva pequeñas diferencias entre las pendientes observadas de las cuatro caras.

## Límites de interpretación

- **Unidades de reconstrucción; escala métrica no verificada.** No interpretar automáticamente los valores del `.blend` o `.glb` como metros.
- El volumen principal y las seis columnas se apoyan en los puntos. Los relieves se reproducen como un patrón geométrico simplificado de ranuras, basado en fotos, no como un relevamiento exacto de cada motivo.
- Las barandas, muretes, pasarelas y escaleras son una interpretación de las imágenes. En particular, la nube no cubre la profundidad completa de los accesos subterráneos: la cantidad de peldaños, su profundidad y las cotas bajo suelo son supuestos de modelado, no mediciones.
- No se modelaron carteles, vallas temporales de obra, instalaciones internas, cimentaciones ni el entorno del cementerio. El suelo exterior es de presentación.
- Se revisaron 196 objetos arquitectónicos: no se detectaron aristas no manifold. Son piezas separadas; sus encuentros no constituyen un sólido booleano único.
- La comparación de distancias contra la nube usada para el ajuste no es validación independiente ni acredita precisión métrica. Ver valores y muestra en `verificacion_modelo.json`.
- Los originales de las carpetas crudas y los capítulos de la tesis no fueron modificados.
