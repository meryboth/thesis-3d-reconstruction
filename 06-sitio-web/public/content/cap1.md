<h2 id="cap1-1-1">1.1 Contexto y motivación</h2>

El patrimonio arquitectónico constituye una de las expresiones tangibles de la identidad cultural de un pueblo. En Argentina, el conjunto de edificios históricos representa un legado irreemplazable cuya conservación plantea desafíos técnicos, económicos y organizativos.

La documentación tradicional de este patrimonio se ha apoyado históricamente en fotografías y, más recientemente, en planos CAD elaborados por equipos de arquitectura. Sin embargo, estas metodologías presentan limitaciones: son costosas en tiempo y recursos humanos, difícilmente reproducibles con fidelidad ante intervenciones futuras, y ofrecen una representación parcial de la geometría y materialidad de los edificios. Hasta ahora ninguna técnica ha permitido plasmar el estado actual de estas obras de forma fehaciente con la capacidad de establecer un archivo que sea el punto de inicio para un plan de preservación.

En este contexto, las técnicas de visión computacional —en particular la fotogrametría, las redes neuronales de representación implícita conocidas como Neural Radiance Fields (NeRFs) y el método de Gaussian Splatting (3DGS)— han emergido como alternativas de alto potencial para la digitalización tridimensional de entornos construidos. Su principal ventaja radica en que permiten obtener modelos 3D densos, con textura y geometría detallada, a partir de conjuntos de imágenes sin necesidad de equipamiento de escaneo costoso. 

Sin embargo, la aplicación sistemática de estas técnicas al patrimonio histórico argentino permanece inexplorada en la literatura académica. Hay desconocimiento sobre qué técnicas implementar, cuáles son las ventajas de cada una de ellas y cuál sería el pipeline o el flujo de trabajo recomendado para llegar a archivos de calidad partiendo de un relevamiento fotográfico. Existe, por lo tanto, una brecha entre el estado del arte tecnológico y su transferencia efectiva al campo de la preservación patrimonial local.

La presente tesis nace de una doble pertenencia disciplinar: la de arquitecta formada en la FADU de la Universidad de Buenos Aires, y la de especialista en Tecnología de la Información que lidera un equipo de I+D en el cruce entre ramas como visión por computadora y computación espacial. Desde esa posición de intersección, el trabajo se propone investigar, comparar y sistematizar el uso de las tres familias de técnicas de reconstrucción 3D mencionadas, con el objetivo de desarrollar un pipeline reproducible para la documentación patrimonial —desde la captura de imágenes hasta la obtención de geometría texturizada— y evaluar su pertinencia en el contexto específico de la arquitectura histórica argentina.

<h2 id="cap1-1-2">1.2 Planteamiento del problema</h2>

La preservación del patrimonio arquitectónico argentino enfrenta una tensión estructural entre la urgencia de documentar y la escasez de recursos y de soluciones tecnológicas de avanzada que permitan acelerar estos procesos. Las instituciones responsables cuentan con capacidades técnicas y presupuestarias heterogéneas, lo que genera importantes asimetrías en la calidad y profundidad de los relevamientos existentes.

Frente a esta realidad, la adopción de tecnologías de reconstrucción 3D a partir de imágenes representa una oportunidad concreta, ya que se trata de métodos de costo relativamente bajo, escalables y compatibles con flujos de trabajo existentes en arquitectura y gestión patrimonial. Sus resultados pueden integrarse, por ejemplo, en modelos HBIM (Heritage Building Information Modelling), una metodología cada vez más utilizada para documentar, analizar y conservar edificaciones históricas. No obstante, la multiplicidad de herramientas disponibles —COLMAP, RealityScan, Nerfstudio, entre otras— y la ausencia de criterios de comparación adaptados al contexto local generan incertidumbre en los equipos técnicos que intentan adoptarlas.

En términos más precisos, el problema que aborda esta tesis puede formularse de la siguiente manera:

*¿Cuál es la técnica de visión computacional —fotogrametría, NeRFs o Gaussian Splatting— más adecuada para la reconstrucción tridimensional de patrimonio arquitectónico argentino a partir de imágenes, considerando distintos criterios de uso (precisión geométrica e integración BIM, síntesis de vistas, renderizado en tiempo real), así como la eficiencia computacional, la calidad visual y la aplicabilidad práctica en contextos de recursos limitados?*

Este interrogante central se desglosa en una serie de preguntas secundarias que estructuran el diseño experimental de la investigación:

- ¿Qué nivel de complejidad geométrica y ornamental de una obra condiciona la técnica de reconstrucción más adecuada para documentarla?

- ¿Es posible integrar en un mismo dataset imágenes provenientes de dispositivos con configuraciones de lente diversas (drone y cámara de acción) sin degradar la calidad de la reconstrucción?

- ¿En qué medida la limpieza y preprocesamiento del dataset de imágenes impacta en la fidelidad del modelo generado?

- ¿Los archivos de output resultantes son compatibles con su visualización en plataformas web de acceso abierto, y el pipeline en su conjunto es reproducible por terceros a partir de la documentación disponible?

<h2 id="cap1-1-3">1.3 Objetivos de la investigación</h2>

<h3 id="cap1-1-3-1">1.3.1 Objetivo general</h3>

Desarrollar un pipeline sistemático y reproducible para la reconstrucción tridimensional de patrimonio arquitectónico argentino mediante técnicas de visión computacional —fotogrametría, NeRFs y Gaussian Splatting—, evaluando comparativamente su desempeño y proponiendo criterios de selección fundamentados para su aplicación en contextos de documentación y preservación patrimonial.

<h3 id="cap1-1-3-2">1.3.2 Objetivos específicos</h3>

- Realizar un relevamiento crítico del estado del arte en técnicas de reconstrucción 3D a partir de imágenes, con énfasis en sus aplicaciones al patrimonio construido.

- Definir y ejecutar un conjunto de experimentos comparativos (benchmarks) que permitan evaluar el impacto de variables clave: preprocesamiento de imágenes, técnica de reconstrucción utilizada y composición del dataset de captura a partir de dispositivos con configuraciones de lente diversas.

- Proponer un pipeline definitivo documentado, desde la adquisición de imágenes hasta la obtención de malla poligonal con textura, optimizado para las condiciones del patrimonio arquitectónico argentino.

- Diseñar una propuesta de integración del pipeline con flujos de trabajo de modelado HBIM/Revit como línea de continuación para la gestión patrimonial profesional.

- Evaluar la asertividad y escalabilidad de las tres técnicas de reconstrucción ante niveles crecientes de complejidad geométrica y ornamental, mediante un diseño comparativo de tres casos de estudio representativos de baja, media y alta complejidad.

- Validar la compatibilidad de los archivos de output del pipeline con plataformas de visualización web de acceso abierto. 

<h2 id="cap1-1-4">1.4 Justificación y relevancia</h2>

<h3 id="cap1-1-4-1">1.4.1 Relevancia científica</h3>

Desde el punto de vista de la investigación en tecnología de la información, esta tesis contribuye al estado del arte en tres dimensiones. En primer lugar, sistematiza la comparación de tres familias de técnicas de reconstrucción 3D —fotogrametría basada en Structure from Motion (SfM), NeRFs y Gaussian Splatting— en un escenario de uso concreto y con métricas cuantitativas rigurosas, algo que los trabajos previos han abordado de forma parcial o en contextos distintos al patrimonial. En segundo lugar, introduce la variable del preprocesamiento de imágenes mediante flujos de trabajo en ComfyUI como factor experimental controlado, aspecto que no ha sido estudiado sistemáticamente en la literatura. En tercer lugar, orienta el análisis al patrimonio arquitectónico argentino, un corpus de casos prácticamente ausente en la producción académica internacional sobre el tema.

<h3 id="cap1-1-4-2">1.4.2 Relevancia disciplinar y social</h3>

Desde la perspectiva de la arquitectura y la gestión cultural, la investigación responde a una necesidad concreta del sistema de preservación patrimonial argentino: contar con metodologías de documentación digital accesibles, de bajo costo relativo y con resultados de precisión suficiente para orientar intervenciones de restauración. La posibilidad de generar nubes de puntos, mallas y modelos texturizados de edificios históricos a partir de video de drone o cámara convencional abre una ventana de oportunidad significativa para organismos con recursos limitados.

Asimismo, los resultados de esta investigación tienen el potencial de sentar las bases para la construcción de un repositorio digital de referencia del patrimonio construido argentino, con formatos interoperables con plataformas de visualización web y herramientas de BIM, contribuyendo así a los objetivos de democratización del acceso cultural.

<h3 id="cap1-1-4-3">1.4.3 Relevancia personal e interdisciplinar</h3>

Como autora de esta tesis puedo verificar que esta investigación tiene relevancia para mí a nivel personal y profesional, teniendo en cuenta mi formación como arquitecta y mi carrera profesional como investigadora en materia de tecnologías de visión por computadora. Estas dos profesiones me permiten articular con idoneidad los requerimientos técnicos del relevamiento arquitectónico con las capacidades computacionales de las herramientas de visión artificial. Esta doble perspectiva constituye en sí misma un valor metodológico: me permite evaluar los resultados no solo desde los parámetros técnicos, sino también desde la utilidad práctica que ofrecen para el trabajo de equipos de arquitectura y preservación.

<h2 id="cap1-1-5">1.5 Hipótesis de trabajo</h2>

La investigación se orienta por las siguientes hipótesis de trabajo, formuladas de manera falseable para guiar el diseño experimental:

**H1 — ESPECIALIZACIÓN POR TÉCNICA**

En lugar de una técnica dominante en términos absolutos, se hipotetiza que SfM, NeRF y 3DGS se especializan según el criterio de uso considerado: el método de fotogrametría SfM ofrece mayor interoperabilidad con flujos de trabajo BIM/HBIM y archivos de menor peso, lo que habilita la creación de un archivo digital de patrimonio arquitectónico argentino; NeRF ofrece la síntesis de vistas fotorrealista de mejor calidad para producción audiovisual y documentales patrimoniales; y 3D Gaussian Splatting ofrece el mejor desempeño de renderizado en tiempo real para entornos interactivos y motores de videojuegos.

**H2 — PREPROCESAMIENTO**

La aplicación de un pipeline de limpieza y preprocesamiento de imágenes —que incluya eliminación de fondos irrelevantes y eliminación de distractores que puedan alterar la interpretación del edificio como personas, aves o vehículos— produce mejoras medibles en la calidad de la reconstrucción respecto al uso de las imágenes crudas.

**H3 — COMPLEJIDAD GEOMÉTRICA**

El desempeño relativo de SfM, NeRF y 3DGS —medido en términos de calidad visual y estabilidad del resultado— se ve afectado de forma diferencial por el nivel de complejidad geométrica y ornamental del objeto relevado, siendo esperable una divergencia creciente entre técnicas a medida que aumenta dicha complejidad.

**H4 — DATASET MULTI-DISPOSITIVO**

Un dataset de captura compuesto por imágenes provenientes de dispositivos con configuraciones de lente diversas —un drone y una cámara de acción— puede integrarse en un único pipeline de reconstrucción sin degradar significativamente la calidad del modelo obtenido respecto a un dataset de un único dispositivo, y puede mejorar la cobertura angular de la obra relevada.

**H5 — COMPATIBILIDAD WEB Y REPRODUCIBILIDAD DEL PIPELINE**

Los archivos de output del pipeline son compatibles con su visualización en plataformas web de acceso abierto sin conversión adicional ni hardware especializado, y el pipeline completo —desde la captura hasta la edición del modelo final— es reproducible por terceros a partir de la documentación y de los archivos de configuración exportables de cada herramienta utilizada.

<h2 id="cap1-1-6">1.6 Alcance y limitaciones</h2>

<h3 id="cap1-1-6-1">1.6.1 Alcance</h3>

La presente tesis abarca las siguientes dimensiones de análisis y producción:

- Revisión del estado del arte en fotogrametría SfM/MVS, NeRFs y Gaussian Splatting, con foco en aplicaciones al patrimonio construido.

- Diseño y ejecución de un conjunto de experimentos comparativos sobre tres edificios de valor patrimonial argentino que representan una escala creciente de complejidad geométrica y ornamental —equipamiento urbano de geometría simple, arquitectura moderna de complejidad media y arquitectura ornamental de alta complejidad—, utilizando datasets de video/imágenes de drone y/o cámara convencional.

- Evaluación cuantitativa mediante métricas de calidad de imagen (PSNR, SSIM).

- Propuesta de un pipeline de adquisición, preprocesamiento y reconstrucción documentado y reproducible.

- Propuesta conceptual de integración con flujos de trabajo HBIM/Revit como líneas de trabajo futuro.

- Creación de un repositorio o plataforma web destinada a alojar, organizar y visualizar los modelos tridimensionales obtenidos, con el objetivo de conformar un archivo digital del patrimonio arquitectónico argentino.

<h3 id="cap1-1-6-2">1.6.2 Limitaciones</h3>

Se reconocen las siguientes limitaciones que enmarcan el alcance de las conclusiones:

- Las pruebas de la investigación estarán basadas en una selección de construcciones argentinas que pueda validarse su valor patrimonial y priorizando un registro exterior de los mismos por sobre uno interior.

- Los resultados en términos de tiempos de procesamiento estarán parcialmente condicionados por las capacidades del hardware disponible (GPU consumer-grade), lo que puede no ser representativo de entornos de producción profesional.

- La creación de los datasets centrales de análisis para cada construcción se realizará a partir de registros propios con equipos aptos para la metodología. Adicionalmente, con fines investigativos, se contempla el uso de datasets basados en videos de disponibilidad pública, con el objetivo de contrastar los resultados y entender cuál es la mejor forma de realizar un registro con drone o cámara consciente para el entrenamiento de modelos, garantizando siempre el debido crédito y respeto a los derechos de autor de los materiales utilizados.

- El análisis de integración con HBIM/Revit tendrá carácter conceptual y propositivo, sin implementación práctica dentro del alcance de esta tesis.

<h2 id="cap1-1-7">1.7 Estructura de la tesis</h2>

El presente trabajo se organiza en siete capítulos, cuya articulación responde a la lógica del método científico: del problema a la revisión teórica, del diseño experimental al análisis de resultados, y de los hallazgos a la propuesta aplicada.

- El Capítulo 1 —el presente— introduce el contexto, la motivación, el problema de investigación, los objetivos, las hipótesis y el alcance del trabajo.

- El Capítulo 2 desarrolla el marco teórico y el estado del arte, revisando los fundamentos matemáticos y algorítmicos de cada técnica de reconstrucción, los trabajos previos más relevantes y las herramientas de software disponibles.

- El Capítulo 3 describe el caso de estudio y la estrategia de adquisición de datos, incluyendo los criterios de selección del edificio, el proceso de captura de imágenes y el diseño del pipeline de preprocesamiento con ComfyUI.

- El Capítulo 4 presenta el diseño experimental, especificando las hipótesis operacionales, las variables controladas, las métricas de evaluación y el entorno de hardware y software utilizado.

- El Capítulo 5 analiza los resultados de los experimentos, comparando el desempeño de las técnicas y herramientas evaluadas en función de las métricas definidas.

- El Capítulo 6 sintetiza los hallazgos en un pipeline definitivo documentado e incluye la propuesta de integración con flujos de trabajo HBIM/Revit para la gestión patrimonial profesional.

- El Capítulo 7 presenta las conclusiones generales, contrasta los resultados con las hipótesis iniciales, identifica las limitaciones del trabajo y propone líneas de investigación futura.
