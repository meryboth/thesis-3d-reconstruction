# formato-entrega

Versión de la tesis en `.docx` alineada al formato institucional de entrega
(referencia: `TESIS-FORMATO.docx`, Universidad de Palermo – Facultad de Ingeniería).

| Archivo | Qué es |
|---|---|
| `Tesis-Reconstruccion3D-Patrimonio.docx` | El documento entregable (230 páginas, ~48.400 palabras) |
| `build_docx.py` | Generador: lee los `.md` de `05-tesis/` y arma el `.docx` |
| `front_matter.py` | Páginas preliminares (portada, aprobación, resumen, índices) |
| `epigrafes.py` | Los 18 epígrafes que los `.md` no tenían, escritos para esta versión |
| `propagar_epigrafes.py` | Lleva epígrafes y numeración a los `.md` de `05-tesis/` |
| `plantilla-formato.docx` | El formato institucional, sin contenido: estilos, fuentes, pie de página |
| `reducir_plantilla.py` | Regenera esa plantilla si la facultad entrega un formato nuevo |
| `renumeracion.md` | Reporte: dice si el `.docx` y los `.md` están alineados |

El build necesita **Word instalado** para dejar la tabla de contenido calculada (ver abajo).

## Las tres versiones tienen que decir lo mismo

`05-tesis/` es la única fuente de verdad; el sitio web y este `.docx` son derivados
y no se editan a mano. Después de tocar cualquier capítulo hay que correr la skill
**`sync-tesis`**, que hace los tres pasos en orden:

```bash
cd C:\nerfstudio_work\thesis\formato-entrega && "C:\Users\mboth\AppData\Local\Programs\Python\Python313\python.exe" propagar_epigrafes.py
```

Dry-run: informa qué haría. Con `--aplicar` escribe los `.md`. Es idempotente.

```bash
"C:\Users\mboth\AppData\Local\Programs\Python\Python313\python.exe" "C:\nerfstudio_work\thesis\06-sitio-web\scripts\prepare_content.py"
```

```bash
cd C:\nerfstudio_work\thesis\formato-entrega && "C:\Users\mboth\AppData\Local\Programs\Python\Python313\python.exe" build_docx.py
```

## El `.docx` es sólo para leer y entregar

Decisión de la autora (09/09): **el texto se escribe siempre en los `.md`** (Mark Text),
nunca en Word. El `.docx` es una salida — lo que se escriba directamente ahí se pierde
en el próximo regenerado.

Como red de seguridad, `build_docx.py` guarda la huella del `.docx` que generó. Si en la
corrida siguiente el archivo no coincide, asume que fue editado a mano: guarda una copia
como `…--editado-a-mano-<fecha>.docx` y avisa antes de sobrescribirlo. Así una edición
accidental en Word no desaparece en silencio.

## Qué tiene de "vivo" el documento

| | Estado |
|---|---|
| Índice clickeable | Sí — 146 entradas, `Ctrl+clic` salta a la sección |
| Panel de navegación de Word | Sí — los títulos usan estilos `Heading1/2/3` con nivel de esquema |
| Lista de tablas y de figuras clickeables | Sí — 115 entradas con número de página y puntos de relleno |
| Números de página | Campos `PAGEREF`: se recalculan al actualizar |
| Índice y listas al abrir | Se refrescan solos (`updateFields` activado) |
| Numeración de figuras (`Figura 5.16`) | **Texto fijo**, no se renumera sola en Word |
| Citas del tipo "ver Figura 5.16" | **Texto fijo**, no son referencias cruzadas de Word |

Las dos últimas son deliberadas: la numeración la manda `05-tesis/`, no Word. Si Word
también numerara, habría dos autoridades sobre el mismo número y terminarían en
desacuerdo. Para renumerar, se edita el `.md` y se corre la skill `sync-tesis`.

El generador, al terminar el build, abre el `.docx` con Word para dejar el índice y las
listas ya calculados, y después reinstala el flag `updateFields` (Word lo consume al
guardar). Si Word no estuviera disponible, el build avisa y el `.docx` sirve igual, sólo
que hay que actualizar los campos a mano (`Ctrl+E`, `F9`).

## Cómo se alineó al formato

Se reutiliza el paquete OOXML de la plantilla de referencia (`styles.xml`,
`fontTable.xml`, fuentes embebidas, `footer1.xml`, `theme/`) y se reemplaza sólo el
contenido. Eso hace que herede exactamente las mismas definiciones de estilo:

| Elemento | Formato (idéntico a la plantilla) |
|---|---|
| Página | A4, márgenes sup. 2,59 cm / inf. 3,82 cm / izq. 3,86 cm / der. 2,59 cm |
| Pie de página | Número de página centrado |
| Cuerpo | Times New Roman 12 pt, justificado, interlineado doble, sangría de primera línea 0,85 cm |
| Título de capítulo | Ubuntu 16 pt, color `#2a6099` (estilo `Heading1`) |
| Secciones N.N | Times New Roman 16 pt negrita (`Heading2`) |
| Subsecciones N.N.N | Times New Roman 14 pt negrita (`Heading3`) |
| Sub-apartados | Times New Roman 13 pt negrita cursiva (`Heading4`) |
| Epígrafes de figura/tabla | Times New Roman 10 pt cursiva, centrado |
| Tablas | Ancho fijo al espejo de texto, encabezado con fondo negro y texto blanco 8 pt, bordes finos |

## Estructura del documento

1. Portada
2. Página de aprobación del comité
3. Resumen — **pendiente de escribir** (`05-tesis/resumen/resumen.md`)
4. Tabla de contenido (146 entradas con números de página, ya calculada)
5. Lista de tablas (34 entradas, clickeables y con número de página)
6. Lista de figuras (81 entradas: series `Figura`, `Gráfico` e `Imagen`)
7. Capítulos 1 a 7
8. Bibliografía
9. Glosario

## Numeración y epígrafes

La tesis usa cuatro series — `Tabla`, `Figura`, `Gráfico` e `Imagen` — y cada una se
numera por separado, correlativa por orden de aparición dentro del capítulo. Los 115
objetos (83 imágenes + 32 tablas) tienen epígrafe con descripción.

Los 18 que no lo tenían se escribieron mirando la imagen y el texto que la rodea en el
capítulo: dicen qué se ve, sin sumar interpretación ni conclusiones. Están en
[`epigrafes.py`](epigrafes.py) y ya propagados a los `.md`.

## Verificación hecha

- Las 905 líneas de texto y las 470 celdas de tabla de los `.md` aparecen literales en
  el `.docx` (chequeo automático de coincidencia exacta).
- Los 115 epígrafes coinciden uno a uno entre los `.md`, el sitio web y el `.docx`.
- Las 82 imágenes de los capítulos resuelven y están embebidas, incluida la que estaba
  escrita como `<img>` HTML en vez de markdown. Las `.webp` y `.gif` se convierten a PNG
  porque Word no las renderiza de forma fiable.
- Los escapes de markdown que dejaba Mark Text (`b\)`, `1\.`, `\[Tesis doctoral\]`) se
  resuelven: no queda ninguna barra invertida suelta en el texto.
- La tabla de contenido se ve completa al abrir el documento, sin tener que apretar `F9`.
- 313 hipervínculos: 146 del índice, 115 de las listas de tablas y figuras, 52 externos.
- El archivo lleva título, autora, materia y palabras clave en sus propiedades.
- Abre en Word sin reparaciones y exporta a PDF correctamente.

## Pendiente

- **Resumen** — el archivo ya está creado en `05-tesis/resumen/resumen.md`, con un
  comentario adentro explicando qué va y dónde. Mientras no tenga texto, el `.docx`
  muestra un `[PENDIENTE]` en esa página y el sitio no publica la sección. En cuanto se
  escriba algo, la skill `sync-tesis` lo lleva a los dos.
