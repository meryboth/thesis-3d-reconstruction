"""Refinado visual de ornamentación: referencia frame_01110 y frame_01348.
Follaje y volutas son aproximaciones geométricas; medallón usa fotografía.
Ejecutar tras reconstruir_panteon_blender.py en su mismo diccionario global.
"""
import numpy as np
COL=DETAIL
for o in list(DETAIL.objects):
 if o.name.startswith('Relieve floral idealizado'):
  bpy.data.objects.remove(o,do_unlink=True)
def point_rot(p,k):
 x,y,z=p;a=k*pi/2;return (x*cos(a)-y*sin(a),x*sin(a)+y*cos(a),z)
def tube(name,pts,r,m=TRIM,k=0):
 pts=[Vector(point_rot(p,k)) for p in pts];vs=[];N=8
 for i,p in enumerate(pts):
  tangent=(pts[min(i+1,len(pts)-1)]-pts[max(0,i-1)]).normalized();u=tangent.cross(Vector((0,0,1)))
  if u.length<.01:u=tangent.cross(Vector((0,1,0)))
  u.normalize();v=tangent.cross(u).normalized()
  vs.extend([tuple(p+r*(cos(2*pi*j/N)*u+sin(2*pi*j/N)*v)) for j in range(N)])
 fs=[tuple(reversed(range(N))),tuple(range((len(pts)-1)*N,len(pts)*N))]+[(i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j) for i in range(len(pts)-1) for j in range(N)]
 o=mesh(name,vs,fs,m)
 for f in o.data.polygons:f.use_smooth=True
 return o
def leaf(x,z,length,width,angle,k,y=-4.245):
 # Lobed acanthus leaf with raised midrib and curled tip; closed double surface.
 vs=[];steps=14
 for back in [False,True]:
  for i in range(steps+1):
   t=i/steps;w=width*(.08+sin(pi*t)**.7)*(.79+.21*cos(10*pi*t))
   for s in [-1,0,1]:
    u=s*w;v=length*t;xx=x+u*cos(angle)+v*sin(angle);zz=z-u*sin(angle)+v*cos(angle)
    yy=y-(.055*sin(pi*t)+.10*t**4)*(1-.55*abs(s))+( .022 if back else 0)
    vs.append(point_rot((xx,yy,zz),k))
 n=(steps+1)*3;fs=[]
 for i in range(steps):
  for j in range(2):
   a=i*3+j;fs += [(a,a+1,a+4,a+3),(n+a+3,n+a+4,n+a+1,n+a)]
 boundary=[i*3 for i in range(steps+1)]+[steps*3+1,steps*3+2]+[i*3+2 for i in reversed(range(steps))]+[1]
 fs += [(boundary[i],boundary[(i+1)%len(boundary)],boundary[(i+1)%len(boundary)]+n,boundary[i]+n) for i in range(len(boundary))]
 o=mesh('Hoja acanto interpretada',vs,fs,TRIM)
 for f in o.data.polygons:f.use_smooth=True
 return o
def scroll(x,z,rx,rz,k,y=-4.27,sign=1,r=.023):
 pts=[]
 for i in range(49):
  t=i/48;ang=sign*(t*2*pi*1.30);scale=1-.85*t
  pts.append((x+rx*scale*cos(ang),y-.015*sin(t*pi),z+rz*scale*sin(ang)))
 return tube('Voluta ornamental',pts,r,TRIM,k)
for k in range(4):
 # Arc moulding around the segmental tympanum.
 for dz,r in [(0,.033),(.07,.025)]:
  pts=[(2.1*cos(pi*i/64),-4.17,7.83+dz+.85*sin(pi*i/64)) for i in range(65)]
  tube('Bocel curvo fronton',pts,r,TRIM,k)
 # Branches curl towards center; leaves vary orientation as in reference.
 for sign in [-1,1]:
  for j in range(5):
   x=sign*(.33+j*.31);z=7.98+.15*(1-j/5)
   scroll(x,z+.11,.20,.16,k,sign=sign)
   for angle,dx,zz,ln in [(sign*.9,-sign*.05,0,.30),(sign*1.8,sign*.06,.02,.30),(-sign*.35,0,.08,.34)]:
    leaf(x+dx,z+zz,ln,.095,angle,k)
  tube('Ramo acanto',[(sign*(.15+i*.055),-4.28,7.98+.065*sin(i*pi/28)) for i in range(29)],.024,TRIM,k)
 # Overdoor has a smaller curved band and dense foliate ornament.
 tube('Arco sobrepuerta',[(1.17*cos(pi*i/48),-4.36,6.34+.36*sin(pi*i/48)) for i in range(49)],.039,ROOF,k)
 for sign in [-1,1]:
  for j in range(3):
   x=sign*(.18+j*.28);z=6.34+.08*(1-j/3)
   scroll(x,z,.17,.115,k,y=-4.37,sign=sign,r=.02)
   leaf(x,z,.22,.09,sign*.8,k,y=-4.36);leaf(x,z,.19,.08,sign*1.9,k,y=-4.36)
 leaf(0,6.37,.31,.10,0,k,y=-4.36)
 # Scrollwork of each gate (upper mirrored curls and lower curls).
 for sign in [-1,1]:
  for j in range(2):
   x=sign*(.18+j*.28)
   scroll(x,5.84,.14,.19,k,y=-4.215,sign=sign,r=.014)
   scroll(x,4.19,.105,.13,k,y=-4.215,sign=-sign,r=.014)
 # Dentil-like leaf sequence along the narrow overdoor arch.
 for i in range(21):
  x=-1.04+i*.104;z=6.38+.32*math.sqrt(max(0,1-(x/1.15)**2))
  leaf(x,z,.065,.026,-x*.4,k,y=-4.39)
# Additional four center columns: photos show 3 columns per face.
COL=CORE
for x,y in [(0,-1.07),(0,1.07),(-1.03,0),(1.03,0)]:
 lathe('Columna intermedia linterna',(x,y),[(11.26,.24),(11.37,.24),(11.4,.16),(12.25,.13),(12.3,.24),(12.43,.24)],TRIM,24)
 box('Capitel intermedio',(x,y,12.44),(.53,.53,.17),TRIM)
COL=DETAIL
# Ionic capital scrolls and fluting on all eight columns.
for x,y in [(x,y) for x in [-1.03,1.03] for y in [-1.07,1.07]]+[(0,-1.07),(0,1.07),(-1.03,0),(1.03,0)]:
 for sign in [-1,1]:scroll(x+sign*.16,12.33,.085,.07,0,y=y-.20,sign=sign,r=.02)
 for a in range(12):
  t=2*pi*a/12;tube('Estria columna',[(x+.153*cos(t),y+.153*sin(t),11.45),(x+.133*cos(t),y+.133*sin(t),12.20)],.009,JOINT)
# Front inscription, directly transcribed from photograph, no attribution added.
box('Placa institucional',(0,-4.29,7.07),(2.7,.10,.40),TRIM)
cu=bpy.data.curves.new('Inscripcion fotografiada','FONT');cu.body='ASSOCIACIO CATALANA de SOCORS MUTUALS\nMONTEPIO MONTSERRAT\nFUNDADA EN 1857';cu.align_x='CENTER';cu.align_y='CENTER';cu.size=.102;cu.space_line=.88;cu.extrude=.001
o=bpy.data.objects.new('Inscripcion fachada principal',cu);DETAIL.objects.link(o);o.location=(0,-4.351,7.07);o.rotation_euler=(pi/2,0,0);o.data.materials.append(IRON)
for x in [-1.48,1.48]:scroll(x,7.06,.11,.20,0,y=-4.28,sign=1 if x>0 else -1,r=.027)
# Photographic medallion from front photo. Texture preserves iconography;
# surface thickness is representational and is NOT a depth reconstruction.
im=bpy.data.images.load(str(OUT/'detalle_frente.jpg'),check_existing=True);w,h=im.size
pix=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4);crop=pix[h-429:h-333,940:1032,:].copy();hh,ww=crop.shape[:2]
tex=bpy.data.images.new('Medallon fuente frame_01348',width=ww,height=hh);tex.pixels.foreach_set(crop.ravel());tex.filepath_raw=str(OUT/'medallon_fotografico.png');tex.file_format='PNG';tex.save();tex.pack()
m=bpy.data.materials.new('Medallon fotografico');m.use_nodes=True;nd=m.node_tree.nodes.new('ShaderNodeTexImage');nd.image=tex;m.node_tree.links.new(nd.outputs['Color'],m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
N=64;vs=[(0,-4.35,8.26)]+[(.37*cos(2*pi*i/N),-4.31,8.26+.40*sin(2*pi*i/N)) for i in range(N)]+[(0,-4.27,8.26)];fs=[(0,1+i,1+(i+1)%N) for i in range(N)]+[(N+1,1+(i+1)%N,1+i) for i in range(N)]
o=mesh('Medallon central con imagen de referencia',vs,fs,m);uv=o.data.uv_layers.new(name='Foto')
for f in o.data.polygons:
 for li in f.loop_indices:
  co=o.data.vertices[o.data.loops[li].vertex_index].co;uv.data[li].uv=(.5+co.x/.74,.5+(co.z-8.26)/.80)
tube('Borde medallon',[(.39*cos(2*pi*i/64),-4.33,8.26+.42*sin(2*pi*i/64)) for i in range(65)],.028,TRIM)
# Ornamental ends to the stone cross, seen in drone photo.
for x,z,a in [(0,16.53,0),(-.44,16.22,-pi/2),(.44,16.22,pi/2)]:
 leaf(x,z,.14,.105,a,0,y=-.075)
print('Refinado ornamental completo:',len(DETAIL.objects),'objetos de detalle')
