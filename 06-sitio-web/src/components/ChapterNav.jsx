import { useEffect, useState } from "react";

export default function ChapterNav({ chapters, activeId }) {
  const [expanded, setExpanded] = useState(() => new Set());

  // al activarse un capitulo por scroll, se auto-expande (sin cerrar los que
  // el usuario ya abrio a mano) -- asi el sub-indice del capitulo que se esta
  // leyendo siempre queda visible sin tener que tocar nada.
  useEffect(() => {
    if (!activeId) return;
    setExpanded((prev) => (prev.has(activeId) ? prev : new Set(prev).add(activeId)));
  }, [activeId]);

  function toggle(id) {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  return (
    <nav className="nav-rail" aria-label="Capítulos">
      <div className="nav-brand">
        <span className="nav-brand-kicker">Tesis</span>
        <span className="nav-brand-title">Reconstrucción 3D de Patrimonio</span>
      </div>
      <ol className="nav-list">
        {chapters.map((c) => {
          const hasSections = c.sections && c.sections.length > 0;
          const isOpen = expanded.has(c.id);
          return (
            <li key={c.id} className="nav-item">
              <div className="nav-row">
                {hasSections ? (
                  <button
                    type="button"
                    className={isOpen ? "nav-caret is-open" : "nav-caret"}
                    aria-expanded={isOpen}
                    aria-label={isOpen ? "Contraer secciones" : "Expandir secciones"}
                    onClick={() => toggle(c.id)}
                  >
                    ▸
                  </button>
                ) : (
                  <span className="nav-caret nav-caret-spacer" aria-hidden="true" />
                )}
                <a
                  href={c.href ?? `#${c.id}`}
                  className={c.id === activeId ? "nav-link is-active" : "nav-link"}
                >
                  {c.num != null ? (
                    <span className="nav-num">{String(c.num).padStart(2, "0")}</span>
                  ) : (
                    <span className="nav-num nav-num-icon" aria-hidden="true">
                      §
                    </span>
                  )}
                  <span className="nav-title">{c.title}</span>
                </a>
              </div>
              {hasSections && isOpen && (
                <ul className="nav-sublist">
                  {c.sections.map((s) => (
                    <li key={s.id}>
                      <a href={`#${s.id}`} className="nav-sublink">
                        {s.num && <span className="nav-subnum">{s.num}</span>}
                        <span>{s.title}</span>
                      </a>
                      {s.children && s.children.length > 0 && (
                        <ul className="nav-subsublist">
                          {s.children.map((sc) => (
                            <li key={sc.id}>
                              <a href={`#${sc.id}`} className="nav-sublink nav-sublink-deep">
                                <span className="nav-subnum">{sc.num}</span>
                                <span>{sc.title}</span>
                              </a>
                            </li>
                          ))}
                        </ul>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
