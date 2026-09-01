# Contexto — Tesis: Reconstrucción 3D de patrimonio (Fotogrametría / NeRF / Gaussian Splatting)

Esta carpeta es la versión **curada y duplicada** (no los originales) de los resultados de tres casos de estudio de reconstrucción 3D, lista para redactar la tesis. Contexto más amplio del workspace (incluyendo las carpetas de trabajo crudas de donde sale todo esto) en [../CLAUDE.md](../CLAUDE.md). Índice completo y detalle de qué se incluyó/excluyó: [README.md](README.md).

## Los 3 casos de estudio

| # | Carpeta | Captura | Comparación de métodos |
|---|---|---|---|
| 1 | [01-paraguas-vicentelopez](01-paraguas-vicentelopez/README.md) | Dron (video) | COLMAP denso (nube+malla Poisson) **vs.** Nerfacto **vs.** Splatfacto — único con los 3 métodos |
| 2 | [02-templete-central](02-templete-central/README.md) | Dron DJI + Insta360 (360°) | Nerfacto vs. Splatfacto, por cada método de captura |
| 3 | [03-panteon-asociacion-espanola](03-panteon-asociacion-espanola/README.md) | Dron DJI + Insta360 (360°) | Nerfacto vs. Splatfacto, por cada método de captura |

> Nombre del sitio 3 resuelto (01/09): **Asociación Española** (arquitecto Alejandro Christophersen, 1896), no Catalana. Corregido en la prosa del Cap. 3 y renombrada la carpeta curada a `03-panteon-asociacion-espanola/`. La carpeta cruda (`panteon-chacarita/panteon-asociacion-catalana/`) mantiene su nombre original, como todas las carpetas crudas.

## Estructura interna de cada `0X-<proyecto>/`

```
0X-<proyecto>/
├── README.md                  ← pipeline, métricas (puntos 3D, % registro, gaussianas exportadas), decisiones/incidentes
├── 00-resumen/                ← experiment-summary.txt originales (fuente primaria de las métricas del README)
├── 01-logs/                   ← copia COMPLETA de logs/ — trazabilidad de cada corrida, reintentos, fallos (OOM, etc.)
├── 02-resultados-finales/     ← config.yml + checkpoint (.ckpt) + export (splat.ply) + video (.mp4) de CADA modelo final
│   └── [dji|insta360]/{nerfacto,splatfacto}/
└── 03-datasets/                ← dataset(s) Nerfstudio REALES usados (verificados vía el campo `data:` de cada config.yml)
    └── [dji|insta360]/         ← images/ (resolución base) + transforms.json + sparse_pc.ply
```

Antes de citar una métrica o afirmar "esta fue la versión final", **revisar el README del proyecto correspondiente** — ya tiene la evidencia (path de log, config, o cálculo) de por qué esa corrida específica se tomó como definitiva y no otra (varios sitios tuvieron 2-3 intentos de la misma corrida antes de la buena).

`02-templete-central/03-datasets/hibrido/` — dataset DJI+Insta360 combinado (794 imágenes, 100% registradas), rescatado el 25/08 de un componente COLMAP que el wrapper de Nerfstudio había reportado como fallo casi total (ver `00-auditoria/`). Panteón no tiene su equivalente todavía (esa corrida se está re-haciendo).

`02-templete-central/01-experimentos/hybrid-dji-insta360-colmap/` — corridas propias de la usuaria (no forman parte de la estructura curada `01-logs/02-resultados-finales/03-datasets`) de COLMAP nativo sobre el mismo dataset híbrido de 794 imágenes, para investigar H4 en profundidad. La corrida `run-20260825-183608` dio un resultado real de solo 5/794 imágenes registradas (0,63%, verificado leyendo `images.bin` directamente) — a diferencia del rescate de arriba, acá no hay componente oculto exitoso, es un fallo real. El análisis de `database.db` de esa corrida (`analyze_hybrid_cross_camera_matching.py`, ver `00-auditoria/hybrid-cross-camera-matching/`) muestra que los matches DJI↔Insta360 son sistemáticamente mucho más débiles (43 inliers promedio, máximo 183) que los matches dentro de un mismo dispositivo (689 DJI-DJI, 189 Insta360-Insta360) — el hallazgo geométrico central que explica por qué el dataset híbrido da resultados tan distintos entre corridas (100% vs. 0,63% de registro). Integrado en `thesis/05-tesis/capitulo5_analisis_resultados/` (sección 5.5, H4).

## Scripts de análisis y auditoría

Todos los scripts de análisis viven en **[04-notebooks/scripts/](04-notebooks/scripts/)** (junto a los notebooks Colab originales que replican) — no dejar scripts sueltos en la raíz de `thesis/`. Corren con el Python local (`C:\Users\mboth\AppData\Local\Programs\Python\Python313\python.exe`; solo tiene numpy/scipy/plyfile/PIL/opencv + torch/lpips/scikit-image instalados para el benchmark de renders — no pandas/matplotlib, por eso la salida es JSON+log en vez de gráficos/PDF).

| Script | Qué hace | Salida |
|---|---|---|
| `analyze_dense_clouds.py` | Métricas geométricas de nubes de puntos densas (COLMAP/RealityScan) | junto a cada nube, en `02-resultados-finales/` |
| `analyze_textured_meshes.py` | Métricas de mallas texturizadas (.obj) | junto a cada malla |
| `analyze_camera_trajectories.py` | Trayectoria de cámaras por dataset (`03-datasets/`) | junto a cada `transforms.json` |
| `analyze_gaussian_splats.py` | Métricas de cada `splat.ply` (gaussianas, opacidad, escala) | junto a cada export |
| `analyze_render_benchmark.py` | PSNR/SSIM/LPIPS render vs. ground truth (los 3 casos, DJI/Insta360) | `02-resultados-finales/*/render/` |
| `analyze_sfm_registration_comparison.py` | Tabla comparativa de registro SfM (DJI/Insta360/híbrido, Templete+Panteón), incluye el hallazgo de componentes COLMAP mal reportados | `00-auditoria/sfm-registration-comparison/` |
| `analyze_output_weights.py` | Peso de archivo final por técnica (Cap. 4, 4.3.5 / Cap. 2, 2.6.2) | `00-auditoria/output-weights/` |
| `analyze_failure_rate.py` | Tasa de fallos (catastrófico/inestabilidad) por patrones en logs (Cap. 4, 4.9) | `00-auditoria/failure-rate/` |
| `analyze_processing_time.py` | Tiempo de procesamiento por etapa, vía mtime de `config.yml`→checkpoint en las carpetas **originales** (no `thesis/`, que tiene fechas de copia) | `00-auditoria/processing-time/` |
| `parse_colmap_images_bin.py` / `colmap_component_to_nerfstudio.py` | Utilidades para leer/exportar componentes COLMAP fragmentados sin Nerfstudio/COLMAP instalado | usados ad-hoc |

`00-auditoria/` acumula las tablas comparativas cross-sitio (no específicas de un solo caso de estudio) — todas regenerables corriendo el script correspondiente.

Dos scripts adicionales generan gráficos puntuales para los capítulos de tesis (no cross-sitio en el sentido de `build_comparison_charts.py`, se corren aparte): `build_psnr_vs_complejidad.py` (→ `00-auditoria/charts/07_psnr_vs_complejidad.png`, usado en Cap. 5) y `build_pipeline_diagram.py` (→ `05-tesis/capitulo6_pipeline_definitivo/media/pipeline-definitivo.png`).

## Capítulos de tesis (`05-tesis/`)

Cap. 1–3 fueron redactados/editados con la usuaria. **Cap. 4 (Diseño Experimental) fue completado el 25/08** rellenando todos los placeholders `[Completar]` con datos reales de `00-auditoria/` (quedan abiertos solo: valor exacto de fps de extracción, detalle de zonas de acceso restringido del Panteón, y la coordinación de la validación de reproducibilidad externa de B5 — genuinamente pendientes de la usuaria, no inventados). **Cap. 5 (Análisis de Resultados) y Cap. 6 (Pipeline Definitivo y Propuesta HBIM) son borradores nuevos, generados el 25/08** a partir de la evidencia ya recopilada en `00-auditoria/` y en cada caso — la usuaria los va a reescribir/editar y sumarles citas; **B1 (preprocesamiento ComfyUI) nunca se ejecutó y así está documentado explícitamente en ambos capítulos**, sin resultados inventados.

**Regla de separación entre capítulos (corregida el 25/08, no romper de nuevo):** el Cap. 4 se completó en una primera pasada volcando resultados, imágenes e interpretación directamente dentro de cada benchmark (B1–B5) — la usuaria marcó correctamente que eso rompe la estructura estándar de tesis (diseño vs. resultados) y duplicaba contenido con el Cap. 5. Se corrigió: **Cap. 4 = solo diseño** (hipótesis, variables, protocolo de cada benchmark, qué se va a medir) **sin tablas de resultados, sin imágenes de resultados, sin interpretación** — cada benchmark cierra con una línea "Resultados: ver Capítulo 5, sección X". **Cap. 5 = todos los resultados**, con las tablas, las ~19 imágenes/gráficos y toda la interpretación. La única tabla de datos que se dejó en el Cap. 4 es la Tabla 4.6 (conteo de imágenes train/eval por dataset, sección 4.7) porque describe la composición del dataset/setup del experimento, no un resultado del mismo. Al escribir o editar estos capítulos en el futuro, mantener esa separación.

Cap. 7 (Conclusiones) existe como borrador de partida (generado el 27/08) — la usuaria lo reescribe a mano.

## ⚠️ Regla no-negociable (27/08): no escribir más prosa de la tesis — EXCEPTO Cap. 5

A partir del 27/08 la usuaria escribe a mano el texto de la tesis (conclusiones, explicaciones, cualquier prosa nueva) — **no editar ni generar texto propio en los capítulos (`05-tesis/*.md`) ni en el sitio web**. Esto reemplaza la dinámica anterior (borradores generados a partir de `00-auditoria/` para que la usuaria los reescribiera).

**Excepción explícita, dada el mismo día: Capítulo 5 (Análisis de Resultados).** La usuaria todavía no empezó a escribirlo — pidió específicamente que, cuando estén las conclusiones/resultados de una corrida, **yo siga redactando ese capítulo** (igual que antes) y ella lo edita después. La regla de "no más prosa" aplica tal cual a Cap. 1–4, 6, 7 y a cualquier prosa que ella ya haya empezado a escribir a mano; en Cap. 5 sigo escribiendo salvo que ella diga lo contrario.

**Segunda excepción, más acotada, del 29/08:** dentro del Capítulo 6, la sección que documenta la POC de segmentación de nubes de puntos (`thesis/04-notebooks/scripts/poc_segmentation_multi_site.py`, visor en `06-sitio-web/src/components/PointCloudSegmentor.jsx`) y su vínculo con la propuesta HBIM/Revit de la sección 6.3 — la usuaria pidió explícitamente que yo la redacte (capturas + bibliografía + prosa explicando el impacto en el pipeline), después de que yo señalara el conflicto con la regla de "no más prosa" y ella eligiera la excepción puntual en vez de solo prepararle los materiales. Esto NO reabre el resto del Cap. 6 (ni Cap. 1/2/3/4/7): si se pide tocar otra parte del capítulo más adelante, volver a confirmar en vez de asumir que la excepción se generalizó.

Sigue permitido en el resto de los capítulos, porque no es "escribir la tesis" sino soporte puntual:
- Identificar/corregir faltas de ortografía.
- Sumar entradas de bibliografía o de glosario (a pedido, como ya se hizo).
- Generar imágenes, gráficos o diagramas que la usuaria pida (con leyenda factual mínima, sin análisis) — esto vale para cualquier capítulo, no solo Cap. 5.
- Todo lo que no sea contenido de la tesis: código, scripts de análisis, datasets, entrenamientos, la web como aplicación (no su contenido), etc.

Ante la duda de si algo cuenta como "escribir texto de la tesis" fuera de Cap. 5, preguntar antes de tocar un `.md` de `05-tesis/`.

## ⚠️ Regla no-negociable: capítulos y sitio web SIEMPRE sincronizados

Cada vez que se cree, edite o reescriba cualquier `.md` dentro de `05-tesis/`, correr la skill **`sync-tesis-web`** (o directamente `06-sitio-web/scripts/prepare_content.py`) antes de dar la tarea por terminada — sin que la usuaria tenga que pedirlo. `06-sitio-web/public/content/` es 100% derivado de `05-tesis/`, nunca se edita a mano ahí. Pedido explícito de la usuaria (26/08): que ambos queden siempre completamente sincronizados.

## Sitio web (`06-sitio-web/`)

App Vite + React (solo frontend) creada el 26/08, versión online de la tesis: lectura continua de los 6 capítulos con nav de capítulos a la izquierda y la conclusión del capítulo activo en el margen derecho (sticky, se actualiza con `IntersectionObserver` al scrollear). El contenido **no está pegado a mano** — `06-sitio-web/scripts/prepare_content.py` lee los `.md` de `05-tesis/` directamente, copia imágenes a `public/content/assets/` (namespaced por capítulo, sin colisiones) y arma `manifest.json`. **Volver a correr ese script después de editar cualquier capítulo.** Ver `06-sitio-web/README.md` para el detalle completo. Node.js se instaló en esta sesión (no estaba, `winget install OpenJS.NodeJS.LTS`) — en Bash/PowerShell hay que refrescar el PATH manualmente en cada llamada (`$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")`), el proceso persistente de la terminal no lo recoge solo. Pendiente explícito de la usuaria: sumar GIFs de los videos de captura para dar contexto de cada relevamiento.

## Qué falta / qué no está acá

- Pirámides de resolución (`images_2/4/8`) — regenerables automáticamente por Nerfstudio, no se duplicaron.
- Corridas fallidas, de prueba, o subsets alternativos — quedan solo en las carpetas de trabajo originales (ver `../CLAUDE.md`).
- `torre-mardel` (4to sitio) — no incluido, no fue pedido.
- Proyectos internos de RealityScan (`realityscan-mesh*`, `.dat`) — formato propietario no exportable directamente, no se copiaron.

## Publicación / hosting

Esta carpeta ES un repo git, con remoto `https://github.com/meryboth/thesis-3d-reconstruction.git`. El `.gitignore` deja afuera lo que no entra o no conviene versionar en GitHub sin Git LFS/plan pago: `03-datasets/` (~14 GB, datasets de imágenes), `*.ckpt` (~1.9 GB, checkpoints), `textured-mesh.obj`/textura (~8.4 GB, mallas RealityScan) y `nube-densa.xyz` (~2.2 GB). Todo eso sigue existiendo en la copia local de esta carpeta, solo que no viaja al remoto. Detalle completo de qué se subió vs. qué quedó afuera: ver la sección correspondiente en [README.md](README.md).

Pendiente si se quiere completar el backup: los `.ckpt` y `.xyz` entrarían con Git LFS pero requieren plan pago de GitHub (cuota gratis: 1 GB); los `.obj` (~4 GB c/u) y `03-datasets/` necesitan un destino aparte — Zenodo recomendado (DOI citable, apropiado para dataset de tesis).
