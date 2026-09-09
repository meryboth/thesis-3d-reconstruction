import bpy, numpy as np
from pathlib import Path
from mathutils import Vector
OUT=Path(__file__).resolve().parent
scene=bpy.data.scenes.new('Panteon Catalan | reconstruccion')
bpy.context.window.scene=scene
q=np.load(OUT/'nube_alineada.npy')
me=bpy.data.meshes.new('Nube densa alineada');me.from_pydata(q[:,:3].tolist(),[],[])
ref=bpy.data.objects.new('REFERENCIA Panteon nube densa',me);scene.collection.objects.link(ref);ref.hide_render=True;ref.hide_set(True)
ns={'__name__':'builder','__file__':str(OUT/'reconstruir_panteon_blender.py')}
exec(compile((OUT/'reconstruir_panteon_blender.py').read_text(encoding='utf-8'),'base','exec'),ns,ns)
ns['build_core']();ns['details']();ns['finish']()
for name in ['refinar_ornamentos.py','ajustes_finales.py','revisar_acceso_basamento.py','refinar_puertas_hierro.py','refinar_barandas_dataset.py']:
 exec(compile((OUT/name).read_text(encoding='utf-8'),name,'exec'),ns,ns)
scene.camera.location=(-32,-40,26);scene.camera.rotation_euler=(Vector((-1,0,7))-scene.camera.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'panteon_catalan_regenerado.blend'))
