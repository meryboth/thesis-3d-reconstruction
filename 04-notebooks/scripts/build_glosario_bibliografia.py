"""
Genera thesis/05-tesis/glosario/glosario.md y thesis/05-tesis/bibliografia/
bibliografia.md como documentos independientes de la tesis (no ya solo texto
embebido dentro de los capitulos 2 y 3), pedido explicito de la usuaria
(26/08): "armemos un md de glosario aparte y un md de bibliografia aparte".

El texto SIGUE viviendo (sin cambios) dentro de capitulo2_marco_teorico.md
("Glosario de terminos") y capitulo2/capitulo3 ("Referencias del Capitulo
N") -- ese sigue siendo el lugar donde se redacta/edita el contenido, y
donde el lector que lee la tesis capitulo por capitulo los encuentra en su
lugar natural. Este script solo los EXTRAE hacia dos documentos aparte, de
alcance general (toda la tesis, no un capitulo puntual), para que existan
como archivos propios -- consumidos despues tanto por el sitio web
(06-sitio-web/scripts/prepare_content.py los trata como un capitulo mas)
como por cualquier ensamblado futuro de la tesis completa en PDF.

Correr de nuevo cada vez que cambie el glosario o las referencias dentro de
Cap. 2 / Cap. 3.
"""
import re
from pathlib import Path

TESIS_DIR = Path(r"C:\nerfstudio_work\thesis\05-tesis")
CAP2 = TESIS_DIR / "capitulo2_marco_teorico" / "capitulo2_marco_teorico.md"
CAP3 = TESIS_DIR / "capitulo3_caso_de_estudio" / "capitulo3_caso_de_estudio.md"
OUT_GLOSARIO = TESIS_DIR / "glosario" / "glosario.md"
OUT_BIBLIOGRAFIA = TESIS_DIR / "bibliografia" / "bibliografia.md"

# entradas duplicadas entre Cap. 2 y Cap. 3 (mismo paper citado en ambos, con
# formato levemente distinto en cada uno) -- se descartan al fusionar,
# quedandose con la version de Cap. 2 (mas completa: DOI + coautor Genchev
# en el caso de Rangelov et al. 2026).
DEDUPE_FRAGMENTS = [
    r"Rangelov, D\., Waanders, S\., Waanders, K\., Genchev, E\., van Keulen, M\. y Miltchev, R\. \(2026\)\.[^\n]*\n\n?",
    r"> Rangelov, D\., Waanders, S\., Waanders, K\., van Keulen, M\., & Miltchev, R\. \(2026\)\.[^\n]*\n\n?",
    r"> Yu, Y\., Verbree, E\., van Oosterom, P\., & Pottgiesser, U\. \(2025\)\.[^\n]*\n\n?",
]


def extract_block(md_text: str, heading_pattern: str, stop_pattern: str = None, drop_heading: bool = True) -> str:
    m = re.search(r"^\*\*(" + heading_pattern + r")\*\*\s*$", md_text, re.MULTILINE)
    if not m:
        raise RuntimeError(f"no se encontro encabezado /{heading_pattern}/")
    start = m.end() if drop_heading else m.start()
    end = len(md_text)
    if stop_pattern:
        m_stop = re.search(r"^\*\*(" + stop_pattern + r")", md_text[m.end():], re.MULTILINE)
        if m_stop:
            end = m.end() + m_stop.start()
    return md_text[start:end].strip()


def build_glosario():
    text = CAP2.read_text(encoding="utf-8")
    block = extract_block(text, r"Glosario de t[ée]rminos[^\n]*")
    # se descarta el parrafo introductorio ("Los siguientes terminos...") --
    # pedido explicito (26/08): que el glosario standalone arranque directo
    # en los terminos, sin intro. El parrafo sigue intacto en Cap. 2.
    block = re.sub(r"^Los siguientes t[ée]rminos[^\n]*\n\n", "", block)
    # idem con el marcador de cierre "-- Fin del Capitulo 2 --": tiene sentido
    # en Cap. 2 (ahi es el cierre real del capitulo) pero no en esta pagina
    # standalone, que no es "el capitulo 2".
    block = re.sub(r"\n*\*— Fin del Cap[ií]tulo\s+\d+\s*—\*\s*$", "", block)
    out = f"{block}\n"
    OUT_GLOSARIO.write_text(out, encoding="utf-8")
    print(f"[OK] {OUT_GLOSARIO} ({len(block)} caracteres)")


def build_bibliografia():
    cap2_text = CAP2.read_text(encoding="utf-8")
    cap3_text = CAP3.read_text(encoding="utf-8")

    cap2_block = extract_block(cap2_text, r"Referencias del Cap[ií]tulo\s+2", stop_pattern=r"Glosario de t[ée]rminos")
    cap3_block = extract_block(cap3_text, r"Referencias del Cap[ií]tulo\s+3")

    for frag in DEDUPE_FRAGMENTS:
        cap3_block = re.sub(frag, "", cap3_block)
    # normaliza el bloque en formato blockquote de Cap. 3 a texto plano
    # ([ \t]? y no \s?: \s tambien matchea \n y se come la linea en blanco
    # siguiente, juntando entradas que deben quedar separadas)
    cap3_block = re.sub(r"^>[ \t]?", "", cap3_block, flags=re.MULTILINE)

    out = f"{cap2_block}\n\n{cap3_block}\n"
    OUT_BIBLIOGRAFIA.write_text(out, encoding="utf-8")
    print(f"[OK] {OUT_BIBLIOGRAFIA} ({len(out)} caracteres)")


if __name__ == "__main__":
    build_glosario()
    build_bibliografia()
