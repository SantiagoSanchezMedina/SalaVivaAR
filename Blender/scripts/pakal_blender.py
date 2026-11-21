# Sala Viva AR — construye la máscara funeraria de Pakal en Blender.
# Uso (consola de Python de Blender):
#   exec(open(r"C:\Users\joses\OneDrive\Escritorio\RA\SalaVivaAR\02_Blender\scripts\pakal_blender.py", encoding="utf-8").read())
import bpy, math, os
import numpy as np

BASE = r"C:\Users\joses\OneDrive\Escritorio\RA\SalaVivaAR"
TEX = os.path.join(BASE, "02_Blender", "texturas")
EXPORT = os.path.join(BASE, "03_Exportados")
ALTO = 0.24          # alto real de la máscara (m)
GROSOR = 0.012       # espesor del mosaico + soporte (m)
PASO = 4             # muestreo de la malla (px de la textura)

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.cameras, bpy.data.lights):
    for b in list(coll):
        if b.users == 0:
            coll.remove(b)

prof = np.load(os.path.join(TEX, "Pakal_prof.npy"))
H, W = prof.shape
filas = np.nonzero(~np.all(np.isnan(prof), axis=1))[0]
M_PX = ALTO / (filas.max() - filas.min())
y_centro = (filas.max() + filas.min()) / 2

ii = np.arange(0, H, PASO); jj = np.arange(0, W, PASO)
indice = -np.ones((len(ii), len(jj)), dtype=np.int64)
verts, uvs = [], []
for a, i in enumerate(ii):
    for b, j in enumerate(jj):
        z = prof[i, j]
        if np.isnan(z):
            continue
        indice[a, b] = len(verts)
        verts.append(((j - W / 2) * M_PX, -float(z), (y_centro - i) * M_PX + ALTO / 2))
        uvs.append((j / (W - 1), 1 - i / (H - 1)))
faces = []
for a in range(len(ii) - 1):
    for b in range(len(jj) - 1):
        q = (indice[a, b], indice[a + 1, b], indice[a + 1, b + 1], indice[a, b + 1])
        if min(q) >= 0:
            faces.append(q)

me = bpy.data.meshes.new("MascaraPakal")
me.from_pydata(verts, [], faces)
me.update()
uv_layer = me.uv_layers.new(name="UVMap")
vi = np.empty(len(me.loops), dtype=np.int32); me.loops.foreach_get("vertex_index", vi)
uv_layer.data.foreach_set("uv", np.array(uvs, dtype=np.float32)[vi].ravel())
me.polygons.foreach_set("use_smooth", np.ones(len(me.polygons), dtype=bool))
me.validate()

obj = bpy.data.objects.new("MascaraPakal", me)
bpy.context.scene.collection.objects.link(obj)

sol = obj.modifiers.new("Espesor", "SOLIDIFY")
sol.thickness = GROSOR
sol.offset = 1.0                 # el espesor crece hacia atrás
sol.use_even_offset = True
dec = obj.modifiers.new("Decimar_para_movil", "DECIMATE")
dec.ratio = 0.35

# ---------- material de jade ----------
mat = bpy.data.materials.new("Pakal_Jade")
try:
    mat.use_nodes = True
except Exception:
    pass
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
t_col = nt.nodes.new("ShaderNodeTexImage"); t_col.location = (-600, 300)
t_col.image = bpy.data.images.load(os.path.join(TEX, "Pakal_color.png"))
t_nrm = nt.nodes.new("ShaderNodeTexImage"); t_nrm.location = (-600, -100)
t_nrm.image = bpy.data.images.load(os.path.join(TEX, "Pakal_normal.png"))
t_nrm.image.colorspace_settings.name = "Non-Color"
nmap = nt.nodes.new("ShaderNodeNormalMap"); nmap.location = (-300, -100)
nt.links.new(t_col.outputs["Color"], bsdf.inputs["Base Color"])
nt.links.new(t_nrm.outputs["Color"], nmap.inputs["Color"])
nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
bsdf.inputs["Roughness"].default_value = 0.32          # jade pulido
obj.data.materials.append(mat)

# ---------- luz y cámara para revisar ----------
sun_d = bpy.data.lights.new("Sol", "SUN"); sun_d.energy = 3.0
sun = bpy.data.objects.new("Sol", sun_d); bpy.context.scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(60), math.radians(-25), math.radians(-25))
cam_d = bpy.data.cameras.new("Camara"); cam_d.lens = 60
cam = bpy.data.objects.new("Camara", cam_d); bpy.context.scene.collection.objects.link(cam)
cam.location = (0.25, -0.75, ALTO / 2 + 0.03); cam.rotation_euler = (math.radians(88), 0, math.radians(18))
bpy.context.scene.camera = cam

bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True); bpy.context.view_layer.objects.active = obj
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE, "02_Blender", "MascaraPakal.blend"))
bpy.ops.export_scene.fbx(
    filepath=os.path.join(EXPORT, "MascaraPakal.fbx"),
    use_selection=True, use_mesh_modifiers=True,
    apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y",
    bake_space_transform=True, path_mode="COPY", embed_textures=True, mesh_smooth_type="FACE")
ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
print("Máscara de Pakal lista. Triángulos exportados aprox:", sum(len(p.vertices) - 2 for p in ev.data.polygons))
