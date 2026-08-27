"""
Peso del archivo de output final por sitio, metodo de captura y tecnica
(SfM/NeRF/3DGS) — metrica explicita del Cap. 4 (seccion 4.3.5, "Peso del
archivo de output") y del Cap. 2 (seccion 2.6.2, "Criterio de peso del
archivo").

Recorre thesis/0X-*/02-resultados-finales/ y mide directamente en disco:
  - splatfacto: checkpoint .ckpt (peso del modelo) + splat.ply exportado (peso
    del archivo de distribucion final, formato .glTF/.SPLAT/.PLY del Cap. 4)
  - nerfacto: checkpoint .ckpt (no tiene "archivo de distribucion" propio,
    los pesos del MLP SON el archivo final)
  - fotogrametria clasica (SfM): nube densa + malla texturizada, donde exista

No modifica ni descubre nada nuevo: es una lectura directa de tamanos de
archivo ya conocidos, pero centralizada en una tabla reproducible en vez de
estar dispersa en READMEs y mensajes de git push.

Escribe en thesis/00-auditoria/output-weights/:
  output_weights.csv
  output_weights.json
  output_weights.log
"""

import csv
import json
from pathlib import Path

ROOT = Path(r"C:\nerfstudio_work\thesis")
OUT_DIR = ROOT / "00-auditoria" / "output-weights"


def mb(path):
    return path.stat().st_size / (1024 ** 2)


def case_and_method(root, path):
    rel = path.relative_to(root)
    parts = rel.parts
    case = parts[0]
    # 0X-caso/02-resultados-finales/[dji|insta360]/tecnica/... o
    # 0X-caso/02-resultados-finales/tecnica/... (paraguas)
    idx = parts.index("02-resultados-finales")
    after = parts[idx + 1:]
    if after[0] in ("dji", "insta360"):
        method = after[0]
        technique_dir = after[1]
    else:
        method = "dji"  # paraguas: unico dispositivo, sin subcarpeta
        technique_dir = after[0]
    return case, method, technique_dir


def find_rows():
    rows = []

    # --- Checkpoints (.ckpt) de nerfacto y splatfacto ---
    for ckpt in ROOT.glob("0*/02-resultados-finales/**/nerfstudio_models/step-*.ckpt"):
        case, method, technique_dir = case_and_method(ROOT, ckpt)
        rows.append({
            "caso": case, "metodo_captura": method, "tecnica": technique_dir,
            "artefacto": "checkpoint (.ckpt)", "archivo": ckpt.name,
            "size_mb": round(mb(ckpt), 2), "path": str(ckpt),
        })

    # --- Exports de Gaussian Splatting (.ply) ---
    for splat in ROOT.glob("0*/02-resultados-finales/**/export/splat.ply"):
        case, method, technique_dir = case_and_method(ROOT, splat)
        rows.append({
            "caso": case, "metodo_captura": method, "tecnica": technique_dir,
            "artefacto": "export final (splat.ply)", "archivo": splat.name,
            "size_mb": round(mb(splat), 2), "path": str(splat),
        })

    # --- Fotogrametria clasica: nube densa + malla texturizada ---
    fotogrametria_globs = [
        "0*/02-resultados-finales/colmap-fotogrametria-densa/*.ply",
        "0*/02-resultados-finales/**/colmap-fotogrametria/*.ply",
        "0*/02-resultados-finales/**/colmap-fotogrametria/*.xyz",
        "0*/02-resultados-finales/colmap-fotogrametria-densa/*.obj",
        "0*/02-resultados-finales/**/colmap-fotogrametria/*.obj",
    ]
    for pattern in fotogrametria_globs:
        for f in ROOT.glob(pattern):
            rel = f.relative_to(ROOT)
            case = rel.parts[0]
            method = "dji"  # las 3 fotogrametrias densas de este proyecto son DJI
            rows.append({
                "caso": case, "metodo_captura": method, "tecnica": "sfm-fotogrametria",
                "artefacto": f"nube/malla ({f.suffix})", "archivo": f.name,
                "size_mb": round(mb(f), 2), "path": str(f),
            })

    return rows


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = find_rows()

    rows.sort(key=lambda r: (r["caso"], r["metodo_captura"], r["tecnica"], r["artefacto"]))

    fieldnames = ["caso", "metodo_captura", "tecnica", "artefacto", "archivo", "size_mb", "path"]

    csv_path = OUT_DIR / "output_weights.csv"
    json_path = OUT_DIR / "output_weights.json"
    log_path = OUT_DIR / "output_weights.log"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "PESO DEL ARCHIVO DE OUTPUT — por sitio / metodo de captura / tecnica",
        "=" * 100,
        "",
    ]

    current = None
    for r in rows:
        key = (r["caso"], r["metodo_captura"])
        if key != current:
            current = key
            lines += ["", f"### {r['caso']} :: {r['metodo_captura']}", "-" * 100]
        lines.append(f"  [{r['tecnica']:20s}] {r['artefacto']:28s} {r['archivo']:30s} {r['size_mb']:>10.2f} MB")

    log_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Filas: {len(rows)}")
    print(f"[OK] CSV:  {csv_path}")
    print(f"[OK] JSON: {json_path}")
    print(f"[OK] LOG:  {log_path}")


if __name__ == "__main__":
    main()
