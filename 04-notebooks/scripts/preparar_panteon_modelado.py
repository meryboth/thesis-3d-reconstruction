from pathlib import Path
import numpy as np,json
from PIL import Image,ImageOps,ImageDraw
from plyfile import PlyData,PlyElement
base=Path(r'C:\nerfstudio_work\thesis')
out=base/'07-modelado/03-panteon-asociacion-catalana';out.mkdir(parents=True,exist_ok=True);(out/'proceso').mkdir(exist_ok=True)
imgs=sorted((base/'03-panteon-asociacion-catalana/03-datasets/dji/dataset-splatfacto-1507-full/images').glob('*.jpg'))
sheet=Image.new('RGB',(1600,1250),'white');d=ImageDraw.Draw(sheet)
for k,i in enumerate(np.linspace(0,len(imgs)-1,20,dtype=int)):
 im=ImageOps.contain(Image.open(imgs[i]).convert('RGB'),(400,225));x=k%4*400;y=k//4*250
 sheet.paste(im,(x,y));d.text((x+8,y+230),imgs[i].name,fill='black')
sheet.save(out/'referencias_dji.jpg')
src=base/'03-panteon-asociacion-catalana/02-resultados-finales/dji/colmap-fotogrametria/nube-densa.xyz'
rows=[]
with src.open() as f:
 for i,line in enumerate(f):
  if i%24==0:rows.append(line)
p=np.loadtxt(rows,dtype=np.float32);np.save(out/'nube_muestreada.npy',p)
v=np.empty(len(p),dtype=[('x','f4'),('y','f4'),('z','f4'),('red','u1'),('green','u1'),('blue','u1')])
for k,name in enumerate(v.dtype.names):v[name]=p[:,k]
PlyData([PlyElement.describe(v,'vertex')],text=False).write(out/'referencia_densa_muestreada.ply')
print('Puntos:',len(p),'Cuantiles:',np.quantile(p[:,:3],[.01,.5,.99],axis=0).tolist(),flush=True)
