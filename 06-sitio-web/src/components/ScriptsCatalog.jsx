import { useEffect, useMemo, useState } from "react";
import CodeViewerModal from "./CodeViewerModal";

const CATEGORY_ORDER = ["Análisis", "Gráficos y datasets derivados", "Pruebas de concepto", "Utilidades"];

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  return `${(bytes / 1024).toFixed(1)} KB`;
}

export default function ScriptsCatalog({ registerRef }) {
  const [scripts, setScripts] = useState([]);
  const [query, setQuery] = useState("");
  const [openScript, setOpenScript] = useState(null);

  useEffect(() => {
    fetch("/scripts/manifest.json")
      .then((r) => r.json())
      .then(setScripts)
      .catch(() => setScripts([]));
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return scripts;
    return scripts.filter(
      (s) => s.name.toLowerCase().includes(q) || s.description.toLowerCase().includes(q)
    );
  }, [scripts, query]);

  const grouped = useMemo(() => {
    const map = new Map();
    for (const s of filtered) {
      if (!map.has(s.category)) map.set(s.category, []);
      map.get(s.category).push(s);
    }
    return CATEGORY_ORDER.filter((c) => map.has(c)).map((c) => [c, map.get(c)]);
  }, [filtered]);

  return (
    <section id="scripts" className="chapter" ref={registerRef}>
      <header className="chapter-head">
        <span className="chapter-eyebrow">Material y reproducibilidad</span>
        <h1>Scripts de análisis</h1>
      </header>
      <div className="chapter-body">
        <p>
          Todas las tablas, gráficos y métricas citadas en los capítulos salen de estos scripts —
          se listan acá para que cualquier número del análisis (PSNR/SSIM/LPIPS, tiempos de
          procesamiento, tasa de fallos, geometría de nubes de puntos y splats) se pueda verificar
          o reproducir. Corren sobre los datasets y resultados locales de cada caso de estudio, no
          contra un servicio externo.
        </p>
        {scripts.length > 0 && (
          <input
            type="search"
            className="scripts-search"
            placeholder={`Buscar en ${scripts.length} scripts (por nombre o descripción)…`}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            aria-label="Buscar script"
          />
        )}
        {grouped.map(([category, items]) => (
          <div key={category} className="scripts-group">
            <h2>{category}</h2>
            <p className="scripts-group-blurb">{items[0].categoryBlurb}</p>
            <ul className="scripts-list">
              {items.map((s) => (
                <li key={s.name} className="scripts-item">
                  <div className="scripts-item-head">
                    <button
                      type="button"
                      className="scripts-item-name"
                      onClick={() => setOpenScript(s)}
                    >
                      {s.name}
                    </button>
                    <span className="scripts-item-meta">
                      {s.lang} · {formatSize(s.sizeBytes)}
                    </span>
                  </div>
                  <p className="scripts-item-desc">{s.description}</p>
                </li>
              ))}
            </ul>
          </div>
        ))}
        {scripts.length > 0 && filtered.length === 0 && (
          <p className="scripts-empty">Ningún script coincide con "{query}".</p>
        )}
      </div>
      <CodeViewerModal script={openScript} onClose={() => setOpenScript(null)} />
    </section>
  );
}
