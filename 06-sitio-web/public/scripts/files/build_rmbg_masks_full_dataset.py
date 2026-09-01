"""
Genera mascaras de entrenamiento Nerfstudio (RMBG-2.0, saliencia) para el
dataset DJI completo del Templete Central (1232 imagenes CRUDAS, sin tocar
pixeles). No inpaintea nada -- ver POC previo (clean_dataset_comfyui_aggressive_poc.py)
que mostro que LaMa no puede rellenar una mascara de ese tamano. En cambio,
la mascara se usa directamente por Nerfstudio para IGNORAR el fondo durante
el entrenamiento (mask_path en transforms.json): blanco=entrenar aca (sujeto),
negro=ignorar (fondo).

Mascara guardada en modo "L" (1 canal), binarizada a 0/255 -- Nerfstudio la
castea con `.bool()`, asi que cualquier valor no-cero cuenta como "entrenar
aca"; binarizar evita que un borde antialiaseado (gris) se cuele como "keep".

Reanudable: si la mascara de salida ya existe, la saltea.
"""
import argparse
import json
import shutil
import time
import urllib.request
from pathlib import Path

from PIL import Image
import numpy as np

SERVER = "http://127.0.0.1:8000"
SRC_DIR = Path(r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-splatfacto-1232-full\images")
DST_DIR = Path(r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-masked-raw-1232-splatfacto\masks")
LOG_PATH = DST_DIR.parent / "logs" / "rmbg_batch_log.csv"
COMFY_INPUT = Path(r"C:\Users\mboth\Documents\ComfyUI\input")
COMFY_OUTPUT = Path(r"C:\Users\mboth\Documents\ComfyUI\output")

RMBG_MODEL = "RMBG-2.0"
BIN_THRESHOLD = 127


def build_workflow(image_name, prefix):
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "2": {
            "class_type": "RMBG",
            "inputs": {
                "image": ["1", 0],
                "model": RMBG_MODEL,
                "sensitivity": 1.0,
                "process_res": 1024,
                "mask_blur": 0,
                "mask_offset": 0,
                "invert_output": False,
                "refine_foreground": False,
                "background": "Alpha",
                "background_color": "#222222",
            },
        },
        "3": {"class_type": "MaskToImage", "inputs": {"mask": ["2", 1]}},
        "4": {"class_type": "SaveImage", "inputs": {"images": ["3", 0], "filename_prefix": prefix}},
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
            if status.get("status_str") == "error":
                msgs = status.get("messages", [])
                err = next((m[1] for m in msgs if m[0] == "execution_error"), {})
                raise RuntimeError(
                    f"nodo {err.get('node_id')} ({err.get('node_type')}): {err.get('exception_message')}"
                )
        time.sleep(1.5)
    raise TimeoutError(f"timeout esperando {prompt_id}")


def process_one(src_path):
    stem = src_path.stem
    dst_path = DST_DIR / f"{stem}.png"
    if dst_path.exists():
        return "skip"

    comfy_in_name = f"rmbg_{src_path.name}"
    shutil.copy2(src_path, COMFY_INPUT / comfy_in_name)
    prefix = f"rmbg_{stem}"
    try:
        prompt_id = submit(comfy_in_name, prefix)
        entry = wait_done(prompt_id)
        status_str = entry.get("status", {}).get("status_str", "unknown")
        outputs = entry.get("outputs", {})
        img_file = None
        for out in outputs.values():
            for img in out.get("images", []):
                if img["filename"].startswith(prefix):
                    img_file = img["filename"]

        if status_str != "success" or not img_file:
            return f"error:{status_str}"

        im = Image.open(COMFY_OUTPUT / img_file).convert("L")
        arr = np.array(im)
        arr = np.where(arr > BIN_THRESHOLD, 255, 0).astype(np.uint8)
        Image.fromarray(arr, mode="L").save(dst_path)
        (COMFY_OUTPUT / img_file).unlink(missing_ok=True)
        keep_pct = float((arr > 0).sum()) / arr.size * 100.0
        return f"ok:{keep_pct:.1f}"
    finally:
        (COMFY_INPUT / comfy_in_name).unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    DST_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    srcs = sorted(SRC_DIR.glob("*.png"))
    if args.limit:
        srcs = srcs[: args.limit]
    print(f"Total: {len(srcs)} imagenes")

    new_log = not LOG_PATH.exists()
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as logf:
        if new_log:
            logf.write("filename,result\n")
        counts = {}
        for i, src in enumerate(srcs, 1):
            try:
                r = process_one(src)
            except Exception as e:
                r = f"exception:{e}"
            logf.write(f"{src.name},{r}\n")
            logf.flush()
            key = r.split(":")[0]
            counts[key] = counts.get(key, 0) + 1
            if i % 25 == 0 or key not in ("ok", "skip"):
                print(f"[{i}/{len(srcs)}] {src.name} -> {r}  (acumulado: {counts})")

    print("FINAL:", counts)


if __name__ == "__main__":
    main()
