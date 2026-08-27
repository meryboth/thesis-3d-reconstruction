"""
PRUEBA EXPLORATORIA (paso 2): lee primitives.json (generado por
analyze_pointcloud_primitives.py) y crea, para cada elemento detectado, una
PRIMITIVA NATIVA de Blender (cilindro real via bpy.ops.mesh.primitive_cylinder_add,
caja real via primitive_cube_add) -- geometria limpia y editable, no una malla
libre reconstruida punto a punto.

Los elementos "freeform_shell" (curvos, no reproducibles como caja/cilindro)
se muestran aparte como la malla de referencia ya reconstruida en el paso
anterior (blender_pointcloud_to_mesh.py / reconstruccion.ply), en un material
mas transparente, para que se vea el contraste: componente parametrico limpio
vs. superficie libre que todavia necesita malla.

Correr en modo background:
  blender --background --python blender_pointcloud_primitives.py -- <primitives.json> <reconstruccion.ply o ""> <out_dir>
"""
import sys
import os
import json
import math
import bpy
import mathutils

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []

JSON_PATH = argv[0] if len(argv) > 0 else r"C:\nerfstudio_work\thesis\00-auditoria\blender-pointcloud-test\primitives.json"
REF_MESH_PATH = argv[1] if len(argv) > 1 else r"C:\nerfstudio_work\thesis\00-auditoria\blender-pointcloud-test\reconstruccion.ply"
OUT_DIR = argv[2] if len(argv) > 2 else r"C:\nerfstudio_work\thesis\00-auditoria\blender-pointcloud-test"

os.makedirs(OUT_DIR, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)

with open(JSON_PATH, encoding="utf-8") as f:
    data = json.load(f)

primitives = data["primitives"]
print(f"[info] {len(primitives)} primitivas en {JSON_PATH}")

# --- materiales ---
def make_material(name, color, alpha=1.0, roughness=0.4):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        mat.blend_method = 'BLEND'
    return mat

mat_cylinder = make_material("PrimitivaCilindro", (0.85, 0.45, 0.15), roughness=0.3)
mat_box = make_material("PrimitivaCaja", (0.20, 0.55, 0.75), roughness=0.3)
mat_freeform = make_material("MallaFreeform", (0.75, 0.75, 0.75), alpha=0.35, roughness=0.9)

n_created = {"cylinder": 0, "box": 0}

for prim in primitives:
    if prim["type"] == "cylinder":
        centroid = mathutils.Vector(prim["centroid"])
        axis = mathutils.Vector(prim["axis"]).normalized()
        radius = max(prim["radius"], 0.02)
        length = max(prim["length"], 0.05)

        bpy.ops.mesh.primitive_cylinder_add(
            radius=radius, depth=length, location=centroid, vertices=24
        )
        cyl = bpy.context.active_object
        cyl.name = f"Columna_{n_created['cylinder']:02d}"
        # el cilindro nace con el eje en +Z local -- rotarlo para alinear Z con el axis detectado
        z_axis = mathutils.Vector((0, 0, 1))
        rot_quat = z_axis.rotation_difference(axis)
        cyl.rotation_euler = rot_quat.to_euler()
        cyl.data.materials.append(mat_cylinder)
        bpy.ops.object.shade_smooth()
        n_created["cylinder"] += 1

    elif prim["type"] == "box":
        centroid = mathutils.Vector(prim["centroid"])
        u = mathutils.Vector(prim["axis_u"]).normalized()
        v = mathutils.Vector(prim["axis_v"]).normalized()
        n = mathutils.Vector(prim["normal"]).normalized()
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=centroid)
        box = bpy.context.active_object
        box.name = f"Losa_{n_created['box']:02d}"
        mat_world = mathutils.Matrix((u, v, n)).transposed().to_4x4()
        box.rotation_euler = mat_world.to_euler()
        box.scale = (prim["size_u"], prim["size_v"], prim["thickness"])
        box.data.materials.append(mat_box)
        n_created["box"] += 1

print(f"[info] primitivas nativas creadas: {n_created}")

# --- malla freeform de referencia (lo que NO se pudo reducir a primitiva) ---
if REF_MESH_PATH and os.path.exists(REF_MESH_PATH):
    bpy.ops.wm.ply_import(filepath=REF_MESH_PATH)
    ref_obj = bpy.context.selected_objects[0]
    ref_obj.name = "Superficie_freeform_referencia"
    ref_obj.data.materials.append(mat_freeform)
    print(f"[info] malla de referencia freeform cargada: {REF_MESH_PATH}")
else:
    ref_obj = None
    print("[info] sin malla de referencia freeform (no se paso o no existe)")

# --- camara + luces ---
all_objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
if all_objs:
    coords = []
    for o in all_objs:
        for c in o.bound_box:
            coords.append(o.matrix_world @ mathutils.Vector(c))
    xs = [c.x for c in coords]; ys = [c.y for c in coords]; zs = [c.z for c in coords]
    center = mathutils.Vector(((max(xs)+min(xs))/2, (max(ys)+min(ys))/2, (max(zs)+min(zs))/2))
    diag = ((max(xs)-min(xs))**2 + (max(ys)-min(ys))**2 + (max(zs)-min(zs))**2) ** 0.5
else:
    center = mathutils.Vector((0, 0, 0))
    diag = 5.0

cam_data = bpy.data.cameras.new("Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam_obj)
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
scene.render.filepath = os.path.join(OUT_DIR, "primitivas_render.png")
scene.render.film_transparent = False

bpy.ops.render.render(write_still=True)
print(f"[info] render guardado: {scene.render.filepath}")

blend_path = os.path.join(OUT_DIR, "pointcloud_primitives.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"[info] .blend guardado: {blend_path}")
print("[OK] listo")
