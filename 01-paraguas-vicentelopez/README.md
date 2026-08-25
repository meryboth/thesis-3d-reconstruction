# 01 — Paraguas Vicente López

Captura por **video de dron**. Es el caso más antiguo (procesado en junio 2026) y el único de los tres que además de NeRF/Gaussian Splatting incluye un pipeline clásico de **fotogrametría densa con COLMAP** (nube de puntos + malla).

Fuente completa: `paraguas-vicentelopez/` · Resumen original: [00-resumen/reporte-colmap-fotogrametria-densa.txt](00-resumen/reporte-colmap-fotogrametria-densa.txt) · Logs completos: [01-logs/](01-logs/)

## Resultados finales

### Nerfacto
`02-resultados-finales/nerfacto/`
- Checkpoint final: `2026-06-20_233157/nerfstudio_models/step-000029999.ckpt` (config.yml en la misma carpeta) — es la versión **v2** (segundo entrenamiento, el que se tomó como definitivo).
- Video de render: `renders/nerf-video.mp4` y `renders/nerf-custompath.mp4` (trayectoria custom).

### Splatfacto (Gaussian Splatting)
`02-resultados-finales/splatfacto/`
- Checkpoint final: `2026-06-20_191333/nerfstudio_models/step-000029999.ckpt`.
- Export final: `export/` → `splat.ply` (el `.ply` de gaussianas listo para visualizar/usar).
- Video de render: `renders/splat-video.mp4` y `renders/splat-custompath.mp4`.

### Fotogrametría densa COLMAP (nube de puntos + malla)
`02-resultados-finales/colmap-fotogrametria-densa/`
Según el reporte (`15_colmap_photogrammetry_report.txt`), se probaron tres niveles de calidad de stereo fusion:

| Calidad | Puntos fusionados | Estado |
|---|---|---|
| low | 1,589,360 (aprox., ver medium) | completado |
| medium | 1,589,360 | completado |
| **medium_high** | **2,107,280** | **completado — mejor resultado válido** |
| high_safe | 2,821,930 | **falló (STATUS=137, killed por OOM)** |

Se tomó **`medium_high`** como resultado final (el intento `high_safe` con más puntos quedó interrumpido). Archivos incluidos:
- `fused_medium_high.ply` — nube de puntos densa (55 MB).
- `fused_medium_high_clean.ply` — versión limpia/filtrada (13 MB).
- `meshed-poisson-medium-high.ply` — malla Poisson sobre esa nube (15 MB).
- `meshed-poisson-clean-trim5.ply` — malla Poisson sobre la nube limpia, trim=5 (30 MB).

## Dataset

`03-datasets/dataset-dron/` — dataset Nerfstudio usado tanto para Nerfacto como para Splatfacto (config `data: ns-data-drone`): `images/` (resolución base), `transforms.json` (poses de cámara) y `sparse_pc.ply` (nube dispersa COLMAP).

## Notas para la tesis
- Es el único caso con comparación directa **COLMAP denso vs. NeRF vs. Gaussian Splatting** sobre el mismo sitio — puede servir como el ejemplo metodológico central para comparar los tres enfoques.
- Los logs completos (`01-logs/`) incluyen varios intentos de `stereo_fusion` con distintos perfiles de memoria (`_medium`, `_medium_high`, `_high_safe`) — útil si querés documentar el trade-off calidad/memoria en la tesis.
