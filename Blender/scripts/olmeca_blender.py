# Sala Viva AR — arma la Cabeza colosal olmeca en Blender a partir de la malla generada.
# Uso (consola de Python de Blender):
#   exec(open(r"C:\Users\joses\OneDrive\Escritorio\RA\SalaVivaAR\02_Blender\scripts\olmeca_blender.py", encoding="utf-8").read())
import bpy, math, os
import numpy as np

BASE = r"C:\Users\joses\OneDrive\Escritorio\RA\SalaVivaAR"
TEX = os.path.join(BASE, "02_Blender", "texturas")
EXPORT = os.path.join(BASE, "03_Exportados")

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.cameras, bpy.data.lights):
    for b in list(coll):
        if b.users == 0:
            coll.remove(b)

d = np.load(os.path.join(TEX, "Olmeca_malla.npz"))
verts, faces, uvs = d["verts"], d["faces"], d["uvs"]

me = bpy.data.meshes.new("CabezaOlmeca")
me.from_pydata(verts.tolist(), [], faces.tolist())
me.update()
uv_layer = me.uv_layers.new(name="UVMap")
vi = np.empty(len(me.loops), dtype=np.int32); me.loops.foreach_get("vertex_index", vi)
uv_layer.data.foreach_set("uv", uvs[vi].ravel())
me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), dtype=bool))
me.validate()
obj = bpy.data.objects.new("CabezaOlmeca", me)
bpy.context.scene.collection.objects.link(obj)

# une la costura de atrás y los polos (vértices repetidos) sin tocar las UV
bpy.context.view_layer.objects.active = obj
obj.select_set(True)
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.remove_doubles(threshold=0.0005)
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode="OBJECT")

dec = obj.modifiers.new("Decimar_para_movil", "DECIMATE")
dec.ratio = 0.5

mat = bpy.data.materials.new("Olmeca_Basalto")
try:
    mat.use_nodes = True
except Exception:
    pass
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
t_col = nt.nodes.new("ShaderNodeTexImage"); t_col.location = (-600, 300)
t_col.image = bpy.data.images.load(os.path.join(TEX, "Olmeca_color.png"))
t_nrm = nt.nodes.new("ShaderNodeTexImage"); t_nrm.location = (-600, -100)
t_nrm.image = bpy.data.images.load(os.path.join(TEX, "Olmeca_normal.png"))
t_nrm.image.colorspace_settings.name = "Non-Color"
nmap = nt.nodes.new("ShaderNodeNormalMap"); nmap.location = (-300, -100); nmap.inputs["Strength"].default_value = 0.6
nt.links.new(t_col.outputs["Color"], bsdf.inputs["Base Color"])
nt.links.new(t_nrm.outputs["Color"], nmap.inputs["Color"])
nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
bsdf.inputs["Roughness"].default_value = 0.9
obj.data.materials.append(mat)

sun_d = bpy.data.lights.new("Sol", "SUN"); sun_d.energy = 3.5
sun = bpy.data.objects.new("Sol", sun_d); bpy.context.scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(55), math.radians(-30), math.radians(-30))
cam_d = bpy.data.cameras.new("Camara"); cam_d.lens = 50
cam = bpy.data.objects.new("Camara", cam_d); bpy.context.scene.collection.objects.link(cam)
cam.location = (2.6, -4.6, 1.2); cam.rotation_euler = (math.radians(86), 0, math.radians(30))
bpy.context.scene.camera = cam

bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True); bpy.context.view_layer.objects.active = obj
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE, "02_Blender", "CabezaOlmeca.blend"))
bpy.ops.export_scene.fbx(
    filepath=os.path.join(EXPORT, "CabezaOlmeca.fbx"),
    use_selection=True, use_mesh_modifiers=True,
    apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y",
    bake_space_transform=True, path_mode="COPY", embed_textures=True, mesh_smooth_type="FACE")
ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
print("Cabeza olmeca lista. Triángulos exportados aprox:", sum(len(p.vertices) - 2 for p in ev.data.polygons))
