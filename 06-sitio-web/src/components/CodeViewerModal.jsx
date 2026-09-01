import "../prismSetup";
import "prismjs/components/prism-powershell";
import { useEffect, useState } from "react";
import { Highlight, themes } from "prism-react-renderer";

function languageFor(name) {
  if (name.endsWith(".ps1")) return "powershell";
  return "python";
}

export default function CodeViewerModal({ script, onClose }) {
  const [code, setCode] = useState(null);
  const [error, setError] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!script) return;
    setCode(null);
    setError(false);
    setCopied(false);
    fetch(script.url)
      .then((r) => {
        if (!r.ok) throw new Error("fetch failed");
        return r.text();
      })
      .then(setCode)
      .catch(() => setError(true));
  }, [script]);

  useEffect(() => {
    if (!script) return;
    const onKey = (e) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", onKey);
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prevOverflow;
    };
  }, [script, onClose]);

  if (!script) return null;

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(code ?? "");
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard API no disponible (contexto no seguro, permisos, etc.) -- sin fallback visible
    }
  }

  return (
    <div className="code-modal-backdrop" onClick={onClose}>
      <div className="code-modal" onClick={(e) => e.stopPropagation()}>
        <div className="code-modal-header">
          <div className="code-modal-title">
            <span className="code-modal-name">{script.name}</span>
            <span className="code-modal-meta">{script.lang}</span>
          </div>
          <div className="code-modal-actions">
            <button type="button" className="code-modal-btn" onClick={handleCopy} disabled={!code}>
              {copied ? "Copiado ✓" : "Copiar"}
            </button>
            <a className="code-modal-btn" href={script.url} target="_blank" rel="noopener noreferrer">
              Ver crudo
            </a>
            <button type="button" className="code-modal-btn code-modal-close" onClick={onClose} aria-label="Cerrar">
              ✕
            </button>
          </div>
        </div>
        <div className="code-modal-body">
          {error && <p className="code-modal-status">No se pudo cargar el archivo.</p>}
          {!error && code === null && <p className="code-modal-status">Cargando…</p>}
          {code !== null && (
            <Highlight theme={themes.github} code={code.replace(/\n$/, "")} language={languageFor(script.name)}>
              {({ style, tokens, getLineProps, getTokenProps }) => (
                <pre className="code-modal-pre" style={style}>
                  {tokens.map((line, i) => (
                    <div key={i} {...getLineProps({ line })} className="code-modal-line">
                      <span className="code-modal-lineno">{i + 1}</span>
                      <span className="code-modal-linecontent">
                        {line.map((token, key) => (
                          <span key={key} {...getTokenProps({ token })} />
                        ))}
                      </span>
                    </div>
                  ))}
                </pre>
              )}
            </Highlight>
          )}
        </div>
      </div>
    </div>
  );
}
