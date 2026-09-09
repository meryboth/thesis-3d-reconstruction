import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { PLYLoader } from "three/addons/loaders/PLYLoader.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

// Visor comparativo de las 3 representaciones de un mismo caso de estudio:
// nube de puntos (SfM), modelo geometrico (reconstruccion asistida por IA,
// Cap.6 seccion 6.3.4) y gaussian splatting (embebido via iframe, reusa el
// visor SuperSplat ya publicado en /archivo-digital/). Es el visor unico al
// que apuntan las 3 cards del Archivo Digital (/archivo-digital -> /modelado
// ?site=<id>): los 3 sitios ya tienen las 4 capas completas.
// El panel tambien deja descargar los archivos de cada capa.
const SITES = [
  {
    id: "paraguas",
    label: "Los Paraguas",
    ply: "/modelado/paraguas/nube-densa.ply",
    // export crudo de RealityScan de este proyecto: X=x_COLMAP, altura=-y_COLMAP
    // (hay que invertir Y para que quede arriba) -- ver README en
    // 07-modelado/01-paraguas-vicentelopez/. No asumir que vale para otros
    // sitios: cada proyecto de RealityScan se alineo/nivelo por separado.
    plyAxisMode: "flipY",
    glb: "/modelado/paraguas/modelo.glb",
    splatFrame: "/archivo-digital/paraguas/editado.html",
    // archivo del splat para descarga (el iframe de arriba solo lo muestra)
    splatFile: "/archivo-digital/paraguas/splat-editado.ply",
    splatCompact: "/archivo-digital/paraguas/splat.splat",
    // nube coloreada por clase (experimento de segmentacion, Cap.6 6.3.2/6.3.3):
    // /segmentador ya la usa, generada por poc_segmentation_multi_site.py.
    // Convencion propia (Z-arriba, sin relacion con plyAxisMode de arriba).
    segPly: "/segmentacion/los-paraguas-dron.ply",
  },
  {
    id: "templete-central",
    label: "Templete Central",
    ply: "/modelado/templete-central/nube-densa.ply",
    // en este proyecto el eje "altura" real es Z (rango angosto -0.5 a 4.8,
    // ~la altura del edificio en metros) -- X e Y son ambos horizontales y
    // muy anchos (~igual de amplios), no Y=altura como en Los Paraguas.
    // rotateXNeg90 = Rx(-90): (x,y,z) -> (x,z,-y), pone Z como el nuevo Y.
    plyAxisMode: "rotateXNeg90",
    glb: "/modelado/templete-central/modelo.glb",
    splatFrame: "/archivo-digital/templete-central/editado.html",
    splatFile: "/archivo-digital/templete-central/splat-editado-v2.ply",
    segPly: "/segmentacion/templete-central-dji.ply",
  },
  {
    id: "panteon",
    label: "Panteón Asociación Catalana",
    ply: "/modelado/panteon/nube-densa.ply",
    // igual que Templete Central: Z sale como la altura real en este export
    // (rango mas angosto que X/Y) -- se confirma visualmente al cargar.
    plyAxisMode: "rotateXNeg90",
    glb: "/modelado/panteon/modelo.glb",
    splatFrame: "/archivo-digital/panteon/editado.html",
    splatFile: "/archivo-digital/panteon/splat-editado.ply",
    segPly: "/segmentacion/panteon-asociacion-catalana-dji.ply",
  },
];

const LAYERS = [
  { id: "nube", label: "Nube de puntos (SfM)" },
  { id: "segmentada", label: "Nube segmentada" },
  { id: "modelo", label: "Modelo 3D (IA asistida)" },
  { id: "splat", label: "Gaussian Splatting" },
];

function ThreeCanvas({ mode, site }) {
  const mountRef = useRef(null);
  const [status, setStatus] = useState("Cargando...");

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0b0b0d);

    const camera = new THREE.PerspectiveCamera(60, mount.clientWidth / mount.clientHeight, 0.01, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    mount.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    scene.add(new THREE.GridHelper(20, 20, 0x333333, 0x1c1c1c));
    scene.add(new THREE.HemisphereLight(0xffffff, 0x222222, 1.2));
    const sun = new THREE.DirectionalLight(0xffffff, 1.5);
    sun.position.set(5, 10, 6);
    scene.add(sun);

    let disposed = false;

    function frame(object, radiusScale = 1.6) {
      const box = new THREE.Box3().setFromObject(object);
      const sphere = box.getBoundingSphere(new THREE.Sphere());
      const r = sphere.radius || 1;
      camera.position.set(r * radiusScale * 0.6, r * radiusScale * 0.55, r * radiusScale * 0.6);
      controls.target.copy(sphere.center);
      controls.update();
    }

    // Centro y extensión por eje robustos por percentiles en vez de min/max
    // real -- una nube de fotogrametria densa suele traer puntos de terreno
    // muy alejados (outliers) que si se usan tal cual inflan el encuadre y
    // dejan el objeto principal como un punto perdido en el centro. Se usa
    // un percentil bastante mas ajustado (15-85) que para el bounding box
    // general porque el edificio (denso) domina la distribucion frente al
    // terreno disperso alrededor. Devuelve la extension POR EJE (no un
    // radio isotropico) para que la camara respete la proporcion real del
    // objeto -- un edificio bajo y ancho necesita una elevacion baja, no la
    // misma que un objeto cubico.
    function robustCenterAndExtent(positionAttr, pLow = 15, pHigh = 85) {
      const n = positionAttr.count;
      const xs = new Float32Array(n);
      const ys = new Float32Array(n);
      const zs = new Float32Array(n);
      for (let i = 0; i < n; i++) {
        xs[i] = positionAttr.getX(i);
        ys[i] = positionAttr.getY(i);
        zs[i] = positionAttr.getZ(i);
      }
      const pct = (arr, p) => {
        const sorted = Array.from(arr).sort((a, b) => a - b);
        return sorted[Math.floor((sorted.length - 1) * (p / 100))];
      };
      const lo = new THREE.Vector3(pct(xs, pLow), pct(ys, pLow), pct(zs, pLow));
      const hi = new THREE.Vector3(pct(xs, pHigh), pct(ys, pHigh), pct(zs, pHigh));
      const center = lo.clone().add(hi).multiplyScalar(0.5);
      const extent = hi.clone().sub(lo).max(new THREE.Vector3(0.02, 0.02, 0.02));
      return { center, extent };
    }

    if (mode === "nube") {
      setStatus("Cargando nube de puntos...");
      new PLYLoader().load(
        site.ply,
        (geometry) => {
          if (disposed) return;
          // cada proyecto de RealityScan puede quedar orientado distinto segun
          // como se alineo/nivelo -- ver site.plyAxisMode (definido junto a
          // cada entrada de SITES, con la razon documentada ahi).
          if (site.plyAxisMode === "flipY") geometry.scale(1, -1, 1);
          else if (site.plyAxisMode === "rotateXNeg90") geometry.rotateX(-Math.PI / 2);
          const { center, extent } = robustCenterAndExtent(geometry.attributes.position);
          geometry.translate(-center.x, -center.y, -center.z);
          // tamaño de punto proporcional a la escala real de la nube en vez
          // de un valor fijo -- una nube grande (~20 unidades) con puntos de
          // 0.02 se ve dispersa/pobre comparada con el visor denso de
          // RealityScan; escalando con la extensión se ve consistentemente
          // densa sin importar la escala de cada sitio.
          const pointSize = Math.max(extent.length() * 0.0022, 0.01);
          const material = new THREE.PointsMaterial({ size: pointSize, vertexColors: true, sizeAttenuation: true });
          const points = new THREE.Points(geometry, material);
          scene.add(points);
          setStatus(null);
          // vista 3/4 elevada, proporcional al ancho/alto reales del objeto
          // (no una elevacion fija que resulta casi cenital en edificios
          // bajos y anchos como este)
          camera.position.set(
            extent.x * 1.1,
            extent.y * 1.3 + Math.max(extent.x, extent.z) * 0.15,
            extent.z * 1.1
          );
          controls.target.set(0, 0, 0);
          controls.update();
        },
        undefined,
        () => !disposed && setStatus("Error cargando la nube de puntos.")
      );
    } else if (mode === "segmentada") {
      setStatus("Cargando nube segmentada...");
      new PLYLoader().load(
        site.segPly,
        (geometry) => {
          if (disposed) return;
          // la nube de /segmentacion/ (poc_segmentation_multi_site.py) viene
          // siempre en convencion Z-arriba, sin relacion con plyAxisMode
          // (que es especifico de cada export crudo de RealityScan) -- ver
          // el mismo ajuste en PointCloudSegmentor.jsx.
          geometry.rotateX(-Math.PI / 2);
          const { center, extent } = robustCenterAndExtent(geometry.attributes.position);
          geometry.translate(-center.x, -center.y, -center.z);
          const pointSize = Math.max(extent.length() * 0.0022, 0.01);
          // color por clase ya viene en el archivo (cubierta/columna/baranda/piso)
          const material = new THREE.PointsMaterial({ size: pointSize, vertexColors: true, sizeAttenuation: true });
          const points = new THREE.Points(geometry, material);
          scene.add(points);
          setStatus(null);
          camera.position.set(
            extent.x * 1.1,
            extent.y * 1.3 + Math.max(extent.x, extent.z) * 0.15,
            extent.z * 1.1
          );
          controls.target.set(0, 0, 0);
          controls.update();
        },
        undefined,
        () => !disposed && setStatus("Error cargando la nube segmentada.")
      );
    } else if (mode === "modelo") {
      setStatus("Cargando modelo 3D...");
      new GLTFLoader().load(
        site.glb,
        (gltf) => {
          if (disposed) return;
          const model = gltf.scene;
          model.traverse((o) => {
            if (o.isMesh) {
              o.material = new THREE.MeshStandardMaterial({
                color: 0xb3ac96,
                roughness: 0.85,
                metalness: 0,
                side: THREE.DoubleSide,
              });
            }
          });
          scene.add(model);
          setStatus(null);
          frame(model, 2.4);
        },
        undefined,
        () => !disposed && setStatus("Error cargando el modelo.")
      );
    }

    function handleResize() {
      camera.aspect = mount.clientWidth / mount.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(mount.clientWidth, mount.clientHeight);
    }
    window.addEventListener("resize", handleResize);

    let raf;
    function animate() {
      raf = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }
    animate();

    return () => {
      disposed = true;
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", handleResize);
      controls.dispose();
      renderer.dispose();
      scene.traverse((o) => {
        if (o.geometry) o.geometry.dispose();
        if (o.material) (Array.isArray(o.material) ? o.material : [o.material]).forEach((m) => m.dispose());
      });
      if (mount.contains(renderer.domElement)) mount.removeChild(renderer.domElement);
    };
  }, [mode, site]);

  return (
    <div style={{ position: "absolute", inset: 0 }}>
      <div ref={mountRef} style={{ position: "absolute", inset: 0, cursor: "grab" }} />
      {status && (
        <p style={{ position: "absolute", top: 16, left: "50%", transform: "translateX(-50%)", fontSize: 12, color: "#f39c12" }}>
          {status}
        </p>
      )}
    </div>
  );
}

function getInitialSiteId() {
  const requested = new URLSearchParams(window.location.search).get("site");
  return SITES.some((s) => s.id === requested) ? requested : SITES[0].id;
}

// Archivos que el usuario puede bajarse de cada sitio. El peso se consulta con
// un HEAD al montar, para no hardcodear numeros que quedan viejos cuando se
// regenera un export.
function descargasDe(site) {
  return [
    { id: "nube", label: "Nube de puntos densa (SfM)", url: site.ply, ext: "ply" },
    { id: "segmentada", label: "Nube de puntos segmentada", url: site.segPly, ext: "ply" },
    { id: "modelo", label: "Modelo 3D (IA asistida)", url: site.glb, ext: "glb" },
    { id: "splat", label: "Gaussian Splatting", url: site.splatFile, ext: "ply" },
    { id: "splatCompact", label: "Gaussian Splatting (compacto)", url: site.splatCompact, ext: "splat" },
  ].filter((d) => !!d.url);
}

function formatearPeso(bytes) {
  if (!bytes && bytes !== 0) return "";
  return bytes >= 1e6 ? `${(bytes / 1e6).toFixed(1)} MB` : `${Math.round(bytes / 1e3)} kB`;
}

export default function ModeladoViewer() {
  const [siteId, setSiteId] = useState(getInitialSiteId);
  const site = SITES.find((s) => s.id === siteId);
  const [layer, setLayer] = useState(site.ply ? "nube" : "splat");
  const [pesos, setPesos] = useState({});

  // peso real de cada descarga, via HEAD (no bloquea el visor si falla)
  useEffect(() => {
    let vigente = true;
    const archivos = descargasDe(site);
    Promise.all(
      archivos.map((d) =>
        fetch(d.url, { method: "HEAD" })
          .then((r) => [d.url, Number(r.headers.get("content-length")) || null])
          .catch(() => [d.url, null]),
      ),
    ).then((pares) => {
      if (vigente) setPesos(Object.fromEntries(pares));
    });
    return () => {
      vigente = false;
    };
  }, [site]);

  useEffect(() => {
    // al cambiar de sitio, si la capa activa no existe para el sitio nuevo
    // (nube/segmentada/modelo todavia no publicados), caemos a la unica que si existe
    if (
      (layer === "nube" && !site.ply) ||
      (layer === "segmentada" && !site.segPly) ||
      (layer === "modelo" && !site.glb)
    ) {
      setLayer("splat");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [siteId]);

  return (
    <div style={{ position: "fixed", inset: 0, background: "#0b0b0d", color: "#eee", fontFamily: "system-ui, sans-serif" }}>
      <div style={{ position: "absolute", inset: 0 }}>
        {layer === "splat" ? (
          <iframe
            title={`Gaussian Splatting — ${site.label}`}
            src={site.splatFrame}
            style={{ position: "absolute", inset: 0, width: "100%", height: "100%", border: "none" }}
            loading="lazy"
          />
        ) : (
          <ThreeCanvas mode={layer} site={site} />
        )}
      </div>

      <div
        style={{
          position: "absolute",
          top: 16,
          left: 16,
          background: "rgba(20,20,22,0.85)",
          padding: "12px 16px",
          borderRadius: 8,
          maxWidth: 320,
        }}
      >
        <a
          href="/"
          style={{ display: "inline-flex", alignItems: "center", gap: 4, fontSize: 12, color: "#9ecbff", textDecoration: "none", marginBottom: 8 }}
        >
          ← Volver a la tesis
        </a>
        <h1 style={{ fontSize: 15, margin: "0 0 8px" }}>Modelado — comparativa de representaciones</h1>
        <p style={{ fontSize: 12, opacity: 0.75, margin: "0 0 10px", lineHeight: 1.4 }}>
          Un mismo caso de estudio, tres formas de verlo: la nube de puntos que produce SfM, el modelo
          geométrico ajustado por un agente de IA (Capítulo 6, sección 6.3.4) y el resultado de Gaussian
          Splatting. Los 3 sitios ya tienen las tres capas completas.
        </p>

        <select
          value={siteId}
          onChange={(e) => setSiteId(e.target.value)}
          style={{ width: "100%", padding: "4px 6px", marginBottom: 8, background: "#1a1a1c", color: "#eee", border: "1px solid #333", borderRadius: 4 }}
        >
          {SITES.map((s) => (
            <option key={s.id} value={s.id}>
              {s.label}
            </option>
          ))}
        </select>

        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {LAYERS.map((l) => {
            const active = layer === l.id;
            const available =
              l.id === "nube"
                ? !!site.ply
                : l.id === "segmentada"
                ? !!site.segPly
                : l.id === "modelo"
                ? !!site.glb
                : true;
            return (
              <button
                key={l.id}
                onClick={() => available && setLayer(l.id)}
                disabled={!available}
                title={available ? undefined : "Todavía no disponible para este sitio"}
                style={{
                  padding: "8px 10px",
                  fontSize: 12,
                  textAlign: "left",
                  background: active ? "#2c5282" : "#1a1a1c",
                  color: available ? "#eee" : "#555",
                  border: `1px solid ${active ? "#4a7ab5" : "#333"}`,
                  borderRadius: 4,
                  cursor: available ? "pointer" : "not-allowed",
                  fontWeight: active ? 700 : 400,
                }}
              >
                {l.label}
                {!available && " (próximamente)"}
              </button>
            );
          })}
        </div>

        <div style={{ marginTop: 14, borderTop: "1px solid #333", paddingTop: 10 }}>
          <h2 style={{ fontSize: 12, margin: "0 0 2px", letterSpacing: 0.3 }}>Descargar archivos</h2>
          <p style={{ fontSize: 11, opacity: 0.6, margin: "0 0 8px", lineHeight: 1.35 }}>
            Los outputs de este caso de estudio, para abrir en CloudCompare, Blender, Revit o
            SuperSplat.
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
            {descargasDe(site).map((d) => (
              <a
                key={d.id}
                href={d.url}
                download
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "baseline",
                  gap: 8,
                  padding: "6px 8px",
                  fontSize: 11.5,
                  color: "#9ecbff",
                  background: "#161618",
                  border: "1px solid #2a2a2e",
                  borderRadius: 4,
                  textDecoration: "none",
                }}
              >
                <span>
                  ↓ {d.label} <span style={{ opacity: 0.5 }}>.{d.ext}</span>
                </span>
                <span style={{ opacity: 0.55, whiteSpace: "nowrap" }}>
                  {formatearPeso(pesos[d.url])}
                </span>
              </a>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
