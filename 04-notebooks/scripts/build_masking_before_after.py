"""Genera comparaciones antes/despues (foto original | mascara | resultado
aislado con la mascara de entrenamiento RMBG) para varios fotogramas
representativos del Templete Central -- para el Cap. 5, seccion de
preprocesamiento."""
from pathlib import Path

from PIL import Image

IMAGES_DIR = Path(r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-masked-raw-1232-splatfacto\images")
MASKS_DIR = Path(r"C:\nerfstudio_work\thesis\02-templete-central\03-datasets\dji\dataset-masked-raw-1232-splatfacto\masks")
OUT_DIR = Path(r"C:\nerfstudio_work\thesis\00-auditoria\preprocesamiento-mascara")
OUT_DIR.mkdir(parents=True, exist_ok=True)

FRAMES = ["00000", "00308", "00462", "00616", "00924", "01078"]
THUMB_W = 600


def main():
    for stem in FRAMES:
        img = Image.open(IMAGES_DIR / f"{stem}.png").convert("RGB")
        mask = Image.open(MASKS_DIR / f"{stem}.png").convert("L")

        w, h = img.size
        new_h = int(h * THUMB_W / w)
        img_small = img.resize((THUMB_W, new_h))
        mask_small = mask.resize((THUMB_W, new_h), Image.NEAREST)
        mask_rgb = mask_small.convert("RGB")

        black = Image.new("RGB", img_small.size, (0, 0, 0))
        result = Image.composite(img_small, black, mask_small)

        gap = 10
        combo = Image.new("RGB", (THUMB_W * 3 + gap * 2, new_h), (255, 255, 255))
        combo.paste(img_small, (0, 0))
        combo.paste(mask_rgb, (THUMB_W + gap, 0))
        combo.paste(result, (THUMB_W * 2 + gap * 2, 0))

        out_path = OUT_DIR / f"comparacion_{stem}_mascara.jpg"
        combo.save(out_path, quality=92)
        print(f"[OK] {out_path}")


if __name__ == "__main__":
    main()
