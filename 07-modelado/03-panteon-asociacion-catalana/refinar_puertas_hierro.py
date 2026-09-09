
# Puertas de hierro: patron comun en acceso principal, opuesto y anexo.
COL=DETAIL
GATE=mat('hierro puertas unificado',(.20,.22,.205),False)
p=GATE.node_tree.nodes.get('Principled BSDF');p.inputs['Metallic'].default_value=.78;p.inputs['Roughness'].default_value=.55
# Remove only obsolete gate components in the three door openings.
def center_obj(o):
 return sum((o.matrix_world@Vector(v) for v in o.bound_box),Vector())/8
for o in list(DETAIL.objects):
 if o.type!='MESH':continue
 c=center_obj(o)
 main=abs(c.x)<.99 and 4.08<abs(c.y)<4.5 and 2<c.z<6.16
 annex=abs(c.x+7.51)<.65 and 5.43<c.y<5.62 and 2<c.z<6.12
 if (main and o.name.startswith(('Barrote','Travesano reja','Rombo herreria','Voluta ornamental'))) or (annex and o.name.startswith('Reja anexo')):
  bpy.data.objects.remove(o,do_unlink=True)
# Cut the stone bands back to the reveals; eliminate stone crossing metal door.
for sign in [-1,1]:
 cut=box('Temporal vano puerta',(0,sign*4.12,4.12),(1.90,1.30,4.04),DARK)
 for o in list(CORE.objects):
  if o.type!='MESH' or o.name.startswith(('Basamento triangular','Anexo','Cupula','Cornisa circular','Remate')):continue
  coords=[o.matrix_world@Vector(v) for v in o.bound_box]
  if min(v.x for v in coords)<.95 and max(v.x for v in coords)>-.95 and min(v.y for v in coords)<sign*4.12+.65 and max(v.y for v in coords)>sign*4.12-.65 and min(v.z for v in coords)<6.14 and max(v.z for v in coords)>2.10:
   mod=o.modifiers.new('Vano libre de piedra','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut
   bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.data.objects.remove(cut,do_unlink=True)
def door(label,cx,cy,bottom,width,height,back=False):
 # Local x horizontal, z vertical; all parts use the same iron material.
 direction=-1 if back else 1
 def P(x,z,depth=0):return (cx+direction*x,cy+direction*depth,bottom+z)
 def bar(name,a,b,r=.022):
  return tube(label+' '+name,[P(*a),P(*b)],r,GATE)
 def plate(name,x,z,w,h,depth=.045):
  return box(label+' '+name,P(x,z),(w,depth,h),GATE)
 # continuous outer frame and central meeting stile
 for x in [-width/2,0,width/2]:plate('montante',x,height/2,.040,height)
 for z in [.04,height*.30,height-.025]:plate('travesaño hierro',0,z,width,.055)
 for side in [-1,1]:
  x=side*width*.25;half=width*.25-.035
  plate('chapa inferior',x,height*.155,width*.5-.055,height*.285,.026)
  # raised panel borders and two recessed-looking fields in sheet metal
  for z0,z1 in [(.08,height*.15),(height*.17,height*.28)]:
   for xx in [x-half+.04,x+half-.04]:bar('moldura chapa',(xx,z0,-.026),(xx,z1,-.026),.012)
   for zz in [z0,z1]:bar('moldura chapa',(x-half+.04,zz,-.026),(x+half-.04,zz,-.026),.012)
  lo=height*.325;hi=height*.975
  # Large elongated X matching photograph; subordinate inner parallel diagonals.
  for a,b in [((x-half,lo,-.035),(x+half,hi,-.035)),((x+half,lo,-.035),(x-half,hi,-.035))]:
   bar('diagonal principal',a,b,.026)
  for a,b in [((x-half*.75,lo+.06,-.025),(x+half*.75,hi-.06,-.025)),((x+half*.75,lo+.06,-.025),(x-half*.75,hi-.06,-.025))]:
   bar('diagonal interior',a,b,.012)
  # Tight scrolls within triangular tips, mirrored above and below.
  for anchor,flip in [(hi-.075,-1),(lo+.075,1)]:
   for sg in [-1,1]:
    pts=[]
    for i in range(61):
     t=i/60;ang=sg*(pi*.45+t*pi*2.2);r=(1-.86*t)
     pts.append(P(x+sg*half*.39+half*.38*r*cos(ang),anchor+flip*(height*.075+height*.065*r*sin(ang)),-.045))
    tube(label+' voluta triangular',pts,.012,GATE)
   pts=[P(x+half*.38*sin(i*pi/32),anchor+flip*height*.13*i/32,-.045) for i in range(33)]
   tube(label+' nervio triangular',pts,.012,GATE)
  # Oval scroll pair halfway up.
  for sg in [-1,1]:
   pts=[P(x+sg*half*.55+half*.22*cos(i*2*pi/48),height*.63+height*.065*sin(i*2*pi/48),-.04) for i in range(49)]
   tube(label+' voluta central',pts,.012,GATE)
  # Hinge knuckles, rivets and curved handle.
  for z in [height*.18,height*.53,height*.90]:
   xx=side*(width/2-.022)
   beam(label+' bisagra',P(xx,z-.04,-.018),P(xx,z+.04,-.018),.027,GATE)
  for z in [.075,height*.29,height*.96]:
   for xx in [x-half+.025,x+half-.025]:
    beam(label+' remache',P(xx,z,-.024),P(xx,z,-.048),.015,GATE)
  pts=[P(side*.08+.035*sin(pi*i/24),height*.47+.15*cos(pi*i/24),-.085-.025*sin(pi*i/24)) for i in range(25)]
  tube(label+' tirador',pts,.018,GATE)
door('Puerta principal',0,-4.22,2.10,1.82,4.02)
door('Puerta opuesta',0,4.22,2.10,1.82,4.02,True)
door('Puerta anexo',-7.51,5.47,2.10,1.20,4.02)
print('Tres portales con patron comun y material de hierro; vanos liberados.')
