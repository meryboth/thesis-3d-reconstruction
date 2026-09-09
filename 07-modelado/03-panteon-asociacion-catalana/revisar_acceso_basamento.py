
# Revision del acceso y respiraderos guiada por las dos fotografias adjuntas.
COL=DETAIL
for o in list(DETAIL.objects):
 if o.name.startswith(('Escalon','Montante baranda','Rombo baranda','Pasamanos','Bucle curvo baranda')):
  bpy.data.objects.remove(o,do_unlink=True)
old=CORE.objects.get('Basamento triangular truncado')
if old:bpy.data.objects.remove(old,do_unlink=True)
COL=CORE
base=prism('Basamento triangular truncado',TERRACE,.12,2.05,BASE)
COL=DETAIL
def cut_base(cut):
 mod=base.modifiers.new('Abertura real','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
 bpy.context.view_layer.objects.active=base;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
# Hollow basement: floor and terrace slab remain; actual openings pass through wall.
cen=Vector((-1.8,1.0))
inner=[tuple(cen+(Vector(p)-cen)*.90) for p in TERRACE]
cut_base(prism('Interior tecnico sin reconstruir',inner,.35,1.75,BASE))
cut_base(box('Corte acceso triple',(0,-9.2,1.3),(5.12,4.2,3.4),BASE))
for side,x,width,count,start,run in [('central',0,2.44,12,-10.65,3.42),('lateral izquierdo',-1.94,1.08,7,-9.42,2.19),('lateral derecho',1.94,1.08,7,-9.42,2.19)]:
 for i in range(count):
  top=.12+1.93*(i+1)/count;depth=run/count;y=start+depth*(i+.5)
  box('Escalon '+side+' %02d'%(i+1),(x,y,(.12+top)/2),(width,depth+.006,top-.12),BASE)
  box('Nariz peldaño '+side,(x,y-depth/2-.012,top-.025),(width+.018,.065,.05),TRIM)
# Thin sloping stone cheeks separate the stair flights.
def yz_prism(name,x,width,poly,mat):
 n=len(poly);v=[(xx,y,z) for xx in [x-width/2,x+width/2] for y,z in poly]
 return mesh(name,v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat)
for sign in [-1,1]:
 yz_prism('Zanca central piedra',sign*1.32,.17,[(-10.73,.12),(-7.12,.12),(-7.12,2.23),(-10.73,.32)],BASE)
 yz_prism('Murete lateral inclinado',sign*2.58,.26,[(-9.52,.12),(-7.1,.12),(-7.1,2.59),(-8.87,2.59),(-9.52,1.43)],BASE)
 beam('Apoyo lateral sencillo',(sign*2.45,-9.35,.45),(sign*2.45,-8.25,2.61),.034,TRIM)
 # Handrail straight with returned curved ends, oval arches and diamond motifs.
 x=sign*1.32
 for i in range(6):
  y=-10.44+i*.61;z=.48+i*.345
  beam('Montante acceso',(x,y,z),(x,y,z+.75),.032,TRIM)
  if i<5:
   pts=[(x,y,z+.42),(x,y+.305,z+.86),(x,y+.61,z+.765),(x,y+.305,z+.32),(x,y,z+.42)]
   tube('Diamante acceso',pts,.026,TRIM)
   tube('Arco acceso',[(x,y+.305+.305*cos(pi*j/32),z+.42+.1725*cos(pi*j/32)+.25*sin(pi*j/32)) for j in range(33)],.032,TRIM)
 beam('Pasamanos central revisado',(x,-10.55,1.20),(x,-7.08,3.16),.045,TRIM)
 tube('Retorno inferior pasamanos',[(x,-10.55-.24*sin(pi*j/32),.93+.27*cos(pi*j/32)) for j in range(33)],.045,TRIM)
 tube('Retorno superior pasamanos',[(x,-7.08+.23*sin(pi*j/32),2.9+.26*cos(pi*j/32)) for j in range(33)],.045,TRIM)
# Rectangular ventilators: stone surround, concentric circles, crossbars and rosettes.
for edge in [1,2,4]:
 a=Vector((*TERRACE[edge],0));b=Vector((*TERRACE[(edge+1)%len(TERRACE)],0));u=(b-a).normalized()
 mid=(a+b)/2;n=Vector((-u.y,u.x,0))
 if n.dot(Vector((-1.8,1,0))-mid)>0:n=-n
 for j in range(5):
  center=a+(b-a)*(.16+j*.17);center.z=.87
  c=box('Corte respiradero',(0,0,0),(1.12,1.7,.68),BASE);c.location=center;c.rotation_euler.z=math.atan2(u.y,u.x);cut_base(c)
  def vp(x,z,off=.025):return tuple(center+u*x+n*off+Vector((0,0,z)))
  for z in [-.39,.39]:
   o=box('Dintel respiradero',(0,0,0),(1.30,.16,.10),TRIM);o.location=center+n*.025+Vector((0,0,z));o.rotation_euler.z=math.atan2(u.y,u.x)
  for x0 in [-.60,.60]:
   o=box('Jamba respiradero',(0,0,0),(.10,.16,.70),TRIM);o.location=center+u*x0+n*.025;o.rotation_euler.z=math.atan2(u.y,u.x)
  for rad in [.115,.22,.31]:
   tube('Circulo reja basamento',[vp(rad*cos(i*2*pi/48),rad*sin(i*2*pi/48),.07) for i in range(49)],.015,TRIM)
  for xx in [-.45,0,.45]:beam('Vertical reja basamento',vp(xx,-.32,.07),vp(xx,.32,.07),.014,TRIM)
  beam('Horizontal reja basamento',vp(-.55,0,.07),vp(.55,0,.07),.014,TRIM)
  for xx in [-.45,.45]:
   tube('Roseta reja basamento',[vp(xx+.045*cos(i*2*pi/16),.07*sin(i*2*pi/16),.075) for i in range(17)],.018,TRIM)
# Stone joint network used only as material relief, not inferred structural blocks.
m=BASE;nodes=m.node_tree.nodes;links=m.node_tree.links;p=nodes.get('Principled BSDF')
g=nodes.new('ShaderNodeNewGeometry');v=nodes.new('ShaderNodeTexVoronoi');v.feature='DISTANCE_TO_EDGE';v.inputs['Scale'].default_value=4.2;links.new(g.outputs['Position'],v.inputs['Vector'])
r=nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.015;r.color_ramp.elements[0].color=(.12,.14,.135,1);r.color_ramp.elements[1].position=.065;r.color_ramp.elements[1].color=(.34,.37,.35,1);links.new(v.outputs['Distance'],r.inputs[0]);links.new(r.outputs[0],p.inputs['Base Color'])
bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.32;bump.inputs['Distance'].default_value=.035;links.new(v.outputs['Distance'],bump.inputs['Height']);links.new(bump.outputs[0],p.inputs['Normal'])
print('Revision acceso: 12 peldaños centrales, 7 por lateral, 15 respiraderos con calado real.')

box('Union descansillo acceso',(0,-7.13,1.97),(5.12,.22,.16),BASE)

# Distinguish dressed stair stone and paving from irregular wall cladding.
paving=BASE.copy();paving.name='PC Piedra lisa acceso'
p=paving.node_tree.nodes.get('Principled BSDF')
for link in list(p.inputs['Base Color'].links):paving.node_tree.links.remove(link)
for link in list(p.inputs['Normal'].links):paving.node_tree.links.remove(link)
p.inputs['Base Color'].default_value=(.38,.40,.38,1)
for o in DETAIL.objects:
 if o.type=='MESH' and o.name.startswith(('Escalon','Union descansillo','Zanca central')):
  o.data.materials.clear();o.data.materials.append(paving)
base.data.materials.append(paving)
for f in base.data.polygons:
 if f.normal.z>.9:f.material_index=len(base.data.materials)-1
for node in BASE.node_tree.nodes:
 if node.type=='VALTORGB' and abs(node.color_ramp.elements[0].position-.015)<.001:
  node.color_ramp.elements[0].color=(.24,.27,.255,1)
  node.color_ramp.elements[1].color=(.34,.37,.35,1)
