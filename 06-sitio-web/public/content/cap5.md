Este capitulo contiene los resultados de los experimentos de esta tesis y sus respectivos analisis, algunos validan las hipotesis planteadas al comienzo de esta investigacion y otros la refutan. A continuacion voy a enumerar los benchmarks que vamos a estar analizando con el fin de comparar estos resultados con lo esperado:

- B1 - Plantea una comparativa de las tres tecnicas (fotogrametria, NeRF y 3DGS) con el fin de identificar ventajas y desventajas de cada uno de estos algoritmos

- B2 - Busca identificar el impacto del preprocesamiento del dataset utilizando dos tecnicas distintas, por un lado una que solo elimina distractores y por otro lado otra mas invasiva que elimina el contexto de los edificios

- B3 - Analiza el impacto de las tecnicas de cara a la reconstruccion de distinta complejidad geometrica. 

- B4 - Analiza el impacto de utilizar multiples dispositivos con el fin de generar un dataset diverso multi-camara. 

- B5 - Valida la compatibilidad con formatos web de los outputs de cada uno de los resultados. 

Como esta planteado en el Capitulo 1, el objetivo de estos experimentos tiene un fin en comun: identificar el mejor pipeline para reconstruir tridimensionalmente edificios a partir de imagenes y colaborar en la integracion de estos resultados con un flujo de reconstruccion HBIM y un potencial archivo digital compatible con web. 

<h2 id="cap5-5-1">5.1 Resumen de los benchmarks</h2>

Antes de profundizar en el detalle de los resultados de cada benchmark, la siguiente tabla (Tabla 5.1), sume la ejecucion de cada una de estas pruebas y detalla el edificio en el cual se ejecuto y el dataset que se utilizo para las pruebas.

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

El objetivo de este benchmark es identificar como performa cada una de las tecnicas relevadas (SfM, NeRF y 3DGS) sobre un mismo caso de estudio: El templete central del Sexto Panteon de Chacarita. Para este relevamiento se utilizo un dataset obtenido con el drone DJI Neo 2. La siguiente tabla (Tabla 5.2) expresa el analisis de los resultados utilizando las siguientes variables:

**PSNR (Peak Signal-to-Noise Rati):** Crea una comparativa pixel a pixel entre el render del output y la imagen del dataset con el fin de medir en decibelios la coincidencia. Cuanto mas alto sea el valor mas fiel es la reconstruccion. 

**SSIM (Structural Similarity Index Measure):** Esta tecnica lo que hace es comparar parametros como luminancia, contraste y estructura (patrones de bordes, texturas). Cuanto mas cerca de 1 sera el resultado mayor es la coincidencia. 

**LPIPS (Learned Perceptual Image Patch Similarity):** Esta tecnica de comparacion usa una red neuronal ya entrenada que se parece mucho a como una persona interpretaria la imagen, puede por ejemplo identificar si una reconstruccion 'se ve mal'. Este indice es contrario a los anteriores y refleja mayor similitud en su cercania con el valor de 0. 

**Tiempo de entrenamiento:** Esta variable es fundamental para entender los costos de correr cada procesamiento y empezar a dimensionar el impacto que puede tener en un posterior plan de generacion de un archivo digital de obras locales. Aquellos procesamientos que duren menos tiempo seran ponderados con el fin de obtener un pipeline que sea reproducible. 

**Peso del output:** El peso de los archivos que se generan como resultado tiene como finalidad medir si es viable o no subir en una plataforma o en algun archivo digital los resultados. Aquellos archivos que pesen menos seran ponderados por sobre los mas pesados. 

Antes de avanzar con el analisis del benchmark es importante entender que el output del proceso de SfM no es comparable en tres variables con NeRF y 3DGS, las tres primeras variables corren sobre videos renderizados como resultados de estos procesamientos, y la tecnica de SfM no es renderizable ya que su output es una nube de puntos densa y una malla texturizada. Esto no afecta la validacion del benchmark porque podemos comparar las tecnicas tambien desde un enfoque cualitativo y no solo cuantitavo a partir de las metricas, por lo tanto compensamos el analisis de SfM evaluando directamente los resultados del procesamiento a nivel cualitativo. 

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

La Tabla 5.2 ya adelanta la magnitud del export de Splatfacto (315 787 gaussianas). El Gráfico 5.1 caracteriza esa nube de gaussianas: casi dos tercios (64,6%) tiene opacidad estimada por encima de 0,5, y solo un 7,3% está por debajo de 0,05 (gaussianas casi transparentes, ya vemos un resultado candidato a limpieza en SuperSplat por la cantidad de gaussianas que conforman el contexto del edificio y no solo la reproduccion del mismo).

![Distribución de opacidad de las gaussianas — Templete Central, DJI, Splatfacto](/content/assets/cap5-gaussian-splat-opacity-histogram.png)

*Gráfico 5.1 — Distribución de opacidad estimada de las 315 787 gaussianas exportadas para el Templete Central (dataset DJI). Fuente: `analyze_gaussian_splats.py`.*

![Distribución espacial de las gaussianas — Templete Central, DJI, Splatfacto](/content/assets/cap5-gaussian-splat-spatial-scatter.png)

*Gráfico 5.2 — Distribución espacial (proyecciones XY/XZ) de las gaussianas exportadas para el Templete Central. A diferencia de la nube de puntos densa de SfM (Gráfico 5.9), aquí no se distingue una silueta arquitectónica nítida: se observa un núcleo denso concentrado cerca del origen (la escena registrada) rodeado por un halo disperso de gaussianas de baja densidad que se extiende varias veces el tamaño del objeto — candidatas, junto con las de opacidad casi nula del Gráfico 5.1, a la limpieza de outliers en SuperSplat mencionada en el Capítulo 6 (sección 6.2.5).*

Podemos concluir en que Splatfacto supera a Nerfacto en PSNR (+4,1 dB) y SSIM (+0,154), y lo hace en el 73% del tiempo de entrenamiento y con un archivo 2,25 veces más liviano — un patrón de eficiencia que se repite, con distinta magnitud, en los otros dos casos de estudio (sección 5.4). El único indicador donde Nerfacto iguala a Splatfacto es LPIPS (0,323 vs. 0,336, prácticamente empatados), lo que sugiere que, aunque Splatfacto reconstruye con mayor fidelidad píxel a píxel (PSNR/SSIM), la distancia perceptual entre ambos métodos es menor de lo que el PSNR por sí solo indicaría.

<h3 id="cap5-5-2-2">5.2.2 Fidelidad geométrica — Nerfacto vs. Splatfacto vs. SfM</h3>

A simple vista los resultados de NeRF y 3DGS son bastante similares y ambos logran representar con exito la geometria y los aspectos esenciales de la materialidad. En al menos 4 de 5 fotogramas se pueden visualizar que ambas tecnicas logran reproducir con exito la interpretacion de la losa en voladizo y las molduras de la misma, siendo un detalle de su materialidad que logra una correcta interpretacion. Hay un caso interesante y es la presencia de una mancha en una captura de 3DGS (Figura 5.4). Lo que se puede ver en la imagen suele denominarse ghosting y es la presencia de zonas borradas o tapadas por otros gaussianos que se anteponen a la captura de la camara en ese punto de vista (tambien llamado floaters por su naturaleza de estar suspendidos y no adosados directamente a la geometria principal). A pesar de este error puntual se puede concluir en que 3DGS es la tecnica mas solida en cuanto a la reconstruccion y logra los resultados mas nitidos al momento de representar materialidad. 

Como ultima instancia vamos a comparar los resultados de SfM, el video/gif a contiuacion contiene una animacion del recorrido generado por el procesamiento, donde no solo puede visualizarse la nube de puntos sino tambien el camino establecido por las imagenes y sus posicionamientos. Como puede verse en la animacion SfM logro una representacion fiel del edificio y tambien puede visualizarse con detalles reproducciones de su geometria y su materialidad. En general la captura es fiel a la obra y solo pueden identificarse defectores menores como la ausencia de puntos en algunas zonas de la cubierta, un defecto que puede estar relacionado con la presencia de sombras especificas al momento de la captura que pueden haber sido identificadas como vacios.

![templete-central-sfm-2.gif](/content/assets/cap5-templete-central-sfm-2.gif)

<h3 id="cap5-5-2-3">5.2.3 SfM — Malla texturizada y potencial de integración BIM</h3>

La malla texturizada obtenida con RealityScan para el Templete Central tiene 17 688 149 vértices y 35 376 582 triángulos, con una textura única de 8192×8192 px (62,4 MB). Su geometria es consistente, a excepcion de estos defectos mencionados en la seccion anterior donde se identifican ausencias de continuidad en la cubierta. 

![](/content/assets/cap5-2026-09-01-13-31-22-image.png)

![](/content/assets/cap5-2026-09-01-13-33-17-image.png)

Como mencionamos con anterioridad, el output de SfM no puede ser comparable con NeRF y 3DGS por lo tanto su evaluacion en este benchmark esta orientada a cualidades visuales que podamos identificar a simple vista. Podemos afirmar que la interpretacion de SfM dio como resultado una geometria explicita, que su materialidad asignada se corresponde visualmente con lo capturado en el dataset, y quitando excepciones puntuales ya mencionadas la representacion se ve completa y representa fielmente a la obra. Su resultado podria utilizarse tranquilamente como referencia para construir un modelado 3D preciso utilizando el mesh de RealityScan como parametro de representacion. 

Algo importante a considerar sobre el output de SfM, es que su nube de puntos y su malla 3D podrian utilizarse en flujos HBIM: en Autocad, Revit, Sketchup, y Blender, por mencionar algunos de los software mas utilizados que permiten abrir este tipo de archivos con alta compatibilidad. Por otro lado, si evaluamos el output de NeRF y de 3DGS, si bien el segundo es bastante mas liviano por su formato .ply lo cierto es que habria que encarar un proceso de conversion para hacer compatible estos archivos con un flujo de reconstruccion BIM. 

![templete-central-sfm.gif](/content/assets/cap5-templete-central-sfm.gif)

<h2 id="cap5-5-3">5.3 B2 — Benchmark de preprocesamiento ComfyUI (H2)</h2>

<h3 id="cap5-5-3-1">5.3.1 Comparacion con dataset sin distractores</h3>

La primera etapa de este benchmark tiene como finalidad medir el impacto de los distractores en el dataset, por lo tanto el primer flujo de procesamiento que se creo se hizo con la finalidad de eliminar la incidencia de personas, vehiculos y aves. Para correr el workflow de procesamiento sobre el dataset original se creo un pipeline de ejecucion local de ComfyUI con deteccion y segmentacion por instancia (YOLOv8-seg, vía Ultralytics, filtrado a las clases COCO `person`/`bird`/car), y luego se corrio un procesamiento de inpainting (LaMa) para realizar una reconstruccion de los pixeles eliminados. El workflow completo se corrio de forma local por GPU sin ningun tipo de costo. 

![](/content/assets/cap5-2026-09-01-13-54-22-image.png)

El procesamiento se hizo sobre el dataset completo de Templete Central que tenia 1232 imágenes, generando como resultado un Dataset B curado con 1232 imagenes alteradas por el workflow.  De las 1232 imágenes, **648 (52,6%) tenían al menos un distractor detectado y removido**; en las 584 restantes el pipeline no encontró nada que remover y la imagen quedó sin alterar. La cobertura promedio de máscara sobre las imágenes con detección fue bastante baja (0,22% del cuadro), consistente con el hecho de que los distractores son objetos puntuales (una persona, un grupo de aves) y no ocupan una porción grande dentro de los frames.

![Detección de distractores por imagen — dataset DJI completo](/content/assets/cap5-batch-deteccion-conteo.png)

*Gráfico 5.3 — Cantidad de imágenes con y sin distractor detectado, sobre las 1232 del dataset DJI completo. Fuente: `build_comfyui_batch_stats_charts.py`, a partir de `dataset-dji-comfyui-clean/logs/batch_log.csv`.*

![Distribución de cobertura de máscara entre las imágenes con detección](/content/assets/cap5-batch-cobertura-mascara-histograma.png)

*Gráfico 5.4 — Distribución de la cobertura de máscara (% del cuadro reconstruido) entre las 648 imágenes con al menos una detección. La mayoría concentra menos del 0,3% del cuadro; la cola larga hacia la derecha corresponde a los casos de múltiples distractores en un mismo fotograma (p. ej. la Figura 5.7).*

Esta primera parte aun no nos permite validar nuestra hipotesis: lo que se obtiene es un nuevo dataset para correr nuevamente los tres procesamientos de reconstruccion 3D, pero aun no tenemos informacion valiosa sobre el impacto que este procesamiento de ComfyUI tuvo en los resultados.

<h3 id="cap5-5-3-2">5.3.2 Evidencia visual del impacto del preprocesamiento</h3>

A continuacion se detalla una comparacion visual entre el dataset original y el obtenido a partir del primer procesamiento en ComfyUI. El objetivo de esta comparacion es dar cuenta visualmente de aquellos distractores que se han eliminado de las imagenes. Las capturas muestran casos visuales representativos del dataset donde puede visualizarse la eliminacion de distractores. 

![Comparación Foto original / Dataset limpio — aves en cielo](/content/assets/cap5-comparacion-00607-aves-en-cielo.jpg)

*Figura 5.6 — Fotograma 00607: siete aves en vuelo detectadas y eliminadas del cielo. Caso favorable para el inpainting (fondo uniforme, sin textura que reconstruir): el resultado es indistinguible de una toma sin aves.*

![Comparación Foto original / Dataset limpio — tres personas removidas](/content/assets/cap5-comparacion-00839-tres-personas.jpg)

*Figura 5.7 — Fotograma 00839: tres personas detectadas y eliminadas simultáneamente (una parcialmente en el borde inferior izquierdo, dos caminando sobre el solado). Confirma que el pipeline escala a múltiples distractores en un mismo cuadro, no solo a casos de un único objeto.*

![Comparación Foto original / Dataset limpio — persona sobre piso de piedra](/content/assets/cap5-comparacion-00522-persona-piso-piedra.jpg)

*Figura 5.8 — Fotograma 00522: persona eliminada sobre el solado de piedra irregular. Caso desfavorable para el inpainting: la persona desaparece por completo (no queda hueco ni silueta), pero el área reconstruida es perceptiblemente más borrosa que el patrón de piedra circundante — la misma limitación de LaMa en texturas complejas ya documentada en la sección 5.2.2 para el inpainting de Splatfacto. Es el tipo de caso, junto con la Figura 5.7, más representativo del dataset real: la mayoría de las detecciones ocurren sobre el solado de piedra que rodea la construcción, no contra fondos uniformes como el cielo.*

<h3 id="cap5-5-3-3">5.3.3 Pipeline de limpieza: nodos y decisiones de diseño</h3>

A continuacion realizamos un recorrido detallado sobre las decisiones de diseno de este pipeline y la responsabilidad de cada uno de los nodos que lo conforman. 

![Diagrama del pipeline de limpieza de distractores en ComfyUI](/content/assets/cap5-pipeline-comfyui-limpieza.png)

*Figura 5.9 — Pipeline de limpieza de distractores ejecutado en ComfyUI. Fuente: `build_comfyui_pipeline_diagram.py`.*

Si bien el workflow completo tiene la funcionalidad de identificar y enmascarar la presencia de distractores en cada uno de los frames del dataset, cada nodo o componente de este sistema tiene una responsabilidad distinta en la obtencion de este objetivo en comun. A continuacion se realiza un repaso por las principales decisiones de diseno que se realizaron al momento de pensar este worflow:

- **Detección con segmentación de instancia, no solo cajas delimitadoras.** `UltralyticsDetectorProvider` con YOLOv8m-seg produce, además de la caja, una máscara con la silueta exacta de cada objeto detectado. Se eligió sobre un detector de cajas simple porque una caja rectangular alrededor de una persona parada cubriría también una franja considerable por fuera de su silueta. De este modo evitamos la sobre-generacion de pixeles y optimizamos el area a reconstruir. 

- **Cambio en el umbral de deteccion.** Con el umbral por defecto de `ImpactSimpleDetectorSEGS`, una revisión visual mostró que aves pequeñas o lejanas contra el cielo no se detectaban. Con la decision de bajar de umbral llegamos a mayor precision en la identificacion sin generar falsos positivos. 

- **Clases ya definidas por YOLOv8-seg.** El modelo utilizado ya contiene clases que matchean con algunos de los distractores que buscabamos identificar: personas, vehiculos y aves. Restringiendo la limpieza exclusivamente a estas tres clases evitamos invadir otras formas geometricas que pudieran impactar en la arquitectura como columnas, cubiertas y otros elementos. 

- **Expansión de máscara (crecer 10 px, difuminar 6 px).** La decision de elevar el borde de las mascaras y expandirlo de forma difumado lo que genera es un area de reconstruccion un poco mas amplia y por ende evitamos que aparezcan bordes duros vinculados a los objetos identificados. Esto genera que el enmascaramiento pueda difuminarse con el fondo y no se note tanto en los frames.

- **LaMa como modelo de inpainting, no MAT ni SDXL+Fooocus.** Antes de elegir definitamente a LaMa como modelo de inpainting se probaron otros modelos como MAT y SDXL+Fooocus. Con el primero se lograron resultados muy parecidos al de LaMa, el segundo generaba un resultado levemente superior a LaMa pero el costo de procesamiento era mayor y se estimaban horas y horas de incidencia para conseguir un resultado levemente superior. Teniendo en cuenta esta comparativa se opto por LaMa ya que los resultados fueron satisfactorios y el impacto en tiempos fue reducido. 

<h3 id="cap5-5-3-4">5.3.4 Resultado de la reconstrucción sobre el Dataset B — contraste de H2</h3>

El primer paso fue re-entrenar el proceso de COLMAP pero reutilizando las poses y las camaras que ya estaban definidas en el archivo transform.json que se habia utilizado para procesar el dataset original. Esto dio como resultado una nube de puntos que pudo utilizarse tanto para obtener insights de SfM como para correr los procesos de NeRF y 3DGS. 

Al igual que las corridas sobre el dataset original se utilizo NerfStudio como software para entrenar tanto Nerfacto como Splatfacto. A continuacion pueden visualizarse los parametros de salida de cada render obtenido como resultado:

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

Podemos afirmar que la hipotesis que planteamos no se sostiene: el dataset proprocesado no mejora sus metricas en comparacion con el dataset original. 

Primero vamos a analizar los resultados tomando como parametro solo el entrenamiento de 3DGS: la fidelidad pixel a pixel no mejora, aunque si hay una mejora en LPIPS del 32% que puede estar vinculada a que hay una mejora en la percepcion humana de la calidad. Esto puede interpretarse como una mejora ya que la interpretacion del edificio liberado de distractores puede tener una interpretacion visual mas limpia. La conclusion negativa de cara a la comparativa pixel a pixel puede estar vinculada al procesamiento de LaMa y la creacion de pixeles nuevos que afectan la lectura y la interpretacion del edificio: el procesamiento sumo puntos dentro de la interpretacion que fueron dificiles de matchear entre imagenes porque fueron inventados por este modelo y no se encontraban realmente en el registro original. 

Llamativamente en NeRF el resultado es opuesto en todos los casos en comparacion al dataset original: todas las metricas comparativas empeoran con el dataset procesado con ComfyUI. Si bien con Splatfacto la metrica de similitud perceptual mejora, en este caso no existe esa compensacion. 

Si bien al menos una de las metricas acompana la teoria de que la percepcion del edificio es mejor con un preprocesamiento de los datos podemos afirmar que es un argumento debil para sostener lo que planteamos en H2: el preprocesamiento que busca eliminar distractores empeora los resultados de NeRF y Gaussian Splatting.

<h3 id="cap5-5-3-5">5.3.5 Máscara de entrenamiento (aislamiento de fondo)</h3>

Como mencionabamos en secciones anteriores de esta investigacion, la validacion de esta hipotesis tiene dos partes: por un lado validar la incidencia de distractores en los resultados y por otra introducir un preprocesamiento mas contundente en el dataset que nos permita aislar el edificio completamente de su contexto y medir como esto indice en el resultado de las tres reconstrucciones.

A continuacion se utilizan algunos fotogramas testigos con la finalidad de mostrar como obtuvimos el dataset nuevo. Se genero un enmascaramiento de los edificios con ComfyUI, que luego se utilizo como filtro directamente en NerfStudio al momento de correr los entrenamientos: lo que utilizo como nuevo dataset dentro del contendedor de Docker que corre el entrenamiento fue un dataset nuevo generado de forma dinamica por el contraste entre el dataset original y el dataset del enmascaramiento. 

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

Como en el caso anterior no se realizo una corrida nueva de COLMAP sino que se aprovecho la referencia del archivo de transform.json para obtener las camaras y sus posiciones y utilizar el masking para aislar los edificios al momento de correr tanto Nerfacto como Splatfacto dentro de NerfStudio. 

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

Los resultados de este experimento fueron aun peores que con el preprocesamiento de distractores: las metricas son inferiores en ambas tecnicas y en cada una de las variables a analizar. Aca el dato importante es que la reconstruccion se utiliza utilizando como ground truth la imagen completa: tanto el edificio como su contexto. Y extraer el edificio de su entorno no mejora su percepcion sino que la empeora. Lo que hacen ambas tecnicas es 'rellenar' la informacion que no tienen del edificio con un ruido que puede leerse como caotico en las imagenes (ver Figura 5.16). Mientras Gaussian Splatting le baja la opacidad a las gaussianas en las secciones donde no interpreta geometria, NeRF adhiere una region con contenido sin restricciones, sumando ruido y materialidad azaroza a regiones que con el dataset limpio pueden interpretarse como cielo o suelo. 

El aprendizaje de esta prueba da cuenta de algo muy importante: el contexto de una construccion ayuda a la interpretacion de la misma en lugar de jugar en su contra. Que exista un cielo y una superficie verde en la parte inferior colabora en que los entrenamientos sean completos y la informacion de la reconstruccion sea fiel al registro original. 

![Comparación visual: foto original, predicción raw y predicción con máscara — Splatfacto y Nerfacto](/content/assets/cap5-visual-comparison-masking.jpg)

*Figura 5.16 — Templete Central (DJI): foto original, predicción del modelo raw y predicción del modelo con máscara, sobre tres fotogramas de evaluación — bloque superior Splatfacto, bloque inferior Nerfacto. En ambas técnicas la predicción con máscara reproduce el edificio con fidelidad razonable, pero el fondo se renderiza como ruido en vez de quedar vacío o uniforme: motas de color en Splatfacto, una masa oscura/humosa en Nerfacto (degradación visual mayor). Fuente: `build_masking_visual_comparison.py`.*

| Técnica    | Dataset       | Tiempo de entrenamiento | Render (fps) | Rayos/seg |
| ---------- | ------------- | ----------------------- | ------------ | --------- |
| Nerfacto   | Raw           | 46 min 1 s              | 0,376        | 192 K     |
| Nerfacto   | Con máscara † | 1 h 50 min 21 s         | 0,361        | 185 K     |
| Splatfacto | Raw           | 33 min 41 s             | 6,65         | 849 K     |
| Splatfacto | Con máscara   | 1 h 3 min 55 s          | 6,94         | 887 K     |

*Tabla 5.5 — Tiempo de entrenamiento (30 000 iteraciones, medido por mtime de config.yml→checkpoint, igual criterio que la Tabla 5.2) y velocidad de render en evaluación (`ns-eval`), raw vs. con máscara. † Nerfacto/con máscara corrió a downscale×4, lo que debería acelerar el entrenamiento respecto a Raw (resolución completa) — ocurre lo contrario. Fuente: timestamps de archivo y `eval_results.json` de cada corrida.*

Otro dato importante a medir dentro de este experimento es el costo computacional y los tiempos de procesamiento, contraria a mi prediccion, los tiempos no se optimizaron por reducir los pixeles o la region a procesar en las imagenes, mas bien todo lo contrario. El entrenamiento es mas lento en ambas tecnicas. La explicación más probable del costo extra posiblemente este vinculado al esfuerzo adicional que tiene que realizar NerfStudio para aplicar el enmascaramiento al momento de procesar las imagenes. 

La velocidad de render en evaluación (fps), en cambio, es prácticamente idéntica entre raw y con máscara en ambas técnicas — un dato esperable, ya que la máscara solo interviene en el entrenamiento, no en la inferencia.

Teniendo en cuenta que el objeto a reconstruir se encontraba aislado de su contexto, algo esperable era una reduccion notable de gaussianas al momento de analizar el resultado del splat final, sin embargo la evaluacion no valida esta expectativa:

|                                  | Raw                  | Con máscara          |
| -------------------------------- | -------------------- | -------------------- |
| Gaussianas exportadas            | 315.787              | 646.359              |
| Extensión bounding box (X, Y, Z) | 156,7 × 126,0 × 49,7 | 156,5 × 135,5 × 55,3 |
| Volumen bounding box             | 981.706              | 1.171.092            |
| Opacidad media (alpha)           | 0,659                | 0,359                |

*Tabla 5.6 — Templete Central (DJI), Splatfacto: nube de gaussianas exportada, raw vs. con máscara de entrenamiento. Fuente: `analyze_masked_splat_comparison.py`.*

El resultado indica que la mascara no reduce la cantidad de floaters ni el halo completo de gaussianas dispersas: el modelo exporta mas del doble de gaussianas. Lo que si cambia notablemente es la claridad y la distribucion de las mismas: se reconocen mas gaussianas transparentes concentradas, posiblemente para reemplazar aquellas regiones del contexto que el entrenamiento no llega a reconocer ni como fondo ni como suelo. 

Para dar cierre a este capitulo paso el limpio aquellas conclusiones de la investigacion:

- La eliminacion de distractores no mejora los resultados de NeRF y de 3DGs. 

- La eliminacion de fondos y contexto general de las obras no mejora los resultados de NeRF y de 3DGs. 

- El tiempo de procesamiento y renderizado es notablemente mayor al del dataset original. 

- El conteo de gaussianas es notablemente mayor en el caso del dataset alterado, a pesar de que muchas de estas gaussianas son transparentes. 

<h2 id="cap5-5-4">5.4 B3 — Escalabilidad ante complejidad geométrica (H3)</h2>

<h3 id="cap5-5-4-1">5.4.1 Matriz de resultados</h3>

Uno de los aspectos mas importantes de esta investigacion tiene como foco descubrir si hay variaciones de resultados en las tres tecnicas si consideramos casos de estudio donde la complejidad arquitectonica sea en ascenso. Tomando en cuenta que Los Paraguas es la obra de menor complejidad geometrica, el Templete Central es una obra de complejidad media, y el Panteon Espanol es la obra de mayor complejidad arquitectonica por sus ornamentos y sus cupulas. 

Para el siguiente analisis de utilizaron distintos dataset, el mismo dispositivo de captura: el drone DJI Neo 2. Y se compararon los resultados de cada uno de los procesamientos: SfM, NeRF y 3DGS. 

| Complejidad | Caso                        | Nerfacto PSNR | Nerfacto SSIM | Splatfacto PSNR | Splatfacto SSIM | Δ PSNR (Splat − Nerf) |
| ----------- | --------------------------- | ------------- | ------------- | --------------- | --------------- | --------------------- |
| Baja        | Los Paraguas                | 25,914        | 0,816         | 30,559          | 0,910           | +4,65                 |
| Media       | Templete Central            | 19,466        | 0,602         | 23,575          | 0,756           | +4,11                 |
| Alta        | Panteón Asociación Española | 10,449        | 0,118         | 25,939          | 0,858           | +15,49                |

*Tabla 5.7 — B3, matriz de PSNR/SSIM por técnica y nivel de complejidad geométrica (dataset DJI). Fuente: `analyze_render_benchmark.py`.*

![PSNR vs. nivel de complejidad geométrica, por técnica](/content/assets/cap5-07-psnr-vs-complejidad.png)

*Gráfico 5.7 — PSNR vs. nivel de complejidad geométrica (dataset DJI), una serie por técnica.*

Podemos asumir, analizando los datos obtenidos, que el procesamiento en NeRF empeora notablemente cuando la complejidad arquitectonica y geometrica es mayor, siendo el mejor resultado de NeRF Los Paraguas y el peor el Panteon. 

Este mismo criterio no parece afectar de la misma forma a la reconstruccion con Gaussian Splatting, tanto Los Paraguas como el Panteon, ambos en extremos opuestos en cuanto a su nivel de complejidad, manifestaron resultados de gran fidelidad en ambos casos. En el caso de Templete Central hay un descenso de calidad, que puede estar vinculado al registro original y a la calidad del dataset y no tanto al algortimo de reconstruccion. Tal vez un dataset mas pobre o con una iluminacion mas compleja por clarouscuros puede tener incidencias en los resultados afectando las metricas de ese edificio en concreto. 

<h3 id="cap5-5-4-2">5.4.2 Lectura de la divergencia entre técnicas</h3>

A continuacion vamos a analizar en detalle la comparacion entre los renders del dataset original y los generados por NeRF y 3DGS. El objetivo es descubrir aquellas divergencias que hay entre tecnicas al momento de analizar los resultados. 

![Comparación Foto / Nerfacto / Splatfacto — Los Paraguas, DJI](/content/assets/cap5-comparacion-frame-00177.jpg)

*Figura 5.17 — Los Paraguas (complejidad baja), dataset DJI. Ambas técnicas son visualmente indistinguibles de la fotografía original a esta resolución — la referencia contra la que se mide la caída de calidad en los otros dos casos.*

- **Nerfacto sigue el patrón esperado por H3:** El analisis preliminar que anticipaba la hipotesis 3 es correcto para NeRF y se cumple al analizar el resultado de las tres obras. A medida que cree el detalle ornamental de la arquitectura el valor de PSNR disminuye notablemente y la comparacion pixel a pixel se hace imprescisa. En el caso del Panteon se llega a un extremo ya que el mismo render nos permite ver floaters masivos sin correspondencia geometria que inundan la escena. 

- **Splatfacto relacionado directamente con la calidad del SfM:** Podemos afirmar que 3DGS sostiene la hipotesis ya que mantiene un resultado sostenido en los tres edificios, y decae un poco en el caso del Templete Central. El factor que mejor explica este resultado ascendiente a medida que la complejidad geometrica sube esta tambien vinculado a la calidad del dataset original y al resultado increible del SfM de entrada, que obtuvo un indice de 99,93% (Tabla 5.8, sección 5.5), el más alto de los tres casos. Podemos entonces asumir que un resultado alto en la reconstruccion de fotogrametria puede incidir directamente en el resultado final del Gaussian Splatting, algo que en NeRF no se verifica. 

![Render Nerfacto — Panteón Asociación Española, floaters](/content/assets/cap5-comparacion-frame-00714.jpg)

*Figura 5.18 — Comparación Foto / Nerfacto / Splatfacto sobre el Panteón Asociación Española (dataset DJI). Nerfacto (centro) degenera en floaters de color sin relación con la geometría real; Splatfacto (derecha) reconstruye la fachada y la ornamentación con fidelidad visual comparable a la fotografía.*

Esta asimetria entre esta comparativa de tecnicas es uno de los hallazgos mas importantes de esta tesis y esta vinculado tanto a la H1 como a la H3 combinadas: la calidad en el resultado no depende solamente de la complejidad geometrica sino que esta fuertemente vinculado a la tecnica de reconstruccion utilizada. Mientras 3DGS tolera la complejidad ornamental alta del Panteon, NeRF con el mismo dataset y el mismo registro de entrada de SfM ofrece un resultado inconcluso y lleno de errores. 

<h3 id="cap5-5-4-3">5.4.3 Fidelidad geométrica por caso — SfM</h3>

A continuacion vamos a analizar de forma especifica los resultados obtenidos en el procesamiento de fotogrametria y como estos han impactado en la reconstruccion de los tres edificios. 

En el caso de Los Paraguas podemos identificar que, si bien la geometria es simple y estan bien constituida, hay zonas de la malla generada que presentan ausencias o huecos, un error que se repitio tambien al momento de reconstruir la cubierta del Templete Central. Estas ausencias de continuidad en la reconstruccion pueden estar vinculadas a registros oscursos del dataset que posiblemente fueron generados por sombras o efectos de la luz al momento del registro. La reconstruccion en 3D del Panteon es una de las mas fieles de las tres, pese a la complejidad arquitectonica y ornamental de la obra. Tanto la nube densa de puntos como su reconstruccion en malla permiten identificar con precision la obra y tambien reproducir en detalle algunos aspectos interesantes de su fachada: como los ornamentos de la cubierta, el detalle del vidrio partido en la puerta (una forma tambien de constatar deterioro como propone al comienzo esta tesis), y detalles muy precisos del estado de sus paredes y sus accesos. 

![Vista lateral de la malla SfM — Los Paraguas](/content/assets/cap5-vista-lateral.webp)

*Figura 5.19 — Vista lateral de la malla SfM (RealityScan) de Los Paraguas, a nivel de piso. Columnas y cubierta se reconstruyen con nitidez y sin huecos visibles desde este ángulo; se aprecia la doble curvatura de la losa mencionada en el Capítulo 3 (sección 3.2.2), con el río de fondo.*

![Vista lateral de la malla SfM — Templete Central](/content/assets/cap5-vista-lateral-01.webp)

*Figura 5.20 — Vista lateral de la malla SfM (RealityScan) del Templete Central, a nivel de piso. Buen detalle de las nervaduras/molduras de la cara inferior de la losa y del ritmo de columnas; los objetos bajo la cubierta (carteles, elementos reflectantes) no quedan registrados con textura limpia.*

![Vista lateral de la malla SfM — Templete Central, ángulo cercano](/content/assets/cap5-vista-lateral-02.webp)

*Figura 5.21 — Segunda vista lateral del Templete Central, más cercana, con el piso empedrado en primer plano. Confirma la lectura de la Figura 5.20: buen detalle estructural de la losa y las columnas, con pérdida de calidad en los objetos y carteles bajo la cubierta.*

![](/content/assets/cap5-2026-09-01-16-22-50-image.png)

![](/content/assets/cap5-2026-09-01-16-25-50-image.png)

El analisis de las nubes densas de cada uno de los edificios nos permite entender con mayor precision la calidad de reconstruccion de esta tecnica. La identificacion de ascenso en la cantidad de puntos de cada modelo habla de el ascenso en la complejidad geometrica, y otro dato importante es el creciente outliner que asciende de un edificio a otro, lo cual indica tambien cierta degradacion entre una geometria de complejidad baja a una de complejidad alta. La distancia media a vecino mas cercano indica la dispersion de puntos, y tambien vemos que esta es mayor cuando la complejidad geometrica sube. 

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

Otra de las hipotesis que buscamos validar en esta investigacion esta vinculada con la posibilidad de obtener datasets enriquecidos por capturas de distintos dispositivos. Para conseguir muestras que nos permitan validar este experimento se utilizaron registros de dos camaras: DJI Neo 2, y la camara Insta360, y se realizaron pruebas que permitieran comparar un dataset hibrido, de dos datasets obtenido con ambas camaras por separado. Los resultados se analizaron en una comparativa de dos edificios, por un lado el Templete Central y por otro el Panteon. A continuacion analizamos los resultados:

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

El resultado mas recurrente al momento de generar el procesamiento de SfM de los dataset hibridos fue la generacion de varios componentes desconectados. El resultado que genero un 0.38% en el registro no solo genero componentes separados sino que fallo catastroficamente y no pudo continuar con el procesamiento. 

El siguiente diagrama muestra como RealityScan en un intento por reconstruir el camino de las camaras y generar la nube de puntos genera dos componentes distintos que buscan recrear el mismo edificio, por un lado uno a una escala y por otro lado otro que repite la geometria general de la obra pero con una escala superior. Estos resultados fueron registrados en RealityScan utilizando el dataset hibrido de Insta360 + DJI Neo 2 en la reconstruccion del Panteon. 

![](/content/assets/cap5-2026-09-01-17-19-01-image.png)

Algo muy parecido sucedio con el Templete Central, donde RealityScan reconstruyo dos componentes separados, por un lado una nube de puntos de 306 camaras identificadas (de un total de 1281), y por otro lado un segundo componente de 728 camaras (de un total de 1281 frames). Los intentos de alinear ambos componentes fallaron: RealityScan cuenta con una funcionalidad que permite seleccionar hasta seis puntos de referencia coincidentes entre ambos modelos con el fin de alinearlos en una segunda corrida. Estos intentos fallaron en ambos edificios generando nuevamente resultados de componentes dispersos y no una reconstruccion total. 

![](/content/assets/cap5-2026-09-01-17-22-11-image.png)

![](/content/assets/cap5-2026-09-01-17-23-52-image.png)

Pero RealityScan no fue la unica herramienta en intentar correr un proceso de COLMAP y fallar en el intento: en un intento por correr el proceso de reconstruccion utilizando COLMAP desde Nerfstudio el software corriendo en Docker registro un fallo catastrofico y demostro solo un 0,38% en su porcentaje de avance. Analizando el output y el resultado binario de COLMAP se llego a a conclusion de que se habian generado dos componentes desconectados en su reconstruccion y eso habia generado la falla. Si bien el primer componente tenia solo un 0,38%, el segundo logro un 100% en el posicionamiento de las 794 imagenes que encontro, y este segundo componente se utilizo como referencia de analisis para la evaluacion de los resultados de Nerfacto y Splatfacto dentro de Nerfstudio en la seccion 5.5.5.

Con el fin de identificar el patron de error al momento de generar la reconstruccion de SfM se corrieron al menos tres pruebas mas con datasets exploratorios, por un lado un procesamiento secuencial con un subset de DJI, otro de Insta360 corriendo fisheye secuencial como parametro de reconstruccion, y un tercero utilizando el subset de Insta360 pero en esta oportunidad seteando perspective secuencial como parametro. Los tres generaron resultados pobres logrando posicionar menos del 5% de los frames. 

Tan solo este antecedente ya marco un presedente en la investigacion que nos llevo a comprender que la reconstruccion de SfM tiene un indice de fallos alto y de registro pobre de camaras cuando los datasets contienen imagenes que provienen de distintos dispositivos. La complejidad en la reconstruccion puede estar vinculada al origen y las caracteristicas de los lentes de cada una de estas camaras, las diferencias en las caracteristicas de los frames (la resolucion, el peso, la calidad, etc), y la complejidad de utilizar SfM cuando el tipo de procesamiento no es secuencial (siendo el registro secuencial el caso mas feliz y simple al momento de procesar). 

La implicancia metodológica excede el caso puntual de esta tesis: **la tasa de registro reportada automáticamente por un wrapper de conversión SfM→Nerfstudio no debe aceptarse sin verificación cuando el dataset de entrada es heterogéneo** (múltiples dispositivos, múltiples orientaciones de lente, capturas no estrictamente secuenciales) — condiciones que, precisamente, son las que introduce H4 al combinar drone y cámara de acción. En ese sentido, este hallazgo es evidencia indirecta a favor de una de las premisas de H4: los datasets híbridos sí introducen mayores dificultades en el proceso de reconstrucción. La sección 5.5.3 profundiza en el mecanismo geométrico detrás de esa dificultad, a partir de una segunda corrida independiente sobre el mismo dataset.

<h3 id="cap5-5-5-3">5.5.3 Por qué fallan los datasets híbridos: calidad de matching cruzado entre dispositivos</h3>

Con el fin de seguir obteniendo comparativas entre distintos datasets, se procedio a realizar una segunda corrida de COLMAP nativo sobre el dataset hibrido del Templete (un dataset con 794 imagenes). El resultado fue nuevamente fallido: se obtuvieron posicionamiento de tan solo 5 camaras (un 0,63% del total). 

La siguiente Tabla contiene la comparacion del dataset del matching del COLMAP con el fin de interpretar que tan bien se entendieron las imagenes entre si durante el procesamiento. Los inliners promedio permiten entender que matching geometrico hubo entre imagenes, es decir, para aquellas imagenes que encontraron correspondencia entre si cuales tambien validaron otros aspectos de geometricas mas estricticas. Y ahi en este indicador es donde vemos el indice mas bajo, los datasets provenientes de la misma camara encontraron mayor correspondencia entre pares. 

Inliners maximo nos permite validar el mejor caso, y cada los resultados son contundentes: el mejor par cruzado (183 inliers) es peor que el promedio de un par DJI-DJI (689) o incluso el promedio de un par Insta360-Insta360 (189). 

A modo de sintesis podemos confirmar que el matching entre imagenes no es un problema, sino mas bien la correspondencia de geometrias una vez que el matching sucedio. Cuando se encuentran esta correspondencia entre camaras distintas el lazo entre pares es mas debil y por eso no logra generar componentes unificados.  

| Tipo de par       | Pares con algún match | Inliers promedio (pares con match) | Inliers máximo |
| ----------------- | --------------------- | ---------------------------------- | -------------- |
| DJI–DJI           | 48,9%                 | 689,1                              | 8.515          |
| Insta360–Insta360 | 45,7%                 | 189,0                              | 6.994          |
| **DJI–Insta360**  | 40,1%                 | **43,2**                           | **183**        |

*Tabla 5.10 — Calidad de matching por tipo de par de dispositivos, dataset híbrido de Templete Central. Fuente: `analyze_hybrid_cross_camera_matching.py`, sobre `database.db` de la corrida de matching exhaustivo.*

![Calidad de matching por tipo de par](/content/assets/cap5-hybrid-cross-camera-matching-chart.png)

*Gráfico 5.11 — Inliers geométricamente verificados (promedio y máximo), por tipo de par de dispositivos.*

<h3 id="cap5-5-5-4">5.5.4 Evidencia complementaria: calidad de render por dispositivo</h3>

En el Capitulo 4 se definio una metrica cuantitativa de cobertura reconstruida en porcentaje, pero dicha metrica no pudo conseguirse por la ausencia una nube de puntos que permita correr una comparativa del tipo TLS. Es por eso que para reemplazar esta evidencia, y con el fin de seguir validando la viabilidad de operar con un dataset hibrido pese a las conclusiones de SfM, se realizo un analisis en base al renderizado de Nerfacto y Splatfacto por dispositivo. 

El diseño original de B4 (Capítulo 4, sección 4.5) acota la comparación entre dispositivos a la etapa de SfM. Sin embargo, para el Templete Central y el Panteón Asociación Española también se entrenaron Nerfacto y Splatfacto por separado sobre el dataset Insta360 (con fines de documentación del caso, no como parte del diseño formal de B4), lo que permite una comparación DJI vs. Insta360 a nivel de calidad de render — evidencia complementaria a H4 que no estaba contemplada en el alcance original del benchmark, pero que es la única comparación de dispositivo pertinente para esta hipótesis (a diferencia de B1/B3, que fijan el dispositivo en DJI por diseño, sección 5.4.1).

![PSNR y SSIM por sitio, dispositivo y técnica](/content/assets/cap5-05-psnr-ssim-por-sitio.png)

*Gráfico 5.12 — PSNR (barras) y SSIM (línea) por sitio, dispositivo y técnica, las diez combinaciones medidas. Fuente: `build_comparison_charts.py`.*

![LPIPS por sitio, dispositivo y técnica](/content/assets/cap5-06-lpips-por-sitio.png)

*Gráfico 5.13 — LPIPS (distancia perceptual, más bajo es mejor) por sitio, dispositivo y técnica. Fuente: `build_comparison_charts.py`.*

Podemos deducir por el analisis del Grafico 5.13 que no hay un dispositivo mejor que otro para la captura, hay indices que muestras que el registro con DJI fue superior, y otros casos donde los resultados con Insta360 superan el dataset de DJI. Lo que si es consistente a modo de conclusion es que la utilizacion de un unico dispositivo durante todo el registro optimiza mucho el procesamiento, el matching de pared en COLMAP y la reconstruccion de un unico componente como geometria reconocida. En todos los casos en los cuales se utilizo un dataset hibrido los resultados fueron mas pobres y complicaron mucho la generacion del SfM incluso llegando a fallos catastroficos. 

![Comparación Foto / Nerfacto / Splatfacto — Templete Central, Insta360](/content/assets/cap5-comparacion-frame-00155.jpg)

*Figura 5.22 — Templete Central, dataset Insta360. Nerfacto (centro) introduce un patrón de distorsión radial concéntrica en los bordes de la vista sintetizada, ausente tanto en la fotografía original (izquierda) como en Splatfacto (derecha).*

Otra conclusion interesante de la comparativa de frames de renders indica que NeRF es mas sensible a la optica de la camara que otros tipos de procesamiento. Como vemos en la Figura 5.22 el render de NeRF muestra que se generaron circunferencias radicales que marcan la lente gran angular del dispositivo marcando el efecto de ojo de pez del lente. 3DGS no tiene registro de las caracteristicas del lente, a pesar de haber generado una reconstruccion fiel del dataset en los resultados. 

<h3 id="cap5-5-5-5">5.5.5 Resultado de reconstrucción sobre el dataset híbrido — contraste directo de H4</h3>

Como se indico de forma previa, la segunda corrida de COLMAP para el dataset hibrido genero al menos un componente con 794 caramas registradas. Este SfM fue procesado con NeRF y Splat tambien en NerfStudio y se llego a la siguiente conclusion: en ninguna de las dos tecnicas el dataset hibrido supero las metricas de los datasets que utilizan imagenes de un unico dispositivo. Una afirmacion que nos permite confirmar que la hipotesis H4 no se valida. Combinar dispositivos no solo genera conflictos al momento de generar procesamientos de SfM, sino que cuando conseguimos reconstruir algun componente la comparativa con otros datasets indica que los resultados tampoco son superiores.

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

Con el fin de definir el impacto del dataset hibrido sobre el caso de mayor complejidad arquitectonica, se suma un analisis mas para terminar de definir si la hipotesis H4 queda finalmente invalidada. La primera parte de esta investigacion fue la generacion de un proceso de COLMAP sobre el dataset hibrido de DJI y Insta360 (Compuesto por 974 imagenes). El proceso corrio en una instancia de Docker y se utilizo NerfStudio, y se trato de una ejecucion de 83 horas, la mas extensa de todas las que conforman esta tesis. El componente principal registró 910 de las 974 imágenes (93,4%, verificado sobre `images.bin`); el resto quedó repartido en ocho componentes desconectados de 21 a 41 imágenes cada uno, el mismo patrón de fragmentación que ya vimos en el Templete Central. 

Exportamos ese componente principal a Nerfstudio y entrenamos Nerfacto (subset de 228 imágenes, una de cada 4, por la misma limitación de memoria de siempre) y Splatfacto (las 910 imágenes completas, downscale×8) — mismo procedimiento que usamos para el Templete Central.

Repetimos acá el mismo análisis de matching cruzado de la sección 5.5.3, sobre el `database.db` de esta corrida (frame_00001–00608 = DJI, 608 imágenes; frame_00609–00973 = Insta360, 365 imágenes). Las conclusiones son muy parecidas a las del Templete Central: dentro del dataset híbrido, los pares cruzados DJI-Insta360 tienen un inliers máximo mucho más bajo (811) que los pares del mismo dispositivo (7.748 en DJI-DJI, 5.342 en Insta360-Insta360), y también un inliers promedio bastante inferior (49,9 contra 647,3 y 170,0). Se repite el mismo patrón: encontrar matches entre imágenes no es el problema (los tres tipos de par lo logran en porcentajes parecidos), pero cuando el par es cruzado, la correspondencia geométrica que se verifica después es mucho más débil — y esa debilidad es la que genera inconsistencia en los resultados.

| Tipo de par       | Pares con algún match | Inliers promedio (pares con match) | Inliers máximo |
| ----------------- | --------------------- | ---------------------------------- | -------------- |
| DJI–DJI           | 31,6%                 | 647,3                              | 7.748          |
| Insta360–Insta360 | 25,1%                 | 170,0                              | 5.342          |
| **DJI–Insta360**  | 17,6%                 | **49,9**                           | **811**        |

*Tabla 5.12 — Calidad de matching por tipo de par de dispositivos, dataset híbrido del Panteón Asociación Española. Fuente: `analyze_hybrid_cross_camera_matching_panteon.py`, sobre `database.db` de la corrida `run-20260827-163722`.*

![Calidad de matching por tipo de par, Panteón Asociación Española](/content/assets/cap5-hybrid-cross-camera-matching-chart-panteon.png)

*Gráfico 5.15 — Inliers geométricamente verificados (promedio y máximo), por tipo de par de dispositivos, Panteón Asociación Española.*

El patrón se repite calcado al del Templete Central: DJI-DJI tiene los inliers más altos, Insta360-Insta360 queda en el medio, y DJI-Insta360 es sistemáticamente el más débil — acá 13 veces menos inliers promedio que DJI-DJI (647,3 vs. 49,9), en línea con las 16 veces del Templete Central. Lo que sí cambia es que el porcentaje de pares que logra algún match es más bajo en los tres tipos (31,6%/25,1%/17,6% contra 48,9%/45,7%/40,1% del Templete Central) — pero esto parece ser un tema de la escena (el Panteón es más alto y más complejo ornamentalmente) y no del dispositivo, porque afecta parejo a los tres tipos de par. Que el matching cruzado débil se repita así de fuerte en un segundo caso, con otro equipo de captura y otro edificio completamente distinto, es la evidencia más sólida de esta tesis de que es una propiedad estructural de mezclar dispositivos con óptica distinta, no una rareza puntual del Templete Central.

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

El entrenamiento fue más rápido en las dos técnicas que con el dataset DJI solo (Splatfacto híbrido: 23 min vs. 36 min 15 s; Nerfacto híbrido: 39 min vs. 1 h 38 min 35 s) — lógico, porque el dataset de entrada es más chico (910 y 228 imágenes contra 1507 y 302), el mismo patrón que ya vimos en el Templete Central.

Con los dos casos híbridos ya completos, la evidencia a favor de H4 queda sólida por dos lados. A nivel de mecanismo: la debilidad del matching cruzado DJI-Insta360 no fue una rareza del Templete Central — se repite con la misma jerarquía (DJI-DJI > Insta360-Insta360 > DJI-Insta360) y una magnitud parecida (13× menos inliers en el Panteón, 16× en el Templete Central) en un sitio totalmente distinto. A nivel de resultado: en 3 de las 4 combinaciones técnica × caso evaluadas, el dataset híbrido rindió peor que cualquiera de los dos dispositivos solos, sin excepción. La única que no sigue ese patrón (Nerfacto/Panteón) no lo hace porque el híbrido haya sido bueno, sino porque el punto de comparación —Nerfacto solo con DJI— ya era en sí mismo un resultado inutilizable.

<h2 id="cap5-5-6">5.6 B5 — Compatibilidad web y reproducibilidad (H5)</h2>

La Tabla 5.14 reproduce el checklist de compatibilidad documental de formatos elaborado en el Capítulo 4 (sección 4.5, B5).

| Técnica           | Formato de output                | Visor(es) compatibles              | Conversión adicional requerida                                                         |
| ----------------- | -------------------------------- | ---------------------------------- | -------------------------------------------------------------------------------------- |
| SfM               | .obj/.mtl/textura → .glTF        | Three.js, Sketchfab, Potree        | Sí — conversión .obj → .glTF no es un paso nativo del pipeline actual                  |
| NeRF (Nerfacto)   | checkpoint .ckpt (pesos del MLP) | Ninguno de forma nativa            | Sí — requiere derivar video o nube de puntos; sin formato de distribución web estándar |
| 3DGS (Splatfacto) | .splat/.ply vía SuperSplat       | Visor web de SuperSplat, Sketchfab | No — export directo                                                                    |

*Tabla 5.14 — Checklist de compatibilidad web por técnica (evaluación documental). Fuente: Capítulo 4, sección 4.5 (B5).*

El hallazgo más claro de esta evaluación —aun sin la validación de carga real en visor, todavía pendiente— es que **NeRF es la técnica menos apta de las tres para el objetivo de un archivo digital de patrimonio de acceso web**, precisamente el objetivo aplicado central de esta tesis (Capítulo 1). Splatfacto y SfM tienen una ruta directa (o casi directa) a un visor web estándar; Nerfacto requiere un paso de conversión adicional no contemplado en el pipeline actual, lo que la posiciona mejor para producción audiovisual/documentales (síntesis de vistas, video) que para publicación interactiva — un matiz que refina H1 tal como está formulada en el Capítulo 1 (que ya anticipaba esta especialización) y que se retoma en la propuesta de pipeline del Capítulo 6.

La carga efectiva de al menos un modelo de cada técnica en un visor real queda pendiente de ejecución (Capítulo 4, sección 4.5, B5).

<h2 id="cap5-5-7">5.7 Tasa de fallos, por sitio</h2>

La Tabla 5.15 resume los eventos de fallo detectados en los logs de procesamiento y entrenamiento (no incluye la etapa de SfM, cubierta en la sección 5.5).

| Caso                        | Fallos catastróficos | Inestabilidad de convergencia | Detalle                                                                                                                                                                            |
| --------------------------- | -------------------- | ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Los Paraguas                | 2                    | 0                             | OOM de sistema y SIGKILL durante la fusión densa de COLMAP (`colmap stereo_fusion`)                                                                                                |
| Templete Central            | 3                    | 0                             | Archivo de entrada faltante (`transforms.json`); excepción de configuración (`not_use_single_camera_mode` solo funciona con `hloc`); archivo faltante en dataset ds8 de Splatfacto |
| Panteón Asociación Española | 0                    | 1 (3 reintentos)              | Reintentos del entrenamiento de Nerfacto (`04_nerfstudio_nerf_train`, 3 corridas)                                                                                                  |

*Tabla 5.15 — Tasa de fallos por sitio. Fuente: `analyze_failure_rate.py`.*

![Fallos por sitio](/content/assets/cap5-04-fallos-por-sitio.png)

*Gráfico 5.17 — Fallos catastróficos e inestabilidad de convergencia detectados en logs, por sitio.*

A esta tabla debe sumarse el **fallo parcial** de Nerfacto sobre el Panteón Asociación Española (dataset DJI, sección 5.4.2): un output que sí se generó (no catastrófico según la clasificación de la sección 4.9) pero que resultó inutilizable para fines de documentación patrimonial por la presencia masiva de floaters — la categoría de fallo más relevante para H3, y la que menos se refleja en un conteo automático de excepciones de log, dado que requiere la inspección visual cualitativa que sí se realizó en este capítulo (Figura 5.18).

El Templete Central concentra la mayor cantidad de fallos catastróficos (3), en línea con ser el caso donde se probaron más variantes de dataset y configuración (subset secuencial, matching exhaustivo híbrido, múltiples estrategias de Insta360) — es decir, buena parte de estos fallos son atribuibles a la etapa exploratoria del proyecto más que a una fragilidad intrínseca del caso frente a Los Paraguas o el Panteón.

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

La brecha de peso entre SfM y las otras dos técnicas es de uno a dos órdenes de magnitud (3,9–4,0 GB vs. 75–170 MB), impulsada por la resolución de textura fija de 8192×8192 px adoptada en el pipeline de RealityScan. Esto tiene una implicancia directa para H5 y para el Capítulo 6: la malla SfM, aun siendo la más apta para integración BIM (sección 5.2.3), es la menos práctica de las tres para distribución web sin un paso adicional de decimación/compresión de textura, algo que el pipeline definitivo del Capítulo 6 debería contemplar explícitamente.

<h2 id="cap5-5-9">5.9 Tiempo de procesamiento</h2>

| Caso                        | Nerfacto        | Splatfacto      |
| --------------------------- | --------------- | --------------- |
| Los Paraguas                | 55 min 32 s     | 1 h 13 min 17 s |
| Templete Central            | 46 min 1 s      | 33 min 41 s     |
| Panteón Asociación Española | 1 h 38 min 35 s | 36 min 15 s     |

*Tabla 5.17 — Tiempo de entrenamiento (30 000 iteraciones) por caso y técnica (dataset DJI, el mismo criterio de B1/B3 — sección 5.4.1). Los tiempos de los datasets Insta360 están documentados en `00-auditoria/processing-time/`; el tiempo de procesamiento no es una métrica definida para H4 (Capítulo 4, sección 4.3.5), por lo que no se comparan aquí entre dispositivos. Fuente: `analyze_processing_time.py`, medido sobre las carpetas de trabajo originales (Capítulo 4, sección 4.3.6).*

A diferencia del peso de archivo, el tiempo de entrenamiento no muestra un patrón consistente entre técnicas: Splatfacto es más rápido que Nerfacto en Los Paraguas y el Templete Central, pero más lento en el Panteón (36 min 15 s vs. 1 h 38 min 35 s de Nerfacto) — el único caso donde Nerfacto entrena más lento que Splatfacto es, a su vez, el caso donde el output de Nerfacto resultó inutilizable (fallo parcial, sección 5.4.2), lo que sugiere que el tiempo elevado podría estar asociado al mismo problema de divergencia del entrenamiento y no a una propiedad estable de la técnica.

<h2 id="cap5-5-10">5.10 Síntesis por hipótesis</h2>

**H1 — Especialización por técnica:** parcialmente confirmada, con matices no anticipados en el planteo original. SfM es, en efecto, la técnica más apta para integración BIM (malla explícita, sección 5.2.3) y la de mayor peso de archivo (sección 5.8). Splatfacto no solo iguala sino que supera consistentemente a Nerfacto en PSNR/SSIM en los tres casos (Tabla 5.7), además de ofrecer mejor tiempo de entrenamiento en dos de los tres sitios DJI y el mejor equilibrio de compatibilidad web (sección 5.6) — su especialización original ("renderizado en tiempo real") queda corroborada, pero la evidencia sugiere que además es, en este conjunto de experimentos, la técnica de mejor desempeño general entre las tres. Nerfacto muestra su mayor fragilidad exactamente donde H1 anticipaba su fortaleza relativa (síntesis de vistas fotorrealista): con complejidad geométrica alta (Panteón) su output resultó inutilizable (fallo parcial, sección 5.7).

**H2 — Preprocesamiento:** se acepta parcialmente, con un matiz que depende de la técnica. La comparación de reconstrucción sobre el Dataset B curado con ComfyUI (sección 5.3.4) es comparable 1:1 en ambas técnicas. En Splatfacto, el preprocesamiento no mejora la fidelidad píxel a píxel (PSNR −1,3 dB, SSIM sin cambios significativos) pero sí la similitud perceptual (LPIPS −32%), con un efecto no uniforme entre frames según la complejidad de la textura de fondo. En Nerfacto, en cambio, el mismo preprocesamiento empeora las tres métricas sin excepción (PSNR −2,38 dB, SSIM −0,109, LPIPS casi 3,5× peor) — el beneficio perceptual que sí aparece en Splatfacto no se replica. H2 depende, entonces, no solo de qué se limpia sino de con qué técnica se reconstruye después.

**H3 — Complejidad geométrica:** confirmada para Nerfacto (caída monótona de PSNR, sección 5.4.2), no confirmada de forma directa para Splatfacto (patrón no monótono, con recuperación en el caso de mayor complejidad). La lectura más ajustada a la evidencia es que la complejidad geométrica y ornamental afecta negativamente el desempeño de reconstrucción, pero su efecto está mediado —y en el caso de Splatfacto, posiblemente dominado— por la calidad del registro SfM de entrada, una interacción no contemplada en el planteo original de H3 y que constituye uno de los aportes empíricos de esta tesis.

**H4 — Dataset multi-dispositivo:** en conjunto, la evidencia recogida respalda H4 con más fuerza que cualquier otra hipótesis de esta tesis. El registro SfM final de los datasets solo-DJI y solo-Insta360 fue alto en ambos casos de estudio híbridos (85%–100%, Tabla 5.9), lo que por sí solo no sugiere dificultad. Pero al combinar ambos dispositivos en un único dataset, dos corridas independientes de COLMAP nativo sobre el mismo dataset híbrido del Templete Central dieron resultados opuestos —una terminó en un único componente con 100% de registro (sección 5.5.2), la otra en apenas 0,63% (sección 5.5.3)—, una inestabilidad que **no ocurre con los datasets de un único dispositivo** en ningún caso de esta tesis. La sección 5.5.3 identifica además un mecanismo geométrico concreto detrás de esa inestabilidad: los matches entre imágenes DJI e Insta360 son sistemáticamente mucho más débiles (43 inliers promedio) que los matches dentro de un mismo dispositivo (689 en DJI-DJI, 189 en Insta360-Insta360) — el "puente" que conecta ambos clusters en la reconstrucción es frágil, y su éxito o fracaso parece depender de la traza particular del algoritmo incremental más que de una propiedad estable del dataset. Este mismo mecanismo se replicó, de forma independiente, sobre el dataset híbrido del Panteón Asociación Española (sección 5.5.6, Tabla 5.12): la misma jerarquía DJI-DJI > Insta360-Insta360 > DJI-Insta360 y una brecha del mismo orden de magnitud (13× menos inliers promedio, frente a 16× en el Templete Central) — dos sitios con geometrías, condiciones de captura y hasta corridas de COLMAP completamente independientes muestran el mismo patrón, lo que eleva este hallazgo de una observación puntual del Templete Central a una **propiedad estructural** del matching cruzado entre dispositivos ópticamente distintos. La evidencia complementaria de calidad de render por dispositivo (sección 5.5.4) es consistente con esta lectura: el efecto de usar Insta360 en lugar de DJI no es uniforme —leve en el Templete Central, marcado y de signo variable por técnica en el Panteón—, lo que sugiere que el resultado final depende más de la calidad del registro SfM logrado en cada corrida que del dispositivo en sí. La comparación directa de calidad de render del dataset **combinado** frente a los datasets de un único dispositivo —la comparación que realmente formula H4— se completó para **los dos** casos de estudio con dataset multi-dispositivo de esta tesis (Templete Central, sección 5.5.5; Panteón Asociación Española, sección 5.5.6) y es la evidencia más contundente a favor de la hipótesis en todo este trabajo: en 3 de las 4 combinaciones técnica × caso evaluadas, el dataset híbrido rinde peor que **cualquiera** de los dos dispositivos por separado, en las tres métricas de calidad, sin excepción; la única combinación restante (Nerfacto/Panteón) no la contradice, sino que mejora marginalmente sobre un punto de comparación que ya era, de por sí, un resultado inutilizable (fallo parcial, sección 5.4.2). Combinar dispositivos no solo arriesga la estabilidad del registro (secciones 5.5.2–5.5.3): incluso cuando el registro sale razonablemente bien (93,4%–100% entre ambos casos), el resultado final es, sistemáticamente, inferior al de un único dispositivo.

**H5 — Compatibilidad web y reproducibilidad:** evidencia documental a favor de una especialización clara entre técnicas (sección 5.6): SfM y Splatfacto tienen rutas de publicación web directas o casi directas; Nerfacto no. La validación experimental completa (carga real de al menos un modelo de cada técnica en un visor web) queda pendiente.

<h2 id="cap5-5-11">5.11 Experimento adicional: reconstrucción a partir de material audiovisual de terceros — Torre Tanque, Mar del Plata</h2>

Como validación adicional, fuera del diseño experimental del Capítulo 4 y de los criterios de selección de casos de estudio del Capítulo 3 (sección 3.1), se corrió el mismo pipeline de reconstrucción (SfM + Nerfacto + Splatfacto) sobre un dataset construido a partir de material audiovisual de terceros, no de un registro propio: un video de dron de acceso público sobre la Torre Tanque en Mar del Plata, publicado en YouTube ("Mar del Plata – Acercamiento a la Histórica Torre Tanque (Drone)", https://www.youtube.com/watch?v=tTOj-kyXqLk). El objetivo de este experimento es validar si el pipeline definido en esta tesis puede aplicarse sobre material capturado bajo un protocolo que no controlamos —dispositivo, altura, velocidad de vuelo y condiciones de luz desconocidos—, a diferencia de los tres casos de estudio principales, todos capturados bajo el protocolo propio descrito en el Capítulo 3 (sección 3.6).

Del video se extrajeron 142 fotogramas, que se procesaron con COLMAP para obtener las poses de cámara y luego se entrenaron ambas técnicas (Nerfacto y Splatfacto, 30 000 iteraciones cada una) siguiendo el mismo procedimiento aplicado al resto de los casos de estudio.

| Técnica    | PSNR (dB) | SSIM  | LPIPS |
| ---------- | --------- | ----- | ----- |
| Nerfacto   | 19,24     | 0,511 | 0,183 |
| Splatfacto | 30,90     | 0,934 | 0,064 |

*Tabla 5.18 — Torre Tanque (Mar del Plata): métricas de render sobre el dataset construido a partir de material de terceros. Fuente: `ns-eval`.*

![PSNR/SSIM/LPIPS Nerfacto vs Splatfacto — Torre Tanque](/content/assets/cap5-torre-mardel-psnr-ssim-lpips.png)

*Gráfico 5.19 — PSNR, SSIM y LPIPS sobre el dataset de la Torre Tanque, por técnica. Fuente: `build_torre_mardel_comparison_chart.py`.*

![Comparación Foto original / Nerfacto / Splatfacto — Torre Tanque](/content/assets/cap5-torre-mardel-visual-comparison.jpg)

*Figura 5.24 — Torre Tanque (Mar del Plata), comparación visual sobre un mismo fotograma de evaluación. Splatfacto reproduce la geometría de la torre y la textura urbana circundante con nitidez cercana a la fotografía original; Nerfacto muestra pérdida de detalle notable, en particular en la vegetación y la trama urbana de fondo — consistente con la brecha de PSNR/SSIM de la Tabla 5.18.*

La brecha entre técnicas es mayor a la observada en los tres casos de estudio principales sobre el caso de referencia (Tabla 5.2: Nerfacto 19,47 dB / Splatfacto 23,57 dB en Templete Central), lo que es compatible con la hipótesis de que un dataset de origen no controlado —sin garantía de solapamiento angular uniforme ni de estabilidad de iluminación (Capítulo 3, sección 3.6.2)— penaliza más al campo implícito de Nerfacto que a la representación explícita de gaussianas de Splatfacto. Splatfacto exportó una nube de 125,6 MB en formato .ply, dentro del mismo orden de magnitud que los exports de los casos de estudio principales (Tabla 5.16). No fue posible reconstruir de forma confiable el tiempo de entrenamiento de este experimento a partir de los metadatos de archivo disponibles, a diferencia del resto de los casos (sección 5.9).

Este resultado no reemplaza ni se compara en pie de igualdad con los tres casos de estudio principales —no hay protocolo de captura controlado, ni criterio de complejidad geométrica o valor patrimonial verificado (Capítulo 3, sección 3.1)—, pero es evidencia a favor de que el pipeline definido en esta tesis es aplicable más allá de las capturas propias, y que Splatfacto sostiene su ventaja de robustez incluso ante condiciones de captura no controladas.

<h2 id="cap5-5-12">5.12 Cierre del capítulo</h2>

De los cinco benchmarks diseñados en el Capítulo 4, los cinco se ejecutaron con resultados completos y comparaciones 1:1 (B1, B2, B3, B4, B5 en su componente documental) — B2 incluye, además de la comparación de Splatfacto ya cerrada desde el primer momento, el reentrenamiento de Nerfacto/raw a `downscale_factor 4` (2026-08-31) que resolvió el confound que dejaba su comparación sin lectura concluyente (sección 5.3.4). B4 incluye, además del hallazgo metodológico original sobre componentes desconectados, la reconstrucción completa de los datasets híbridos rescatados en **ambos** casos de estudio con dataset multi-dispositivo y su comparación de calidad de render contra los datasets de un único dispositivo (Templete Central, sección 5.5.5; Panteón Asociación Española, sección 5.5.6) — la evidencia más contundente de toda esta tesis a favor de una de las cinco hipótesis. La evidencia recogida permite, no obstante, una lectura sustantiva de cuatro de las cinco hipótesis de trabajo. Dos hallazgos destacan por encima del resto: la interacción no anticipada entre complejidad geométrica y calidad de registro SfM como determinantes conjuntos del desempeño de Splatfacto (sección 5.4.2), y la evidencia reunida en torno a H4 sobre la fragilidad de los datasets híbridos multi-dispositivo —componentes de reconstrucción desconectados con reporte automático engañoso en una corrida (sección 5.5.2), una segunda corrida del mismo dataset con un resultado real de registro casi nulo (sección 5.5.3), y un mecanismo geométrico identificado y cuantificado que explica ambos resultados: los matches entre imágenes de distintos dispositivos son sistemáticamente mucho más débiles que los matches dentro de un mismo dispositivo (sección 5.5.3)—. Estos resultados, junto con las limitaciones y tareas pendientes identificadas en cada sección, se traducen en el Capítulo 6 en un pipeline definitivo documentado y en criterios prácticos de selección de técnica según el objeto patrimonial a relevar.

*— Continúa en Capítulo 6: Pipeline Definitivo y Propuesta de Integración HBIM —*
