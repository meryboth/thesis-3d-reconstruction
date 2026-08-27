**<span class="smallcaps">CAPÍTULO 3</span>**

**Caso de estudio y estrategia de adquisición de datos**

El presente capítulo describe el caso de estudio seleccionado para los experimentos comparativos de esta tesis, los criterios que justifican su elección, el equipamiento y protocolo de captura de imágenes utilizados, y el diseño del pipeline de preprocesamiento de datasets con ComfyUI. La información aquí presentada constituye la base operativa sobre la cual se desarrollan el diseño experimental (Capítulo 4) y el análisis de resultados (Capítulo 5).

<h2 id="cap3-3-1">3.1 Criterios de selección de los casos de estudio</h2>

Como se menciona en el capítulo anterior, una parte esencial de esta investigación tiene como foco descubrir qué tipo de variaciones se generarían en los resultados si lo que analizamos son obras arquitectónicas de impronta o naturaleza distinta. Teniendo en cuenta que cada obra de arquitectura cuenta con una geometría, y que la geometría es, por naturaleza capaz de contener complejidad infinita o de ser abruptamente simple, podemos establecer un parámetro de análisis basado en la siguiente variable:

1.  Complejidad geométrica

Como bien establecimos, también es necesario que las obras que analicemos sean consideradas patrimonio nacional, porque en definitiva esta investigación busca inaugurar un archivo digital que promete ser el primer paso dentro de una campaña nacional de preservación. Por lo tanto, podemos afirmar que otra variable importante es:

2.  Valor patrimonial verificable

El presente estudio limita la investigación a la región del territorio argentino, y como bien sabemos hay una vasta obra arquitectónica en todas las provincias del país. Como personalmente me encuentro ubicada en la provincia de Buenos Aires, la selección de obras que voy a analizar se encuentran limitadas dentro de este sector.

3.  El Área Metropolitana de Buenos Aires y la Ciudad de Buenos Aires

Otra condición importante del análisis tiene que ver con el acceso a las obras, ya que para generar en procesamiento de las imágenes y los registros que inauguren nuestro dataset es necesario tener acceso exterior a los edificios con el fin de poder registrarlos:

4.  Acceso exterior disponible de forma pública

Con estos parámetros quedó definida una selección que compone las siguientes piezas de arquitectura nacional:

1)  Los Paraguas de Amancio Williams en Vicente López, Buenos Aires

2)  El templete central del Sexto Panteón de Chacarita de Ítala Fulvia Villa

3)  Panteón de Asociación Catalana de Socorros Mutuos Montepío de Montserrat en el cementerio de Chacarita del arquitecto Santiago Barris.

En el siguiente capítulo se explica en profundidad por qué se eligieron estas obras y cuál es el valor patrimonial que sustentan.

<h2 id="cap3-3-2">3.2 Caso de estudio 1: Los Paraguas de Amancio Williams</h2>

<h3 id="cap3-3-2-1">3.2.1 Justificación como caso de estudio</h3>

El nombre original de esta obra es El monumento al fin del Milenio, pero popularmente se la conoce como Los Paraguas de Amancio Williams. Se encuentra ubicada a metros del Río de la Plata, sobre el Vial Costero de Vicente López. La obra es de fácil acceso porque forma parte de un paseo público junto al río y se trata incluso de un sector habilitado para el vuelo de drones, por lo tanto la creación del registro fotográfico que permitirá la generación del dataset no propone un desafío que involucra permisos especiales.

![](/content/assets/cap3-image5.jpg)

*\[Imagen 3.1 — Captura aérea propia del monumento ubicado en Vicente López, obtenida mediante un drone DJI Neo 2 con el propósito de generar el dataset respectivo.\]*

La obra, como se puede ver en la imagen 3.1 es una instalación que tiene el fin de funcionar como equipamiento urbano, por lo tanto su geometría es simple y está compuesta por una única pieza, algo que podría facilitar el registro y la obtención de una volumetría tridimensional que logre plasmar las piezas con fidelidad. Otra ventaja es que se trata de dos piezas de un único material: hormigón, por lo tanto esto puede resultar de ayuda al momento de que el procesamiento de las imágenes y la comparativa de cada uno de los algoritmos reconozca la geometría. Estas características la convierten en una candidata ideal para evaluar un nivel de complejidad geométrica bajo.

Por otro lado, la ubicación de la obra supone un contexto a cielo abierto y superficie verde que puede resultar ventajosa para probar el pipeline de limpieza del dataset, en especial aquellos nodos que pueden contener limpieza del fondo, las personas y la fauna que pueda rodear la construcción.

En cuanto al valor patrimonial de la pieza, Luis Müller es uno de los historiadores que más escribió sobre la obra de Amancio Williams y uno de los que sostiene el valor cultural e histórico de los proyectos del diseñador del Movimiento Moderno argentino. La geometría y el diseño de Los Paraguas en realidad deviene de una obra previa del arquitecto: el diseño de las bóvedas cáscara propuesta para materializar un proyecto de Hospitales en Corrientes. Müller en el libro *Amancio Williams: la invención como proyecto* publicado en 2025 sitúa el proyecto de los hospitales para Corrientes —antecedente directo— como un caso que condensa el núcleo central de la arquitectura de Williams y lo coloca en diálogo activo con las principales problemáticas de la arquitectura internacional de la segunda posguerra. Según Müller (2025), Amancio Williams fue uno de los grandes representantes de la arquitectura moderna en Argentina, y posiblemente el que logró mayor reconocimiento internacional dentro de su generación, un factor que hace que su obra esté en la mira dentro de los proyectos de preservación tanto a escala municipal como nacional.

<h3 id="cap3-3-2-2">3.2.2 Desafíos de reconstrucción 3D aplicados a la obra</h3>

Con respecto a esta obra particular de Amancio Williams, presento a continuación un breve desglose de las expectativas técnicas vinculadas a cada tecnología seleccionada para el procesamiento y desarrollo de las volumetrías tridimensionales.

Como se menciona de forma previa, uno de los aspectos más importantes de esta obra está vinculado al diseño de doble curvatura de la cubierta. La literatura analizada en resultados de fotogrametría indica que esta técnica tiene un desempeño bajo cuando la textura es regular (como es el caso de Los Paraguas, donde no hay combinación de texturas sino una única lámina plegada de hormigón). Eso se debe a que la metodología de SfM va reconstruyendo la forma geométrica a partir de un matching de features, y si la textura es pareja en toda la superficie la técnica puede tener dificultades para entender de qué se trata de la misma forma geométrica. Esta dificultad no estaría presente en los otros dos métodos: NeRF y 3DGS porque estas dos técnicas no reconstruyen el 3D emparejando puntos discretos entre imágenes por lo tanto espero que puedan interpretar la geometría de la curva con mayor fidelidad.

Lo que considero una ventaja en cuanto a la facilidad del registro puede volverse una desventaja para el tipo de procesamiento utilizando 3DGS. Como mencionaba en el subcapítulo anterior, que la obra esté a cielo abierto puede ser una ventaja para el preprocesamiento del dataset y también para agilizar la captura del registro con el drone. Pero algo que identificó uno de los autores consultados en el capítulo anterior (Rangelov et al., 2026) es que hay superficies reflectantes, como el agua del río, que pueden complejizar mucho un procesamiento con gaussian splatting. Esto se debe al carácter reflector del agua, y también al movimiento de la misma, lo cual genera variaciones constantes que pueden alterar el procesamiento.

<h2 id="cap3-3-3">3.3 Caso de estudio 2: Los templetes del Sexto Panteón de Chacarita de Ítala Fulvia Villa</h2>

<h3 id="cap3-3-3-1">3.3.1 Justificación como caso de estudio</h3>

Esta obra se realizó en el contexto de un proyecto de la Dirección General de Arquitectura y Urbanismo de la Ciudad de Buenos Aires y tuvo a la arquitecta Ítala Fulvia Villa como responsable del proyecto. Hay mucha literatura al respecto que confunde la autoría de esta obra y se la atribuye a Clorindo Testa, el célebre arquitecto argentino que fue aparte del proyecto pero colaboró como pasante del equipo de Ítala. Lea Namer es la investigadora que en el año 2024 publica *Chacarita Moderna: la necrópolis brutalista de Buenos Aires* y tras una exhaustiva investigación define con detalle los roles de ambos arquitectos durante el proyecto. El mismo libro es el que destaca la obra y su carácter patrimonial cuando dice que: “no existe en ningún otro lugar del mundo una arquitectura funeraria comparable a la del Sexto Panteón, lo que la posiciona como la primera y mayor experimentación de arquitectura moderna aplicada al ámbito funerario de su escala.”

Para los intereses de esta investigación se trata de una obra de acceso público porque se encuentra emplazada dentro del Cementerio de Chacarita. Si bien el proyecto es un desarrollo extenso que incluye también los pasadizos subterráneos y una serie de intervenciones urbanas, lo que vamos a tomar como objeto de estudio son los templetes del sexto panteón, que están conformados por una cubierta de carácter brutalista que corona el acceso al sector subterráneo donde se encuentran los nichos.

Al igual que la obra de Los Paraguas, el templete se encuentra liberado en todos sus extremos y emplazado en un contexto natural, que permite el recorrido de la obra en todo su perímetro, algo que facilita mucho el registro en drones y cámaras con recorridos perimetrales.

A nivel complejidad geométrica podemos decir que esta obra es más compleja que los Paraguas, pero a la vez la resolución material fue llevada a cabo con un mismo material en distintos estados y condiciones, como lo es el hormigón. Esto la posiciona como una candidata perfecta para elevar el nivel de complejidad del estudio a nivel geométrico, pero sin sacrificar complejidad que pueda conseguirse por combinación de materiales.

No caben dudas de que la obra de Itala Fulvia Villa es de interés patrimonial, no solo por lo plasmado en el libro de Namer sino también por la realidad que acompaña a la obra: hoy la mayor parte de los recorridos turísticos que se realizan en el interior del cementerio tienen como eje la visita al Panteón y la valoración de la figura de la arquitecta.

![](/content/assets/cap3-image6.jpg)

*\[Imagen 3.2 — Captura aérea propia del Templete Central del Panteón Sexto en el Cementerio de Chacarita, obtenida mediante un drone DJI Neo 2 con el propósito de generar el dataset respectivo.\]*

<h3 id="cap3-3-3-2">3.3.2 Desafíos de reconstrucción 3D aplicados a la obra</h3>

A diferencia del análisis que hicimos con Los Paraguas y las dificultades que podría tener un procesamiento de SfM por sobre una geometría de una misma materialidad, podemos afirmar que en esta obra podría ocurrir el caso opuesto. Si bien los templetes son de hormigón, este tipo de hormigón presenta variaciones en la materialidad que pueden beneficiar el procesamiento de fotogrametría. Esto se puede ver en variaciones de tono y en la utilización del hormigón pero implementando diversas texturas. A su vez una superficie con mayor espectro de color puede beneficiar altamente los procesamientos de NeRF y 3DGS, lo cual hace que las tres tecnologías puedan tener un rendimiento esperado positivo al momento de identificar la geometría general de la obra.

Hay nervaduras que generan un patrón repetitivo y que al sol genera sombras sobre la superficie, esta variación en las sombras, si el registro ocurre durante una franja horaria amplia puede generar dificultades al momento de procesar con SfM. NeRF y 3DGS pueden tener un desafío muy parecido, ya que ambas tecnologías asumen que el momento del registro es un mismo instante. Por lo tanto el desafío general al momento de crear el dataset de esta obra es lograr el registro integral de la obra en el menor tiempo posible, así las variaciones de sol son mínimas.

La cara inferior de la losa, vista desde el pórtico, solo es visible desde ángulos muy oblicuos y con poca luz directa. Es esperable que SfM tenga dificultad para triangular esta zona con precisión, mientras que NeRF y 3DGS podrían interpolar mejor la geometría en esa zona. Para conseguir esto es necesario garantizar una cobertura lo más completa posible de la obra desde todo su perímetro.

<h2 id="cap3-3-4">3.4 Caso de estudio 3: El Panteón de la Asociación Española de Socorros Mutuos</h2>

<h3 id="cap3-3-4-1">3.4.1 Justificación como caso de estudio</h3>

Esta pieza de arquitectura se encuentra en el cementerio de Chacarita y fue diseñada por el arquitecto Alejandro Christophersen en el año 1896. Considerar a esta obra patrimonio en pos de justificar su elección es uno de los ejercicios más sencillos de esta investigación porque fue declarada oficialmente Monumento Histórico Nacional en el año 2010 a partir del [<u>Decreto 525</u>](https://www.argentina.gob.ar/normativa/nacional/norma-166496/texto). El motivo por el cual se le otorgó este título está relacionado con el tipo de arquitectura promovida por asociaciones mutuales de colectividades extranjeras, en su mayoría piezas de gran valor por sus ornamentos y prácticas de materialización inspiradas en los orígenes de sus contratistas.

No existe literatura o publicaciones oficiales que hagan mención a esta obra, pero tanto la declaración de su patrimonio como su valor arquitectónico son validadas por el decreto oficial que la oficializó como pieza patrimonial. Tal vez lo más interesante de incluir esta pieza sea su estado actual y la urgencia por incluirla dentro de algún programa que ponga como prioridad su restauración. Una nota de 2023 la reconoce como una de las obras de arquitectura en mayor estado de abandono dentro del cementerio de Chacarita e incluso manifiesta peligro de derrumbe.

![](/content/assets/cap3-image4.webp)

*\[Imagen 3.4 — Captura aérea propia de El Panteón de la Asociación Española de Socorros Mutuos en el Cementerio de Chacarita, obtenida mediante un drone DJI Neo 2 con el propósito de generar el dataset respectivo.\]*

<h3 id="cap3-3-4-2">3.4.2 Desafíos de reconstrucción 3D aplicados a la obra</h3>

Su emplazamiento la convierte en una obra posible debido a su fácil acceso, el panteón, a diferencia de otras piezas de arquitectura funeraria, no tiene edificios linderos y se posiciona sobre un lote de esquina teniendo libre todo el perímetro para su recorrido en 360 grados. Una de las dificultades de su ubicación puede estar en la presencia cercana de arboledas altas que puedan generar distracciones durante el registro y también la posibilidad de que existan aves o peatones cerca que también imposibiliten la obtención de un dataset limpio.

En cuanto al uso de fotogrametría como técnica de reconstrucción podemos predecir que posiblemente sea la técnica con mayor dificultad para lograr una reproducción fiel de la obra. El principal desafio va a estar en la reproducción de ornamentos y elementos decorativos de la fachada que pueden resultar repetitivos, esto por lo general genera un problema clásico para el emparejamiento de puntos de interés, porque elementos muy similares entre sí generan correspondencias falsas y duplicados. Por otro lado la presencia de texturas y manchas en la superficie, posiblemente por el deterioro, puede llegar a jugar a favor del procesamiento porque le va a permitir identificar diferencias en la materialidad que va a colaborar en reproducir geométricamente la obra.

En cuanto a NeRF es posible que los resultados sean más óptimos, en especial en aquellas superficies donde hay huecos u orificios, ya que este tipo de procesamiento suele identificar con éxito las superficies discontinuas incluso ante falta de datos. También se espera que las superficies que presentan la misma materialidad como la cúpula logren una interpretación correcta de su geometría

El procesamiento con gaussian splatting es posiblemente el que más incognitas represente: como se inicializa a partir de la nube de SfM, es probable que herede los mismos huecos en las zonas de sombra y que la geometría repetitiva de las columnas y la balaustrada genere ruido, algo consistente con lo que ya está documentado en el Capítulo 2 sobre la sensibilidad de este tipo de procesamiento.

Lo interesante de este caso de estudio es descubrir como el deterioro de la pieza pueda empezar a jugar un factor adicional en la reproducción, viendo que tan lejos llegan los algoritmos de reproducción al momento de replicar desgastes de pintura, manchas de humedad o incluso irregularidades o daños en las superficie. Es por eso que este ejemplo se presenta como un nivel de complejidad superior a los anteriores donde las formas eran mas simples y las superficies más regulares.

<h2 id="cap3-3-5">3.5 Equipamiento de captura</h2>

<h3 id="cap3-3-5-1">3.5.1 Cámara Insta360</h3>

Entre los dispositivos de captura propuestos para esta investigación se encuentra la cámara Insta360. La cámara cuenta con un gran angular que hace que el angulo de captura sea amplio y por ende se optimiza mucho el dataset y el procesamiento de las imágenes. Por otro lado también se trata de un dispositivo portable, pequeño y fácil de trasladar, por lo tanto representa un tipo de equipamiento cómodo para realizar los registros. Pero, pese a estas características, la elección de esta cámara estuvo fundamentada por datos concretos que aparecieron durante la investigación del estado del arte: muchos investigadores estaban utilizando la cámara Insta360 para generación de nube de puntos, y en concreto una investigación elaborada por Morena (2022) y titulada *"Application of Action Camera Video for Fast and Low-Cost Photogrammetric Survey of Cultural Heritage."* pretende validar la utilización de esta cámara en procesos de fotogrametría (en el año 2022 aún no había metodologías más recientes como gaussian splatting, por eso la limitación de su alcance), y obtiene conclusiones bastante sorprendentes sobre la capacidad de la cámara y una comparativa con sistemas lásers: Morena validó la nube de puntos generada a partir de video de una Insta360 ONE R contra el modelo de referencia de un escáner láser de precisión (Leica HDS7000, un modelo que tiene un costo promedio de diez mil dólares), encontrando que aproximadamente el 93% de los puntos procesados con se encontraban dentro de un margen de 3 cm respecto al modelo de referencia. Podemos afirmar, a partir de esta investigación, que la utilización de esta cámara es lo más parecido a utilizar un sistema de Lidars con la precisión de lasers para obtener la nube de puntos.

Otro aspecto importante de las conclusiones de esta publicación, es que la autora no tuvo que realizar calibraciones o configuraciones especiales para lograr dichos resultados, simplemente utilizó la cámara en su configuración estándar y realizó recorridos sin siquiera contar con trípodes ni accesorios de captura especiales.

Para los propósitos de reconstrucción 3D a partir de imágenes, se propone utilizar la cámara en modo de captura estándar (no omnidireccional), extrayendo fotogramas individuales del video capturado. El uso del modo de gran angular permite cubrir mayor área de fachada por fotograma, reduciendo la cantidad total de imágenes necesarias y por ende, optimizando el tiempo de procesado de las mismas para obtener resultados relevantes.

<h3 id="cap3-3-5-2">3.5.2 Drone DJI Neo 2</h3>

El Neo 2 es uno de los modelos más recientes de la compañía DJI por lo tanto hay escasa literatura académica que pueda vincular este dispositivo a conclusiones validadas de forma empírica por otros investigadores. El modelo salió al mercado el 13 de Noviembre de 2025, por lo tanto son nueves meses desde el momento en el cual se está escribiendo esta tesis. Sin embargo, hay investigaciones académicas de uno de sus modelos antecesores, el DJI Neo 1 y DJI Mini 4 Pro, y podemos apreciar que hay una adopción ascendente de este tipo de dispositivos al momento de dar soporte a investigaciones académicas.

| **Evidencia**                                      | **Año** | **Dominio**                                                                 |
|----------------------------------------------------|---------|-----------------------------------------------------------------------------|
| DJI Neo 2: lanzamiento oficial                     | 2025    | Captura visual ligera, seguimiento automático y operación recreativa        |
| Vigilancia con DJI Neo                             | 2025    | Vigilancia con computer vision                                              |
| Detección y ranging con DJI Neo                    | 2025    | Detección de UAV y estimación monocular de distancia                        |
| Inspección de pavimentos con DJI Mini 4 Pro        | 2025    | Inspección de infraestructura y procesamiento de imágenes                   |
| Navegación BEV con ortomosaico de DJI Neo          | 2026    | Ortomosaicos, representación BEV y navegación robótica                      |
| Certificación EASA y soporte técnico del DJI Neo 2 | 2026    | Clasificación regulatoria, seguridad operacional y características técnicas |

Podemos afirmar que no se encontró evidencia del uso de DJI Neo 2 en aplicativos e investigaciones vinculadas a la generación de 3D a partir de métodos de computer vision, por lo tanto se trata de una exploración en la cual esta tesis va a ser pionera. Sin embargo lo que se puede visualizar en el diagrama que se encuentra a continuación es una adopción gradual en el ámbito académico. A continuación voy a describir de forma breve lo que aportaron cada uno de estos hitos: el trabajo de Arab et al. demostró la viabilidad para captura aérea aplicada a vigilancia y detección de objetos mediante técnicas de computer vision. Wang et al., a través de ADG-YOLO, aportaron evidencia sobre su estabilidad de vuelo y utilidad en tareas de detección y estimación de distancias; por su parte, Poma et al. Validaron el empleo en procesos automatizados de inspección de infraestructura. En 2026, PathPainter amplió estos antecedentes al utilizar imágenes capturadas con un DJI Neo para generar un ortomosaico georreferenciado destinado a la navegación robótica. Finalmente, la certificación de EASA y la documentación técnica oficial consolidaron la caracterización operativa del DJI Neo 2.

Si bien, como se indica con anterioridad no hay evidencia empírica de que este dispositivo es idóneo para la investigación, hay otras características del modelo que lo convierten en un candidato perfecto para el fin de la captura de imágenes en altura. Se trata de un dispositivo de apenas 151 gramos, que cabe en la palma de la mano y que puede guardarse en cualquier bolsillo de amplia dimensión. Es portable y su autonomía es de 15 minutos, una variable que no complica en absoluto el registro continuo en edificios de las dimensiones propuestas dentro de los casos de uso. Su carga es rápida y se puede operar desde cualquier dispositivo móvil sin contar con controles o accesorios adicionales. Su costo es el más bajo del mercado (entre 500.000 pesos y 600.000 pesos, dependiendo del proveedor), lo cual lo convierte en un dispositivo accesible para aquellos que quieran explorar la implementación de drones para generación de 3D con bajos costos.

![](/content/assets/cap3-image1.png)

<h2 id="cap3-3-6">3.6 Protocolo de captura de imágenes</h2>

<h3 id="cap3-3-6-1">3.6.1 Diseño del recorrido de captura</h3>

El protocolo de captura es lo que va a definir el diseño de la trayectoria de la cámara alrededor del edificio con el fin de obtener como resultado el dataset que permita operar como base del procesamiento de las tres tecnologías mencionadas. Este protocolo por ejemplo incluye una altura definida, un velocidad de desplazamiento particular y también un patrón de registro y recomendaciones vinculadas al momento de la captura del video o la secuencia de imágenes. El fin de estas recomendaciones tiene como objetivo lograr una captura que sea uniforme y completa, de forma tal que los algoritmos de reconstrucción puedan comprender la geometría general y específica de cada una de las partes del edificio.

El primer paso para definir este diseño es consultar el estado del arte vinculado a registros y recorridos recomendados con el fin de obtener un dataset completo y útil para nuestro propósito. Una de las investigaciones más sólidas consultadas para empezar a entender cual es el patrón de registro más recomendado está dada por la investigación de los autores de la publicación: *"Evaluating 3D Reconstruction: A Side-by-Side Comparison of NeRF and Gaussian Splatting." (2026),* allí definen diagramas específicos como propuesta de captura y llegan a la conclusión de que la mejor trayectoria está compuesta por una serie de recorridos en forma de bucle alrededor del edificio cubriendo al menos 3 alturas: media, baja y alta.

Una publicación previa, que data del 2022 titulada *“Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields”* propone que los trayectos dispongan un recorrido de 360 grados alrededor del objetivo de la captura, pero también establece que el ángulo y la altura deben ser fijos. Algo interesante es que la publicación de Rangelov et al. propone lo contrario y asegura que el recorrido con múltiples alturas mejora la fidelidad en especial en construcciones de carácter vertical que pueden llegar a tener ornamentos o geometrías complejas. ![](/content/assets/cap3-image3.jpg)

Teniendo en cuenta que las publicaciones más recientes sostienen que la mejor técnica es la de bucles con distintas alturas, y sólo papers y publicaciones vinculadas a la construcción utilizando NerF sostienen que es importante una única altura durante los recorrido voy a implementar este criterio como el válido y más recomendado. En promedio el despegue del drone debería garantizar un primer recorrido a una altura de entre 1 a 1.5 metros, mientras que el segundo recorrido debería contener la altura media del edificio y el último recorrido debería contener el remate. La existencia de entre dos a tres recorridos va a depender de la altura del edificio: para proyectos de hasta dos plantas con dos recorridos se establece una cobertura suficiente, mientras que para las obras que tengan más de 6 metros de alto se recomienda un tercer recorrido que permita extender la zona de cobertura.

![](/content/assets/cap3-image2.jpg)

<h3 id="cap3-3-6-2">3.6.2 Condiciones de captura</h3>

La bibliografía consultada ya plantea algunos consejos acerca de las condiciones de captura y aquellas variables que pueden incidir en la creación de un dataset óptimo para la reconstrucción en tres dimensiones. El texto "Impact of Data Capture Methods on 3D Reconstruction with Gaussian Splatting." rescata la importancia de mantener condiciones climáticas constantes durante el registro y buscar la menor alteración posible de iluminación en la escena al momento de la captura. Otra variable importante que destaca la publicación es el entorno de la obra: lo registrado tiene que estar inmerso en un entorno de áreas espaciales amplias. Este factor está vinculado a la posibilidad de obtener un registro en todos los ángulos y conseguir cierta separación entre la pieza a registrar y su entorno, cuando más “limpio” sea el vínculo entre la obra y su contexto más posibilidades hay de conseguir mayor información acerca de las texturas y una correcta interpretación de la geometría al momento de procesar los algoritmos de reconstrucción. Gran parte de la literatura que analiza las condiciones de luz sostiene

Hay una investigación en concreto que apunta de lleno a dos temas que se abordan en esta tesis, por un lado las condiciones de luz durante el momento del registro y por otro la reconstrucción orientada a proyectos de preservación, el nombre es: "Evaluating the Impact of Lighting Conditions on Photogrammetric Acquisition of Cultural Heritage.". A diferencia de esta tesis, esta investigación evalúa la técnica de fotogrametría orientada al escaneo de objetos, esculturas y piezas que representen cierto valor histórico. La conclusión de este autor sobre la iluminación y las condiciones de captura aporta un dato interesante acerca del rol del ISO de la cámara: generalmente cuando las condiciones de iluminación son malas en un registro cualquier fotógrafo suele compensar esta falta de luz con un valor de ISO más alto durante el registro para generar una compensación. Lo que indican los autores es que esta compensación deteriora mucho el dataset y genera una reconstrucción pobre cuando la técnica implementada es SfM. Si bien la interpretación de la geometría general continúa siendo constante el mayor diferencial se nota en los puntos de referencia (también llamados tie points) y esto genera un error de reproyección que va deteriorándose de forma constante a medida que el valor de ISO se incrementa.

Otra condición de captura es la dependencia de la luz solar natural. Por lo tanto los registros tienen que hacerse de día para obtener luz natural, priorizando las horas en las cuales la presencia del sol puede ser continua o mostrar poca variación en el efecto que genera dicha presencia en las sombras que proyectan los edificios.

Esta tesis pone el foco en registros de exteriores de edificaciones que puedan considerarse patrimonio nacional, por lo tanto es importante que los responsables de realizar los registros puedan tener acceso completo al edificio en su exterior. Mientras elaboraba una preselección de obras para la investigación consideré la posibilidad de sumar entre los edificios a la Parroquia Nuestra Señora de Fátima, una obra célebre del arquitecto Claudio Caveri que se encuentra ubicada sobre Av. Libertador en Martinez y que forma parte de los edificios que el Municipio de San Isidro protege por su carácter de Patrimonio Nacional. La pieza refleja un tipo de arquitectura nacional llamada “casa blanquismo” del que Caveri fue referente, por lo tanto se trata de una construcción más que valorada dentro del catálogo nacional. El desafío de este edificio estaba dado por su emplazamiento, si bien el frente de la Iglesia es de público acceso porque se encuentra vinculado a un atrio sobre la avenida antes mencionada, la obra no es accesible en uno de sus laterales, porque contiene un patio interno vinculado a un edificio lindero que forma parte de las edificaciones de la congregación, por lo tanto la posibilidad de realizar un registro en todo el perímetro de la obra quedaba fuera de las posibilidades de la investigación. Lo que parecía un bloqueo en realidad descubrió una nueva condición de este proyecto: para registrar el edificio público es necesario tener acceso a todo el perímetro de la construcción para conseguir un dataset que refleje toda la complejidad de la obra.

<h3 id="cap3-3-6-3">3.6.3 Parámetros de captura del video</h3>

La captura de video con el drone DJI Neo 2 tiene dos configuraciones: la opción manual y la opción pro. En la selección manual el dispositivo se ajusta a la luz solar y establece una configuración de ISO, velocidad de obturación y compensación de exposición automática. El usuario puede elegir distintos tipos de resolución, pero para los fines de esta investigación todos los registros con este drone van a guardarse en 4k. Teniendo en cuenta que un alto valor de ISO puede degradar la calidad del dataset para algoritmos de reconstrucción de SfM y que los registros van a realizarse en plena luz del día, se opta por elegir una configuración manual de ISO considerando que la cámara va a seleccionar un ISO bajo gracias a la compensación de la luz solar exterior. Se prioriza una disposición horizontal de la imagen y un registro de 100 frames por segundo, este segundo parámetro está vinculado a la posibilidad de obtener más frames del video y posibilitar una selección y preprocesamiento más enriquecido al momento de trabajar con el material obtenido.

Otro parámetro de configuración personalizado es la cantidad de frames por segundo durante la captura, en este caso se establece 60 frames por segundo, de forma tal que el video obtenido tenga la misma cantidad de fps que el registro en el otro dispositivo. El objetivo de este setup es empatar de la forma más homogénea posible la configuración de ambos dispositivos con el fin de obtener un único dataset que no requieran procesamientos o ajustes adicionales.

| Dispositivo        | DJI Neo 2 |
|--------------------|-----------|
| Tipo de navegación | Manual    |
| Formato de salida  | .mp4      |
| FPS                | 60        |
| Formato            | Apaisado  |
| Relación           | 16:9      |

Para la cámara Insta360 el usuario puede elegir si utilizar la cámara con un gran angular pronunciado o si filmar directamente con los dos lentes obteniendo un resultado de 360 grados. El primer enfoque fue mejor para los registros, ya que la disposición de 360 grados implica un preprocesamiento más intensivo: esto ocurre porque el usuario que captura las imágenes queda capturado dentro de la imagen panorámica que obtiene como resultado. Una aclaración importante es que en Junio de 2026, RealityCapture, uno de los software más utilizados para procesamiento con SfM incluye soporte para imágenes 360, lo que facilita mucho la implementación de un pipeline de reconstrucción 3D utilizando este tipo de imágenes panorámicas que ofrece Insta360. El motivo por el cual esta tesis no incluye esto en su pipeline de investigación es que RealityCapture no ofrece tantas posibilidad de configuración como otros softwares open source que permiten configurar de forma más específica las variables de salida de SfM, como por ejemplo NerfStudio. Por ese motivo este proyecto de investigación no utiliza las imágenes panorámicas de Insta360 y en su lugar utiliza las posibilidades captura de video haciendo uso del gran angular de la cámara. A continuación se especifican los parámetros de salida configurados al momento de realizar capturas con este dispositivo:

- Se elige la relación de 16:9, es decir, una disposición apaisada de las imágenes. Esta selección busca que el resultado obtenido pueda emparejarse mejor con el output de los videos generados por el drone ante la posibilidad de generar un dataset único con ambos registros.

- La resolución obtenida es 4K.

- La captura tiene una configuración de 60 frames por segundo.

Estos parámetros de configuración tienen como finalidad que los registros obtenidos con este dispositivo sean lo más ‘parecidos’ posible a los registros obtenidos con el drone. La principal diferencia entre ambos dispositivos no está en la calidad del registro de salida, sino en el lente de la cámara. Los lentes de la cámara Insta 360 son lo que se conoce como ‘lentes ojo de pez’, que tienen un campo de visión muy amplio, 180 grados en cada uno de los lentes. Por otro lado, la cámara del DJI Neo 2 tiene un lente plano y un campo de visión fijo.

Un factor que se busca validar durante esta investigación tiene que ver con la posibilidad de generar un dataset con distintos registros y distintas cámaras, es por eso que se va a buscar comparar los resultados de un registro compuesto. Para apoyar esta hipótesis se propone como referencia las conclusiones de una de las publicaciones consultadas en la bibliografía: ‘*3D Gaussian Splatting for Modern Architectural Heritage: Integrating UAV-Based Data Acquisition and Advanced Photorealistic 3D Techniques’,* los autores de esta investigación proponen un registro híbrido que incluye imágenes obtenidas con un drone DJI Mini 2 y fotografías DSLR terrestres de alta resolución. Este caso empírico nos permite validar que es posible la combinación de imágenes de distintas fuentes y sobre todo la posibilidad de combinar dispositivos que permitan un registro fiel terrestre y uno aéreo.

<h3 id="cap3-3-6-4">3.6.4 Resumen del dataset obtenido</h3>

> *\[ Completar con: duración total del video capturado, número de fotogramas totales antes del preprocesamiento, tamaño total del material en GB, y cualquier incidencia o condición especial durante la sesión. \]*
>
> *\[ Insertar tabla resumen del dataset: nivel de captura / duración de video / fotogramas totales / cobertura estimada del edificio. \]*

<h2 id="cap3-3-7">3.7 Pipeline de preprocesamiento con ComfyUI</h2>

<h3 id="cap3-3-7-1">3.7.1 Justificación del preprocesamiento</h3>

Uno de los primeros antecedentes en materia de publicaciones que habla de la necesidad de plantear un preprocesamiento de los datos antes de someter al registro a los algoritmos de reconstrucción es la publicación “*An Advanced Pre-Processing Pipeline to Improve Automated Photogrammetric Reconstructions of Architectural Scenes.* Remote Sensing”. El paper es de 2016 y plantea la necesidad de generar un pipeline de procesamiento de cara a una reconstrucción basada en el algoritmo de fotogrametría. Lo valioso de este hallazgo es que los autores basan su investigación en la reconstrucción de escenas arquitectónicas, un punto en común con el foco de esta tesis, y por otro lado lo que identifican los autores es que hay una serie de variables que pueden influir negativamente en el procesamiento y que estan dadas por los siguientes factores: el desenfoque producto del movimiento, el ruido que puede generar en las imágenes los sensores de captura y los artefactos de compresión terminan generando una degradación en el pipeline de fotogrametría que afecta negativamente los resultados. Lo que los autores proponen a modo de solución es un preprocesamiento que incluya los siguientes pasos:

1)  Corrección de color

2)  Reducción de ruido

3)  Transformación a escala de grises

Otro antecedente más reciente, publicado en el año 2022 fue creado por el equipo responsable de la publicación “*Analysing Key Steps of the Photogrammetric Pipeline for Museum Artefacts 3D Digitisation”.* Los investigadores en este caso encaran un proyecto de digitalización de piezas patrimoniales de museos y el algoritmo que utilizan también es SfM. En este caso enfocan las tareas de preprocesamiento en dos variables concretas:

1)  Corrección de desenfoque por profundidad de campo

2)  Enmascaramiento de fondo

Lo que consideran los autores es que estas dos operaciones mejoran mucho el tiempo de procesamiento del algoritmo cuando tiene que reconstruir las piezas, y por otro lado el resultado que obtienen es superior a las pruebas que realizan de forma previa sin preprocesamiento.

Con la llegada de los algoritmos de procesamiento NeRF nació en la literatura de investigación asociada a este método el concepto de ‘distractores’. Este termino ya lo abordamos con anterioridad y hace referencia a aquellos objetos que pueden llegar a distraer al algoritmo de la identificación geométrica de la pieza central: pueden ser autos, aves, personas, bicicletas, etc. La publicación *‘NeRF in the Wild: Neural Radiance Fields for Unconstrained Photo Collections.’* plantea que los distractores generan inconvenientes en los procesamientos con NerF porque van en contra de la naturaleza de la captura con NeRF y 3DGS que es entender a la escena como una situación estática. Ellos proponen en la publicación separar los elementos que son estáticos de los transitorios, con el fin de identificar estos distractores y luego someterlos a algún tipo de preprocesamiento donde se pueda reducir el impacto que tienen en los resultados.

La publicación “*SpotLessSplats: Ignoring Distractors in 3D Gaussian Splatting”* plantea un pipeline que propone reducir el efecto de los distractores en procesamientos de reconstrucción que utilizan gaussian splatting. Lo que propone esta investigación es utilizarlas características semánticas preentrenadas de modelos de difusión para agrupar y enmascarar distractores y de esa forma reducir el impacto que tienen en la reconstrucción.

A modo de sintesis podemos afirmar que se encontró evidencia de que el la generación de un pipeline de preprocesamiento puede mejorar los resultados de cara a la reconstrucción que realizan los tres algoritmos, tanto para mejorar la calidad del dataset generando balance de blancos, mejorando el contraste de las imagenes o corrigiendo el color y el ruido, o realizando procesos mas contundentes como el enmascaramiento de personas, vehiculos o animales que puedan transitar cerca de la obra a registrar.

El motivo por el cual se optó por ComfyUI como herramienta para ejecutar este pipeline tiene que ver con la habilidad de este software para permitir la manipulación de grandes cantidades de imágenes y ofrecer una serie de workflows en nodos donde las responsabilidades y el impacto de cada paso del procesamiento puede ser configurado con precisión. Por otro lado este software es open source y puede correrse con modelos locales, algo alineado con otros aspectos de esta investigación: la priorización de herramientas de uso libre que puedan estar a la mano de personas con el interés de seguir expandiendo el archivo de patrimonio histórico que se propone como iniciativa.

La arquitectura de ComfyUI es a partir de nodos configurables, se pueden generar flujos de trabajo que contengan accionables específicos sobre una imagen o un grupo de ellas y luego guardar los resultados. Lo interesante de este enfoque es que el pipeline utilizado se puede exportar como json y luego cualquier usuario puede replicarlo en segundos importando el código de forma local en su software, por lo tanto sería fácil extrapolar el pipeline y reproducirlo en otras computadoras. Esta facilidad para reproducir el pipeline fortalece el carácter metodológico de esta tesis donde la intención de trazar un camino, un framework, que permita entender el flujo de trabajo más recomendado para realizar reconstrucción arquitectónica.

<h3 id="cap3-3-7-2">3.7.2 Descripción del pipeline implementado</h3>

El pipeline propuesto lo podemos definir en tres etapas:

- Etapa 1: Ajustes visuales y de correcciones de color, lente y balances de imagen

- Etapa 2: Limpieza de distractores y enmascaramiento de fondos

- Etapa 3: Evaluación de resultados y guardado del nuevo dataset.

La Etapa 1 propuesta está vinculada con las conclusiones mencionadas previamente en la publicación “*Analysing Key Steps of the Photogrammetric Pipeline for Museum Artefacts 3D Digitisation”.* La finalidad de esta etapa es cubrir algunos aspectos básicos de la composición y el balance de las imágenes para mejorar su futuro procesamiento con SfM. Esta etapa incluye:

1.  Normalización de color

2.  Balance de blancos

3.  Evaluación de nitidez y ajuste de nitidez

4.  Evaluación de exposición y ajuste de exposición

Tras este primer paso se guarda una segunda versión del dataset que contiene estos ajustes con la finalidad de establecer un backup y poder revertir algún proceso posterior que genera inconsistencia en las imágenes.

El segundo proceso que se lleva adelante en la Etapa 2 es más invasivo a nivel manipulación de las imágenes y tiene como objetivo identificar y eliminar distractores que puedan afectar los resultados en etapas posteriores. El flujo de esta etapa incluye:

5.  Identificación de personas, vehículos y animales

6.  *Masking* de estos distractores y eliminación de los mismos

7.  Identificación y eliminación de fondos

Lo esperado como parte de este procesamiento más robusto es la obtención de un dataset que incluya imágenes en formato .png que tenga como protagonista a la obra de arquitectura y que puedan extraerla de su contexto para su correcto análisis. Lo importante de esta etapa es que puede generar la eliminación de piezas o componentes que en realidad son parte de la obra y por eso es importante contar con un último nivel de análisis que permita identificar si hubo fallas en el preprocesamiento y revertir algunas acciones claves que hayan generado errores.

<h3 id="cap3-3-7-3">3.7.3 Datasets generados para la experimentación</h3>

El pipeline de preprocesamiento genera dos versiones del dataset para cada sesión de captura, que serán utilizadas como variables en el diseño experimental del Capítulo 4:

**Dataset A — Sin preprocesamiento (raw):** fotogramas extraídos del video a cadencia fija, sin ningún filtrado de calidad ni corrección. Este dataset representa la línea base contra la cual se mide el impacto del preprocesamiento (hipótesis H3).

**Dataset B — Con preprocesamiento (curado):** fotogramas que superaron todas las etapas del pipeline de ComfyUI, con enmascaramiento de elementos dinámicos y normalización de color. Este dataset representa la versión optimizada del material de entrada.

> *\[ Completar con la tabla comparativa de los dos datasets: número de fotogramas / tamaño en MB / porcentaje de fotogramas descartados / tiempo de procesamiento del pipeline. \]*

<h2 id="cap3-3-8">3.8 Posibles casos de estudio adicionales</h2>

El diseño de esta investigación contempla la posibilidad de incorporar casos de estudio adicionales a los mencionados con anterioridad con la intención de validar o enriquecer la propuesta de esta tesis. Los casos adicionales podrán foco en algún aspecto de esta investigación como:

1)  La posibilidad de evaluar este pipeline para la reconstrucción de detalles arquitectónicos como ornamentos o fachadas.

2)  La oportunidad de construir datasets a partir de registros audiovisuales obtenidos de material de acceso público.

3)  El testeo de herramientas open source que permitan dar cuenta del estado del arte de la reconstrucción de geometrías a partir del uso de algoritmos de visión por computadora.

Estos casos adicionales, que se escapan del diseño de experimentación de este proyecto, buscan enriquecer el corpus académico y experimental de esta tesis y brindar un marco de conocimiento que pueda dar cuenta de la diversidad de aplicativos y casos de uso que podrían resolverse utilizando algoritmos de reconstrucción de 3d.

<h2 id="cap3-3-9">3.9 Síntesis del capítulo</h2>

Este capítulo ha presentado los distintos casos de estudio que van a abordarse en esta investigación y ha justificado su selección en función de los criterios patrimoniales, geométricos y operativos definidos. Se ha descrito el equipamiento de captura y el protocolo de relevamiento al momento de realizar los registros de las obras. Se ha detallado el pipeline de preprocesamiento implementado en ComfyUI, que constituye la variable experimental para la hipótesis H3, y se han definido los dos datasets —raw y curado— que serán utilizados como inputs en el diseño experimental del Capítulo 4.

*— Continúa en Capítulo 4: Diseño experimental —*

<h2 id="cap3-referencias-del-cap-tulo-3">Referencias del Capítulo 3</h2>

ModernaBuenosAires.org. (s.f.). Testa, Clorindo Manuel José. https://www.modernabuenosaires.org/arquitectos/clorindo-manuel-jose-testa

Rangelov, D., Waanders, S., Waanders, K., Genchev, E., van Keulen, M. y Miltchev, R. (2026). Evaluating 3D Reconstruction: A Side-by-Side Comparison of NeRF and Gaussian Splatting in Indoor and Outdoor Environments. *Engineering, Technology & Applied Science Research, 16*(2), 33736–33745. https://doi.org/10.48084/etasr.16947

> Müller, L. (2025). Amancio Williams: la invención como proyecto. Prólogo de Jorge Francisco Liernur. Bernal: Universidad Nacional de Quilmes; Santa Fe: Universidad Nacional del Litoral. ISBN 978-987-558-996-4.
>
> Namer, L. (2024). *Chacarita Moderna: la necrópolis brutalista de Buenos Aires / The Brutalist Necropolis of Buenos Aires*. Edición bilingüe castellano-inglés, con el apoyo de la Graham Foundation for Advanced Studies in the Fine Arts.
>
> de la Fuente, M. L. (2021/2022). "Peripheral Architectural Hierophanies. Claudio Caveri's Sacred Architecture". En: Bartolomei, C., Ippolito, A. y Vizioli, S. H. T. (eds.), Digital Modernism Heritage Lexicon. Springer International Publishing. https://doi.org/10.1007/978-3-030-76239-1_50
>
> Morena, S. (2022). "Application of Action Camera Video for Fast and Low-Cost Photogrammetric Survey of Cultural Heritage." *International Archives of the Photogrammetry, Remote Sensing and Spatial Information Sciences, XLVIII-2/W1-2022*, 177–184. https://doi.org/10.5194/isprs-archives-XLVIII-2-W1-2022-177-2022
>
> Rangelov, D., Waanders, S., Waanders, K., van Keulen, M., & Miltchev, R. (2026). "Evaluating 3D Reconstruction: A Side-by-Side Comparison of NeRF and Gaussian Splatting." Engineering, Technology & Applied Science Research, 16(2), 33736–33745.
>
> Barron, J. T., Mildenhall, B., Verbin, D., Srinivasan, P. P., & Hedman, P. (2022). "Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields." Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 5470–5479. https://arxiv.org/abs/2111.12077
>
> Gangi, F., Shafqat, M. U., & Guidi, G. (2025). "Evaluating the Impact of Lighting Conditions on Photogrammetric Acquisition of Cultural Heritage." Digital Heritage 2025 (Eurographics Workshop on Graphics and Cultural Heritage), Politecnico di Milano.
>
> Rangelov, D., Waanders, S., Waanders, K., van Keulen, M., & Miltchev, R. (2025). "Impact of Data Capture Methods on 3D Reconstruction with Gaussian Splatting." Journal of Imaging, 11(2), 65.
>
> Yu, Y., Verbree, E., van Oosterom, P., & Pottgiesser, U. (2025). 3D Gaussian Splatting for modern architectural heritage: Integrating UAV-based data acquisition and advanced photorealistic 3D techniques. AGILE: GIScience Series, 6, 51. https://doi.org/10.5194/agile-giss-6-51-2025

Poder Ejecutivo Nacional. (2010). Decreto 525/2010. https://www.argentina.gob.ar/normativa/nacional/norma-166496/texto
