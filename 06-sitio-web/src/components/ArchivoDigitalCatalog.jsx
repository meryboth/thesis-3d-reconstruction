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
  },
];

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
        <div className="splat-catalog">
          {SITES.map((site) => (
            <div key={site.id} className="splat-card">
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
