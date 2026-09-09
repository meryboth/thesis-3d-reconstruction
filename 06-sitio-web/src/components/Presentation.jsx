import { useCallback, useEffect, useState } from "react";

// Presentacion de tesis, pensada para una exposicion oral de ~20 minutos.
// Sintetiza los 7 capitulos sin dejar afuera ninguna hipotesis ni conclusion --
// cada slide cita el capitulo/seccion de origen para poder volver al detalle
// completo durante la defensa si hace falta.

const A = "/content/assets/"; // assets derivados de 05-tesis, copiados por prepare_content.py
const W = "/presentacion-assets/"; // assets propios de la presentacion, fuera de public/content -- prepare_content.py borra y reconstruye ese directorio en cada sync, así que cualquier imagen puesta ahí a mano (como los wireframes) desaparece en el próximo run

function Kicker({ children }) {
  return <span className="pz-kicker">{children}</span>;
}

function Source({ children }) {
  return <span className="pz-source">{children}</span>;
}

const SLIDES = [
  {
    id: "portada",
    render: () => (
      <div className="pz-slide pz-slide-center pz-slide-cover">
        <div className="pz-cover-collage" aria-hidden="true">
          <div className="pz-cover-frag" style={{ backgroundImage: `url(${W}paraguas-wireframe.png)`, backgroundPosition: "50% 22%" }} />
          <div className="pz-cover-frag" style={{ backgroundImage: `url(${W}templete-wireframe.png)`, backgroundPosition: "50% 55%" }} />
          <div className="pz-cover-frag pz-cover-frag-tall" style={{ backgroundImage: `url(${W}panteon-wireframe.png)`, backgroundPosition: "50% 62%", backgroundSize: "140% auto" }} />
        </div>
        <img src="/branding/logo-up.jpg" alt="Universidad de Palermo" className="pz-logo" />
        <Kicker>Tesis de Maestría en Tecnología de la Información</Kicker>
        <h1 className="pz-title pz-title-xl">
          Reconstrucción 3D de patrimonio arquitectónico argentino con técnicas de Computer Vision
        </h1>
        <p className="pz-subtitle">
          Comparativa de SfM, NeRF y 3DGS
          <br />
          Con el fin de obtener un pipeline de reconstrucción e integración con sistemas HBIM
          para la conformación de un archivo digital
        </p>
      </div>
    ),
  },
  {
    id: "motivacion",
    render: () => (
      <div className="pz-slide">
        <Kicker>Motivación · Capítulo 1</Kicker>
        <h2 className="pz-title">No hay planes de restauración que permitan entender el estado actual de las obras</h2>
        <ul className="pz-bullets pz-bullets-lg">
          <li>La documentación tradicional (fotografía, planos CAD) es costosa, lenta y difícil de reproducir ante intervenciones futuras.</li>
          <li>Argentina no cuenta con un archivo digital nacional de referencia para su patrimonio arquitectónico.</li>
          <li>Las técnicas de visión computacional (SfM, NeRF, 3DGS) prometen digitalizar edificios completos a partir de simples videos o fotos.</li>
          <li>
            <strong>Pregunta de investigación:</strong> ¿cuál de estas técnicas es la más adecuada
            —y bajo qué criterios— para documentar patrimonio argentino?
          </li>
        </ul>
      </div>
    ),
  },
  {
    id: "objetivos",
    render: () => (
      <div className="pz-slide">
        <Kicker>Objetivos · Capítulo 1, sección 1.3</Kicker>
        <h2 className="pz-title">Objetivo general</h2>
        <p className="pz-lead">
          Desarrollar un pipeline sistemático y reproducible para la reconstrucción 3D de
          patrimonio arquitectónico argentino, evaluando comparativamente SfM, NeRF y 3DGS y
          proponiendo criterios de selección fundamentados en evidencia.
        </p>
        <ol className="pz-bullets pz-bullets-compact">
          <li>Relevamiento crítico del estado del arte.</li>
          <li>Diseño y ejecución de 5 benchmarks comparativos.</li>
          <li>Propuesta de un pipeline definitivo documentado.</li>
          <li>Diseño de una integración conceptual con flujos HBIM/Revit.</li>
          <li>Evaluación de escalabilidad ante complejidad geométrica creciente.</li>
          <li>Validación de compatibilidad con archivo digital web.</li>
        </ol>
      </div>
    ),
  },
  {
    id: "marco-teorico",
    render: () => (
      <div className="pz-slide">
        <Kicker>Marco teórico · Capítulo 2</Kicker>
        <h2 className="pz-title">Tres formas de reconstruir en 3D a partir de imágenes</h2>
        <div className="pz-cols-3">
          <div className="pz-card">
            <span className="pz-card-tag" style={{ color: "#2454ff" }}>SfM</span>
            <h3>Fotogrametría clásica</h3>
            <p>Triangula puntos coincidentes entre fotos (COLMAP/RealityScan). Da nube de puntos + malla texturizada explícita, con topología real.</p>
          </div>
          <div className="pz-card">
            <span className="pz-card-tag" style={{ color: "#c9820f" }}>NeRF</span>
            <h3>Campo de radiancia neuronal</h3>
            <p>Una red neuronal aprende a sintetizar vistas nuevas de la escena (Nerfacto). No produce geometría explícita.</p>
          </div>
          <div className="pz-card">
            <span className="pz-card-tag" style={{ color: "#1f9e6d" }}>3DGS</span>
            <h3>Gaussian Splatting</h3>
            <p>Representa la escena como millones de "gaussianas" 3D con color y opacidad (Splatfacto). Renderiza en tiempo real.</p>
          </div>
        </div>
      </div>
    ),
  },
  {
    id: "casos-de-estudio",
    render: () => (
      <div className="pz-slide">
        <Kicker>Casos de estudio · Capítulo 3</Kicker>
        <h2 className="pz-title">Tres obras, complejidad geométrica creciente</h2>
        <div className="pz-cols-3">
          <div className="pz-photo-card pz-photo-card-wireframe">
            <img src={`${W}paraguas-wireframe.png`} alt="Los Paraguas, estilo wireframe" />
            <h3>Los Paraguas</h3>
            <p>Amancio Williams<br />1999–2000</p>
          </div>
          <div className="pz-photo-card pz-photo-card-wireframe">
            <img src={`${W}templete-wireframe.png`} alt="Templete Central, estilo wireframe" />
            <h3>Templete Central</h3>
            <p>Ítala Fulvia Villa<br />1958</p>
          </div>
          <div className="pz-photo-card pz-photo-card-wireframe">
            <img src={`${W}panteon-wireframe.png`} alt="Panteón Asociación Catalana, estilo wireframe" />
            <h3>Panteón Asoc. Catalana</h3>
            <p>Santiago Barris<br />1899</p>
          </div>
        </div>
      </div>
    ),
  },
  {
    id: "diseno-experimental",
    render: () => (
      <div className="pz-slide">
        <Kicker>Diseño experimental · Capítulo 4</Kicker>
        <h2 className="pz-title">5 hipótesis, 5 benchmarks</h2>
        <table className="pz-table">
          <thead>
            <tr><th>Benchmark</th><th>Hipótesis</th><th>Qué evalúa</th></tr>
          </thead>
          <tbody>
            <tr><td>B1</td><td>H1</td><td>Especialización de cada técnica por criterio de uso</td></tr>
            <tr><td>B2</td><td>H2</td><td>Preprocesamiento de imágenes (ComfyUI): distractores y fondo</td></tr>
            <tr><td>B3</td><td>H3</td><td>Complejidad geométrica creciente entre los 3 casos</td></tr>
            <tr><td>B4</td><td>H4</td><td>Dataset multi-dispositivo (DJI + Insta360 combinados)</td></tr>
            <tr><td>B5</td><td>H5</td><td>Compatibilidad web y reproducibilidad</td></tr>
          </tbody>
        </table>
        <p className="pz-footnote">Hardware consumer-grade en todos los casos: GPU con 6 GB de VRAM, sin acceso a nivel profesional.</p>
      </div>
    ),
  },
  {
    id: "h1",
    render: () => (
      <div className="pz-split">
        <div className="pz-split-text">
          <Kicker>H1 · Especialización por técnica</Kicker>
          <h2 className="pz-title">Parcialmente confirmada — con una sorpresa</h2>
          <p className="pz-lead">
            SfM es, en efecto, la única técnica con integración BIM directa. Pero Splatfacto
            <strong> superó a Nerfacto en PSNR/SSIM en los tres casos de estudio</strong>, sin
            excepción.
          </p>
          <ul className="pz-bullets">
            <li>Los Paraguas (baja complejidad): 30,6 dB vs. 25,9 dB</li>
            <li>Templete Central (media): 23,6 dB vs. 19,5 dB</li>
            <li>Panteón Asoc. Catalana (alta): 25,9 dB vs. 10,4 dB — Nerfacto casi inutilizable</li>
          </ul>
          <Source>Capítulo 5, Tabla 5.7</Source>
        </div>
        <div className="pz-split-media">
          <img src={`${A}cap5-05-psnr-ssim-por-sitio.png`} alt="PSNR y SSIM por sitio y técnica" />
          <div className="pz-render-compare">
            <div>
              <img src={`${W}panteon-nerfacto-render.gif`} alt="Render Nerfacto del Panteón Asociación Catalana, con floaters" />
              <span>Nerfacto</span>
            </div>
            <div>
              <img src={`${W}panteon-splatfacto-render.gif`} alt="Render Splatfacto del Panteón Asociación Catalana" />
              <span>Splatfacto</span>
            </div>
          </div>
        </div>
      </div>
    ),
  },
  {
    id: "renders-galeria",
    render: () => (
      <div className="pz-slide">
        <Kicker>Resultados · Capítulo 5</Kicker>
        <h2 className="pz-title">Nerfacto vs. Splatfacto, en los tres casos</h2>
        <div className="pz-render-gallery">
          <div className="pz-render-gallery-col">
            <h3>Los Paraguas</h3>
            <div className="pz-render-compare pz-render-compare-stacked">
              <div>
                <img src={`${W}paraguas-nerfacto-render.gif`} alt="Render Nerfacto de Los Paraguas" />
                <span>Nerfacto</span>
              </div>
              <div>
                <img src={`${W}paraguas-splatfacto-render.gif`} alt="Render Splatfacto de Los Paraguas" />
                <span>Splatfacto</span>
              </div>
            </div>
          </div>
          <div className="pz-render-gallery-col">
            <h3>Templete Central</h3>
            <div className="pz-render-compare pz-render-compare-stacked">
              <div>
                <img src={`${W}templete-nerfacto-render.gif`} alt="Render Nerfacto del Templete Central" />
                <span>Nerfacto</span>
              </div>
              <div>
                <img src={`${W}templete-splatfacto-render.gif`} alt="Render Splatfacto del Templete Central" />
                <span>Splatfacto</span>
              </div>
            </div>
          </div>
          <div className="pz-render-gallery-col">
            <h3>Panteón Asoc. Catalana</h3>
            <div className="pz-render-compare pz-render-compare-stacked">
              <div>
                <img src={`${W}panteon-nerfacto-render.gif`} alt="Render Nerfacto del Panteón Asociación Catalana" />
                <span>Nerfacto</span>
              </div>
              <div>
                <img src={`${W}panteon-splatfacto-render.gif`} alt="Render Splatfacto del Panteón Asociación Catalana" />
                <span>Splatfacto</span>
              </div>
            </div>
          </div>
        </div>
        <Source>Capítulo 5 · Renders finales por sitio y técnica (dataset DJI)</Source>
      </div>
    ),
  },
  {
    id: "h2",
    render: () => (
      <div className="pz-split">
        <div className="pz-split-text">
          <Kicker>H2 · Preprocesamiento</Kicker>
          <h2 className="pz-title">No se sostiene</h2>
          <p className="pz-lead">
            Se probaron dos variantes de limpieza con ComfyUI: eliminar distractores (YOLOv8-seg
            + inpainting LaMa) y aislar el edificio de su fondo. <strong>Ambas empeoraron los
            resultados</strong> respecto al dataset original, sin procesar.
          </p>
          <ul className="pz-bullets">
            <li>Eliminar distractores: no mejora PSNR/SSIM; en Nerfacto empeora en las tres métricas.</li>
            <li>Aislar el fondo: resultados aún peores — el contexto ayuda a interpretar el edificio, no lo perjudica.</li>
          </ul>
          <Source>Capítulo 5, secciones 5.3.4 y 5.3.6</Source>
        </div>
        <div className="pz-split-media">
          <img src={`${A}cap5-masking-psnr-ssim-lpips-raw-vs-masked.png`} alt="PSNR/SSIM/LPIPS raw vs. dataset con máscara" />
        </div>
      </div>
    ),
  },
  {
    id: "h3",
    render: () => (
      <div className="pz-split">
        <div className="pz-split-text">
          <Kicker>H3 · Complejidad geométrica</Kicker>
          <h2 className="pz-title">Confirmada para Nerfacto, no para Splatfacto</h2>
          <p className="pz-lead">
            Nerfacto cae de forma monótona a medida que crece la complejidad ornamental. Splatfacto
            no: se recupera en el caso más complejo, porque su resultado está mediado por la
            calidad del registro SfM de entrada.
          </p>
          <ul className="pz-bullets">
            <li>El Panteón (alta complejidad) tuvo el mejor registro SfM de los tres casos: 99,93%.</li>
            <li>La complejidad geométrica y la calidad de registro interactúan — no son variables independientes.</li>
          </ul>
          <Source>Capítulo 5, sección 5.4</Source>
        </div>
        <div className="pz-split-media">
          <img src={`${A}cap5-07-psnr-vs-complejidad.png`} alt="PSNR vs. nivel de complejidad geométrica" />
        </div>
      </div>
    ),
  },
  {
    id: "h4",
    render: () => (
      <div className="pz-split">
        <div className="pz-split-text">
          <Kicker>H4 · Dataset multi-dispositivo · el hallazgo central</Kicker>
          <h2 className="pz-title">No se sostiene — y por qué, a nivel geométrico</h2>
          <p className="pz-lead">
            Combinar DJI Neo 2 e Insta360 X5 en un mismo dataset introduce un riesgo real de
            fallo de registro, y aun logrando el registro, el resultado es peor que un único
            dispositivo.
          </p>
          <ul className="pz-bullets">
            <li>Dos corridas de COLMAP sobre el mismo dataset híbrido: <strong>100% vs. 0,63%</strong> de registro.</li>
            <li>Los matches DJI↔Insta360 son sistemáticamente más débiles (43 inliers promedio) que dentro de un mismo dispositivo (689 DJI-DJI, 189 Insta360-Insta360).</li>
            <li>En 3 de 4 combinaciones técnica × caso, el dataset híbrido rindió peor que cualquier dispositivo solo — sin excepción.</li>
          </ul>
          <Source>Capítulo 5, secciones 5.5.2–5.5.6</Source>
        </div>
        <div className="pz-split-media">
          <img src={`${A}cap5-hybrid-cross-camera-matching-chart.png`} alt="Calidad de matching por tipo de par de dispositivos" />
        </div>
      </div>
    ),
  },
  {
    id: "h5",
    render: () => (
      <div className="pz-split">
        <div className="pz-split-text">
          <Kicker>H5 · Compatibilidad web y reproducibilidad</Kicker>
          <h2 className="pz-title">Confirmada — y validada en vivo</h2>
          <p className="pz-lead">
            SfM y Splatfacto tienen rutas de publicación web directas (malla <code>.glTF</code>,
            splat <code>.ply</code>/<code>.splat</code>); Nerfacto no. El archivo digital de esta
            tesis carga los tres casos de estudio en un visor real, sin errores.
          </p>
          <a
            className="pz-btn"
            href="https://thesis-3d-reconstruction.vercel.app/archivo-digital"
            target="_blank"
            rel="noopener noreferrer"
          >
            Ver el archivo digital en vivo →
          </a>
          <Source>Capítulo 5, sección 5.6 · Capítulo 6, sección 6.2.3</Source>
        </div>
        <div className="pz-split-media pz-split-media-frame">
          <iframe
            title="Archivo digital — Los Paraguas"
            src="/archivo-digital/paraguas/index.html"
            loading="lazy"
          />
        </div>
      </div>
    ),
  },
  {
    id: "pipeline",
    render: () => (
      <div className="pz-slide">
        <Kicker>Pipeline definitivo · Capítulo 6</Kicker>
        <h2 className="pz-title">Un pipeline, dos rutas de destino</h2>
        <img className="pz-diagram" src={`${A}cap6-pipeline-definitivo.png`} alt="Diagrama del pipeline definitivo" />
        <p className="pz-footnote">
          Captura con un único dispositivo, sin preprocesamiento, con verificación binaria de SfM.
          A partir de ahí, una ruta orientada a la publicación web con Gaussian Splatting, y otra
          al procesamiento con SfM para la integración con BIM.
        </p>
      </div>
    ),
  },
  {
    id: "segmentacion",
    render: () => (
      <div className="pz-slide">
        <Kicker>Aporte propio · Capítulo 6, sección 6.3</Kicker>
        <h2 className="pz-title">Segmentación geométrica de la nube de puntos</h2>
        <p className="pz-lead">
          Un clasificador propio, sin redes neuronales ni entrenamiento, que separa la nube densa
          de SfM en 4 clases relevantes para BIM — validado sobre los tres casos de estudio.
        </p>
        <div className="pz-cols-3 pz-cols-3-imgs">
          <img src={`${A}cap6-segmentacion-templete.png`} alt="Templete Central segmentado" />
          <img src={`${A}cap6-segmentacion-paraguas.png`} alt="Los Paraguas segmentado" />
          <img src={`${A}cap6-segmentacion-panteon.png`} alt="Panteón segmentado" />
        </div>
        <pre className="pz-code">{`# poc_segmentation_multi_site.py — sin ML, 4 pasos geométricos
1. Nivelado:      RANSAC sobre el plano de piso
2. Verticalidad:  normales locales (PCA)
3. Bandas:        picos de densidad en el histograma de alturas
4. Columna/baranda: fracción de altura techo-piso por celda`}</pre>
        <Source>Templete: 589.605 pts · Paraguas: 502.817 pts · Panteón: 356.234 pts (post-filtro de vegetación)</Source>
      </div>
    ),
  },
  {
    id: "vlm",
    render: () => (
      <div className="pz-split">
        <div className="pz-split-text">
          <Kicker>Exploración · Capítulo 6, sección 6.3.3</Kicker>
          <h2 className="pz-title">Segmentación asistida por VLM: resultado negativo, honesto</h2>
          <p className="pz-lead">
            Se probó reemplazar el umbral geométrico por un modelo de visión (Moondream2,
            Qwen2-VL) para distinguir columna de baranda. Ninguno superó al clasificador simple.
          </p>
          <ul className="pz-bullets">
            <li>Moondream2: 54% de acierto total — pero respondió <strong>"baranda" el 100% de las veces</strong>, sin importar la imagen.</li>
            <li>Qwen2-VL: mismo patrón, sesgo opuesto — siempre "columna".</li>
            <li>El sesgo se sostiene incluso ante un rectángulo negro sintético: es una propiedad del modelo, no del dataset.</li>
          </ul>
          <Source>Capítulo 6, Tabla 6.3</Source>
        </div>
        <div className="pz-split-media">
          <img src={`${A}cap6-poc-vlm-frag-columna.png`} alt="Columna clasificada incorrectamente como baranda" />
        </div>
      </div>
    ),
  },
  {
    id: "reconstruccion-ia",
    render: () => (
      <div className="pz-split">
        <div className="pz-split-text">
          <Kicker>Exploración · Capítulo 6, sección 6.3.4</Kicker>
          <h2 className="pz-title">Reconstrucción geométrica asistida por un agente de IA</h2>
          <p className="pz-lead">
            Alternativa a la malla texturizada: en vez de segmentar la nube por clase, un agente de
            IA con control directo sobre Blender <strong>ajusta geometría paramétrica explícita</strong> —
            círculos, superficies suaves — directamente sobre la nube densa de SfM.
          </p>
          <ul className="pz-bullets">
            <li>GPT-6 Astra (OpenAI), operado desde Codex, conectado a Blender vía Blender MCP.</li>
            <li>Columnas: circunferencias en 9 cortes de altura. Cubiertas: grilla 34×34, superficie ajustada por cuantiles de altura.</li>
            <li>Distancia mediana a la nube: 0,0044 unidades SfM — pero contra los mismos puntos usados para ajustar, no es validación independiente.</li>
            <li>Los 3 sitios tienen modelo completo: Los Paraguas, Templete Central y Panteón Asoc. Catalana.</li>
          </ul>
          <Source>Capítulo 6, sección 6.3.4 y Tabla 6.4</Source>
        </div>
        <div className="pz-split-media">
          <img src={`${W}paraguas-reconstruccion-ia.png`} alt="Render del modelo reconstruido de Los Paraguas, dos cubiertas sobre columnas" />
        </div>
      </div>
    ),
  },
  {
    id: "nerf-potencial",
    render: () => (
      <div className="pz-split">
        <div className="pz-split-text">
          <Kicker>Hallazgo lateral · Capítulo 6, sección 6.1</Kicker>
          <h2 className="pz-title">NeRF, fuera de este objetivo — pero no sin mérito</h2>
          <p className="pz-lead">
            Excluido del pipeline definitivo (peor fidelidad, sin ruta de publicación web), NeRF sí
            mostró potencial para generar recorridos de cámara nuevos, no presentes en la captura
            original — un caso de uso audiovisual, no patrimonial.
          </p>
          <Source>Los Paraguas, recorrido generado con el visor de Nerfstudio</Source>
        </div>
        <div className="pz-split-media">
          <img src={`${A}cap6-paraguas-nerf-custompath.gif`} alt="Recorrido de cámara nuevo sobre Los Paraguas, generado con Nerfstudio" />
        </div>
      </div>
    ),
  },
  {
    id: "sfm-animado",
    render: () => (
      <div className="pz-slide">
        <Kicker>Reconstrucción SfM · Capítulo 5</Kicker>
        <h2 className="pz-title">De la nube dispersa a la malla texturizada</h2>
        <div className="pz-render-gallery">
          <div className="pz-render-gallery-col">
            <h3>Los Paraguas</h3>
            <img className="pz-diagram" src={`${W}paraguas-sfm-render.gif`} alt="Reconstrucción SfM de Los Paraguas" />
          </div>
          <div className="pz-render-gallery-col">
            <h3>Templete Central</h3>
            <img className="pz-diagram" src={`${A}cap5-templete-central-sfm.gif`} alt="Reconstrucción SfM del Templete Central" />
          </div>
          <div className="pz-render-gallery-col">
            <h3>Panteón Asoc. Catalana</h3>
            <img className="pz-diagram" src={`${W}panteon-sfm-render.gif`} alt="Reconstrucción SfM del Panteón Asociación Catalana" />
          </div>
        </div>
      </div>
    ),
  },
  {
    id: "conclusiones",
    render: () => (
      <div className="pz-slide">
        <Kicker>Conclusiones · Capítulo 7</Kicker>
        <h2 className="pz-title">No existe una técnica dominante — existe especialización real</h2>
        <ul className="pz-bullets pz-bullets-lg">
          <li>Splatfacto: mejor desempeño visual general y el único formato listo para la web.</li>
          <li>SfM: insustituible para integración BIM — malla explícita, con topología.</li>
          <li>Nerfacto: sin ventaja decisiva en ningún criterio evaluado en esta tesis.</li>
          <li><strong>Un único dispositivo de captura, siempre</strong> — combinar cámaras no compensa, empeora.</li>
          <li><strong>Sin preprocesamiento</strong> — el dataset original ya es suficiente.</li>
          <li>El aporte metodológico no anticipado: un clasificador geométrico de segmentación, sin ML, que agiliza la integración con BIM.</li>
        </ul>
      </div>
    ),
  },
  {
    id: "futuro",
    render: () => (
      <div className="pz-slide">
        <Kicker>Líneas futuras · Capítulo 7, sección 7.5</Kicker>
        <h2 className="pz-title">Lo que queda abierto</h2>
        <ul className="pz-bullets pz-bullets-lg">
          <li>Estabilizar el registro SfM híbrido con matching guiado por dispositivo.</li>
          <li>Métrica cuantitativa de cobertura reconstruida, con referencia geométrica de control.</li>
          <li>Validar la integración HBIM/Revit con un modelador profesional.</li>
          <li>Fine-tuning de VLMs sobre nubes de puntos arquitectónicas.</li>
          <li>Medición cuantitativa de fidelidad geométrica contra una nube de control (TLS).</li>
        </ul>
      </div>
    ),
  },
  {
    id: "cierre",
    render: () => (
      <div className="pz-slide pz-slide-center">
        <Kicker>Reflexión final · Capítulo 7</Kicker>
        <h2 className="pz-title">Los aportes de esta tesis</h2>
        <ul className="pz-bullets pz-bullets-lg pz-bullets-center">
          <li>Se definió un pipeline open source para reconstruir en 3D patrimonio.</li>
          <li>Se inauguró un archivo digital con los casos de estudio, que puede seguir creciendo.</li>
          <li>Se construyó un algoritmo que permite segmentar la nube de puntos, para que la integración con BIM sea más fácil.</li>
          <li>Se recomendó una estrategia de captura sólida, basada en un único dispositivo de fácil acceso y con alcance aéreo.</li>
          <li>Se validó que hay técnicas —SfM y Gaussian Splatting— que permiten reconstruir obras de complejidad geométrica y ornamental elevada.</li>
        </ul>
        <p className="pz-subtitle">
          Esperamos que la tecnología sea una disciplina que permita tender puentes y generar
          soluciones para otras áreas de conocimiento, como la arquitectura.
        </p>
        <p className="pz-thanks">Gracias.</p>
      </div>
    ),
  },
];

export default function Presentation() {
  const [index, setIndex] = useState(0);
  const total = SLIDES.length;

  const goTo = useCallback(
    (i) => setIndex(Math.max(0, Math.min(total - 1, i))),
    [total]
  );

  useEffect(() => {
    function onKey(e) {
      if (e.key === "ArrowRight" || e.key === " " || e.key === "PageDown") {
        e.preventDefault();
        goTo(index + 1);
      } else if (e.key === "ArrowLeft" || e.key === "PageUp") {
        e.preventDefault();
        goTo(index - 1);
      } else if (e.key === "Home") {
        goTo(0);
      } else if (e.key === "End") {
        goTo(total - 1);
      }
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [index, goTo, total]);

  const slide = SLIDES[index];
  const progress = ((index + 1) / total) * 100;

  return (
    <div className="pz-root">
      <header className="pz-header">
        <a className="pz-back" href="/">
          ← Volver a la tesis
        </a>
        <div className="pz-progress-track">
          <div className="pz-progress-fill" style={{ width: `${progress}%` }} />
        </div>
        <span className="pz-counter">
          {String(index + 1).padStart(2, "0")} / {String(total).padStart(2, "0")}
        </span>
      </header>

      <main className="pz-stage">{slide.render()}</main>

      <nav className="pz-nav">
        <button type="button" onClick={() => goTo(index - 1)} disabled={index === 0} aria-label="Anterior">
          ‹
        </button>
        <div className="pz-dots">
          {SLIDES.map((s, i) => (
            <button
              key={s.id}
              type="button"
              className={i === index ? "pz-dot is-active" : "pz-dot"}
              onClick={() => goTo(i)}
              aria-label={`Ir a la diapositiva ${i + 1}`}
            />
          ))}
        </div>
        <button type="button" onClick={() => goTo(index + 1)} disabled={index === total - 1} aria-label="Siguiente">
          ›
        </button>
      </nav>
    </div>
  );
}
