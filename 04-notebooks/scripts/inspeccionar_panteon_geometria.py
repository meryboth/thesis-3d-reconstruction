from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
out=Path(r'C:\nerfstudio_work\thesis\07-modelado\03-panteon-asociacion-catalana')
p=np.load(out/'nube_muestreada.npy');p=p[(abs(p[:,0])<12)&(abs(p[:,1])<12)]
sheet=Image.new('RGB',(1400,1440),'white');d=ImageDraw.Draw(sheet)
for j,(a,b,title,mask) in enumerate([(0,1,'PLANTA general',p[:,2]>1.5),(0,1,'PLANTA corte z=3..5',(p[:,2]>3)&(p[:,2]<5)),(0,2,'ALZADO XZ',p[:,2]>0),(1,2,'ALZADO YZ',p[:,2]>0)]):
 im=Image.new('RGB',(700,700),(235,235,235));pix=im.load();pts=p[mask];idx=np.argsort(pts[:,2 if b==1 else (1 if a==0 else 0)])
 for row in pts[idx]:
  x=int(row[a]*27+350);y=int(-row[b]*27+(350 if b==1 else 650))
  if 0<=x<700 and 0<=y<700:pix[x,y]=tuple(row[3:6].astype(int))
 x=(j%2)*700;y=(j//2)*720;sheet.paste(im,(x,y+20));d.text((x+8,y+3),title,fill='black')
sheet.save(out/'proyecciones_inspeccion.jpg')
