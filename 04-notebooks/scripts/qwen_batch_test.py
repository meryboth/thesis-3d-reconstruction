"""Prueba rapida (sin pasar por ComfyUI, directo) de Qwen2-VL-2B sobre los
renders de fragmentos ya generados por poc_segmentation_vlm.py, para
comparar su tasa de acierto contra la etiqueta geometrica de origen antes de
integrarlo al pipeline completo via ComfyUI."""
import time
from pathlib import Path

import torch
from PIL import Image
from transformers import AutoProcessor, Qwen2VLForConditionalGeneration

MODEL_ID = "Qwen/Qwen2-VL-2B-Instruct"
RENDER_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\poc-segmentacion-vlm\templete-central-dji")

QUESTION = (
    "This image has two panels of the same 3D point-cloud fragment from an "
    "architectural heritage building. The LEFT panel shows the fragment "
    "isolated and zoomed in, with its true height-to-width proportions -- "
    "use this panel to judge its shape. The RIGHT panel shows the same "
    "fragment (in red) in context within the full gray building, just to "
    "show where it sits. Based on the LEFT panel's proportions -- tall and "
    "slender extending mostly vertically like a supporting post or pillar, "
    "versus short and elongated mostly horizontally like a railing, "
    "parapet or low wall -- classify this fragment. Answer with exactly "
    "one word: COLUMN or RAILING."
)

model = Qwen2VLForConditionalGeneration.from_pretrained(MODEL_ID, torch_dtype=torch.bfloat16, device_map="cuda")
processor = AutoProcessor.from_pretrained(MODEL_ID)


def ask(image_path):
    img = Image.open(image_path).convert("RGB")
    messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": QUESTION}]}]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text], images=[img], return_tensors="pt").to("cuda")
    out = model.generate(**inputs, max_new_tokens=10)
    trimmed = out[:, inputs["input_ids"].shape[1]:]
    return processor.batch_decode(trimmed, skip_special_tokens=True)[0].strip().upper()


files = sorted(RENDER_DIR.glob("frag_*_columna.png")) + sorted(RENDER_DIR.glob("frag_*_baranda.png"))
correct, total = 0, 0
for f in files:
    expected = "COLUMN" if "_columna" in f.name else "RAILING"
    t0 = time.time()
    answer = ask(f)
    hit = expected in answer
    correct += hit
    total += 1
    print(f"{f.name}: esperado={expected} modelo={answer!r} {'OK' if hit else 'MISS'} ({time.time()-t0:.1f}s)")

print(f"\nAcierto: {correct}/{total} ({100*correct/total:.0f}%)")
