// Prism.languages.python viene incluido por defecto en prism-react-renderer,
// pero powershell no -- se registra a mano contra la MISMA instancia de Prism
// que usa la libreria (por eso el global.Prism = Prism antes de cargar el
// componente). Este archivo se importa ANTES que "prismjs/components/prism-powershell"
// en CodeViewerModal -- el orden de los imports importa.
import { Prism } from "prism-react-renderer";

(typeof global !== "undefined" ? global : window).Prism = Prism;
