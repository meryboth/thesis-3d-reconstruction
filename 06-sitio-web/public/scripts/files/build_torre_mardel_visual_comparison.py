"""
Grilla Foto original / Nerfacto / Splatfacto para el experimento adicional de
la Torre Tanque (Mar del Plata). Reutiliza el frame GT|prediccion ya generado
por ns-eval (--render-output-path): recorta la mitad GT de un archivo y la
mitad de prediccion de cada tecnica, y arma un panel de 3 columnas.
Capitulo 5, seccion 5.11.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\torre-mardel-eval")
FRAME = "eval_img_0005.png"

nerf_img = Image.open(OUT_DIR / "nerfacto_renders" / FRAME)
splat_img = Image.open(OUT_DIR / "splatfacto_renders" / FRAME)

w, h = nerf_img.size
gt = nerf_img.crop((0, 0, w // 2, h))
nerf_pred = nerf_img.crop((w // 2, 0, w, h))

w2, h2 = splat_img.size
splat_pred = splat_img.crop((w2 // 2, 0, w2, h2)).resize((w // 2, h))

panel_w = (w // 2) * 3
label_h = 34
panel = Image.new("RGB", (panel_w, h + label_h), "white")
draw = ImageDraw.Draw(panel)
try:
    font = ImageFont.truetype("arial.ttf", 20)
except Exception:
    font = ImageFont.load_default()

labels = ["Foto original", "Nerfacto (PSNR 19,24 dB)", "Splatfacto (PSNR 30,90 dB)"]
imgs = [gt, nerf_pred, splat_pred]
for i, (img, label) in enumerate(zip(imgs, labels)):
    x0 = i * (w // 2)
    panel.paste(img, (x0, label_h))
    bbox = draw.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((x0 + (w // 2 - tw) // 2, 6), label, fill="black", font=font)

out_path = OUT_DIR / "torre_mardel_visual_comparison.jpg"
panel.save(out_path, quality=90)
print(f"[OK] {out_path}")
