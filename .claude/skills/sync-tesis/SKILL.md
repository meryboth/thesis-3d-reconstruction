---
name: sync-tesis
description: Sincroniza las tres versiones de la tesis — capítulos en thesis/05-tesis/, sitio web en thesis/06-sitio-web/ y el .docx de entrega en thesis/formato-entrega/ — para que digan exactamente lo mismo. Usar SIEMPRE, sin que el usuario lo pida, inmediatamente después de crear, editar o reescribir cualquier archivo dentro de thesis/05-tesis/**/*.md (texto, tablas, imágenes agregadas o quitadas, títulos, epígrafes, lo que sea) — el sitio y el .docx quedan desactualizados si este paso se salta. También usar si el usuario dice que la web o el .docx muestran algo viejo o incorrecto, pregunta por qué no se refleja un cambio reciente de un capítulo, o pide explícitamente sincronizar, actualizar o regenerar el sitio o el documento de entrega.
---

# Sincronizar las tres versiones de la tesis

## Por qué existe esto

La tesis existe en tres formas y **`thesis/05-tesis/` es la única fuente de verdad**:

| Versión | Dónde | Cómo se genera |
|---|---|---|
| Capítulos (fuente) | `05-tesis/*/*.md` | Se editan a mano |
| Sitio web | `06-sitio-web/public/content/` | `prepare_content.py` |
| `.docx` de entrega | `formato-entrega/Tesis-Reconstruccion3D-Patrimonio.docx` | `build_docx.py` |

Las dos últimas son **100% derivadas**: nunca se editan a mano. La autora escribe siempre en los `.md` con Mark Text; el `.docx` es sólo para leer y entregar (decisión del 09/09, tras evaluar la alternativa de escribir en Word). Editar `public/content/` o el `.docx` directamente crea una divergencia silenciosa — el próximo regenerado lo pisa igual, y mientras tanto la tesis dice tres cosas distintas.

Pedido explícito de la usuaria (26/08, ampliado el 09/09): que las tres queden siempre alineadas con la misma información.

## Qué hacer

Después de una tanda de ediciones sobre uno o más capítulos, correr los tres pasos **en este orden**:

```bash
cd C:\nerfstudio_work\thesis\formato-entrega && "C:\Users\mboth\AppData\Local\Programs\Python\Python313\python.exe" propagar_epigrafes.py
```

**1. Propagar epígrafes y numeración.** Sin `--aplicar` es un dry-run que informa qué cambiaría. Si dice `TOTAL: 0 renumerados, 0 líneas con citas actualizadas, 0 epígrafes insertados`, no hay nada que propagar — seguir al paso 2.

Si informa cambios, es porque se agregó una figura o tabla sin epígrafe, o porque la numeración quedó fuera de orden. Entonces:

- Si hay imágenes nuevas sin epígrafe **ni texto alternativo**, el script no tiene qué escribirles: primero agregar su descripción a `formato-entrega/epigrafes.py` (clave = nombre de archivo de la imagen). Ver ahí el formato y el criterio: describir qué se ve, sin interpretación ni conclusiones.
- **Antes de escribir sobre un `.md`, confirmar con la usuaria que no lo tiene abierto en Mark Text con cambios sin guardar** — escribe ahí y se pisarían.
- Después, aplicar: `python propagar_epigrafes.py --aplicar`

Es idempotente: volver a correrlo no cambia nada.

```bash
"C:\Users\mboth\AppData\Local\Programs\Python\Python313\python.exe" "C:\nerfstudio_work\thesis\06-sitio-web\scripts\prepare_content.py"
```

**2. Regenerar el sitio web.** Borra y regenera `public/content/assets/`, copia todas las imágenes referenciadas desde los capítulos (markdown `![]()` y también `<img>` HTML, con nombre único por capítulo), reescribe los `.md` copiados con las rutas corregidas y reconstruye `manifest.json`.

No hace falta reiniciar Vite si ya está corriendo — sirve `public/` directamente; alcanza con refrescar el navegador (`Ctrl+Shift+R` si insiste con una versión vieja).

```bash
cd C:\nerfstudio_work\thesis\formato-entrega && "C:\Users\mboth\AppData\Local\Programs\Python\Python313\python.exe" build_docx.py
```

**3. Regenerar el `.docx` de entrega.** Si imprime `[ATENCION] el .docx cambio desde el ultimo build`, alguien escribió en Word: quedó una copia `…--editado-a-mano-<fecha>.docx` al lado. Avisar a la usuaria y ver si hay que rescatar algo de ahí antes de seguir. Este paso necesita **Word instalado**: al final abre el documento con Word para dejar la tabla de contenido ya calculada (el campo `TOC` no se actualiza solo al abrir, y sin este paso el índice se ve vacío). Si Word no está, el script avisa y el `.docx` sirve igual, pero hay que actualizar los campos a mano (`Ctrl+E`, `F9`).

## Verificar que salió bien

- **`prepare_content.py`**: si aparece alguna línea `[WARN] no existe: ...`, un capítulo referencia una imagen cuya ruta relativa no resuelve. Arreglar esa referencia en el `.md` del capítulo (no en `public/content/`) y volver a correr. No dejarlo pasar en silencio. La última línea reporta `Assets copiados: N` — comprobar que el número no bajó de golpe respecto a la corrida anterior.
- **`build_docx.py`**: tiene que imprimir `tabla de contenido generada; N paginas`. Si en cambio imprime un `[AVISO]`, el índice quedó sin calcular. Además escribe `formato-entrega/renumeracion.md`. Si todo está alineado, ese archivo dice **"Alineados"**. Si en cambio lista epígrafes renumerados o agregados, significa que el paso 1 quedó sin aplicar — volver a él.
- Los tres tienen que coincidir en cantidad de epígrafes y de imágenes. Chequeo rápido: contar en los `.md`, en `06-sitio-web/public/content/*.md` y en el `.docx` las líneas que arrancan con `*Tabla|Figura|Gráfico|Imagen N.M`.

Si no aparece nada raro, no hace falta contárselo al usuario: es higiene, no un entregable. Si algo no cierra, sí avisar.

## Detalles que ya mordieron

- **La tesis usa cuatro series de epígrafes**: `Tabla`, `Figura`, `Gráfico` e `Imagen`. No unificarlas ni asumir que sólo hay figuras y tablas. Cada una se numera por separado y correlativa dentro de su capítulo.
- **Hay citas cruzadas entre capítulos** (el Cap. 7 cita figuras y tablas del Cap. 6), por eso la numeración se calcula sobre todos los capítulos antes de reescribir ninguno.
- **Mark Text deja escapes de markdown** (`b\)`, `1\.`, `\[Tesis doctoral\]`) y a veces mete imágenes como `<img>` HTML en vez de markdown. Los tres generadores lo contemplan; si aparece un caso nuevo que no se maneja, arreglarlo en el generador, no en el `.md`.
- **El resumen se publica solo cuando tiene texto.** `05-tesis/resumen/resumen.md` existe desde el principio con un comentario HTML de instrucciones. Los generadores descartan los comentarios HTML: mientras el archivo no tenga texto real, el `.docx` muestra `[PENDIENTE]` y `prepare_content.py` omite la sección (e informa `Omitiendo resumen: ...`). No es un error.
- **La numeración de figuras es texto fijo, a propósito.** No se usan campos `SEQ` ni referencias cruzadas de Word: si Word también numerara, habría dos autoridades sobre el mismo número (Word y `05-tesis/`) y terminarían en desacuerdo. Lo que sí es campo vivo: el índice, y los números de página de la lista de tablas y de figuras.
- **Los epígrafes sí se pueden escribir.** La regla de "no escribir prosa de la tesis" no los alcanza: son leyenda factual de una imagen, y la usuaria pidió explícitamente (09/09) que todas las figuras y tablas tengan descripción. Van en `epigrafes.py` hasta que `propagar_epigrafes.py` los lleva al `.md`.
