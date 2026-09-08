"""Modelo interpretativo del Templete Central. Ejecutar con Python de Blender.
Lee parametros ajustados a la nube; detalles marcados como interpretacion visual.
"""
import bpy,math,json,numpy as np
from pathlib import Path
from mathutils import Vector,Matrix
OUT=Path(r'C:\nerfstudio_work\thesis\07-modelado\02-templete-central')
D=json.loads((OUT/'parametros_ajuste.json').read_text(encoding='utf-8'))
SC=None;CORE=None;DETAIL=None;REF=None;PRES=None
FACES=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
def mat(name,color,rough=.85,texture=False):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough
 if texture:
  n=m.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=7;n.inputs['Detail'].default_value=3
  ramp=m.node_tree.nodes.new('ShaderNodeValToRGB')
  ramp.color_ramp.elements[0].position=.22;ramp.color_ramp.elements[0].color=(*(x*.58 for x in color),1)
  ramp.color_ramp.elements[1].position=.78;ramp.color_ramp.elements[1].color=(*color,1)
  m.node_tree.links.new(n.outputs['Fac'],ramp.inputs[0]);m.node_tree.links.new(ramp.outputs[0],p.inputs['Base Color'])
  fine=m.node_tree.nodes.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=110
  geo=m.node_tree.nodes.new('ShaderNodeNewGeometry');m.node_tree.links.new(geo.outputs['Position'],n.inputs['Vector']);m.node_tree.links.new(geo.outputs['Position'],fine.inputs['Vector'])
  bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.008
  m.node_tree.links.new(fine.outputs['Fac'],bump.inputs['Height']);m.node_tree.links.new(bump.outputs[0],p.inputs['Normal'])
 return m
def mesh(name,verts,faces,col,material):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);col.objects.link(ob)
 if material:me.materials.append(material)
 return ob
def box(name,center,size,col,material):
 x,y,z=center;hx,hy,hz=np.array(size)/2
 vs=[(x+sx*hx,y+sy*hy,z+sz*hz) for sz in [-1,1] for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
 return mesh(name,vs,FACES,col,material)
def rect(z,inset=0):
 vals={}
 for f in D['facades']:
  a,b=f['coef'];vals[(f['axis'],f['sign'])]=f['sign']*(a*z+b-inset)
 return [(vals[(0,-1)],vals[(1,-1)],z),(vals[(0,1)],vals[(1,-1)],z),(vals[(0,1)],vals[(1,1)],z),(vals[(0,-1)],vals[(1,1)],z)]
def build_core():
 global SC,CORE,DETAIL,REF,PRES,CON,METAL,TOP,STONE
 SC=bpy.context.scene
 SC.name='Templete Central | modelo documentado'
 CORE=bpy.data.collections.new('01 Geometria ajustada a nube')
 DETAIL=bpy.data.collections.new('02 Detalles interpretados de fotografias')
 REF=bpy.data.collections.new('03 Referencia densa alineada')
 PRES=bpy.data.collections.new('04 Presentacion')
 for c in [CORE,DETAIL,REF,PRES]:SC.collection.children.link(c)
 ob=bpy.data.objects.get('REFERENCIA Templete nube densa')
 if ob:
  for c in list(ob.users_collection):c.objects.unlink(ob)
  REF.objects.link(ob)
 else:
  bpy.ops.wm.ply_import(filepath=str(OUT/'referencia_densa_muestreada.ply'))
  ob=bpy.context.object;ob.name='REFERENCIA Templete nube densa'
  for c in list(ob.users_collection):c.objects.unlink(ob)
  REF.objects.link(ob)
  ob.rotation_euler.z=-D['transform']['angle'];ob.location=(*(-np.array(D['transform']['center_uv'])),0)
 ob.hide_render=True;ob.select_set(False)
 REF.hide_viewport=True;REF.hide_render=True
 CON=mat('Hormigon visto envejecido',(.48,.47,.40),texture=True)
 METAL=mat('Acero de barandas',(.085,.09,.075),.65)
 TOP=mat('Impermeabilizacion gris clara',(.46,.49,.49),texture=True)
 STONE=mat('Pavimento y escalones',(.32,.31,.29),texture=True)
 z0,z1=D['slab_bottom'],D['slab_top'];bottom=rect(z0)
 hx=(bottom[1][0]-bottom[0][0])/2;hy=(bottom[2][1]-bottom[1][1])/2
 cx=(bottom[1][0]+bottom[0][0])/2;cy=(bottom[2][1]+bottom[1][1])/2
 ob=box('Losa | cotas ajustadas',(cx,cy,(z0+z1)/2),(hx*2,hy*2,z1-z0),CORE,CON);ob['evidencia']='Medianas de planos horizontales de la nube'
 low=rect(z0);up=rect(D['rim_top']);inside_up=rect(D['rim_top'],.17);inside_low=rect(z1,.16)
 # Four closed wedges, each spanning one complete inclined facade.
 for i in range(4):
  j=(i+1)%4
  vs=[low[i],low[j],inside_low[j],inside_low[i],up[i],up[j],inside_up[j],inside_up[i]]
  ob=mesh('Frente inclinado '+str(i+1),vs,FACES,CORE,CON)
  ob['evidencia']='Pendiente de plano ajustada robustamente a la nube'
 for i,c in enumerate(D['columns']):
  ob=box('Columna '+str(i+1),(*c['center'],(.30+z0)/2),(*c['size'],z0-.30),CORE,CON)
  ob['evidencia']='Envolvente robusta de puntos entre z=1.75 y 2.3'
 # A thin roof finish and cross ribs visible in high drone views.
 box('Paño superior de cubierta',(cx,cy,z1+.012),(2*hx-.35,2*hy-.35,.025),CORE,TOP)
 box('Nervio superior longitudinal',(0,cy,z1+.055),(.08,2*hy-.38,.11),DETAIL,CON)
 box('Nervio superior transversal',(cx,0,z1+.055),(2*hx-.38,.08,.11),DETAIL,CON)
 for a in bpy.context.screen.areas:
  if a.type=='VIEW_3D':
   s=a.spaces.active;s.region_3d.view_location=Vector((0,0,2))
   s.region_3d.view_rotation=Vector((20,-25,15)).to_track_quat('Z','Y')
   s.region_3d.view_distance=25;s.shading.type='MATERIAL'
   s.overlay.show_floor=False;s.overlay.show_axis_x=False;s.overlay.show_axis_y=False;s.overlay.show_extras=False
 print('Estructura principal creada')

def add_details():
 # Engraved linear relief, regularized from photos, not an exact ornamental survey.
 for i,ob in enumerate([bpy.data.objects['Frente inclinado '+str(j+1)] for j in range(4)]):
  if i==0:axis,sign=1,-1
  elif i==1:axis,sign=0,1
  elif i==2:axis,sign=1,1
  else:axis,sign=0,-1
  f=next(f for f in D['facades'] if f['axis']==axis and f['sign']==sign);m,b=f['coef']
  tangent=Vector((1,0,0) if axis==1 else (0,1,0))
  vertical=Vector((sign*m,0,1) if axis==0 else (0,sign*m,1)).normalized()
  normal=Vector((sign,0,-m) if axis==0 else (0,sign,-m)).normalized()
  width=10.6 if axis==1 else 14.4
  n=4 if axis==1 else 5
  cv=[];cf=[]
  def cutter(u,z,w,h):
   center=Vector((0,0,z));center[axis]=sign*(m*z+b)
   center[1-axis]=u
   # One shallow recess with real geometry.
   center+=normal*.012
   idx=len(cv)
   for d in [-.047,.047]:
    for a,c in [(-1,-1),(1,-1),(1,1),(-1,1)]:
     cv.append(tuple(center+tangent*(a*w/2)+vertical*(c*h/2)+normal*d))
   cf.extend(tuple(idx+v for v in face) for face in FACES)
  pitch=width/n
  for j in range(n):
   mid=-width/2+(j+.5)*pitch
   for row in range(3):
    cutter(mid-.30+(.12 if row==1 else 0),2.88+row*.38,pitch*.53,.055)
   for v in range(3):
    cutter(mid+pitch*.29+v*.14,3.34,.048,.92)
  cuts=mesh('Cortadores temporales',cv,cf,DETAIL,None)
  import bmesh
  bm=bmesh.new();bm.from_mesh(cuts.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cuts.data);bm.free()
  mod=ob.modifiers.new('Bajorrelieves interpretados','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cuts
  bpy.context.view_layer.objects.active=ob
  bpy.ops.object.modifier_apply(modifier=mod.name)
  bpy.data.objects.remove(cuts,do_unlink=True)
  ob['relieve']='Patron simplificado a partir de fotografias; no reproduccion exacta'
 # Access arrangement: perimeter walkways and two interpreted descending flights.
 # Below-ground geometry is deliberately separate from measured core.
 g=.3
 box('Pasarela central',(0,0,g-.09),(13.3,1.8,.18),DETAIL,STONE)
 for x in [-5.45,5.45]:box('Circulacion lateral',(x,0,g-.09),(2.35,14.5,.18),DETAIL,STONE)
 for y in [-6.45,6.45]:box('Descanso de acceso',(0,y,g-.09),(8.55,1.6,.18),DETAIL,STONE)
 for x in [-6.55,6.55]:box('Murete lateral',(x,0,.65),(.16,14.4,.7),DETAIL,CON)
 for side in [-1,1]:
  # Steps rise towards each outer landing; descent is an interpretation of photos.
  for j in range(18):
   y=side*(5.48-(j+.5)*.25);zt=g-j*.115
   o=box('Escalera interpretada | peldaño',(0,y,zt-.09),(7.0,.25,.18),DETAIL,STONE)
   o['alcance']='Profundidad y numero de escalones interpretados; no medidos por nube'
  for x in [-3.7,3.7]:box('Contencion escalera',(x,side*3.25,-.35),(.18,4.6,1.3),DETAIL,CON)
 def bar(name,p1,p2,r=.018):
  a,b=Vector(p1),Vector(p2);v=b-a
  # Use a small closed square section, editable mesh.
  ob=box(name,(0,0,0),(2*r,2*r,v.length),DETAIL,METAL)
  ob.location=(a+b)/2;ob.rotation_euler=v.to_track_quat('Z','Y').to_euler()
  return ob
 for x in [-3.85,3.85]:
  for side in [-1,1]:
   y0,y1=side*1.,side*5.55
   bar('Pasamanos de borde',(x,y0,1.12),(x,y1,1.12),.025)
   bar('Travesaño inferior',(x,y0,.43),(x,y1,.43),.014)
   for y in np.linspace(y0,y1,24):bar('Barrote',(x,y,.32),(x,y,1.12),.011)
 for side in [-1,1]:
  # Central stair handrail, depth is approximate.
  p1=(0,side*5.48,1.15);p2=(0,side*1.10,-.79)
  bar('Pasamanos de escalera',p1,p2,.025)
  for t in np.linspace(0,1,12):
   p=np.array(p1)*(1-t)+np.array(p2)*t
   bar('Montante escalera',(p[0],p[1],p[2]-.8),tuple(p),.012)
 box('Fondo de acceso | interpretativo',(0,0,-1.94),(7.5,11.4,.16),DETAIL,CON)
 for x in [-3.72,3.72]:box('Muro bajo rasante | interpretativo',(x,0,-.78),(.16,11.4,2.15),DETAIL,CON)
 for y in [-5.65,5.65]:box('Testero bajo rasante | interpretativo',(0,y,-.78),(7.5,.16,2.15),DETAIL,CON)
 print('Detalles y accesos creados')

def finish():
 SC.unit_settings.system='NONE';SC['escala']=D['units']
 # Framing floor has an opening so it does not conceal the stair flights.
 grass=mat('Entorno neutro',(.12,.18,.13))
 for x in [-24,24]:box('Suelo de presentacion',(x,0,.17),(34,70,.20),PRES,grass)
 for y in [-24,24]:box('Suelo de presentacion',(0,y,.17),(14,33,.20),PRES,grass)
 for ob in PRES.objects:
  if ob.name.startswith('Suelo de presentacion'):
   for v in ob.data.vertices:
    for ax in [0,1]:
     if abs(v.co[ax])>15:v.co[ax]=500 if v.co[ax]>0 else -500
 world=bpy.data.worlds.new('Luz ambiente Templete');world.use_nodes=True
 world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.72,.82,1)
 world.node_tree.nodes['Background'].inputs[1].default_value=.45;SC.world=world
 sun=bpy.data.lights.new('Sol','SUN');sun.energy=2.3;sun.angle=.18
 so=bpy.data.objects.new('Sol',sun);PRES.objects.link(so);so.rotation_euler=(.45,-.5,-.6)
 ld=bpy.data.lights.new('Relleno de acceso','AREA');ld.energy=1200;ld.shape='DISK';ld.size=10
 lo=bpy.data.objects.new('Relleno de acceso',ld);PRES.objects.link(lo);lo.location=(8,-13,7)
 lo.rotation_euler=(Vector((0,0,1.5))-lo.location).to_track_quat('-Z','Y').to_euler()
 cd=bpy.data.cameras.new('Camara general');cam=bpy.data.objects.new('Camara general',cd);PRES.objects.link(cam)
 cam.location=(22,-28,9);target=Vector((0,0,1.5));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
 cd.type='ORTHO';cd.ortho_scale=24;SC.camera=cam
 SC.render.engine='CYCLES';SC.cycles.samples=32;SC.cycles.use_denoising=True
 SC.render.resolution_x=1500;SC.render.resolution_y=1100;SC.render.resolution_percentage=100
 SC.render.image_settings.file_format='PNG';SC.render.filepath=str(OUT/'templete_perspectiva.png')
 SC.view_settings.view_transform='AgX'
 for area in bpy.context.screen.areas:
  if area.type=='VIEW_3D':
   s=area.spaces.active;s.region_3d.view_rotation=cam.rotation_euler.to_quaternion()
   s.region_3d.view_location=target;s.region_3d.view_distance=25
 note=bpy.data.texts.new('LEEME Templete | procedencia')
 note.write('Estructura principal ajustada a nube densa RealityScan.\n'
 'Escala metrica no verificada. Seis columnas y cuatro frentes inclinados.\n'
 'Relieves regularizados y accesos interpretados de fotos. Escaleras bajo suelo no medidas.\n'
 'Nube alineada en coleccion 03. Datos originales conservados.\n')
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'templete_central_reconstruido.blend'))
 print('Modelo guardado')
if __name__=='__main__':
 build_core();add_details();finish()

