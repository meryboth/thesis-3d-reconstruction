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

function Nodo({ n, archivo, titulo, pie }) {
  return (
    <figure className="pz-nodo" style={{ "--paso": n }}>
      <img src={`${W}${archivo}`} alt={`${titulo}: ${pie}`} />
      <figcaption>
        <strong>
          <span className="pz-nodo-n">{n}</span> {titulo}
        </strong>
        <span>{pie}</span>
      </figcaption>
    </figure>
  );
}

// Colores por tecnica -- se reusan en las tarjetas del marco teorico y en los
// diagramas, para que cada columna se lea como una unidad.
const SFM = "#2454ff";
const NERF = "#c9820f";
const GS = "#1f9e6d";

// Los tres diagramas de abajo son esquemas propios de lo que pasa DENTRO de cada
// tecnica (no del resultado), dibujados en SVG para que queden nitidos proyectados
// y sigan el mismo lenguaje grafico del resto de la presentacion. Corresponden a
// las Figuras 2.1, 2.2 y 2.3 del Capitulo 2.

// nube dispersa con silueta de cubierta a dos aguas
const NUBE_SFM = [
  [196, 100], [205, 91], [214, 82], [223, 73], [232, 64], [241, 73], [250, 82],
  [259, 91], [268, 100], [228, 56], [220, 66], [236, 66], [212, 76], [244, 76],
  [204, 86], [252, 86], [216, 94], [240, 94], [228, 80], [228, 92], [200, 104],
  [256, 104], [228, 104], [212, 106], [244, 106], [190, 106], [266, 106],
];

function DiagramaSfM() {
  const foto = (y) => (
    <rect x="8" y={y} width="62" height="46" rx="3" fill="none" stroke={SFM} strokeWidth="1.2" opacity="0.75" />
  );
  const kp = [[22, 16], [44, 10], [56, 30], [32, 36]];
  return (
    <svg className="pz-diagrama" viewBox="0 0 320 150" role="img"
      aria-label="Esquema de fotogrametría: keypoints emparejados entre dos fotos, rayos que triangulan y nube de puntos resultante">
      {foto(10)}
      {foto(70)}
      {kp.map(([x, y], i) => (
        <g key={i}>
          <circle cx={x} cy={10 + y} r="2.1" fill={SFM} />
          <circle cx={x + 3} cy={70 + y + 4} r="2.1" fill={SFM} />
          <line x1={x} y1={10 + y} x2={x + 3} y2={70 + y + 4} stroke={SFM} strokeWidth="0.8" strokeDasharray="2 2" opacity="0.55" />
        </g>
      ))}
      {[[70, 22], [70, 48], [70, 82], [70, 108]].map(([x, y], i) => (
        <line key={i} x1={x} y1={y} x2="196" y2={y < 65 ? 74 : 86} stroke={SFM} strokeWidth="0.7" opacity="0.35" />
      ))}
      {NUBE_SFM.map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r="2" fill={SFM} opacity={i % 3 === 0 ? 0.9 : 0.55} />
      ))}
      <text className="pz-diagrama-t" x="39" y="140" textAnchor="middle">keypoints</text>
      <text className="pz-diagrama-t" x="135" y="140" textAnchor="middle">matching + poses</text>
      <text className="pz-diagrama-t" x="250" y="140" textAnchor="middle">nube de puntos</text>
    </svg>
  );
}

function DiagramaNeRF() {
  const capas = [116, 150, 184];
  const filas = [12, 27, 42];
  const muestras = [[92, 1.5], [112, 2.1], [132, 3.2], [152, 3.8], [172, 2.9], [192, 2], [212, 1.5], [232, 1.2]];
  return (
    <svg className="pz-diagrama" viewBox="0 0 320 150" role="img"
      aria-label="Esquema de NeRF: un rayo por píxel, muestreo de puntos, un MLP que predice color y densidad, e integración hasta el píxel">
      {capas.map((x, ci) => filas.map((y, fi) => (
        <circle key={`${ci}-${fi}`} cx={x} cy={y} r="3" fill="none" stroke={NERF} strokeWidth="1.1" />
      )))}
      {filas.map((y1, i) => filas.map((y2, j) => (
        <g key={`e${i}-${j}`}>
          <line x1={capas[0] + 3} y1={y1} x2={capas[1] - 3} y2={y2} stroke={NERF} strokeWidth="0.5" opacity="0.35" />
          <line x1={capas[1] + 3} y1={y1} x2={capas[2] - 3} y2={y2} stroke={NERF} strokeWidth="0.5" opacity="0.35" />
        </g>
      )))}
      <text className="pz-diagrama-t" x="100" y="30" textAnchor="end">MLP</text>
      <text className="pz-diagrama-t pz-diagrama-t-fuerte" x="198" y="24">σ · RGB</text>
      <line x1="152" y1="80" x2="152" y2="52" stroke={NERF} strokeWidth="0.9" strokeDasharray="3 2.5" />
      <rect x="72" y="62" width="188" height="54" rx="4" fill="none" stroke={NERF} strokeWidth="0.9" strokeDasharray="4 3" opacity="0.5" />
      <rect x="6" y="82" width="9" height="14" rx="1.5" fill={NERF} opacity="0.85" />
      <polygon points="15,84 34,74 34,104 15,94" fill={NERF} opacity="0.35" />
      <line x1="34" y1="89" x2="272" y2="89" stroke={NERF} strokeWidth="1" />
      {muestras.map(([x, r], i) => (
        <circle key={i} cx={x} cy="89" r={r} fill={NERF} opacity="0.85" />
      ))}
      <rect x="278" y="81" width="16" height="16" rx="2" fill={NERF} opacity="0.75" />
      <text className="pz-diagrama-t" x="90" y="140" textAnchor="middle">rayo por píxel</text>
      <text className="pz-diagrama-t" x="180" y="140" textAnchor="middle">muestreo 3D</text>
      <text className="pz-diagrama-t" x="278" y="140" textAnchor="middle">píxel</text>
    </svg>
  );
}

// gaussianas: x, y, radio mayor, radio menor, rotacion
const GAUSSIANAS = [
  [128, 34, 11, 5, -32], [150, 30, 13, 5, 8], [172, 38, 10, 4, 34],
  [116, 54, 9, 4, -14], [140, 50, 14, 6, -4], [166, 56, 11, 5, 22],
  [124, 74, 8, 5, 40], [148, 70, 12, 5, -18], [174, 76, 9, 4, 6],
  [136, 92, 10, 4, 16], [162, 94, 8, 4, -28],
];

function DiagramaGS() {
  const flecha = (x) => (
    <path d={`M${x} 62 h16 m-4 -3.5 l4 3.5 -4 3.5`} fill="none" stroke={GS} strokeWidth="1.2" />
  );
  return (
    <svg className="pz-diagrama" viewBox="0 0 320 150" role="img"
      aria-label="Esquema de Gaussian Splatting: cada punto de la nube se convierte en una gaussiana, se proyecta al plano de imagen y el ciclo clona, divide y poda">
      {[[14, 40], [26, 32], [38, 44], [20, 58], [34, 62], [46, 54], [16, 76], [30, 82], [44, 74], [24, 94], [40, 92]].map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r="1.8" fill={GS} opacity="0.8" />
      ))}
      {flecha(58)}
      {GAUSSIANAS.map(([x, y, rx, ry, rot], i) => (
        <ellipse key={i} cx={x} cy={y} rx={rx} ry={ry} fill={GS}
          opacity={0.18 + (i % 4) * 0.12} transform={`rotate(${rot} ${x} ${y})`} />
      ))}
      {flecha(192)}
      <rect x="224" y="22" width="84" height="84" rx="3" fill="none" stroke={GS} strokeWidth="1.2" opacity="0.75" />
      {GAUSSIANAS.map(([x, y, rx, ry, rot], i) => (
        <ellipse key={`p${i}`} cx={224 + (x - 110) * 0.86} cy={22 + (y - 22) * 0.9} rx={rx * 0.8} ry={ry * 0.8}
          fill={GS} opacity={0.16 + (i % 4) * 0.11} transform={`rotate(${rot} ${224 + (x - 110) * 0.86} ${22 + (y - 22) * 0.9})`} />
      ))}
      <path d="M262 110 C 238 128, 176 128, 152 112" fill="none" stroke={GS} strokeWidth="1" strokeDasharray="4 3" />
      <path d="M156 108 l-4 4.5 6 1.5" fill="none" stroke={GS} strokeWidth="1" />
      <text className="pz-diagrama-t" x="30" y="140" textAnchor="middle">nube SfM</text>
      <text className="pz-diagrama-t" x="150" y="140" textAnchor="middle">clonar · dividir · podar</text>
      <text className="pz-diagrama-t" x="266" y="140" textAnchor="middle">rasterizado</text>
    </svg>
  );
}

// Diagrama de arquitectura del pipeline definitivo (Cap. 6, seccion 6.2).
// Reemplaza al PNG generado por build_pipeline_diagram.py: en HTML/CSS se lee a
// cualquier tamano de proyeccion y cada nodo puede llevar el icono de la pieza
// tecnica que le corresponde. El .md del Capitulo 6 sigue usando la Figura 6.2.

const ICO = {
  dron: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="5" cy="6" r="3" /><circle cx="19" cy="6" r="3" />
      <circle cx="5" cy="18" r="3" /><circle cx="19" cy="18" r="3" />
      <path d="M7.4 8.1 10 10.5h4l2.6-2.4M7.4 15.9 10 13.5h4l2.6 2.4" />
      <rect x="9.5" y="10" width="5" height="4" rx="1" />
    </svg>
  ),
  sfm: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M2 8v8l6-4z" /><path d="M8 12h4" />
      <circle cx="16" cy="6" r="1.3" /><circle cx="20" cy="12" r="1.3" />
      <circle cx="15" cy="17" r="1.3" /><circle cx="19.5" cy="4" r="1" />
      <path d="M12 12 16 6M12 12l8 0M12 12l3 5" />
    </svg>
  ),
  nube: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      {[[5, 16], [8, 12], [11, 8], [14, 12], [17, 16], [8, 18], [12, 15], [16, 18], [11, 19], [12, 5], [6, 19], [18, 19]].map(
        ([x, y], i) => <circle key={i} cx={x} cy={y} r="1.15" />
      )}
    </svg>
  ),
  malla: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M3 6h18v12H3z" /><path d="M3 6l9 6 9-6M3 18l9-6 9 6M12 6v12" />
    </svg>
  ),
  splat: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <ellipse cx="9" cy="9" rx="5" ry="2.6" transform="rotate(-28 9 9)" />
      <ellipse cx="15" cy="13" rx="5.5" ry="2.8" transform="rotate(16 15 13)" />
      <ellipse cx="9" cy="17" rx="4.5" ry="2.3" transform="rotate(-8 9 17)" />
    </svg>
  ),
  capas: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 3 21 7.5 12 12 3 7.5z" /><path d="M3 12l9 4.5L21 12" /><path d="M3 16.5 12 21l9-4.5" />
    </svg>
  ),
  mano: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M4 4l7 16 2-6 6-2z" /><path d="M14 14l5 5" />
    </svg>
  ),
  archivo: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <rect x="2.5" y="4" width="19" height="16" rx="2" /><path d="M2.5 8.5h19" />
      <circle cx="5.5" cy="6.2" r="0.7" /><circle cx="8" cy="6.2" r="0.7" />
    </svg>
  ),
  repo: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <ellipse cx="12" cy="6" rx="8" ry="3" />
      <path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6" />
      <path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3" />
    </svg>
  ),
  cubo: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 2.8 21 7.4v9.2L12 21.2 3 16.6V7.4z" /><path d="M3 7.4 12 12l9-4.6M12 12v9.2" />
    </svg>
  ),
  descarga: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 3v11M7.5 9.5 12 14l4.5-4.5" /><path d="M4 18h16" />
    </svg>
  ),
};

function NodoPipe({ ico, titulo, detalle, tipo }) {
  return (
    <div className={`pp-nodo pp-${tipo}`}>
      <span className="pp-ico">{ICO[ico]}</span>
      <span className="pp-txt">
        <strong>{titulo}</strong>
        <em>{detalle}</em>
      </span>
    </div>
  );
}

function DiagramaPipeline() {
  return (
    <div className="pp">
      <div className="pp-tronco">
        <span className="pp-lane">Tronco común</span>
        <div className="pp-fila">
          <NodoPipe tipo="captura" ico="dron" titulo="Captura"
            detalle="DJI Neo 2 · Insta360 X5 — un solo dispositivo" />
          <span className="pp-flecha" />
          <NodoPipe tipo="sfm" ico="sfm" titulo="SfM"
            detalle="RealityScan · COLMAP/Nerfstudio + verificación binaria" />
          <span className="pp-flecha" />
          <div className="pp-par-salidas">
            <NodoPipe tipo="salida" ico="nube" titulo="Nube densa + dispersa" detalle=".ply / COLMAP" />
            <NodoPipe tipo="salida" ico="malla" titulo="Malla texturizada" detalle=".obj + texturas" />
          </div>
          <span className="pp-flecha pp-flecha-tenue" />
          <NodoPipe tipo="concepto" ico="cubo" titulo="Modelado asistido por IA"
            detalle="Blender MCP — experimento, §6.3.4" />
        </div>
      </div>

      <div className="pp-bifurca">
        <span>bifurca según el destino</span>
      </div>

      <div className="pp-ramas">
        <div className="pp-rama">
          <span className="pp-lane pp-lane-hbim">Rama HBIM · 6.2.2</span>
          <NodoPipe tipo="impl" ico="capas" titulo="Segmentación geométrica"
            detalle="poc_segmentation_multi_site.py — 4 clases, sin ML" />
          <span className="pp-flecha-v" />
          <NodoPipe tipo="impl" ico="mano" titulo="Control de calidad humano"
            detalle="visor /segmentador — edición manual" />
          <span className="pp-flecha-v" />
          <NodoPipe tipo="salida" ico="descarga" titulo="Nube segmentada por clase" detalle=".ply" />
          <div className="pp-conceptual">
            <span className="pp-conceptual-tag">Fuera de alcance · propuesta conceptual</span>
            <ul>
              <li>Importación a Revit / Recap como referencia scan-to-BIM</li>
              <li>Modelado paramétrico: cada clase → categoría Revit</li>
              <li>Vínculo documental con la malla y el SfM original</li>
            </ul>
          </div>
        </div>

        <div className="pp-rama">
          <span className="pp-lane pp-lane-web">Rama archivo digital web · 6.2.3</span>
          <NodoPipe tipo="impl" ico="splat" titulo="Entrenamiento Splatfacto"
            detalle="Nerfstudio — sin preprocesamiento, sin Nerfacto" />
          <span className="pp-flecha-v" />
          <NodoPipe tipo="impl" ico="mano" titulo="Edición en SuperSplat"
            detalle="recorte de outliers y gaussianas de baja opacidad" />
          <span className="pp-flecha-v" />
          <NodoPipe tipo="salida" ico="descarga" titulo="Escena de gaussianas" detalle=".splat / .ply" />
          <span className="pp-flecha-v" />
          <NodoPipe tipo="impl" ico="archivo" titulo="Visor en navegador"
            detalle="PlayCanvas — render en tiempo real" />
        </div>
      </div>

      <div className="pp-converge">
        <span className="pp-cv-izq" />
        <span className="pp-cv-h" />
        <span className="pp-cv-der" />
        <span className="pp-cv-baja" />
        <NodoPipe tipo="captura" ico="repo" titulo="Archivo digital web — descarga dual"
          detalle=".splat limpio (rama web) + .ply segmentado (rama HBIM) · §6.4" />
      </div>

      <ul className="pp-leyenda">
        <li className="pp-l-captura">Captura / publicación</li>
        <li className="pp-l-sfm">SfM / reconstrucción</li>
        <li className="pp-l-impl">Implementado y validado</li>
        <li className="pp-l-salida">Output / descarga</li>
        <li className="pp-l-concepto">Propuesta conceptual</li>
      </ul>
    </div>
  );
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
        <h2 className="pz-title">Problema y propuesta</h2>
        <p className="pz-pitch">
          El patrimonio arquitectónico argentino se sigue documentando con fotografías y planos
          CAD: costoso, difícil de reproducir con fidelidad ante una intervención futura y parcial
          en geometría y materialidad. No existe un archivo digital nacional que deje asentado el
          estado actual de las obras.
        </p>
        <div className="pz-pitch-solucion">
          <span className="pz-pitch-tag">La propuesta</span>
          <p>
            Las técnicas de visión computacional —SfM, NeRF y 3DGS— reconstruyen edificios
            completos en 3D desde fotos o video, sin escáner. Su aplicación al patrimonio argentino
            sigue inexplorada y no hay criterios locales para elegir entre ellas. Esta tesis las
            compara sobre tres obras reales y propone un pipeline reproducible con software libre.
          </p>
        </div>
        <p className="pz-pitch-pregunta">
          <strong>Pregunta de investigación:</strong> ¿cuál de estas técnicas es la más adecuada
          —y bajo qué criterios— para documentar patrimonio argentino?
        </p>
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
        <div className="pz-cols-3 pz-cols-tecnicas">
          <div className="pz-card pz-card-tecnica">
            <span className="pz-card-tag" style={{ color: SFM }}>SfM + MVS</span>
            <h3>Fotogrametría clásica</h3>
            <DiagramaSfM />
            <ol className="pz-pasos">
              <li>Detecta <strong>keypoints</strong> en cada foto con descriptores SIFT/SURF.</li>
              <li>Empareja correspondencias entre pares y estima la <strong>pose de cada cámara</strong> con RANSAC.</li>
              <li>Triangula esos puntos y corrige todo junto con <strong>bundle adjustment</strong>.</li>
              <li>MVS densifica por correlación fotométrica entre vistas vecinas.</li>
            </ol>
            <p className="pz-salida"><span>Salida</span> geometría explícita: nube densa y malla con topología real.</p>
          </div>
          <div className="pz-card pz-card-tecnica">
            <span className="pz-card-tag" style={{ color: NERF }}>NeRF</span>
            <h3>Campo de radiancia neuronal</h3>
            <DiagramaNeRF />
            <ol className="pz-pasos">
              <li>Parte de las poses de cámara que resolvió SfM.</li>
              <li>Lanza <strong>un rayo por píxel</strong> y muestrea puntos 3D a lo largo del rayo.</li>
              <li>Un <strong>MLP</strong> predice color y densidad en cada punto según posición y dirección de vista.</li>
              <li>Integra el rayo, compara con el píxel real y retropropaga el error, millones de veces.</li>
            </ol>
            <p className="pz-salida"><span>Salida</span> los pesos de una red: la escena solo existe al renderizarla.</p>
          </div>
          <div className="pz-card pz-card-tecnica">
            <span className="pz-card-tag" style={{ color: GS }}>3DGS</span>
            <h3>Gaussian Splatting</h3>
            <DiagramaGS />
            <ol className="pz-pasos">
              <li>Inicializa <strong>una gaussiana por punto</strong> de la nube dispersa de SfM.</li>
              <li>Cada una lleva posición, covarianza, opacidad y color en armónicos esféricos.</li>
              <li>Un <strong>rasterizador diferenciable</strong> las proyecta al plano de imagen y mide el error.</li>
              <li>En cada iteración <strong>clona, divide y poda</strong> gaussianas donde falta o sobra detalle.</li>
            </ol>
            <p className="pz-salida"><span>Salida</span> millones de primitivas explícitas que se renderizan en tiempo real.</p>
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
        <h2 className="pz-title">SfM, Nerfacto y Splatfacto, en los tres casos</h2>
        <div className="pz-render-gallery">
          <div className="pz-render-gallery-col">
            <h3>Los Paraguas</h3>
            <div className="pz-render-compare pz-render-compare-stacked">
              <div>
                <img src={`${W}paraguas-sfm-render.gif`} alt="Nube de puntos SfM de Los Paraguas" />
                <span>SfM</span>
              </div>
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
                <img src={`${W}templete-sfm-render.gif`} alt="Nube de puntos SfM de Templete Central" />
                <span>SfM</span>
              </div>
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
                <img src={`${W}panteon-sfm-render.gif`} alt="Nube de puntos SfM de Panteón Asociación Catalana" />
                <span>SfM</span>
              </div>
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
          <h2 className="pz-title">El preprocesamiento perjudica la reconstrucción</h2>
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
        <div className="pz-split-media pz-split-media-apilada">
          <figure>
            <img src={`${W}preproc-distractores.jpg`} alt="Fotograma original a la izquierda y el mismo fotograma con las personas eliminadas a la derecha" />
            <figcaption>1 · Distractores: original (izq.) y con las personas borradas por YOLOv8-seg + LaMa (der.).</figcaption>
          </figure>
          <figure>
            <img src={`${W}preproc-mascara.jpg`} alt="Fotograma original, máscara de entrenamiento y edificio aislado del fondo" />
            <figcaption>2 · Fondo: original, máscara de entrenamiento y edificio aislado.</figcaption>
          </figure>
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
        <div className="pz-split-media pz-split-media-apilada">
          <img src={`${A}cap5-07-psnr-vs-complejidad.png`} alt="PSNR vs. nivel de complejidad geométrica" />
          <figure>
            <img src={`${W}panteon-nerf-vs-splat.jpg`} alt="Panteón Asociación Catalana: render de Nerfacto junto al render de Splatfacto" />
            <figcaption>Panteón, misma vista: Nerfacto degenera en floaters (izq.); Splatfacto sostiene la geometría (der.).</figcaption>
          </figure>
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
        <div className="pz-split-media pz-split-media-apilada">
          <img src={`${A}cap5-hybrid-cross-camera-matching-chart.png`} alt="Calidad de matching por tipo de par de dispositivos" />
          <figure>
            <div className="pz-par">
              <img src={`${W}hibrido-componente-a.png`} alt="Primer componente reconstruido del dataset híbrido" />
              <img src={`${W}hibrido-componente-b.png`} alt="Segundo componente reconstruido del dataset híbrido" />
            </div>
            <figcaption>El fallo, a la vista: del mismo dataset híbrido salen dos componentes separados que nunca llegan a alinearse.</figcaption>
          </figure>
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
            title="Archivo digital — Los Paraguas, las tres representaciones"
            src="/modelado?site=paraguas&embed=1"
          />
        </div>
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
            <li>Ajusta bien donde la geometría es simple (Los Paraguas: 0,004 unidades SfM de distancia mediana a la nube) y se despega un orden de magnitud en la ornamentación (Panteón: 0,058; p95 0,29).</li>
            <li>No es una medida de precisión: se compara contra la misma nube que se usó para ajustar. Dice que el ajuste cerró, no que el modelo sea fiel al edificio.</li>
          </ul>
          <Source>Capítulo 6, sección 6.3.4 y Tabla 6.4</Source>
        </div>
        <div className="pz-split-media pz-split-media-apilada">
          {[
            ["paraguas", "Los Paraguas"],
            ["templete", "Templete Central"],
            ["panteon", "Panteón Asoc. Catalana"],
          ].map(([id, nombre]) => (
            <figure key={id}>
              <img src={`${W}${id}-reconstruccion-ia.png`} alt={`Modelo reconstruido por el agente de IA: ${nombre}`} />
              <figcaption>{nombre}</figcaption>
            </figure>
          ))}
        </div>
      </div>
    ),
  },
  {
    id: "recorrido",
    render: () => (
      <div className="pz-slide">
        <Kicker>Pipeline definitivo · Capítulo 6</Kicker>
        <h2 className="pz-title">Pipeline</h2>
        <div className="pz-recorrido">
          <div className="pz-recorrido-tronco">
            <Nodo n="1" archivo="pipeline-1-dataset.jpg" titulo="Dataset"
                  pie="1232 fotogramas de un vuelo con DJI Neo 2" />
            <Nodo n="2" archivo="pipeline-2-sfm.gif" titulo="SfM"
                  pie="Poses de cámara y geometría de la escena" />
          </div>

          <div className="pz-recorrido-ramas">
            <div className="pz-rama">
              <span className="pz-rama-tag">Rama 1 · hacia BIM</span>
              <div className="pz-rama-nodos">
                <Nodo n="3" archivo="pipeline-3-nube.jpg" titulo="Nube densa"
                      pie="La geometría, punto a punto" />
                <Nodo n="4" archivo="pipeline-5-segmentacion.jpg" titulo="Segmentación"
                      pie="Cada parte etiquetada por clase" />
                <Nodo n="5" archivo="pipeline-6-modelo.jpg" titulo="Modelo 3D"
                      pie="Geometría paramétrica, lista para Revit" />
              </div>
            </div>

            <div className="pz-rama">
              <span className="pz-rama-tag">Rama 2 · escena navegable</span>
              <div className="pz-rama-nodos">
                <Nodo n="6" archivo="pipeline-4-splat.gif" titulo="Gaussian Splatting"
                      pie="La escena, en .splat" />
                <span className="pz-rama-linea" aria-hidden="true" />
              </div>
            </div>
          </div>

          <div className="pz-recorrido-convergencia">
            <Nodo n="7" archivo="pipeline-7-archivo.jpg" titulo="Archivo digital"
                  pie="Modelo, nube y splat: los tres descargables" />
          </div>
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
        <DiagramaPipeline />
        <p className="pz-footnote">
          Captura con un único dispositivo, sin preprocesamiento, con verificación binaria de SfM.
          A partir de ahí, una ruta orientada a la publicación web con Gaussian Splatting, y otra
          al procesamiento con SfM para la integración con BIM.
        </p>
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
      </div>
    ),
  },
  {
    id: "archivo-cierre",
    render: () => (
      <div className="pz-slide pz-slide-center">
        <Kicker>El archivo digital · Capítulo 6</Kicker>
        <h2 className="pz-title">Tres obras, un archivo que empieza</h2>
        <a
          className="pz-cierre-archivo"
          href="https://thesis-3d-reconstruction.vercel.app/archivo-digital"
          target="_blank"
          rel="noopener noreferrer"
        >
          {[
            ["paraguas", "Los Paraguas"],
            ["templete-central", "Templete Central"],
            ["panteon", "Panteón Asoc. Catalana"],
          ].map(([id, nombre]) => (
            <figure key={id}>
              <img src={`/archivo-digital/${id}/preview.gif`} alt={`Modelo reconstruido de ${nombre}`} />
              <figcaption>{nombre}</figcaption>
            </figure>
          ))}
          <span className="pz-cierre-archivo-pie">
            Nube de puntos, modelo 3D y splat, descargables en el archivo digital →
          </span>
        </a>
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
