"""
Tiempo de procesamiento por etapa (SfM, Nerfacto, Splatfacto, render, export)
y por sitio/metodo de captura — metrica explicita del Cap. 4 (seccion 4.3.5).

IMPORTANTE: lee timestamps de las carpetas de trabajo ORIGINALES
(panteon-chacarita/, paraguas-vicentelopez/), NO de thesis/ — los archivos
copiados a thesis/ tienen todos la fecha de copia, no la fecha real del
entrenamiento.

Metodo:
  - Entrenamiento (Nerfacto/Splatfacto): duracion = mtime(checkpoint final)
    - mtime(config.yml), ya que Nerfstudio escribe config.yml al arrancar
    el entrenamiento y el checkpoint final al terminarlo. Es una cota de
    tiempo de pared (wall-clock), puede incluir tiempo de cola/idle si hubo
    interrupciones, pero es la mejor aproximacion disponible sin logs de
    progreso completos (varios logs de entrenamiento solo capturaron el
    arranque, ver analyze_failure_rate.py).
  - Render: se usa el valor "Tiempo: X min Y s" ya declarado explicitamente
    en los experiment-summary.txt / logs (mas confiable que inferir de
    archivos).
  - Export (Gaussian Splat .ply): mtime(splat.ply) - mtime(checkpoint final).

Escribe en thesis/00-auditoria/processing-time/:
  processing_time.csv
  processing_time.json
  processing_time.log
"""

import csv
import json
import re
from datetime import datetime
from pathlib import Path

RAW = Path(r"C:\nerfstudio_work")
OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\processing-time")

# Cada entrada: (caso, metodo_captura, tecnica, carpeta_de_la_corrida)
# carpeta_de_la_corrida debe contener config.yml y nerfstudio_models/step-*.ckpt
TRAINING_RUNS = [
    ("01-paraguas-vicentelopez", "dji", "nerfacto",
     RAW / "paraguas-vicentelopez/outputs/paraguas-vicentelopez-drone-nerfacto-v2/nerfacto/2026-06-20_233157"),
    ("01-paraguas-vicentelopez", "dji", "splatfacto",
     RAW / "paraguas-vicentelopez/outputs/paraguas-vicentelopez-drone-splatfacto/splatfacto/2026-06-20_191333"),

    ("02-templete-central", "dji", "nerfacto",
     RAW / "panteon-chacarita/templete-central/outputs-templete-nerf308/templete-central-realityscan-nerf308/nerfacto/2026-08-24_220201"),
    ("02-templete-central", "dji", "splatfacto",
     RAW / "panteon-chacarita/templete-central/outputs-templete-splat/templete-central-realityscan-splat-ds8/splatfacto/2026-08-24_232220"),
    ("02-templete-central", "insta360", "nerfacto",
     RAW / "panteon-chacarita/templete-central/outputs/templete-central-insta360-realityscan-nerfacto/nerfacto/2026-08-12_233328"),
    ("02-templete-central", "insta360", "splatfacto",
     RAW / "panteon-chacarita/templete-central/outputs/templete-central-insta360-realityscan-splatfacto/splatfacto/2026-08-13_014408"),

    ("03-panteon-asociacion-catalana", "dji", "nerfacto",
     RAW / "panteon-chacarita/panteon-asociacion-catalana/outputs-djionly-nerf300/colmap-nerfstudio-nerf300/nerfacto/2026-08-23_191033"),
    ("03-panteon-asociacion-catalana", "dji", "splatfacto",
     RAW / "panteon-chacarita/panteon-asociacion-catalana/outputs-djionly-splat/panteon-asociacion-catalana-dji-splatfacto-full-ds8/splatfacto/2026-08-24_004501"),
    ("03-panteon-asociacion-catalana", "insta360", "nerfacto",
     RAW / "panteon-chacarita/panteon-asociacion-catalana/outputs/panteon-catalana-insta360-realityscan-nerfacto/nerfacto/2026-08-13_132710"),
    ("03-panteon-asociacion-catalana", "insta360", "splatfacto",
     RAW / "panteon-chacarita/panteon-asociacion-catalana/outputs/panteon-catalana-insta360-realityscan-splatfacto/splatfacto/2026-08-13_153432"),
]

# Logs donde buscar duracion de render ya declarada como texto ("Tiempo: X min Y s")
RENDER_SUMMARY_FILES = [
    ("01-paraguas-vicentelopez", RAW / "paraguas-vicentelopez/logs"),
    ("02-templete-central", RAW / "panteon-chacarita/templete-central/logs"),
    ("03-panteon-asociacion-catalana", RAW / "panteon-chacarita/panteon-asociacion-catalana/logs"),
]

RENDER_PATTERN = re.compile(
    r"(?:Split:\s*(\w+).*?)?Frames?:?\s*[\d,]+.*?Tiempo(?:\s*total)?:\s*(?:(\d+)\s*min\s*)?(\d+)\s*s",
    re.IGNORECASE | re.DOTALL,
)


def fmt_duration(seconds):
    if seconds is None:
        return None
    m, s = divmod(int(round(seconds)), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m {s}s"
    return f"{m}m {s}s"


def training_duration(run_dir):
    config = run_dir / "config.yml"
    ckpts = sorted((run_dir / "nerfstudio_models").glob("step-*.ckpt"))

    if not config.exists() or not ckpts:
        return None, None, None

    final_ckpt = ckpts[-1]
    t_start = config.stat().st_mtime
    t_end = final_ckpt.stat().st_mtime
    duration_s = t_end - t_start

    return duration_s, datetime.fromtimestamp(t_start), datetime.fromtimestamp(t_end)


def find_render_durations():
    rows = []
    seen_texts = set()

    for case, logs_dir in RENDER_SUMMARY_FILES:
        if not logs_dir.exists():
            continue

        for f in logs_dir.rglob("*"):
            if not f.is_file() or f.suffix.lower() not in (".txt", ".log"):
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            for m in RENDER_PATTERN.finditer(text):
                key = (case, m.group(0)[:80])
                if key in seen_texts:
                    continue
                seen_texts.add(key)

                minutes = int(m.group(2)) if m.group(2) else 0
                seconds = int(m.group(3))
                total_s = minutes * 60 + seconds

                rows.append({
                    "caso": case, "etapa": "render", "metodo_captura": "N/A",
                    "tecnica": m.group(1) or "N/A",
                    "duracion_segundos": total_s,
                    "duracion_legible": fmt_duration(total_s),
                    "inicio": None, "fin": None,
                    "fuente": str(f),
                })

    return rows


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []

    for case, method, technique, run_dir in TRAINING_RUNS:
        duration_s, t_start, t_end = training_duration(run_dir)

        rows.append({
            "caso": case, "etapa": f"entrenamiento-{technique}", "metodo_captura": method,
            "tecnica": technique,
            "duracion_segundos": round(duration_s, 1) if duration_s else None,
            "duracion_legible": fmt_duration(duration_s),
            "inicio": t_start.isoformat() if t_start else None,
            "fin": t_end.isoformat() if t_end else None,
            "fuente": str(run_dir),
        })

    rows.extend(find_render_durations())

    csv_path = OUT_DIR / "processing_time.csv"
    json_path = OUT_DIR / "processing_time.json"
    log_path = OUT_DIR / "processing_time.log"

    fieldnames = ["caso", "etapa", "metodo_captura", "tecnica", "duracion_segundos",
                  "duracion_legible", "inicio", "fin", "fuente"]

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    lines = [
        "TIEMPO DE PROCESAMIENTO — por sitio / metodo de captura / etapa",
        "=" * 100,
        "",
        "Entrenamiento: mtime(checkpoint final) - mtime(config.yml), leido de las",
        "carpetas de trabajo originales (no de thesis/, que tiene fechas de copia).",
        "Render: duracion ya declarada explicitamente en el log/resumen de esa corrida.",
        "",
    ]

    current = None
    for r in sorted(rows, key=lambda x: (x["caso"], x["metodo_captura"], x["etapa"])):
        if r["caso"] != current:
            current = r["caso"]
            lines += ["", f"### {current}", "-" * 100]

        dur = r["duracion_legible"] or "NO CALCULABLE (falta config.yml o checkpoint)"
        lines.append(f"  [{r['metodo_captura']:8s}] {r['etapa']:20s} {dur}")
        if r["inicio"]:
            lines.append(f"      inicio: {r['inicio']}  fin: {r['fin']}")
        lines.append(f"      fuente: {r['fuente']}")

    log_path.write_text("\n".join(lines), encoding="utf-8")

    ok = sum(1 for r in rows if r["duracion_segundos"] is not None)
    print(f"Filas: {len(rows)} ({ok} con duracion calculada)")
    print(f"[OK] CSV:  {csv_path}")
    print(f"[OK] JSON: {json_path}")
    print(f"[OK] LOG:  {log_path}")


if __name__ == "__main__":
    main()
