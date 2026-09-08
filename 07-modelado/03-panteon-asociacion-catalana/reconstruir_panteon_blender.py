"""Panteón Catalán: reconstrucción interpretativa desde nube DJI y fotografías.
Ejecutar con Blender. Unidades SfM sin calibración métrica. Ornamentación idealizada.
"""
import bpy, math, bmesh, json
from pathlib import Path
from mathutils import Vector
from math import sin,cos,pi
OUT=Path(__file__).resolve().parent if '__file__' in globals() else Path(r'C:\nerfstudio_work\thesis\07-modelado\03-panteon-asociacion-catalana')
SC=bpy.context.scene
CORE=bpy.data.collections.new('PANTEON | geometria referenciada');SC.collection.children.link(CORE)
DETAIL=bpy.data.collections.new('PANTEON | detalles interpretados');SC.collection.children.link(DETAIL)
STUDIO=bpy.data.collections.new('PANTEON | presentacion');SC.collection.children.link(STUDIO)
COL=CORE
def mat(name,color,noise=False):
 m=bpy.data.materials.new('PC '+name);m.diffuse_color=(*color,1);m.use_nodes=True
 n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.85
 if noise:
  g=n.new('ShaderNodeNewGeometry');t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=2.4;t.inputs['Detail'].default_value=4;l.new(g.outputs['Position'],t.inputs['Vector'])
  r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(*(v*.62 for v in color),1);r.color_ramp.elements[1].color=(*color,1);l.new(t.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Base Color'])
 return m
STONE=mat('piedra clara',(.65,.65,.59),True);TRIM=mat('molduras',(.77,.76,.68),True);ROOF=mat('piedra envejecida',(.29,.30,.27),True);BASE=mat('basamento',(.34,.36,.34),True);IRON=mat('hierro',(.075,.085,.078));DARK=mat('hueco',(.018,.022,.019));JOINT=mat('juntas',(.28,.29,.26));GROUND=mat('suelo neutro',(.24,.27,.25))
def mesh(name,vs,fs,m):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 o=bpy.data.objects.new(name,me);COL.objects.link(o);o.data.materials.append(m);return o
def box(name,loc,size,m=STONE):
 x,y,z=size;v=[(loc[0]+i*x/2,loc[1]+j*y/2,loc[2]+k*z/2) for k in [-1,1] for i,j in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 return mesh(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)
def prism(name,poly,z0,z1,m):
 n=len(poly);return mesh(name,[(x,y,z) for z in [z0,z1] for x,y in poly],[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],m)
def lathe(name,c,profile,m,n=64):
 vs=[(c[0]+r*cos(2*pi*i/n),c[1]+r*sin(2*pi*i/n),z) for z,r in profile for i in range(n)];fs=[tuple(reversed(range(n))),tuple(range((len(profile)-1)*n,len(profile)*n))]
 fs += [(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for k in range(len(profile)-1) for i in range(n)]
 o=mesh(name,vs,fs,m)
 for f in o.data.polygons:
  if len(f.vertices)==4:f.use_smooth=True
 return o
def pyramid(name,profile,m):
 vs=[(x*r,y*r,z) for z,r in profile for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]];fs=[(3,2,1,0),tuple(range(len(vs)-4,len(vs)))]+[(k*4+i,k*4+(i+1)%4,(k+1)*4+(i+1)%4,(k+1)*4+i) for k in range(len(profile)-1) for i in range(4)]
 return mesh(name,vs,fs,m)
def beam(name,a,b,r,m=TRIM):
 a,b=Vector(a),Vector(b);d=b-a
 o=lathe(name,(0,0),[(-d.length/2,r),(d.length/2,r)],m,12);o.location=(a+b)/2;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();return o
def rotate(o,k):
 # Mesh coordinates are world-space, rotate about origin.
 a=k*pi/2
 for v in o.data.vertices:
  x,y=v.co.x,v.co.y;v.co.x=x*cos(a)-y*sin(a);v.co.y=x*sin(a)+y*cos(a)
 return o
def arch(name,w,z,h,y,depth,m):
 poly=[(-w,z),(w,z)]+[(w*cos(t),z+h*sin(t)) for t in [pi*i/32 for i in range(1,33)]]
 n=len(poly);vs=[(x,yy,zz) for yy in [y-depth/2,y+depth/2] for x,zz in poly];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];return mesh(name,vs,fs,m)
TERRACE=[(-9.6,7.6),(-8.7,9.6),(8.1,3.3),(2.4,-9.5),(-2.5,-9.5)]
def build_core():
 global COL
 COL=CORE
 prism('Basamento triangular truncado',TERRACE,.12,2.05,BASE)
 box('Cuerpo central',(0,0,4.8),(6.0,6.1,5.5))
 for k in range(4):
  rotate(box('Resalto fachada '+str(k),(0,-3.51,4.8),(3.65,1.17,5.5)),k)
  for x in [-1.68,1.68]:rotate(box('Pilastra angular',(x,-3.89,4.8),(.62,.54,5.5)),k)
  for z,extra,th in [(2.3,.16,.45),(3.05,.09,.15),(7.12,.1,.18),(7.42,.19,.28),(7.68,.29,.23)]:
   rotate(box('Cornisa frente',(0,-3.55,z),(3.95+extra,1.25+extra,th),TRIM if z<7.5 else ROOF),k)
   rotate(box('Cornisa lateral',(0,-2.9,z),(6.25+extra,.45+extra,th),TRIM if z<7.5 else ROOF),k)
  rotate(arch('Fronton segmental',2.18,7.8,.94,-3.79,.68,ROOF),k)
  rotate(arch('Timpano',1.93,7.88,.67,-4.15,.08,TRIM),k)
 pyramid('Cubierta escalonada inferior',[(7.7,3.17),(8.35,3.17),(8.82,2.62),(8.88,2.72),(9.04,2.72),(9.38,2.27),(9.48,2.36),(9.62,2.36),(10.03,1.86),(10.12,1.98),(10.25,1.98),(10.61,1.51),(10.72,1.62),(10.86,1.62),(11.12,1.31)],ROOF)
 box('Zocalo linterna',(0,0,11.14),(2.7,2.75,.26),ROOF)
 for x in [-1.03,1.03]:
  for y in [-1.07,1.07]:
   lathe('Columna linterna',(x,y),[(11.26,.24),(11.37,.24),(11.4,.16),(12.25,.13),(12.3,.24),(12.43,.24)],TRIM,24)
   box('Capitel linterna',(x,y,12.44),(.53,.53,.17),TRIM)
 box('Entablamento linterna',(0,0,12.62),(2.82,2.88,.24),TRIM)
 pyramid('Cubierta escalonada superior',[(12.76,1.48),(12.94,1.48),(13.3,1.12),(13.39,1.24),(13.52,1.24),(13.86,.89),(13.95,1.00),(14.07,1.0),(14.36,.66),(14.44,.77),(14.57,.77),(14.85,.44),(14.93,.54),(15.05,.54),(15.31,.24),(15.43,.22)],ROOF)
 box('Cruz vertical',(0,.08,15.98),(.23,.24,1.15),ROOF);box('Cruz horizontal',(0,.08,16.22),(.94,.24,.22),ROOF)
 c=(-7.51,7.40)
 lathe('Anexo circular',c,[(2.05,1.94),(2.35,1.94),(2.45,1.85),(6.3,1.85),(6.4,1.76),(6.67,1.76)],STONE)
 lathe('Cornisa circular',c,[(6.58,1.81),(6.68,2.02),(6.86,2.02),(7.04,1.88)],ROOF)
 lathe('Cupula anexo',c,[(7.04,1.83),(7.58,1.83),(7.95,1.68),(8.4,1.47),(8.77,1.08),(9.02,.8),(9.22,.40),(9.28,.23)],ROOF)
 lathe('Remate cupula',c,[(9.25,.24),(9.4,.34),(9.57,.18),(9.9,.13),(10.04,.23),(10.2,.025)],ROOF)
def details():
 global COL
 COL=DETAIL
 for k in range(4):
  # Black inset, stone frame and ornamental ironwork, based on photos.
  zbase=2.08 if k in [0,2] else 3.65
  rotate(box('Hueco puerta ventana',(0,-4.116,(zbase+6.13)/2),(1.87,.028,6.13-zbase),DARK),k)
  for x in [-1.05,1.05]:rotate(box('Jamba portal',(x,-4.18,4.25),(.19,.25,4.35),TRIM),k)
  rotate(box('Dintel portal',(0,-4.19,6.25),(2.38,.28,.23),TRIM),k)
  rotate(arch('Sobrepuerta ornamental',1.18,6.34,.36,-4.21,.20,TRIM),k)
  for x in [-.82,-.41,0,.41,.82]:rotate(box('Barrote',(x,-4.16,(zbase+6.08)/2),(.036,.042,6.08-zbase),IRON),k)
  for z in [zbase+.15,4.45,5.95]:rotate(box('Travesano reja',(0,-4.18,z),(1.78,.045,.038),IRON),k)
  # Diagonal diamonds modeled as closed rods.
  for x in [-.43,.43]:
   for z in [max(zbase+.65,3.3),5.25]:
    pts=[(x,-4.19,z-.58),(x+.35,-4.19,z),(x,-4.19,z+.58),(x-.35,-4.19,z)]
    for i in range(4):
     a=pts[i];b=pts[(i+1)%4];ang=k*pi/2
     beam('Rombo herreria',(a[0]*cos(ang)-a[1]*sin(ang),a[0]*sin(ang)+a[1]*cos(ang),a[2]),(b[0]*cos(ang)-b[1]*sin(ang),b[0]*sin(ang)+b[1]*cos(ang),b[2]),.026,IRON)
  # Joint lines and pilaster bases.
  for z in [3.35+i*.43 for i in range(9)]:
   rotate(box('Junta horizontal central',(0,-4.105,z),(3.1,.016,.016),JOINT),k)
   for x in [-2.43,2.43]:rotate(box('Junta paño lateral',(x,-3.06,z),(1.1,.018,.018),JOINT),k)
  for x in [-1.7,1.7]:
   rotate(box('Basamento pilastra',(x,-3.99,2.53),(.70,.55,.87),TRIM),k)
  # Simplified rosettes; explicitly interpretative, not recovered sculpture.
  for xx in [-1.35,-.9,-.45,0,.45,.9,1.35]:
   zz=8.02+.27*(1-(xx/1.6)**2)
   for t in range(5):
    x=xx+.12*cos(t*2*pi/5);z=zz+.09*sin(t*2*pi/5)
    o=lathe('Relieve floral idealizado',(0,0),[(-.03,.02),(0,.09),(.03,.02)],TRIM,12)
    o.rotation_euler.x=pi/2;o.location=(x,-4.23,z)
    a=k*pi/2;o.location=(x*cos(a)+4.23*sin(a),x*sin(a)-4.23*cos(a),z);o.rotation_euler.z=a
 # Steps and rails, approach centered on negative Y.
 for i in range(12):
  h=(2.05-.12)*(i+1)/12;y=-10.45+i*.285
  box('Escalon %02d'%(i+1),(0,y,.12+h/2),(2.45,.31,h),BASE)
 for x in [-1.32,1.32]:
  for i in range(6):
   y=-10.52+i*.61;z=.33+i*.345
   beam('Montante baranda',(x,y,z),(x,y,z+.92),.036,TRIM)
   if i<5:
    a=(x,y,z+.4);b=(x,y+.3,z+.8);c=(x,y+.61,z+.745);d=(x,y+.3,z+.34)
    for u,v in [(a,b),(b,c),(c,d),(d,a)]:beam('Rombo baranda',u,v,.026,TRIM)
  beam('Pasamanos',(x,-10.6,1.22),(x,-7.36,3.06),.055,TRIM)
 # Perimeter walls; front opening maintained.
 for i in range(len(TERRACE)):
  a=Vector((*TERRACE[i],0));b=Vector((*TERRACE[(i+1)%len(TERRACE)],0))
  if i==3:continue
  d=b-a;mid=(a+b)/2
  o=box('Pretil perimetral',(0,0,2.29),(d.length,.22,.48),BASE);o.rotation_euler.z=math.atan2(d.y,d.x);o.location.x=mid.x;o.location.y=mid.y
  o=box('Albarda perimetral',(0,0,2.56),(d.length,.30,.10),ROOF);o.rotation_euler.z=math.atan2(d.y,d.x);o.location.x=mid.x;o.location.y=mid.y
 # Circular annex front frame, door and circumferential masonry joints.
 cx,cy=-7.51,7.40
 box('Puerta anexo',(cx,cy-1.855,4.08),(1.22,.045,3.95),DARK)
 for x in [cx-.74,cx+.74]:box('Jamba anexo',(x,cy-1.9,4.12),(.22,.28,4.15),TRIM)
 o=arch('Dintel anexo',.89,6.18,.27,cy-1.87,.24,TRIM)
 for v in o.data.vertices:v.co.x+=cx
 for x in [-.45,-.15,.15,.45]:box('Reja anexo',(cx+x,cy-1.9,4.1),(.038,.04,3.82),IRON)
 for z in [2.8+i*.46 for i in range(8)]:lathe('Junta circular',(cx,cy),[(z,1.854),(z+.014,1.854)],JOINT)
 # Circular bands on dome.
 for z,r in [(7.58,1.84),(8.05,1.66),(8.56,1.35)]:lathe('Faja cupula',(cx,cy),[(z-.028,r),(z+.028,r)],ROOF)
def finish():
 global COL
 COL=STUDIO
 box('Suelo presentacion',(0,0,-.08),(200,200,.2),GROUND)
 SC.render.engine='CYCLES';SC.cycles.samples=40
 SC.render.resolution_x=1550;SC.render.resolution_y=1450;SC.render.resolution_percentage=100
 SC.world=bpy.data.worlds.new('PC ambiente');SC.world.use_nodes=True;SC.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.72,.8,1);SC.world.node_tree.nodes['Background'].inputs[1].default_value=.45
 data=bpy.data.lights.new('PC sol','AREA');data.energy=4200;data.shape='DISK';data.size=12;o=bpy.data.objects.new('PC sol',data);COL.objects.link(o);o.location=(-10,-15,26);o.rotation_euler=(Vector((0,0,5))-o.location).to_track_quat('-Z','Y').to_euler()
 data=bpy.data.cameras.new('PC Camara');o=bpy.data.objects.new('PC Camara',data);COL.objects.link(o);o.location=(27,-39,25);o.rotation_euler=(Vector((-1,0,7))-o.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=26;data.clip_end=1000;SC.camera=o
 SC.render.image_settings.file_format='PNG';SC.render.filepath=str(OUT/'panteon_perspectiva.png')
 for o in SC.objects:
  if o.name.startswith('REFERENCIA'):o.hide_render=True;o.hide_set(True)
 SC['metodo']='Reconstruccion interpretativa desde nube densa DJI y fotografias; escala SfM no calibrada; relieves idealizados.'
if __name__=='__main__':
 build_core();details();finish()
