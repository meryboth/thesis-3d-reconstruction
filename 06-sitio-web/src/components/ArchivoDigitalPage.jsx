const SITES = [
  {
    id: "paraguas",
    title: "Los Paraguas",
    subtitle: "Vicente López — Amancio Williams",
    description: "Splatfacto, dataset DJI. Editado en SuperSplat (limpieza de floaters, encuadre de cámara).",
    // visor comparativo de las 3 capas (nube / modelo IA / splat), no el splat solo
    viewerUrl: "/modelado?site=paraguas",
    thumbnail: "/archivo-digital/paraguas/preview.gif",
    plyUrl: "/archivo-digital/paraguas/splat-editado.ply",
    splatUrl: "/archivo-digital/paraguas/splat.splat",
  },
  {
    id: "templete-central",
    title: "Templete Central",
    subtitle: "Sexto Panteón, Cementerio de la Chacarita",
    description: "Splatfacto, dataset DJI. Editado en SuperSplat (limpieza de floaters, encuadre de cámara).",
    // visor comparativo de las 3 capas (nube / modelo IA / splat), no el splat solo
    viewerUrl: "/modelado?site=templete-central",
    thumbnail: "/archivo-digital/templete-central/preview.gif",
    plyUrl: "/archivo-digital/templete-central/splat-editado-v2.ply",
    // .splat todavia no exportado -- pendiente de curar en SuperSplat
    splatUrl: null,
  },
  {
    id: "panteon",
    title: "Panteón Asociación Catalana",
    subtitle: "Cementerio de la Chacarita",
    description: "Splatfacto, dataset DJI. Editado en SuperSplat (limpieza de floaters, encuadre de cámara).",
    // visor comparativo de las 3 capas (nube / modelo IA / splat), no el splat solo
    viewerUrl: "/modelado?site=panteon",
    thumbnail: null,
    plyUrl: "/archivo-digital/panteon/splat-editado.ply",
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

// Pagina a pantalla completa (sin nav lateral), igual que /presentacion y
// /segmentador -- el catalogo de splats no necesita el andamiaje de lectura
// continua del resto del sitio.
export default function ArchivoDigitalPage() {
  return (
    <div className="ad-root">
      <header className="ad-header">
        <a href="/" className="ad-back">
          ← Volver a la tesis
        </a>
        <h1 className="ad-title">Archivo digital</h1>
      </header>
      <div className="ad-stage">
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
                </div>
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
