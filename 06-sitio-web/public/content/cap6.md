Este capítulo tiene dos objetivos. El primero es documentar, a partir de lo que efectivamente funcionó a lo largo de los tres casos de estudio (Capítulo 5), un pipeline definitivo reproducible desde la captura de imágenes hasta la obtención de un archivo digital publicable en la web. El segundo es proponer, a nivel conceptual, cómo ese pipeline podría integrarse con flujos de trabajo HBIM/Revit para la gestión patrimonial profesional. Ambos objetivos responden directamente a los objetivos específicos planteados en el Capítulo 1 (sección 1.3.2).

<h2 id="cap6-6-1">6.1 Criterios de selección de técnica según el objeto patrimonial</h2>

El hallazgo central del Capítulo 5 es que **no existe una técnica óptima en términos absolutos** (confirmando H1), pero tampoco una elección arbitraria: la evidencia recogida permite formular criterios prácticos de selección, resumidos en la Tabla 6.1.

| Criterio de uso | Técnica recomendada | Evidencia (Capítulo 5) |
|---|---|---|
| Documentación con potencial de integración BIM/HBIM | **SfM** (malla texturizada) | Única técnica con geometría explícita, topología de malla y textura UV (sección 5.2.3) |
| Síntesis de vistas fotorrealista / producción audiovisual | **Splatfacto (3DGS)**, no Nerfacto | Splatfacto superó a Nerfacto en PSNR/SSIM en los tres casos (Tabla 5.2); Nerfacto falló parcialmente en el caso de mayor complejidad (sección 5.4.2) |
| Renderizado interactivo en tiempo real / entornos web | **Splatfacto (3DGS)** | Mejor compatibilidad de publicación web entre las tres técnicas (sección 5.6); archivo liviano (sección 5.8) |
| Objetos de complejidad geométrica y ornamental alta | **Splatfacto (3DGS)**, condicionado a buen registro SfM | Único método que mantuvo calidad aceptable en el caso de complejidad alta (Tabla 5.2, Figura 5.18) |
| Objetos de geometría simple y regular | Las tres técnicas ofrecen resultados utilizables | Diferencias de PSNR entre técnicas más acotadas en el caso de complejidad baja (Tabla 5.2) |

*Tabla 6.1 — Criterios de selección de técnica de reconstrucción 3D según el objeto patrimonial y el uso previsto.*

Un matiz importante que la Tabla 6.1 no captura por sí sola, y que surge directamente de la sección 5.4.2: la recomendación de Splatfacto para objetos de complejidad alta está **condicionada a un buen registro SfM previo**, no es una propiedad incondicional de la técnica. El pipeline definitivo (sección 6.2) incorpora esta condición como un paso explícito de verificación, no opcional.

<h2 id="cap6-6-2">6.2 Pipeline definitivo documentado</h2>

La Figura 6.1 documenta el pipeline definitivo propuesto, de la captura a la publicación. A diferencia del diseño experimental del Capítulo 4 —que trata SfM, NeRF y 3DGS como alternativas comparadas entre sí—, este pipeline las trata como **outputs complementarios de un mismo flujo**, generados a partir de una única etapa de captura y de SfM, tal como efectivamente se ejecutó en los tres casos de estudio (Nerfstudio como framework unificado, Capítulo 4, sección 4.4.3).

![Pipeline definitivo propuesto](/content/assets/cap6-pipeline-definitivo.png)

*Figura 6.1 — Pipeline definitivo propuesto: de la captura al archivo digital web / integración BIM.*

<h3 id="cap6-6-2-1">6.2.1 Captura</h3>

Registro con DJI Neo 2 (cobertura aérea, recorridos de bucle a distintas alturas) e, idealmente, Insta360 X5 como complemento a nivel peatonal (Capítulo 3, secciones 3.6.1 y 3.6.3). La recomendación operativa que surge de la sección 5.5.2 es **no descartar un dataset combinado por un reporte de bajo registro sin verificarlo primero** (sección 6.2.3).

<h3 id="cap6-6-2-2">6.2.2 Preprocesamiento</h3>

El pipeline de ComfyUI (Capítulo 3, sección 3.7.2) está diseñado pero no fue validado experimentalmente en esta tesis (H2, sección 5.3). Se incluye en el pipeline definitivo como paso recomendado por diseño —limpieza de fondos irrelevantes, corrección de exposición, filtrado de fotogramas de baja calidad—, pero su inclusión aquí es una recomendación teórica pendiente de validación empírica, no una conclusión respaldada por los benchmarks de esta tesis.

<h3 id="cap6-6-2-3">6.2.3 SfM con verificación binaria</h3>

Este es el paso que el pipeline definitivo agrega respecto al diseño experimental original, directamente motivado por el hallazgo de la sección 5.5.2: **la tasa de registro reportada por el wrapper de conversión (`ns-process-data` u otro) no debe aceptarse sin verificación cuando el dataset es heterogéneo.** Se recomienda, como paso estándar del pipeline (no como excepción ante un resultado sospechoso):

1. Ejecutar SfM con ambas herramientas disponibles (COLMAP nativo de Nerfstudio y RealityCapture/RealityScan) y quedarse con el resultado de mejor registro, tal como se hizo en los tres casos de estudio (Capítulo 4, sección 4.4.3).
2. Si el registro reportado es bajo (por debajo de, por ejemplo, un 50%) **y** el dataset combina más de un dispositivo o estrategia de captura, verificar directamente los archivos binarios de COLMAP (`cameras.bin`/`images.bin`/`points3D.bin`) en busca de componentes de reconstrucción desconectados, en lugar de descartar el dataset como fallo catastrófico. Los scripts `parse_colmap_images_bin.py` y `colmap_component_to_nerfstudio.py` desarrollados para esta tesis (Capítulo 4, sección 4.9; Capítulo 5, sección 5.5.2) documentan un procedimiento reproducible para esta verificación y para exportar el componente correcto a formato Nerfstudio.

<h3 id="cap6-6-2-4">6.2.4 Reconstrucción: NeRF y 3DGS</h3>

A partir de la misma nube de puntos dispersa y poses de cámara de SfM, se entrenan Nerfacto y Splatfacto en paralelo (no como alternativas excluyentes). La Tabla 6.1 orienta cuál de los dos priorizar según el uso previsto cuando los recursos de cómputo son limitados (Capítulo 4, sección 4.4.1) y no es posible entrenar ambos.

<h3 id="cap6-6-2-5">6.2.5 Edición, exportación y publicación</h3>

SuperSplat para la edición y exportación de los modelos 3DGS (recorte de outliers, formatos .splat/.ply); conversión de la malla SfM a .glTF para publicación web e integración BIM (sección 6.3). La sección 5.6 (H5) documenta que este es, hoy, el paso menos resuelto del pipeline para el output de Nerfacto —sin una ruta de publicación web estándar—, algo que el Capítulo 7 retoma como línea de trabajo futura.

<h2 id="cap6-6-3">6.3 Propuesta de integración con flujos de trabajo HBIM/Revit</h2>

Esta sección responde al objetivo específico de la tesis de "diseñar una propuesta de integración del pipeline con flujos de trabajo de modelado HBIM/Revit como línea de continuación para la gestión patrimonial profesional" (Capítulo 1, sección 1.3.2). La integración con Revit/BIM propiamente dicha es una propuesta **conceptual**, sin implementación práctica dentro del alcance de esta tesis (Capítulo 1, sección 1.6.2); la sección 6.3.3, en cambio, documenta una prueba de concepto que sí se implementó y validó: un paso previo de segmentación semántica de la nube de puntos que prepara el terreno para esa integración futura.

<h3 id="cap6-6-3-1">6.3.1 Punto de entrada: la malla SfM</h3>

De las tres técnicas evaluadas, únicamente el output de SfM —malla poligonal con textura UV— tiene una ruta de integración directa con software BIM. Nerfacto y Splatfacto, por su naturaleza (campo neuronal implícito y nube de primitivas gaussianas respectivamente), no producen una malla poligonal navegable por un modelador BIM sin un paso adicional de conversión (extracción de superficie desde un campo de densidad, o meshing sobre las gaussianas), que ninguna herramienta del pipeline actual (Nerfstudio, SuperSplat) resuelve de forma nativa.

<h3 id="cap6-6-3-2">6.3.2 Flujo conceptual propuesto</h3>

1. **Malla SfM texturizada (.obj)** → decimación y limpieza topológica (reducción del triángulo-count desde los ~7–35 millones observados en los tres casos, Capítulo 5, Tabla del Capítulo 4 sección 4.6, a un nivel manejable por un modelador BIM, probablemente dos a tres órdenes de magnitud menor).
2. **Importación a un entorno de modelado** (por ejemplo, Recap Photo / Revit, o alternativas de código abierto) como nube/malla de referencia (*scan-to-BIM*), no como el modelo final.
3. **Modelado paramétrico manual o semiautomático** de los elementos arquitectónicos sobre la malla de referencia, siguiendo el estándar de niveles de detalle (LOD) propio de HBIM para patrimonio histórico —fuera del alcance técnico de esta tesis, pero documentado en la literatura relevada en el Capítulo 2—.
4. **Vínculo bidireccional documental**: conservar el output original de SfM (y, opcionalmente, los renders de Nerfacto/Splatfacto) como evidencia fotográfica/geométrica de respaldo del modelo HBIM final, replicando el criterio de trazabilidad ya aplicado en esta tesis a nivel de logs y datasets (Capítulo 4, sección 4.9).

<h3 id="cap6-6-3-3">6.3.3 Implementación preliminar: segmentación semántica de la nube de puntos</h3>

El paso 1 del flujo conceptual (sección 6.3.2) señala que la malla SfM texturizada necesita, antes de servir como referencia *scan-to-BIM*, un trabajo de limpieza y organización que hoy recae por completo en el modelador BIM: recorrer la nube o la malla completa e identificar a mano qué región corresponde a cada elemento constructivo (cubierta, columna, muro, piso) antes de empezar a levantar geometría paramétrica encima. Este cuello de botella está documentado en la literatura de *scan-to-BIM* para patrimonio —Romero-Jarén y Arranz (2021) lo describen como el paso "muy costoso en tiempo y enteramente delegado al trabajo manual de expertos, lejos de estar automatizado"— y motivó una prueba de concepto adicional dentro de esta tesis: un clasificador geométrico que segmenta automáticamente la nube densa de SfM en las cuatro clases relevantes para BIM antes de exportarla como referencia.

El script `poc_segmentation_multi_site.py` (Capítulo 4, sección 4.9) implementa esta clasificación sin redes neuronales ni datos de entrenamiento, apoyándose únicamente en propiedades geométricas locales de la nube:

1. **Nivelado**: ajuste del plano de piso por RANSAC y rotación de la nube para que quede horizontal, necesario porque ni RealityScan ni COLMAP nativo garantizan que el eje vertical del archivo crudo sea el "arriba" real de la obra (sección 5.5.2 documenta un caso concreto de este problema en Los Paraguas).
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

**Respaldo en la literatura y posicionamiento de este aporte.** La automatización de este paso —comúnmente llamada segmentación semántica de nubes de puntos para *scan-to-BIM*— es un área activa de investigación. Romero-Jarén y Arranz (2021) proponen un método de segmentación y clasificación automática de elementos BIM (pisos, techos, muros, columnas) a partir de nubes de puntos de interiores; Buldo et al. (2023) documentan un flujo *scan-to-BIM* específico para patrimonio cultural con segmentación automática y modelado paramétrico-adaptativo de sistemas abovedados; Croce et al. (2023) combinan clasificación por Random Forest con reconstrucción H-BIM semi-automática sobre claustros medievales; y Pan et al. (2024) usan una red neuronal profunda (KP-SG) para llevar nubes de puntos semánticas a modelos BIM semánticos en el contexto de un gemelo digital patrimonial. Frente a ese estado del arte, el aporte de esta tesis es modesto pero honesto: una clasificación geométrica simple —sin entrenamiento, sin dataset anotado, ejecutable con los mismos recursos consumer-grade del resto del pipeline (Capítulo 4, Tabla 4.2)— que demuestra, sobre los tres casos de estudio reales de esta investigación, que incluso ese enfoque liviano produce clases usables como punto de partida para el flujo de la sección 6.3.2. La adopción de un clasificador basado en aprendizaje profundo (siguiendo, por ejemplo, el enfoque de Pan et al., 2024) queda documentada como línea de trabajo futura (Capítulo 7), no como parte de esta implementación.

<h3 id="cap6-6-3-4">6.3.4 Limitación reconocida</h3>

La propuesta de integración con Revit/BIM propiamente dicha —el paso 2 en adelante del flujo conceptual de la sección 6.3.2— no fue validada con un modelador BIM real ni con un caso de uso profesional dentro de esta tesis; su valor es orientar la siguiente etapa de trabajo (Capítulo 7), no cerrar la pregunta de integración HBIM. La segmentación semántica de la sección 6.3.3 sí es una implementación funcional y validada sobre los tres casos de estudio —a diferencia del resto de la propuesta HBIM, que permanece conceptual—, pero se detiene en la nube de puntos clasificada: no genera geometría paramétrica, no exporta a un formato nativo de Revit (.rvt) ni a un formato de intercambio BIM estándar (IFC), y no fue puesta a prueba por un profesional de modelado BIM. Es, en los términos de la literatura citada, un paso semi-automático de preparación de datos, no un pipeline scan-to-BIM completo.

<h2 id="cap6-6-4">6.4 Lineamientos para el archivo digital de patrimonio arquitectónico web</h2>

A partir de la evidencia de la sección 5.6 (H5), se proponen los siguientes lineamientos para el repositorio/plataforma web mencionado como parte del alcance de esta tesis (Capítulo 1, sección 1.6.1):

- **3DGS (Splatfacto) como formato principal de exploración interactiva**, por su combinación de peso liviano (Tabla 5.14), buen desempeño de calidad visual (Tabla 5.2) y compatibilidad directa con visores web (sección 5.6).
- **La malla SfM (.glTF) como capa de referencia geométrica y documental**, útil para mediciones aproximadas y para usuarios que requieran un modelo poligonal (por ejemplo, integración con visores BIM ligeros), pese a su mayor peso — se recomienda ofrecer una versión decimada específicamente para web, distinta de la usada como insumo para la integración HBIM (sección 6.3).
- **Nerfacto como material de producción audiovisual**, no como parte directa del visor interactivo del archivo digital: los videos renderizados a lo largo de la trayectoria de captura (ya generados como parte del pipeline de cada caso de estudio) son el output más aprovechable de esta técnica para el objetivo de divulgación patrimonial.
- **Metadatos de trazabilidad por modelo**: sitio, técnica, dispositivo(s) de captura, fecha de relevamiento y estado de conservación documentado, siguiendo el mismo criterio de trazabilidad que esta tesis aplicó internamente a nivel de logs (Capítulo 4, sección 4.9) — relevante en particular para casos como el Panteón Asociación Española, cuyo estado de conservación condiciona la interpretación de cualquier resultado (Capítulo 4, sección 4.10).

<h2 id="cap6-6-5">6.5 Recomendaciones de infraestructura</h2>

El hardware consumer-grade utilizado en esta tesis (Capítulo 4, Tabla 4.2) resultó suficiente para completar los tres casos de estudio, pero con un costo de tiempo no despreciable —hasta 2 h 35 min de entrenamiento por modelo (Tabla 5.17)— y una incidencia directa en la tasa de fallos catastróficos (Capítulo 5, sección 5.7), concentrada en las etapas de mayor demanda de memoria (fusión densa de COLMAP, `ParallelDataManager` de Nerfacto sobre datasets grandes). Para un equipo de gestión patrimonial que busque adoptar este pipeline de forma sostenida, se recomienda:

- Priorizar una GPU con mayor VRAM disponible (8–12 GB o más) sobre un aumento de velocidad de cómputo puro, dado que las fallas observadas fueron predominantemente de memoria, no de tiempo.
- Mantener el criterio de esta tesis de entrenar Nerfacto sobre un subset del dataset cuando la escena supere el orden de las ~1000 imágenes (Capítulo 4, sección 4.4.1), y reservar el dataset completo para Splatfacto, que toleró los tres casos de estudio sin ese ajuste.
- Incorporar la verificación binaria de registro SfM (sección 6.2.3) como paso estándar de control de calidad, dado su bajo costo de cómputo relativo frente al riesgo de descartar datasets válidos.

<h2 id="cap6-6-6">6.6 Síntesis del capítulo</h2>

Este capítulo tradujo los resultados del Capítulo 5 en cuatro productos aplicados: (a) un criterio de selección de técnica según el tipo de objeto patrimonial y el uso previsto (Tabla 6.1), directamente respaldado por la evidencia cuantitativa y cualitativa recogida; (b) un pipeline definitivo documentado (Figura 6.1) que incorpora, como novedad respecto al diseño experimental original, un paso explícito de verificación binaria del registro SfM, motivado por el hallazgo metodológico más significativo de esta tesis (Capítulo 5, sección 5.5.2); (c) una prueba de concepto de segmentación semántica de la nube de puntos con control de calidad manual (sección 6.3.3), la única pieza de la propuesta HBIM que se implementó y validó sobre los tres casos de estudio, no solo se propuso conceptualmente; y (d) una propuesta conceptual de integración con flujos HBIM/Revit —construida sobre esa segmentación como punto de partida— y lineamientos para el archivo digital web, ambos aún pendientes de validación práctica con un profesional de modelado BIM. El Capítulo 7 retoma estos cuatro productos para las conclusiones generales y las líneas de investigación futura.

*— Continúa en Capítulo 7: Conclusiones —*
