"""
Corre la pipeline de limpieza de distractores (YOLO seg + LaMa inpaint, local,
sin costo) sobre el dataset DJI completo del Templete Central, via la API
REST de ComfyUI (http://127.0.0.1:8000).

Detecta y borra: personas, pajaros, autos (clases COCO). Mantiene el mismo
nombre de archivo que el original, para que el dataset resultante pueda
alimentar directamente el pipeline de SfM/Nerfstudio despues.

Reanudable: si un archivo de salida ya existe, lo saltea. Corre uno por vez
(la GPU es un recurso compartido, no hay ganancia en paralelizar).
"""
import argparse
import csv
import json
import shutil
import time
import urllib.error
import urllib.request
from pathlib import Path

SERVER = "http://127.0.0.1:8000"
SRC_DIR = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\images")
DST_DIR = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\dataset-dji-comfyui-clean\images")
LOG_PATH = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\dataset-dji-comfyui-clean\logs\batch_log.csv")
COMFY_INPUT = Path(r"C:\Users\mboth\Documents\ComfyUI\input")
COMFY_OUTPUT = Path(r"C:\Users\mboth\Documents\ComfyUI\output")

LABELS = "person,bird,car"
BBOX_THRESHOLD = 0.12
SUB_THRESHOLD = 0.12
DROP_SIZE = 1
MASK_GROW = 10
MASK_BLUR = 6


def build_workflow(image_name, prefix):
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "2": {"class_type": "UltralyticsDetectorProvider", "inputs": {"model_name": "segm/yolov8m-seg.pt"}},
        "3": {
            "class_type": "ImpactSimpleDetectorSEGS",
            "inputs": {
                "bbox_detector": ["2", 0],
                "segm_detector_opt": ["2", 1],
                "image": ["1", 0],
                "bbox_threshold": BBOX_THRESHOLD,
                "bbox_dilation": 0,
                "crop_factor": 3.0,
                "drop_size": DROP_SIZE,
                "sub_threshold": SUB_THRESHOLD,
                "sub_dilation": 0,
                "sub_bbox_expansion": 0,
                "sam_mask_hint_threshold": 0.7,
            },
        },
        "4": {
            "class_type": "ImpactSEGSLabelFilter",
            "inputs": {"segs": ["3", 0], "preset": "all", "labels": LABELS},
        },
        "5": {"class_type": "SegsToCombinedMask", "inputs": {"segs": ["4", 0]}},
        "6": {
            "class_type": "INPAINT_ExpandMask",
            "inputs": {"mask": ["5", 0], "grow": MASK_GROW, "blur": MASK_BLUR, "blur_type": "gaussian"},
        },
        "7": {"class_type": "INPAINT_LoadInpaintModel", "inputs": {"model_name": "big-lama.pt"}},
        "8": {
            "class_type": "INPAINT_InpaintWithModel",
            "inputs": {"inpaint_model": ["7", 0], "image": ["1", 0], "mask": ["6", 0], "seed": 0},
        },
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": prefix}},
        # tambien guardamos la mascara como imagen: permite revisar despues,
        # sin costo extra de inferencia, cuanto se detecto/borro por foto.
        "10": {"class_type": "MaskToImage", "inputs": {"mask": ["6", 0]}},
        "11": {"class_type": "SaveImage", "inputs": {"images": ["10", 0], "filename_prefix": prefix + "_mask"}},
    }


def submit(image_name, prefix):
    wf = build_workflow(image_name, prefix)
    payload = json.dumps({"prompt": wf}).encode("utf-8")
    req = urllib.request.Request(f"{SERVER}/prompt", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))["prompt_id"]


def wait_done(prompt_id, timeout=180):
    start = time.time()
    while time.time() - start < timeout:
        req = urllib.request.Request(f"{SERVER}/history/{prompt_id}")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if prompt_id in data:
            entry = data[prompt_id]
            status = entry.get("status", {})
            if status.get("completed"):
                return entry
        time.sleep(2)
    raise TimeoutError(f"timeout esperando {prompt_id}")


def mask_coverage_pct(mask_png_path):
    from PIL import Image
    import numpy as np

    im = Image.open(mask_png_path).convert("L")
    arr = np.array(im)
    return float((arr > 127).sum()) / arr.size * 100.0


def process_one(src_path, writer, logf):
    stem = src_path.stem
    dst_path = DST_DIR / src_path.name
    if dst_path.exists():
        return "skip"

    t0 = time.time()
    comfy_in_name = f"clean_{src_path.name}"
    shutil.copy2(src_path, COMFY_INPUT / comfy_in_name)

    prefix = f"clean_{stem}"
    try:
        prompt_id = submit(comfy_in_name, prefix)
        entry = wait_done(prompt_id)
        status_str = entry.get("status", {}).get("status_str", "unknown")
        outputs = entry.get("outputs", {})
        img_file = None
        mask_file = None
        for node_id, out in outputs.items():
            for img in out.get("images", []):
                fn = img["filename"]
                if fn.startswith(prefix + "_mask"):
                    mask_file = fn
                elif fn.startswith(prefix):
                    img_file = fn

        if status_str != "success" or not img_file:
            row = [src_path.name, "ERROR", status_str, "", f"{time.time()-t0:.1f}", prompt_id]
            writer.writerow(row)
            logf.flush()
            return "error"

        for attempt in range(6):
            try:
                shutil.copy2(COMFY_OUTPUT / img_file, dst_path)
                break
            except PermissionError:
                if attempt == 5:
                    raise
                time.sleep(1.5)
        cov = None
        if mask_file:
            try:
                cov = mask_coverage_pct(COMFY_OUTPUT / mask_file)
            except Exception:
                cov = None
            (COMFY_OUTPUT / mask_file).unlink(missing_ok=True)
        (COMFY_OUTPUT / img_file).unlink(missing_ok=True)

        flag = ""
        if cov is not None and cov > 15.0:
            flag = "REVIEW_HIGH_MASK_AREA"

        row = [src_path.name, "OK", status_str, f"{cov:.2f}" if cov is not None else "", f"{time.time()-t0:.1f}", prompt_id + (" " + flag if flag else "")]
        writer.writerow(row)
        logf.flush()
        return "review" if flag else "ok"
    finally:
        (COMFY_INPUT / comfy_in_name).unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="procesar solo N imagenes (para lotes de validacion)")
    ap.add_argument("--every", type=int, default=1, help="tomar 1 de cada N imagenes (para muestreo espaciado)")
    args = ap.parse_args()

    DST_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    all_srcs = sorted(SRC_DIR.glob("*.png"))
    srcs = all_srcs[:: args.every]
    if args.limit:
        srcs = srcs[: args.limit]

    print(f"Total fuente: {len(all_srcs)} | a procesar en esta corrida: {len(srcs)}")

    new_log = not LOG_PATH.exists()
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as logf:
        writer = csv.writer(logf)
        if new_log:
            writer.writerow(["filename", "result", "status_str", "mask_coverage_pct", "duration_s", "prompt_id_note"])

        counts = {"ok": 0, "skip": 0, "error": 0, "review": 0}
        for i, src in enumerate(srcs, 1):
            try:
                r = process_one(src, writer, logf)
            except Exception as e:
                writer.writerow([src.name, "EXCEPTION", str(e), "", "", ""])
                logf.flush()
                r = "error"
            counts[r] = counts.get(r, 0) + 1
            if i % 10 == 0 or r != "ok":
                print(f"[{i}/{len(srcs)}] {src.name} -> {r}  (acumulado: {counts})")

    print("FINAL:", counts)


if __name__ == "__main__":
    main()
