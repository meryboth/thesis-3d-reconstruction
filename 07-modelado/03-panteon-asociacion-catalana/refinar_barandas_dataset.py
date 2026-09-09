
# Revision basada en frame_00218, 00238 y 00195 del dataset DJI.
COL=DETAIL
for o in list(DETAIL.objects):
 if o.name.startswith(('Montante acceso','Diamante acceso','Arco acceso','Pasamanos central revisado','Retorno inferior pasamanos','Retorno superior pasamanos','Murete lateral inclinado','Apoyo lateral sencillo')):
  bpy.data.objects.remove(o,do_unlink=True)
# The sloping termination cuts the actual basement and its coping, not just an added cheek.
# z(y) at entry: 1.43 at -9.5, 2.57 at -8.05.
cut=yz_prism('Temporal rebaje frente',0,30,[(-12,-.536),(-8.05,2.57),(-8.05,5),(-12,5)],BASE)
base=CORE.objects.get('Basamento triangular truncado')
for o in [base]+[o for o in DETAIL.objects if o.name.startswith(('Pretil perimetral','Albarda perimetral'))]:
 mod=o.modifiers.new('Perfil descendente acceso','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cut,do_unlink=True)
GRANITE=mat('granito remates acceso',(.36,.38,.38),True)
# Continuation along each true oblique terrace edge, with a continuous inclined stone cap.
for sign,front,back in [(1,(2.4,-9.5),(8.1,3.3)),(-1,(-2.5,-9.5),(-9.6,7.6))]:
 a=Vector((*front,0));u=(Vector((*back,0))-a).normalized();n=Vector((-u.y,u.x,0))
 if n.dot(Vector((-1.8,1,0))-a)<0:n=-n
 def strip(name,s0,s1,z0,z1,thick,mat):
  pts=[a+u*s+n*t for s,t in [(s0,-.035),(s1,-.035),(s1,.29),(s0,.29)]]
  vs=[(p.x,p.y,z) for p,z in zip(pts,[z0-thick,z1-thick,z1-thick,z0-thick])]+[(p.x,p.y,z) for p,z in zip(pts,[z0,z1,z1,z0])]
  return mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
 end=1.45/u.y
 # Side wedge rebuild fills the entry corner removed by the wider stair opening.
 pts=[a+n*t+u*s for s,t in [(0,-.025),(end,-.025),(end,.26),(0,.26)]]
 vs=[(p.x,p.y,.12) for p in pts]+[(p.x,p.y,z) for p,z in zip(pts,[1.43,2.57,2.57,1.43])]
 mesh('Muro continuo descendente',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],BASE)
 strip('Albardilla inclinada continua',0,end,1.46,2.60,.115,GRANITE)
 # Terminal dressed vertical slab and foot block.
 center=a+n*.125
 o=box('Testero granito acceso',(0,0,.81),(.33,.14,1.38),GRANITE);o.location.x=center.x;o.location.y=center.y;o.rotation_euler.z=math.atan2(n.y,n.x)
 o=box('Zocalo testero',(0,0,.17),(.39,.22,.22),GRANITE);o.location.x=center.x;o.location.y=center.y;o.rotation_euler.z=math.atan2(n.y,n.x)
 # Simple lateral rail is parallel to the stone slope, supported at both ends.
 p0=a+u*.03+n*.36+Vector((0,0,1.55));p1=a+u*end+n*.36+Vector((0,0,2.68))
 beam('Pasamanos lateral fijado',p0,p1,.034,TRIM)
 for p in [p0,p1]:beam('Anclaje pasamanos lateral',p,p-n*.22,.025,TRIM)
# Continuous ornamental rail in a local sloping frame.
U=Vector((0,1,.565)).normalized();V=Vector((0,-U.z,U.y))
length=4.03;height=.72
for sign in [-1,1]:
 origin=Vector((sign*1.32,-10.48,.50))
 def Q(s,h):return tuple(origin+U*s+V*h)
 def path(name,points,r=.022,mat=TRIM):
  return tube('Baranda precisa '+name,[Q(s,h) for s,h in points],r,mat)
 # straight top rail with returns tangent to the rail and connected to end diamonds
 path('pasamanos',[(0,height),(length,height)],.043)
 for end,direction in [(0,-1),(length,1)]:
  path('retorno continuo',[(end+direction*height*.5*sin(pi*i/48),height*.5+height*.5*cos(pi*i/48)) for i in range(49)],.043)
 # Diamond elements: top at handrail, lower tip connected to arched ribbon.
 for i in range(6):
  s=length*i/5;half=.145
  diamond=[(s,.04),(s+half,.37),(s,.69),(s-half,.37),(s,.04)]
  path('rombo exterior',diamond,.022)
  path('rombo interior',[(s,.11),(s+.095,.37),(s,.61),(s-.095,.37),(s,.11)],.012)
  # striped inset observed in the photographs, kept geometric and muted.
  for dx in [-.05,0,.05]:
   lo=.13+abs(dx)*1.8;hi=.59-abs(dx)*1.8
   path('liston interior',[(s+dx,lo),(s+dx,hi)],.014,TRIM)
  # split feet and small sockets instead of a continuous vertical bar
  for dx in [-.06,.06]:
   path('pata abierta',[(s,.10),(s+dx,-.14)],.026)
   p=Vector(Q(s+dx,-.14));box('Baranda precisa placa anclaje',p,(.11,.10,.035),TRIM)
  for h in [.04,.69]:
   p=Q(s,h);box('Baranda precisa collar',p,(.09,.07,.06),TRIM)
  if i<5:
   start=s;step=length/5
   path('arco entre rombos',[(start+step*t/48,.04+.275*sin(pi*t/48)) for t in range(49)],.025)
print('Barandas reconstruidas desde fotos; muro descendente y albardilla continuos.')

# Seat the terminal anchors on the stone cheeks, without floating feet.
for o in DETAIL.objects:
 if o.type=='MESH' and o.name.startswith('Baranda precisa'):
  for v in o.data.vertices:
   p=o.matrix_world@v.co;origin=Vector((p.x,-10.48,.50));d=p-origin;s=d.dot(U)
   p+=U*s*(3.70/4.03-1);p.z-=.05;v.co=o.matrix_world.inverted()@p
 if o.type=='MESH' and o.name.startswith('Union descansillo'):
  for v in o.data.vertices:v.co.z-=.003
