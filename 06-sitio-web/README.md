# Sitio web de la tesis

Versión web (solo frontend, Vite + React) de la tesis — lectura continua de los 6 capítulos con navegación de capítulos a la izquierda y la conclusión del capítulo activo en el margen derecho (se actualiza sola al scrollear).

## Cómo se genera el contenido

El sitio **no** tiene el texto de la tesis pegado a mano: `scripts/prepare_content.py` lee directamente los `.md` de `../05-tesis/capituloN_*/`, copia las imágenes que referencian a `public/content/assets/` (con nombre único por capítulo, sin colisiones) y arma `public/content/manifest.json` con el título y el extracto de "conclusión"/"cierre del capítulo" de cada uno para el margen derecho.

**Cada vez que se edite un capítulo en `05-tesis/` hay que volver a correr el script para que el sitio se actualice:**

```bash
python scripts/prepare_content.py
```

(usa el Python de `C:\Users\mboth\AppData\Local\Programs\Python\Python313\python.exe`, no tiene dependencias fuera de la librería estándar).

## Cómo correrlo

```bash
npm install   # solo la primera vez
npm run dev
```

Node.js no estaba instalado en esta máquina — se instaló la versión LTS vía `winget install OpenJS.NodeJS.LTS`.

## Estructura

- `src/App.jsx` — layout de 3 columnas (nav / contenido / margen) + `IntersectionObserver` que detecta qué capítulo está en pantalla.
- `src/components/ChapterNav.jsx` — navegación fija de capítulos (izquierda).
- `src/components/ChapterSection.jsx` — fetch + render de un capítulo (`react-markdown` + `remark-gfm` para tablas + `rehype-raw` para el `<u>` que usan los títulos de sección de la tesis).
- `src/components/MarginNote.jsx` — nota del margen derecho con la conclusión del capítulo activo.
- `src/layout.css` — todo el diseño (tipografía, grilla, estilos de imagen/tabla/caption). `src/index.css` son los estilos base globales.
- `public/content/` — **generado**, no editar a mano (lo pisa `prepare_content.py`).

## Pendiente / próximas iteraciones

- Sumar GIFs de los videos de captura de cada sitio (para dar contexto de cómo se hizo el relevamiento) — la idea es agregarlos junto a las imágenes de cada capítulo, probablemente en el Cap. 3 (caso de estudio) y/o Cap. 5 (fidelidad geométrica).
- Deploy (GitHub Pages / Vercel / Netlify — a definir).
- Ajustes de diseño a medida que se revise en el navegador real.
