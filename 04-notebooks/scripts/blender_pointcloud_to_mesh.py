"""
PRUEBA EXPLORATORIA (no forma parte todavia de la tesis): reconstruir una
superficie 3D dentro de Blender a partir de una nube de puntos densa (.ply),
usando solo herramientas nativas de Blender (Geometry Nodes: Points to
Volume -> Volume to Mesh), sin addons externos.

Objetivo de la prueba: evaluar si este camino (nube de puntos -> reconstruccion
en Blender) es viable como propuesta alternativa/complementaria al "archivo
digital" final de la tesis (hoy: export .ply de Splatfacto o .obj texturizado
de RealityScan).

Correr en modo background:
  blender --background --python blender_pointcloud_to_mesh.py -- <input.ply> <out_dir> [voxel_size]

Si no se pasan argumentos usa el dataset de prueba por defecto (Los Paraguas,
nube densa limpia de CloudCompare, 502817 puntos).
"""
import sys
import os
import bpy
import bmesh
import mathutils

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []

PLY_PATH = argv[0] if len(argv) > 0 else r"C:\nerfstudio_work\thesis\01-paraguas-vicentelopez\02-resultados-finales\colmap-fotogrametria-densa\fused_medium_high_clean.ply"
OUT_DIR = argv[1] if len(argv) > 1 else r"C:\nerfstudio_work\thesis\00-auditoria\blender-pointcloud-test"
VOXEL_SIZE = float(argv[2]) if len(argv) > 2 else None  # None = auto, segun bbox

os.makedirs(OUT_DIR, exist_ok=True)

# --- limpiar escena por defecto ---
bpy.ops.wm.read_factory_settings(use_empty=True)

# --- importar la nube de puntos ---
bpy.ops.wm.ply_import(filepath=PLY_PATH)
pc_obj = bpy.context.selected_objects[0]
pc_obj.name = "PointCloud"
n_points = len(pc_obj.data.vertices)
print(f"[info] nube importada: {n_points} puntos, archivo: {PLY_PATH}")

# --- bbox para calibrar voxel_size / radio automaticamente ---
bbox_corners = [pc_obj.matrix_world @ mathutils.Vector(c) for c in pc_obj.bound_box]
xs = [c.x for c in bbox_corners]
ys = [c.y for c in bbox_corners]
zs = [c.z for c in bbox_corners]
diag = ((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2 + (max(zs) - min(zs)) ** 2) ** 0.5
if VOXEL_SIZE is None:
    VOXEL_SIZE = diag / 350.0
point_radius = VOXEL_SIZE * 1.6
print(f"[info] bbox diagonal: {diag:.3f} m -> voxel_size={VOXEL_SIZE:.4f}  point_radius={point_radius:.4f}")

# --- Geometry Nodes: Mesh to Points -> Points to Volume -> Volume to Mesh ---
bpy.ops.object.modifier_add(type='NODES')
gn_mod = pc_obj.modifiers[-1]
node_group = gn_mod.node_group

if node_group is None:
    # en algunas versiones/contextos (headless) modifier_add(type='NODES') no
    # arma un node tree por defecto -- se crea a mano con las interfaces
    # Geometry in/out estandar.
    node_group = bpy.data.node_groups.new("PointsToVolumeToMesh", 'GeometryNodeTree')
    node_group.interface.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    node_group.interface.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
    gn_mod.node_group = node_group
else:
    node_group.name = "PointsToVolumeToMesh"

nodes = node_group.nodes
links = node_group.links

group_in = next((n for n in nodes if n.type == 'GROUP_INPUT'), None) or nodes.new("NodeGroupInput")
group_out = next((n for n in nodes if n.type == 'GROUP_OUTPUT'), None) or nodes.new("NodeGroupOutput")

mesh_to_points = nodes.new("GeometryNodeMeshToPoints")
mesh_to_points.location = (group_in.location.x + 200, 0)

points_to_volume = nodes.new("GeometryNodePointsToVolume")
points_to_volume.location = (mesh_to_points.location.x + 200, 0)
points_to_volume.inputs["Resolution Mode"].default_value = "Size"  # en vez de "Amount"
points_to_volume.inputs["Voxel Size"].default_value = VOXEL_SIZE
points_to_volume.inputs["Radius"].default_value = point_radius

volume_to_mesh = nodes.new("GeometryNodeVolumeToMesh")
volume_to_mesh.location = (points_to_volume.location.x + 200, 0)
volume_to_mesh.inputs["Resolution Mode"].default_value = "Size"
volume_to_mesh.inputs["Voxel Size"].default_value = VOXEL_SIZE
volume_to_mesh.inputs["Threshold"].default_value = 0.1
volume_to_mesh.inputs["Adaptivity"].default_value = 0.2

smooth = nodes.new("GeometryNodeSetShadeSmooth")
smooth.location = (volume_to_mesh.location.x + 200, 0)

links.new(group_in.outputs["Geometry"], mesh_to_points.inputs["Mesh"])
links.new(mesh_to_points.outputs["Points"], points_to_volume.inputs["Points"])
links.new(points_to_volume.outputs["Volume"], volume_to_mesh.inputs["Volume"])
links.new(volume_to_mesh.outputs["Mesh"], smooth.inputs["Geometry"])
links.new(smooth.outputs["Geometry"], group_out.inputs["Geometry"])

print("[info] geometry nodes armado, aplicando modificador...")

# --- aplicar el modificador (bakear a malla real) ---
depsgraph = bpy.context.evaluated_depsgraph_get()
eval_obj = pc_obj.evaluated_get(depsgraph)
mesh_from_eval = bpy.data.meshes.new_from_object(eval_obj)

recon_obj = bpy.data.objects.new("PointCloud_Reconstruida", mesh_from_eval)
bpy.context.collection.objects.link(recon_obj)
recon_obj.matrix_world = pc_obj.matrix_world.copy()

n_verts = len(mesh_from_eval.vertices)
n_faces = len(mesh_from_eval.polygons)
print(f"[info] malla reconstruida (antes de limpiar islas sueltas): {n_verts} vertices, {n_faces} caras")

pc_obj.hide_render = True
pc_obj.hide_set(True)

# --- Points to Volume genera "floaters": blobs sueltos donde hay puntos
# aislados/ruido en la nube (mismo problema que ya aparece en los floaters de
# Nerfacto documentados en el Cap. 5). Se separan las islas conectadas y se
# se queda solo con la mas grande (el cuerpo principal de la reconstruccion).
bpy.ops.object.select_all(action='DESELECT')
recon_obj.select_set(True)
bpy.context.view_layer.objects.active = recon_obj
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.separate(type='LOOSE')
bpy.ops.object.mode_set(mode='OBJECT')

island_objs = [o for o in bpy.context.selected_objects if o.type == 'MESH']
island_objs.sort(key=lambda o: len(o.data.vertices), reverse=True)
main_obj = island_objs[0]
discarded_verts = sum(len(o.data.vertices) for o in island_objs[1:])
for o in island_objs[1:]:
    mesh_data = o.data
    bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.meshes.remove(mesh_data)

main_obj.name = "PointCloud_Reconstruida"
recon_obj = main_obj
mesh_from_eval = recon_obj.data
n_verts_clean = len(mesh_from_eval.vertices)
print(f"[info] islas sueltas descartadas: {len(island_objs) - 1} ({discarded_verts} vertices) "
      f"-> malla final: {n_verts_clean} vertices ({n_verts_clean/n_verts*100:.1f}% del total)")

# --- material simple tipo clay (arcilla), para poder leer la geometria ---
mat = bpy.data.materials.new("ClayGris")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.72, 0.70, 0.65, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.85
recon_obj.data.materials.append(mat)

# --- camara + luz basica para poder renderizar una vista ---
cam_data = bpy.data.cameras.new("Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam_obj)

center = mathutils.Vector(((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, (max(zs) + min(zs)) / 2))
cam_dist = diag * 1.4
cam_obj.location = center + mathutils.Vector((cam_dist * 0.6, -cam_dist * 0.9, cam_dist * 0.5))
direction = center - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam_obj

sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3.0
sun_obj = bpy.data.objects.new("Sun", sun_data)
sun_obj.rotation_euler = (0.9, 0.2, 0.6)
bpy.context.collection.objects.link(sun_obj)

fill_data = bpy.data.lights.new("Fill", type='SUN')
fill_data.energy = 1.0
fill_obj = bpy.data.objects.new("Fill", fill_data)
fill_obj.rotation_euler = (2.0, 0.0, -1.2)
bpy.context.collection.objects.link(fill_obj)

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 800
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = os.path.join(OUT_DIR, "reconstruccion_render.png")

print(f"[info] render engine: {scene.render.engine}")
bpy.ops.render.render(write_still=True)
print(f"[info] render guardado: {scene.render.filepath}")

# --- exportar la malla reconstruida y guardar el .blend ---
export_path = os.path.join(OUT_DIR, "reconstruccion.ply")
bpy.ops.object.select_all(action='DESELECT')
recon_obj.select_set(True)
bpy.context.view_layer.objects.active = recon_obj
bpy.ops.wm.ply_export(filepath=export_path, export_selected_objects=True)
print(f"[info] malla exportada: {export_path}")

blend_path = os.path.join(OUT_DIR, "pointcloud_test.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"[info] .blend guardado: {blend_path}")

print("[OK] listo")
