# 02 — Templete Central (Panteón Chacarita)

Dos capturas independientes del mismo sitio: **dron DJI** y **cámara 360 Insta360**. Ambas se procesaron con RealityScan → COLMAP → Nerfstudio (Nerfacto + Splatfacto).

Fuente completa: `panteon-chacarita/templete-central/` · Resumen original (pipeline DJI): [00-resumen/experiment-summary-dji.txt](00-resumen/experiment-summary-dji.txt) · Logs completos: [01-logs/](01-logs/)

## DJI (1234 imágenes → 1232 registradas, 100%)

`02-resultados-finales/dji/`

- **Nerfacto** (`nerfacto/2026-08-24_220201/`): entrenado sobre un subset de **308 vistas** (muestreo ~1 cada 4, por límite de memoria del `ParallelDataManager`), 30.000 iteraciones, **COMPLETADO**. Render final: `nerfacto/render/templete-central-nerfacto-train.mp4`.
- **Splatfacto** (`splatfacto/2026-08-24_232220/`): entrenado con las **1232 vistas completas**, downscale ×8 (≈477×267 px), 30.000 iteraciones, **COMPLETADO**. Export final: `splatfacto/export/splat.ply` (328.801 gaussianas totales → 315.787 exportadas, 96.04%). Render final: `splatfacto/render/templete-central-splat-ds8-train.mp4`.

> Nota: hubo dos corridas de Splatfacto ds8 (`2026-08-24_225316` y `2026-08-24_232220`); se tomó la **segunda** (más reciente) como definitiva.

## Insta360

`02-resultados-finales/insta360/`

- **Nerfacto** (`nerfacto/2026-08-12_233328/`): entrenado y renderizado. Video: `nerfacto/render/templete-central-insta360-nerfacto-dataset-traj.mp4`.
- **Splatfacto** (`splatfacto/2026-08-13_014408/`): entrenado y renderizado. Export: `splatfacto/export/splat.ply`. Video: `splatfacto/render/templete-central-insta360-splatfacto-dataset-traj.mp4`.

*(No se encontró un `experiment-summary` numérico específico para la corrida Insta360 de este sitio como sí existe para Panteón Asociación Catalana; los detalles están en `01-logs/`.)*

## Datasets

`03-datasets/`, identificados a partir del campo `data:` de cada `config.yml` final:
- `dji/dataset-nerfacto-308-subset/` — subset de 308 vistas usado para entrenar Nerfacto DJI (config `data: /workspace/ns-from-realityscan-nerf308`).
- `dji/dataset-splatfacto-1232-full/` — dataset completo de 1232 imágenes usado para Splatfacto DJI (config `data: /workspace/ns-from-realityscan`). `images/` a resolución base + `transforms.json` + `sparse_pc.ply`.
- `insta360/dataset-insta360/` — dataset usado tanto para Nerfacto como Splatfacto Insta360 (config `data: /workspace/sfm-realitycapture/nerfstudio-insta360`).

## Incidentes / decisiones relevantes (del resumen original)
1. COLMAP corrido directamente por Nerfstudio sobre las 1234 imágenes DJI solo registró 8 imágenes al inicio, pese a tener muchos matches (17.457 pares verificados, ~1.495 inliers/par).
2. Un segundo intento con mapper más permisivo llegó a Global Bundle Adjustment pero terminó en OOM (contenedor con 6 GB).
3. Se optó por usar el COLMAP **exportado desde RealityScan**, que sí registró el 100% de las imágenes (1232/1232) — este es el que se usó para entrenar Nerfacto y Splatfacto.
4. RealityScan reportó reprojection error = 0.000000 px — se aclara en el log que **no es una métrica de precisión válida**, sino una característica del modelo COLMAP exportado por esa herramienta.
