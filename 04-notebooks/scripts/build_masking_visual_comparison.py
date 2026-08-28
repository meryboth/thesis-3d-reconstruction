"""Grid comparativo de renders reales (no solo metricas): raw vs. con mascara
de entrenamiento, para Nerfacto y Splatfacto juntos en una sola imagen, con
encabezados de seccion grandes para que no haya ambiguedad sobre cual tecnica
es cual. Mismos frames de eval (mismo split, mismo orden de frames -> misma
vista) para las dos columnas de prediccion."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(r"C:\nerfstudio_work\thesis\00-auditoria\masking-comparison\renders")
OUT = Path(r"C:\nerfstudio_work\thesis\00-auditoria\masking-comparison")

FRAME_IDXS = [0, 10, 20]
THUMB_W = 460
GAP = 8
COL_LABEL_H = 30
SECTION_H = 46
ROW_LABEL_H = 22

CONFIGS = [
    ("SPLATFACTO", "raw-splatfacto", "masked-splatfacto", "#c0392b"),
    ("NERFACTO", "raw-nerfacto", "masked-nerfacto", "#2471a3"),
]

try:
    FONT_BIG = ImageFont.truetype("arialbd.ttf", 22)
    FONT_MED = ImageFont.truetype("arialbd.ttf", 15)
    FONT_SMALL = ImageFont.truetype("arial.ttf", 14)
except OSError:
    FONT_BIG = FONT_MED = FONT_SMALL = ImageFont.load_default()


def load_gt_and_pred(dir_name, idx):
    # ns-eval guarda GT|pred concatenados horizontalmente en un solo PNG
    p = BASE / dir_name / f"eval_img_{idx:04d}.png"
    im = Image.open(p).convert("RGB")
    w, h = im.size
    gt = im.crop((0, 0, w // 2, h))
    pred = im.crop((w // 2, 0, w, h))
    return gt, pred


def thumb(im):
    w, h = im.size
    new_h = int(h * THUMB_W / w)
    return im.resize((THUMB_W, new_h))


# precargar todo primero para conocer alturas
sections = []
for method, raw_dir, masked_dir, color in CONFIGS:
    rows = []
    for idx in FRAME_IDXS:
        gt, raw_pred = load_gt_and_pred(raw_dir, idx)
        _, masked_pred = load_gt_and_pred(masked_dir, idx)
        rows.append((idx, thumb(gt), thumb(raw_pred), thumb(masked_pred)))
    sections.append((method, color, rows))

row_h = sections[0][2][0][1].size[1]
grid_w = THUMB_W * 3 + GAP * 2
grid_h = COL_LABEL_H + sum(SECTION_H + len(rows) * (row_h + ROW_LABEL_H) for _, _, rows in sections)

grid = Image.new("RGB", (grid_w, grid_h), "white")
draw = ImageDraw.Draw(grid)

col_titles = ["Foto original (GT)", "Prediccion RAW (sin mascara)", "Prediccion CON MASCARA"]
for i, title in enumerate(col_titles):
    draw.text((i * (THUMB_W + GAP) + 8, 6), title, fill="black", font=FONT_MED)

y = COL_LABEL_H
for method, color, rows in sections:
    draw.rectangle([0, y, grid_w, y + SECTION_H], fill=color)
    draw.text((14, y + 10), method, fill="white", font=FONT_BIG)
    y += SECTION_H
    for idx, gt, raw_pred, masked_pred in rows:
        draw.text((8, y + 2), f"{method.lower()} -- eval frame {idx}", fill=color, font=FONT_SMALL)
        y += ROW_LABEL_H
        grid.paste(gt, (0, y))
        grid.paste(raw_pred, (THUMB_W + GAP, y))
        grid.paste(masked_pred, (THUMB_W * 2 + GAP * 2, y))
        y += row_h

out_path = OUT / "visual_comparison_masking.jpg"
grid.save(out_path, quality=92)
print(f"[OK] {out_path}")
