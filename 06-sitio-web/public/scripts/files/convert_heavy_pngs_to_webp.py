"""
Convierte a WebP los PNG mas pesados referenciados desde los capitulos de
la tesis (diagramas y fotos guardados como PNG sin comprimir, algunos de
varios MB) -- WebP da una compresion mucho mejor que PNG tanto para fotos
como para diagramas con texto/lineas finas (a diferencia de JPEG, que
introduce artefactos visibles alrededor de texto).

Convierte in-place junto al PNG original (mismo directorio), y NO borra el
PNG viejo -- eso lo hace el caller despues de confirmar visualmente que el
.webp se ve bien y de actualizar las referencias en los .md.
"""
from pathlib import Path
from PIL import Image

TARGETS = [
    r"C:\nerfstudio_work\thesis\05-tesis\capitulo2_marco_teorico\media\image1.png",
    r"C:\nerfstudio_work\thesis\05-tesis\capitulo2_marco_teorico\media\image2.png",
    r"C:\nerfstudio_work\thesis\05-tesis\capitulo2_marco_teorico\media\image3.png",
    r"C:\nerfstudio_work\thesis\05-tesis\capitulo2_marco_teorico\media\image4.png",
    r"C:\nerfstudio_work\thesis\05-tesis\capitulo3_caso_de_estudio\media\image4.png",
    r"C:\nerfstudio_work\thesis\00-auditoria\fidelidad-geometrica\02-templete-central\sfm-cobertura\vista_lateral_01.png",
    r"C:\nerfstudio_work\thesis\00-auditoria\fidelidad-geometrica\02-templete-central\sfm-cobertura\vista_lateral_02.png",
]

QUALITY = 88

for src_str in TARGETS:
    src = Path(src_str)
    dst = src.with_suffix(".webp")
    im = Image.open(src).convert("RGB")
    im.save(dst, "WEBP", quality=QUALITY, method=6)
    before = src.stat().st_size
    after = dst.stat().st_size
    print(f"{src.name}: {before/1024:.0f} KB -> {dst.name}: {after/1024:.0f} KB ({100*after/before:.0f}%)")
