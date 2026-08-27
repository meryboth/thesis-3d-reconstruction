"""Arma un grid comparativo (original | RMBG foreground | mascara final | limpio)
por cada muestra del POC de limpieza agresiva, para revision visual rapida."""
from pathlib import Path
from PIL import Image

SRC = Path(r"C:\nerfstudio_work\panteon-chacarita\templete-central\dataset-dji-comfyui-clean-aggressive-poc")
OUT = Path(r"C:\nerfstudio_work\thesis\00-auditoria\comfyui-aggressive-poc")
OUT.mkdir(parents=True, exist_ok=True)

stems = sorted({p.name.split("_original")[0] for p in SRC.glob("*_original.png")})
THUMB_W = 380

cols = ["original", "rmbg_fg", "mask", "clean"]
labels = ["Original", "RMBG foreground (sujeto)", "Mascara final (union)", "Resultado limpio"]

rows = []
for stem in stems:
    imgs = []
    for c in cols:
        p = SRC / f"{stem}_{c}.png"
        im = Image.open(p).convert("RGB")
        w, h = im.size
        new_h = int(h * THUMB_W / w)
        imgs.append(im.resize((THUMB_W, new_h)))
    rows.append((stem, imgs))

row_h = max(im.size[1] for _, imgs in rows for im in imgs)
label_h = 28
grid_w = THUMB_W * len(cols)
grid_h = label_h + (row_h + label_h) * len(rows)

grid = Image.new("RGB", (grid_w, grid_h), "white")
from PIL import ImageDraw
draw = ImageDraw.Draw(grid)

for ci, lab in enumerate(labels):
    draw.text((ci * THUMB_W + 8, 6), lab, fill="black")

y = label_h
for stem, imgs in rows:
    draw.text((8, y + 4), stem, fill="red")
    for ci, im in enumerate(imgs):
        grid.paste(im, (ci * THUMB_W, y + label_h))
    y += row_h + label_h

out_path = OUT / "aggressive_poc_grid.png"
grid.save(out_path)
print(f"[OK] {out_path} ({grid_w}x{grid_h})")
