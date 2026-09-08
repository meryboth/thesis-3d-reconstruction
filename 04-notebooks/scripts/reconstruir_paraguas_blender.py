"""Reconstruccion de los dos paraguas a partir de parametros ajustados a COLMAP.
Ejecutar en Blender: exec(compile(open(__file__,encoding='utf-8').read(),__file__,'exec'))
Las unidades son SfM, sin calibracion metrica. No modifica los archivos fuente.
"""
import bpy, numpy as np, math, json
from pathlib import Path
from mathutils import Vector
OUT=Path(r'C:\nerfstudio_work\thesis\01-paraguas-vicentelopez\04-modelo-geometrico')
data=json.loads((OUT/'parametros_ajuste.json').read_text(encoding='utf-8'))
scene=bpy.data.scenes.new('El Paraguas | reconstruccion geometrica')
bpy.context.window.scene=scene
scene.unit_settings.system='NONE'
scene['escala']='Unidades SfM. No calibrado en metros.'
scene['fuente']=data['source']
model=bpy.data.collections.new('01 Arquitectura reconstruida')
refs=bpy.data.collections.new('02 Referencias COLMAP (ocultas)')
studio=bpy.data.collections.new('03 Presentacion')
for col in [model,refs,studio]: scene.collection.children.link(col)
for name in ['REFERENCIA_COLMAP_densa_original','REFERENCIA_malla_Poisson']:
    ob=bpy.data.objects.get(name)
    if ob:
        refs.objects.link(ob)
        ob.hide_render=True
        ob.hide_set(True)
refs.hide_render=True
refs.hide_viewport=True

def material(name,color,rough=.8):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough
    return m
concrete=material('Hormigon claro | interpretacion fotografica',(.66,.64,.56))
topmat=material('Cara superior oscura | interpretacion fotografica',(.14,.155,.14))
ground=material('Suelo de presentacion',(.19,.23,.20))
def mesh_obj(name,verts,faces,col):
    m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update()
    ob=bpy.data.objects.new(name,m);col.objects.link(ob);return ob
def height(u,v,coef):
    r=math.hypot(u,v)
    b=[1,math.sqrt(r),r,r*r,r**3,u,v,u*u-v*v,u*v,u*u*v*v]
    return float(np.dot(b,coef))
N=192;NR=64
for k,f in enumerate(data['fits']):
    a=f['angle'];ca,sa=math.cos(a),math.sin(a)
    cx,cy=f['center'];hu,hv=f['halfsize'];rad=f['radius']
    verts=[];faces=[];mi=[]
    # Annular underside and top. Angular samples align with rectangle corners.
    theta=[2*math.pi*j/N for j in range(N)]
    def world(u,v,z):return (cx+ca*u-sa*v,cy+sa*u+ca*v,z)
    for layer in range(2):
        for i in range(NR+1):
            t=i/NR
            for th in theta:
                ct,st=math.cos(th),math.sin(th)
                boundary=min(hu/max(abs(ct),1e-9),hv/max(abs(st),1e-9))
                r=rad+(boundary-rad)*t
                u,v=r*ct,r*st
                low=height(u,v,f['lower_coef'])
                up=height(u,v,f['upper_coef'])
                # Undersampled central top is a smooth cap constrained at r=.22.
                if r<.22:
                    edge=height(.22*ct,.22*st,f['upper_coef'])
                    cap=2.82 if k==0 else 2.79
                    s=(r/.22)**2
                    up=cap+(edge-cap)*s
                up=max(low+.015,min(up,low+.16))
                verts.append(world(u,v,low if layer==0 else up))
    stride=(NR+1)*N
    for layer in range(2):
        off=layer*stride
        for i in range(NR):
            for j in range(N):
                jn=(j+1)%N
                face=(off+i*N+j,off+i*N+jn,off+(i+1)*N+jn,off+(i+1)*N+j)
                faces.append(face if layer==0 else tuple(reversed(face)));mi.append(layer)
    for j in range(N):
        jn=(j+1)%N
        faces.append((NR*N+j,NR*N+jn,stride+NR*N+jn,stride+NR*N+j));mi.append(0)
    # Cap the central disks; lower cap is concealed by the fitted shaft.
    for layer in range(2):
        off=layer*stride
        z=sum(verts[off+j][2] for j in range(N))/N
        idx=len(verts);verts.append((cx,cy,z))
        for j in range(N):
            face=(idx,off+j,off+(j+1)%N)
            faces.append(tuple(reversed(face)) if layer==0 else face);mi.append(layer)
    shell=mesh_obj(f'Paraguas {k+1} | cubierta de doble cara',verts,faces,model)
    shell.data.materials.append(concrete);shell.data.materials.append(topmat)
    for p,idx in zip(shell.data.polygons,mi):p.material_index=idx;p.use_smooth=True
    shell['origen']='Superficies suaves ajustadas por celdas a nube COLMAP'
    shell['zona_interpolada']='Cara superior central: r < 0.22 SfM'
    shell['parametros']=json.dumps(f)
    shell['ancho_SfM']=2*hu;shell['largo_SfM']=2*hv
    # Shaft fitted from nine horizontal circle sections.
    axis=np.array(f['axis'])
    ztop=sum(verts[j][2] for j in range(N))/N+.008
    zv=[.025,ztop];vv=[]
    for z in zv:
        c=np.array([1,z])@axis
        for th in theta:vv.append((c[0]+rad*math.cos(th),c[1]+rad*math.sin(th),z))
    ff=[(j,(j+1)%N,N+(j+1)%N,N+j) for j in range(N)]
    ff+=[tuple(reversed(range(N))),tuple(range(N,2*N))]
    shaft=mesh_obj(f'Paraguas {k+1} | columna ajustada',vv,ff,model)
    shaft.data.materials.append(concrete)
    for p in shaft.data.polygons:p.use_smooth=(len(p.vertices)==4)
    shaft['radio_SfM']=rad
    shaft['origen']='Circulos ajustados a secciones entre z=0.5 y 2.4 SfM'

# A presentation plane, not a reconstructed architectural element.
plane=mesh_obj('Plano de presentacion | no relevado',[(-200,-200,.025),(200,-200,.025),(200,200,.025),(-200,200,.025)],[(0,1,2,3)],studio)
plane.data.materials.append(ground)
plane['nota']='Soporte visual plano; no es terreno reconstruido'
world=bpy.data.worlds.new('Estudio neutro');world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.55,.64,.76,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.3
scene.world=world
def light(name,loc,energy,size):
    d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size
    o=bpy.data.objects.new(name,d);studio.objects.link(o);o.location=loc
    o.rotation_euler=(Vector((.3,-1,1.5))-o.location).to_track_quat('-Z','Y').to_euler()
light('Luz principal',(-3,-5,8),270,5)
light('Luz de relleno',(5,-1,6),162,4)
light('Luz posterior',(0,4,7),324,3)
camdata=bpy.data.cameras.new('Camara arquitectura')
cam=bpy.data.objects.new('Camara arquitectura',camdata);studio.objects.link(cam)
cam.location=(6,-11,4.4)
target=Vector((.35,-1.1,1.65))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
camdata.type='ORTHO';camdata.ortho_scale=7.6
scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=48
scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX'
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        sp=area.spaces.active;sp.clip_end=1000
        sp.region_3d.view_rotation=cam.rotation_euler.to_quaternion()
        sp.region_3d.view_location=target;sp.region_3d.view_distance=8
        sp.shading.type='MATERIAL'
        sp.overlay.show_floor=False
        sp.overlay.show_axis_x=False;sp.overlay.show_axis_y=False
# Save a readable in-file note and the reproducible code.
note=bpy.data.texts.new('LEEME | alcance y referencias')
note.write('Modelo geometrico interpretativo de los dos paraguas.\n'
'Escala SfM sin calibrar. Referencias alineadas en coleccion 02, inicialmente oculta.\n'
'Cubiertas: ajuste a cuantiles por celdas; centro superior interpolado.\n'
'Columnas: circulos ajustados en nueve secciones. Materiales aproximados por fotografias.\n'
'No representa documentacion ejecutiva ni valida espesores estructurales.\n')
scene.render.filepath=str(OUT/'paraguas_perspectiva.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'el_paraguas_reconstruido.blend'))
print('MODELO GUARDADO',len(model.objects),'objetos arquitectonicos')

