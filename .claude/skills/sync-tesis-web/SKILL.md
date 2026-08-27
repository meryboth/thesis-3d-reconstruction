---
name: sync-tesis-web
description: Regenera el contenido de thesis/06-sitio-web/ (la versión web de la tesis) a partir de los capítulos en thesis/05-tesis/. Usar SIEMPRE, sin que el usuario lo pida, inmediatamente después de crear, editar o reescribir cualquier archivo dentro de thesis/05-tesis/**/*.md (texto, tablas, imágenes agregadas/quitadas, títulos, lo que sea) — el sitio web queda desincronizado y desactualizado si este paso se salta. También usar si el usuario dice que la web muestra algo viejo/incorrecto, pregunta por qué el sitio no refleja un cambio reciente del capítulo, o pide explícitamente sincronizar/actualizar/regenerar el sitio.
---

# Sincronizar el sitio web de la tesis con los capítulos

## Por qué existe esto

`thesis/05-tesis/capituloN_*/capituloN_*.md` es la **única fuente de verdad** de la tesis. `thesis/06-sitio-web/public/content/` (los `.md`, las imágenes en `assets/`, y `manifest.json`) es **100% derivado** — lo genera el script `prepare_content.py` leyendo los capítulos originales. Nunca se edita nada dentro de `public/content/` a mano: el próximo `prepare_content.py` lo pisa igual, y editarlo a mano solo crea una divergencia silenciosa entre lo que dice la tesis y lo que muestra la web.

Por eso, cada edición a un capítulo (agregar una figura, corregir una cifra, reescribir un párrafo, sacar una sección) dejar sin correr este paso implica que la web queda mostrando una versión vieja o incorrecta — exactamente el tipo de inconsistencia que ya generó confusión en esta sesión (la usuaria vio una imagen desactualizada en el sitio después de un fix en el capítulo). El usuario pidió explícitamente que ambos queden siempre sincronizados.

## Qué hacer

Después de terminar una tanda de ediciones sobre uno o más capítulos de `thesis/05-tesis/`, correr:

```bash
"C:\Users\mboth\AppData\Local\Programs\Python\Python313\python.exe" "C:\nerfstudio_work\thesis\06-sitio-web\scripts\prepare_content.py"
```

Esto: borra y regenera `public/content/assets/`, vuelve a copiar todas las imágenes referenciadas desde los capítulos (con nombre único por capítulo, sin colisiones), reescribe los `.md` copiados con las rutas de imagen corregidas, y reconstruye `manifest.json` (títulos + extracto de "cierre del capítulo" para el margen derecho del sitio).

No hace falta reiniciar el dev server de Vite (`npm run dev`) si ya está corriendo — sirve los archivos de `public/` directamente; alcanza con refrescar la página en el navegador (si el navegador insiste en mostrar una versión vieja, sugerir un refresh forzado: `Ctrl+Shift+R`).

## Verificar que salió bien

Revisar la salida del script:

- **Si aparece alguna línea `[WARN] no existe: ...`** — significa que un capítulo referencia una imagen cuya ruta relativa no resuelve a un archivo real (por ejemplo, se movió/renombró el archivo, o hay un typo en la ruta del `![...]()`). Hay que arreglar esa referencia en el `.md` del capítulo (no en `public/content/`) y volver a correr el script. No lo dejes pasar en silencio.
- **La última línea reporta `Assets copiados: N`** — comprobar que el número tiene sentido (no bajó de golpe respecto a la última vez, lo cual indicaría que algo se dejó de copiar).

Si el script no imprime ningún `[WARN]`, la sincronización está completa y no hace falta decirle nada más al usuario al respecto — es un paso de higiene, no un entregable en sí mismo. Si aparece algo raro, sí avisar.
