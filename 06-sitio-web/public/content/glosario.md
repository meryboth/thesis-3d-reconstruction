**Patrimonio y gestión**

**Patrimonio arquitectónico nacional:** A los efectos de esta tesis: conjunto de bienes construidos —edificios, conjuntos urbanos, obras de ingeniería y sitios históricos— con valor histórico, cultural, artístico o social reconocido, que representan la identidad de comunidades argentinas a lo largo del tiempo. Definición basada en la Convención de Granada (1985) y la Ley Nacional 12.665 (1940).

**BIM (Building Information Modelling):** Metodología de trabajo colaborativa para la creación y gestión de un proyecto de construcción. Su objetivo es centralizar toda la información del proyecto en un modelo de información digital creado por todos sus agentes.

**HBIM (Heritage Building Information Modelling):** Extensión del paradigma BIM aplicada a edificios históricos, incorporando información geométrica, material, histórica y de estado de conservación en modelos paramétricos interoperables con plataformas como Autodesk Revit.

**Scan-to-BIM:** Flujo de trabajo que convierte nubes de puntos o mallas generadas por escaneado o fotogrametría en modelos paramétricos compatibles con plataformas BIM. Desafío abierto en la automatización del modelado patrimonial.

**TLS (Terrestrial Laser Scanning):** Escaneo láser terrestre. Técnica de relevamiento de alta precisión que genera nubes de puntos densas métricamente verificables. Constituye la referencia de precisión geométrica con la que se comparan las técnicas de reconstrucción basadas en imágenes.

**Técnicas de reconstrucción**

**3D Gaussian Splatting (3DGS):** Técnica de reconstrucción y renderizado 3D introducida por Kerbl et al. (2023) que representa escenas mediante millones de elipsoides gaussianos tridimensionales optimizables, permitiendo renderizado en tiempo real. Técnica de referencia para integración con motores de videojuegos y entornos interactivos.

**3DGSR:** Extensión de 3DGS propuesta por Lyu et al. (2025) que incorpora una función de distancia implícita firmada (SDF) dentro de las gaussianas para habilitar la reconstrucción de superficies métricamente precisas.

**Fotogrametría:** Ciencia y técnica que permite obtener medidas tridimensionales de un objeto o escena a partir del análisis de fotografías. Término introducido por Albrecht Meydenbauer en 1867. En su forma computacional moderna se apoya en los algoritmos SfM y MVS. Técnica de referencia para documentación patrimonial con integración BIM.

**NeRF (Neural Radiance Fields):** Método de representación de escenas 3D como campos de radiancia continuos y volumétricos, optimizados mediante un MLP a partir de imágenes 2D. Introducido por Mildenhall et al. (2020). Técnica de referencia para producción cinemática y síntesis de vistas fotorrealistas desde trayectorias inéditas.

**SfM (Structure from Motion):** Familia de algoritmos de visión computacional que recupera la estructura tridimensional de una escena y las posiciones de las cámaras a partir de imágenes, analizando el movimiento aparente de puntos de interés entre vistas. Formalizado por Ullman (1979).

**Nerfacto:** Implementación de NeRF dentro de Nerfstudio, optimizada para velocidad de entrenamiento mediante hash encoding multiresolución y muestreo por importancia. Una de las dos técnicas comparadas en los tres casos de estudio de esta tesis.

**Splatfacto:** Implementación de 3D Gaussian Splatting dentro de Nerfstudio. La segunda de las dos técnicas comparadas en los tres casos de estudio de esta tesis.

**Pipeline y procesamiento**

**Bundle Adjustment:** Etapa de optimización global del pipeline SfM que minimiza simultáneamente el error de reproyección de todos los puntos 3D sobre todas las imágenes.

**ComfyUI:** Framework modular en nodos para procesamiento de imágenes con IA. Utilizado en esta tesis para el pipeline de preprocesamiento experimental de datasets fotográficos (hipótesis H3).

**Dataset:** Conjunto de imágenes o fotogramas de video utilizados como entrada para los algoritmos de reconstrucción 3D. La calidad, densidad y diversidad angular del dataset son factores determinantes en la calidad del modelo generado.

**Distractores:** Elementos ajenos a la obra arquitectónica capturada —como vehículos, personas o efectos de desenfoque por movimiento— que introducen ruido en el dataset y degradan la calidad de la reconstrucción 3D. Su identificación y remoción es una etapa crítica del preprocesamiento para garantizar un dataset "limpio".

**Densificación adaptativa:** Estrategia empleada en 3DGS durante el entrenamiento para clonar, dividir o eliminar gaussianas según su contribución al modelo.

**Floaters:** Artefactos de reconstrucción consistentes en fragmentos de geometría y color sin correspondencia con la escena real, típicamente desconectados de la estructura principal. Falla característica de NeRF (y en menor medida de 3DGS) ante datasets con registro SfM débil o geometría/ornamentación compleja.

**Inpainting:** Técnica que reconstruye el contenido de una región eliminada de una imagen a partir del contexto circundante. Utilizada en esta tesis como etapa final del pipeline de limpieza de distractores, luego de la detección y el enmascarado (Capítulo 5, sección 5.2.3).

**Keypoints:** Puntos de interés detectados automáticamente en imágenes mediante descriptores como SIFT o SURF, utilizados en el pipeline SfM para establecer correspondencias entre vistas.

**Marching Cubes:** Algoritmo de extracción de superficies isométricas a partir de campos volumétricos. Utilizado en NeRF para convertir el campo de densidad implícito en una malla poligonal exportable.

**Multi-View Stereo (MVS):** Algoritmo que estima la profundidad de cada píxel por correlación fotométrica entre vistas adyacentes, produciendo una nube de puntos densa a partir de las poses de cámara estimadas por SfM.

**Novel View Synthesis:** Síntesis de vistas fotorrealistas desde ángulos no presentes en el conjunto de entrenamiento. Aplicación central de NeRF para producción cinemática, y capacidad relevante de 3DGS para entornos interactivos.

**ParallelDataManager:** Componente de Nerfstudio encargado de cargar y distribuir en paralelo el dataset de imágenes durante el entrenamiento. Responsable de la limitación de memoria detectada en esta tesis al entrenar Nerfacto sobre datasets grandes (1000+ imágenes), que obligó a entrenar sobre un subset reducido en varios de los casos de estudio (ver limitaciones metodológicas, Capítulo 4).

**Pipeline:** Secuencia ordenada de etapas de procesamiento que transforma un conjunto de imágenes de entrada en un modelo 3D de salida.

**RANSAC:** Algoritmo de estimación robusta de parámetros ante la presencia de outliers, utilizado en SfM para estimar poses de cámara.

**Rasterización diferenciable:** Proceso de rasterización implementado de forma diferenciable para permitir la optimización end-to-end de parámetros 3D mediante retropropagación. Base del pipeline de entrenamiento de 3DGS.

**Registro (imágenes registradas):** Proporción de imágenes de un dataset a las que el pipeline de SfM logra asignarles una pose de cámara válida mediante bundle adjustment. Métrica central para evaluar la robustez de un pipeline de SfM ante un dataset dado; una imagen no registrada queda excluida del modelo resultante.

**Herramientas y software**

**CloudCompare:** Software de código abierto para edición, limpieza y análisis de nubes de puntos densas. Utilizado en esta tesis para limpieza de outliers y cálculo de métricas geométricas sobre las nubes densas exportadas.

**COLMAP:** Software de código abierto de Structure from Motion y Multi-View Stereo. Utilizado en esta tesis como pipeline de SfM nativo (vía `ns-process-data` o directamente por línea de comandos), alternativo a RealityScan.

**LaMa (Large Mask Inpainting):** Modelo de inpainting basado en convoluciones de Fourier rápidas. Utilizado en el pipeline de limpieza de distractores de esta tesis (Capítulo 5, sección 5.2.3) para reconstruir el fondo en las áreas donde se eliminaron distractores.

**Nerfstudio:** Framework de código abierto para el entrenamiento, evaluación y exportación de modelos NeRF y 3D Gaussian Splatting a partir de un pipeline de datos común. Framework central utilizado en esta tesis para entrenar Nerfacto y Splatfacto sobre los datasets de los tres casos de estudio.

**RealityScan:** Software comercial de fotogrametría (Epic Games). Utilizado en esta tesis como pipeline de SfM principal para los datasets finales, exportado a formato COLMAP para su uso posterior en Nerfstudio.

**YOLOv8-seg:** Modelo de detección y segmentación de instancias de la familia YOLO (You Only Look Once). Utilizado en esta tesis para detectar y generar máscaras de distractores (personas, aves, vehículos) sobre las imágenes del dataset (Capítulo 5, sección 5.2.3).

**Representaciones y formatos**

**Armónicos esféricos:** Base de funciones matemáticas sobre la esfera que permiten representar la variación del color en función de la dirección de visión. Utilizados en 3DGS para codificar el color view-dependent de cada gaussiana.

**Campo de radiancia:** Representación de una escena que describe la luz emitida o reflejada en cada punto del espacio para cada dirección de visión. Tanto NeRF (implícito) como 3DGS (explícito) son métodos de aprendizaje de campos de radiancia.

**Malla poligonal (Mesh):** Representación geométrica de una superficie 3D mediante una red de triángulos. Formato de salida estándar del pipeline SfM/MVS, directamente integrable con BIM y CAD.

**MLP (Multi-Layer Perceptron):** Red neuronal completamente conectada utilizada en NeRF para aproximar la función de campo de radiancia.

**Nube de puntos (Point Cloud):** Conjunto de puntos discretos (x, y, z) con información de color (RGB). Output intermedio del pipeline SfM e input inicial para 3DGS.

**SDF (Signed Distance Function):** Función que asigna a cada punto del espacio su distancia con signo a la superficie más cercana. Utilizada en 3DGSR para representar implícitamente la geometría dentro del framework de 3DGS.

**.glTF / .GLB:** Formato abierto de distribución de modelos 3D optimizado para transmisión web eficiente. Formato de distribución recomendado para el repositorio digital patrimonial.

**.SPLAT:** Formato emergente de distribución de modelos 3D Gaussian Splatting, diseñado para reducir el tamaño del archivo y facilitar la visualización web sin hardware especializado.

**IFC (Industry Foundation Classes):** Estándar abierto de interoperabilidad para el intercambio de datos BIM entre plataformas. Formato de exportación clave para la integración con flujos de trabajo de gestión patrimonial profesional.

**Métricas de evaluación**

**LPIPS (Learned Perceptual Image Patch Similarity):** Métrica de calidad de imagen basada en distancias entre activaciones de una red neuronal preentrenada, diseñada para correlacionar mejor con la percepción humana que PSNR y SSIM ante artefactos estructurales. Valores más bajos indican mayor similitud perceptual con la referencia.

**PSNR (Peak Signal-to-Noise Ratio):** Métrica de calidad de imagen en decibelios. Valores más altos indican mayor fidelidad de la imagen sintetizada respecto a la referencia.

**SSIM (Structural Similarity Index Measure):** Métrica de calidad de imagen que evalúa similitud estructural considerando luminancia, contraste y estructura local. Correlaciona mejor con la percepción visual humana que el PSNR.

**Hardware y captura**

**GPU (Graphics Processing Unit):** Unidad de procesamiento gráfico. Recurso computacional crítico para el entrenamiento de modelos NeRF y 3DGS.

**GPU consumer-grade:** hardware gráfico orientado al mercado de consumo/gaming (p. ej. NVIDIA GeForce RTX), con memoria VRAM limitada y menor rendimiento sostenido que las GPU de nivel profesional o datacenter (p. ej. NVIDIA A100/H100). Es el hardware efectivamente disponible para esta tesis (Capítulo 4, sección 4.10), condicionando los tiempos de procesamiento reportados y limitando su representatividad frente a un entorno de producción profesional.

**UAV (Unmanned Aerial Vehicle):** Vehículo aéreo no tripulado (drone). Plataforma de captura principal para relevamientos exteriores de edificios históricos, ofreciendo cobertura aérea a bajo costo y alta resolución.
