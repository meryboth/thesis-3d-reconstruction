El presente capítulo profundiza acerca de los fundamentos teóricos y el estado del arte de las tres familias de técnicas de reconstrucción tridimensional que constituyen el objeto de estudio de esta tesis: la fotogrametría basada en Structure from Motion (SfM), las redes neuronales de representación implícita conocidas como Neural Radiance Fields (NeRFs) y el método de Gaussian Splatting (3DGS). Se comienza por establecer una definición de patrimonio arquitectónico nacional que encuadra el problema desde una perspectiva histórica y argentina. Se revisan luego los principios algorítmicos de cada técnica, su genealogía terminológica, sus casos de uso específicos en la industria y las herramientas de software disponibles para su implementación. El capítulo cierra con una síntesis comparativa orientada a los criterios de selección de esta investigación.

<h2 id="cap2-2-1">2.1 El objeto de estudio: patrimonio arquitectónico argentino</h2>

A los efectos de esta investigación, se entiende por **patrimonio arquitectónico nacional** a la definición creada por el autor argentino Alfredo Conti en su libro “El patrimonio como representación del "nosotros". El caso de Argentina.”, ahí el autor plantea al patrimonio como una construcción humana —bienes materiales e inmateriales a los que la sociedad asigna valores que lo constituyen como referente simbólico de identidad—. Su definición se apoya en la definición de Llorenç Prats elaborada en el libro Antropología y patrimonio de 1997, quien destaca que esta colección de edificios debe tener "capacidad para representar simbólicamente una identidad".

Lo que interesa a esta tesis no es el debate teórico sobre qué debe o no considerarse patrimonio, sino la constatación de que existe un corpus extenso de edificios argentinos con valor patrimonial reconocido que carece de documentación digital sistemática. Hay múltiples debates en torno a la preservación del patrimonio nacional, el libro “Entre la renovación edilicia y la preservación patrimonial” de María de las Mercedes Bracco plantea una tensión existente entre el carácter orgánico de las ciudades y la necesidad de una preservación de la arquitectura que permita construir una identidad cultural. Se data que en el año 1940, bajo la ley 12.665 se ordena la creación de Comisión Nacional de Museos y de Monumentos y Lugares Históricos, y una de las primeras responsabilidades vinculadas a la creación de este organismo es que se realice un censo nacional con el fin de identificar un “Registro de los bienes históricos e histórico-artísticos”. El libro menciona que en el año 1944, con la creación del Código de Edificación, se crea también un “registro de edificios de interés histórico”. Este antecedente marca uno de los primeros indicios de la creación de un archivo que pretende dar cuenta del historial de edificios que pertenecen a esta categoría, sin embargo desde 1944 hasta el presente existieron decenas de intentos de crear un registro nacional que pueda mantenerse actualizado y sea escalable en su mantenimiento. Si nos limitamos sólo a archivos nacionales digitales podemos afirmar que todos los registros de historial patrimonial digitales existentes contienen documentación bidimensional de las obras, desde imágenes hasta escaneos digitales de planos, alzadas y documentación técnica vinculada a la construcción de las obras. Un ejemplo es el Archivo de la Ciudad ([<u>https://archivodelaciudad.org/</u>](https://archivodelaciudad.org/)), creado por el gobierno de la Ciudad de Buenos Aires en 2021 y descontinuado en 2025, y el Portal Nacional de Arquitectura: ([<u>https://www.argentina.gob.ar/bienesdelestado/cediap-pp/portal-nacional-de-arquitectura</u>](https://www.argentina.gob.ar/bienesdelestado/cediap-pp/portal-nacional-de-arquitectura)) que cuenta con un historial de documentos de edificios públicos como el Teatro Colón y la Casa Rosada, por mencionar algunos, pero que tiene un listado limitado y donde solo se encuentran planos de las obras e imágenes de su documentación. Como se plantea en el Capítulo 1, la presencia de registros que hacen referencia a la existencia de un archivo siempre son limitados, no cuentan con obras completas y en su mayoría cuentan con documentación vinculada a las obras que es escasa o está desactualizada, y que impide enterar cuál es el estado actual de las mismas.  

Que no existan archivos digitales para consultar el patrimonio dificulta la resolución de un conflicto que identifica Mercedes Bracco en su libro, sin la existencia de un archivo es difícil pensar que la tensión que ella menciona en cuanto a la preservación del carácter edilicio de la ciudad pueda resolverse, en sus palabras: "la necesidad de construir un relato unificador... constituyó una base ideológica fuerte que restringió la noción de patrimonio hasta hace pocas décadas". A esta problemática se suma otro aspecto importante: si los pocos archivos digitales existentes sólo contienen material bidimensional de las obras como planos y documentaciones es difícil mantener un registro que nos permita entender el estado actual de las mismas y operar de forma activa para promover su preservación o mantenimiento.

La digitalización tridimensional de estos edificios abre una oportunidad concreta: generar un archivo digital de referencia que persista más allá del deterioro físico de los objetos y que sea accesible, distribuible y enriquecido por múltiples actores sin requerir infraestructura costosa. Este objetivo introduce un criterio de evaluación central en esta tesis —el peso del archivo de output— que se suma al de calidad visual: para que un repositorio patrimonial sea verdaderamente escalable, los modelos generados deben poder distribuirse y visualizarse sin hardware especializado ni anchos de banda extraordinarios. Lo que nos permitirá conseguir este historial de archivos tridimensionales de los edificios patrimoniales a escala nacional es:  
a) **Trazar una diferencia entre la arquitectura documentada y la construida:** La representación tridimensional que obtendremos utilizando fotogrametría, neural radiante fields y gaussian splatting permiten generar una reproducción de la obra en tres dimensiones a partir de la obra construida y no a partir de su documentación, por lo tanto la reproducción que consigamos puede llegar a ser más fiel que la documentación que se generó para construir la obra.

b\) **Tener un histórico del estado de la obra en tiempo real en el momento de la captura:** El archivo generado va a plasmar con detalle la obra en el instante en el cual se generó el registro, permitiendo también capturar aquellas patologías que aparecen en la misma con el paso del tiempo, como manchas de humedad, deterioros en la pintura, y demás registros. Algo que permitiría a un equipo de restauración realizar análisis de diagnóstico de los edificios que pueden utilizarse en posteriori para un plan de restauración. Por otro lado, la naturaleza del registro capturado en tiempo real permite comparar la obra con el paso del tiempo y obtener un timelapse de su transformación o deterioro.

c\) **Habilitar un archivo digital disponible para todos:** La democratización de la información y el acceso indiscriminado propone no sólo difundir la cultura del país sino también agilizar el desarrollo de nuevas e innovadoras investigaciones que pongan en foco en la historia arquitectónica del país y su legado.

Para concretar la creación de este archivo tridimensional accesible y escalable, resulta fundamental analizar las herramientas tecnológicas que permiten la captura y representación digital del patrimonio. A continuación, se examinan las tres familias de técnicas de reconstrucción 3D que constituyen el núcleo metodológico de esta investigación: la fotogrametría basada en Structure from Motion (SfM), los Neural Radiance Fields (NeRFs) y el método de Gaussian Splatting (3DGS). El estudio técnico que sigue no solo define sus fundamentos algorítmicos y su genealogía, sino que también evalúa su capacidad para responder a los desafíos específicos de documentación patrimonial, interoperabilidad y eficiencia que se plantearon en la sección anterior.

<h2 id="cap2-2-2">2.2 Fotogrametría basada en Structure from Motion (SfM)</h2>

<h3 id="cap2-2-2-1">2.2.1 Genealogía del término y antecedentes históricos</h3>

El término **fotogrametría** fue introducido por Albrecht Meydenbauer en 1867, a partir de una denominación propuesta junto con Otto Kersten en el artículo *"Die Photogrammetrie"* (Grimm, 2007). Sin embargo, sus antecedentes metodológicos se remontan a los trabajos de Aimé Laussedat, quien aplicó fotografías a relevamientos topográficos durante la década de 1860 bajo la denominación de *metrophotography*. 

El aspecto más importante de la fotogrametría tiene que ver con la técnica que se utiliza para realizar la reconstrucción, y lo que instala esta disciplina es el concepto de que se puede utilizar un método geométrico para calcular la posición, el ángulo y la altura de una cámara al momento de sacar una fotografía. En 1860 se utilizaba esta técnica para medir aspectos topográficos o calcular de forma aproximada la distancia entre una fotografía y un edificio. Laussedat es considerado el padre fundacional de la disciplina, al demostrar por primera vez la posibilidad de extraer información métrica tridimensional de imágenes bidimensionales (Polidori, 2020).

Por su parte, **Structure from Motion (SfM)** surge como problema formal dentro de la visión computacional con los trabajos de Shimon Ullman, particularmente su artículo de 1979 *"The interpretation of structure from motion"*, donde se estudia la recuperación de estructura tridimensional a partir del movimiento aparente en secuencias de imágenes (Ullman, 1979). La denominación *fotogrametría SfM* como convergencia de ambas tradiciones no tiene un único acto fundacional, sino que emerge progresivamente durante los años 2000 con el desarrollo de algoritmos automáticos de emparejamiento de puntos de interés y el abaratamiento del hardware de cómputo. Lo que hoy conocemos como SfM y fotogrametría se consolida entre 2010 y 2020, cuando se define un workflow concreto que combina visión por computadora con la técnica algorítmica creada por Laussedat para calcular la posición y la ubicación exacta de una cámara al momento de sacar una fotografía. Lo que en 1860 sucedía aplicado a una fotografía en concreto en 2010 ya estaba ocurriendo sobre un dataset de cientos de imágenes y con la finalidad de no solo conseguir el posicionamiento de las cámaras sino además reconstruir una nube de puntos densa que pueda representar geométricamente el objeto capturado. 

<h3 id="cap2-2-2-2">2.2.2 Fundamentos del método</h3>

Para que ocurra el proceso completo de reconstrucción es necesario que se combinen dos procesos juntos, por un lado el SfM y por otro el MVS (Multi-View Stereo), el primero va a construir un camino de cámaras y posiciones y el segundo va a ser el responsable de construir la nube de puntos. 

Dentro del pipeline completo suceden los siguientes procesos:

- **Identificación de keypoints:** Se detectan puntos o también llamados keypoints. Esto se hace mediante descriptores que reciben el nombre de Scale-Invariant Feature Transform (SIFT) o *Speeded-Up Robust Features* (SURF). Si lo llevamos al terreno de investigación de esta tesis podemos decir que estos keypoints van a ser puntos importantes de la obra: puede ser la esquina de una losa, el comienzo de una columna, un punto que marca el remate de una cubierta, por mencionar algunos casos. 

- **Matching de puntos:** En este paso se busca emparejar correspondencia o matching entre pares de imágenes. Con el fin de empezar a entender la posición de las cámaras y su orientación el algoritmo busca correspondencia entre puntos de forma tal que pueda empezar a entender la relación que hay entre las imágenes en relación a la escena y a sí mismas. 

- **Posicionamiento relativo de cámaras:** Con la información del paso previo el algoritmo empieza a construir una especie de camino o roadmap del recorrido de las cámaras en relación al objeto. Para eso utiliza Random Sample Consensus (RANSAC). 

- **Nube de puntos**: A partir de una triangulación incremental se genera una nube de puntos dispersa que va a representar la estructura general de la escena. Durante este paso también se realizan ajustes sobre la posición de las cámaras y las orientaciones con el fin de mejorar la interpretación y reducir los posibles errores.

- **Ajuste global:** Este paso se conoce como el procesamiento de bundle adjustments y es básicamente una optimización global de los resultados. 

- **Nube de puntos densa:** En este proceso entra en juego el MVS que lo que hace es generar una nube de puntos densa. Este paso le incorpora mayor detalle a la escena a partir de la incorporación masiva de varios puntos más que permiten completar la reconstrucción.   

Esta interpretación de los pasos que suceden durante el procesamiento de SFM en combinación con MVS fue realizada a partir de la interpretación de la publicación de  Croce et al. en el 2024. 

![](/content/assets/cap2-image3.webp)

<h3 id="cap2-2-2-3">2.2.3 Fortalezas y desafíos para la documentación patrimonial</h3>

Lo más interesante de esta técnica, que podríamos decir que se remonta a conceptos geométricos y algoritmos de al menos un siglo atrás, es que su resultado tiene una precisión geométrica de mucha exactitud. Si bien es importante destacar que el output final va a depender siempre de la calidad del dataset implementado y de las técnicas de captura de imagen, podemos confirmar que la literatura indica que ante un registro completo de un edificio el pipeline de fotogrametría puede generar un resultado de precisión alta que es compatible con flujos de trabajo BIM ya utilizados en la industria (obteniendo formatos como .obj y .ply que ya tienen alta compatibilidad con softwares de modelado como Blender o Revit). Yu et al. (2025) confirman que SfM es la opción más compatible para la integración con herramientas de documentación y análisis patrimonial profesional.

Un desafío vinculado a este tipo de procesamiento está relacionado al peso de los archivos, generalmente las mallas texturizadas y las nubes de puntos densas que pueden obtenerse como resultado de este procesamiento suelen generar outputs muy pesados (superando los 100 MB), lo cual puede complicar la posibilidad de pensar en un archivo digital que renderice online estos edificios. 

Otro posible desafío está vinculado a la reproducción de algunas de las superficies arquitectónicas al momento de realizar la reconstrucción, algunas publicaciones mencionan dificultades al momento de capturar superficies reflectantes o áreas translúcidas. Otra alarma está vinculada a las áreas de sombra o oclusiones, que pueden ser interpretadas de forma errónea al momento de la reconstrucción, esto es algo que ya advierte Yu et al. (2025). A modo de solución algunas publicaciones sugieren la posibilidad de realizar un post-procesamiento de los resultados con el fin de mejorar la percepción del edificio, pero a través de un proceso de intervención manual. 

<h3 id="cap2-2-2-4">2.2.4 Herramientas de software</h3>

Las dos soluciones más sólidas y mencionadas en publicaciones académicas son COLMAP y RealityScan (de Epic Games). Ambas son herramientas de código abierto, que no necesitan un hardware costoso de ejecución y que presentan métricas de usabilidad altas. Entre otras soluciones también aparecen Meshroom (de AliceVision) y Metashape (de Agisoft), esta última mencionada por Croce et al. (2024) en su investigación. Si bien todas parecen ser alternativas viables para la ejecución y garantizan resultados óptimos es importante destacar que las últimas mencionadas requieren un consumo de memoria RAM superior a las primeras. 

<h2 id="cap2-2-3">2.3 Neural Radiance Fields (NeRF)</h2>

<h3 id="cap2-2-3-1">2.3.1 Genealogía del término y antecedentes históricos</h3>

La principal diferencia conceptual entre NeRF y fotogrametría es que la segunda hace foco en intentar reconstruir la geometría de la escena, mientras que el proceso de Neural Radiance Fields lo que busca es entender cómo se visualiza esa escena desde cualquier punto de vista. El término aparece por primera vez en la literatura en 2020 cuando se publica *"NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis"* con autoría de Mildenhall et al. El paper busca representar la capacidad de este algoritmo de reconstrucción al momento de reproducir una escena de un campo abierto, y detrás de este procesamiento hay un modelo que lo que busca es aprender a través de fotografías cómo debería verse un determinado edificio desde cualquier posición.

<h3 id="cap2-2-3-2">2.3.2 Fundamentos del método</h3>

Cuando se corre un entrenamiento de un modelo NeRF lo que sucede podría resumirse en los siguientes pasos:

- **Recepción de las imágenes y ubicación de las fotografías:** Lo primero que hace el procesamiento es cargar el dataset y luego invocar un proceso de SfM para entender la ubicación de esas imágenes y la posición de las cámaras. Este paso es uno de los más interesantes, porque coincide con la primera gran etapa dentro del procesamiento de fotogrametría. 

- **Comprender la escena:**  El modelo comienza a comprender la escena y lo primero que hace es identificar qué color hay detrás de cada punto y cuál es su grado de densidad. Otra cosa que hace el modelo es simular rayos entre la ubicación de estas cámaras y los distintos puntos de las escenas, creando una especie de red imaginaria que busca identificar la ubicación y la formación de los píxeles. 

- **Predicción de píxeles:** A partir de la información que recolectó en pasos anteriores lo que hace el modelo es predecir el color y la densidad de los píxeles y luego va comparando esa predicción con las imágenes reales, si el color no está bien en el píxel hace un ajuste en la red. Este proceso lo hace infinidad de veces para mejorar el entrenamiento. 

- **Generación de vistas nuevas:** Una vez que finaliza el entrenamiento el modelo te permite cargar paths o rutas nuevas de cámara y te muestra los resultados de cómo considera que debería verse la escena desde ese nuevo punto de vista. 

Que el procesamiento se base en la interpretación de píxeles y sus características de densidad y color ya es un cambio significativo en relación al proceso de fotogrametría, y también anticipa algo importante a considerar de cara a entender el proceso de NeRF: el output de un NeRF lo vamos a analizar a partir del renderizado de rutas y no tanto a partir de la interpretación volumétrica del archivo. Esta descripción del procesamiento de NeRF es una interpretación de los pasos que menciona Croce et al., en su publicación de 2024. 

![](/content/assets/cap2-image4.webp)

<h3 id="cap2-2-3-3">2.3.3 Fortalezas y desafíos para la documentación patrimonial</h3>

Hay un término vinculado al procesamiento en NeRF y es novel view synthesis, lo que indica este concepto es que este tipo de entrenamiento es perfecto para reconstruir imágenes o videos renderizados de registros que no sean exclusivamente el material que se utilizó para el entrenamiento. Dicho esto, es importante entender la importancia de NeRF como herramienta para ayudarnos a "Expandir el universo" de aquellas escenas que buscamos reconstruir, y entender su oportunidad única para generar material nuevo a partir de estos registros. El resultado esperado de estos outputs es tan bueno como la calidad del dataset y las métricas del entrenamiento, pero la literatura indica que hay resultados fotorrealistas de gran calidad, que permiten entender en profundidad e incorporar nuevos puntos de vista únicos a partir de escenas reconstruidas. 

A pesar de esta distinción, creo que hay un aspecto que es importante destacar y es que todo parece indicar que NeRF es una técnica más orientada a la reconstrucción audiovisual de material, que una técnica que nos permita obtener registros tridimensionales que puedan integrarse a pipelines a archivado y reconstrucción a partir de procesos BIM. Otros casos de uso que puedo llegar a imaginarme vinculan a esta herramienta con la posibilidad de generar registros en video que pueden llegar a utilizarse para documentales que destaquen el valor patrimonial de la obra, siendo el universo cinematográfico el mayor beneficiado al momento de sacarle provecho a esta tecnología. 

Pese a estas conclusiones anticipadas se destaca que Croce et al. (2024) reportan que, ante escenarios de un dataset pobre NeRF supera a la fotogrametría en la preservación de la interpretación de la obra como un todo y en la capacidad para reproducir fielmente los materiales. Por lo tanto se espera que las capacidades de reconstrucción sean superiores incluso en escenarios donde el dataset puede llegar a ser pobre. 

Otro desafío vinculado a esta tecnología está relacionado con el costo computacional al momento de generar los entrenamientos. Rangelov et al. (2026) documentan tiempos de entrenamiento superiores a 30 minutos incluso en corridas optimizadas. La publicación también identifica que el resultado de NeRF es un archivo de un tamaño grande, algo que podría dificultar nuestro objetivo de construir un archivo digital que tenga un rendimiento web óptimo. 

<h3 id="cap2-2-3-4">2.3.4 Herramientas de software</h3>

Teniendo en cuenta nuestro interés en soluciones open source Nerfstudio lidera el mercado como un framework de código abierto basada en python, otra alternativa es Instant-NGP, y NVIDIA lanzó para Unreal Engine NVIDIA Omniverse que apunta sobre todo a aplicativos de producción audiovisual. 

<h2 id="cap2-2-4">2.4 3D Gaussian Splatting (3DGS)</h2>

<h3 id="cap2-2-4-1">2.4.1 Genealogía del término y antecedentes históricos</h3>

La técnica de Gaussian Splatting es la más nueva de las tres, y la que mayor literatura tiene vinculada, ya que en términos de metodologías de visión por computadora para recreación en tres dimensiones es el método más mencionado en papers y publicaciones académicas, liderando los rankings con un promedio de 425 publicaciones en menos de un año. 

En términos simples lo que crea este algoritmo es una reconstrucción 3D a partir de cientos y cientos de gaussianas, que actúan como partículas con distintos tamaños, posiciones y transparencias. El término gaussiana hace referencia a las campanas de Gauss, la forma geométrica que representa un centro concentrado que va debilitándose en sus extremos. En su expresión tridimensional estas gaussianas en realidad parecen elipses difusos, que depende el nivel de aproximación que tengas con la forma geométrica pueden percibirse como curvaturas o de lejos pueden parecer simplemente manchas o píxeles. Lo que hace el algoritmo al momento de la reconstrucción es ir generando gaussianas en distintas posiciones, con distintos tamaños y ubicación con el fin de que la reconstrucción se parezca a lo que está en la fotografía, en un proceso de entrenamiento continuo que busca mejorar en cada ciclo que repite. 

La expresión splatting aparece por primera vez en una publicación de 1990 de Lee Westover llamada *"Footprint evaluation for volume rendering"*. Lo revolucionario de la publicación es que Westover plantea la posibilidad de utilizar una primitiva volumétrica (que puede ser una gaussiana o cualquier otra forma) como unidad para construir volumen. En la tesis original esta primitiva podía ser una esfera, un elipsoide o cualquier función espacial. Recién en 2023 esta tesis evoluciona en el concepto de Gaussian Splatting cuando se publica *"3D Gaussian Splatting for Real-Time Radiance Field Rendering"* por Kerbl et al. Lo que proponen los autores a partir de esta publicación es construir una alternativa a otras reconstrucciones 3D (como NeRF) utilizando la tesis de primitivas como modo de generación de volumen, proponiendo el gaussian como forma repetitiva y a la vez presentando la capacidad de esta técnica de renderizarse en tiempo real.

<h3 id="cap2-2-4-2">2.4.2 Fundamentos del método</h3>

A continuación vamos a repasar los distintos procesos que se ponen en juego al momento de generar un gaussian splatting:

- **Consumo de datos:** Al igual que en el procesamiento NeRF el primer paso es la recepción del dataset y la incorporación un archivo tipo colmap que contenga definidas las cámaras y sus posiciones. 

- **Nube de puntos:** Lo primero que genera es una nube inicial de puntos que plantea de forma muy genérica la escena pero que va a ser el puntapié para la ubicación del resto de las gaussianas. 

- **Primeras gaussianas:** En un segundo paso cada punto se transforma en una gaussiana. Acá podemos hacer un paralelo con SfM, en lugar de tener una escena con puntos estructurales tenemos una escena con 'manchas', que en realidad son una serie de gaussianas que marcan de forma parcial los aspectos más relevantes de la escena. A su vez cada gaussiana tiene vinculada una serie de propiedades que tienen que ver con su ubicación, su tamaño, su forma, su color, etc. 

- **Proyección en imágenes:** Para continuar el entrenamiento el algoritmo proyecta las gaussianas sobre las imágenes para simular cómo estas deberían verse para representar de forma fiel la escena. Esta comparación permite hacer ajustes en la estimación de gaussianas para entrar en un ciclo de mejora en cada ciclo del entrenamiento. 

- **Entrenamiento iterativo:** Durante cada paso de optimización el sistema agrega gaussianas nuevas, mueve las que generó y continúa iterando hasta lograr un resultado que se parezca a las fotografías del dataset. 

- **Resultado:** El resultado final es una escena en tres dimensiones, donde las gaussianas se acomodan a la visualización del usuario para permitirle que en cada visual vea una reconstrucción de la escena fiel a lo generado durante el entrenamiento. 

![](/content/assets/cap2-image2.webp)

<h3 id="cap2-2-4-3">2.4.3 Fortalezas y desafíos para la documentación patrimonial</h3>

La mayoría de las publicaciones hablan de esta técnica como la más rápida de las tres y mencionan los increíbles resultados que se pueden lograr de reconstrucción con costos computacionales bajos y escaso tiempo. Este aspecto puede llegar a ser una variable importante al momento de definir el pipeline porque esperamos que haya un flujo de trabajo que pueda ser reproducible sin muchos costos. Rangelov et al. (2026) confirman que 3DGS completó la reconstrucción de escenas complejas en aproximadamente 10 minutos frente a más de 30 de NeRF. Yu et al. (2025), un dato que permite validar el potencial de esta herramienta al momento de competir con NeRF.

Actualmente hay evidencia de la utilización de un pipeline en concreto que es utilizando el motor Unreal Engine y su software RealityCapture y el caso de uso abordado es la recreación de entornos urbanos con la finalidad de utilizar esos escenarios en escenas de ficción y desarrollo de videojuegos. Este antecedente puede llegar a ser clave para entender la viabilidad de utilizar un pipeline parecido pero con el fin de crear un archivo de documentación de edificios nacionales, como lo es el objetivo de esta tesis. 

Otro de los aspectos destacables es su capacidad para generar archivos que puedan tener un grado de edición manual con el fin de mejorar el resultado final: Chen y Wang (2024) destacan que 3DGS introduce niveles de editabilidad sin precedentes respecto a NeRF, ya que sus primitivas gaussianas son entidades explícitas manipulables individualmente. Para esto se expone SuperSplat como el software de soporte nativo en navegadores como una de las soluciones más utilizadas. 

Mientras la geométrica exportable de nube de puntos de los procesos de fotogrametría es compatible con varios software de arquitectura, el desafío de los resultados de 3DGS es que la geometría exportable es más ruidosa e incompleta que una nube densa por lo tanto la reconstrucción a partir de este tipo de archivos representa un desafío adicional si lo que se busca es un proceso de documentación del estilo BIM. 

Al momento de realizar la captura también hay una serie de advertencias que aparecen en varias publicaciones académicas, como Rangelov et al. (2026), donde se percibe que algunas materialidades pueden ser desafiantes al momento de la reconstrucción, en especial al momento de capturar cielo o revoques con textura uniforme. 

En cuanto al peso de los archivos y la posible compatibilidad con soporte web es posible afirmar que esta técnica es la más prometedora, si bien el output original suele ser bastante pesado, la posibilidad de convertir los resultados y exportarlos en formato .splat hace que en pocos megabytes tengamos condensada escenas de gran complejidad y extensión geométrica. 

<h3 id="cap2-2-4-4">2.4.4 Herramientas de software</h3>

Si priorizamos las soluciones de software libre como en los otros casos vamos a encontrarnos con que Nerfstudio es la solución más óptima (y permitiría utilizar un mismo software open source para ejecutar tanto el entrenamiento de NeRF como el de Gaussian Splatting). También hay alternativas pagas como Postshot, Luma AI, y Polycam, que quedan fuera del alcance de lo que buscamos por su licencia paga y también porque permiten la configuración de menos aspectos al momento de ejecutar el entrenamiento, algo que teniendo en cuenta la naturaleza de esta investigación puede generar limitaciones. En cuanto a la visualización y edición de escenas SuperSplat es la alternativa más sólida ya que se trata de una solución opensource que corre en navegadores web y que permite no solo editar los splats sino también compartirlos con una comunidad. Al momento de pensar en una solución que nos permita integrar los resultados en un soporte web existe PlayCanvas que es un framework de Frontend para poder renderizar resultados de gaussian splatting que tengan una complejidad geométrica elevada pero que puedan performar de forma aceptable en navegadores. 

<h2 id="cap2-2-5">2.5 Comparación de técnicas: síntesis y criterios de selección</h2>

La revisión de la literatura y la combinación con los criterios específicos de esta investigación —documentación patrimonial argentina, interoperabilidad con BIM, construcción de un repositorio digital accesible— permite proponer una lectura comparativa orientada a descubrir a partir de la investigación cuál es la fortaleza de cada técnica y qué tipo de método de reconstrucción podemos utilizar para dicho fin. A continuación voy a detallar los criterios de aceptación que van a estar jugando un rol crítico al momento de establecer los componentes que definan el pipeline final. 

**Criterio 1: Precisión geométrica e integración con BIM/Revit**

Podemos asumir que la técnica de fotogrametría es la mejor candidata para este fin ya que se trata de una de las técnicas con mayor dominio al momento de integrarse con software BIM. Autodesk creó la herramienta ReCap que permite integrar archivos de nube de puntos a otros programas de la suite encargados de documentar proyectos de arquitectura como Autocad y Revit. Si vamos por el camino de utilizar los resultados de NeRF y 3DGS es probable que tengamos que implementar algún tipo de conversión en los resultados que puede alterar la calidad de los mismos. 

**Criterio 2: Peso del archivo y escalabilidad del repositorio patrimonial**

Los archivos que contienen nube de puntos como parte del procesamiento de fotogrametría y la conversión a .splats para archivos de 3DGS se posicionan como los formatos más livianos del mercado. Si bien el benchmark que realicemos de resultados terminará indicando las métricas reales de cada metodología podemos afirmar de antemano que la literatura consultada indica que los resultados en NeRF suelen tener un peso alto, y algunas versiones de nube de puntos y gaussian splattings también puede complicar mucho su renderizado en navegadores. 

**Criterio 3: Posibilidad de editar los outputs**

Teniendo en cuenta que todos los resultados pueden contener errores, producto de la naturaleza de las reproducciones es importante como validación que estos outputs puedan ser editables. Tanto los archivos de fotogrametría como lo de gaussian splatting pueden editarse de forma sencilla, en cambio NeRF tiene más desafíos para tolerar la edición de los mismos teniendo en cuenta las conclusiones de varias publicaciones analizadas. 

**Criterio 4: Capacidad de reconstruir el pipeline**

Hay dos criterios de aceptación que marcan el diseño de esta investigación y que tienen como protagonista el uso de herramientas open source para la construcción de este flujo de trabajo. Esta decisión está vinculada a la disponibilización de un pipeline que sea reproducible por otros y democratizable a nivel accesibilidad. Es por eso que las herramientas elegidas para construir el pipeline deben ser de acceso libre y gratuitas, priorizando aquellas que puedan ejecutarse en entornos que impliquen bajo costo computacional. 

**Criterio 5: Robustez ante la complejidad geométrica y ornamental**

Durante la investigación del marco teórico para esta investigación se encontró evidencia que la complejidad geométrica afecta de forma variable a cada una de estas técnicas, es por eso que parte de esta tesis es descubrir la potencialidad de cada método de reconstrucción y aprender las limitaciones que pueden tener al momento de generar la reconstrucción (Croce et al., 2024). 

Un hallazgo relevante del estado del arte es la tendencia emergente hacia la hibridación. Fang et al. (2025) proponen NeRF-GS, que combina representaciones continuas de NeRF con representaciones discretas de 3DGS. Lyu et al. (2025) incorporan SDF implícitas en 3DGS para mejorar la geometría. Estos desarrollos apuntan hacia una convergencia en la que las fronteras entre técnicas se vuelven progresivamente más porosas. El siguiente gráfico pretende resumir los hallazgos descubiertos durante la investigación de publicaciones académicas con el fin de anticipar en una escala de 1 a 5 cuáles son las fortalezas y debilidades de cada técnica. 

![](/content/assets/cap2-image1.webp)

*\[Tabla 2.1 — Comparación de técnicas SfM, NeRF y 3DGS según criterios de selección para documentación patrimonial argentina. **Escala ordinal de desempeño:** 0 = nulo, 1 = muy bajo, 2 = bajo, 3 = medio, 4 = alto y 5 = muy alto. Las puntuaciones sintetizan la literatura revisada y expresan una valoración comparativa, no mediciones experimentales absolutas. Fuente: elaboración propia a partir de Yu et al. (2025), Rangelov et al. (2026), Croce et al. (2024), Chen y Wang (2024), Fang et al. (2025).\]*

<h2 id="cap2-2-6">2.6 Criterios de evaluación y métricas</h2>

Los criterios de evaluación y las métricas definidas a continuación han sido propuestas teniendo en cuenta mecanismos empíricos de otras publicaciones académicas que han dado cuenta de que estas métricas permiten validar cuestiones como la calidad de imagen, el peso del archivo, la eficiencia computacional, y demás. A continuación se detalla cada métrica y se expone en el caso que corresponda la publicación o el libro que inspiró su uso. 

<h3 id="cap2-2-6-1">2.6.1 Métricas de calidad de imagen</h3>

Las dos métricas más utilizadas para medir calidad de imagen son PSNR y SSIM. El PSNR (Peak Signal-to-Noise Ratio) mide la relación entre la señal máxima posible y el ruido de reconstrucción en decibelios; valores más altos indican mayor fidelidad. El SSIM (Structural Similarity Index Measure) evalúa la similitud estructural considerando luminancia, contraste y estructura, y correlaciona mejor con la percepción visual humana. Rangelov et al. (2026) utiliza ambas métricas para medir la calidad de los resultados, por lo cual es válido pensar que ambas métricas pueden utilizarse en el diseño experimental de esta tesis. 

<h3 id="cap2-2-6-2">2.6.2 Criterio de peso del archivo</h3>

Con el objetivo de construir un archivo digital que pueda ser accesible desde navegadores webs uno de los aspectos importantes de esta investigación es validar que la técnica que elijamos para el pipeline tenga garantizado un tamaño bajo de output. Se medirá el tamaño en MB del modelo final en su formato de distribución estándar (.glTF para SfM, .SPLAT comprimido para 3DGS, pesos del MLP para NeRF), y se considerará la compatibilidad con plataformas de visualización web de acceso abierto como SuperSplat, Sketchfab, Potree o [<u>Three.js</u>](http://three.js).

<h3 id="cap2-2-6-3">2.6.3 Métricas de eficiencia computacional: tiempo de procesamiento y tasa de fallos</h3>

Como criterio adicional vinculado a la eficiencia operativa del pipeline, se evaluará el tiempo de procesamiento por técnica y etapa sobre una configuración de hardware de referencia detallado en la tabla 2.2, junto con la tasa de fallos observada durante la ejecución, clasificada en fallo catastrófico (el proceso no llega a generar un output, por ejemplo por agotamiento de memoria o divergencia del optimizador), fallo parcial (el modelo se genera con artefactos severos —huecos, *floaters*, regiones no reconstruidas— que lo vuelven inutilizable) e inestabilidad de convergencia (requiere reinicios o ajuste manual de hiper parámetros). A continuación se especifican las condiciones del hardware donde va a estar ejecutándose el experimento. Es importante mencionar que el mismo es considerado consumer-grade, es decir, un tipo de dispositivo computacional estándar que no cuenta con placas de video de última generación ni capacidad RAM que sea por sobre lo normal. 

| **Componente**               | **Especificación**                  |
| ---------------------------- | ----------------------------------- |
| Equipo                       | ASUS ROG Zephyrus G14 GA401IV       |
| Sistema operativo            | Microsoft Windows 11 Home, 64 bits  |
| Procesador                   | AMD Ryzen 9 4900HS                  |
| Núcleos / hilos              | 8 núcleos / 16 procesadores lógicos |
| Frecuencia reportada         | 3,0 GHz                             |
| Memoria RAM                  | 16 GB DDR4 a 3200 MHz               |
| GPU dedicada                 | NVIDIA GeForce RTX 2060 Max-Q       |
| GPU integrada                | AMD Radeon Graphics                 |
| Almacenamiento               | SSD Intel NVMe de 1 TB              |
| Capacidad efectiva del disco | 953,86 GB                           |
| Resolución                   | 1920 × 1080                         |

*\[Tabla 2.2 — Información sobre el hardware de ejecución.\]*

<h2 id="cap2-2-7">2.7 Adquisición y preprocesamiento de imágenes</h2>

<h3 id="cap2-2-7-1">2.7.1 Estrategias de captura</h3>

Con el fin de garantizar accesibilidad al momento de reproducir el pipeline se propone el uso de dos dispositivos, que si bien han sido validados como hardware de captura válido para estos experimentos por publicaciones, no dejan de ser dispositivos de uso cotidiano. Por un lado se encuentra el drone DJI Neo 2, que es el drone más portable y económico de la empresa DJI que lidera el mercado de drones profesionales, y la cámara Insta360, un dispositivo fotográfico frecuentemente utilizado para tomas de acción y registros turísticos. 

Esta elección se fundamenta en una estrategia de accesibilidad: se trata de equipos de consumo masivo, accesibles para cualquier persona interesada en el registro fotográfico, y no de equipamiento profesional especializado. A pesar de su carácter doméstico, estos dispositivos son muy versátiles: el DJI Neo 2 permite cobertura aérea, mientras que la Insta360 complementa el dataset con registros de detalle a nivel peatonal y de media altura.

| **Variable**               | **Especificación utilizada**     |
| -------------------------- | -------------------------------- |
| **Modelo**                 | DJI Neo 2                        |
| **Sensor**                 | CMOS de 1/2″                     |
| **Resolución fotográfica** | 12 MP, 4000 × 3000 px            |
| **Formato de imagen**      | JPEG                             |
| **Lente**                  | 16,5 mm equivalentes, f/2.2      |
| **Campo de visión**        | 119,8°                           |
| **Enfoque**                | Fijo, desde 0,7 m hasta infinito |
| **Resolución de video**    | 4K, 3840 × 2160 px               |
| **Frecuencia de captura**  | Hasta 60 fps en 4K               |
| **Estabilización**         | Gimbal biaxial y RockSteady      |
| **Posicionamiento**        | GPS, Galileo y BeiDou            |
| **Autonomía máxima**       | Aproximadamente 19 minutos       |
| **Almacenamiento**         | 49 GB internos                   |

*\[Tabla 2.3 — Información técnica sobre el Drone utilizado para las capturas: DJI Neo 2\]*

| ***Variable para reconstrucción 3D***           | ***Comportamiento de la Insta360 X5***                                                          |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| ***Cobertura espacial***                        | *Muy alta: registra simultáneamente todo el entorno alrededor de la cámara*                     |
| ***Cantidad de imágenes obtenibles***           | *Alta: permite extraer múltiples vistas desde un único recorrido*                               |
| ***Resolución disponible***                     | *Alta en términos globales, con video 360° de hasta 8K*                                         |
| ***Resolución efectiva por dirección***         | *Media: los 8K se distribuyen sobre toda la esfera y no sobre una única vista frontal*          |
| ***Continuidad entre capturas***                | *Muy alta: reduce sectores sin registrar durante el recorrido*                                  |
| ***Estabilidad del video***                     | *Alta gracias a la estabilización y al giroscopio*                                              |
| ***Control de exposición***                     | *Alto: permite fijar ISO, balance de blancos y compensación de exposición*                      |
| ***Compatibilidad directa con COLMAP***         | *Media: requiere exportar el video y convertir la proyección esférica en imágenes perspectivas* |
| ***Adecuación para SfM***                       | *Media: útil para cobertura, pero exige corregir la proyección y controlar las distorsiones*    |
| ***Adecuación para NeRF y 3DGS***               | *Alta, especialmente para recorridos continuos y captura inmersiva*                             |
| ***Precisión métrica***                         | *Media o baja si se utiliza sola; requiere escala o puntos de control para mediciones fiables*  |
| ***Captura de fachadas y espacios interiores*** | *Alta*                                                                                          |
| ***Captura de cubiertas***                      | *Limitada desde el suelo; se complementa con imágenes de dron*                                  |
| ***Aplicación principal en el pipeline***       | *Captura continua a nivel peatonal, interiores, fachadas y entorno inmediato*                   |

*\[Tabla 2.4 — Información técnica sobre la cámara Insta360.\]*

<h3 id="cap2-2-7-2">2.7.2 Preprocesamiento y curación del dataset con ComfyUI</h3>

La mayoría de los estudios sobre el uso de modelos tridimensionales generados mediante las técnicas analizadas tiende a subestimar la relevancia de la limpieza y el preprocesamiento del dataset. La publicación *A Large-Scale Dataset and Benchmark for Distractor-Free Novel View Synthesis* publicada durante 2026 (Lu et al., 2026) confirma que hay una deuda en torno a los procesos de investigación vinculados a la generación de archivos de tres dimensiones:

1) Casi ningún investigador habla activamente de la importancia de manipular y mejorar el dataset obtenido y la mayoría de los autores analizan resultados directamente de las capturas, trabajando sobre un dataset virgen.

2) Los autores introducen el concepto de lo que ellos llaman distractores, y plantean que pueden ser vehículos, personas, efectos de desenfoque producto del movimiento de cámara y todo tipo de elementos que puedan generar ruido al momento de realizar el procesamiento de las imágenes.

Considerando que es un terreno poco explorado y que los distractores pueden llegar a ser muy frecuentes en el tipo de capturas que haría cualquier tipo de usuario al momento de capturar un edificio (es relevante ser conscientes que cualquier edificio está inmerso en un contexto urbano y por ende no está exento de contener distractores próximos que pueden atentar contra los resultados esperados), propongo un pipeline de limpieza de datos que tiene como objetivo identificar aquellos distractores que pueden llegar a impactar en la captura del edificio y extraerlos de las imágenes para generar un dataset “limpio”, donde la obra arquitectónica sea central.

El pipeline que va a implementarse incluye los siguientes pasos:

1) Identificación y remoción de personas

2) Identificación y remoción de aves o animales

3) Identificación y remoción de vehículos

Mientras un pipeline definido va a estar removiendo distractores de las escenas para validar su impacto en los resultados, se propone adicionalmente un segundo pipeline más invasivo que pueda medir el impacto de la remoción del contexto para comprender cómo este modifica los resultados.

1. Generación de máscaras con la identificación del edificio

2. Subida a Nerfstudio del dataset original y el dataset de máscaras configurando que transforms.json apunte hacia el resultado del masking en el procesamiento. 

La elección de ComfyUI como software para el preprocesamiento del dataset está vinculada al hecho de que se trata de una herramienta opensource, que puede correrse de forma local y que la creación de workflows permite utilizar nodos que ejecuten modelos locales y gratuitos. 

El objetivo de este ejercicio es comparar los resultados obtenidos de este dataset procesado con un dataset puro y ver el impacto que este preprocesamiento puede tener en las tres técnicas que utilicemos. En el segundo experimento vamos a estar validando la incidencia de imágenes que contengan de forma exclusiva el edificio a reconstruir, extrayendo no solo distractores sino también fondos y vegetaciones próximas que puedan impactar de forma negativa en los resultados. Esta prueba busca también entender el impacto del contexto en los procesamientos. 

<h2 id="cap2-2-8">2.8 Integración con flujos de trabajo HBIM</h2>

El concepto de HBIM nace en el año 2009 a partir de la publicación del paper Historic building information modelling (Murphy et al., 2009), el término hace referencia a Heritage Building Information Modeling y fue la solución que propusieron los autores de la publicación para resolver una de las problemáticas que más preocupaba en Europa a la hora de proponer tecnologías emergentes que dieran soporte a tareas de conservación de patrimonio histórico. Lo que propone el paper es la creación de una serie de objetos paramétricos, tal como los objetos que ya se venían creando en cualquier software de BIM (Revit siendo el pionero y Archicad siendo otro de los más utilizados) para la creación de edificios nuevos, pero en esta oportunidad que representaran piezas esenciales de obras arquitectónicas de gran valor patrimonial realizadas por arquitectos como Vitruvio y Palladio.

Lo que propone este paper es innovador porque revierte el uso tradicional de la tecnología BIM: del diseño a la construcción. Lo que proponen los autores es la utilización de tecnología de nube de puntos para recrear piezas en BIM que representen partes esenciales de edificios históricos. La nube de puntos que proponen, en este caso, puede ser obtenida a partir de lasers como Lidars, e introduce una metodología que en Europa se volvería pionera en cualquier proceso de preservación: el scan-to-BIM.

Teniendo en cuenta el camino ya trazado en la utilización de HBIM para encarar procesos de mantenimiento y restauración de obras arquitectónicas, lo que propone esta investigación no es reinventar un workflow tan instalado a escala global, sino más bien introducirnos en él en su etapa más temprana: en el proceso de recolección de datos y en el procesamiento de las imágenes para la obtención de la nube de puntos.

Lo importante a tener en cuenta es que los archivos que obtengamos como resultado del procesamiento de las imágenes tiene que ser, de forma obligatoria, compatible con tecnologías BIM, porque en definitiva la mayoría de los estudios y equipos de trabajo destinados a la restauración ya implementan este tipo de software para llevar adelante proyectos de esta naturaleza.

<h2 id="cap2-2-9">2.9 Síntesis y posicionamiento de la investigación</h2>

A modo de síntesis, y habiendo abordado el estado del arte vinculado a los distintos tópicos que contienen esta investigación, podemos afirmar que el objetivo de este proyecto es profundizar el conocimiento existente en la aplicación de fotogrametría, NeRF y 3DGS (Rangelov et al., 2026), al momento de generar réplicas en tres dimensiones de obras arquitectónicas. Asimismo, esta investigación se propone capitalizar el conocimiento adquirido para el diseño de un framework replicable que estandarice una serie de fases secuenciales, con el fin de asegurar la correcta implementación de este pipeline en la constitución de un archivo digital del patrimonio arquitectónico argentino.

Si bien existe una extensa literatura vinculada a la investigación de estas tres tecnologías al momento de reproducir réplicas del mundo real, el alcance al universo de la arquitectura es más limitado, y a la arquitectura argentina en concreto es nulo, por lo tanto esta exploración supone un aporte a considerar.

Por otro lado, la mayoría de los papers y publicaciones que abordan el tema dejan afuera la exploración de la manipulación y la mejora del dataset original, o la implementación de alguna estrategia al momento de la captura de las imágenes que pueda suponer una mejora en los resultados, por lo tanto ambos aspectos pueden ser un gran aporte a la literatura general del tema.

Por último, la propuesta de aplicar estas tres tecnologías en distintas escalas y tipos de obras nacionales ofrece un nuevo parámetro de análisis hasta ahora inexplorado: cómo la incidencia de la complejidad geométrica al momento de obtener resultados fieles.

Con el fin de sintetizar los aportes que haría esta investigación, a continuación se detallan los puntos fuertes de esta investigación con el fin de reconocer el aporte que esta tesis haría al estado del arte actual:

1\. La comparativa sistemática de SfM, NeRF y 3DGS en el contexto de patrimonio arquitectónico argentino, utilizando métricas cuantitativas y cualitativas rigurosas.

2\. La introducción del preprocesamiento como una variable que propone mejorar la calidad de los resultados y optimizar el costo computacional del procesamiento al momento de garantizar fidelidad en las reproducciones.

3\. La propuesta de un pipeline documentado y reproducible, orientado a equipos con recursos limitados y bajo presupuesto, que permita garantizar la reproducción de cualquier obra arquitectónica nacional y alimentar el archivo nacional promovido.

4\. La evaluación de la asertividad tomando como referencia obras de distinta complejidad arquitectónica, mediante un diseño comparativo de tres obras que van de una complejidad geométrica básica a la presencia de ornamentos y piezas arquitectónicas de difícil reproducción. Las obras elegidas son: —equipamiento urbano de geometría simple (Los Paraguas, monumento de 1999–2000 en homenaje a Amancio Williams, Vicente López), arquitectura moderna de complejidad media (el templete del Panteón de la Chacarita, de Ítala Fulvia Villa) y arquitectura ornamental de alta complejidad (Panteón de la Asociación Española de Socorros Mutuos de Alejandro Christophersen de 1896).
