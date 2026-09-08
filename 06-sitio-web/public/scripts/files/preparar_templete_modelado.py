"""Prepara insumos de referencia (hoja de contacto de fotogramas, nube
muestreada) para la reconstrucción geométrica asistida por IA de Templete
Central (Cap.6, sección 6.3.4)."""
from pathlib import Path
import numpy as np,json
from PIL import Image,ImageOps,ImageDraw
from plyfile import PlyData,PlyElement
base=Path(r'C:\nerfstudio_work\thesis')
out=base/'07-modelado/02-templete-central';out.mkdir(parents=True,exist_ok=True)
imgs=sorted((base/'02-templete-central/03-datasets/dji/dataset-splatfacto-1232-full/images').glob('*.png'))
sheet=Image.new('RGB',(1600,1000),'white');d=ImageDraw.Draw(sheet)
for k,i in enumerate(np.linspace(0,len(imgs)-1,16,dtype=int)):
 im=ImageOps.contain(Image.open(imgs[i]).convert('RGB'),(400,225));x=k%4*400;y=k//4*250
 sheet.paste(im,(x,y));d.text((x+8,y+230),imgs[i].name,fill='black')
sheet.save(out/'referencias_dji.jpg')
src=base/'02-templete-central/02-resultados-finales/dji/colmap-fotogrametria/nube-densa.xyz'
rows=[]
with src.open() as f:
 for i,line in enumerate(f):
  if i%24==0:rows.append(line)
p=np.loadtxt(rows,dtype=np.float32);np.save(out/'nube_muestreada.npy',p)
v=np.empty(len(p),dtype=[('x','f4'),('y','f4'),('z','f4'),('red','u1'),('green','u1'),('blue','u1')])
for k,name in enumerate(v.dtype.names):v[name]=p[:,k]
PlyData([PlyElement.describe(v,'vertex')],text=False).write(out/'referencia_densa_muestreada.ply')
print('Puntos:',len(p),'Cuantiles:',np.quantile(p[:,:3],[.01,.5,.99],axis=0).tolist(),flush=True)
# Orthographic point projections cropped to the central building.
p=p[(np.abs(p[:,0])<8)&(np.abs(p[:,1])<8)]
sheet=Image.new('RGB',(1500,550),'white');d=ImageDraw.Draw(sheet)
for j,(a,b,title) in enumerate([(0,1,'PLANTA XY'),(0,2,'ALZADO XZ'),(1,2,'ALZADO YZ')]):
 im=Image.new('RGB',(500,500),(235,235,235));pix=im.load()
 sc=28;offset=np.array([250,250 if b==1 else 460])
 idx=np.argsort(p[:,2 if b==1 else (1 if a==0 else 0)])
 for row in p[idx]:
  x=int(row[a]*sc+offset[0]);y=int(-row[b]*sc+offset[1])
  if 0<=x<500 and 0<=y<500:pix[x,y]=tuple(row[3:6].astype(int))
 sheet.paste(im,(j*500,30));d.text((j*500+12,8),title,fill='black')
sheet.save(out/'proyecciones_nube.jpg')
