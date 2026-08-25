# 03 — Panteón Asociación Catalana (Panteón Chacarita)

> Ver nota en el [README raíz](../README.md) sobre el nombre de este proyecto ("Panteón Asoc Esp" vs. el nombre real de la carpeta, `asociacion-catalana`).

Dos capturas independientes: **dron DJI** (1507 imágenes) y **cámara 360 Insta360** (365 imágenes). Ambas procesadas con RealityScan/COLMAP → Nerfacto + Splatfacto.

Fuente completa: `panteon-chacarita/panteon-asociacion-catalana/` · Resúmenes originales: [00-resumen/experiment-summary-dji.txt](00-resumen/experiment-summary-dji.txt), [00-resumen/experiment-summary-insta360.txt](00-resumen/experiment-summary-insta360.txt) · Logs completos: [01-logs/](01-logs/)

## DJI (1507 imágenes → 1506 registradas, 99.93%)

`02-resultados-finales/dji/`

SfM (COLMAP): 532.339 puntos 3D, 5.820.948 observaciones, error de reproyección medio 0.948 px.

- **Nerfacto** (`nerfacto/2026-08-23_191033/`): entrenado sobre subset de **302 vistas** (~1 de cada 5, por presión de memoria del `ParallelDataManager`), 30.000 iteraciones, **COMPLETADO**. Render final: `nerfacto/render/panteon-catalan-nerfacto-train.mp4`.
- **Splatfacto** (`splatfacto/2026-08-24_004501/`): entrenado con las **1507 imágenes completas**, downscale ×8 (≈480×270 px), 30.000 iteraciones, **COMPLETADO**. Export: `splatfacto/export/splat.ply` (319.958 gaussianas totales → 315.327 exportadas, 98.55%). Render final: `splatfacto/render/panteon-catalan-splat-ds8-train.mp4`.

## Insta360 (365 imágenes → 311 registradas, 85.21%)

`02-resultados-finales/insta360/`

54 frames sin datos de cámara, descartados.

- **Nerfacto** (`nerfacto/2026-08-13_132710/`): entrenado y renderizado. Video: `nerfacto/render/panteon-catalana-insta360-nerfacto-dataset-traj.mp4`.
- **Splatfacto** (`splatfacto/2026-08-13_153432/`): entrenado y renderizado. Export: `splatfacto/export/splat.ply` (357.796 gaussianas totales → 353.894 exportadas). Video: `splatfacto/render/panteon-catalana-insta360-splatfacto-dataset-traj.mp4`.

## Datasets

`03-datasets/`, identificados a partir del campo `data:` de cada `config.yml` final:
- `dji/dataset-nerfacto-302-subset/` — subset de 302 vistas usado para Nerfacto DJI (config `data: /workspace/sfm-djionly/colmap-nerfstudio-nerf300`).
- `dji/dataset-splatfacto-1507-full/` — dataset completo de 1507 imágenes usado para Splatfacto DJI (config `data: /workspace/sfm-djionly/colmap-nerfstudio`). `images/` a resolución base + `transforms.json` + `sparse_pc.ply`.
- `insta360/dataset-insta360/` — dataset usado tanto para Nerfacto como Splatfacto Insta360 (config `data: /workspace/sfm-realityscan/insta360/nerfstudio`).

## Incidentes / decisiones relevantes (del resumen original, variante DJI)
- El dataset completo de 1507 imágenes generaba presión excesiva de memoria en Nerfacto (`ParallelDataManager`) → de ahí el subset de 302 vistas.
- El intento de exportar una point cloud desde Nerfacto quedó bloqueado durante la carga de datos del `ParallelDataManager` (no se pudo completar).
- Entrenar Splatfacto con downscale ×4 sobre las 1507 imágenes produjo **OOM**; con downscale ×8 sí se completó correctamente.
- Los renders finales de la variante DJI (tanto Nerfacto como Splatfacto) se completaron recién el **25/08/2026**, después de que se escribiera el `experiment-summary.txt` original (por eso ese archivo todavía dice "en procesamiento" / "pendiente" en la sección de renders — ya están completos y son los que están copiados acá).
