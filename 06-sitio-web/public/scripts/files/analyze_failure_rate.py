"""
Tasa de fallos durante procesamiento/entrenamiento (Cap. 2, seccion 2.6.3;
Cap. 4, seccion 4.9), clasificada en:
  - catastrofico: el proceso no llega a producir un output valido
    (agotamiento de memoria, error de dependencias/archivos, divergencia).
  - inestabilidad_convergencia: el proceso se reintento varias veces
    (detectado por archivos *_retry*.log/*_retry2*.log/etc. del mismo comando).

No cubre "fallo parcial" (huecos/floaters visuales) porque esa categoria
requiere inspeccion visual cualitativa (Cap. 4, 4.9) y no es extraible de
logs de texto.

Complementa, sin duplicar, a analyze_sfm_registration_comparison.py (que ya
cubre los fallos de la ETAPA de SfM/registro de camaras). Este script cubre
la etapa de PROCESAMIENTO/ENTRENAMIENTO (COLMAP denso, Nerfacto, Splatfacto).

Escribe en thesis/00-auditoria/failure-rate/:
  failure_events.csv
  failure_events.json
  failure_events.log
"""

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(r"C:\nerfstudio_work\thesis")
OUT_DIR = ROOT / "00-auditoria" / "failure-rate"

# (categoria, patron_regex, descripcion)
CATASTROFICO_PATTERNS = [
    ("OOM_SIGKILL", re.compile(r"^bash: line \d+:\s+\d+\s+Killed\s+(.+)$", re.MULTILINE), "Proceso terminado por el sistema (SIGKILL, tipicamente OOM)"),
    ("OOM_SISTEMA", re.compile(r"OSError:\s*\[Errno 12\][^\n]*"), "Sin memoria suficiente en el sistema (Cannot allocate memory)"),
    ("OOM_CUDA", re.compile(r"(CUDA out of memory|torch\.cuda\.OutOfMemoryError)[^\n]*"), "Sin memoria suficiente en GPU"),
    ("ARCHIVO_FALTANTE", re.compile(r"FileNotFoundError:[^\n]*"), "Archivo de entrada esperado no existia (dataset no listo / pipeline mal secuenciado)"),
    ("EXCEPCION_GENERICA", re.compile(r"^([A-Za-z_][A-Za-z0-9_.]*Error):\s*(.+)$", re.MULTILINE), "Excepcion de Python no clasificada en las categorias anteriores"),
]

STATUS_137_PATTERN = re.compile(r"STATUS=137")


def find_log_files():
    exts = ("*.log", "*.txt")
    files = []
    for ext in exts:
        files.extend(ROOT.glob(f"0*/01-logs/**/{ext}"))
    return sorted(set(files))


def case_of(path):
    return path.relative_to(ROOT).parts[0]


def scan_catastrophic(path, text):
    events = []
    seen_spans = set()

    for category, pattern, desc in CATASTROFICO_PATTERNS:
        for m in pattern.finditer(text):
            # Evita contar la misma linea de error dos veces bajo distintos patrones
            # (p.ej. OOM_SISTEMA y EXCEPCION_GENERICA sobre el mismo OSError).
            span_key = (m.start() // 200)
            if span_key in seen_spans:
                continue

            snippet = m.group(0).strip().replace("\n", " ")[:200]

            if category == "OOM_SIGKILL" and not STATUS_137_PATTERN.search(text):
                # "Killed" sin STATUS=137 puede ser ruido (otro proceso ajeno); igual lo
                # dejamos pero marcado, ya que es una senal fuerte igualmente.
                pass

            events.append({
                "categoria": "catastrofico",
                "subtipo": category,
                "descripcion": desc,
                "evidencia": snippet,
            })
            seen_spans.add(span_key)

    return events


def find_retry_groups():
    """Agrupa archivos *_retryN.log (mismo comando reintentado) como un
    unico evento de inestabilidad de convergencia con N reinicios."""
    retry_files = list(ROOT.glob("0*/01-logs/**/*retry*.*"))

    groups = defaultdict(list)
    for f in retry_files:
        # Nombre base sin el sufijo _retry/_retryN, para agrupar variantes
        # del mismo comando bajo la misma clave.
        base = re.sub(r"_retry\d*", "", f.stem)
        groups[(case_of(f), f.parent, base)].append(f)

    events = []
    for (case, parent, base), files in groups.items():
        events.append({
            "caso": case,
            "categoria": "inestabilidad_convergencia",
            "comando_base": base,
            "reinicios_detectados": len(files),
            "archivos": [str(f) for f in sorted(files)],
        })

    return events


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    catastrophic_rows = []
    for path in find_log_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        events = scan_catastrophic(path, text)
        for e in events:
            catastrophic_rows.append({
                "caso": case_of(path),
                "archivo_log": str(path),
                **e,
            })

    retry_events = find_retry_groups()

    all_rows = catastrophic_rows + [
        {
            "caso": r["caso"], "archivo_log": "; ".join(r["archivos"]),
            "categoria": r["categoria"], "subtipo": "REINICIOS",
            "descripcion": f"Comando reintentado {r['reinicios_detectados']} veces: {r['comando_base']}",
            "evidencia": r["comando_base"],
        }
        for r in retry_events
    ]

    csv_path = OUT_DIR / "failure_events.csv"
    json_path = OUT_DIR / "failure_events.json"
    log_path = OUT_DIR / "failure_events.log"

    fieldnames = ["caso", "categoria", "subtipo", "descripcion", "evidencia", "archivo_log"]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    json_path.write_text(json.dumps(all_rows, indent=2, ensure_ascii=False), encoding="utf-8")

    by_case = defaultdict(lambda: defaultdict(int))
    for r in all_rows:
        by_case[r["caso"]][r["categoria"]] += 1

    lines = [
        "TASA DE FALLOS — procesamiento / entrenamiento (no incluye etapa de SfM,",
        "ver analyze_sfm_registration_comparison.py para esa etapa)",
        "=" * 100,
        "",
        "RESUMEN POR SITIO",
        "-" * 100,
    ]
    for case, counts in sorted(by_case.items()):
        lines.append(f"{case}: {dict(counts)}")

    lines += ["", "DETALLE", "-" * 100]

    current = None
    for r in sorted(all_rows, key=lambda x: (x["caso"], x["categoria"])):
        if r["caso"] != current:
            current = r["caso"]
            lines += ["", f"### {current}", "-" * 60]
        lines.append(f"[{r['categoria']}/{r['subtipo']}] {r['descripcion']}")
        lines.append(f"    evidencia: {r['evidencia']}")
        lines.append(f"    log: {r['archivo_log']}")
        lines.append("")

    lines += [
        "=" * 100,
        "NOTA METODOLOGICA",
        "-" * 100,
        "Deteccion automatica por patrones de texto sobre los logs ya recopilados en",
        "thesis/0X-*/01-logs/. No sustituye la categoria 'fallo parcial' del Cap. 4",
        "(seccion 4.9), que requiere inspeccion visual cualitativa del resultado.",
        "Los 'reinicios detectados' cuentan archivos *_retryN.* del mismo comando,",
        "no necesariamente reinicios consecutivos de una unica sesion.",
    ]

    log_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Eventos catastroficos: {len(catastrophic_rows)}")
    print(f"Grupos de reinicio (inestabilidad): {len(retry_events)}")
    print(f"[OK] CSV:  {csv_path}")
    print(f"[OK] JSON: {json_path}")
    print(f"[OK] LOG:  {log_path}")


if __name__ == "__main__":
    main()
