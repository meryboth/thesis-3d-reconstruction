"""
Genera la carpeta images_N/ (downscale factor N, division entera de ancho y
alto) que el dataparser de Nerfstudio espera encontrar ya generada cuando se
le pasa --downscale-factor explicito. ns-process-data la genera sola como
parte de su pipeline; como los datasets hibridos de esta tesis se arman a
mano a partir de un componente COLMAP (colmap_component_to_nerfstudio.py),
ese paso nunca corre, y el training rompe con FileNotFoundError buscando
images_N/<archivo> la primera vez.

Uso:
    python generate_downscaled_images.py <carpeta_dataset> <factor>

Ejemplo:
    python generate_downscaled_images.py \
        "C:\\nerfstudio_work\\thesis\\03-panteon-asociacion-espanola\\03-datasets\\hibrido\\dataset-splatfacto-910-full" \
        8
"""
import sys
from pathlib import Path
from PIL import Image


def main():
    if len(sys.argv) != 3:
        print("Uso: python generate_downscaled_images.py <carpeta_dataset> <factor>")
        sys.exit(1)

    dataset_dir = Path(sys.argv[1])
    factor = int(sys.argv[2])
    src_dir = dataset_dir / "images"
    dst_dir = dataset_dir / f"images_{factor}"
    dst_dir.mkdir(exist_ok=True)

    files = sorted(src_dir.glob("*.jpg")) + sorted(src_dir.glob("*.png"))
    print(f"[info] {len(files)} imagenes en {src_dir}, generando factor {factor} -> {dst_dir}")

    for i, f in enumerate(files):
        out_path = dst_dir / f.name
        if out_path.exists():
            continue
        with Image.open(f) as im:
            w, h = im.size
            im_small = im.resize((w // factor, h // factor), Image.LANCZOS)
            im_small.save(out_path, quality=90)
        if (i + 1) % 100 == 0:
            print(f"  {i + 1}/{len(files)}")

    print(f"[OK] {dst_dir} ({len(files)} archivos)")


if __name__ == "__main__":
    main()
