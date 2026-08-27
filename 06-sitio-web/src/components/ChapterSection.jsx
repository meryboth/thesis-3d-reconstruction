import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";

export default function ChapterSection({ chapter, registerRef }) {
  const [markdown, setMarkdown] = useState(null);

  useEffect(() => {
    let cancelled = false;
    fetch(chapter.file)
      .then((r) => r.text())
      .then((text) => {
        if (!cancelled) setMarkdown(text);
      });
    return () => {
      cancelled = true;
    };
  }, [chapter.file]);

  return (
    <section id={chapter.id} ref={registerRef} className="chapter">
      <header className="chapter-head">
        <span className="chapter-eyebrow">
          {chapter.num != null ? `Capítulo ${chapter.num}` : "Referencia"}
        </span>
        <h1>{chapter.title}</h1>
      </header>
      {markdown === null ? (
        <p className="chapter-loading">Cargando…</p>
      ) : (
        <div className="chapter-body">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeRaw]}
            components={{
              img: (props) => <img {...props} loading="lazy" decoding="async" />,
            }}
          >
            {markdown}
          </ReactMarkdown>
        </div>
      )}
    </section>
  );
}
