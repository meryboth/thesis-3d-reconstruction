"""Arma una hoja de contacto con fotogramas muestreados del dataset de Los
Paraguas, como referencia visual al ajustar geometría en Blender."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import json
root=Path(r'C:\nerfstudio_work\thesis\01-paraguas-vicentelopez')
out=root/'04-modelo-geometrico'
out.mkdir(exist_ok=True)
files=sorted((root/'03-datasets/dataset-dron/images').glob('*.jpg'))
indices=[0,60,120,180,240,300,360,420,480,540,600,706]
sheet=Image.new('RGB',(1200,900),'white')
d=ImageDraw.Draw(sheet)
for k,i in enumerate(indices):
    im=Image.open(files[i]); im.thumbnail((400,270))
    x=(k%3)*400; y=(k//3)*225
    im=ImageOps.contain(im,(400,200))
    sheet.paste(im,(x,y)); d.text((x+8,y+202),files[i].name,fill='black')
sheet.save(out/'referencias.jpg')
print(out/'referencias.jpg')
