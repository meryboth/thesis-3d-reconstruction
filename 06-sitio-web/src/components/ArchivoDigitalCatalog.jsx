// `captures`: una entrada por dispositivo/sesion de relevamiento (fecha de
// inicio y fin del registro en campo). Cuando se sume un futuro caso de
// estudio, alcanza con agregar un objeto mas a este array -- tanto las
// cards como la cronologia de abajo se arman solas a partir de esto.
const SITES = [
  {
    id: "paraguas",
    title: "Los Paraguas",
    subtitle: "Vicente López — Amancio Williams",
    description: "Splatfacto, dataset DJI. Editado en SuperSplat (limpieza de floaters, encuadre de cámara).",
    viewerUrl: "https://superspl.at/s?id=08270ab6",
    // GIF/imagen de preview pendiente -- ver thumbnail abajo
    thumbnail: null,
    plyUrl: "/archivo-digital/paraguas/scene.ply",
    splatUrl: "/archivo-digital/paraguas/splat.splat",
    captures: [{ device: "DJI Neo 2", start: "2026-06-20", end: "2026-06-20" }],
    // dispositivo cuyo registro efectivamente se uso para entrenar el
    // splat publicado (ver `captures` para el historial completo de
    // relevamiento en campo, que puede incluir otros dispositivos).
    splatDevice: "DJI Neo 2",
  },
  {
    id: "templete-central",
    title: "Templete Central",
    subtitle: "Sexto Panteón, Cementerio de la Chacarita",
    description:
      "Splatfacto, dataset DJI. Export crudo, sin curar todavía en SuperSplat — sirve para probar el visor, no como versión final.",
    thumbnail: null,
    plyUrl: "/archivo-digital/templete-central/scene.ply",
    // .splat todavia no exportado -- pendiente de curar en SuperSplat
    splatUrl: null,
    captures: [
      { device: "Insta360 X5", start: "2026-08-02", end: "2026-08-09" },
      { device: "DJI Neo 2", start: "2026-08-09", end: "2026-08-23" },
    ],
    splatDevice: "DJI Neo 2",
  },
  {
    id: "panteon",
    title: "Panteón Asociación Española",
    subtitle: "Cementerio de la Chacarita",
    description:
      "Splatfacto, dataset DJI. Export crudo, sin curar todavía en SuperSplat — sirve para probar el visor, no como versión final.",
    thumbnail: null,
    plyUrl: "/archivo-digital/panteon/scene.ply",
    // .splat todavia no exportado -- pendiente de curar en SuperSplat
    splatUrl: null,
    captures: [
      { device: "DJI Neo 2", start: "2026-08-09", end: "2026-08-22" },
      { device: "Insta360 X5", start: "2026-08-09", end: "2026-08-09" },
    ],
    splatDevice: "DJI Neo 2",
  },
];

const MONTHS = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];

function formatDate(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  return `${d} ${MONTHS[m - 1]} ${y}`;
}

function formatRange(start, end) {
  if (start === end) return formatDate(start);
  const [ys, ms, ds] = start.split("-").map(Number);
  const [ye, me, de] = end.split("-").map(Number);
  if (ys === ye && ms === me) return `${ds}–${de} ${MONTHS[ms - 1]} ${ys}`;
  if (ys === ye) return `${ds} ${MONTHS[ms - 1]} – ${de} ${MONTHS[me - 1]} ${ys}`;
  return `${formatDate(start)} – ${formatDate(end)}`;
}

function earliestDate(captures) {
  return captures.reduce((min, c) => (c.start < min ? c.start : min), captures[0].start);
}

function latestDate(captures) {
  return captures.reduce((max, c) => (c.end > max ? c.end : max), captures[0].end);
}

// icono placeholder generico (nube de puntos / splat) para las cards sin
// thumbnail todavia -- reemplazar `thumbnail` en SITES por un gif/imagen
// (ej. "/archivo-digital/paraguas/preview.gif") apenas este disponible.
function PlaceholderIcon() {
  return (
    <svg viewBox="0 0 64 64" width="40" height="40" fill="none" aria-hidden="true">
      <circle cx="32" cy="14" r="3" fill="currentColor" opacity="0.55" />
      <circle cx="18" cy="24" r="2.4" fill="currentColor" opacity="0.4" />
      <circle cx="46" cy="24" r="2.4" fill="currentColor" opacity="0.4" />
      <circle cx="10" cy="38" r="2" fill="currentColor" opacity="0.3" />
      <circle cx="26" cy="34" r="3.2" fill="currentColor" opacity="0.6" />
      <circle cx="40" cy="36" r="2.6" fill="currentColor" opacity="0.5" />
      <circle cx="54" cy="38" r="2" fill="currentColor" opacity="0.3" />
      <circle cx="20" cy="50" r="2.4" fill="currentColor" opacity="0.35" />
      <circle cx="34" cy="52" r="3" fill="currentColor" opacity="0.55" />
      <circle cx="48" cy="50" r="2" fill="currentColor" opacity="0.3" />
    </svg>
  );
}

export default function ArchivoDigitalCatalog({ registerRef }) {
  const timeline = [...SITES].sort((a, b) =>
    earliestDate(a.captures).localeCompare(earliestDate(b.captures))
  );

  return (
    <section id="archivo-digital" className="chapter" ref={registerRef}>
      <header className="chapter-head">
        <span className="chapter-eyebrow">Archivo digital</span>
        <h1>Los tres casos de estudio, en 3D</h1>
      </header>
      <div className="chapter-body">
        <p>
          Prueba de concepto: los exports de Splatfacto de los tres casos de estudio, visualizados en el
          navegador con el visor de PlayCanvas / SuperSplat (WebGL/WebGPU, sin plugins). Cada splat se
          navega en 3D libre — arrastrar para orbitar, rueda para zoom, click derecho para desplazar.
        </p>
        <p>
          <em>
            Nota: estos son los exports crudos de Splatfacto, todavía sin pasar por la limpieza de
            floaters en SuperSplat Editor — la cámara inicial puede quedar mirando a través del halo de
            outliers. Es la prueba de que el visor funciona con nuestros propios archivos, no la versión
            final del archivo digital.
          </em>
        </p>

        <h2 className="timeline-heading">Cronología de relevamientos</h2>
        <p className="timeline-intro">
          Fecha de registro en campo de cada caso de estudio, por dispositivo. A medida que se sumen
          nuevos relevamientos al archivo, se van a ir agregando acá en orden.
        </p>
        <div className="timeline">
          {timeline.map((site) => (
            <a key={site.id} href={`#archivo-digital-${site.id}`} className="timeline-item">
              <div className="timeline-marker" aria-hidden="true" />
              <div className="timeline-content">
                <span className="timeline-date">
                  {formatRange(earliestDate(site.captures), latestDate(site.captures))}
                </span>
                <h3 className="timeline-title">{site.title}</h3>
                <ul className="timeline-devices">
                  {site.captures.map((c) => (
                    <li key={c.device}>
                      {c.device} · {formatRange(c.start, c.end)}
                    </li>
                  ))}
                </ul>
              </div>
            </a>
          ))}
          <div className="timeline-item timeline-item-future">
            <div className="timeline-marker timeline-marker-future" aria-hidden="true" />
            <div className="timeline-content">
              <span className="timeline-date timeline-date-future">Próximo relevamiento</span>
              <p className="timeline-placeholder">
                Nuevos casos de estudio se van a documentar acá a medida que se sumen al archivo.
              </p>
            </div>
          </div>
        </div>

        <div className="splat-catalog">
          {SITES.map((site) => (
            <div key={site.id} id={`archivo-digital-${site.id}`} className="splat-card">
              <a
                className="splat-card-link"
                href={site.viewerUrl || `/archivo-digital/${site.id}/index.html`}
                target="_blank"
                rel="noopener noreferrer"
              >
                <div className="splat-card-thumb" aria-hidden="true">
                  {site.thumbnail ? (
                    <img
                      className="splat-card-thumb-img"
                      src={site.thumbnail}
                      alt=""
                      loading="lazy"
                    />
                  ) : (
                    <div className="splat-card-thumb-placeholder">
                      <PlaceholderIcon />
                    </div>
                  )}
                </div>
                <div className="splat-card-body">
                  <h3>{site.title}</h3>
                  <p className="splat-card-subtitle">{site.subtitle}</p>
                  <p className="splat-card-description">{site.description}</p>
                  {site.captures
                    .filter((c) => c.device === site.splatDevice)
                    .map((c) => (
                      <p key={c.device} className="splat-card-meta">
                        Relevamiento usado: {c.device} · {formatRange(c.start, c.end)}
                      </p>
                    ))}
                  <span className="splat-card-cta">Ver en 3D →</span>
                </div>
              </a>
              <div className="splat-card-downloads">
                <a className="splat-card-download" href={site.plyUrl} download>
                  Descargar .ply
                </a>
                {site.splatUrl ? (
                  <a className="splat-card-download" href={site.splatUrl} download>
                    Descargar .splat
                  </a>
                ) : (
                  <span className="splat-card-download splat-card-download-pending">
                    .splat (pendiente)
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
