# Divergencia entre los `.md` y el `.docx`

**Alineados.** El `.docx` refleja exactamente los `.md` de `05-tesis/`:
todas las figuras y tablas tienen epígrafe ahí y las cuatro series
(`Tabla`, `Figura`, `Gráfico`, `Imagen`) ya están correlativas por
capítulo. El generador no tuvo que renumerar ni agregar nada.

## Epígrafes que cambiaron de número

Ninguno.

## Epígrafes agregados sobre la marcha

Objetos sin epígrafe en el `.md`, a los que el generador les puso uno usando
[`epigrafes.py`](epigrafes.py) o el texto alternativo de la propia imagen.
Sólo viven en el `.docx` hasta que se corra `propagar_epigrafes.py`.

Ninguno.
