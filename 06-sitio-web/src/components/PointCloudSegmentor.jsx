import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { PLYLoader } from "three/addons/loaders/PLYLoader.js";

// Visor de nube de puntos coloreada por clase de segmentacion, con edicion
// manual: modo seleccion por rectangulo (arrastre) + eliminar + deshacer +
// exportar el resultado editado como .ply.

const SITES = [
  { id: "templete-central-dji", label: "Templete Central" },
  { id: "los-paraguas-dron", label: "Los Paraguas" },
  { id: "panteon-asociacion-espanola-dji", label: "Panteón Asociación Española" },
];

// sitios que ya tienen el .ply -vlm generado (poc_segmentation_vlm.py) --
// para el resto el metodo VLM queda deshabilitado en el selector en vez de
// intentar cargar un archivo que no existe.
const VLM_AVAILABLE = new Set(["templete-central-dji", "los-paraguas-dron", "panteon-asociacion-espanola-dji"]);

const METHODS = [
  { id: "geometrica", label: "Geométrica (reglas fijas)" },
  { id: "vlm", label: "Asistida por VLM (Moondream)" },
];

function plyPath(siteId, method) {
  return method === "vlm" ? `/segmentacion/${siteId}-vlm.ply` : `/segmentacion/${siteId}.ply`;
}

const LEGEND = [
  { label: "Cubierta", color: "#e74c3c" },
  { label: "Columna (estructural)", color: "#27ae60" },
  { label: "Baranda / pared no estructural", color: "#f1c40f" },
  { label: "Piso / base", color: "#2980b9" },
];

const HIGHLIGHT_COLOR = new THREE.Color(0xffee58);

export default function PointCloudSegmentor() {
  const mountRef = useRef(null);
  const [site, setSite] = useState(SITES[0].id);
  const [method, setMethod] = useState("geometrica");
  const [status, setStatus] = useState("Cargando...");
  const [pointCount, setPointCount] = useState(null);
  const [selectionMode, setSelectionMode] = useState(false);
  const [selectedCount, setSelectedCount] = useState(0);
  const [selectionRect, setSelectionRect] = useState(null);
  const [canUndo, setCanUndo] = useState(false);
  const [saveStatus, setSaveStatus] = useState(null); // null | "saving" | "saved" | "error"

  const actionsRef = useRef({});
  const controlsRef = useRef(null);
  const selectionModeRef = useRef(false);

  useEffect(() => {
    selectionModeRef.current = selectionMode;
    if (controlsRef.current) controlsRef.current.enabled = !selectionMode;
  }, [selectionMode]);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0b0b0d);

    const camera = new THREE.PerspectiveCamera(60, mount.clientWidth / mount.clientHeight, 0.01, 1000);
    camera.position.set(15, 15, 15);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(mount.clientWidth, mount.clientHeight);
    mount.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.enabled = !selectionModeRef.current;
    controlsRef.current = controls;

    const grid = new THREE.GridHelper(60, 30, 0x333333, 0x1c1c1c);
    scene.add(grid);
    const axes = new THREE.AxesHelper(3);
    scene.add(axes);

    let points = null;
    // fuente de verdad de la geometria editada -- sobrevive a cada
    // seleccion/eliminacion, independiente de los BufferAttributes de three
    // (que se reconstruyen a partir de esto en cada cambio).
    let basePositions = null;
    let baseColors = null;
    let selected = new Set();
    let history = [];
    let disposed = false;

    function applySelectionHighlight() {
      if (!points) return;
      const colorAttr = points.geometry.attributes.color;
      const display = baseColors.slice();
      selected.forEach((i) => {
        display[i * 3] = HIGHLIGHT_COLOR.r;
        display[i * 3 + 1] = HIGHLIGHT_COLOR.g;
        display[i * 3 + 2] = HIGHLIGHT_COLOR.b;
      });
      colorAttr.array.set(display);
      colorAttr.needsUpdate = true;
      setSelectedCount(selected.size);
    }

    function rebuildGeometry() {
      const geometry = points.geometry;
      geometry.setAttribute("position", new THREE.BufferAttribute(basePositions, 3));
      geometry.setAttribute("color", new THREE.BufferAttribute(baseColors.slice(), 3));
      geometry.computeBoundingSphere();
      setPointCount(basePositions.length / 3);
      applySelectionHighlight();
    }

    actionsRef.current.clearSelection = () => {
      if (!points || selected.size === 0) return;
      selected.clear();
      applySelectionHighlight();
    };

    actionsRef.current.deleteSelected = () => {
      if (!points || selected.size === 0) return;
      history.push({ positions: basePositions, colors: baseColors });
      const n = basePositions.length / 3;
      const newPositions = new Float32Array((n - selected.size) * 3);
      const newColors = new Float32Array((n - selected.size) * 3);
      let w = 0;
      for (let i = 0; i < n; i++) {
        if (selected.has(i)) continue;
        newPositions[w * 3] = basePositions[i * 3];
        newPositions[w * 3 + 1] = basePositions[i * 3 + 1];
        newPositions[w * 3 + 2] = basePositions[i * 3 + 2];
        newColors[w * 3] = baseColors[i * 3];
        newColors[w * 3 + 1] = baseColors[i * 3 + 1];
        newColors[w * 3 + 2] = baseColors[i * 3 + 2];
        w++;
      }
      basePositions = newPositions;
      baseColors = newColors;
      selected.clear();
      rebuildGeometry();
      setCanUndo(true);
    };

    actionsRef.current.undo = () => {
      if (!points || history.length === 0) return;
      const prev = history.pop();
      basePositions = prev.positions;
      baseColors = prev.colors;
      selected.clear();
      rebuildGeometry();
      setCanUndo(history.length > 0);
    };

    function buildPlyBuffer() {
      const n = basePositions.length / 3;
      const header =
        "ply\nformat binary_little_endian 1.0\n" +
        `element vertex ${n}\n` +
        "property float x\nproperty float y\nproperty float z\n" +
        "property uchar red\nproperty uchar green\nproperty uchar blue\n" +
        "end_header\n";
      const headerBytes = new TextEncoder().encode(header);
      const recordSize = 15; // 3 floats (4 bytes) + 3 uchar
      const buffer = new ArrayBuffer(headerBytes.length + n * recordSize);
      new Uint8Array(buffer).set(headerBytes, 0);
      const view = new DataView(buffer, headerBytes.length);
      for (let i = 0; i < n; i++) {
        const off = i * recordSize;
        const x = basePositions[i * 3];
        const y = basePositions[i * 3 + 1];
        const z = basePositions[i * 3 + 2];
        // el visor convierte Z-arriba (formato de origen) a Y-arriba
        // (Three.js) con rotateX(-90grados) al cargar -- aca se deshace esa
        // rotacion (equivalente a +90grados) para que el .ply exportado
        // quede otra vez en Z-arriba, listo para recargarse sin duplicar la
        // rotacion (que dejaria el modelo mal orientado la proxima vez).
        view.setFloat32(off, x, true);
        view.setFloat32(off + 4, -z, true);
        view.setFloat32(off + 8, y, true);
        view.setUint8(off + 12, Math.round(baseColors[i * 3] * 255));
        view.setUint8(off + 13, Math.round(baseColors[i * 3 + 1] * 255));
        view.setUint8(off + 14, Math.round(baseColors[i * 3 + 2] * 255));
      }
      return buffer;
    }

    actionsRef.current.exportPly = () => {
      if (!points) return;
      const blob = new Blob([buildPlyBuffer()], { type: "application/octet-stream" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${site}${method === "vlm" ? "-vlm" : ""}-editado.ply`;
      a.click();
      URL.revokeObjectURL(url);
    };

    actionsRef.current.saveToServer = async () => {
      if (!points) return;
      setSaveStatus("saving");
      try {
        const fileId = method === "vlm" ? `${site}-vlm` : site;
        const res = await fetch(`/api/segmentacion/${fileId}.ply`, {
          method: "PUT",
          body: buildPlyBuffer(),
        });
        setSaveStatus(res.ok ? "saved" : "error");
      } catch (err) {
        console.error(err);
        setSaveStatus("error");
      }
    };

    const plyFile = plyPath(site, method);
    setStatus("Cargando nube de puntos...");
    setPointCount(null);
    setSelectedCount(0);
    setCanUndo(false);
    setSaveStatus(null);
    history = [];

    const loader = new PLYLoader();
    loader.load(
      plyFile,
      (geometry) => {
        if (disposed) return;
        // la nube viene en convencion Z-arriba (COLMAP/RealityScan); Three.js
        // asume Y-arriba -- sin este ajuste el edificio aparece "acostado".
        geometry.rotateX(-Math.PI / 2);

        // centrar X/Z en el medio de la caja, pero Y (altura) en el nivel del
        // piso -- no en el punto medio del rango total -- para que la grilla
        // (en Y=0) quede debajo del edificio en vez de atravesarlo. El piso
        // real se aproxima con un percentil bajo de Y (robusto a un par de
        // puntos sueltos por debajo del piso real).
        const pos = geometry.attributes.position;
        let minX = Infinity, maxX = -Infinity, minZ = Infinity, maxZ = -Infinity;
        const ys = new Float32Array(pos.count);
        for (let i = 0; i < pos.count; i++) {
          const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i);
          if (x < minX) minX = x;
          if (x > maxX) maxX = x;
          if (z < minZ) minZ = z;
          if (z > maxZ) maxZ = z;
          ys[i] = y;
        }
        ys.sort();
        const groundY = ys[Math.floor(ys.length * 0.02)]; // percentil 2 -- nivel del piso
        geometry.translate(-(minX + maxX) / 2, -groundY, -(minZ + maxZ) / 2);
        geometry.computeBoundingSphere();

        basePositions = geometry.attributes.position.array.slice();
        // PLYLoader entrega red/green/blue (uchar) como Uint8Array con
        // normalized:true (GL lo escala 0-255 -> 0-1 al renderizar); se
        // vuelca a Float32 0-1 explicito aca para que sea seguro reusar en
        // aritmetica (resaltado de seleccion, export) sin reimplementar esa
        // normalizacion en cada lugar -- BufferAttribute.getX/Y/Z ya la
        // aplica automaticamente segun el flag de origen.
        const colorAttr = geometry.attributes.color;
        if (colorAttr) {
          baseColors = new Float32Array(colorAttr.count * 3);
          for (let i = 0; i < colorAttr.count; i++) {
            baseColors[i * 3] = colorAttr.getX(i);
            baseColors[i * 3 + 1] = colorAttr.getY(i);
            baseColors[i * 3 + 2] = colorAttr.getZ(i);
          }
        } else {
          baseColors = new Float32Array(pos.count * 3).fill(1);
        }

        const material = new THREE.PointsMaterial({
          size: 0.035,
          vertexColors: true,
          sizeAttenuation: true,
        });
        points = new THREE.Points(geometry, material);
        scene.add(points);

        setStatus(null);
        rebuildGeometry();

        const radius = geometry.boundingSphere ? geometry.boundingSphere.radius : 10;
        // vista inicial cenital (predominantemente desde arriba, con un leve
        // desvio para conservar profundidad 3D en vez de una vista plana)
        camera.position.set(radius * 0.4, radius * 1.9, radius * 0.4);
        controls.target.set(0, 0, 0);
        controls.update();
      },
      undefined,
      (err) => {
        console.error(err);
        setStatus("Error cargando el archivo.");
      }
    );

    // ---- seleccion por rectangulo (arrastre) ----
    let dragging = false;
    let dragStart = { x: 0, y: 0 };

    function getLocalPos(evt) {
      const rect = renderer.domElement.getBoundingClientRect();
      return { x: evt.clientX - rect.left, y: evt.clientY - rect.top };
    }

    function onPointerDown(evt) {
      if (!selectionModeRef.current || !points || evt.button !== 0) return;
      dragging = true;
      dragStart = getLocalPos(evt);
      if (!evt.shiftKey) selected.clear();
      setSelectionRect({ x: dragStart.x, y: dragStart.y, w: 0, h: 0 });
    }

    function onPointerMove(evt) {
      if (!dragging) return;
      const p = getLocalPos(evt);
      setSelectionRect({
        x: Math.min(dragStart.x, p.x),
        y: Math.min(dragStart.y, p.y),
        w: Math.abs(p.x - dragStart.x),
        h: Math.abs(p.y - dragStart.y),
      });
    }

    function onPointerUp(evt) {
      if (!dragging) return;
      dragging = false;
      setSelectionRect(null);

      const p = getLocalPos(evt);
      const x0 = Math.min(dragStart.x, p.x), x1 = Math.max(dragStart.x, p.x);
      const y0 = Math.min(dragStart.y, p.y), y1 = Math.max(dragStart.y, p.y);

      if (x1 - x0 < 3 && y1 - y0 < 3) {
        // click sin arrastre real -- no suma puntos, solo re-aplica el resaltado
        applySelectionHighlight();
        return;
      }

      const w = mount.clientWidth, h = mount.clientHeight;
      const posAttr = points.geometry.attributes.position;
      const v = new THREE.Vector3();
      camera.updateMatrixWorld();
      for (let i = 0; i < posAttr.count; i++) {
        v.set(posAttr.getX(i), posAttr.getY(i), posAttr.getZ(i));
        v.project(camera);
        if (v.z < -1 || v.z > 1) continue; // fuera del frustum (detras de camara, etc.)
        const sx = ((v.x + 1) / 2) * w;
        const sy = ((1 - v.y) / 2) * h;
        if (sx >= x0 && sx <= x1 && sy >= y0 && sy <= y1) selected.add(i);
      }
      applySelectionHighlight();
    }

    renderer.domElement.addEventListener("pointerdown", onPointerDown);
    window.addEventListener("pointermove", onPointerMove);
    window.addEventListener("pointerup", onPointerUp);

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
      renderer.domElement.removeEventListener("pointerdown", onPointerDown);
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("pointerup", onPointerUp);
      controls.dispose();
      renderer.dispose();
      if (points) {
        points.geometry.dispose();
        points.material.dispose();
      }
      if (mount.contains(renderer.domElement)) mount.removeChild(renderer.domElement);
    };
  }, [site, method]);

  return (
    <div style={{ position: "fixed", inset: 0, background: "#0b0b0d", color: "#eee", fontFamily: "system-ui, sans-serif" }}>
      <div
        ref={mountRef}
        style={{ position: "absolute", inset: 0, cursor: selectionMode ? "crosshair" : "grab" }}
      />

      {selectionRect && (
        <div
          style={{
            position: "absolute",
            left: selectionRect.x,
            top: selectionRect.y,
            width: selectionRect.w,
            height: selectionRect.h,
            border: "1px solid #ffee58",
            background: "rgba(255,238,88,0.15)",
            pointerEvents: "none",
          }}
        />
      )}

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
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 4,
            fontSize: 12,
            color: "#9ecbff",
            textDecoration: "none",
            marginBottom: 8,
          }}
        >
          ← Volver a la tesis
        </a>
        <h1 style={{ fontSize: 15, margin: "0 0 8px" }}>Segmentador de nube de puntos</h1>
        <p style={{ fontSize: 12, opacity: 0.75, margin: "0 0 10px", lineHeight: 1.4 }}>
          Segmentación por normales locales (verticalidad + altura) sobre la nube densa de SfM.
          El método "VLM" reclasifica columna vs. baranda con Moondream2 (vía ComfyUI) en vez de un
          umbral geométrico fijo — comparar con la versión geométrica. Permite marcar y eliminar
          puntos manualmente en ambos casos.
        </p>

        <select
          value={site}
          onChange={(e) => setSite(e.target.value)}
          style={{ width: "100%", padding: "4px 6px", marginBottom: 8, background: "#1a1a1c", color: "#eee", border: "1px solid #333", borderRadius: 4 }}
        >
          {SITES.map((s) => (
            <option key={s.id} value={s.id}>
              {s.label}
            </option>
          ))}
        </select>

        <div style={{ display: "flex", gap: 6, marginBottom: 10 }}>
          {METHODS.map((m) => {
            const disabled = m.id === "vlm" && !VLM_AVAILABLE.has(site);
            const active = method === m.id;
            return (
              <button
                key={m.id}
                onClick={() => !disabled && setMethod(m.id)}
                disabled={disabled}
                title={disabled ? "Todavía no se generó la versión VLM para este sitio" : ""}
                style={{
                  flex: 1,
                  padding: "6px 6px",
                  fontSize: 11,
                  lineHeight: 1.25,
                  background: active ? "#2c5282" : "#1a1a1c",
                  color: disabled ? "#555" : "#eee",
                  border: `1px solid ${active ? "#4a7ab5" : "#333"}`,
                  borderRadius: 4,
                  cursor: disabled ? "default" : "pointer",
                  fontWeight: active ? 700 : 400,
                }}
              >
                {m.label}
              </button>
            );
          })}
        </div>

        {status && <p style={{ fontSize: 12, color: "#f39c12" }}>{status}</p>}
        {pointCount != null && (
          <p style={{ fontSize: 12, opacity: 0.7, margin: "0 0 10px" }}>{pointCount.toLocaleString("es-AR")} puntos</p>
        )}

        <div style={{ marginBottom: 10, display: "flex", flexDirection: "column", gap: 4 }}>
          {LEGEND.map((l) => (
            <div key={l.label} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12 }}>
              <span style={{ width: 10, height: 10, borderRadius: "50%", background: l.color, display: "inline-block" }} />
              {l.label}
            </div>
          ))}
        </div>

        <hr style={{ border: "none", borderTop: "1px solid #333", margin: "10px 0" }} />

        <button
          onClick={() => setSelectionMode((m) => !m)}
          style={{
            width: "100%",
            padding: "6px 8px",
            marginBottom: 6,
            background: selectionMode ? "#f1c40f" : "#1a1a1c",
            color: selectionMode ? "#1a1a1c" : "#eee",
            border: "1px solid #333",
            borderRadius: 4,
            fontSize: 12,
            fontWeight: selectionMode ? 700 : 400,
            cursor: "pointer",
          }}
        >
          {selectionMode ? "Modo selección: ON" : "Activar modo selección"}
        </button>

        {selectionMode && (
          <p style={{ fontSize: 11, opacity: 0.6, margin: "0 0 8px", lineHeight: 1.4 }}>
            Arrastrá un rectángulo sobre los puntos a marcar (mantené Shift para sumar a la selección).
            La órbita de cámara queda desactivada mientras este modo esté activo.
          </p>
        )}

        <p style={{ fontSize: 12, opacity: 0.8, margin: "0 0 8px" }}>
          {selectedCount.toLocaleString("es-AR")} puntos seleccionados
        </p>

        <div style={{ display: "flex", gap: 6, marginBottom: 6 }}>
          <button onClick={() => actionsRef.current.clearSelection?.()} disabled={selectedCount === 0} style={buttonStyle(selectedCount === 0)}>
            Deseleccionar
          </button>
          <button onClick={() => actionsRef.current.deleteSelected?.()} disabled={selectedCount === 0} style={buttonStyle(selectedCount === 0)}>
            Eliminar
          </button>
        </div>

        <div style={{ display: "flex", gap: 6, marginBottom: 6 }}>
          <button onClick={() => actionsRef.current.undo?.()} disabled={!canUndo} style={buttonStyle(!canUndo)}>
            Deshacer
          </button>
          <button onClick={() => actionsRef.current.exportPly?.()} style={buttonStyle(false)}>
            Descargar .ply
          </button>
        </div>

        <button
          onClick={() => {
            setSaveStatus(null);
            actionsRef.current.saveToServer?.();
          }}
          disabled={saveStatus === "saving"}
          style={{ ...buttonStyle(saveStatus === "saving"), width: "100%" }}
        >
          {saveStatus === "saving" ? "Guardando..." : "Guardar cambios en el modelo"}
        </button>
        {saveStatus === "saved" && (
          <p style={{ fontSize: 11, color: "#27ae60", margin: "6px 0 0" }}>
            Guardado — el .ply del sitio se actualizó en el servidor.
          </p>
        )}
        {saveStatus === "error" && (
          <p style={{ fontSize: 11, color: "#e74c3c", margin: "6px 0 0" }}>
            Error al guardar. Revisá que el servidor de desarrollo esté corriendo.
          </p>
        )}
      </div>
    </div>
  );
}

function buttonStyle(disabled) {
  return {
    flex: 1,
    padding: "6px 8px",
    background: disabled ? "#141416" : "#1a1a1c",
    color: disabled ? "#555" : "#eee",
    border: "1px solid #333",
    borderRadius: 4,
    fontSize: 12,
    cursor: disabled ? "default" : "pointer",
  };
}
