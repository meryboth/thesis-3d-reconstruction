"""
Inferencia de Moondream2 aislada en su propio venv (04-notebooks/.venv-moondream),
separado del venv de ComfyUI porque el transformers que ya tiene ComfyUI (5.16,
muy nueva) rompe la carga del remote code de moondream2 (moondream2 todavia no
actualizo su codigo para la API interna nueva de tied-weights de transformers).

Uso: python moondream_infer.py --image <path> --question "..."
Imprime a stdout un JSON de una linea: {"answer": "..."}

Carga el modelo en cada invocacion (no queda residente) para no competir por
VRAM con lo que ComfyUI tenga cargado en simultaneo -- mas lento por llamada
(~10-15s de carga + inferencia) pero mas seguro en una GPU de 6GB.
"""
import argparse
import json
import sys

import torch
from PIL import Image
from transformers import AutoModelForCausalLM

MODEL_ID = "vikhyatk/moondream2"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--question", required=True)
    args = ap.parse_args()

    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, trust_remote_code=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device, dtype=torch.bfloat16 if device == "cuda" else torch.float32)

    img = Image.open(args.image).convert("RGB")
    result = model.query(img, args.question)

    print(json.dumps({"answer": result["answer"]}))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stdout)
        sys.exit(1)
