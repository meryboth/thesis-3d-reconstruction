"""
Graficos comparativos (matplotlib) a partir de las tablas ya generadas por
los demas scripts de analyze_*.py — no recalcula nada, solo visualiza.

Requiere matplotlib (instalado especificamente para esto).

Genera, en thesis/00-auditoria/charts/:
  01_sfm_registro_reportado_vs_real.png
  02_peso_archivo_por_tecnica.png
  03_tiempo_entrenamiento.png
  04_fallos_por_sitio.png
  05_psnr_ssim_por_sitio.png
  06_lpips_por_sitio.png
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

THESIS = Path(r"C:\nerfstudio_work\thesis")
AUDIT = THESIS / "00-auditoria"
OUT_DIR = AUDIT / "charts"

plt.rcParams.update({
    "figure.dpi": 140,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.axisbelow": True,
})


def read_csv(path):
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ------------------------------------------------------------
# 1. SfM: registro reportado vs. real (muestra el hallazgo de componentes)
# ------------------------------------------------------------

def chart_sfm_registration():
    rows = read_csv(AUDIT / "sfm-registration-comparison" / "sfm_registration_comparison.csv")
    rows = [r for r in rows if r["tasa_real_pct"]]

    labels = [f"{r['caso'].split('-', 1)[1][:12]}\n{r['metodo_captura'][:22]}" for r in rows]
    reportada = [float(r["tasa_reportada_pct"]) for r in rows]
    real = [float(r["tasa_real_pct"]) for r in rows]

    x = range(len(labels))
    width = 0.38

    fig, ax = plt.subplots(figsize=(13, 6))
    ax.bar([i - width / 2 for i in x], reportada, width, label="Reportado (wrapper)", color="#c0392b")
    ax.bar([i + width / 2 for i in x], real, width, label="Real (verificado)", color="#27ae60")
    ax.set_ylabel("% de imagenes registradas")
    ax.set_title("SfM: tasa de registro reportada vs. verificada, por dataset")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "01_sfm_registro_reportado_vs_real.png")
    plt.close(fig)


# ------------------------------------------------------------
# 2. Peso de archivo por tecnica
# ------------------------------------------------------------

def chart_output_weights():
    rows = read_csv(AUDIT / "output-weights" / "output_weights.csv")

    grouped = defaultdict(float)
    for r in rows:
        key = (r["caso"], r["metodo_captura"], r["tecnica"])
        grouped[key] += float(r["size_mb"])

    items = sorted(grouped.items(), key=lambda kv: kv[0])
    labels = [f"{c.split('-', 1)[1][:10]}\n{m}/{t}" for (c, m, t), _ in items]
    values = [v for _, v in items]

    colors = ["#2980b9" if "nerfacto" in l else "#8e44ad" if "splatfacto" in l else "#d35400" for l in labels]

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(range(len(labels)), values, color=colors)
    ax.set_ylabel("MB (escala log)")
    ax.set_yscale("log")
    ax.set_title("Peso total de archivos de output, por sitio / metodo / tecnica")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "02_peso_archivo_por_tecnica.png")
    plt.close(fig)


# ------------------------------------------------------------
# 3. Tiempo de entrenamiento
# ------------------------------------------------------------

def chart_processing_time():
    rows = read_csv(AUDIT / "processing-time" / "processing_time.csv")
    rows = [r for r in rows if r["etapa"].startswith("entrenamiento") and r["duracion_segundos"]]

    labels = [f"{r['caso'].split('-', 1)[1][:10]}\n{r['metodo_captura']}/{r['tecnica']}" for r in rows]
    minutes = [float(r["duracion_segundos"]) / 60 for r in rows]
    colors = ["#2980b9" if "nerfacto" in r["etapa"] else "#8e44ad" for r in rows]

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(range(len(labels)), minutes, color=colors)
    ax.set_ylabel("minutos")
    ax.set_title("Tiempo de entrenamiento (30.000 iteraciones), por sitio / metodo / tecnica")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "03_tiempo_entrenamiento.png")
    plt.close(fig)


# ------------------------------------------------------------
# 4. Fallos por sitio
# ------------------------------------------------------------

def chart_failures():
    rows = read_csv(AUDIT / "failure-rate" / "failure_events.csv")

    counts = defaultdict(lambda: defaultdict(int))
    for r in rows:
        counts[r["caso"]][r["categoria"]] += 1

    casos = sorted(counts)
    categorias = ["catastrofico", "inestabilidad_convergencia"]
    colors = {"catastrofico": "#c0392b", "inestabilidad_convergencia": "#f39c12"}

    fig, ax = plt.subplots(figsize=(9, 5))
    bottom = [0] * len(casos)
    for cat in categorias:
        vals = [counts[c].get(cat, 0) for c in casos]
        ax.bar([c.split("-", 1)[1][:15] for c in casos], vals, bottom=bottom, label=cat, color=colors[cat])
        bottom = [b + v for b, v in zip(bottom, vals)]

    ax.set_ylabel("cantidad de eventos")
    ax.set_title("Eventos de fallo detectados, por sitio (etapa de procesamiento/entrenamiento)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "04_fallos_por_sitio.png")
    plt.close(fig)


# ------------------------------------------------------------
# 5-6. PSNR/SSIM/LPIPS del benchmark de renders
# ------------------------------------------------------------

def load_benchmark_rows():
    rows = []
    for f in THESIS.glob("0*/02-resultados-finales/**/render-benchmark-metadata.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        case = d["case"]
        method = d["method"]
        rows.append({"caso": case, "metodo": method, "summary": d["summary"]})
    return rows


def chart_psnr_ssim():
    rows = load_benchmark_rows()
    rows.sort(key=lambda r: (r["caso"], r["metodo"]))

    labels = [f"{r['caso'].split('-', 1)[1][:10]}\n{r['metodo']}" for r in rows]
    psnr = [r["summary"]["psnr"]["mean"] for r in rows]
    psnr_std = [r["summary"]["psnr"]["std"] for r in rows]
    ssim = [r["summary"]["ssim"]["mean"] * 30 for r in rows]  # escalado para compartir eje visualmente

    x = range(len(labels))
    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax1.bar(x, psnr, yerr=psnr_std, capsize=3, color="#2980b9", label="PSNR (dB)")
    ax1.set_ylabel("PSNR (dB) — mas alto es mejor")
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(labels, rotation=45, ha="right", fontsize=7)

    ax2 = ax1.twinx()
    ssim_real = [r["summary"]["ssim"]["mean"] for r in rows]
    ax2.plot(x, ssim_real, "o-", color="#e67e22", label="SSIM")
    ax2.set_ylabel("SSIM — mas alto es mejor")
    ax2.set_ylim(0, 1)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    ax1.set_title("PSNR y SSIM (render vs. foto original), por sitio / metodo")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "05_psnr_ssim_por_sitio.png")
    plt.close(fig)


def chart_lpips():
    rows = load_benchmark_rows()
    rows.sort(key=lambda r: (r["caso"], r["metodo"]))

    labels = [f"{r['caso'].split('-', 1)[1][:10]}\n{r['metodo']}" for r in rows]
    lpips = [r["summary"]["lpips"]["mean"] for r in rows]
    lpips_std = [r["summary"]["lpips"]["std"] for r in rows]

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(range(len(labels)), lpips, yerr=lpips_std, capsize=3, color="#c0392b")
    ax.set_ylabel("LPIPS — mas bajo es mejor")
    ax.set_title("LPIPS (distancia perceptual, AlexNet), por sitio / metodo")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "06_lpips_por_sitio.png")
    plt.close(fig)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    chart_sfm_registration()
    print("[OK] 01_sfm_registro_reportado_vs_real.png")

    chart_output_weights()
    print("[OK] 02_peso_archivo_por_tecnica.png")

    chart_processing_time()
    print("[OK] 03_tiempo_entrenamiento.png")

    chart_failures()
    print("[OK] 04_fallos_por_sitio.png")

    chart_psnr_ssim()
    print("[OK] 05_psnr_ssim_por_sitio.png")

    chart_lpips()
    print("[OK] 06_lpips_por_sitio.png")

    print(f"\nTodos los graficos en: {OUT_DIR}")


if __name__ == "__main__":
    main()
