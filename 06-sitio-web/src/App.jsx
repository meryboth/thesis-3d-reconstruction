import { useEffect, useRef, useState } from "react";
import ChapterNav from "./components/ChapterNav";
import MarginNote from "./components/MarginNote";
import ChapterSection from "./components/ChapterSection";
import ArchivoDigitalCatalog from "./components/ArchivoDigitalCatalog";
import "./layout.css";

// no viene del manifest (no es un capitulo en markdown) -- es una seccion de
// UI propia, pero se suma al nav como una entrada mas para que el scroll-spy
// y el acordeon de ChapterNav la traten igual que a un capitulo.
const ARCHIVO_DIGITAL_NAV_ENTRY = {
  id: "archivo-digital",
  num: null,
  title: "Archivo Digital",
  sections: [],
};

export default function App() {
  const [chapters, setChapters] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const refs = useRef({});

  useEffect(() => {
    fetch("/content/manifest.json")
      .then((r) => r.json())
      .then((data) => {
        setChapters(data);
        setActiveId(data[0]?.id ?? null);
      });
  }, []);

  useEffect(() => {
    if (chapters.length === 0) return;
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (visible[0]) setActiveId(visible[0].target.id);
      },
      { rootMargin: "-15% 0px -70% 0px", threshold: [0, 0.1, 0.25, 0.5] }
    );
    Object.values(refs.current).forEach((el) => el && observer.observe(el));
    return () => observer.disconnect();
  }, [chapters]);

  const activeChapter = chapters.find((c) => c.id === activeId);
  const navChapters = chapters.length ? [...chapters, ARCHIVO_DIGITAL_NAV_ENTRY] : chapters;

  return (
    <div className="page">
      <ChapterNav chapters={navChapters} activeId={activeId} />
      <main className="content-rail">
        <header className="masthead">
          <p className="masthead-kicker">Fotogrametría · NeRF · Gaussian Splatting</p>
          <h1 className="masthead-title">
            Reconstrucción 3D de Patrimonio Arquitectónico Argentino
          </h1>
        </header>
        {chapters.map((chapter) => (
          <ChapterSection
            key={chapter.id}
            chapter={chapter}
            registerRef={(el) => (refs.current[chapter.id] = el)}
          />
        ))}
        <ArchivoDigitalCatalog registerRef={(el) => (refs.current["archivo-digital"] = el)} />
      </main>
      <MarginNote chapter={activeChapter} />
    </div>
  );
}
