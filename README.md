# Tesis — Reconstrucción 3D (Fotogrametría / NeRF / Gaussian Splatting)

## Qué hay en este repo

Este repo tiene tres partes:

- **[`05-tesis/`](05-tesis/)** — el texto de la tesis en sí, capítulo por capítulo (Markdown), con el análisis de resultados, el marco teórico, la propuesta de pipeline y las conclusiones.
- **[`06-sitio-web/`](06-sitio-web/)** — app Vite + React que publica la tesis online: lectura de los 7 capítulos, catálogo del archivo digital (splats navegables en 3D) y una sección de scripts (índice navegable con visor de código resaltado de todos los scripts de análisis citados en el Cap. 5). Deployada en Vercel.
- **Datos y análisis de soporte**, curados a partir de las carpetas de trabajo originales en `C:\nerfstudio_work` (nunca modificadas): `01-paraguas-vicentelopez/`, `02-templete-central/` y `03-panteon-asociacion-espanola/` (resultados por caso de estudio, ver tabla abajo), **[`00-auditoria/`](00-auditoria/)** (comparativas cruzadas entre los tres sitios) y **[`04-notebooks/scripts/`](04-notebooks/scripts/)** (todos los scripts de análisis, con sus notebooks de Colab equivalentes).

El objetivo de la parte de datos es tener, para cada caso, **solo lo necesario para redactar la tesis**: el resumen del pipeline, los logs completos (para trazabilidad/metodología) y los resultados finales (checkpoints, exports `.ply`, videos de render) — sin las decenas de intentos fallidos, reintentos y carpetas de resolución intermedia (`images_2`, `images_4`, `images_8`, datasets de prueba, renders con downscale, etc.) que existen en las carpetas originales.

## Los tres casos de estudio

| # | Carpeta | Carpeta original | Método de captura |
|---|---|---|---|
| 01 | [01-paraguas-vicentelopez](01-paraguas-vicentelopez) | `paraguas-vicentelopez/` | Dron (video) |
| 02 | [02-templete-central](02-templete-central) | `panteon-chacarita/templete-central/` | Dron (DJI) + cámara 360 (Insta360) |
| 03 | [03-panteon-asociacion-espanola](03-panteon-asociacion-espanola) | `panteon-chacarita/panteon-asociacion-catalana/` | Dron (DJI) + cámara 360 (Insta360) |

> **Nota sobre nombres (actualizada 01/09):** confirmado — el panteón es el de la **Asociación Española** de Socorros Mutuos (arquitecto Alejandro Christophersen, 1896, Decreto 525/2010), no de la Asociación Catalana. La prosa del Cap. 3 ya está corregida, y la carpeta curada de acá se renombró a `03-panteon-asociacion-espanola/` (con todas las rutas de imágenes de Cap5 actualizadas). La carpeta **original/cruda** (`panteon-chacarita/panteon-asociacion-catalana/`) mantiene su nombre de siempre — nunca se toca.

> **Torre Mardel** no es un cuarto proyecto curado con su propia carpeta `0X-*` — pero sí está incluido, como experimento adicional del Cap. 5 (sección 5.11): reconstrucción a partir de un video de dron de terceros (no un relevamiento propio), usado para validar el pipeline sobre material que no controlamos nosotros. Sus datos están en [`00-auditoria/torre-mardel-eval/`](00-auditoria/torre-mardel-eval/).

## Estructura interna de cada proyecto

```
0X-<proyecto>/
├── README.md                  ← resumen del pipeline, métricas y decisiones clave
├── 00-resumen/                ← el/los .txt de experiment-summary originales (texto plano)
├── 01-logs/                   ← copia completa de logs/ (todas las corridas, incidentes, reintentos)
├── 02-resultados-finales/
│   ├── [dji|insta360]/        ← cuando el sitio tiene más de un método de captura
│   │   ├── nerfacto/          ← config.yml + checkpoint final + video de render
│   │   └── splatfacto/        ← config.yml + checkpoint final + splat.ply exportado + video de render
│   └── colmap-fotogrametria-densa/   ← (solo Paraguas) nube de puntos densa + malla Poisson
└── 03-datasets/                ← dataset(s) Nerfstudio efectivamente usados para entrenar los modelos de arriba
    └── [dji|insta360]/         ← images/ (resolución base, sin pirámide) + transforms.json + sparse_pc.ply
```

Los **logs completos** (`01-logs/`) sí se copiaron enteros porque son texto plano y pesan poco (17–31 MB por proyecto) — ahí queda documentado todo el proceso de prueba y error por si necesitás justificar metodológicamente alguna decisión en la tesis, sin tener que volver a las carpetas de trabajo originales.

Los **datasets** (`03-datasets/`) se identificaron leyendo el campo `data:` de cada `config.yml` final (no se adivinaron) — son exactamente las imágenes + `transforms.json` (poses de cámara) + `sparse_pc.ply` (nube dispersa COLMAP) que alimentaron cada entrenamiento. Cuando Nerfacto se entrenó sobre un subset (por límite de memoria) y Splatfacto sobre el dataset completo, se incluyeron **ambos** datasets por separado.

Lo que **no** se copió (queda solo en las carpetas originales, por si lo necesitás): pirámides de resolución (`images_2/4/8`, regenerables automáticamente por Nerfstudio), corridas fallidas o de prueba, frames de render individuales (solo se guardó el `.mp4` final), y los proyectos internos de RealityScan (`realityscan-mesh*`, formato propietario `.dat`, no exportable directamente).

Dos de los tres proyectos (Templete Central y Panteón Asociación Española) tienen además una carpeta `01-experimentos/` — corridas exploratorias del dataset híbrido DJI+Insta360 (bases de datos COLMAP, exports de prueba) que no forman parte de la estructura curada `01-logs/02-resultados-finales/03-datasets` y quedan fuera de GitHub (`.gitignore`) por su peso, aunque sí existen en la copia local.

## Tamaño y qué está en GitHub vs. solo local

Con logs + resultados finales + datasets, esta carpeta pesa ~28 GB localmente. El repo de GitHub (`meryboth/thesis-3d-reconstruction`) tiene un `.gitignore` que deja afuera lo que no entra o no conviene versionar ahí (~27 GB entre todo):

| Excluido de GitHub | Tamaño | Por qué | Dónde está |
|---|---|---|---|
| `03-datasets/` (imágenes de entrenamiento) | ~14 GB | Miles de archivos, impráctico en git plano | Solo copia local |
| Checkpoints `*.ckpt` (9 archivos) | ~1.9 GB | Superan 100 MB (límite de GitHub sin Git LFS) | Solo copia local |
| `textured-mesh.obj` + textura (3 sitios) | ~8.4 GB | Hasta ~4 GB c/u — superan incluso Git LFS (2 GB) | Solo copia local |
| `nube-densa.xyz` (2 sitios) | ~2.2 GB | ~1.1 GB c/u | Solo copia local |

Lo que **sí está en GitHub** (~977 MB, sin necesidad de Git LFS): todos los `README.md`/`CLAUDE.md`, `00-resumen/`, `01-logs/` completos, `config.yml`/`dataparser_transforms.json` de cada corrida, **todos los `splat.ply` exportados**, **todos los videos de render finales**, y los `.ply` de nube densa/malla Poisson más livianos de Paraguas. Es decir: toda la documentación, trazabilidad y los resultados visuales/cuantitativos finales — lo que falta es el material para *reproducir desde cero* (datasets crudos, pesos entrenados) y las mallas texturizadas de RealityScan.

Si en algún momento se quiere subir también lo excluido: los checkpoints y las nubes `.xyz` entrarían con Git LFS (pero requiere plan pago de GitHub, la cuota gratis es 1 GB); los `.obj` de ~4GB y los datasets de 14GB necesitan un destino aparte (Zenodo recomendado, da DOI citable).
