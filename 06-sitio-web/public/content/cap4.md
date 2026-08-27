Este capítulo tiene como finalidad profundizar acerca del diseño experimental de la investigación de esta tesis. El foco va a ser detallar en profundidad las hipótesis que se sugieren de forma resumida durante el Capítulo 1, entender las variables que entran en juego al momento de definir las conclusiones de cada uno de los experimentos, las métricas que van a evaluarse de forma aplicada y entender en profundidad cómo está conformado el software elegido para la ejecución del pipeline y por qué se eligió ese stack tecnológico.

Es fundamental comprender el rol que ocupa dentro de este diseño experimental los tres casos de estudio elegidos, (Los Paraguas de Amancio Williams, el templete del Sexto Panteón de Chacarita y el Panteón de la Asociación Española de Socorros Mutuos, también dentro del cementerio de la Chacarita), que conteniendo un nivel de complejidad arquitectónica variable entran en juego dentro de este experimento para ofrecernos un panorama más completo sobre el potencial de los algoritmos de reconstrucción en tres dimensiones. Este capítulo opera como un puente de conexión entre el Capítulo 2 donde planteamos el marco teórico, el Capítulo 3 donde profundizamos acerca de los casos de estudio y la adquisición de datos, y el Capítulo 5 donde ya se profundizan con mayor detalle los resultados obtenidos.

<h2 id="cap4-4-1">4.1 Hipótesis operacionales</h2>

A continuación se especifican las hipótesis operacionales de esta investigación, con afirmaciones específicas, falsificables y medibles que van a guiar el curso de cada uno de los experimentos con el fin de lograr validación.

**H1 — Adecuación de las técnicas según las características arquitectónicas**

SfM, NeRF y 3DGS presentan diferentes ventajas y limitaciones según las características del objeto arquitectónico relevado. Su desempeño varía en función de aspectos como la complejidad geométrica, la presencia de ornamentos y detalles, y la predominancia de geometrías simples o regulares. En consecuencia, no existe una técnica óptima para todos los casos, sino que cada una resulta más adecuada para determinados tipos de arquitectura y propósitos de representación.

La comparación de los casos de estudio permitirá identificar estas diferencias y establecer criterios prácticos para la selección de SfM, NeRF o 3DGS según las características del patrimonio arquitectónico a documentar y el uso previsto del modelo resultante.

> **Criterio de contrastación**: *H1 será evaluada mediante la comparación del desempeño relativo de SfM, NeRF y 3DGS en casos de estudio con diferentes características arquitectónicas, identificando fortalezas, limitaciones y aplicaciones más adecuadas para cada técnica.*

**H2 — Incidencia del preprocesamiento del dataset**

El preprocesamiento de las imágenes, orientado a reducir elementos distractores y aislar visualmente el objeto arquitectónico de interés, tiene una incidencia positiva en los resultados obtenidos mediante las técnicas de reconstrucción 3D evaluadas.

Esta hipótesis será contrastada sobre un único caso de estudio, comparando los resultados obtenidos a partir del dataset original con aquellos generados a partir del mismo dataset luego de aplicar el pipeline de preprocesamiento propuesto.

> **Criterio de contrastación**: *Se seleccionará un único caso de estudio y se procesará a partir de dos versiones del mismo conjunto de imágenes: el dataset original (raw) y el dataset sometido al pipeline de preprocesamiento. Los resultados obtenidos serán comparados mediante indicadores cuantitativos y cualitativos de calidad, con el objetivo de determinar si el preprocesamiento produce mejoras y en qué aspectos estas resultan más significativas.*

**H3 — Incidencia de la complejidad arquitectónica**

La complejidad geométrica y ornamental del objeto arquitectónico influye negativamente en la calidad de los resultados obtenidos mediante las técnicas de reconstrucción 3D evaluadas. Se espera que los objetos de geometría más simple produzcan reconstrucciones de mayor calidad, mientras que el aumento de la complejidad, el detalle y la ornamentación genere mayores dificultades y una progresiva pérdida de calidad en los resultados.

Esta hipótesis será contrastada mediante los tres casos de estudio seleccionados, correspondientes a niveles de complejidad arquitectónica baja, media y alta.

> **Criterio de contrastación**: *Se compararán los resultados obtenidos para los tres casos de estudio, clasificados según niveles de complejidad arquitectónica baja, media y alta. Se analizará si el aumento de la complejidad geométrica y ornamental se corresponde con una disminución de la calidad de las reconstrucciones, considerando indicadores cuantitativos y cualitativos comunes a los casos evaluados.*

**H4 — Incidencia del uso de múltiples dispositivos de captura**

La utilización de imágenes provenientes de distintos dispositivos de captura puede influir en el desempeño de la reconstrucción mediante SfM, debido a las diferencias entre cámaras, lentes y características de las imágenes obtenidas. Se espera que los datasets híbridos proporcionen una mayor diversidad de puntos de vista y cobertura del objeto arquitectónico, aunque la combinación de dispositivos puede introducir mayores dificultades durante el proceso de reconstrucción.

Esta hipótesis será evaluada específicamente en la etapa de SfM, comparando el caso de Los Paraguas de Amancio Williams, cuyo dataset fue obtenido íntegramente mediante un único dispositivo (DJI Neo 2), con los otros dos casos de estudio, cuyos datasets combinan imágenes obtenidas mediante DJI Neo 2 e Insta360 X5.

> **Criterio de contrastación**: *Se comparará el desempeño de SfM entre el dataset obtenido mediante un único dispositivo y los datasets compuestos por imágenes provenientes de diferentes dispositivos. La comparación considerará la capacidad de SfM para estimar y registrar correctamente las cámaras, la completitud de la reconstrucción y la presencia de errores o zonas no reconstruidas. El análisis permitirá determinar si la utilización de datasets híbridos representa una ventaja o una limitación para la reconstrucción geométrica inicial.*

**H5 — Aptitud para la creación de un archivo digital web**

Los resultados obtenidos mediante SfM, NeRF y 3DGS presentan diferentes grados de compatibilidad y aptitud para su publicación y visualización en entornos web. Se espera que alguna de estas técnicas ofrezca un mejor equilibrio entre calidad de representación, facilidad de acceso, rendimiento y compatibilidad con herramientas de visualización web, resultando más adecuada para la creación de un archivo digital de patrimonio arquitectónico de acceso público.

Esta hipótesis será evaluada a partir de los resultados obtenidos para los tres casos de estudio, comparando las posibilidades y limitaciones de publicación web de los modelos generados mediante cada una de las técnicas.

> **Criterio de contrastación**: *Los resultados obtenidos mediante SfM, NeRF y 3DGS para los tres casos de estudio serán evaluados en función de su aptitud para formar parte de un archivo digital de acceso web. Se considerarán aspectos como la compatibilidad con visores web, la facilidad de publicación y acceso, el rendimiento durante la visualización y la calidad de representación obtenida. La comparación permitirá identificar qué técnica y tipo de resultado resulta más adecuado para este propósito.*

<h2 id="cap4-4-2">4.2 Casos de estudio y su rol en el diseño experimental</h2>

Los tres casos de estudio seleccionados cumplen funciones diferenciadas dentro del diseño experimental, de acuerdo con las hipótesis planteadas. En lugar de aplicar la totalidad de los experimentos sobre los tres edificios, cada hipótesis se evalúa sobre los casos necesarios para responder a la pregunta específica que plantea. Esta estrategia permite reducir la cantidad de procesamientos y mantener un alcance experimental acorde con los objetivos de la investigación.

Los casos fueron seleccionados originalmente por presentar diferentes características geométricas y ornamentales, permitiendo establecer tres niveles relativos de complejidad arquitectónica: baja, media y alta. Esta diferenciación constituye la variable principal para la evaluación de H3 y, al mismo tiempo, permite analizar en H1 el comportamiento de las tres técnicas frente a objetos arquitectónicos de características diferentes.

H1 se evalúa sobre los tres casos de estudio mediante la comparación de los resultados obtenidos con SfM, NeRF y 3DGS, con el objetivo de identificar las ventajas, limitaciones y posibles aplicaciones de cada técnica según las características del objeto arquitectónico.

H3 utiliza los tres casos de estudio y su clasificación en niveles de complejidad baja, media y alta. La comparación permite analizar si el incremento de la complejidad geométrica y ornamental se relaciona con una disminución de la calidad de las reconstrucciones obtenidas.

Para H2, vinculada con la incidencia del preprocesamiento de las imágenes, se selecciona **Los Paraguas de Amancio Williams** como único caso de experimentación. Sobre este edificio se comparan los resultados obtenidos a partir del dataset original y de su versión preprocesada, manteniendo constantes las restantes condiciones de procesamiento.

H4 se concentra exclusivamente en la etapa de reconstrucción mediante SfM y compara el comportamiento de datasets obtenidos mediante diferentes estrategias de captura. Los Paraguas de Amancio Williams representa el caso de dataset homogéneo, registrado íntegramente mediante DJI Neo 2, mientras que los casos del Sexto Panteón y del Panteón de la Asociación Española corresponden a datasets híbridos, compuestos por imágenes provenientes del DJI Neo 2 y de la Insta360 X5. La comparación busca determinar la incidencia que puede tener la combinación de dispositivos sobre la reconstrucción inicial mediante SfM. Dado que los datasets corresponden a edificios diferentes, los resultados serán interpretados de manera comparativa y no como un experimento controlado exclusivamente por la variable dispositivo.

Finalmente, H5 reutiliza los resultados generados mediante SfM, NeRF y 3DGS para los tres casos de estudio, evaluándolos desde la perspectiva de su compatibilidad y aptitud para la publicación en un archivo digital de patrimonio arquitectónico de acceso web. Esta instancia no requiere generar nuevas reconstrucciones, sino analizar los modelos obtenidos en las etapas anteriores según criterios específicos de publicación, acceso, rendimiento y calidad de representación.

|                                          | **Los Paraguas** | **Sexto Panteón** | **Asociación Española** |
|------------------------------------------|------------------|-------------------|-------------------------|
| **SfM**                                  | ✓                | ✓                 | ✓                       |
| **NeRF**                                 | ✓                | ✓                 | ✓                       |
| **3DGS**                                 | ✓                | ✓                 | ✓                       |
| **Preprocesamiento raw vs. curado (H2)** | —                | ✓                 | —                       |
| **Dataset homogéneo/híbrido – SfM (H4)** | Homogéneo        | Híbrido           | Híbrido                 |
| **Evaluación web (H5)**                  | ✓                | ✓                 | ✓                       |

*Tabla 4.1 — Matriz de relación entre casos de estudio, técnicas y benchmarks experimentales.*

<h2 id="cap4-4-3">4.3 Variables del experimento</h2>

<h3 id="cap4-4-3-1">4.3.1 Variable independiente principal: el algoritmo de reconstrucción</h3>

La variable independiente principal es la técnica de reconstrucción 3D utilizada, con tres niveles: (1) fotogrametría SfM+MVS, (2) NeRF, y (3) 3D Gaussian Splatting. Las tres técnicas se implementan sobre un único framework unificado, RealityCapture y COLMAP desde Nerfstudio para SfM (eligiendo el resultado con mejor matches entre cantidad de imágenes del dataset y poses y camaras registradas en el procesamiento) y Nerfstudio con Nerfacto y Splatfacto para generar el procesamiento NeRF y el Gaussian Splatting a partir de esa misma estructura de nube de puntos y posicionamiento de cámaras. Esta variable define los benchmarks B1 (sobre el caso de referencia) y B3 (sobre los tres casos de estudio), que constituyen el aporte central de la investigación.

<h3 id="cap4-4-3-2">4.3.2 Variable de complejidad geométrica</h3>

Como variable independiente adicional se introduce la complejidad geométrica y ornamental del caso de estudio, con tres niveles ordinales: baja (Los Paraguas), media (templete de Chacarita) y alta (Panteón de la Asociación Española), siguiendo la caracterización cualitativa desarrollada en el Capítulo 3. Esta variable, cruzada con la variable de técnica, define el benchmark B3 y constituye la operacionalización experimental de H3.

<h3 id="cap4-4-3-3">4.3.3 Variable de composición del dataset (multi-dispositivo)</h3>

Como variable independiente adicional se introduce la composición del dataset de entrada, con tres niveles: (1) solo drone (DJI Neo 2), (2) solo cámara (Insta360 X5), y (3) combinado (drone + cámara, homogeneizado en resolución y relación de aspecto según el protocolo del Capítulo 3, sección 3.6.3). Esta variable, evaluada sobre el caso de referencia, define el benchmark B4 y constituye la operacionalización experimental de H4.

<h3 id="cap4-4-3-4">4.3.4 Variables independientes secundarias</h3>

Preprocesamiento del dataset: presencia o ausencia del pipeline de ComfyUI, evaluada sobre el caso de referencia. Niveles: Dataset A (raw) vs. Dataset B (curado). Define el benchmark B2.

Densidad de muestreo (fps): la cadencia de extracción de fotogramas del video de captura se fija en un único valor constante para todos los benchmarks, definido a priori en base a la literatura consultada en el Capítulo 2 y al criterio de la investigadora, y se mantiene como variable controlada (sección 4.3.6). No se incluye una comparación experimental entre distintas densidades de muestreo, dado el tiempo y el costo computacional que implicaría ejecutar múltiples niveles sobre el hardware disponible (sección 4.4.1).

> **Nota metodológica:** los registros de procesamiento conservados (sección 4.9) documentan el resultado de la extracción de fotogramas —entre 302 y 1507 imágenes por dataset según el sitio y el dispositivo (detalle completo en la sección 4.7, Tabla 4.6)— pero no dejaron registrado explícitamente el parámetro de fps de extracción utilizado en cada corrida de `ns-process-data`/ffmpeg. *[Completar: valor de fps de extracción adoptado y su justificación, a confirmar por la investigadora contra la configuración original de cada corrida.]*

Herramienta de reconstrucción: el pipeline utiliza una única herramienta por función en todos los benchmarks —RealityCapture y COLMAP para SfM y Nerfstudio como framework unificado para NeRF y 3DGS—, seleccionada por su compatibilidad con el hardware disponible (sección 4.4.1). No se incluye una comparación experimental entre herramientas alternativas.

<h3 id="cap4-4-3-5">4.3.5 Variables dependientes (métricas de evaluación)</h3>

**PSNR (Peak Signal-to-Noise Ratio):** calidad visual de las vistas sintetizadas respecto a imágenes de referencia no utilizadas en el entrenamiento. Unidad: dB. A mayor valor, mejor calidad.

**SSIM (Structural Similarity Index Measure):** similitud estructural entre vistas sintetizadas y de referencia. Rango: 0–1. A mayor valor, mejor similitud perceptual.

**Fidelidad geométrica (análisis cualitativo):** comparación visual entre el modelo reconstruido y el edificio real, orientada a identificar qué zonas o elementos arquitectónicos fueron reproducidos con fidelidad y cuáles presentan pérdida de detalle, distorsión o ausencia de registro. No se expresa como valor numérico ni se compara contra mediciones dimensionales; se documenta de forma descriptiva, por caso de estudio y por técnica. Aplicable a las tres técnicas por igual.

**Tiempo de procesamiento:** duración total del pipeline de reconstrucción desde la ingesta del dataset hasta la obtención del modelo final. Unidad: minutos. Medido en el entorno de hardware definido en la sección 4.4.

**Peso del archivo de output:** tamaño del modelo final en su formato de distribución estándar. Unidad: MB. Formatos evaluados: .glTF (SfM), .SPLAT o .PLY exportado y comprimido con SuperSplat (3DGS), pesos del MLP exportados (NeRF).

**Tasa de fallos:** clasificada en fallo catastrófico, fallo parcial e inestabilidad de convergencia, conforme a la clasificación introducida en el Capítulo 2 (sección 2.6.3) y operacionalizada en el protocolo de registro de la sección 4.9. Esta métrica es central para la evaluación de H3 y H4.

**Cobertura reconstruida:** porcentaje de la superficie del edificio efectivamente representada en el modelo, sin huecos ni regiones vacías. Unidad: %. Métrica central para la evaluación de H4 (dataset multi-dispositivo).

**Checklist de compatibilidad web y reproducibilidad:** métrica cualitativa binaria (cumple / no cumple) por ítem, aplicada en el benchmark B5 para evaluar H5. Se detalla en la sección 4.5.

<h3 id="cap4-4-3-6">4.3.6 Variables controladas</h3>

Las siguientes variables se mantienen constantes dentro de cada benchmark para garantizar la comparabilidad de los resultados: dataset de entrada (mismo conjunto de imágenes del caso o casos de estudio correspondientes a cada benchmark, salvo en B4, donde la composición del dataset es la variable manipulada); densidad de muestreo (valor fijo definido a priori, sección 4.3.4); herramienta de reconstrucción (fija en todos los benchmarks: Nerfstudio para las tres técnicas, con COLMAP integrado para la etapa de SfM y SuperSplat para la edición y exportación de los modelos 3DGS; sección 4.4.3); condiciones de captura (protocolo definido en el Capítulo 3, secciones 3.6.1 a 3.6.3, aplicado de forma homogénea a los tres edificios); entorno de hardware (especificado en la sección 4.4); y parámetros de entrenamiento en los valores por defecto de cada herramienta, salvo indicación explícita.

<h2 id="cap4-4-4">4.4 Entorno de hardware y software</h2>

<h3 id="cap4-4-4-1">4.4.1 Hardware</h3>

El hardware disponible para esta investigación corresponde a una configuración de uso general (consumer-grade), sin acceso a infraestructura de cómputo de alta performance ni a GPU de nivel profesional. Esta condición es una limitación reconocida en el Capítulo 1 y es consistente con el objetivo de la tesis de evaluar las técnicas en condiciones de recursos limitados, representativas del contexto de equipos técnicos de gestión patrimonial en Argentina. La Tabla 4.2 detalla las especificaciones del equipo utilizado, tomadas de la caracterización de hardware presentada en el Capítulo 2 (Tabla 2.2).

| Componente | Especificación |
|---|---|
| Equipo | ASUS ROG Zephyrus G14 GA401IV |
| Sistema operativo | Microsoft Windows 11 Home, 64 bits |
| Procesador | AMD Ryzen 9 4900HS |
| Núcleos / hilos | 8 núcleos / 16 procesadores lógicos |
| Frecuencia reportada | 3,0 GHz |
| Memoria RAM | 16 GB DDR4 a 3200 MHz |
| GPU dedicada | NVIDIA GeForce RTX 2060 Max-Q (6 GB VRAM) |
| GPU integrada | AMD Radeon Graphics |
| Almacenamiento | SSD Intel NVMe de 1 TB (953,86 GB de capacidad efectiva) |
| Resolución de pantalla | 1920 × 1080 |

*Tabla 4.2 — Hardware utilizado en los experimentos.*

La GPU dedicada (NVIDIA GeForce RTX 2060 Max-Q, 6 GB de VRAM) constituye la principal restricción operativa del entorno: los entrenamientos de NeRF y 3DGS son sensibles a la memoria disponible, por lo que se anticipa que esta limitación incida en la tasa de fallos catastróficos —particularmente ante los casos de estudio de mayor complejidad geométrica (B3) o ante el dataset combinado del benchmark B4—. Esta consideración se retoma en las limitaciones del diseño experimental (sección 4.10).

El entrenamiento de los tres modelos (COLMAP/Nerfstudio para SfM, nerfacto para NeRF, splatfacto para 3DGS) se ejecuta íntegramente sobre este hardware local. Google Colab (sección 4.4.3) se utiliza exclusivamente en la etapa posterior de análisis y comparación de resultados, y no modifica el perfil de hardware ni las limitaciones de cómputo descriptas en esta sección.

<h3 id="cap4-4-4-2">4.4.2 Equipos de captura</h3>

El Capítulo 3 detalla el protocolo de captura completo; se resumen aquí las especificaciones técnicas relevantes para la interpretación de los resultados experimentales.

| Dispositivo | Especificaciones clave | Uso en el pipeline |
|---|---|---|
| DJI Neo 2 (drone) | Sensor CMOS de 1/2″, 12 MP (4000×3000 px); lente 16,5 mm equiv., f/2.2; FOV 119,8°; video 4K (3840×2160) hasta 60 fps; gimbal biaxial + RockSteady; GPS/Galileo/BeiDou; autonomía máxima ≈19 min (Cap. 2, Tabla 2.3). | Cobertura aérea en recorridos de bucle a distintas alturas (Cap. 3, sección 3.6.1). |
| Insta360 X5 (cámara) | Video 360° de hasta 8K; resolución efectiva media por dirección al distribuirse sobre toda la esfera; usada en modo gran angular (no panorámico) para esta investigación; formato de salida 16:9, 4K, 60 fps (Cap. 2, Tabla 2.4; Cap. 3, sección 3.6.3). | Registro complementario a nivel peatonal y de media altura, fachadas y entorno inmediato. |

*Tabla 4.3 — Equipos de captura utilizados en la generación de los datasets.*

<h3 id="cap4-4-4-3">4.4.3 Software y herramientas del pipeline</h3>

El pipeline utiliza una única herramienta por función para NeRF y 3DGS, mientras que para la etapa de SfM permite seleccionar el mejor resultado entre COLMAP (integrado en Nerfstudio) y RealityCapture, basándose en la mayor cantidad de imágenes coincidentes y poses de cámara registradas correctamente. Nerfstudio opera como framework unificado para las tres técnicas —integrando el resultado de SfM para los modelos nerfacto (NeRF) y splatfacto (3DGS)—, lo que garantiza la compatibilidad con el hardware disponible (sección 4.4.1).

| Función en el pipeline | Herramienta | Notas |
|---|---|---|
| SfM (estimación de poses y nube de puntos dispersa) | COLMAP (vía Nerfstudio) o RealityCapture | Se selecciona la herramienta que logre el mejor registro de cámaras para alimentar el flujo de Nerfstudio. |
| NeRF | Nerfstudio — modelo nerfacto | Entrenamiento y renderizado de vistas sintetizadas para el cálculo de PSNR/SSIM. |
| 3D Gaussian Splatting | Nerfstudio — modelo splatfacto | Entrenamiento del modelo de gaussianas a partir de la nube de puntos dispersa de COLMAP. |
| Edición y exportación de splats | SuperSplat | Limpieza, recorte de outliers y exportación de los modelos 3DGS a formatos de distribución (.ply / .splat / .ksplat). |
| Preprocesamiento de imágenes | ComfyUI | Pipeline de tres etapas definido en el Capítulo 3 (sección 3.7.2), sin cambios respecto al diseño original. |
| Análisis y comparación de resultados | Google Colab (notebooks en Python) | Procesamiento de los registros (logs) y métricas de los cinco benchmarks (PSNR, SSIM, tiempo, tasa de fallos, cobertura reconstruida, análisis cualitativo de fidelidad geométrica) y generación de tablas y gráficos comparativos. No se utiliza para el entrenamiento de los modelos (sección 4.4.1). |

*Tabla 4.4 — Herramientas del pipeline de reconstrucción, edición y análisis.*

> **Nota de consistencia (no presente en el original):** el toolchain de SfM permite tanto COLMAP como RealityCapture, seleccionando el de mejor registro, porque en la experimentación real ambas herramientas difirieron sustancialmente en su tasa de registro sobre el mismo dataset en más de un caso de estudio — evidencia presentada y discutida en el Capítulo 5 (sección 5.5).

<h2 id="cap4-4-5">4.5 Estructura de los benchmarks</h2>

Los experimentos se organizan en cinco benchmarks (B1–B5), diseñados de menor a mayor complejidad y articulados de forma que los resultados de los primeros informan el diseño de los siguientes. B2 es un experimento de control ejecutado sobre el caso de referencia (templete de Chacarita) que permite fijar el dataset para los experimentos centrales B1 y B4. B3 generaliza los resultados de B1 a los tres casos de estudio. B5 no genera nuevas reconstrucciones: valida los outputs ya producidos en B1 y B3. El toolchain (Nerfstudio, COLMAP, SuperSplat) y la densidad de muestreo son fijos en los cinco benchmarks (secciones 4.3.4 y 4.4.3).

**B2 — Benchmark de preprocesamiento ComfyUI**

**Hipótesis asociada:** H2.

**Objetivo:** cuantificar el impacto del pipeline de preprocesamiento ComfyUI en la calidad de la reconstrucción, comparando los modelos generados con el dataset raw (A) y el dataset curado (B) para las tres técnicas, sobre el caso de referencia.

**Variable independiente:** presencia o ausencia del preprocesamiento (Dataset A vs. Dataset B).

**Variables controladas:** caso de estudio (Chacarita), técnica (las tres: SfM, NeRF, 3DGS), herramienta (fija: Nerfstudio/COLMAP, sección 4.4.3), densidad de muestreo (valor fijo, sección 4.3.4).

**Métricas evaluadas:** PSNR, SSIM, evaluación cualitativa de artefactos visuales.

**Procedimiento:** para cada técnica, se ejecuta la reconstrucción con Dataset A y Dataset B por separado, manteniendo todos los demás parámetros constantes. Se comparan los resultados obtenidos.

> **Estado al cierre de este capítulo: benchmark no ejecutado.** El pipeline de preprocesamiento con ComfyUI (Capítulo 3, sección 3.7.2) está diseñado pero no se corrió sobre el caso de referencia al momento de redactar este capítulo — no existe un Dataset B curado independiente del Dataset A raw para ningún caso de estudio; los datasets efectivamente usados en B1, B3 y B4 (Tabla 4.6) corresponden todos a la extracción directa del video de captura, sin el pipeline de ComfyUI aplicado. En consecuencia, H2 permanece sin contrastar experimentalmente y se retoma como línea de trabajo pendiente en el Capítulo 5 (sección 5.6) y en las limitaciones de esta tesis (Capítulo 7).

**B1 — Benchmark de técnicas sobre el caso de referencia**

**Hipótesis asociada:** H1.

**Objetivo:** comparar el desempeño de las tres técnicas de reconstrucción 3D (SfM, NeRF, 3DGS) sobre el caso de referencia (Chacarita) en las mismas condiciones, evaluando fidelidad geométrica, calidad visual, eficiencia computacional, peso del archivo y potencial de integración BIM — es decir, para qué sirve mejor cada técnica y en qué es buena cada una, y no solo cuál es superior en términos absolutos.

**Variable independiente:** técnica de reconstrucción (SfM / NeRF / 3DGS).

**Variables controladas:** caso de estudio (Chacarita), dataset de entrada (Dataset B curado según B2), densidad de muestreo (valor fijo, sección 4.3.4), herramienta (fija: Nerfstudio/COLMAP; SuperSplat para la edición de splats en 3DGS), parámetros por defecto.

**Métricas evaluadas:** PSNR, SSIM, tiempo de procesamiento, peso del archivo de output (.glTF / .SPLAT / MLP), análisis cualitativo de fidelidad geométrica (zonas bien y mal reproducidas, por técnica), evaluación cualitativa de síntesis de vistas (NeRF) y de renderizado en tiempo real (3DGS).

**Procedimiento:** el dataset curado se procesa con cada una de las tres técnicas de forma independiente. Los modelos obtenidos se evalúan sobre el mismo conjunto de imágenes de test, se comparan visualmente con el edificio real y con material fotográfico de referencia —identificando para cada técnica las zonas bien reproducidas y las que presentan pérdida de detalle o inconsistencias—, y se evalúan cualitativamente según el criterio de uso de cada técnica (documentación con potencial de integración BIM para SfM, síntesis de vistas para NeRF, renderizado en tiempo real para 3DGS).

Este benchmark valida H1 en el caso de complejidad media, caracterizando el desempeño de cada técnica según su criterio de uso. Su generalización a los casos de complejidad baja y alta se aborda en el benchmark B3.

**Resultados:** ver Capítulo 5, sección 5.3.

**B3 — Benchmark de escalabilidad ante complejidad geométrica**

**Hipótesis asociada:** H3.

**Objetivo:** evaluar, a partir de los tres casos de estudio definidos en el Capítulo 3, qué técnica de reconstrucción es más compatible con cada nivel de complejidad arquitectónica, y si la divergencia de desempeño entre SfM, NeRF y 3DGS observada en el caso de referencia (B1) se mantiene, se atenúa o se amplifica al variar la complejidad geométrica y ornamental del objeto relevado.

**Variable independiente:** complejidad geométrica del caso de estudio (baja / media / alta), cruzada con la técnica de reconstrucción (SfM / NeRF / 3DGS).

**Variables controladas:** herramienta (fija: Nerfstudio/COLMAP; SuperSplat para la edición de splats en 3DGS), densidad de muestreo (valor fijo, sección 4.3.4), preprocesamiento (Dataset B curado según B2), protocolo de captura (Capítulo 3, secciones 3.6.1–3.6.3) aplicado de forma homogénea a los tres edificios.

**Métricas evaluadas:** PSNR, SSIM, tiempo de procesamiento, tasa de fallos (fallo catastrófico / fallo parcial / inestabilidad de convergencia), y análisis cualitativo de fidelidad geométrica (zonas bien y mal reproducidas, por caso de estudio y técnica).

**Procedimiento:** para cada uno de los tres casos de estudio, se procesa el dataset curado con cada una de las tres técnicas, utilizando la herramienta y la densidad de muestreo fijadas en la sección 4.3. Los resultados se organizan en una matriz de 3 técnicas × 3 casos de estudio (9 combinaciones), lo que permite tanto la comparación entre técnicas dentro de un mismo caso como la comparación de una misma técnica a través de los tres niveles de complejidad.

Este benchmark constituye, junto con B1, el aporte central de la investigación: sus resultados permiten validar o refutar H3 y responder si la elección de técnica óptima debería condicionarse al tipo de arquitectura a documentar, una pregunta con implicancias directas para la propuesta de pipeline definitivo que se desarrolla en el Capítulo 6.

**Resultados:** ver Capítulo 5, sección 5.4.

**B4 — Benchmark de dataset multi-dispositivo**

**Hipótesis asociada:** H4.

**Objetivo:** evaluar si un dataset combinado (DJI Neo 2 + Insta360 X5) mejora la cobertura de captura y mantiene la calidad de reconstrucción respecto a datasets de un único dispositivo, sobre el caso de referencia (Chacarita).

**Variable independiente:** composición del dataset (solo drone / solo cámara / combinado), sección 4.3.3.

**Variables controladas:** caso de estudio (Chacarita), técnica (se ejecuta como referencia sobre SfM, por ser la técnica más sensible a errores de alineación de poses entre dispositivos; sujeto a extensión a NeRF y 3DGS según disponibilidad de tiempo), preprocesamiento (Dataset B curado según B2), herramienta (fija: Nerfstudio/COLMAP), densidad de muestreo (valor fijo, sección 4.3.4).

**Métricas evaluadas:** PSNR, SSIM, cobertura reconstruida (%), evaluación cualitativa de discontinuidades de textura y exposición en las zonas de transición entre las imágenes de cada dispositivo, tasa de fallos.

**Procedimiento:** se arman tres datasets sobre el mismo edificio: uno compuesto únicamente por fotogramas del DJI Neo 2, otro únicamente por fotogramas de la Insta360 X5, y un tercero que combina ambas fuentes tras homogeneizar resolución y relación de aspecto (Capítulo 3, sección 3.6.3). Los tres datasets se procesan de forma independiente con la misma técnica y se comparan entre sí.

Este benchmark valida H4 y aporta evidencia práctica sobre una decisión operativa del protocolo de captura: si conviene combinar sistemáticamente ambos dispositivos para el archivo digital de patrimonio propuesto por esta tesis, o si el aporte de uno de ellos es marginal frente a los riesgos de discontinuidad que introduce la combinación.

**Resultados:** ver Capítulo 5, sección 5.5, que incluye además un hallazgo metodológico sobre la fiabilidad del registro SfM reportado automáticamente por las herramientas de conversión, relevante para el protocolo de registro de fallos de la sección 4.9.

**B5 — Validación de compatibilidad web y reproducibilidad del pipeline**

**Hipótesis asociada:** H5.

Este benchmark no compara niveles de una variable independiente cuantitativa: aplica un protocolo de validación de tipo checklist sobre los modelos ya generados en B1 y B3, por lo que no requiere nuevas corridas de reconstrucción.

**Objetivo:** verificar la compatibilidad de los formatos de output del pipeline con visores web de acceso abierto, y evaluar la reproducibilidad del pipeline completo a partir de la documentación generada.

**Procedimiento:** (a) se carga al menos un modelo de cada técnica —malla SfM en .glTF, modelo 3DGS exportado con SuperSplat en .SPLAT/.PLY, y la exportación correspondiente de NeRF— en visores web de acceso abierto (Potree, Sketchfab, Three.js, el visor web de SuperSplat), sin pasos de conversión manual adicionales a los ya contemplados en el pipeline; (b) se documenta el pipeline completo y se exportan los archivos de configuración de cada herramienta (workflow en JSON de ComfyUI, configuración de entrenamiento de Nerfstudio), verificando que esa documentación sea suficiente para repetir cada etapa sin pasos implícitos no registrados.

**Métricas / criterios evaluados:** checklist binario (cumple / no cumple) de carga en visor web por técnica; cantidad de pasos manuales adicionales requeridos, si los hubiera; completitud de la documentación y los archivos de configuración exportados por etapa del pipeline.

Este benchmark valida H5 y responde directamente al objetivo aplicado de la tesis: la viabilidad de un archivo digital de patrimonio argentino accesible en la web y reproducible a partir de su documentación, más allá de la validez experimental de las técnicas de reconstrucción evaluadas en B1–B4.

**Resultados:** ver Capítulo 5, sección 5.6. La carga efectiva en visor real —paso (a) del procedimiento— queda pendiente de ejecución.

<h2 id="cap4-4-6">4.6 Tabla resumen del diseño experimental</h2>

| Benchmark | Hip. | Variable independiente | Variable controlada | Métricas |
|---|---|---|---|---|
| B2 — Preproceso | H2 | Dataset A vs. B | Caso ref. (Chacarita). 3 técnicas. Herramienta y fps fijos | PSNR, SSIM, artefactos |
| B1 — Técnicas (caso ref.) | H1 | SfM / NeRF / 3DGS | Caso ref. Dataset B de B2. Herramienta fija (Nerfstudio/SuperSplat) | PSNR, SSIM, tiempo, peso, fidelidad geométrica (cualitativa) |
| B3 — Complejidad geométrica | H3 | Complejidad (baja/media/alta) × Técnica | 3 casos. Dataset de B2. Herramienta y fps fijos | PSNR, SSIM, tiempo, tasa de fallos, fidelidad geométrica (cualitativa) |
| B4 — Dataset multi-dispositivo | H4 | Composición: solo drone / solo cámara / combinado | Caso ref. Técnica SfM. Dataset B de B2 | PSNR, SSIM, cobertura reconstruida, tasa de fallos |
| B5 — Web y reproducibilidad | H5 | — (validación checklist, no comparativa) | Modelos ya generados en B1 y B3 | Checklist binario, bitácora de reproducibilidad |

*Tabla 4.5 — Resumen del diseño experimental: benchmarks, hipótesis, variables y métricas.*

<h2 id="cap4-4-7">4.7 Conjunto de imágenes de test y evaluación</h2>

Para garantizar que las métricas de calidad visual (PSNR, SSIM) se calculen sobre vistas genuinamente no vistas por los algoritmos durante el entrenamiento, se reserva un subconjunto de imágenes de cada caso de estudio como conjunto de test. Este conjunto se selecciona antes de cualquier experimento y se mantiene fuera de todos los pipelines de reconstrucción.

La proporción efectivamente aplicada es la que resulta del modo de partición por fracción de Nerfstudio (`eval_mode="fraction"`, `train_split_fraction=0.9`): el 90% de los fotogramas de cada dataset se utiliza como conjunto de entrenamiento y el 10% restante se reserva como conjunto de evaluación (eval/test) para el cálculo de PSNR y SSIM, seleccionado automáticamente a intervalos regulares sobre el orden de los fotogramas del dataset —lo que en la práctica aproxima la cobertura angular uniforme buscada, dado que el orden de los fotogramas sigue el recorrido de captura—. Este procedimiento es el que efectivamente se aplicó en los benchmarks ejecutados (B1, B3, B4); la proporción 80/20 con selección estratificada manual planteada originalmente para esta sección no llegó a implementarse como script separado y se reemplaza aquí por el mecanismo real, de partición fija y reproducible, provisto por la herramienta.

**Tabla 4.6 — Imágenes de entrenamiento y evaluación por dataset (split 90/10 de Nerfstudio).**

| Caso de estudio | Dispositivo | Dataset (uso) | Total imágenes | Entrenamiento (~90%) | Evaluación (~10%) |
|---|---|---|---|---|---|
| Los Paraguas | DJI Neo 2 | único (Nerfacto + Splatfacto) | 707 | 637 | 70 |
| Templete Central | DJI Neo 2 | subset (Nerfacto) | 308 | 278 | 30 |
| Templete Central | DJI Neo 2 | full ds8 (Splatfacto) | 1232 | 1109 | 123 |
| Templete Central | Insta360 X5 | único (Nerfacto + Splatfacto) | 306 | ≈276 | ≈30 |
| Panteón Asociación Española | DJI Neo 2 | subset (Nerfacto) | 302 | 272 | 30 |
| Panteón Asociación Española | DJI Neo 2 | full ds8 (Splatfacto) | 1506 | 1356 | 150 |
| Panteón Asociación Española | Insta360 X5 | único (Nerfacto + Splatfacto) | 311 | ≈280 | ≈31 |

*Fuente: campo `frames.total_in_json` de `analyze_camera_trajectories.py` (recuento del dataset) contrastado contra `total_paired_frames`/`gt_only_frames` de `analyze_render_benchmark.py` (recuento efectivo de imágenes de entrenamiento render­eadas vs. imágenes de evaluación no vistas por el modelo). Los subsets de Nerfacto (308/302 imágenes) responden a la limitación de memoria del `ParallelDataManager` descripta en el Capítulo 4 —sección 4.4.1— frente a los datasets completos usados sin problema por Splatfacto.*

<h2 id="cap4-4-8">4.8 Protocolo de evaluación cualitativa de fidelidad geométrica</h2>

La evaluación de fidelidad geométrica complementa las métricas de calidad de imagen (PSNR, SSIM) con un análisis cualitativo orientado a identificar en qué medida cada modelo reconstruido reproduce fielmente la geometría del edificio relevado, sin recurrir a mediciones dimensionales ni a comparaciones cuantitativas contra una nube de puntos de referencia.

El protocolo consiste en una inspección visual comparativa entre el modelo 3D obtenido y el edificio real —apoyada en fotografías de referencia y en el conocimiento directo del caso adquirido durante el relevamiento descrito en el Capítulo 3—, realizada de forma independiente para cada técnica y caso de estudio. Para cada modelo se documentan de forma descriptiva: (a) las zonas o elementos arquitectónicos reconstruidos con fidelidad, y (b) las zonas o elementos que presentan pérdida de detalle, distorsión, ausencia de registro o inconsistencias respecto al edificio real.

Este análisis no produce un valor numérico ni una clasificación fija por caso; su resultado es un registro cualitativo, por edificio y por técnica, de fortalezas y debilidades geométricas observadas, que se presenta y discute en el Capítulo 5.

En la práctica, el protocolo se instrumentó mediante dos artefactos generados automáticamente a partir de los datasets y resultados ya obtenidos: (a) grillas comparativas *Foto original | Nerfacto | Splatfacto* sobre 5 fotogramas equiespaciados del recorrido de captura, por sitio y por dispositivo (`build_fidelity_comparisons.py`, salida en `00-auditoria/fidelidad-geometrica/`); y (b) capturas de cobertura de la malla SfM tomadas directamente sobre el modelo texturizado en CloudCompare/RealityScan (no atadas a una pose de cámara puntual), disponibles para Los Paraguas y el Templete Central al cierre de este capítulo (Panteón Asociación Española pendiente de captura manual).

El análisis cualitativo completo resultante de este protocolo —caso por caso y técnica por técnica, con las imágenes comparativas correspondientes— se presenta y discute íntegramente en el Capítulo 5 (secciones 5.3 y 5.4).

<h2 id="cap4-4-9">4.9 Protocolo de registro de fallos</h2>

Con el fin de operacionalizar la métrica de tasa de fallos introducida en el Capítulo 2 (sección 2.6.3) y necesaria para evaluar H3 y H4, se define el siguiente protocolo de registro, aplicado a cada corrida de reconstrucción en los benchmarks B1 a B4 (B5 no genera nuevas corridas de reconstrucción, ya que reutiliza los modelos de B2 y B3):

**Fallo catastrófico:** el proceso de reconstrucción no llega a producir un output válido (por ejemplo, agotamiento de memoria de GPU, error de dependencias, o divergencia irrecuperable del optimizador). Se registra como fallo catastrófico y no se computan métricas de calidad para esa corrida.

**Fallo parcial:** el proceso produce un output, pero este presenta artefactos severos —huecos, floaters (elementos flotantes sin correspondencia geométrica real), regiones no reconstruidas— que lo vuelven inutilizable para los fines de documentación patrimonial, aun cuando las métricas de PSNR/SSIM puedan no reflejar completamente esta condición. Este juicio se realiza mediante inspección visual cualitativa siguiendo una rúbrica binaria (utilizable / no utilizable).

**Inestabilidad de convergencia:** el proceso completa la reconstrucción, pero requiere reinicios, ajuste manual de hiperparámetros o un número de iteraciones significativamente mayor al esperado para alcanzar un resultado estable. Se registra el número de reinicios y los ajustes realizados.

Cada corrida genera un registro (log) con: caso de estudio, técnica, herramienta, configuración de parámetros, resultado de la clasificación anterior y, si corresponde, las métricas de calidad obtenidas. Esta bitácora es la fuente de datos para el análisis de tasa de fallos en el Capítulo 5, particularmente relevante para contrastar los criterios de aceptación de H3 y H4.

<h2 id="cap4-4-10">4.10 Limitaciones del diseño experimental</h2>

**Hardware consumer-grade.** los tiempos de procesamiento reportados están condicionados por el hardware disponible (GPU RTX 2060 Max-Q, 6 GB de VRAM, sin acceso a nivel profesional) y no son directamente extrapolables a entornos de producción con hardware de mayor performance. Esta limitación es explicitada en el Capítulo 1 y los resultados de tiempo deben interpretarse como indicativos, no como valores absolutos; adicionalmente, se anticipa que la memoria de GPU disponible incida en la tasa de fallos catastróficos ante los casos de alta complejidad geométrica (B3) y ante el dataset combinado del benchmark B4. El uso de Google Colab se limita a la etapa de análisis de resultados (sección 4.4.3) y no atenúa esta limitación, dado que el entrenamiento de los modelos se ejecuta íntegramente en el hardware local.

**Toolchain fijo, sin comparación de herramientas.** el diseño experimental no genera evidencia propia sobre si Nerfstudio, COLMAP y SuperSplat son las opciones de mejor desempeño frente a alternativas como Meshroom, Instant-NGP o Postshot; la elección se basa en criterios de compatibilidad con el hardware disponible y de practicidad de un framework unificado para las tres técnicas, y no en una comparación empírica dentro de esta tesis.

**Densidad de muestreo fija, sin comparación experimental.** el valor de fps utilizado se fija a priori en base al criterio de la investigadora y a la literatura consultada en el Capítulo 2, sin una comparación empírica entre distintas densidades de muestreo dentro de esta tesis, dado el tiempo y el costo computacional que implicaría evaluar múltiples niveles en el hardware disponible. Esto introduce el riesgo de que un valor subóptimo afecte por igual a todos los datasets utilizados en B1–B4, sin que el diseño experimental pueda detectarlo.

**Benchmark de preprocesamiento (B2) no ejecutado.** al cierre de esta tesis, el pipeline de ComfyUI diseñado en el Capítulo 3 (sección 3.7.2) no se corrió sobre ningún caso de estudio, por lo que no existe un Dataset B curado independiente del Dataset A raw y H2 no pudo contrastarse experimentalmente (sección 4.5, B2). Los datasets efectivamente usados en B1, B3 y B4 corresponden a la extracción directa del video de captura, sin preprocesamiento adicional. Esto tiene una segunda implicancia metodológica: el diseño original preveía calibrar el dataset curado únicamente sobre el caso de complejidad media (Chacarita) y asumir esa calibración como transferible a los casos de complejidad baja y alta evaluados en B3 —una simplificación que ya no aplica, dado que B2 no se ejecutó sobre ningún caso—. La incidencia del preprocesamiento sobre la calidad de reconstrucción, y su posible interacción con la complejidad geométrica del objeto (una posibilidad coherente con la lógica de H3), queda como línea de trabajo futura (Capítulo 7).

**Acceso condicionado por el estado de conservación del Panteón de la Asociación Española.** el edificio se encuentra cerrado por orden judicial y en un estado de deterioro documentado (Capítulo 3), lo que restringe el registro a su exterior y puede introducir restricciones de proximidad o de ángulo de captura por razones de seguridad estructural, resultando en una cobertura de captura menos uniforme que en los otros dos casos y afectando la comparabilidad directa de los resultados de B3 entre edificios. *[Completar con el detalle de las zonas con acceso restringido, a confirmar durante el relevamiento de campo documentado en el Capítulo 3.]*

**Alcance acotado del benchmark de dataset multi-dispositivo.** por razones de tiempo, B4 se ejecuta sobre una sola técnica (SfM) y un solo caso de estudio (Chacarita); su extensión a NeRF, a 3DGS y a los otros dos casos queda sujeta a la disponibilidad de recursos, lo que limita la generalización de los resultados de H4.

**Parámetros por defecto.** los experimentos utilizan los parámetros por defecto de cada herramienta, salvo indicación explícita. Esta decisión garantiza reproducibilidad y comparabilidad, pero implica que los resultados podrían mejorar con configuraciones optimizadas para cada caso de estudio específico.

**Evaluación geométrica cualitativa, sin métrica cuantitativa.** la fidelidad geométrica de los modelos se evalúa mediante inspección visual comparativa contra el edificio real, sin mediciones dimensionales ni contraste contra una nube de puntos de referencia (TLS u otro relevamiento de control). Esta decisión evita la necesidad de equipamiento de relevamiento adicional no disponible para esta investigación, pero introduce un grado de subjetividad en la identificación de zonas bien o mal reproducidas, dado que el juicio es realizado por una única investigadora sin verificación cruzada por un segundo evaluador. Los resultados de este análisis deben interpretarse como una caracterización descriptiva y no como una medición objetiva de exactitud geométrica.

<h2 id="cap4-4-11">4.11 Síntesis del capítulo</h2>

El diseño experimental de esta tesis organiza los experimentos en cinco benchmarks. B2 mide el efecto del preprocesamiento de ComfyUI sobre el caso de referencia. B1 compara las tres técnicas de reconstrucción sobre ese mismo caso, caracterizando en qué es buena cada una según el criterio de uso (documentación con potencial de integración BIM, síntesis de vistas, renderizado en tiempo real). B3 generaliza esa comparación a los tres casos de estudio definidos en el Capítulo 3, evaluando qué técnica es más compatible con cada nivel de complejidad geométrica y ornamental. B4 valida si un dataset combinado de drone y cámara mejora la cobertura de captura sin degradar la calidad de reconstrucción. B5 valida, mediante un checklist cualitativo, la compatibilidad de los outputs con visores web y la reproducibilidad del pipeline completo a partir de su documentación. El toolchain de reconstrucción —Nerfstudio con COLMAP integrado para SfM y SuperSplat para la edición de splats de 3DGS— y la densidad de muestreo son fijos en los cinco benchmarks, sin comparación entre alternativas. Google Colab se incorpora como entorno de análisis y comparación de resultados, sin intervenir en el entrenamiento de los modelos. Las cinco hipótesis de trabajo (H1–H5) se operacionalizan con criterios de aceptación cuantitativos (H1–H4) o de checklist cualitativo (H5).

Las métricas de evaluación y criterios de análisis —PSNR, SSIM, tiempo de procesamiento, peso del archivo, tasa de fallos, cobertura reconstruida y el análisis cualitativo de fidelidad geométrica— cubren las dimensiones de calidad visual, fidelidad geométrica, eficiencia computacional, viabilidad de distribución en repositorios digitales patrimoniales, robustez ante la complejidad del objeto relevado y viabilidad práctica de un dataset multi-dispositivo.

Los resultados de los experimentos aquí diseñados se presentan y analizan en el Capítulo 5.

*— Continúa en Capítulo 5: Análisis de resultados —*
