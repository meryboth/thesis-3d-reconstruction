Este capítulo contiene los resultados de los experimentos de esta tesis y sus respectivos análisis, algunos validan las hipótesis planteadas al comienzo de esta investigación y otros la refutan. A continuación voy a enumerar los benchmarks que vamos a estar analizando con el fin de comparar estos resultados con lo esperado:

- B1 - Plantea una comparativa de las tres técnicas (fotogrametría, NeRF y 3DGS) con el fin de identificar ventajas y desventajas de cada uno de estos algoritmos

- B2 - Busca identificar el impacto del preprocesamiento del dataset utilizando dos técnicas distintas, por un lado una que solo elimina distractores y por otro lado otra más invasiva que elimina el contexto de los edificios

- B3 - Analiza el impacto de las técnicas de cara a la reconstrucción de distinta complejidad geométrica. 

- B4 - Analiza el impacto de utilizar múltiples dispositivos con el fin de generar un dataset diverso multi-cámara. 

- B5 - Valida la compatibilidad con formatos web de los outputs de cada uno de los resultados. 

Como está planteado en el Capítulo 1, el objetivo de estos experimentos tiene un fin en común: identificar el mejor pipeline para reconstruir tridimensionalmente edificios a partir de imágenes y colaborar en la integración de estos resultados con un flujo de reconstrucción HBIM y un potencial archivo digital compatible con web. 

<h2 id="cap5-5-1">5.1 Resumen de los benchmarks</h2>

Antes de profundizar en el detalle de los resultados de cada benchmark, la siguiente tabla (Tabla 5.1), resume la ejecución de cada una de estas pruebas y detalla el edificio en el cual se ejecutó y el dataset que se utilizó para las pruebas.

| Benchmark                          | Hipótesis | Estado                                                                                                                                                                                 | Casos cubiertos                                             |
| ---------------------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| B1 — Técnicas (caso de referencia) | H1        | Ejecutado (SfM, NeRF, 3DGS)                                                                                                                                                            | Templete Central, dataset DJI                               |
| B2 — Preprocesamiento              | H2        | Ejecutado (dataset curado + comparación de reconstrucción 1:1 para ambas técnicas)                                                                                                     | Templete Central, dataset DJI                               |
| B3 — Complejidad geométrica        | H3        | Ejecutado (NeRF, 3DGS; SfM cualitativo)                                                                                                                                                | Los Paraguas, Templete Central, Panteón Asociación Española |
| B4 — Dataset multi-dispositivo     | H4        | Ejecutado (SfM + reconstrucción completa sobre Templete Central **y** Panteón Asociación Española); cobertura reconstruida (%) pendiente por falta de referencia geométrica de control | Templete Central, Panteón Asociación Española               |
| B5 — Web y reproducibilidad        | H5        | Checklist documental completo; carga real en visor pendiente                                                                                                                           | Los tres casos (evaluación de formatos)                     |

*Tabla 5.1 — Estado de ejecución de los cinco benchmarks al cierre de esta tesis.*

<h2 id="cap5-5-2">5.2 B1 — Técnicas sobre el caso de referencia: Templete Central (H1)</h2>

<h3 id="cap5-5-2-1">5.2.1 Métricas cuantitativas</h3>

El objetivo de este benchmark es identificar cómo performa cada una de las técnicas relevadas (SfM, NeRF y 3DGS) sobre un mismo caso de estudio: El templete central del Sexto Panteón de Chacarita. Para este relevamiento se utilizó un dataset obtenido con el drone DJI Neo 2. La siguiente tabla (Tabla 5.2) expresa el análisis de los resultados utilizando las siguientes variables:

**PSNR (Peak Signal-to-Noise Ratio):** Crea una comparativa pixel a pixel entre el render del output y la imagen del dataset con el fin de medir en decibelios la coincidencia. Cuanto más alto sea el valor más fiel es la reconstrucción. 

**SSIM (Structural Similarity Index Measure):** Esta técnica lo que hace es comparar parámetros como luminancia, contraste y estructura (patrones de bordes, texturas). Cuanto más cerca de 1 será el resultado mayor es la coincidencia. 

**LPIPS (Learned Perceptual Image Patch Similarity):** Esta técnica de comparación usa una red neuronal ya entrenada que se parece mucho a como una persona interpretaría la imagen, puede por ejemplo identificar si una reconstrucción 'se ve mal'. Este índice es contrario a los anteriores y refleja mayor similitud en su cercanía con el valor de 0. 

**Tiempo de entrenamiento:** Esta variable es fundamental para entender los costos de correr cada procesamiento y empezar a dimensionar el impacto que puede tener en un posterior plan de generación de un archivo digital de obras locales. Aquellos procesamientos que duren menos tiempo serán ponderados con el fin de obtener un pipeline que sea reproducible. 

**Peso del output:** El peso de los archivos que se generan como resultado tiene como finalidad medir si es viable o no subir en una plataforma o en algún archivo digital los resultados. Aquellos archivos que pesen menos serán ponderados por sobre los más pesados. 

Antes de avanzar con el análisis del benchmark es importante entender que el output del proceso de SfM no es comparable en tres variables con NeRF y 3DGS, las tres primeras variables corren sobre videos renderizados como resultados de estos procesamientos, y la técnica de SfM no es renderizable ya que su output es una nube de puntos densa y una malla texturizada. Esto no afecta la validación del benchmark porque podemos comparar las técnicas también desde un enfoque cualitativo y no solo cuantitativo a partir de las métricas, por lo tanto compensamos el análisis de SfM evaluando directamente los resultados del procesamiento a nivel cualitativo. 

| Técnica                              | PSNR (dB)                                | SSIM  | LPIPS | Tiempo de entrenamiento                           | Peso del output                                 |
| ------------------------------------ | ---------------------------------------- | ----- | ----- | ------------------------------------------------- | ----------------------------------------------- |
| SfM (RealityScan, malla texturizada) | *(sin PSNR/SSIM comparable — ver 5.2.3)* | —     | —     | *(etapa de SfM, no reportada como entrenamiento)* | 3 934,3 MB (.obj) + 62,4 MB (textura 8192×8192) |
| Nerfacto (NeRF)                      | 19,466                                   | 0,602 | 0,323 | 46 min 1 s                                        | 167,9 MB (checkpoint)                           |
| Splatfacto (3DGS)                    | 23,575                                   | 0,756 | 0,336 | 33 min 41 s                                       | 74,7 MB (splat.ply, 315 787 gaussianas)         |

*Tabla 5.2 — B1, resultados cuantitativos sobre el caso de referencia (Templete Central, dataset DJI). Fuente: `analyze_render_benchmark.py`, `analyze_processing_time.py`, `analyze_output_weights.py`, `analyze_gaussian_splats.py`.*

![Comparación Foto original / Nerfacto / Splatfacto — Templete Central, DJI, fotograma inicial](/content/assets/cap5-comparacion-00000.jpg)

*Figura 5.1 — Primer fotograma de la grilla comparativa (recorrido DJI del Templete Central), vista frontal desde el camino de acceso. Splatfacto reproduce con nitidez la cubierta, las columnas y la textura del solado de piedra; Nerfacto muestra un suavizado algo mayor en esas mismas zonas, sin perder la geometría general.*

![Comparación Foto / Nerfacto / Splatfacto — Templete Central, DJI, otro fotograma](/content/assets/cap5-comparacion-00292.jpg)

*Figura 5.2 — Segundo fotograma de la grilla, vista completa del edificio desde otro punto del camino de acceso. El patrón de la Figura 5.1 se sostiene: ambas técnicas reproducen fielmente la geometría, con Splatfacto algo más nítido en los bordes de mayor contraste.*

![Renders comparativos Foto / Nerfacto / Splatfacto — Templete Central, DJI](/content/assets/cap5-comparacion-00608.jpg)

*Figura 5.3 — Tercer fotograma de la grilla, plano más cercano sobre la losa y las columnas. Ambas técnicas reproducen correctamente la losa, las columnas y el detalle de las nervaduras de hormigón; el render de Splatfacto conserva bordes ligeramente más nítidos que el de Nerfacto.*

![Comparación Foto / Nerfacto / Splatfacto — Templete Central, DJI, vista elevada con ghosting en Splatfacto](/content/assets/cap5-comparacion-00924.jpg)

*Figura 5.4 — Cuarto fotograma de la grilla, vista elevada del edificio. Es la excepción del conjunto: Splatfacto presenta una franja de ghosting horizontal a la altura del horizonte, un artefacto localizado ausente en el render de Nerfacto sobre la misma vista.*

![Comparación Foto / Nerfacto / Splatfacto — Templete Central, DJI, quinto fotograma](/content/assets/cap5-comparacion-01228.jpg)

*Figura 5.5 — Quinto y último fotograma de la grilla, vista similar a la Figura 5.1 con peatones en el encuadre. Se sostiene el mismo patrón general: Splatfacto reproduce bordes y texturas con mayor nitidez, Nerfacto con un suavizado algo mayor en esas mismas zonas.*

Las Figuras 5.1 a 5.5 son los cinco fotogramas analizados por el script `build_fidelity_comparisons.py`.

La Tabla 5.2 ya adelanta la magnitud del export de Splatfacto (315 787 gaussianas). El Gráfico 5.1 caracteriza esa nube de gaussianas: casi dos tercios (64,6%) tiene opacidad estimada por encima de 0,5, y solo un 7,3% está por debajo de 0,05 (gaussianas casi transparentes, ya vemos un resultado candidato a limpieza en SuperSplat por la cantidad de gaussianas que conforman el contexto del edificio y no solo la reproducción del mismo).

![Distribución de opacidad de las gaussianas — Templete Central, DJI, Splatfacto](/content/assets/cap5-gaussian-splat-opacity-histogram.png)

*Gráfico 5.1 — Distribución de opacidad estimada de las 315 787 gaussianas exportadas para el Templete Central (dataset DJI). Fuente: `analyze_gaussian_splats.py`.*

![Distribución espacial de las gaussianas — Templete Central, DJI, Splatfacto](/content/assets/cap5-gaussian-splat-spatial-scatter.png)

*Gráfico 5.2 — Distribución espacial (proyecciones XY/XZ) de las gaussianas exportadas para el Templete Central. A diferencia de la nube de puntos densa de SfM (Gráfico 5.9), aquí no se distingue una silueta arquitectónica nítida: se observa un núcleo denso concentrado cerca del origen (la escena registrada) rodeado por un halo disperso de gaussianas de baja densidad que se extiende varias veces el tamaño del objeto — candidatas, junto con las de opacidad casi nula del Gráfico 5.1, a la limpieza de outliers en SuperSplat mencionada en el Capítulo 6 (sección 6.2.5).*

Podemos concluir en que Splatfacto supera a Nerfacto en PSNR (+4,1 dB) y SSIM (+0,154), y lo hace en el 73% del tiempo de entrenamiento y con un archivo 2,25 veces más liviano — un patrón de eficiencia que se repite, con distinta magnitud, en los otros dos casos de estudio (sección 5.4). El único indicador donde Nerfacto iguala a Splatfacto es LPIPS (0,323 vs. 0,336, prácticamente empatados), lo que sugiere que, aunque Splatfacto reconstruye con mayor fidelidad píxel a píxel (PSNR/SSIM), la distancia perceptual entre ambos métodos es menor de lo que el PSNR por sí solo indicaría.

<h3 id="cap5-5-2-2">5.2.2 Fidelidad geométrica — Nerfacto vs. Splatfacto vs. SfM</h3>

A simple vista los resultados de NeRF y 3DGS son bastante similares y ambos logran representar con éxito la geometría y los aspectos esenciales de la materialidad. En al menos 4 de 5 fotogramas se pueden visualizar que ambas técnicas logran reproducir con éxito la interpretación de la losa en voladizo y las molduras de la misma, siendo un detalle de su materialidad que logra una correcta interpretación. Hay un caso interesante y es la presencia de una mancha en una captura de 3DGS (Figura 5.4). Lo que se puede ver en la imagen suele denominarse ghosting y es la presencia de zonas borradas o tapadas por otros gaussianos que se anteponen a la captura de la cámara en ese punto de vista (también llamado floaters por su naturaleza de estar suspendidos y no adosados directamente a la geometría principal). A pesar de este error puntual se puede concluir en que 3DGS es la técnica más sólida en cuanto a la reconstrucción y logra los resultados más nítidos al momento de representar materialidad. 

Como última instancia vamos a comparar los resultados de SfM, el video/gif a continuación contiene una animación del recorrido generado por el procesamiento, donde no solo puede visualizarse la nube de puntos sino también el camino establecido por las imágenes y sus posicionamientos. Como puede verse en la animación SfM logró una representación fiel del edificio y también puede visualizarse con detalle las reproducciones de su geometría y su materialidad. En general la captura es fiel a la obra y solo pueden identificarse defectos menores como la ausencia de puntos en algunas zonas de la cubierta, un defecto que puede estar relacionado con la presencia de sombras específicas al momento de la captura que pueden haber sido identificadas como vacíos.

![templete-central-sfm-2.gif](/content/assets/cap5-templete-central-sfm-2.gif)

<h3 id="cap5-5-2-3">5.2.3 SfM — Malla texturizada y potencial de integración BIM</h3>

La malla texturizada obtenida con RealityScan para el Templete Central tiene 17 688 149 vértices y 35 376 582 triángulos, con una textura única de 8192×8192 px (62,4 MB). Su geometría es consistente, a excepción de estos defectos mencionados en la sección anterior donde se identifican ausencias de continuidad en la cubierta. 

![](/content/assets/cap5-2026-09-01-13-31-22-image.png)

![](/content/assets/cap5-2026-09-01-13-33-17-image.png)

Como mencionamos con anterioridad, el output de SfM no puede ser comparable con NeRF y 3DGS por lo tanto su evaluación en este benchmark está orientada a cualidades visuales que podamos identificar a simple vista. Podemos afirmar que la interpretación de SfM dio como resultado una geometría explícita, que su materialidad asignada se corresponde visualmente con lo capturado en el dataset, y quitando excepciones puntuales ya mencionadas la representación se ve completa y representa fielmente a la obra. Su resultado podría utilizarse tranquilamente como referencia para construir un modelado 3D preciso utilizando el mesh de RealityScan como parámetro de representación. 

Algo importante a considerar sobre el output de SfM, es que su nube de puntos y su malla 3D podrían utilizarse en flujos HBIM: en Autocad, Revit, Sketchup, y Blender, por mencionar algunos de los software más utilizados que permiten abrir este tipo de archivos con alta compatibilidad. Por otro lado, si evaluamos el output de NeRF y de 3DGS, si bien el segundo es bastante más liviano por su formato .ply lo cierto es que habría que encarar un proceso de conversión para hacer compatible estos archivos con un flujo de reconstrucción BIM. 

![templete-central-sfm.gif](/content/assets/cap5-templete-central-sfm.gif)

<h2 id="cap5-5-3">5.3 B2 — Benchmark de preprocesamiento ComfyUI (H2)</h2>

<h3 id="cap5-5-3-1">5.3.1 Comparación con dataset sin distractores</h3>

La primera etapa de este benchmark tiene como finalidad medir el impacto de los distractores en el dataset, por lo tanto el primer flujo de procesamiento que se creo se hizo con la finalidad de eliminar la incidencia de personas, vehículos y aves. Para correr el workflow de procesamiento sobre el dataset original se creó un pipeline de ejecución local de ComfyUI con detección y segmentación por instancia (YOLOv8-seg, vía Ultralytics, filtrado a las clases COCO `person`/`bird`/car), y luego se corrió un procesamiento de inpainting (LaMa) para realizar una reconstrucción de los píxeles eliminados. El workflow completo se corrió de forma local por GPU sin ningún tipo de costo. 

![](/content/assets/cap5-2026-09-01-13-54-22-image.png)

El procesamiento se hizo sobre el dataset completo de Templete Central que tenía 1232 imágenes, generando como resultado un Dataset B curado con 1232 imágenes alteradas por el workflow.  De las 1232 imágenes, **648 (52,6%) tenían al menos un distractor detectado y removido**; en las 584 restantes el pipeline no encontró nada que remover y la imagen quedó sin alterar. La cobertura promedio de máscara sobre las imágenes con detección fue bastante baja (0,22% del cuadro), consistente con el hecho de que los distractores son objetos puntuales (una persona, un grupo de aves) y no ocupan una porción grande dentro de los frames.

![Detección de distractores por imagen — dataset DJI completo](/content/assets/cap5-batch-deteccion-conteo.png)

*Gráfico 5.3 — Cantidad de imágenes con y sin distractor detectado, sobre las 1232 del dataset DJI completo. Fuente: `build_comfyui_batch_stats_charts.py`, a partir de `dataset-dji-comfyui-clean/logs/batch_log.csv`.*

![Distribución de cobertura de máscara entre las imágenes con detección](/content/assets/cap5-batch-cobertura-mascara-histograma.png)

*Gráfico 5.4 — Distribución de la cobertura de máscara (% del cuadro reconstruido) entre las 648 imágenes con al menos una detección. La mayoría concentra menos del 0,3% del cuadro; la cola larga hacia la derecha corresponde a los casos de múltiples distractores en un mismo fotograma (p. ej. la Figura 5.7).*

Esta primera parte aún no nos permite validar nuestra hipótesis: lo que se obtiene es un nuevo dataset para correr nuevamente los tres procesamientos de reconstrucción 3D, pero aún no tenemos información valiosa sobre el impacto que este procesamiento de ComfyUI tuvo en los resultados.

<h3 id="cap5-5-3-2">5.3.2 Evidencia visual del impacto del preprocesamiento</h3>

A continuación se detalla una comparación visual entre el dataset original y el obtenido a partir del primer procesamiento en ComfyUI. El objetivo de esta comparación es dar cuenta visualmente de aquellos distractores que se han eliminado de las imágenes. Las capturas muestran casos visuales representativos del dataset donde puede visualizarse la eliminación de distractores. 

![Comparación Foto original / Dataset limpio — aves en cielo](/content/assets/cap5-comparacion-00607-aves-en-cielo.jpg)

*Figura 5.6 — Fotograma 00607: siete aves en vuelo detectadas y eliminadas del cielo. Caso favorable para el inpainting (fondo uniforme, sin textura que reconstruir): el resultado es indistinguible de una toma sin aves.*

![Comparación Foto original / Dataset limpio — tres personas removidas](/content/assets/cap5-comparacion-00839-tres-personas.jpg)

*Figura 5.7 — Fotograma 00839: tres personas detectadas y eliminadas simultáneamente (una parcialmente en el borde inferior izquierdo, dos caminando sobre el solado). Confirma que el pipeline escala a múltiples distractores en un mismo cuadro, no solo a casos de un único objeto.*

![Comparación Foto original / Dataset limpio — persona sobre piso de piedra](/content/assets/cap5-comparacion-00522-persona-piso-piedra.jpg)

*Figura 5.8 — Fotograma 00522: persona eliminada sobre el solado de piedra irregular. Caso desfavorable para el inpainting: la persona desaparece por completo (no queda hueco ni silueta), pero el área reconstruida es perceptiblemente más borrosa que el patrón de piedra circundante — la misma limitación de LaMa en texturas complejas ya documentada en la sección 5.2.2 para el inpainting de Splatfacto. Es el tipo de caso, junto con la Figura 5.7, más representativo del dataset real: la mayoría de las detecciones ocurren sobre el solado de piedra que rodea la construcción, no contra fondos uniformes como el cielo.*

<h3 id="cap5-5-3-3">5.3.3 Pipeline de limpieza: nodos y decisiones de diseño</h3>

A continuación realizamos un recorrido detallado sobre las decisiones de diseño de este pipeline y la responsabilidad de cada uno de los nodos que lo conforman. 

![Diagrama del pipeline de limpieza de distractores en ComfyUI](/content/assets/cap5-pipeline-comfyui-limpieza.png)

*Figura 5.9 — Pipeline de limpieza de distractores ejecutado en ComfyUI. Fuente: `build_comfyui_pipeline_diagram.py`.*

Si bien el workflow completo tiene la funcionalidad de identificar y enmascarar la presencia de distractores en cada uno de los frames del dataset, cada nodo o componente de este sistema tiene una responsabilidad distinta en la obtención de este objetivo en común. A continuación se realiza un repaso por las principales decisiones de diseño que se realizaron al momento de pensar este workflow:

- **Detección con segmentación de instancia, no solo cajas delimitadoras.** `UltralyticsDetectorProvider` con YOLOv8m-seg produce, además de la caja, una máscara con la silueta exacta de cada objeto detectado. Se eligió sobre un detector de cajas simple porque una caja rectangular alrededor de una persona parada cubriría también una franja considerable por fuera de su silueta. De este modo evitamos la sobre-generación de píxeles y optimizamos el área a reconstruir. 

- **Cambio en el umbral de detección.** Con el umbral por defecto de `ImpactSimpleDetectorSEGS`, una revisión visual mostró que aves pequeñas o lejanas contra el cielo no se detectaban. Con la decisión de bajar de umbral llegamos a mayor precisión en la identificación sin generar falsos positivos. 

- **Clases ya definidas por YOLOv8-seg.** El modelo utilizado ya contiene clases que matchean con algunos de los distractores que buscábamos identificar: personas, vehículos y aves. Restringiendo la limpieza exclusivamente a estas tres clases evitamos invadir otras formas geométricas que pudieran impactar en la arquitectura como columnas, cubiertas y otros elementos. 

- **Expansión de máscara (crecer 10 px, difuminar 6 px).** La decisión de elevar el borde de las máscaras y expandirlo de forma difumado lo que genera es un área de reconstrucción un poco más amplia y por ende evitamos que aparezcan bordes duros vinculados a los objetos identificados. Esto genera que el enmascaramiento pueda difuminarse con el fondo y no se note tanto en los frames.

- **LaMa como modelo de inpainting, no MAT ni SDXL+Fooocus.** Antes de elegir definitivamente a LaMa como modelo de inpainting se probaron otros modelos como MAT y SDXL+Fooocus. Con el primero se lograron resultados muy parecidos al de LaMa, el segundo generaba un resultado levemente superior a LaMa pero el costo de procesamiento era mayor y se estimaban horas y horas de incidencia para conseguir un resultado levemente superior. Teniendo en cuenta esta comparativa se optó por LaMa ya que los resultados fueron satisfactorios y el impacto en tiempos fue reducido. 

<h3 id="cap5-5-3-4">5.3.4 Resultado de la reconstrucción sobre el Dataset B — contraste de H2</h3>

El primer paso fue re-entrenar el proceso de COLMAP pero reutilizando las poses y las cámaras que ya estaban definidas en el archivo transform.json que se había utilizado para procesar el dataset original. Esto dio como resultado una nube de puntos que pudo utilizarse tanto para obtener insights de SfM como para correr los procesos de NeRF y 3DGS. 

Al igual que las corridas sobre el dataset original se utilizó NerfStudio como software para entrenar tanto Nerfacto como Splatfacto. A continuación pueden visualizarse los parámetros de salida de cada render obtenido como resultado:

| Técnica    | Dataset             | PSNR (dB) | SSIM  | LPIPS     |
| ---------- | ------------------- | --------- | ----- | --------- |
| Nerfacto   | Raw                 | 20,22     | 0,654 | 0,114     |
| Nerfacto   | Dataset B (ComfyUI) | 17,84     | 0,545 | 0,389     |
| Splatfacto | Raw                 | 23,57     | 0,756 | 0,336     |
| Splatfacto | Dataset B (ComfyUI) | 22,28     | 0,754 | **0,227** |

*Tabla 5.3 — Templete Central (DJI): métricas de render, dataset raw vs. Dataset B curado con ComfyUI, por técnica. Ambas filas de Nerfacto corren a `downscale_factor 4` (raw reentrenado para igualar la condición de Dataset B) y ambas de Splatfacto a `downscale_factor 8` — comparación 1:1 en los dos casos.*

![Comparación PSNR/SSIM/LPIPS, raw vs. Dataset B, por técnica](/content/assets/cap5-h2-psnr-ssim-lpips-raw-vs-clean.png)

*Gráfico 5.5 — PSNR, SSIM y LPIPS del Templete Central (DJI), dataset raw vs. Dataset B (ComfyUI), por técnica. Fuente: `build_h2_comparison_chart.py`.*

**Lectura de los resultados — H2 no se sostiene sin matices:**

Podemos afirmar que la hipótesis que planteamos no se sostiene: el dataset preprocesado no mejora sus métricas en comparación con el dataset original. 

Primero vamos a analizar los resultados tomando como parámetro solo el entrenamiento de 3DGS: la fidelidad pixel a pixel no mejora, aunque si hay una mejora en LPIPS del 32% que puede estar vinculada a que hay una mejora en la percepción humana de la calidad. Esto puede interpretarse como una mejora ya que la interpretación del edificio liberado de distractores puede tener una interpretación visual más limpia. La conclusión negativa de cara a la comparativa pixel a pixel puede estar vinculada al procesamiento de LaMa y la creacion de pixeles nuevos que afectan la lectura y la interpretación del edificio: el procesamiento sumó puntos dentro de la interpretación que fueron difíciles de matchear entre imágenes porque fueron inventados por este modelo y no se encontraban realmente en el registro original. 

Llamativamente en NeRF el resultado es opuesto en todos los casos en comparación al dataset original: todas las métricas comparativas empeoran con el dataset procesado con ComfyUI. Si bien con Splatfacto la métrica de similitud perceptual mejora, en este caso no existe esa compensación. 

Si bien al menos una de las métricas acompaña la teoría de que la percepción del edificio es mejor con un preprocesamiento de los datos podemos afirmar que es un argumento débil para sostener lo que planteamos en H2: el preprocesamiento que busca eliminar distractores empeora los resultados de NeRF y Gaussian Splatting.

<h3 id="cap5-5-3-5">5.3.5 Máscara de entrenamiento (aislamiento de fondo)</h3>

Como mencionábamos en secciones anteriores de esta investigación, la validación de esta hipótesis tiene dos partes: por un lado validar la incidencia de distractores en los resultados y por otra introducir un preprocesamiento más contundente en el dataset que nos permita aislar el edificio completamente de su contexto y medir cómo esto incide en el resultado de las tres reconstrucciones.

A continuación se utilizan algunos fotogramas testigos con la finalidad de mostrar como obtuvimos el dataset nuevo. Se generó un enmascaramiento de los edificios con ComfyUI, que luego se utilizó como filtro directamente en NerfStudio al momento de correr los entrenamientos: lo que utilizó como nuevo dataset dentro del contendedor de Docker que corre el entrenamiento fue un dataset nuevo generado de forma dinámica por el contraste entre el dataset original y el dataset del enmascaramiento. 

![Foto original / máscara / resultado aislado — fotograma 00000](/content/assets/cap5-comparacion-00000-mascara.jpg)

*Figura 5.10 — Fotograma 00000: foto original, máscara de entrenamiento RMBG-2.0 y resultado de aplicarla, de izquierda a derecha. Fuente: `build_masking_before_after.py`.*

![Foto original / máscara / resultado aislado — fotograma 00308](/content/assets/cap5-comparacion-00308-mascara.jpg)

*Figura 5.11 — Fotograma 00308, mismo procedimiento. Fuente: `build_masking_before_after.py`.*

![Foto original / máscara / resultado aislado — fotograma 00462](/content/assets/cap5-comparacion-00462-mascara.jpg)

*Figura 5.12 — Fotograma 00462, mismo procedimiento. Fuente: `build_masking_before_after.py`.*

![Foto original / máscara / resultado aislado — fotograma 00616](/content/assets/cap5-comparacion-00616-mascara.jpg)

*Figura 5.13 — Fotograma 00616, mismo procedimiento. Fuente: `build_masking_before_after.py`.*

![Foto original / máscara / resultado aislado — fotograma 00924](/content/assets/cap5-comparacion-00924-mascara.jpg)

*Figura 5.14 — Fotograma 00924, mismo procedimiento, con una persona en el encuadre. Fuente: `build_masking_before_after.py`.*

![Foto original / máscara / resultado aislado — fotograma 01078](/content/assets/cap5-comparacion-01078-mascara.jpg)

*Figura 5.15 — Fotograma 01078, mismo procedimiento. Fuente: `build_masking_before_after.py`.*

<h3 id="cap5-5-3-6">5.3.6 Resultado de entrenar con la máscara</h3>

Como en el caso anterior no se realizó una corrida nueva de COLMAP sino que se aprovechó la referencia del archivo de transform.json para obtener las cámaras y sus posiciones y utilizar el masking para aislar los edificios al momento de correr tanto Nerfacto como Splatfacto dentro de NerfStudio. 

Se entrenaron ambas técnicas sobre el Templete Central (DJI) con esta máscara: Splatfacto sobre las 1232 imágenes completas y Nerfacto sobre el mismo subset de 308 imágenes ya usado en las demás comparaciones de Nerfacto.

| Técnica    | Dataset       | PSNR (dB) | SSIM  | LPIPS |
| ---------- | ------------- | --------- | ----- | ----- |
| Nerfacto   | Raw           | 19,47     | 0,602 | 0,323 |
| Nerfacto   | Con máscara † | 10,66     | 0,340 | 0,702 |
| Splatfacto | Raw           | 23,57     | 0,756 | 0,336 |
| Splatfacto | Con máscara   | 13,34     | 0,486 | 0,426 |

*Tabla 5.4 — Templete Central (DJI): métricas de render, dataset raw vs. dataset con máscara de entrenamiento RMBG, por técnica. † Nerfacto/con máscara corrió a downscale×4 (raw fue a resolución completa) — no comparable 1:1, ver nota metodológica abajo. Fuente: `build_masking_comparison_chart.py`.*

![Comparación PSNR/SSIM/LPIPS, raw vs. máscara de entrenamiento, por técnica](/content/assets/cap5-masking-psnr-ssim-lpips-raw-vs-masked.png)

*Gráfico 5.6 — PSNR, SSIM y LPIPS del Templete Central (DJI), dataset raw vs. dataset con máscara de entrenamiento, por técnica. Fuente: `build_masking_comparison_chart.py`.*

Los resultados de este experimento fueron aún peores que con el preprocesamiento de distractores: las métricas son inferiores en ambas técnicas y en cada una de las variables a analizar. Acá el dato importante es que la reconstrucción se evalúa utilizando como ground truth la imagen completa: tanto el edificio como su contexto. Y extraer el edificio de su entorno no mejora su percepción sino que la empeora. Lo que hacen ambas técnicas es 'rellenar' la información que no tienen del edificio con un ruido que puede leerse como caótico en las imágenes (ver Figura 5.16). Mientras Gaussian Splatting le baja la opacidad a las gaussianas en las secciones donde no interpreta geometría, NeRF adhiere una región con contenido sin restricciones, sumando ruido y materialidad azarosa a regiones que con el dataset limpio pueden interpretarse como cielo o suelo. 

El aprendizaje de esta prueba da cuenta de algo muy importante: el contexto de una construcción ayuda a la interpretación de la misma en lugar de jugar en su contra. Que exista un cielo y una superficie verde en la parte inferior colabora en que los entrenamientos sean completos y la información de la reconstrucción sea fiel al registro original. 

![Comparación visual: foto original, predicción raw y predicción con máscara — Splatfacto y Nerfacto](/content/assets/cap5-visual-comparison-masking.jpg)

*Figura 5.16 — Templete Central (DJI): foto original, predicción del modelo raw y predicción del modelo con máscara, sobre tres fotogramas de evaluación — bloque superior Splatfacto, bloque inferior Nerfacto. En ambas técnicas la predicción con máscara reproduce el edificio con fidelidad razonable, pero el fondo se renderiza como ruido en vez de quedar vacío o uniforme: motas de color en Splatfacto, una masa oscura/humosa en Nerfacto (degradación visual mayor). Fuente: `build_masking_visual_comparison.py`.*

| Técnica    | Dataset       | Tiempo de entrenamiento | Render (fps) | Rayos/seg |
| ---------- | ------------- | ----------------------- | ------------ | --------- |
| Nerfacto   | Raw           | 46 min 1 s              | 0,376        | 192 K     |
| Nerfacto   | Con máscara † | 1 h 50 min 21 s         | 0,361        | 185 K     |
| Splatfacto | Raw           | 33 min 41 s             | 6,65         | 849 K     |
| Splatfacto | Con máscara   | 1 h 3 min 55 s          | 6,94         | 887 K     |

*Tabla 5.5 — Tiempo de entrenamiento (30 000 iteraciones, medido por mtime de config.yml→checkpoint, igual criterio que la Tabla 5.2) y velocidad de render en evaluación (`ns-eval`), raw vs. con máscara. † Nerfacto/con máscara corrió a downscale×4, lo que debería acelerar el entrenamiento respecto a Raw (resolución completa) — ocurre lo contrario. Fuente: timestamps de archivo y `eval_results.json` de cada corrida.*

Otro dato importante a medir dentro de este experimento es el costo computacional y los tiempos de procesamiento, contraria a mi predicción, los tiempos no se optimizaron por reducir los píxeles o la región a procesar en las imágenes, más bien todo lo contrario. El entrenamiento es más lento en ambas técnicas. La explicación más probable del costo extra posiblemente esté vinculado al esfuerzo adicional que tiene que realizar NerfStudio para aplicar el enmascaramiento al momento de procesar las imágenes. 

La velocidad de render en evaluación (fps), en cambio, es prácticamente idéntica entre raw y con máscara en ambas técnicas — un dato esperable, ya que la máscara solo interviene en el entrenamiento, no en la inferencia.

Teniendo en cuenta que el objeto a reconstruir se encontraba aislado de su contexto, algo esperable era una reducción notable de gaussianas al momento de analizar el resultado del splat final, sin embargo la evaluación no valida esta expectativa:

|                                  | Raw                  | Con máscara          |
| -------------------------------- | -------------------- | -------------------- |
| Gaussianas exportadas            | 315.787              | 646.359              |
| Extensión bounding box (X, Y, Z) | 156,7 × 126,0 × 49,7 | 156,5 × 135,5 × 55,3 |
| Volumen bounding box             | 981.706              | 1.171.092            |
| Opacidad media (alpha)           | 0,659                | 0,359                |

*Tabla 5.6 — Templete Central (DJI), Splatfacto: nube de gaussianas exportada, raw vs. con máscara de entrenamiento. Fuente: `analyze_masked_splat_comparison.py`.*

El resultado indica que la máscara no reduce la cantidad de floaters ni el halo completo de gaussianas dispersas: el modelo exporta más del doble de gaussianas. Lo que sí cambia notablemente es la claridad y la distribución de las mismas: se reconocen más gaussianas transparentes concentradas, posiblemente para reemplazar aquellas regiones del contexto que el entrenamiento no llega a reconocer ni como fondo ni como suelo. 

Para dar cierre a este capítulo paso el limpio aquellas conclusiones de la investigación:

- La eliminación de distractores no mejora los resultados de NeRF y de 3DGS. 

- La eliminación de fondos y contexto general de las obras no mejora los resultados de NeRF y de 3DGS. 

- El tiempo de procesamiento y renderizado es notablemente mayor al del dataset original. 

- El conteo de gaussianas es notablemente mayor en el caso del dataset alterado, a pesar de que muchas de estas gaussianas son transparentes. 

<h2 id="cap5-5-4">5.4 B3 — Escalabilidad ante complejidad geométrica (H3)</h2>

<h3 id="cap5-5-4-1">5.4.1 Matriz de resultados</h3>

Uno de los aspectos más importantes de esta investigación tiene como foco descubrir si hay variaciones de resultados en las tres técnicas si consideramos casos de estudio donde la complejidad arquitectónica sea en ascenso. Tomando en cuenta que Los Paraguas es la obra de menor complejidad geométrica, el Templete Central es una obra de complejidad media, y el Panteón Español es la obra de mayor complejidad arquitectónica por sus ornamentos y sus cúpulas. 

Para el siguiente análisis se utilizaron distintos dataset, el mismo dispositivo de captura: el drone DJI Neo 2. Y se compararon los resultados de cada uno de los procesamientos: SfM, NeRF y 3DGS. 

| Complejidad | Caso                        | Nerfacto PSNR | Nerfacto SSIM | Splatfacto PSNR | Splatfacto SSIM | Δ PSNR (Splat − Nerf) |
| ----------- | --------------------------- | ------------- | ------------- | --------------- | --------------- | --------------------- |
| Baja        | Los Paraguas                | 25,914        | 0,816         | 30,559          | 0,910           | +4,65                 |
| Media       | Templete Central            | 19,466        | 0,602         | 23,575          | 0,756           | +4,11                 |
| Alta        | Panteón Asociación Española | 10,449        | 0,118         | 25,939          | 0,858           | +15,49                |

*Tabla 5.7 — B3, matriz de PSNR/SSIM por técnica y nivel de complejidad geométrica (dataset DJI). Fuente: `analyze_render_benchmark.py`.*

![PSNR vs. nivel de complejidad geométrica, por técnica](/content/assets/cap5-07-psnr-vs-complejidad.png)

*Gráfico 5.7 — PSNR vs. nivel de complejidad geométrica (dataset DJI), una serie por técnica.*

Podemos asumir, analizando los datos obtenidos, que el procesamiento en NeRF empeora notablemente cuando la complejidad arquitectónica y geométrica es mayor, siendo el mejor resultado de NeRF Los Paraguas y el peor el Panteón. 

Este mismo criterio no parece afectar de la misma forma a la reconstrucción con Gaussian Splatting, tanto Los Paraguas como el Panteón, ambos en extremos opuestos en cuanto a su nivel de complejidad, manifestaron resultados de gran fidelidad en ambos casos. En el caso de Templete Central hay un descenso de calidad, que puede estar vinculado al registro original y a la calidad del dataset y no tanto al algoritmo de reconstrucción. Tal vez un dataset más pobre o con una iluminación más compleja por claroscuros puede tener incidencias en los resultados afectando las métricas de ese edificio en concreto. 

<h3 id="cap5-5-4-2">5.4.2 Lectura de la divergencia entre técnicas</h3>

A continuación vamos a analizar en detalle la comparación entre los renders del dataset original y los generados por NeRF y 3DGS. El objetivo es descubrir aquellas divergencias que hay entre técnicas al momento de analizar los resultados. 

![Comparación Foto / Nerfacto / Splatfacto — Los Paraguas, DJI](/content/assets/cap5-comparacion-frame-00177.jpg)

*Figura 5.17 — Los Paraguas (complejidad baja), dataset DJI. Ambas técnicas son visualmente indistinguibles de la fotografía original a esta resolución — la referencia contra la que se mide la caída de calidad en los otros dos casos.*

- **Nerfacto sigue el patrón esperado por H3:** El análisis preliminar que anticipaba la hipótesis 3 es correcto para NeRF y se cumple al analizar el resultado de las tres obras. A medida que cree el detalle ornamental de la arquitectura el valor de PSNR disminuye notablemente y la comparación píxel a píxel se hace imprecisa. En el caso del Panteón se llega a un extremo ya que el mismo render nos permite ver floaters masivos sin correspondencia geométrica que inundan la escena. 

- **Splatfacto relacionado directamente con la calidad del SfM:** Podemos afirmar que 3DGS sostiene la hipótesis ya que mantiene un resultado sostenido en los tres edificios, y decae un poco en el caso del Templete Central. El factor que mejor explica este resultado ascendiente a medida que la complejidad geométrica sube está también vinculado a la calidad del dataset original y al resultado increíble del SfM de entrada, que obtuvo un índice de 99,93% (Tabla 5.8, sección 5.5), el más alto de los tres casos. Podemos entonces asumir que un resultado alto en la reconstrucción de fotogrametría puede incidir directamente en el resultado final del Gaussian Splatting, algo que en NeRF no se verifica. 

![Render Nerfacto — Panteón Asociación Española, floaters](/content/assets/cap5-comparacion-frame-00714.jpg)

*Figura 5.18 — Comparación Foto / Nerfacto / Splatfacto sobre el Panteón Asociación Española (dataset DJI). Nerfacto (centro) degenera en floaters de color sin relación con la geometría real; Splatfacto (derecha) reconstruye la fachada y la ornamentación con fidelidad visual comparable a la fotografía.*

Esta asimetría entre esta comparativa de técnicas es uno de los hallazgos más importantes de esta tesis y está vinculado tanto a la H1 como a la H3 combinadas: la calidad en el resultado no depende solamente de la complejidad geométrica sino que está fuertemente vinculado a la técnica de reconstrucción utilizada. Mientras 3DGS tolera la complejidad ornamental alta del Panteón, NeRF con el mismo dataset y el mismo registro de entrada de SfM ofrece un resultado inconcluso y lleno de errores. 

<h3 id="cap5-5-4-3">5.4.3 Fidelidad geométrica por caso — SfM</h3>

A continuación vamos a analizar de forma específica los resultados obtenidos en el procesamiento de fotogrametría y cómo estos han impactado en la reconstrucción de los tres edificios. 

En el caso de Los Paraguas podemos identificar que, si bien la geometría es simple y está bien constituida, hay zonas de la malla generada que presentan ausencias o huecos, un error que se repitió también al momento de reconstruir la cubierta del Templete Central. Estas ausencias de continuidad en la reconstrucción pueden estar vinculadas a registros oscuros del dataset que posiblemente fueron generados por sombras o efectos de la luz al momento del registro. La reconstrucción en 3D del Panteón es una de las más fieles de las tres, pese a la complejidad arquitectónica y ornamental de la obra. Tanto la nube densa de puntos como su reconstrucción en malla permiten identificar con precisión la obra y también reproducir en detalle algunos aspectos interesantes de su fachada: como los ornamentos de la cubierta, el detalle del vidrio partido en la puerta (una forma también de constatar deterioro como propone al comienzo esta tesis), y detalles muy precisos del estado de sus paredes y sus accesos. 

![Vista lateral de la malla SfM — Los Paraguas](/content/assets/cap5-vista-lateral.webp)

*Figura 5.19 — Vista lateral de la malla SfM (RealityScan) de Los Paraguas, a nivel de piso. Columnas y cubierta se reconstruyen con nitidez y sin huecos visibles desde este ángulo; se aprecia la doble curvatura de la losa mencionada en el Capítulo 3 (sección 3.2.2), con el río de fondo.*

![Vista lateral de la malla SfM — Templete Central](/content/assets/cap5-vista-lateral-01.webp)

*Figura 5.20 — Vista lateral de la malla SfM (RealityScan) del Templete Central, a nivel de piso. Buen detalle de las nervaduras/molduras de la cara inferior de la losa y del ritmo de columnas; los objetos bajo la cubierta (carteles, elementos reflectantes) no quedan registrados con textura limpia.*

![Vista lateral de la malla SfM — Templete Central, ángulo cercano](/content/assets/cap5-vista-lateral-02.webp)

*Figura 5.21 — Segunda vista lateral del Templete Central, más cercana, con el piso empedrado en primer plano. Confirma la lectura de la Figura 5.20: buen detalle estructural de la losa y las columnas, con pérdida de calidad en los objetos y carteles bajo la cubierta.*

![](/content/assets/cap5-2026-09-01-16-22-50-image.png)

![](/content/assets/cap5-2026-09-01-16-25-50-image.png)

El análisis de las nubes densas de cada uno de los edificios nos permite entender con mayor precisión la calidad de reconstrucción de esta técnica. La identificación de ascenso en la cantidad de puntos de cada modelo habla del ascenso en la complejidad geométrica, y otro dato importante es el creciente outlier que asciende de un edificio a otro, lo cual indica también cierta degradación entre una geometría de complejidad baja a una de complejidad alta. La distancia media a vecino más cercano indica la dispersión de puntos, y también vemos que esta es mayor cuando la complejidad geométrica sube. 

| Caso                        | Fuente                     | Puntos     | Distancia media a vecino más cercano | % de puntos outlier (muestra) |
| --------------------------- | -------------------------- | ---------- | ------------------------------------ | ----------------------------- |
| Los Paraguas                | COLMAP (fusión densa)      | 502 817    | 8,8 mm                               | 3,1%                          |
| Templete Central            | RealityScan (export denso) | 17 688 149 | 38,3 mm                              | 7,2%                          |
| Panteón Asociación Española | RealityScan (export denso) | 17 871 606 | 57,8 mm                              | 8,0%                          |

*Tabla 5.8 — Densidad y calidad local de la nube de puntos densa por caso de estudio. Fuente: `analyze_dense_clouds.py`.*

![Nube de puntos densa — Los Paraguas, proyecciones XY/XZ](/content/assets/cap5-fused-medium-high-clean-scatter.png)

*Gráfico 5.8 — Los Paraguas: proyecciones XY (planta) y XZ (perfil) de la nube densa, nivelada respecto al plano del piso (a diferencia de Templete Central y Panteón Asociación Española, este caso proviene de COLMAP nativo en vez de RealityScan y no trae los ejes alineados de fábrica). La silueta de ambas cubiertas tipo "hongo" es reconocible en la proyección de perfil, incluyendo el vástago central de cada una; la proyección de planta muestra el contorno romboidal de ambas cubiertas vistas desde arriba.*

![Nube de puntos densa — Templete Central, proyecciones XY/XZ](/content/assets/cap5-nube-densa-scatter.png)

*Gráfico 5.9 — Templete Central: proyecciones XY/XZ de la nube densa (RealityScan, dataset DJI). La proyección de planta muestra el anillo de la trayectoria de vuelo del dron rodeando la losa cuadrada; el perfil XZ reconstruye con nitidez la cubierta plana elevada sobre la fila de columnas, coherente con las Figuras 5.3 y 5.20.*

![Nube de puntos densa — Panteón Asociación Española, proyecciones XY/XZ](/content/assets/cap5-nube-densa-scatter-643e89.png)

*Gráfico 5.10 — Panteón Asociación Española: proyecciones XY/XZ de la nube densa (RealityScan, dataset DJI). El perfil XZ reconstruye con claridad la silueta de las dos cúpulas del panteón entre la arboleda circundante mencionada en el Capítulo 3 (sección 3.4.2) como fuente de distracciones para el registro.*

<h2 id="cap5-5-5">5.5 B4 — Dataset multi-dispositivo (H4)</h2>

<h3 id="cap5-5-5-1">5.5.1 Registro SfM: solo drone vs. solo cámara vs. híbrido</h3>

Otra de las hipótesis que buscamos validar en esta investigación está vinculada con la posibilidad de obtener datasets enriquecidos por capturas de distintos dispositivos. Para conseguir muestras que nos permitan validar este experimento se utilizaron registros de dos cámaras: DJI Neo 2, y la cámara Insta360, y se realizaron pruebas que permitieran comparar un dataset híbrido, de dos datasets obtenidos con ambas cámaras por separado. Los resultados se analizaron en una comparativa de dos edificios, por un lado el Templete Central y por otro el Panteón. A continuación analizamos los resultados:

| Caso                        | Dataset                                                     | Imágenes | % registrado (reportado por el wrapper)            | % registrado (real, verificado)                              |
| --------------------------- | ----------------------------------------------------------- | -------- | -------------------------------------------------- | ------------------------------------------------------------ |
| Templete Central            | Solo DJI (final)                                            | 1234     | 99,84%                                             | 99,84%                                                       |
| Templete Central            | Solo Insta360 (final)                                       | 307      | 99,67%                                             | 99,67%                                                       |
| Templete Central            | Híbrido DJI+Insta360, corrida 1 (COLMAP nativo, exhaustivo) | 794      | 0,38%                                              | **100,00%**                                                  |
| Templete Central            | Híbrido DJI+Insta360, corrida 2 (COLMAP nativo, exhaustivo) | 794      | 0,63%                                              | 0,63%                                                        |
| Panteón Asociación Española | Solo DJI (final)                                            | 1507     | 99,93%                                             | 99,93%                                                       |
| Panteón Asociación Española | Solo Insta360                                               | 365      | 85,21%                                             | 85,21%                                                       |
| Panteón Asociación Española | Híbrido DJI+Insta360 (COLMAP nativo, matching exhaustivo)   | 974      | — (corrida directa, sin wrapper `ns-process-data`) | **93,4%** (910/974, componente principal; ver sección 5.5.6) |

*Tabla 5.9 — Registro SfM por composición de dataset. Fuente: `analyze_sfm_registration_comparison.py`, `parse_colmap_images_bin.py`.*

<h3 id="cap5-5-5-2">5.5.2 Hallazgo metodológico: componentes de reconstrucción desconectados</h3>

El resultado más recurrente al momento de generar el procesamiento de SfM de los datasets híbridos fue la generación de varios componentes desconectados. El resultado que generó un 0,38% en el registro no solo generó componentes separados sino que falló catastróficamente y no pudo continuar con el procesamiento. 

El siguiente diagrama muestra como RealityScan en un intento por reconstruir el camino de las cámaras y generar la nube de puntos genera dos componentes distintos que buscan recrear el mismo edificio, por un lado uno a una escala y por otro lado otro que repite la geometría general de la obra pero con una escala superior. Estos resultados fueron registrados en RealityScan utilizando el dataset híbrido de Insta360 + DJI Neo 2 en la reconstrucción del Panteón. 

![](/content/assets/cap5-2026-09-01-17-19-01-image.png)

Algo muy parecido sucedió con el Templete Central, donde RealityScan reconstruyó dos componentes separados, por un lado una nube de puntos de 306 cámaras identificadas (de un total de 1281), y por otro lado un segundo componente de 728 cámaras (de un total de 1281 frames). Los intentos de alinear ambos componentes fallaron: RealityScan cuenta con una funcionalidad que permite seleccionar hasta seis puntos de referencia coincidentes entre ambos modelos con el fin de alinearlos en una segunda corrida. Estos intentos fallaron en ambos edificios generando nuevamente resultados de componentes dispersos y no una reconstrucción total. 

![](/content/assets/cap5-2026-09-01-17-22-11-image.png)

![](/content/assets/cap5-2026-09-01-17-23-52-image.png)

Pero RealityScan no fue la única herramienta en intentar correr un proceso de COLMAP y fallar en el intento: en un intento por correr el proceso de reconstrucción utilizando COLMAP desde Nerfstudio el software corriendo en Docker registró un fallo catastrófico y demostró solo un 0,38% en su porcentaje de avance. Analizando el output y el resultado binario de COLMAP se llegó a la conclusión de que se habían generado dos componentes desconectados en su reconstrucción y eso había generado la falla. Si bien el primer componente tenía solo un 0,38%, el segundo logró un 100% en el posicionamiento de las 794 imágenes que encontró, y este segundo componente se utilizó como referencia de análisis para la evaluación de los resultados de Nerfacto y Splatfacto dentro de Nerfstudio en la sección 5.5.5.

Con el fin de identificar el patrón de error al momento de generar la reconstrucción de SfM se corrieron al menos tres pruebas más con datasets exploratorios, por un lado un procesamiento secuencial con un subset de DJI, otro de Insta360 corriendo fisheye secuencial como parámetro de reconstrucción, y un tercero utilizando el subset de Insta360 pero en esta oportunidad seteando perspective secuencial como parámetro. Los tres generaron resultados pobres logrando posicionar menos del 5% de los frames. 

Tan solo este antecedente ya marcó un precedente en la investigación que nos llevó a comprender que la reconstrucción de SfM tiene un índice de fallos alto y de registro pobre de cámaras cuando los datasets contienen imágenes que provienen de distintos dispositivos. La complejidad en la reconstrucción puede estar vinculada al origen y las características de los lentes de cada una de estas cámaras, las diferencias en las características de los frames (la resolucion, el peso, la calidad, etc), y la complejidad de utilizar SfM cuando el tipo de procesamiento no es secuencial (siendo el registro secuencial el caso más feliz y simple al momento de procesar). 

La implicancia metodológica excede el caso puntual de esta tesis: **la tasa de registro reportada automáticamente por un wrapper de conversión SfM→Nerfstudio no debe aceptarse sin verificación cuando el dataset de entrada es heterogéneo** (múltiples dispositivos, múltiples orientaciones de lente, capturas no estrictamente secuenciales) — condiciones que, precisamente, son las que introduce H4 al combinar drone y cámara de acción. En ese sentido, este hallazgo es evidencia indirecta a favor de una de las premisas de H4: los datasets híbridos sí introducen mayores dificultades en el proceso de reconstrucción. La sección 5.5.3 profundiza en el mecanismo geométrico detrás de esa dificultad, a partir de una segunda corrida independiente sobre el mismo dataset.

<h3 id="cap5-5-5-3">5.5.3 Por qué fallan los datasets híbridos: calidad de matching cruzado entre dispositivos</h3>

Con el fin de seguir obteniendo comparativas entre distintos datasets, se procedió a realizar una segunda corrida de COLMAP nativo sobre el dataset híbrido del Templete (un dataset con 794 imágenes). El resultado fue nuevamente fallido: se obtuvo el posicionamiento de tan solo 5 cámaras (un 0,63% del total). 

La siguiente Tabla contiene la comparación del dataset del matching del COLMAP con el fin de interpretar qué tan bien se entendieron las imágenes entre sí durante el procesamiento. Los inliers promedio permiten entender qué matching geométrico hubo entre imágenes. Para aquellas imágenes que se encontraron correspondencia entre sí, no validaron otros aspectos de correspondencia entre geometrías de forma estricta. Y ahí en este indicador es donde vemos el índice más bajo, los datasets provenientes de la misma cámara encontraron mayor correspondencia entre pares. 

Inliers máximo nos permite validar el mejor caso, y los resultados son contundentes: el mejor par cruzado (183 inliers) es peor que el promedio de un par DJI-DJI (689) o incluso el promedio de un par Insta360-Insta360 (189). 

A modo de síntesis podemos confirmar que el matching entre imágenes no es un problema, sino más bien la correspondencia de geometrías una vez que el matching sucedió. Cuando se encuentran esta correspondencia entre cámaras distintas el lazo entre pares es más débil y por eso no logra generar componentes unificados.  

| Tipo de par       | Pares con algún match | Inliers promedio (pares con match) | Inliers máximo |
| ----------------- | --------------------- | ---------------------------------- | -------------- |
| DJI–DJI           | 48,9%                 | 689,1                              | 8.515          |
| Insta360–Insta360 | 45,7%                 | 189,0                              | 6.994          |
| **DJI–Insta360**  | 40,1%                 | **43,2**                           | **183**        |

*Tabla 5.10 — Calidad de matching por tipo de par de dispositivos, dataset híbrido de Templete Central. Fuente: `analyze_hybrid_cross_camera_matching.py`, sobre `database.db` de la corrida de matching exhaustivo.*

![Calidad de matching por tipo de par](/content/assets/cap5-hybrid-cross-camera-matching-chart.png)

*Gráfico 5.11 — Inliers geométricamente verificados (promedio y máximo), por tipo de par de dispositivos.*

<h3 id="cap5-5-5-4">5.5.4 Evidencia complementaria: calidad de render por dispositivo</h3>

En el Capítulo 4 se definió una métrica cuantitativa de cobertura reconstruida en porcentaje, pero dicha métrica no pudo conseguirse por la ausencia una nube de puntos que permita correr una comparativa del tipo TLS. Es por eso que para reemplazar esta evidencia, y con el fin de seguir validando la viabilidad de operar con un dataset híbrido pese a las conclusiones de SfM, se realizó un análisis en base al renderizado de Nerfacto y Splatfacto por dispositivo. 

El diseño original de B4 (Capítulo 4, sección 4.5) acota la comparación entre dispositivos a la etapa de SfM. Sin embargo, para el Templete Central y el Panteón Asociación Española también se entrenaron Nerfacto y Splatfacto por separado sobre el dataset Insta360 (con fines de documentación del caso, no como parte del diseño formal de B4), lo que permite una comparación DJI vs. Insta360 a nivel de calidad de render — evidencia complementaria a H4 que no estaba contemplada en el alcance original del benchmark, pero que es la única comparación de dispositivo pertinente para esta hipótesis (a diferencia de B1/B3, que fijan el dispositivo en DJI por diseño, sección 5.4.1).

![PSNR y SSIM por sitio, dispositivo y técnica](/content/assets/cap5-05-psnr-ssim-por-sitio.png)

*Gráfico 5.12 — PSNR (barras) y SSIM (línea) por sitio, dispositivo y técnica, las diez combinaciones medidas. Fuente: `build_comparison_charts.py`.*

![LPIPS por sitio, dispositivo y técnica](/content/assets/cap5-06-lpips-por-sitio.png)

*Gráfico 5.13 — LPIPS (distancia perceptual, más bajo es mejor) por sitio, dispositivo y técnica. Fuente: `build_comparison_charts.py`.*

Podemos deducir por el análisis del Gráfico 5.13 que no hay un dispositivo mejor que otro para la captura, hay índices que muestran que el registro con DJI fue superior, y otros casos donde los resultados con Insta360 superan el dataset de DJI. Lo que sí es consistente a modo de conclusión es que la utilización de un único dispositivo durante todo el registro optimiza mucho el procesamiento, el matching de pared en COLMAP y la reconstrucción de un único componente como geometría reconocida. En todos los casos en los cuales se utilizó un dataset híbrido los resultados fueron más pobres y complicaron mucho la generación del SfM incluso llegando a fallos catastróficos. 

![Comparación Foto / Nerfacto / Splatfacto — Templete Central, Insta360](/content/assets/cap5-comparacion-frame-00155.jpg)

*Figura 5.22 — Templete Central, dataset Insta360. Nerfacto (centro) introduce un patrón de distorsión radial concéntrica en los bordes de la vista sintetizada, ausente tanto en la fotografía original (izquierda) como en Splatfacto (derecha).*

Otra conclusión interesante de la comparativa de frames de renders indica que NeRF es más sensible a la óptica de la cámara que otros tipos de procesamiento. Como vemos en la Figura 5.22 el render de NeRF muestra que se generaron circunferencias radicales que marcan la lente gran angular del dispositivo marcando el efecto de ojo de pez del lente. 3DGS no tiene registro de las características del lente, a pesar de haber generado una reconstrucción fiel del dataset en los resultados. 

<h3 id="cap5-5-5-5">5.5.5 Resultado de reconstrucción sobre el dataset híbrido — contraste directo de H4</h3>

Como se indicó de forma previa, la segunda corrida de COLMAP para el dataset híbrido generó al menos un componente con 794 cámaras registradas. Este SfM fue procesado con NeRF y Splat también en NerfStudio y se llegó a la siguiente conclusión: en ninguna de las dos técnicas el dataset híbrido superó las métricas de los datasets que utilizan imágenes de un único dispositivo. Una afirmación que nos permite confirmar que la hipótesis H4 no se valida. Combinar dispositivos no solo genera conflictos al momento de generar procesamientos de SfM, sino que cuando conseguimos reconstruir algún componente la comparativa con otros datasets indica que los resultados tampoco son superiores.

| Técnica    | Dataset   | PSNR (dB) | SSIM  | LPIPS |
| ---------- | --------- | --------- | ----- | ----- |
| Nerfacto   | DJI       | 19,47     | 0,602 | 0,323 |
| Nerfacto   | Insta360  | 18,79     | 0,560 | 0,449 |
| Nerfacto   | Híbrido † | 11,56     | 0,460 | 0,684 |
| Splatfacto | DJI       | 23,57     | 0,756 | 0,336 |
| Splatfacto | Insta360  | 13,99     | 0,523 | 0,433 |
| Splatfacto | Híbrido   | 15,51     | 0,555 | 0,557 |

*Tabla 5.11 — Templete Central: métricas de render por dispositivo (DJI, Insta360, Híbrido) y técnica. † Nerfacto/Híbrido corrió a downscale×8 (DJI/Insta360-solo, a resolución completa) — confound adicional, ver nota metodológica arriba. DJI/Insta360 evaluados con `analyze_render_benchmark.py`; Híbrido con `ns-eval` (corrida fuera de la estructura curada de este proyecto) — mismo tipo de métrica, pipeline de cálculo distinto. Fuente: `build_hybrid_comparison_chart.py`.*

![Comparación PSNR/SSIM/LPIPS, DJI vs. Insta360 vs. Híbrido, por técnica](/content/assets/cap5-hibrido-psnr-ssim-lpips.png)

*Gráfico 5.14 — PSNR, SSIM y LPIPS del Templete Central, por dispositivo y técnica. Fuente: `build_hybrid_comparison_chart.py`.*

<h3 id="cap5-5-5-6">5.5.6 Segundo caso de estudio híbrido: reconstrucción completa del Panteón Asociación Española</h3>

Con el fin de definir el impacto del dataset híbrido sobre el caso de mayor complejidad arquitectónica, se suma un análisis más para terminar de definir si la hipótesis H4 queda finalmente invalidada. La primera parte de esta investigación fue la generación de un proceso de COLMAP sobre el dataset híbrido de DJI y Insta360 (Compuesto por 974 imágenes). El proceso corrió en una instancia de Docker y se utilizó NerfStudio, y se trató de una ejecución de 83 horas, la más extensa de todas las que conforman esta tesis. El componente principal registró 910 de las 974 imágenes (93,4%, verificado sobre `images.bin`); el resto quedó repartido en ocho componentes desconectados de 21 a 41 imágenes cada uno, el mismo patrón de fragmentación que ya vimos en el Templete Central. 

Para que la comparación sea lo más completa posible también se corrieron procesamientos de 3DGS y NeRF utilizando Nerfstudio, y las métricas que dieron como resultado son muy parecidas a lo ocurrido con Templete Central: hay matching entre pares pero el vínculo entre estos pares se vuelve muy débil cuando el algoritmo empieza a encontrar inconsistencias entre las cámaras. 

| Tipo de par       | Pares con algún match | Inliers promedio (pares con match) | Inliers máximo |
| ----------------- | --------------------- | ---------------------------------- | -------------- |
| DJI–DJI           | 31,6%                 | 647,3                              | 7.748          |
| Insta360–Insta360 | 25,1%                 | 170,0                              | 5.342          |
| **DJI–Insta360**  | 17,6%                 | **49,9**                           | **811**        |

*Tabla 5.12 — Calidad de matching por tipo de par de dispositivos, dataset híbrido del Panteón Asociación Española. Fuente: `analyze_hybrid_cross_camera_matching_panteon.py`, sobre `database.db` de la corrida `run-20260827-163722`.*

![Calidad de matching por tipo de par, Panteón Asociación Española](/content/assets/cap5-hybrid-cross-camera-matching-chart-panteon.png)

*Gráfico 5.15 — Inliers geométricamente verificados (promedio y máximo), por tipo de par de dispositivos, Panteón Asociación Española.*

| Técnica    | Dataset  | PSNR (dB) | SSIM  | LPIPS |
| ---------- | -------- | --------- | ----- | ----- |
| Nerfacto   | DJI      | 10,45     | 0,118 | 0,814 |
| Nerfacto   | Insta360 | 15,62     | 0,377 | 0,653 |
| Nerfacto   | Híbrido  | 11,34     | 0,191 | 0,827 |
| Splatfacto | DJI      | 25,94     | 0,858 | 0,163 |
| Splatfacto | Insta360 | 14,48     | 0,397 | 0,497 |
| Splatfacto | Híbrido  | 12,90     | 0,269 | 0,854 |

*Tabla 5.13 — Panteón Asociación Española: métricas de render por dispositivo (DJI, Insta360, Híbrido) y técnica. Misma metodología de cálculo mixta que la Tabla 5.11 (DJI/Insta360 con `analyze_render_benchmark.py`, Híbrido con `ns-eval`). Fuente: `build_hybrid_comparison_chart_panteon.py`.*

![Comparación PSNR/SSIM/LPIPS, DJI vs. Insta360 vs. Híbrido, Panteón Asociación Española](/content/assets/cap5-hibrido-psnr-ssim-lpips-panteon.png)

*Gráfico 5.16 — PSNR, SSIM y LPIPS del Panteón Asociación Española, por dispositivo y técnica. Fuente: `build_hybrid_comparison_chart_panteon.py`.*

Con Splatfacto el resultado calca al del Templete Central: el híbrido (12,90 dB) rinde peor que DJI solo (25,94 dB) y que Insta360 solo (14,48 dB), en las tres métricas, sin excepción. El export también lo confirma: el modelo híbrido tiene más gaussianas que el de DJI solo (673.437 vs. 315.327) en un archivo más pesado (97,5 vs. 74,6 MB) pero con peor render — la misma desconexión entre cantidad de gaussianas y calidad que ya vimos en el Templete Central.

Con Nerfacto el resultado matiza un poco esa lectura, sin contradecirla: el híbrido (11,34 dB) mejora apenas sobre DJI solo (10,45 dB) pero se queda muy por debajo de Insta360 solo (15,62 dB). A diferencia del Templete Central, acá el híbrido no es el peor de los tres — pero hay que leer esto con cuidado, no como evidencia a favor de combinar datasets: el punto de comparación (Nerfacto/DJI en el Panteón) ya era en sí mismo un fallo parcial, con floaters masivos (Figura 5.18). Mejorar un poco sobre un resultado que ya era inservible no lo vuelve servible: con PSNR 11,34 dB y SSIM 0,191, el híbrido de Nerfacto sigue muy por debajo de cualquier umbral razonable de fidelidad para documentación patrimonial.

<img title="" src="../../00-auditoria/fidelidad-geometrica/03-panteon-asociacion-espanola/hibrido/comparacion_frame_00001.jpg" alt="Comparación Foto / Nerfacto / Splatfacto — Panteón Asociación Española, dataset híbrido" width="415">

*Figura 5.23 — Panteón Asociación Española, dataset híbrido DJI+Insta360, mismo frame renderizado por ambas técnicas. Nerfacto (centro) degenera en floaters sin correspondencia geométrica reconocible, el mismo patrón que su fallo parcial sobre el dataset DJI solo (Figura 5.18). Splatfacto (abajo) reconstruye la escena con fidelidad visual reconocible, aunque —consistente con la Tabla 5.13— por debajo de su propio resultado con DJI solo.*

La prueba con el Panteón reafirma la evidencia que fuimos recolectando de cara a la conclusión de H4: los datasets híbridos generan resultados desfavorables en todos los escenarios. A nivel de resultado: en 3 de las 4 combinaciones técnica por caso evaluadas, el dataset híbrido rindió peor que cualquiera de los dos dispositivos solos, sin excepción. La única que no sigue ese patrón (Nerfacto/Panteón) no lo hace porque el híbrido haya sido bueno, sino porque el punto de comparación —Nerfacto solo con DJI— ya era en sí mismo un resultado inutilizable.

A modo de conclusión podemos reflexionar que la captura secuencial generada con un mismo dispositivo genera resultados confiables que cumplen las expectativas, siempre que el dataset contenga recorridos lo suficientemente completos la reproducción va a ser fiel al registro generado y va a entregar reconstrucciones completas. 

<h2 id="cap5-5-6">5.6 B5 — Compatibilidad web y reproducibilidad (H5)</h2>

Otro aspecto a evaluar dentro de esta tesis está vinculado a la posible compatibilidad de estos resultados con su reproductibilidad en web. El objetivo de esta investigación es validar si es posible construir un archivo digital donde los usuarios puedan visualizar las reconstrucciones en 3D y descargarlas. Para hacer esto posible es importante entender el peso de los outputs y también su posible compatibilidad con web en base a sus formatos. La Tabla 5.14 reproduce el checklist de compatibilidad documental de formatos elaborado en el Capítulo 4 (sección 4.5, B5).

| Técnica           | Formato de output                | Visor(es) compatibles              | Conversión adicional requerida                                                         |
| ----------------- | -------------------------------- | ---------------------------------- | -------------------------------------------------------------------------------------- |
| SfM               | .obj/.mtl/textura → .glTF        | Three.js, Sketchfab, Potree        | Sí — conversión .obj → .glTF no es un paso nativo del pipeline actual                  |
| NeRF (Nerfacto)   | checkpoint .ckpt (pesos del MLP) | Ninguno de forma nativa            | Sí — requiere derivar video o nube de puntos; sin formato de distribución web estándar |
| 3DGS (Splatfacto) | .splat/.ply vía SuperSplat       | Visor web de SuperSplat, Sketchfab | No — export directo                                                                    |

*Tabla 5.14 — Checklist de compatibilidad web por técnica (evaluación documental). Fuente: Capítulo 4, sección 4.5 (B5).*

El hallazgo más claro en relación a los archivos de importación es que NeRF es la técnica menos sólida para compatibilidad web, principalmente porque su output directo es un video renderizado que reproduce el recorrido original, o en su derecho nuevos recorridos seteados desde un viewer como el de NeRFStudio. Tanto 3DGS como SfM tienen una exportación que es compatible de forma directa con navegadores, tanto si se busca renderizar la nube de puntos densa como el mesh o el conjunto de gaussianas. Algunas de las plataformas/librerías que posibilitan el renderizado web con Play Canvas que permite exportar archivos .splat y generar embebings que pueden renderizarse en cualquier aplicación web, o ThreeJS que funciona como un puente entre aplicaciones basadas en React y la visualización de archivos en 3D como mesh texturizados. 

<h2 id="cap5-5-7">5.7 Tasa de fallos, por sitio</h2>

Con el fin de garantizar la reproducibilidad del pipeline que va a proponer como flujo de trabajo recomendado para garantizar la reconstrucción es importante considerar la existencia de posibles fallas y poder contextualizarlas. La Tabla 5.15 resume los eventos de fallo detectados en los logs de procesamiento y entrenamiento (no incluye la etapa de SfM, cubierta en la sección 5.5).

| Caso                        | Fallos catastróficos | Inestabilidad de convergencia | Detalle                                                                                                                                                                            |
| --------------------------- | -------------------- | ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Los Paraguas                | 2                    | 0                             | OOM de sistema y SIGKILL durante la fusión densa de COLMAP (`colmap stereo_fusion`)                                                                                                |
| Templete Central            | 3                    | 0                             | Archivo de entrada faltante (`transforms.json`); excepción de configuración (`not_use_single_camera_mode` solo funciona con `hloc`); archivo faltante en dataset ds8 de Splatfacto |
| Panteón Asociación Española | 0                    | 1 (3 reintentos)              | Reintentos del entrenamiento de Nerfacto (`04_nerfstudio_nerf_train`, 3 corridas)                                                                                                  |

*Tabla 5.15 — Tasa de fallos por sitio. Fuente: `analyze_failure_rate.py`.*

![Fallos por sitio](/content/assets/cap5-04-fallos-por-sitio.png)

*Gráfico 5.17 — Fallos catastróficos e inestabilidad de convergencia detectados en logs, por sitio.*

El Templete Central concentra la mayor cantidad de fallos catastróficos (3), en línea con ser el caso donde se probaron más variantes de dataset y configuración (subset secuencial, matching exhaustivo híbrido, múltiples estrategias de Insta360) — es decir, buena parte de estos fallos se podrían atribuir a la etapa exploratoria del proyecto donde buscábamos determinar qué tipo de dispositivo capturaba con mayor calidad y qué cantidad de imágenes garantizaba un resultado fiel, entre otras cosas. 

Teniendo en cuenta los aspectos mencionados podemos garantizar un índice de fallas bajos si el usuario que intenta reproducir el pipeline respeta los siguientes consejos:

- La utilización de un único dispositivo al momento de realizar la captura.

- Un recorrido uniforme helicoidal que garantice que cada aspecto del edificio es registrado en 360 en al menos dos o más alturas. 

<h2 id="cap5-5-8">5.8 Peso del archivo de output, por técnica</h2>

| Caso                        | Técnica    | Formato        | Peso                 |
| --------------------------- | ---------- | -------------- | -------------------- |
| Los Paraguas                | SfM        | .obj + textura | 755,9 MB + 47,1 MB   |
| Los Paraguas                | Nerfacto   | .ckpt          | 168,1 MB             |
| Los Paraguas                | Splatfacto | splat.ply      | 52,3 MB              |
| Templete Central            | SfM        | .obj + textura | 3 934,3 MB + 62,4 MB |
| Templete Central            | Nerfacto   | .ckpt          | 167,9 MB             |
| Templete Central            | Splatfacto | splat.ply      | 74,7 MB              |
| Panteón Asociación Española | SfM        | .obj + textura | 3 993,9 MB + 83,6 MB |
| Panteón Asociación Española | Nerfacto   | .ckpt          | 167,9 MB             |
| Panteón Asociación Española | Splatfacto | splat.ply      | 74,6 MB              |

*Tabla 5.16 — Peso del archivo de output final por caso y técnica (dataset DJI, el mismo criterio de B1/B3 — sección 5.4.1). El peso no es una métrica definida para H4 (Capítulo 4, sección 4.3.5); los valores de los outputs Insta360, del mismo orden de magnitud, están documentados en `00-auditoria/output-weights/` sin reproducirse aquí. Fuente: `analyze_output_weights.py`.*

![Peso de archivo por técnica](/content/assets/cap5-02-peso-archivo-por-tecnica.png)

*Gráfico 5.18 — Peso del archivo de output por técnica, comparado entre casos.*

Un aspecto interesante de este análisis es el gran peso que tienen los archivos de SfM, algo que genera desafíos al momento de definir la mejor técnica ya que encima se trata del algoritmo de reconstrucción que mayor compatibilidad tiene con un flujo de trabajo en BIM. El mesh con textura es el output que más facilitaría una integración con BIM y una posibilidad de reconstrucción en modelado 3D como Blender o Revit, sin embargo es el tipo de output más incompatible con distribución por web considerando su peso. Esto nos da una primera pista de algo importante: es probable que el pipeline de archivo digital no sea el mismo que utilicemos para integraciones HBIM. Teniendo en cuenta las bondades de 3DGS y el bajo peso de sus outputs y su compatibilidad con web es probable que esta técnica sea la más recomendada para un archivo digital, mientras la nube de puntos densa de SfM se posiciona como el resultado más amigable para integrarse con softwares de BIM. 

<h2 id="cap5-5-9">5.9 Tiempo de procesamiento</h2>

| Caso                        | Nerfacto        | Splatfacto      |
| --------------------------- | --------------- | --------------- |
| Los Paraguas                | 55 min 32 s     | 1 h 13 min 17 s |
| Templete Central            | 46 min 1 s      | 33 min 41 s     |
| Panteón Asociación Española | 1 h 38 min 35 s | 36 min 15 s     |

*Tabla 5.17 — Tiempo de entrenamiento (30 000 iteraciones) por caso y técnica (dataset DJI, el mismo criterio de B1/B3 — sección 5.4.1). Los tiempos de los datasets Insta360 están documentados en `00-auditoria/processing-time/`; el tiempo de procesamiento no es una métrica definida para H4 (Capítulo 4, sección 4.3.5), por lo que no se comparan aquí entre dispositivos. Fuente: `analyze_processing_time.py`, medido sobre las carpetas de trabajo originales (Capítulo 4, sección 4.3.6).*

Las conclusiones sobre el tiempo de procesamiento de cada técnica son ambiguas, mientras en algunos edificios NeRF se posiciona como la técnica más rápida (como en el caso de Los Paraguas), en otros como en el caso del Panteón y el Templete Central NeRF es más lenta que Splatfacto. Es probable que la complejidad geométrica del Panteón haya dificultado el procesamiento de NeRF y por eso la técnica fue casi tres veces más lenta que en 3DGS. 

<h2 id="cap5-5-10">5.10 Síntesis por hipótesis</h2>

Para cerrar este capítulo se propone un repaso por cada una de las hipótesis y las conclusiones preliminares a las cuales podemos llegar a partir del análisis de los resultados. 

**H1 — Especialización por técnica:** Esta hipótesis está parcialmente confirmada, y presenta matices que no han sido identificados al momento de su planteo. Mientras que SfM se posiciona como la técnica más compatible con una integración BIM, 3DGS tiene bondades como:

1. Su tiempo de entrenamiento inferior

2. Su calidad visual y su fidelidad con el registro del dataset original

3. Su output liviano en formato .splat que puede editarse posteriormente en SuperSplat y disponibilizarse en formato web utilizando Play Canvas.

Teniendo en cuenta estos tres aspectos 3DGS se posiciona como la mejor candidata para la generación de un archivo digital de preservación de patrimonio. NeRF por su lado no pudo garantizar buena performance al momento de reproducir complejidad geométrica alta (como en el caso del Panteón) y su output es inutilizable para el fin para el cual lo necesitamos. 

**H2 — Preprocesamiento:** Esta hipótesis es invalidada por los resultados, mientras esperábamos que el procesamiento de los datasets tenga un impacto positivo en los resultados por la posibilidad de eliminar distractores o aislar la geometría lo que demostró la evidencia es que la interpretación de estas tres técnicas sobre el edificio está condicionada positivamente por el impacto de sus entornos. 

**H3 — Complejidad geométrica:** La lectura más ajustada a la evidencia es que la complejidad geométrica y ornamental afecta negativamente el desempeño de reconstrucción, pero su efecto está mediado —y en el caso de Splatfacto, posiblemente dominado— por la calidad del registro SfM de entrada, una interacción no contemplada en el planteo original de H3 y que constituye uno de los aportes empíricos de esta tesis.

**H4 — Dataset multi-dispositivo:** Esta hipótesis es fuertemente invalidada por la evidencia. En todos los casos los resultados de datasets híbridos empeoraron el procesamiento en las tres técnicas, comenzando en algunos por generar resultados que no han podido utilizarse cuando durante el proceso de SfM se intenta reconstruir la obra y el procesamiento devuelve componentes sueltos y desconectados. La conclusión es que cualquier dataset realizado con un único dispositivo presenta mejores métricas y por ende mejores chances de ser exitoso en su proceso de reconstrucción.

**H5 — Compatibilidad web y reproducibilidad:** La evidencia marca algo que anticipamos en la hipótesis y es que cada técnica cuenta con una especialización y un nivel de compatibilidad distinto. En la hipótesis se plantea que alguna de estas técnicas va a presentar mayor compatibilidad (como sucedió con 3DGS), mientras que otras van a quedar completamente descartadas (como el caso de NeRF). 

<h2 id="cap5-5-12">5.12 Conclusiones del capítulo</h2>

Se puede afirmar que todos los experimentos que se plantearon en el Capítulo 4 se pudieron ejecutar con éxito, si bien no todos los resultados acompañaron las hipótesis que se plantearon, lo cierto es que todas las conclusiones obtenidas nos permitieron tener un entendimiento de las tres técnicas de reconstrucción que son eje de este estudio y comprender cómo cada una podría colaborar de forma distinta en la conformación de un pipeline único. 

Estos resultados, junto con las limitaciones y sus conclusiones, se traducen en el Capítulo 6 en un pipeline definitivo documentado y en criterios prácticos de selección de técnica según el objeto patrimonial a relevar.
