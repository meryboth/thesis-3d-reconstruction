# 00-auditoria/ — índice de análisis y reportes comparativos

Esta carpeta junta los análisis **cross-sitio** (comparan entre Paraguas/Templete/Panteón, no son de un solo caso de estudio) generados por los scripts de `04-notebooks/scripts/`. Todo acá es regenerable — si algo queda desactualizado, correr de nuevo el script correspondiente.

Los análisis **por sitio** (nube de puntos, malla, Gaussian Splat, trayectoria de cámara — de un solo caso de estudio) NO están acá: quedan justo al lado del artefacto que describen, dentro de `0X-<caso>/02-resultados-finales/` y `0X-<caso>/03-datasets/` (buscar `*-metadata.json` / `*-metrics.log`).

## Qué hay en cada carpeta

| Carpeta | Contenido | Generado por | Estado |
|---|---|---|---|
| [sfm-registration-comparison/](sfm-registration-comparison/sfm_registration_comparison.log) | Tabla DJI/Insta360/Híbrido × Templete+Panteón: % de registro reportado vs. real, incluye el hallazgo de componentes COLMAP mal reportados y la segunda corrida híbrida de Templete (0,63% real) | `analyze_sfm_registration_comparison.py` | ✅ completo |
| [hybrid-cross-camera-matching/](hybrid-cross-camera-matching/hybrid-cross-camera-matching.log) | Calidad de matching (inliers post-RANSAC) DJI-DJI vs. Insta360-Insta360 vs. DJI-Insta360, sobre `database.db` de la 2da corrida híbrida de Templete Central (H4) | `analyze_hybrid_cross_camera_matching.py` | ✅ completo |
| [output-weights/](output-weights/output_weights.log) | Peso de archivo final (checkpoint, export, malla) por sitio/método/técnica | `analyze_output_weights.py` | ✅ completo |
| [failure-rate/](failure-rate/failure_events.log) | Fallos catastróficos e inestabilidad de convergencia detectados en logs de procesamiento/entrenamiento | `analyze_failure_rate.py` | ✅ completo |
| [processing-time/](processing-time/processing_time.log) | Tiempo real de entrenamiento y render por sitio/método/etapa | `analyze_processing_time.py` | ✅ completo |
| [fidelidad-geometrica/](fidelidad-geometrica/) | Grillas Foto\|Nerfacto\|Splatfacto (5 frames por sitio/método) para la inspección visual cualitativa del Cap. 4 (4.8) | `build_fidelity_comparisons.py` | ⚠️ falta la columna SfM (ver `LEEME.txt` en cada subcarpeta — necesita screenshot manual desde RealityScan/CloudCompare) |
| [colmap-dji-insta360/](colmap-dji-insta360/) | Auditoría propia (no de Claude) sobre el intento de COLMAP híbrido de Panteón | script del usuario | histórico, resultado: sin datos exportados |
| `mesh-artifacts-index.csv` | Índice de mallas texturizadas analizadas | `analyze_textured_meshes.py` (root de cada resultado) | ✅ |
| [charts/](charts/) | 6 gráficos comparativos cross-sitio: registro SfM (reportado vs. real), peso de archivo, tiempo de entrenamiento, fallos, PSNR/SSIM, LPIPS | `build_comparison_charts.py` | ✅ completo |

### Gráficos por artefacto (no cross-sitio, quedan junto al artefacto)

Desde que se instaló `matplotlib`, estos dos scripts generan además PNGs junto a cada `*-metadata.json`:

- `analyze_gaussian_splats.py` → por cada `splat.ply`: histograma de opacidad, histograma de escala, scatter espacial XY/XZ (`gaussian-splat-*.png` en `02-resultados-finales/*/splatfacto/export/`).
- `analyze_dense_clouds.py` → por cada nube densa: scatter XY/XZ (`*-scatter.png` en `02-resultados-finales/colmap-fotogrametria*/`).

**Benchmark PSNR/SSIM/LPIPS** (`analyze_render_benchmark.py`) — ✅ completo (incluye el fix del bug de alineación de Paraguas y Templete DJI). Resultado en `0X-<caso>/02-resultados-finales/benchmark-comparison.log` (por sitio) y `.../render/render-benchmark-metrics.log` (por técnica) — **no en esta carpeta**, porque es un análisis por-sitio, no cross-sitio. Los gráficos `05_psnr_ssim_por_sitio.png` y `06_lpips_por_sitio.png` de `charts/` sí resumen esto a nivel cross-sitio.

## Pendiente de generar

- **Cobertura reconstruida (%)** — B4, bloqueada hasta tener datos del híbrido.
- **Checklist web/reproducibilidad (B5)** — 100% manual, no se genera acá.
- **Screenshots de mallas SfM** para completar `fidelidad-geometrica/` — no hay renderer 3D viable en este entorno para los `.obj` (ver `LEEME.txt` en cada subcarpeta).

## Cómo regenerar todo

```bash
cd thesis/04-notebooks/scripts
python analyze_sfm_registration_comparison.py
python analyze_hybrid_cross_camera_matching.py
python analyze_output_weights.py
python analyze_failure_rate.py
python analyze_processing_time.py
python build_fidelity_comparisons.py
python analyze_render_benchmark.py   # tarda ~2h en CPU (LPIPS)
python analyze_gaussian_splats.py    # ahora tambien genera PNGs
python analyze_dense_clouds.py       # ahora tambien genera PNGs
python build_comparison_charts.py    # correr al final, lee la salida de los anteriores
```
