import { useEffect, useRef, useState } from "react";
import ChapterNav from "./components/ChapterNav";
import MarginNote from "./components/MarginNote";
import ChapterSection from "./components/ChapterSection";
import ScriptsCatalog from "./components/ScriptsCatalog";
import "./layout.css";

// no vienen del manifest (no son capitulos en markdown) -- son secciones de
// UI propia, pero se suman al nav como una entrada mas para que el scroll-spy
// y el acordeon de ChapterNav las traten igual que a un capitulo.

// al igual que el segmentador, es una ruta aparte (slides a pantalla completa),
// por eso lleva `href` propio en vez de anclar por id.
const PRESENTACION_NAV_ENTRY = {
  id: "presentacion",
  href: "/presentacion",
  num: null,
  title: "Presentación",
  sections: [],
};

// ruta aparte a pantalla completa (sin nav lateral), igual que Presentacion
// y el Segmentador -- por eso lleva `href` propio en vez de anclar por id.
const ARCHIVO_DIGITAL_NAV_ENTRY = {
  id: "archivo-digital",
  href: "/archivo-digital",
  num: null,
  title: "Archivo Digital",
  sections: [],
};

const SCRIPTS_NAV_ENTRY = {
  id: "scripts",
  num: null,
  title: "Scripts",
  sections: [],
};

// a diferencia de las dos anteriores, esta no es una seccion inline de esta
// misma pagina -- es una ruta aparte (visor 3D a pantalla completa), por eso
// lleva `href` propio en vez de anclar por id.
const SEGMENTADOR_NAV_ENTRY = {
  id: "segmentador",
  href: "/segmentador",
  num: null,
  title: "Segmentador de nube de puntos",
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

  // Los capitulos se cargan de a uno via fetch (ChapterSection), asincronico
  // y despues del render inicial -- el salto nativo del navegador a #hash en
  // la carga de la pagina ocurre ANTES de que ese contenido (y por lo tanto
  // el elemento con ese id) exista en el DOM, asi que nunca hace nada. Mismo
  // problema si el usuario clickea un link a una seccion/referencia que
  // todavia no se monto. Ademas, si el destino esta mas abajo en la pagina
  // que contenido (imagenes, sobre todo) que todavia no termino de cargar,
  // ese contenido sigue empujando todo hacia abajo despues del primer
  // scroll y el destino termina desalineado -- por eso este efecto sigue
  // re-scrolleando ante cada mutacion del DOM durante toda la ventana, no
  // solo la primera vez que aparece el elemento.
  useEffect(() => {
    let observer;
    let quietTimer;
    let hardStop;
    const tryScroll = () => {
      const hash = window.location.hash.slice(1);
      if (!hash) return;
      const el = document.getElementById(hash);
      if (el) el.scrollIntoView({ block: "start" });
    };
    const disconnect = () => {
      observer?.disconnect();
      clearTimeout(quietTimer);
      clearTimeout(hardStop);
    };
    const onMutation = () => {
      tryScroll();
      // sigue reintentando hasta que el DOM este "quieto" 800ms seguidos --
      // asi se adapta solo, aguante lo que aguante en cargar (esta pagina
      // tiene bastantes imagenes pesadas), en vez de una ventana fija que
      // corta demasiado pronto.
      clearTimeout(quietTimer);
      quietTimer = setTimeout(disconnect, 800);
    };
    tryScroll();
    observer = new MutationObserver(onMutation);
    observer.observe(document.body, { childList: true, subtree: true });
    quietTimer = setTimeout(disconnect, 800);
    hardStop = setTimeout(disconnect, 20000);
    window.addEventListener("hashchange", tryScroll);
    return () => {
      disconnect();
      window.removeEventListener("hashchange", tryScroll);
    };
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
  const navChapters = chapters.length
    ? [
        PRESENTACION_NAV_ENTRY,
        ...chapters,
        ARCHIVO_DIGITAL_NAV_ENTRY,
        SCRIPTS_NAV_ENTRY,
        SEGMENTADOR_NAV_ENTRY,
      ]
    : chapters;

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
        <ScriptsCatalog registerRef={(el) => (refs.current["scripts"] = el)} />
      </main>
      <MarginNote chapter={activeChapter} />
    </div>
  );
}
