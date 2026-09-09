"""
Arma plantilla-formato.docx a partir del TESIS-FORMATO.docx que entrega la facultad.

La plantilla original pesa ~16 MB porque incluye el texto y las imagenes de la tesis
de ejemplo. Para generar el .docx solo hacen falta las definiciones de formato, asi
que aca se copia todo menos el contenido: quedan los estilos, las fuentes embebidas,
el pie de pagina, el tema y la numeracion (~1,3 MB), y el paquete entra comodo en el
repo. Con eso el build deja de depender de un archivo suelto en Downloads.

Solo hay que volver a correr esto si la facultad cambia el formato y entrega un
TESIS-FORMATO.docx nuevo.

Uso:
    python reducir_plantilla.py [ruta\\al\\TESIS-FORMATO.docx]
"""

import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DESTINO = HERE / "plantilla-formato.docx"
ORIGEN_POR_DEFECTO = Path(r"C:\Users\mboth\Downloads\TESIS-FORMATO.docx")

R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

# document.xml y sus relaciones se reemplazan enteros al generar la tesis, asi que
# en la plantilla alcanza con dejarlos vacios y validos.
STUB_DOC = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    '<w:body><w:p/></w:body></w:document>'
).encode("utf-8")

STUB_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    f'<Relationship Id="rIdStyles" Type="{R}/styles" Target="styles.xml"/>'
    f'<Relationship Id="rIdSettings" Type="{R}/settings" Target="settings.xml"/>'
    f'<Relationship Id="rIdFontTable" Type="{R}/fontTable" Target="fontTable.xml"/>'
    f'<Relationship Id="rIdTheme" Type="{R}/theme" Target="theme/theme1.xml"/>'
    f'<Relationship Id="rIdNumbering" Type="{R}/numbering" Target="numbering.xml"/>'
    f'<Relationship Id="rIdFooter" Type="{R}/footer" Target="footer1.xml"/>'
    '</Relationships>'
).encode("utf-8")


def reducir(origen: Path, destino: Path):
    with zipfile.ZipFile(origen) as z:
        piezas = {}
        for nombre in z.namelist():
            if nombre.startswith("word/media/"):
                continue                       # imagenes del contenido, no del formato
            if nombre == "word/document.xml":
                piezas[nombre] = STUB_DOC
            elif nombre == "word/_rels/document.xml.rels":
                piezas[nombre] = STUB_RELS
            else:
                piezas[nombre] = z.read(nombre)

    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for nombre, datos in piezas.items():
            z.writestr(nombre, datos)

    print(f"{origen.name}: {origen.stat().st_size / 1e6:.1f} MB")
    print(f"{destino.name}: {destino.stat().st_size / 1e6:.2f} MB "
          f"({len(piezas)} piezas)")


if __name__ == "__main__":
    origen = Path(sys.argv[1]) if len(sys.argv) > 1 else ORIGEN_POR_DEFECTO
    if not origen.exists():
        sys.exit(f"No se encontro la plantilla original: {origen}")
    reducir(origen, DESTINO)
