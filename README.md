# Tesis — Reconstrucción 3D (Fotogrametría / NeRF / Gaussian Splatting)

Esta carpeta es un **duplicado curado** de los resultados de los tres casos de estudio trabajados en `C:\nerfstudio_work`. No se modificó ni se movió nada de las carpetas originales — todo lo de acá es una copia.

El objetivo es tener, para cada caso, **solo lo necesario para redactar la tesis**: el resumen del pipeline, los logs completos (para trazabilidad/metodología) y los resultados finales (checkpoints, exports `.ply`, videos de render) — sin las decenas de intentos fallidos, reintentos y carpetas de resolución intermedia (`images_2`, `images_4`, `images_8`, datasets de prueba, renders con downscale, etc.) que existen en las carpetas originales.

## Proyectos

| # | Carpeta | Carpeta original | Método de captura |
|---|---|---|---|
| 01 | [01-paraguas-vicentelopez](01-paraguas-vicentelopez) | `paraguas-vicentelopez/` | Dron (video) |
| 02 | [02-templete-central](02-templete-central) | `panteon-chacarita/templete-central/` | Dron (DJI) + cámara 360 (Insta360) |
| 03 | [03-panteon-asociacion-espanola](03-panteon-asociacion-espanola) | `panteon-chacarita/panteon-asociacion-catalana/` | Dron (DJI) + cámara 360 (Insta360) |

> **Nota sobre nombres (actualizada 01/09):** confirmado — el panteón es el de la **Asociación Española** de Socorros Mutuos (arquitecto Alejandro Christophersen, 1896, Decreto 525/2010), no de la Asociación Catalana. La prosa del Cap. 3 ya está corregida, y la carpeta curada de acá se renombró a `03-panteon-asociacion-espanola/` (con todas las rutas de imágenes de Cap5 actualizadas). La carpeta **original/cruda** (`panteon-chacarita/panteon-asociacion-catalana/`) mantiene su nombre de siempre — nunca se toca.

> `torre-mardel` no se incluyó porque no lo mencionaste en el pedido (era un cuarto sitio ya cerrado/exportado). Si también lo querés acá, lo agrego como `04-torre-mardel` con el mismo criterio.

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
