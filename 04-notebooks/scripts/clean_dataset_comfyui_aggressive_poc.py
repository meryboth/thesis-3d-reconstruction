"""
POC de una version MAS AGRESIVA de limpieza con ComfyUI: ademas de los
distractores discretos (persona/pajaro/auto via YOLO, igual que
clean_dataset_comfyui.py), esta version tambien intenta borrar el CONTEXTO
que no es la estructura principal que se esta relevando (cielo, edificios de
fondo, terreno) -- via segmentacion de objeto saliente (RMBG-2.0), que aisla
el sujeto dominante del encuadre e inpaint-ea todo lo demas.

Corre sobre un puñado de imagenes espaciadas (no el dataset completo) para
validar visualmente el resultado ANTES de decidir si vale la pena correr la
version completa. Guarda, por cada imagen de muestra: el resultado limpio,
la mascara final combinada (YOLO union invertido-RMBG), y la mascara cruda
de RMBG (foreground/sujeto detectado) por separado, para poder diagnosticar
si el sujeto se esta aislando bien o mal.

IMPORTANTE (dataset original vs. limpiado): esto NO reemplaza en ningun caso
el dataset original -- graba en una carpeta nueva. El pipeline de SfM/NeRF/
Splat siempre corre sobre lo que haya en la carpeta `images/` de un dataset
puntual; nunca hay una corrida "mixta" a medio camino entre original y
limpiado dentro de una misma carpeta.
"""
import argparse
import json
import shutil
import time
import urllib.request
from pathlib import Path

SERVER = "http://127.0.0.1:8000"
SRC_DIR = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\images")
OUT_DIR = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\dataset-dji-comfyui-clean-aggressive-poc")
COMFY_INPUT = Path(r"C:\Users\mboth\Documents\ComfyUI\input")
COMFY_OUTPUT = Path(r"C:\Users\mboth\Documents\ComfyUI\output")

LABELS = "person,bird,car"
BBOX_THRESHOLD = 0.12
SUB_THRESHOLD = 0.12
DROP_SIZE = 1
MASK_GROW = 10
MASK_BLUR = 6
RMBG_MODEL = "RMBG-2.0"


def build_workflow(image_name, prefix):
    return {
        "1": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        # --- distractores discretos, igual que clean_dataset_comfyui.py ---
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
        # --- contexto (cielo + edificios de fondo + piso): saliency ---
        "6": {
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
        "7": {"class_type": "InvertMask", "inputs": {"mask": ["6", 1]}},
        # --- union: distractores + contexto ---
        "8": {"class_type": "AddMask", "inputs": {"mask1": ["5", 0], "mask2": ["7", 0]}},
        "9": {
            "class_type": "INPAINT_ExpandMask",
            "inputs": {"mask": ["8", 0], "grow": MASK_GROW, "blur": MASK_BLUR, "blur_type": "gaussian"},
        },
        "10": {"class_type": "INPAINT_LoadInpaintModel", "inputs": {"model_name": "big-lama.pt"}},
        "11": {
            "class_type": "INPAINT_InpaintWithModel",
            "inputs": {"inpaint_model": ["10", 0], "image": ["1", 0], "mask": ["9", 0], "seed": 0},
        },
        "12": {"class_type": "SaveImage", "inputs": {"images": ["11", 0], "filename_prefix": prefix}},
        "13": {"class_type": "MaskToImage", "inputs": {"mask": ["9", 0]}},
        "14": {"class_type": "SaveImage", "inputs": {"images": ["13", 0], "filename_prefix": prefix + "_mask"}},
        # mascara cruda de RMBG (sujeto detectado como foreground), para diagnostico
        "15": {"class_type": "MaskToImage", "inputs": {"mask": ["6", 1]}},
        "16": {"class_type": "SaveImage", "inputs": {"images": ["15", 0], "filename_prefix": prefix + "_rmbg_fg"}},
    }


def submit(image_name, prefix):
    wf = build_workflow(image_name, prefix)
    payload = json.dumps({"prompt": wf}).encode("utf-8")
    req = urllib.request.Request(f"{SERVER}/prompt", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))["prompt_id"]


def wait_done(prompt_id, timeout=600):
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
                    f"ComfyUI error en nodo {err.get('node_id')} ({err.get('node_type')}): "
                    f"{err.get('exception_message')}"
                )
        time.sleep(2)
    raise TimeoutError(f"timeout esperando {prompt_id}")


def process_one(src_path, out_dir):
    stem = src_path.stem
    comfy_in_name = f"aggr_{src_path.name}"
    shutil.copy2(src_path, COMFY_INPUT / comfy_in_name)
    prefix = f"aggr_{stem}"

    try:
        prompt_id = submit(comfy_in_name, prefix)
        print(f"  [{src_path.name}] prompt_id={prompt_id} -- esperando...")
        entry = wait_done(prompt_id)
        status_str = entry.get("status", {}).get("status_str", "unknown")
        outputs = entry.get("outputs", {})

        files = {"clean": None, "mask": None, "rmbg_fg": None}
        for out in outputs.values():
            for img in out.get("images", []):
                fn = img["filename"]
                if fn.startswith(prefix + "_rmbg_fg"):
                    files["rmbg_fg"] = fn
                elif fn.startswith(prefix + "_mask"):
                    files["mask"] = fn
                elif fn.startswith(prefix):
                    files["clean"] = fn

        if status_str != "success" or not files["clean"]:
            print(f"  [{src_path.name}] ERROR status={status_str} outputs={outputs}")
            return False

        for kind, fn in files.items():
            if not fn:
                continue
            dst = out_dir / f"{stem}_{kind}.png"
            shutil.copy2(COMFY_OUTPUT / fn, dst)
            (COMFY_OUTPUT / fn).unlink(missing_ok=True)
        shutil.copy2(src_path, out_dir / f"{stem}_original.png")
        print(f"  [{src_path.name}] OK")
        return True
    finally:
        (COMFY_INPUT / comfy_in_name).unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=8, help="cantidad de imagenes de muestra (espaciadas parejo)")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_srcs = sorted(SRC_DIR.glob("*.png"))
    step = max(1, len(all_srcs) // args.n)
    samples = all_srcs[::step][: args.n]

    print(f"Total dataset: {len(all_srcs)} | muestra: {len(samples)} imagenes")
    for s in samples:
        print(f" - {s.name}")

    ok = 0
    for src in samples:
        try:
            if process_one(src, OUT_DIR):
                ok += 1
        except Exception as e:
            print(f"  [{src.name}] EXCEPTION: {e}")

    print(f"\nFINAL: {ok}/{len(samples)} OK. Resultados en {OUT_DIR}")


if __name__ == "__main__":
    main()
