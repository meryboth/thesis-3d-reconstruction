Este capítulo tiene como objetivo no solo documentar el conocimiento que se ganó a partir de la búsqueda de validación de las hipótesis en el capítulo anterior, sino también definir, a partir de estas conclusiones, cuál es el pipeline definitivo de reconstrucción en 3D recomendado para asegurar dos fines:

- La integración con HBIM

- La construcción de un archivo digital web

En la búsqueda por garantizar este doble objetivo se genera una nueva propuesta que tiene el fin de asegurar mayor inteligencia en la interpretación de los datos al momento de realizar la integración: Se trata de la propuesta de un paso adicional dentro del flujo de trabajo que no había sido previsto al momento de diseñar la experimentación. La oportunidad de sumar una herramienta propia de segmentación dentro del pipeline que garantice una lectura más clara de la arquitectura que brinda la nube de puntos densa y permita introducirnos en un flujo de reconstrucción con BIM de forma más rápida y asertiva. 

Lo que vamos a repasar durante este capítulo es la evidencia empírica que ganamos para fundamentar esta recomendación y vamos a cruzar esta información con material académico que nos permita validar o contradecir algunas de las premisas que afirmamos en el capítulo previo. Podría afirmarse que este capítulo es una de las piezas claves de esta investigación porque pretende dar respuesta a la principal pregunta que plantea esta tesis: ¿Puede una técnica de reconstrucción de computer vision agilizar un trabajo de digitalización de obras construidas y colaborar en la construcción de un archivo digital? 

<h2 id="cap6-6-1">6.1 Criterios de selección de técnica según el objeto patrimonial</h2>

El hallazgo central del Capítulo 5 es que **no existe una técnica óptima en términos absolutos** (confirmando H1), pero identificamos potencialidad y desventajas en cada una de ellas para entender cómo estas técnicas pueden ser más o menos óptimas para nuestro objetivo. Esta evidencia está plasmada en la Tabla 6.1. De las tres técnicas evaluadas, solo dos —SfM y 3DGS— entran en los pipelines definitivos de este capítulo; Nerfacto queda explícitamente excluida, por las razones que documentamos. 

| Técnica                 | Rol en los pipelines definitivos                                                                                                                                                      | Evidencia (Capítulo 5)                                                                                                                                                                                                                                                                                                                                                                                         |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **SfM (Fotogrametría)** | Registro de cámaras y geometría de partida para Splatfacto. Output de nube de puntos para pipeline de segmentación para integración HBIM y mesh texturizada como respaldo documental. | Es la única técnica necesaria para correr otros procesos como 3DGS. Su output de nube de puntos tiene una integración óptima para flujos HBIM. Define geometría explícita a través de su mesh (sección 5.2.3).                                                                                                                                                                                                 |
| **Splatfacto (3DGS)**   | Procesamiento protagonista para el pipeline de construcción de archivo digital web. (sección 6.2.3)                                                                                   | Superó a Nerfacto en PSNR/SSIM en los tres casos de estudio (Tabla 5.7); mejor compatibilidad de publicación web entre las tres técnicas (sección 5.6); archivo liviano (Tabla 5.16)                                                                                                                                                                                                                           |
| **Nerfacto (NeRF)**     | **Excluida de ambos pipelines definitivos**                                                                                                                                           | No ofrece una ventaja decisiva en ningún criterio de uso evaluado en esta tesis: peor que Splatfacto en fidelidad de render en los tres casos (Tabla 5.7); sin ruta de publicación web estándar (sección 5.6); no produce geometría explícita utilizable para BIM (sección 6.3); y su output fue directamente inutilizable en el caso de mayor complejidad geométrica (fallo parcial, secciones 5.4.2 y 5.7) |

*Tabla 6.1 — Rol de cada técnica en los pipelines definitivos propuestos, y evidencia que respalda la exclusión de Nerfacto.*

Que NeRF es la técnica menos compatible con nuestro objetivo es algo que algunos investigadores ya venían relevando en el material que consultamos para entender el estado del arte: Rangelov et al. (2026), en una comparación directa entre NeRF y 3DGS sobre entornos interiores y exteriores, encuentran el mismo patrón —3DGS supera a NeRF en eficiencia computacional y reducción de ruido—. 

Hay excepciones puntuales que descubrieron otros investigaciones, sobre el potencial de NeRF cuando el dataset de entrada es pobre, aparentemente esta técnica tiene mayor poder de reconstrucción con registros escasos. Croce et al. (2024) es uno de los autores que valida esta afirmación demostrando cómo algunos resultados de NeRF superan procesamientos de fotogrametría si el dataset tiene pocas imágenes o estas tienen baja resolución. Como parte de nuestra recomendación del pipeline es la creación de un registro completo que reconstruya de forma completa la obra brindando recorridos en 360 completos en al menos tres niveles de altura, podríamos afirmar que la problemática de un dataset incompleto puede ser descartada dentro del flujo de trabajo que recomendamos. 

Se puede afirmar que la técnica de NeRF tiene mucha potencialidad para la resolución de otros casos de uso, posiblemente vinculados a la reconstrucción de escenarios para eventos cinematográficos o generación de material audiovisual (teniendo en cuenta la potencialidad de la técnica para generar nuevos paths de cámara y renderizar videos nuevos). La siguiente animación es un ejemplo de esto, la prueba que se hizo en este caso fue la construcción de un path de cámaras nuevo utilizando el visor de Nerfstudio y renderizando nuevamente en base a la reconstrucción de NeRF. Si bien la calidad visual del cielo tiene defectos, se logró reconstruir puntos de vista únicos de la escena. Este experimento dio cuenta del potencial de NeRF para generar resultados visuales únicos que pueden ser de utilidad para producciones de imagen y sonido. Si bien el potencial es claro, se trata de un caso de uso que se aleja bastante del objetivo de nuestra investigación. 

![Render de Nerfacto sobre Los Paraguas con un recorrido de cámara personalizado, distinto al del video de captura original](/content/assets/cap6-paraguas-nerf-custompath.gif)

*Figura 6.1 — Los Paraguas, Nerfacto: recorrido de cámara nuevo, generado con el visor de Nerfstudio, no presente en el video de captura original. Fuente: `nerf-custompath.mp4`.*

Un aspecto importante para destacar de la Tabla 6.1 es la incidencia de un buen registro de imágenes. El éxito tanto de SfM como de 3DGS depende de la calidad del registro y qué tan completo es el recorrido que plantea el dataset. El pipeline que proponemos incorpora esta aclaración para garantizar el éxito del flujo de trabajo (sección 6.2.1). 

<h2 id="cap6-6-2">6.2 Pipeline definitivo: de la captura a BIM y al archivo digital web</h2>

A continuación vamos a especificar las características del pipeline recomendado para llevar de punta a punta un proceso de reconstrucción 3D que permita integración con BIM y subida a un archivo digital. 

El pipeline parte de la captura, donde se recomienda un único dispositivo (ya sea DJI Neo 2, o Insta360, priorizando el primero si la obra a capturar tiene altura y hay que registrar cubiertas). El proceso de captura incluye una recomendación importante: cuanto más completo sea el dataset y el recorrido que se plantee en el video mejor va a ser la reconstrucción y la interpretación de la geometría en el procesamiento. Luego de la captura se genera el proceso de SfM donde recomendamos en concreto dos herramientas: COLMAP a través de Nerfstudio o RealityScan. La primera herramienta es idónea si el usuario busca realizar los entrenamientos con un único software, y la ventaja principal de RealityScan es que, si bien es una herramienta con limitaciones en la configuración de la corrida de SfM, su tiempo de procesamiento es mucho más rápido y sus resultados son óptimos. Como resultado de este proceso el pipeline genera dos componentes: una nube de puntos densa que representa la geometría de la escena y un archivo en formato malla texturizada que contiene la geometría sólida de la escena. En este punto es donde en el pipeline se genera una bifurcación que habilita dos escenarios:

a) Bifurcación 1: Integración con BIM a partir de una segmentación de la nube de puntos densa

b) Bifurcación 2: Generación de un .splat utilizando Gaussian Splatting para la subida de la escena digital a la web del archivo. 

En la primera bifurcación se propone un sub pipeline donde cobra protagonismo un paso adicional propuesto por este proyecto de investigación: la segmentación a partir de un algoritmo que interpreta la geometría de la nube de puntos y permite categorizar y subdividir sus componentes por el objeto arquitectónico: cubierta, mampostería, suelo, etc. Este paso adicional es una propuesta de esta tesis que tiene como objetivo reducir tiempos y optimizar la interpretación del modelo de cara a un proceso de reconstrucción en BIM. La sección 6.2.2 elabora con mayor profundidad esta propuesta. 

La segunda bifurcación tiene como objetivo generar un archivo .splat que va a utilizarse para mostrar la geometría del edificio en navegadores webs. El objetivo de este sub pipeline es aprovechar las bondades de la técnica de Gaussian Splatting para reconstruir con precisión geométrica escenas de gran complejidad, y permitir a los usuarios la descarga del .splat del edificio con el fin de comprender y entender la obra. 

Una de las principales conclusiones de la H1 es entender qué técnica es mejor para la reconstrucción 3D y cuáles pueden aportar dentro de nuestro objeto de estudio, y podemos afirmar que tanto 3DGS como SfM aparecen como etapas complementarias de un mismo flujo de trabajo, algo con lo que algunos autores ya venían explorando como Lyu et al. (2025) que plantea en el texto "3DGSR: Implicit Surface Reconstruction with 3D Gaussian Splatting" la posibilidad de generar un híbrido entre 3DGS y NeRF. 

La Tabla 6.1 permite visualizar de forma gráfica la propuesta y los pasos del pipeline completo de reconstrucción. 

![Diagrama del pipeline definitivo: tronco común de captura y SfM que se bifurca en una rama HBIM (segmentación, control de calidad humano, nube segmentada — implementado; importación a Revit, modelado paramétrico, vínculo documental — conceptual) y una rama de archivo digital web (Splatfacto, SuperSplat, exportación), que convergen en la descarga dual del archivo digital web](/content/assets/cap6-pipeline-definitivo.png)

*Figura 6.2 — Pipeline definitivo: tronco común, rama HBIM y rama archivo digital web. Fuente: [`build_pipeline_diagram.py`](https://thesis-3d-reconstruction.vercel.app/?script=build_pipeline_diagram.py#scripts).*

<h3 id="cap6-6-2-1">6.2.1 Comienzo del pipeline con SfM y aprendizajes</h3>

Esta sección propone profundizar en aquellos aspectos aprendidos durante los experimentos que proponen validar las distintas hipótesis, y comprender cuánto de aquello sirvió para establecer hoy por hoy un criterio en común que nos permita definir cuál es el flujo de trabajo que se recomienda. 

La captura con un único dispositivo es uno de los aspectos más sólidos que logramos validar durante el Capítulo 5. Se trata de uno de los hallazgos más importantes y sólidos de esta tesis y pueden consultarse en las secciones 5.5.2–5.5.6. Los pipelines definitivos de esta tesis, en consecuencia, **no combinan dispositivos de captura** dentro de un mismo dataset; DJI Neo 2 e Insta360 X5 son alternativas válidas usadas en solitario (Capítulo 3, secciones 3.6.1 y 3.6.3), no complementos entre sí.

Otro aspecto importante que validamos tiene que ver con la posibilidad de someter al dataset a un preprocesamiento de imágenes. Los pipelines de limpieza que generamos utilizando ComfyUI dieron cuenta de que ambas variantes de investigación (por un lado la eliminación de distracciones y por otro la eliminación del contexto) empeoran notablemente los resultados de la reconstrucción en relación al dataset sin procesar. Esta conclusión fue determinante para definir que **el pipeline final no necesita un paso adicional de procesamiento** sino que el dataset original es suficiente para lograr buenos resultados. Si analizamos en profundidad la evidencia que sobre este tema en materia de investigación parece sostener que otros investigadores han llegado a conclusiones parecidas: Lu et al. (2026) construyeron el benchmark más grande hasta la fecha para reconstrucción "distractor-free" (DF3DV-1K, más de mil escenas) y encontraron que incluso los métodos especializados en este problema —más sofisticados que la combinación de detección e *inpainting* usada en esta tesis— logran solo mejoras modestas (+0,96 dB PSNR) sobre un dataset curado específicamente para evaluarlos. 

Un hallazgo de esta investigación **en relación al procesamiento de SfM es la importancia de la verificación binaria**. Se recomienda sumar un paso estándar de verificación binaria al momento de validar la tasa de registro reportada por el wrapper de conversión (que en Nerfstudio suele ser ns-process-data). En nuestro caso exploramos tanto el uso de RealityScan como el de Nerfstudio para la generación de COLMAP, ambas herramientas nos permitieron generar procesos de SfM exitosos, en algunos casos, se recomienda probar ambas y elegir el mejor resultado para avanzar con el pipeline (Capítulo 4, sección 4.4.3). El registro binario recomendado como paso adicional permite identificar si el registro reportado es bajo y si hay componentes desconectados en la reconstrucción (un dataset híbrido puede generar componentes dispersos en COLMAP, incluso cuando el proceso reporta un resultado exitoso). 

<h3 id="cap6-6-2-2">6.2.2 Integración con HBIM</h3>

Para garantizar la integración con sistemas BIM el pipeline propone utilizar la nube de puntos densa como referencia de la geometría general del edificio, y utilizar la malla texturizada como una pieza adicional que simplemente permite constatar como resultado documental. Teniendo en cuenta la parametrización de componentes que caracteriza a la metodología BIM **se propone una segmentación de la nube de puntos** con el fin de mejorar la interpretación general del modelo y brindarle a programas como Revit o Archicad un archivo de nube integrado que ya cuente con el desglose y la identificación de sus componentes principales a nivel arquitectónico. La segmentación propuesta abarca componentes como cubierta, columnas, paredes o barandas, y piso. Con el fin de realizar esta segmentación se utilizó el siguiente [segmentation-multi-site.py](https://thesis-3d-reconstruction.vercel.app/?script=poc_segmentation_multi_site.py#scripts).

Además de la segmentación se propone el uso de un editor online que le permita a los usuarios manipular la nube de puntos generada y poder eliminar puntos del entorno si lo consideran necesario. Este mismo visor permite la posibilidad de exportar en formato .ply la nube segmentada y editada. Tanto este archivo .ply como el .splat que se genere con el procesamiento de Splatfacto van a ser los dos archivos que van a acompañar la publicación de las obras en el archivo digital. 

Hay una parte del flujo de HBIM que queda por fuera del alcance de esta tesis y tiene que ver con la integración de este archivo .ply dentro de un entorno de trabajo (como por ejemplo en Revit), y cómo la importación de este archivo como referencia de scan-to-BIM puede convertirse en parte del proceso de modelado y parametrización del edificio. Este proyecto de investigación propone de forma conceptual esta integración y disponibiliza los archivos segmentados y editados, pero no implementa la solución ya que es parte de un flujo de trabajo que escapa del fin de esta tesis. El pipeline propone documentar también y conservar la malla texturizada producto de SfM para acompañar cualquier referencia adicional del modelo que un proceso de BIM necesite con el fin de entender la complejidad de la obra. 

<h3 id="cap6-6-2-3">6.2.3 Rama hacia el archivo digital web</h3>

La otra rama del pipeline propone utilizar entrenamiento de Gaussian Splatting para generar un archivo de gaussianas que permita representar la escena para visualizarse en cualquier navegador web utilizando Play Canvas como dependencia para el visualizador. Una vez obtenido el archivo en formato .ply/.splat se invita a la utilización de SuperSplat para la edición manual del mismo, esta herramienta open source permite editar gaussianas de escenas de gran complejidad y borrar primitivas con el fin de limpiar la escena y hacer foco en la obra de arquitectura. La publicación en el archivo digital propone publicar tanto el archivo segmentado para HBIM como el archivo .splat con la escena. En el siguiente enlace se puede visualizar una muestra del archivo digital propuesto: [Archivo digital](https://thesis-3d-reconstruction.vercel.app/#archivo-digital). 

<h2 id="cap6-6-3">6.3 Detalle de implementación: segmentación semántica de la nube de puntos</h2>

Como mencionamos con anterioridad, una de las propuestas de esta tesis es sumar una capa de segmentación al resultado de SfM para poder enriquecer el proceso de BIM. Esta segmentación semántica contó con dos exploraciones: por un lado la segmentación con un script y por otro la exploración de una capa adicional de inteligencia utilizando un VLM como modelo interpretativo de la geometría. Durante esta sección se desarrolla en profundidad los resultados de las dos exploraciones. 

Ese paso de conversión no es del todo nuevo en la literatura: Lyu et al. (2025) propone implementar una capa división semántica de gaussianas utilizando distancia con signo (SDF) dentro de las propias gaussianas para extraer superficies explícitas de un modelo 3DGS entrenado. Lo interesante de esta propuesta es que, si bien es una línea de investigación activa y no un terreno sobre el que haya certezas, la evolución en modos de segmentación de escenas gaussianas puede derivar en la construcción de una ruta directa de Splatfacto a BIM en el futuro.

<h3 id="cap6-6-3-2">6.3.2 Implementación: segmentación semántica de la nube de puntos</h3>

Con el fin de profundizar acerca de la propuesta de segmentación para la nube de puntos densa de SfM es importante entender el estado del arte que nos llevó a plantear la integración con HBIM y el proceso de BIM como un flujo de trabajo posible de mejorar: recorrer la nube completa e identificar a mano qué región corresponde a cada elemento constructivo (cubierta, columna, muro, piso) antes de empezar a levantar geometría paramétrica es un proceso tedioso y artesanal en su ejecución. Este cuello de botella está documentado en la literatura de *scan-to-BIM* para patrimonio —Romero-Jarén y Arranz (2021) lo describen como el paso "muy costoso en tiempo y enteramente delegado al trabajo manual de expertos, lejos de estar automatizado". Este descubrimiento motivó una prueba de concepto adicional dentro de esta tesis: un clasificador geométrico que segmenta automáticamente la nube densa de SfM en las cuatro clases relevantes para BIM antes de exportarla como referencia.

El script [`poc_segmentation_multi_site.py`](https://thesis-3d-reconstruction.vercel.app/?script=poc_segmentation_multi_site.py#scripts) implementa esta clasificación sin redes neuronales ni datos de entrenamiento, apoyándose únicamente en propiedades geométricas locales de la nube:

1. **Nivelado**: ajuste del plano de piso por RANSAC y rotación de la nube para que quede horizontal. Ni RealityScan ni COLMAP de Nerfstudio garantizan que la nube de puntos esté correctamente posicionada sobre el eje Z con el piso en el nivel inferior y es por eso que el primer paso es la nivelación y la correspondencia de la volumetría en relación a los tres ejes. 
2. **Verticalidad**: estimación de normales para distinguir superficies horizontales (techo/piso) de superficies verticales (muro/columna). 
3. **Bandas de altura**: detección de picos de densidad en el histograma de alturas para ubicar la banda de techo y la banda de piso de cada caso, sin asumir una altura fija.
4. **Columna vs. elemento no estructural**: agrupamiento de los puntos verticales en celdas de planta; una celda se clasifica como columna estructural si alcanza una fracción alta de la altura total techo-piso, y como baranda/pared no estructural si se corta antes. Este paso permite identificar con claridad muros de barandas y columnas de otro tipo de planos de geometría no estructural. 

La Tabla 6.2 resume el resultado sobre los tres casos de estudio y representa los resultados de la segmentación y cómo se generaron distintos grupos de categorías alineadas con los parámetros BIM. Por otro lado las Figuras 6.3 a 6.5 muestran la clasificación resultante en el [visor web de segmentación](https://thesis-3d-reconstruction.vercel.app/segmentador). 

| Caso de estudio             | Puntos totales | Cubierta | Columna | Baranda/pared no estructural | Piso/base |
| --------------------------- | -------------- | -------- | ------- | ---------------------------- | --------- |
| Templete Central            | 589.605        | 150.000  | 19.094  | 33.651                       | 386.860   |
| Los Paraguas                | 502.817        | 196.453  | 127.293 | 6.044                        | 173.027   |
| Panteón Asociación Española | 356.234        | 39.346   | 48.555  | 96.249                       | 172.084   |

*Tabla 6.2 — Conteo de puntos por clase resultante de la segmentación automática, tres casos de estudio.*

![Templete Central segmentado en el visor web: techo (rojo), columnas (verde), baranda no estructural (amarillo) y piso (azul)](/content/assets/cap6-segmentacion-templete.png)

*Figura 6.3 — Templete Central: las cuatro clases mapean directamente a categorías de Revit (Roofs, Structural Columns, Railings, Floors).*

![Los Paraguas segmentado: ambas cubiertas tipo hongo, vástago central y piso correctamente diferenciados](/content/assets/cap6-segmentacion-paraguas.png)

*Figura 6.4 — Los Paraguas: la doble curvatura de las cubiertas se resuelve correctamente pese a no ser una geometría plana.*

![Panteón Asociación Española segmentado, con la arboleda circundante excluida de la clasificación](/content/assets/cap6-segmentacion-panteon.png)

*Figura 6.5 — Panteón Asociación Española: el filtrado por color (índice ExG) excluye la vegetación circundante antes de clasificar, evitando que contamine las clases estructurales.*

**Visor de segmentación y herramientas de edición** 

Lo que se puede identificar a partir de la Figura 6.5 demuestra que, si el edificio tiene un contexto cercano de vegetación, estos puntos son interpretados dentro de la segmentación como partes de la arquitectura. Queda en evidencia la necesidad de incluir un modo de edición manual para poder continuar optimizando la nube de puntos, con ese fin se incluye en el visor la posibilidad de eliminar puntos y guardar el modelo (Figura 6.6). Esta solución está fundada por la literatura: Croce et al. (2023) y Pan et al. (2024) framean sus propuestas como *"semi-automáticas"* precisamente porque ningún clasificador —ni el geométrico simple de esta tesis, ni los basados en aprendizaje profundo— elimina la necesidad de una revisión humana antes de que el resultado se use como base de un modelo BIM.

![Modo de selección manual activo sobre Templete Central, con un rectángulo de selección arrastrado sobre parte de la cubierta](/content/assets/cap6-segmentacion-edicion-manual.png)

*Figura 6.6 — Editor manual del visor: control de calidad humano sobre la clasificación automática antes de exportar por clase.*

<h3 id="cap6-6-3-3">6.3.3 Exploración: segmentación asistida por un modelo de visión (VLM)</h3>

Con el fin de continuar explorando métodos para mejorar la segmentación se realizó un experimento utilizando modelos de visión (VLM, *vision-language model*). La conclusión de este experimento no terminó superando de forma exitosa el algoritmo que planteamos como solución de segmentación, principalmente porque los modelos de visión utilizados confunden con regularidad columnas estructurales con barandas y tienden a agruparlas dentro de la misma familia. Algo que el algoritmo de segmentación resuelve de forma simple: con un umbral de altura, los modelos de visión no pudieron replicar por su interpretación semántica de la geometría. 

Se probaron dos modelos livianos, elegidos por poder correr en el mismo hardware consumer-grade del resto del pipeline: Moondream2 (1.6B parámetros), corrido sobre los tres casos de estudio, y Qwen2-VL-2B-Instruct (2B), corrido sobre el caso de referencia como segundo punto de comparación. La Tabla 6.3 muestra cómo todos los modelos fallaron en la interpretación de baranda, o en el caso de Qwen2-VL-2B-Instruct con columna, sin capacidad para poder segmentar estas dos familias. 

| Modelo               | Caso de estudio             | Fragmentos evaluados            | Acierto         | Sesgo observado    |
| -------------------- | --------------------------- | ------------------------------- | --------------- | ------------------ |
| Moondream2           | Templete Central            | 15 (8 columna, 7 baranda)       | 7/15 (47%)      | 100% "baranda"     |
| Moondream2           | Panteón Asociación Española | 19 (9 columna, 10 baranda)      | 10/19 (53%)     | 100% "baranda"     |
| Moondream2           | Los Paraguas                | 7 (2 columna, 5 baranda)        | 5/7 (71%)       | 100% "baranda"     |
| Moondream2           | **Total, tres sitios**      | **41 (19 columna, 22 baranda)** | **22/41 (54%)** | **100% "baranda"** |
| Qwen2-VL-2B-Instruct | Templete Central            | 15 (8 columna, 7 baranda)       | 8/15 (53%)      | 100% "columna"     |

*Tabla 6.3 — Acierto de dos modelos de visión livianos frente a la etiqueta del clasificador geométrico, sobre los fragmentos de columna/baranda de los tres casos de estudio (Moondream2) y del caso de referencia (Qwen2-VL-2B-Instruct). Fuente: [`poc_segmentation_vlm.py`](https://thesis-3d-reconstruction.vercel.app/?script=poc_segmentation_vlm.py#scripts), [`qwen_batch_test.py`](https://thesis-3d-reconstruction.vercel.app/?script=qwen_batch_test.py#scripts).*

![Fragmento de columna real (izquierda, proporciones reales) y en contexto dentro del Templete Central (derecha, en rojo), que Moondream2 clasificó incorrectamente como baranda](/content/assets/cap6-poc-vlm-frag-columna.png)

*Figura 6.7 — Ejemplo de clasificación fallida: fragmento de 2,23 m de altura, geométricamente una columna, visualmente inequívoco en el panel izquierdo — el modelo respondió "baranda" de todas formas. Fuente: [`poc_segmentation_vlm.py`](https://thesis-3d-reconstruction.vercel.app/?script=poc_segmentation_vlm.py#scripts).*

Si bien podemos confirmar que el pipeline de ComfyUI con VLM funciona de forma correcta, la segmentación y sus resultados en la clasificación fueron negativos: ni Moondream2 ni Qwen2-VL-2B-Instruct superaron al umbral geométrico simple en esta tarea puntual. Se llega a la conclusión de que la idea de utilizar VLMs para la segmentación es buena y puede llegar a funcionar para el objetivo de esta investigación, pero los modelos utilizados en las pruebas eran livianos y fueron entrenados mayormente con fotografías, por lo tanto no tienen capacidad para generalizar bien imágenes que no vieron durante su entrenamiento. Por lo tanto esta oportunidad de incorporar VLMs a la segmentación se abre como una futura línea de trabajo, incorporando las siguientes pruebas:

1. Modelos más grandes

2. Fine-tuning sobre ejemplos de nube de puntos arquitectónicas



<h2 id="cap6-6-4">6.4 Lineamientos para el archivo digital de patrimonio arquitectónico web</h2>

A partir de la evidencia que se recolecta en función de validar H5 se tomaron las siguientes decisiones, fundamentadas por los lineamientos que proponen las técnicas elegidas en el pipeline:

- **3DGS (Splatfacto) como formato principal de exploración interactiva**, por su combinación de peso liviano (Tabla 5.16), buen desempeño de calidad visual (Tabla 5.7) y compatibilidad directa con visores web (sección 5.6).
- **La malla SfM (.glTF) como información adicional**, útil para mediciones aproximadas y para usuarios que requieran un modelo poligonal (por ejemplo, integración con visores BIM ligeros). 
- **Descarga dual: el .splat limpio de 3DGS y el .ply segmentado por clase**, uno por cada rama del pipeline (secciones 6.2.2 y 6.2.3) — el archivo digital propone descarga tanto del escenario en .splat como del archivo segmentado .ply para importación en BIM.
- **Metadatos de trazabilidad por modelo**: Cada archivo en el registro data la fecha de relevamiento con el fin de dar trazabilidad a la obra y entender su estadio en el tiempo. 

<h2 id="cap6-6-5">6.5 Recomendaciones de infraestructura</h2>

Si bien el hardware utilizado (Capítulo 4, Tabla 4.2) resultó exitoso para cumplir con éxito los casos de estudio de esta tesis y reconstruir cada edificio a partir de los tres métodos planteados, lo cierto es que en algunos casos el tiempo de ejecución de algunos entrenamientos fue demasiado elevado. Como conclusión podemos decir que a nivel básico un hardware como el utilizado cumple las expectativas, pero ante una posibilidad de definir una infraestructura superior consideramos que es probable que los resultados sean superiores. Para un equipo de gestión patrimonial que busque adoptar este pipeline de forma sostenida, se recomienda una GPU con mayor VRAM: entre 8 a 12 GB o más. Este cambio puede generar mejoras como:

- Entrenamientos más rápidos.

- Posibilidad de procesar datasets en alta resolución y más imágenes con el fin de reconstruir en 3D escenas y edificios más complejos y más grandes. 

- La oportunidad de probar VLMs para segmentación más grandes y por ende más precisos al momento de categorizar con éxito las partes de la obra.

<h2 id="cap6-6-6">6.6 Síntesis del capítulo</h2>

Este capítulo propone formalizar la propuesta de pipeline de reconstrucción sugerido y establece los conceptos y las conclusiones más relevantes de esta investigación: 

1. Un criterio de selección de técnica según el tipo de objeto patrimonial y el uso previsto (Tabla 6.1), directamente respaldado por la evidencia cuantitativa y cualitativa, que deja fuera de los pipelines definitivos a Nerfacto y descarta combinar dispositivos de captura o preprocesar las imágenes.

2. Un pipeline definitivo documentado que funciona como una síntesis de todo lo aprendido durante esta investigación (sección 6.2). 

3. Una prueba de concepto de segmentación semántica de la nube de puntos con control de calidad manual (sección 6.3.2) y una exploración sobre la posible utilización de VLMs para la segmentación, proponiendo un pipeline de integración con BIM más óptimo. 

4. Lineamientos para el archivo digital web, que ya ofrece para descarga tanto el .splat como el .ply segmentado y que documenta una cronología histórica de registros con el fin de obtener trazabilidad.  

El Capítulo 7 retoma algunos de estos puntos para finalizar con futuras líneas de investigación y oportunidades de continuar ampliando lo aprendido. 
