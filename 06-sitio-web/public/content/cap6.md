Este capítulo tiene dos objetivos. El primero es documentar, a partir de lo que efectivamente funcionó a lo largo de los tres casos de estudio (Capítulo 5), **dos pipelines definitivos** que comparten el mismo tronco de captura y SfM pero divergen según el destino del resultado: uno orientado a la integración con flujos HBIM/Revit (fotogrametría más nube de puntos segmentada), y otro orientado a la publicación en el archivo digital web (Gaussian Splatting editado en SuperSplat). El segundo objetivo es proponer, a nivel conceptual, cómo el primero de esos pipelines podría integrarse con flujos de trabajo HBIM/Revit para la gestión patrimonial profesional. Ambos objetivos responden directamente a los objetivos específicos planteados en el Capítulo 1 (sección 1.3.2).

<h2 id="cap6-6-1">6.1 Criterios de selección de técnica según el objeto patrimonial</h2>

El hallazgo central del Capítulo 5 es que **no existe una técnica óptima en términos absolutos** (confirmando H1), pero tampoco una elección arbitraria: la evidencia recogida permite formular un criterio de selección claro, resumido en la Tabla 6.1. De las tres técnicas evaluadas, solo dos —SfM y Splatfacto— entran en los pipelines definitivos de este capítulo; Nerfacto queda explícitamente excluida, por las razones que la propia tabla documenta.

| Técnica | Rol en los pipelines definitivos | Evidencia (Capítulo 5) |
|---|---|---|
| **SfM** (RealityScan, malla texturizada + nube de puntos densa) | Tronco común de ambos pipelines: registro de cámaras y geometría de partida para Splatfacto, y output principal del Pipeline A — integración HBIM (sección 6.2.2) | Única técnica con geometría explícita, topología de malla y textura UV (sección 5.2.3) |
| **Splatfacto (3DGS)** | Output principal del Pipeline B — archivo digital web (sección 6.2.3) | Superó a Nerfacto en PSNR/SSIM en los tres casos de estudio (Tabla 5.7); mejor compatibilidad de publicación web entre las tres técnicas (sección 5.6); archivo liviano (Tabla 5.16) |
| **Nerfacto (NeRF)** | **Excluida de ambos pipelines definitivos** | No ofrece una ventaja decisiva en ningún criterio de uso evaluado en esta tesis: peor que Splatfacto en fidelidad de render en los tres casos (Tabla 5.7); sin ruta de publicación web estándar (sección 5.6); no produce geometría explícita utilizable para BIM (sección 6.3.1); y su output fue directamente inutilizable en el caso de mayor complejidad geométrica (fallo parcial, secciones 5.4.2 y 5.7) |

*Tabla 6.1 — Rol de cada técnica en los pipelines definitivos propuestos, y evidencia que respalda la exclusión de Nerfacto.*

Un matiz importante que la Tabla 6.1 no captura por sí sola, y que surge directamente de la sección 5.4.2: la fidelidad de Splatfacto en objetos de complejidad geométrica alta está **condicionada a un buen registro SfM previo**, no es una propiedad incondicional de la técnica. El tronco común de ambos pipelines (sección 6.2.1) incorpora esta condición como un paso explícito de verificación del registro SfM, no opcional.

<h2 id="cap6-6-2">6.2 Dos pipelines definitivos: HBIM y archivo digital web</h2>

Ambos pipelines comparten el mismo tronco —captura y SfM— y divergen recién después, según si el destino del resultado es la integración con flujos HBIM (Pipeline A, sección 6.2.2) o la publicación en el archivo digital web (Pipeline B, sección 6.2.3). A diferencia del diseño experimental del Capítulo 4 —que trata SfM, NeRF y 3DGS como alternativas comparadas entre sí—, aquí SfM y Splatfacto se tratan como **etapas complementarias de dos flujos con destinos distintos**, no como alternativas excluyentes entre sí; Nerfacto no participa de ninguno de los dos (Tabla 6.1).

<h3 id="cap6-6-2-1">6.2.1 Tronco común: captura y SfM</h3>

**Captura con un único dispositivo.** Esta no es una preferencia menor: es la lectura directa de H4, el hallazgo más contundente de esta tesis (Capítulo 5, secciones 5.5.2–5.5.6). Combinar DJI Neo 2 e Insta360 X5 en un mismo dataset no solo introdujo inestabilidad de registro SfM —dos corridas independientes del mismo dataset híbrido dieron 100% y 0,63% de registro—, sino que, incluso cuando el registro se logró, el resultado final de render fue peor que con cualquiera de los dos dispositivos por separado, en 3 de las 4 combinaciones técnica × caso evaluadas, sin excepción (secciones 5.5.5–5.5.6). Los pipelines definitivos de esta tesis, en consecuencia, **no combinan dispositivos de captura** dentro de un mismo dataset; DJI Neo 2 e Insta360 X5 son alternativas válidas usadas en solitario (Capítulo 3, secciones 3.6.1 y 3.6.3), no complementos entre sí.

**Sin preprocesamiento de imágenes.** El pipeline de limpieza con ComfyUI diseñado en el Capítulo 3 (sección 3.7.2) se evaluó experimentalmente en esta tesis (H2, sección 5.3) en sus dos variantes, y ambas empeoraron el resultado de reconstrucción respecto al dataset sin procesar: la eliminación de distractores no mejoró la fidelidad píxel a píxel de Nerfacto ni de Splatfacto (sección 5.3.4), y el enmascarado de fondo para aislar el edificio de su contexto dio resultados notablemente peores en ambas técnicas y en todas las métricas (sección 5.3.6) — el contexto de la escena ayuda a que el entrenamiento interprete correctamente los bordes del objeto, en vez de perjudicarlo. Los pipelines definitivos, en consecuencia, **no incluyen ningún paso de preprocesamiento de imágenes**: se entrena directamente sobre el dataset extraído de la captura, sin enmascarar ni limpiar distractores.

**SfM con verificación binaria.** Este es el paso que los pipelines definitivos agregan respecto al diseño experimental original, directamente motivado por el hallazgo de la sección 5.5.2: **la tasa de registro reportada por el wrapper de conversión (`ns-process-data` u otro) no debe aceptarse sin verificación.** Se recomienda, como paso estándar (no como excepción ante un resultado sospechoso):

1. Ejecutar SfM con ambas herramientas disponibles (COLMAP nativo de Nerfstudio y RealityCapture/RealityScan) y quedarse con el resultado de mejor registro, tal como se hizo en los tres casos de estudio (Capítulo 4, sección 4.4.3).
2. Si el registro reportado es bajo (por debajo de, por ejemplo, un 50%), verificar directamente los archivos binarios de COLMAP (`cameras.bin`/`images.bin`/`points3D.bin`) en busca de componentes de reconstrucción desconectados, en lugar de descartar el dataset como fallo catastrófico. Los scripts `parse_colmap_images_bin.py` y `colmap_component_to_nerfstudio.py` desarrollados para esta tesis (Capítulo 4, sección 4.9; Capítulo 5, sección 5.5.2) documentan un procedimiento reproducible para esta verificación y para exportar el componente correcto a formato Nerfstudio. Esta verificación sigue siendo una buena práctica general de control de calidad SfM, incluso con la recomendación de un único dispositivo: los datasets de un único dispositivo de esta tesis no mostraron este problema, pero el costo de verificar es bajo frente al riesgo de descartar un dataset válido.

<h3 id="cap6-6-2-2">6.2.2 Pipeline A — Integración HBIM</h3>

A partir del SfM del tronco común (sección 6.2.1), este pipeline se queda en la malla texturizada y la nube de puntos densa, no en un render:

1. **Segmentación geométrica automática** de la nube de puntos densa de SfM en las cuatro clases relevantes para BIM (cubierta, columna, baranda/pared no estructural, piso), con el clasificador desarrollado para esta tesis (`poc_segmentation_multi_site.py`, detallado en la sección 6.3).
2. **Control de calidad humano** sobre la clasificación automática, con el editor manual del visor web de esta tesis (sección 6.3.2).
3. **Exportación de la nube segmentada por clase** (.ply) — este es, junto con el .splat del Pipeline B, uno de los dos archivos que el archivo digital web ofrece para descarga (sección 6.4).
4. **Decimación y limpieza topológica de la malla SfM** (.obj) a un nivel manejable por un modelador BIM — propuesta conceptual, sin implementación en esta tesis (sección 6.3.4).
5. **Importación a un entorno de modelado** (por ejemplo, Recap Photo / Revit) de la nube segmentada y la malla decimada como referencia *scan-to-BIM*, no como modelo final — propuesta conceptual (sección 6.3.4).
6. **Modelado paramétrico manual o semiautomático** sobre esa referencia, siguiendo el estándar de niveles de detalle (LOD) propio de HBIM para patrimonio histórico — fuera del alcance técnico de esta tesis (sección 6.3.4).
7. **Vínculo documental bidireccional**: conservar el output original de SfM como evidencia fotográfica/geométrica de respaldo del modelo HBIM final, replicando el criterio de trazabilidad que esta tesis aplicó internamente a nivel de logs y datasets (Capítulo 4, sección 4.9).

Los pasos 1 y 2 son la única parte de este pipeline que se implementó y validó sobre los tres casos de estudio; los pasos 4 a 7 son una propuesta conceptual (sección 6.3.4 desarrolla el detalle y las limitaciones de cada tramo).

<h3 id="cap6-6-2-3">6.2.3 Pipeline B — Archivo digital web</h3>

A partir del SfM del tronco común (sección 6.2.1) —nube de puntos dispersa y poses de cámara—, este pipeline entrena y publica un modelo de Gaussian Splatting:

1. **Entrenamiento de Splatfacto** sobre la nube dispersa y las poses de SfM (Nerfstudio, Capítulo 4, sección 4.4.3).
2. **Edición en SuperSplat**: recorte de outliers y del halo de gaussianas de baja opacidad identificado en el Capítulo 5 (sección 5.2.1, Gráficos 5.1–5.2).
3. **Exportación** en formato .splat/.ply.
4. **Publicación web**, junto con la nube de puntos segmentada del Pipeline A (sección 6.2.2, paso 3) como descarga complementaria: el archivo digital de esta tesis ofrece las dos cosas, el .splat limpio de 3DGS y el .ply segmentado por clase (sección 6.4) — ya implementado en el visor de esta tesis (`06-sitio-web`, ruta `/segmentador`).

<h2 id="cap6-6-3">6.3 Detalle de implementación: segmentación semántica de la nube de puntos</h2>

Esta sección desarrolla el detalle técnico del paso 1 del Pipeline A (sección 6.2.2) y responde al objetivo específico de la tesis de "diseñar una propuesta de integración del pipeline con flujos de trabajo de modelado HBIM/Revit como línea de continuación para la gestión patrimonial profesional" (Capítulo 1, sección 1.3.2). A diferencia del resto del Pipeline A (pasos 4 a 7, conceptuales), la segmentación semántica de la nube de puntos —y su control de calidad manual— sí se implementó y validó sobre los tres casos de estudio.

<h3 id="cap6-6-3-1">6.3.1 Punto de entrada: la malla SfM</h3>

De las tres técnicas evaluadas, únicamente el output de SfM —malla poligonal con textura UV, más la nube de puntos densa de la que parte— tiene una ruta de integración directa con software BIM. Nerfacto y Splatfacto, por su naturaleza (campo neuronal implícito y nube de primitivas gaussianas respectivamente), no producen una malla poligonal navegable por un modelador BIM sin un paso adicional de conversión (extracción de superficie desde un campo de densidad, o meshing sobre las gaussianas), que ninguna herramienta del pipeline actual (Nerfstudio, SuperSplat) resuelve de forma nativa — otra razón, junto con las de la Tabla 6.1, por la que ninguna de las dos participa del Pipeline A.

<h3 id="cap6-6-3-2">6.3.2 Implementación: segmentación semántica de la nube de puntos</h3>

El paso 1 del Pipeline A (sección 6.2.2) requiere que la nube de puntos densa de SfM se organice, antes de servir como referencia *scan-to-BIM*, en un trabajo de limpieza y clasificación que hoy recae por completo en el modelador BIM: recorrer la nube o la malla completa e identificar a mano qué región corresponde a cada elemento constructivo (cubierta, columna, muro, piso) antes de empezar a levantar geometría paramétrica encima. Este cuello de botella está documentado en la literatura de *scan-to-BIM* para patrimonio —Romero-Jarén y Arranz (2021) lo describen como el paso "muy costoso en tiempo y enteramente delegado al trabajo manual de expertos, lejos de estar automatizado"— y motivó una prueba de concepto adicional dentro de esta tesis: un clasificador geométrico que segmenta automáticamente la nube densa de SfM en las cuatro clases relevantes para BIM antes de exportarla como referencia.

El script `poc_segmentation_multi_site.py` (Capítulo 4, sección 4.9) implementa esta clasificación sin redes neuronales ni datos de entrenamiento, apoyándose únicamente en propiedades geométricas locales de la nube:

1. **Nivelado**: ajuste del plano de piso por RANSAC y rotación de la nube para que quede horizontal, necesario porque ni RealityScan ni COLMAP nativo garantizan que el eje vertical del archivo crudo sea el "arriba" real de la obra (sección 5.4.3 documenta un caso concreto de este problema en Los Paraguas).
2. **Verticalidad**: estimación de normales locales (PCA sobre vecinos cercanos, o normales precalculadas cuando el archivo las trae) para distinguir superficies horizontales (techo/piso) de superficies verticales (muro/columna).
3. **Bandas de altura**: detección de picos de densidad en el histograma de alturas para ubicar la banda de techo y la banda de piso de cada caso, sin asumir una altura fija.
4. **Columna vs. elemento no estructural**: agrupamiento de los puntos verticales en celdas de planta; una celda se clasifica como columna estructural si alcanza una fracción alta de la altura total techo-piso, y como baranda/pared no estructural si se corta antes.

La Tabla 6.2 resume el resultado sobre los tres casos de estudio, y las Figuras 6.2 a 6.4 muestran la clasificación resultante en el visor web desarrollado para esta tesis (`06-sitio-web`, ruta `/segmentador`).

| Caso de estudio | Puntos totales | Cubierta | Columna | Baranda/pared no estructural | Piso/base |
|---|---|---|---|---|---|
| Templete Central | 589.605 | 150.000 | 19.094 | 33.651 | 386.860 |
| Los Paraguas | 502.817 | 196.453 | 127.293 | 6.044 | 173.027 |
| Panteón Asociación Española (post-filtro de vegetación) | 356.234 | 39.346 | 48.555 | 96.249 | 172.084 |

*Tabla 6.2 — Conteo de puntos por clase resultante de la segmentación automática, tres casos de estudio.*

![Templete Central segmentado en el visor web: techo (rojo), columnas (verde), baranda no estructural (amarillo) y piso (azul)](/content/assets/cap6-segmentacion-templete.png)

*Figura 6.2 — Templete Central: las cuatro clases mapean directamente a categorías de Revit (Roofs, Structural Columns, Railings, Floors).*

![Los Paraguas segmentado: ambas cubiertas tipo hongo, vástago central y piso correctamente diferenciados](/content/assets/cap6-segmentacion-paraguas.png)

*Figura 6.3 — Los Paraguas: la doble curvatura de las cubiertas se resuelve correctamente pese a no ser una geometría plana.*

![Panteón Asociación Española segmentado, con la arboleda circundante excluida de la clasificación](/content/assets/cap6-segmentacion-panteon.png)

*Figura 6.4 — Panteón Asociación Española: el filtrado por color (índice ExG) excluye la vegetación circundante antes de clasificar, evitando que contamine las clases estructurales.*

**Control de calidad humano.** La clasificación puramente geométrica no es perfecta —el caso del Panteón, con arboledas cercanas que en algunos tramos comparten color con la pátina de la cúpula, y el caso de Los Paraguas, donde el borde curvo de la cubierta requirió un ajuste específico para no confundirse con piso, son evidencia directa de esto dentro de esta misma tesis—. Por esa razón se extendió el visor con una herramienta de edición manual: selección de puntos por rectángulo, eliminación, deshacer y guardado directo sobre el archivo segmentado (Figura 6.5). Esto no es un detalle secundario del visor sino la respuesta concreta a una limitación reconocida en la literatura: Croce et al. (2023) y Pan et al. (2024) framean sus propuestas como *"semi-automáticas"* precisamente porque ningún clasificador —ni el geométrico simple de esta tesis, ni los basados en aprendizaje profundo de la literatura relevada— elimina la necesidad de una revisión humana antes de que el resultado se use como base de un modelo BIM.

![Modo de selección manual activo sobre Templete Central, con un rectángulo de selección arrastrado sobre parte de la cubierta](/content/assets/cap6-segmentacion-edicion-manual.png)

*Figura 6.5 — Editor manual del visor: control de calidad humano sobre la clasificación automática antes de exportar por clase.*

**Respaldo en la literatura y posicionamiento de este aporte.** La automatización de este paso —comúnmente llamada segmentación semántica de nubes de puntos para *scan-to-BIM*— es un área activa de investigación. Romero-Jarén y Arranz (2021) proponen un método de segmentación y clasificación automática de elementos BIM (pisos, techos, muros, columnas) a partir de nubes de puntos de interiores; Buldo et al. (2023) documentan un flujo *scan-to-BIM* específico para patrimonio cultural con segmentación automática y modelado paramétrico-adaptativo de sistemas abovedados; Croce et al. (2023) combinan clasificación por Random Forest con reconstrucción H-BIM semi-automática sobre claustros medievales; y Pan et al. (2024) usan una red neuronal profunda (KP-SG) para llevar nubes de puntos semánticas a modelos BIM semánticos en el contexto de un gemelo digital patrimonial. Frente a ese estado del arte, el aporte de esta tesis es modesto pero honesto: una clasificación geométrica simple —sin entrenamiento, sin dataset anotado, ejecutable con los mismos recursos consumer-grade del resto del pipeline (Capítulo 4, Tabla 4.2)— que demuestra, sobre los tres casos de estudio reales de esta investigación, que incluso ese enfoque liviano produce clases usables como punto de partida para el Pipeline A (sección 6.2.2). La adopción de un clasificador basado en aprendizaje profundo (siguiendo, por ejemplo, el enfoque de Pan et al., 2024) queda documentada como línea de trabajo futura (Capítulo 7), no como parte de esta implementación.

<h3 id="cap6-6-3-3">6.3.3 Exploración: segmentación asistida por un modelo de visión (VLM)</h3>

El "control de calidad humano" descrito en la sección 6.3.2 —revisar y corregir a mano los errores del clasificador geométrico— es exactamente el cuello de botella que la literatura de *scan-to-BIM* señala como no resuelto (Romero-Jarén y Arranz, 2021). Como exploración adicional, no contemplada en el diseño original de esta tesis, se probó si un modelo de visión liviano (VLM, *vision-language model*) podía reducir ese trabajo manual: en lugar de reemplazar el clasificador geométrico, se lo usó para **revisar** su decisión más frágil —columna estructural vs. baranda/pared no estructural, hoy resuelta con un umbral fijo de altura (sección 6.3.2, paso 4)— mostrándole a un modelo una imagen de cada fragmento y preguntándole cuál de las dos clases le corresponde.

El pipeline construido para esta prueba: los puntos ya clasificados como columna o baranda por el método geométrico se agrupan por separado (dentro de cada clase) en fragmentos conectados espacialmente, cada fragmento se renderiza en dos paneles —aislado, con sus proporciones reales de alto y ancho, y en contexto dentro del edificio completo—, y la imagen se envía a un modelo de lenguaje-visión corriendo localmente a través de un nodo propio expuesto por la API de ComfyUI, con la pregunta de si el fragmento se parece más a una columna (alto y angosto) o a una baranda (bajo y horizontal). Se probaron dos modelos livianos, elegidos por poder correr en el mismo hardware consumer-grade del resto del pipeline (Capítulo 4, Tabla 4.2): Moondream2 (1.6B parámetros), corrido sobre los tres casos de estudio, y Qwen2-VL-2B-Instruct (2B), corrido sobre el caso de referencia como segundo punto de comparación.

| Modelo | Caso de estudio | Fragmentos evaluados | Acierto | Sesgo observado |
|---|---|---|---|---|
| Moondream2 | Templete Central | 15 (8 columna, 7 baranda) | 7/15 (47%) | 100% "baranda" |
| Moondream2 | Panteón Asociación Española | 19 (9 columna, 10 baranda) | 10/19 (53%) | 100% "baranda" |
| Moondream2 | Los Paraguas | 7 (2 columna, 5 baranda) | 5/7 (71%) | 100% "baranda" |
| Moondream2 | **Total, tres sitios** | **41 (19 columna, 22 baranda)** | **22/41 (54%)** | **100% "baranda"** |
| Qwen2-VL-2B-Instruct | Templete Central | 15 (8 columna, 7 baranda) | 8/15 (53%) | 100% "columna" |

*Tabla 6.3 — Acierto de dos modelos de visión livianos frente a la etiqueta del clasificador geométrico, sobre los fragmentos de columna/baranda de los tres casos de estudio (Moondream2) y del caso de referencia (Qwen2-VL-2B-Instruct). Fuente: `poc_segmentation_vlm.py`, `qwen_batch_test.py`.*

La Tabla 6.3 muestra un patrón más revelador que el porcentaje de acierto en sí: en los cuatro sitios/modelos evaluados, cada corrida respondió lo mismo para absolutamente todos sus fragmentos, sin una sola excepción, con un sesgo opuesto entre los dos modelos (Moondream2 siempre "baranda", Qwen2-VL siempre "columna"). El 54% de acierto total de Moondream2 no refleja que el modelo esté evaluando la forma del fragmento caso por caso —es, esencialmente, el resultado de responder siempre lo mismo sobre un conjunto con una proporción de clases relativamente pareja (19 columna contra 22 baranda)—, y el hecho de que ese mismo sesgo se sostenga sin variación en tres edificios de geometría, altura y complejidad ornamental completamente distintas (Capítulo 3) descarta que sea una particularidad de un solo caso de estudio: es una propiedad del modelo frente a este tipo de imagen, no del dataset. Un chequeo adicional con figuras geométricas sintéticas (un rectángulo negro simple, sin nube de puntos de por medio) confirmó además que el sesgo no es específico del render de nube de puntos: los dos modelos repitieron la misma respuesta única incluso ante una forma trivial e inequívoca.

![Fragmento de columna real (izquierda, proporciones reales) y en contexto dentro del Templete Central (derecha, en rojo), que Moondream2 clasificó incorrectamente como baranda](/content/assets/cap6-poc-vlm-frag-columna.png)

*Figura 6.6 — Ejemplo de clasificación fallida: fragmento de 2,23 m de altura, geométricamente una columna, visualmente inequívoco en el panel izquierdo — el modelo respondió "baranda" de todas formas. Fuente: `poc_segmentation_vlm.py`.*

**Lectura del resultado.** La infraestructura construida para esta prueba funciona de punta a punta —nodo de ComfyUI expuesto por API, entorno aislado para correr un modelo con dependencias incompatibles con las del resto del pipeline sin afectarlo, agrupamiento de fragmentos, render y reclasificación— y queda disponible como herramienta reusable. El resultado de clasificación en sí, sin embargo, es negativo: ni Moondream2 ni Qwen2-VL-2B-Instruct superaron al umbral geométrico simple en esta tarea puntual, con esta forma de preguntarles. La explicación más probable no es que la idea sea inviable, sino que estos dos modelos —livianos y entrenados mayormente sobre fotografías naturales— no generalizan bien a un tipo de imagen (una nube de puntos dispersa, renderizada de forma abstracta) que probablemente no vieron durante su entrenamiento, y que forzar una respuesta entre solo dos opciones, sin darle al modelo la posibilidad de contestar "no estoy seguro", probablemente amplifica ese problema en vez de dejarlo en evidencia. Queda como línea de trabajo futura (Capítulo 7) probar esta misma idea con un modelo de mayor tamaño, con *fine-tuning* sobre ejemplos de nubes de puntos arquitectónicas, o con un render más realista (por ejemplo, una malla sombreada en vez de puntos dispersos) antes de descartar el enfoque.

Sobre esta última hipótesis, un chequeo acotado descartó al menos su componente más económico de probar. La nube de puntos de origen (`nube-densa.xyz`) ya trae color real por punto, no solo geometría, pero el render usado en la prueba lo ignoraba en favor de un color plano uniforme. Repitiendo la clasificación sobre cinco fragmentos de Templete Central (tres columnas reales, mal clasificadas en la corrida original, y dos barandas, bien clasificadas) pero coloreando cada punto con su color real en vez de plano, Moondream2 volvió a responder "RAILING" en el 100% de los casos —sin ningún cambio respecto a la corrida original (`poc_vlm_color_render_test.py`)—. El color fotográfico por sí solo no alcanza para revertir el sesgo. Lo que queda sin probar, entonces, es específicamente la continuidad de la superficie: una malla sombreada (la textura de RealityScan generada para los tres sitios, entre 800 MB y 4 GB por archivo según el caso) es una superficie sólida y continua, muy distinta de un scatter de puntos dispersos aunque ambos tengan el mismo color. No se llegó a evaluar esa variante por el costo de cargar y renderizar mallas de ese tamaño con el hardware disponible (Capítulo 4).

<h3 id="cap6-6-3-4">6.3.4 Limitación reconocida</h3>

La propuesta de integración con Revit/BIM propiamente dicha —los pasos 4 a 7 del Pipeline A (sección 6.2.2)— no fue validada con un modelador BIM real ni con un caso de uso profesional dentro de esta tesis; su valor es orientar la siguiente etapa de trabajo (Capítulo 7), no cerrar la pregunta de integración HBIM. La segmentación semántica de la sección 6.3.2 sí es una implementación funcional y validada sobre los tres casos de estudio —a diferencia del resto de la propuesta HBIM, que permanece conceptual—, pero se detiene en la nube de puntos clasificada: no genera geometría paramétrica, no exporta a un formato nativo de Revit (.rvt) ni a un formato de intercambio BIM estándar (IFC), y no fue puesta a prueba por un profesional de modelado BIM. Es, en los términos de la literatura citada, un paso semi-automático de preparación de datos, no un pipeline scan-to-BIM completo.

<h2 id="cap6-6-4">6.4 Lineamientos para el archivo digital de patrimonio arquitectónico web</h2>

A partir de la evidencia de la sección 5.6 (H5), se proponen los siguientes lineamientos para el repositorio/plataforma web mencionado como parte del alcance de esta tesis (Capítulo 1, sección 1.6.1):

- **3DGS (Splatfacto) como formato principal de exploración interactiva**, por su combinación de peso liviano (Tabla 5.16), buen desempeño de calidad visual (Tabla 5.7) y compatibilidad directa con visores web (sección 5.6).
- **La malla SfM (.glTF) como capa de referencia geométrica y documental**, útil para mediciones aproximadas y para usuarios que requieran un modelo poligonal (por ejemplo, integración con visores BIM ligeros), pese a su mayor peso — se recomienda ofrecer una versión decimada específicamente para web, distinta de la usada como insumo para la integración HBIM (sección 6.3).
- **Descarga dual: el .splat limpio de 3DGS y el .ply segmentado por clase**, uno por cada pipeline definitivo (secciones 6.2.2 y 6.2.3) — el usuario del archivo digital puede llevarse tanto el modelo interactivo completo (Pipeline B) como la nube de puntos ya clasificada por elemento constructivo (Pipeline A), ya implementado en el visor de esta tesis (`06-sitio-web`, ruta `/segmentador`).
- **Metadatos de trazabilidad por modelo**: sitio, técnica, dispositivo(s) de captura, fecha de relevamiento y estado de conservación documentado, siguiendo el mismo criterio de trazabilidad que esta tesis aplicó internamente a nivel de logs (Capítulo 4, sección 4.9) — relevante en particular para casos como el Panteón Asociación Española, cuyo estado de conservación condiciona la interpretación de cualquier resultado (Capítulo 4, sección 4.10).

<h2 id="cap6-6-5">6.5 Recomendaciones de infraestructura</h2>

El hardware consumer-grade utilizado en esta tesis (Capítulo 4, Tabla 4.2) resultó suficiente para completar los tres casos de estudio, pero con un costo de tiempo no despreciable —hasta 1 h 38 min de entrenamiento por modelo (Tabla 5.17)— y una incidencia directa en la tasa de fallos catastróficos (Capítulo 5, sección 5.7), concentrada en las etapas de mayor demanda de memoria (fusión densa de COLMAP, `ParallelDataManager` de Nerfacto sobre datasets grandes). Para un equipo de gestión patrimonial que busque adoptar este pipeline de forma sostenida, se recomienda:

- Priorizar una GPU con mayor VRAM disponible (8–12 GB o más) sobre un aumento de velocidad de cómputo puro, dado que las fallas observadas fueron predominantemente de memoria, no de tiempo.
- Splatfacto toleró el dataset completo de los tres casos de estudio sin necesidad de submuestreo, incluso en el sitio de mayor volumen de imágenes — a diferencia de Nerfacto (excluida del pipeline definitivo, Tabla 6.1), que sí requería reducir el dataset por las mismas limitaciones de memoria.
- Incorporar la verificación binaria de registro SfM (sección 6.2.1) como paso estándar de control de calidad, dado su bajo costo de cómputo relativo frente al riesgo de descartar datasets válidos.

<h2 id="cap6-6-6">6.6 Síntesis del capítulo</h2>

Este capítulo tradujo los resultados del Capítulo 5 en cuatro productos aplicados: (a) un criterio de selección de técnica según el tipo de objeto patrimonial y el uso previsto (Tabla 6.1), directamente respaldado por la evidencia cuantitativa y cualitativa recogida, que deja fuera de los pipelines definitivos a Nerfacto —no aporta una ventaja decisiva en ningún criterio de uso evaluado— y descarta combinar dispositivos de captura o preprocesar las imágenes, ambas prácticas invalidadas por la evidencia de H4 y H2 respectivamente; (b) **dos pipelines definitivos documentados** (sección 6.2) que comparten el mismo tronco de captura con un único dispositivo y SfM con verificación binaria, y divergen en un Pipeline A hacia integración HBIM (fotogrametría más nube de puntos segmentada) y un Pipeline B hacia el archivo digital web (Splatfacto editado en SuperSplat); (c) una prueba de concepto de segmentación semántica de la nube de puntos con control de calidad manual (sección 6.3.2), la única pieza del Pipeline A que se implementó y validó sobre los tres casos de estudio, no solo se propuso conceptualmente; y (d) una propuesta conceptual de integración con flujos HBIM/Revit —los pasos 4 a 7 del Pipeline A, construidos sobre esa segmentación como punto de partida— y lineamientos para el archivo digital web, que ya ofrece para descarga tanto el .splat del Pipeline B como el .ply segmentado del Pipeline A. El Capítulo 7 retoma estos cuatro productos para las conclusiones generales y las líneas de investigación futura.

*— Continúa en Capítulo 7: Conclusiones —*
