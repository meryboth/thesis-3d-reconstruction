"""
Grillas comparativas Foto original (raw) | Dataset limpio (ComfyUI: YOLO-seg +
LaMa inpaint) para documentar el impacto real del preprocesamiento ejecutado
sobre el dataset DJI completo del Templete Central (Cap. 5, seccion B1/H2).

Apiladas verticalmente (no lado a lado) para que cada panel se vea grande,
mismo criterio que build_fidelity_comparisons.py.

Escribe en thesis/00-auditoria/preprocesamiento-comfyui/02-templete-central/:
  comparacion_<frame>.jpg
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAW_DIR = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\images")
CLEAN_DIR = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\dataset-dji-comfyui-clean\images")
OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\preprocesamiento-comfyui\02-templete-central")

PANEL_WIDTH = 1100
LABEL_HEIGHT = 38

# frame, etiqueta descriptiva breve para el nombre de archivo
FRAMES = [
    ("00607", "aves-en-cielo"),
    ("00839", "tres-personas"),
    ("00522", "persona-piso-piedra"),
]


def load_panel(path, width):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    new_h = int(h * width / w)
    return img.resize((width, new_h), Image.BICUBIC)


def make_comparison(raw_path, clean_path, width):
    panels = [
        (load_panel(raw_path, width), "Foto original (raw)"),
        (load_panel(clean_path, width), "Dataset limpio — ComfyUI (YOLO-seg + LaMa)"),
    ]
    row_h = LABEL_HEIGHT + max(p.height for p, _ in panels)

    canvas = Image.new("RGB", (width, row_h * len(panels)), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except Exception:
        font = ImageFont.load_default()

    for i, (panel, label) in enumerate(panels):
        y = i * row_h
        draw.rectangle([0, y, width, y + LABEL_HEIGHT], fill=(30, 30, 30))
        draw.text((10, y + 7), label, fill="white", font=font)
        canvas.paste(panel, (0, y + LABEL_HEIGHT))

    return canvas


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for frame, tag in FRAMES:
        raw_path = RAW_DIR / f"{frame}.png"
        clean_path = CLEAN_DIR / f"{frame}.png"
        if not raw_path.exists() or not clean_path.exists():
            print(f"[SKIP] falta {frame}")
            continue
        canvas = make_comparison(raw_path, clean_path, PANEL_WIDTH)
        out_path = OUT_DIR / f"comparacion_{frame}_{tag}.jpg"
        canvas.save(out_path, quality=92)
        print("[OK]", out_path.name)


if __name__ == "__main__":
    main()
