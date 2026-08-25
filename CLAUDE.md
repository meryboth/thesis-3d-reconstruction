# Contexto — Tesis: Reconstrucción 3D de patrimonio (Fotogrametría / NeRF / Gaussian Splatting)

Esta carpeta es la versión **curada y duplicada** (no los originales) de los resultados de tres casos de estudio de reconstrucción 3D, lista para redactar la tesis. Contexto más amplio del workspace (incluyendo las carpetas de trabajo crudas de donde sale todo esto) en [../CLAUDE.md](../CLAUDE.md). Índice completo y detalle de qué se incluyó/excluyó: [README.md](README.md).

## Los 3 casos de estudio

| # | Carpeta | Captura | Comparación de métodos |
|---|---|---|---|
| 1 | [01-paraguas-vicentelopez](01-paraguas-vicentelopez/README.md) | Dron (video) | COLMAP denso (nube+malla Poisson) **vs.** Nerfacto **vs.** Splatfacto — único con los 3 métodos |
| 2 | [02-templete-central](02-templete-central/README.md) | Dron DJI + Insta360 (360°) | Nerfacto vs. Splatfacto, por cada método de captura |
| 3 | [03-panteon-asociacion-catalana](03-panteon-asociacion-catalana/README.md) | Dron DJI + Insta360 (360°) | Nerfacto vs. Splatfacto, por cada método de captura |

> Nombre del sitio 3 sin confirmar por la usuaria (¿"Asociación Catalana" o "Asociación Española"?) — ver nota en el README raíz.

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

## Qué falta / qué no está acá

- Pirámides de resolución (`images_2/4/8`) — regenerables automáticamente por Nerfstudio, no se duplicaron.
- Corridas fallidas, de prueba, o subsets alternativos — quedan solo en las carpetas de trabajo originales (ver `../CLAUDE.md`).
- `torre-mardel` (4to sitio) — no incluido, no fue pedido.
- Proyectos internos de RealityScan (`realityscan-mesh*`, `.dat`) — formato propietario no exportable directamente, no se copiaron.

## Publicación / hosting

Esta carpeta ES un repo git, con remoto `https://github.com/meryboth/thesis-3d-reconstruction.git`. El `.gitignore` deja afuera lo que no entra o no conviene versionar en GitHub sin Git LFS/plan pago: `03-datasets/` (~14 GB, datasets de imágenes), `*.ckpt` (~1.9 GB, checkpoints), `textured-mesh.obj`/textura (~8.4 GB, mallas RealityScan) y `nube-densa.xyz` (~2.2 GB). Todo eso sigue existiendo en la copia local de esta carpeta, solo que no viaja al remoto. Detalle completo de qué se subió vs. qué quedó afuera: ver la sección correspondiente en [README.md](README.md).

Pendiente si se quiere completar el backup: los `.ckpt` y `.xyz` entrarían con Git LFS pero requieren plan pago de GitHub (cuota gratis: 1 GB); los `.obj` (~4 GB c/u) y `03-datasets/` necesitan un destino aparte — Zenodo recomendado (DOI citable, apropiado para dataset de tesis).
