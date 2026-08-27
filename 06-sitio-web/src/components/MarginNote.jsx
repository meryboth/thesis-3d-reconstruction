import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function MarginNote({ chapter }) {
  if (!chapter) return <aside className="margin-rail" aria-hidden="true" />;

  const isReferencePage = chapter.num == null;

  return (
    <aside className="margin-rail" aria-label="Conclusión del capítulo">
      <div className="margin-note">
        <span className="margin-kicker">
          {isReferencePage
            ? chapter.title
            : `Conclusión · Cap. ${String(chapter.num).padStart(2, "0")}`}
        </span>
        <div className="margin-body">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {chapter.conclusion ||
              (isReferencePage
                ? "_(página de referencia, sin síntesis)_"
                : "_(capítulo introductorio, sin síntesis propia)_")}
          </ReactMarkdown>
        </div>
      </div>
    </aside>
  );
}
