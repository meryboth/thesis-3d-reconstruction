
# Stair well cut into triangular terrace so every tread remains exposed.
COL=DETAIL
cut=box('Temporal hueco escalera',(0,-9.08,1.2),(2.68,3.95,3.2),BASE)
base=CORE.objects.get('Basamento triangular truncado');mod=base.modifiers.new('Acceso escalinata','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut
bpy.context.view_layer.objects.active=base;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
# Tiny object-specific expansion prevents coincident modular faces in rendering.
for idx,o in enumerate(CORE.objects):
 if o.type=='MESH' and o.name!='Basamento triangular truncado':
  center=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
  factor=1+0.00001*(1+idx%17)
  for v in o.data.vertices:v.co=center+(v.co-center)*factor
# Window facades: lower stone panel and round ironwork, matching side photograph.
for k in [1,3]:
 rotate(box('Antepecho ventana',(0,-4.16,2.89),(1.86,.12,1.60),TRIM),k)
 for rad in [.40,.62]:tube('Aro reja ventana',[(rad*cos(i*2*pi/64),-4.225,4.93+rad*sin(i*2*pi/64)) for i in range(65)],.025,IRON,k)
 for x in [-.60,.60]:scroll(x,4.53,.17,.18,k,y=-4.23,r=.017)
# Rounded loops on stair handrail; photograph shows loops above diamond bars.
for x in [-1.32,1.32]:
 for i in range(5):
  y=-10.5+i*.61;z=.65+i*.345
  tube('Bucle curvo baranda',[(x,y+.305+.305*cos(pi*j/32),z+.17*cos(pi*j/32)+.34*sin(pi*j/32)) for j in range(33)],.035,TRIM)
