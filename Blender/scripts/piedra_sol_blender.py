# Sala Viva AR — construye la Piedra del Sol en Blender a partir del mapa de altura.
# Uso (consola de Python de Blender):
#   exec(open(r"C:\Users\joses\OneDrive\Escritorio\RA\SalaVivaAR\02_Blender\scripts\piedra_sol_blender.py", encoding="utf-8").read())
import bpy, math, os
import numpy as np

BASE = r"C:\Users\joses\OneDrive\Escritorio\RA\SalaVivaAR"
TEX = os.path.join(BASE, "02_Blender", "texturas")
EXPORT = os.path.join(BASE, "03_Exportados")
DOCS = os.path.join(BASE, "06_Documentacion", "renders")
os.makedirs(EXPORT, exist_ok=True)
os.makedirs(DOCS, exist_ok=True)

DIAM = 3.58          # diámetro real (m)
GROSOR = 0.98        # grosor real (m)
RELIEVE = 0.18       # profundidad del tallado (m) entre el fondo y lo más alto
H_FONDO = 0.38       # valor del mapa de altura que corresponde al fondo tallado
NR, NS = 180, 540    # anillos y segmentos de la malla polar
S = DIAM / 0.985     # tamaño que cubre la imagen completa
RAD = DIAM / 2

# ---------- limpiar escena ----------
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.cameras, bpy.data.lights):
    for b in list(coll):
        if b.users == 0:
            coll.remove(b)

# ---------- mapa de altura ----------
alt = np.load(os.path.join(TEX, "PiedraSol_altura.npy")).astype(np.float32)
NPX = alt.shape[0]

def altura(x, y):
    # x, y en metros (plano de la cara); bilineal sobre el mapa
    u = (x / S + 0.5) * (NPX - 1)
    v = (0.5 - y / S) * (NPX - 1)          # fila 0 = arriba
    u0 = np.clip(np.floor(u).astype(int), 0, NPX - 2); v0 = np.clip(np.floor(v).astype(int), 0, NPX - 2)
    fu, fv = u - u0, v - v0
    a = alt[v0, u0] * (1 - fu) + alt[v0, u0 + 1] * fu
    b = alt[v0 + 1, u0] * (1 - fu) + alt[v0 + 1, u0 + 1] * fu
    return a * (1 - fv) + b * fv

# ---------- malla ----------
verts, faces, uvs_por_vert = [], [], []
ang = np.linspace(0, 2 * math.pi, NS, endpoint=False)

def uv(x, y):
    return (x / S + 0.5, y / S + 0.5)

# cara frontal: centro + anillos
radios = np.linspace(0, RAD, NR + 1)[1:]
xs = np.concatenate([[0.0], (radios[:, None] * np.cos(ang)[None, :]).ravel()])
ys = np.concatenate([[0.0], (radios[:, None] * np.sin(ang)[None, :]).ravel()])
zs = (altura(xs, ys) - H_FONDO) * (RELIEVE / (1 - H_FONDO))
zs[np.hypot(xs, ys) > RAD * 0.995] = np.minimum(zs[np.hypot(xs, ys) > RAD * 0.995], 0.02)
for x, y, z in zip(xs, ys, zs):
    verts.append((x, y, z)); uvs_por_vert.append(uv(x, y))

def idx(i, j):  # anillo i (0..NR-1), segmento j
    return 1 + i * NS + (j % NS)

for j in range(NS):
    faces.append((0, idx(0, j), idx(0, j + 1)))
for i in range(NR - 1):
    for j in range(NS):
        faces.append((idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)))
n_frente = len(faces)

# costado: anillo propio (vértices duplicados para que el borde quede marcado)
base_lado = len(verts)
z_borde = float(np.max(zs[-NS:]))
for k, a in enumerate(ang):
    x, y = RAD * math.cos(a), RAD * math.sin(a)
    verts.append((x, y, zs[idx(NR - 1, k)])); uvs_por_vert.append(uv(x, y))
for k, a in enumerate(ang):
    x, y = RAD * math.cos(a), RAD * math.sin(a)
    verts.append((x, y, -GROSOR)); uvs_por_vert.append(uv(x * 0.97, y * 0.97))
for k in range(NS):
    a0, a1 = base_lado + k, base_lado + (k + 1) % NS
    b0, b1 = base_lado + NS + k, base_lado + NS + (k + 1) % NS
    faces.append((a0, b0, b1, a1))
n_lado = len(faces)

# reverso: disco plano
base_atras = len(verts)
verts.append((0, 0, -GROSOR)); uvs_por_vert.append((0.5, 0.5))
for a in ang:
    x, y = RAD * math.cos(a), RAD * math.sin(a)
    verts.append((x, y, -GROSOR)); uvs_por_vert.append(uv(x, y))
for k in range(NS):
    faces.append((base_atras, base_atras + 1 + (k + 1) % NS, base_atras + 1 + k))

me = bpy.data.meshes.new("PiedraSol")
me.from_pydata(verts, [], faces)
me.update()
# normales hacia afuera (la cara frontal mira a +Z)
uv_layer = me.uv_layers.new(name="UVMap")
loop_uv = np.empty(len(me.loops) * 2, dtype=np.float32)
loop_vi = np.empty(len(me.loops), dtype=np.int32)
me.loops.foreach_get("vertex_index", loop_vi)
uv_arr = np.array(uvs_por_vert, dtype=np.float32)
uv_layer.data.foreach_set("uv", uv_arr[loop_vi].ravel())
smooth = np.ones(len(me.polygons), dtype=bool)
smooth[n_lado:] = False
me.polygons.foreach_set("use_smooth", smooth)
me.validate()

obj = bpy.data.objects.new("PiedraSol", me)
bpy.context.scene.collection.objects.link(obj)
obj.rotation_euler = (math.radians(90), 0, 0)      # de pie, la cara mira hacia -Y (vista frontal)
obj.location = (0, 0, RAD)                           # apoyada en el piso

# ---------- material ----------
mat = bpy.data.materials.new("PiedraSol_Basalto")
try:
    mat.use_nodes = True
except Exception:
    pass
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
img_col = bpy.data.images.load(os.path.join(TEX, "PiedraSol_color.png"))
img_nrm = bpy.data.images.load(os.path.join(TEX, "PiedraSol_normal.png"))
img_nrm.colorspace_settings.name = "Non-Color"
t_col = nt.nodes.new("ShaderNodeTexImage"); t_col.image = img_col; t_col.location = (-600, 300)
t_nrm = nt.nodes.new("ShaderNodeTexImage"); t_nrm.image = img_nrm; t_nrm.location = (-600, -100)
nmap = nt.nodes.new("ShaderNodeNormalMap"); nmap.location = (-300, -100); nmap.inputs["Strength"].default_value = 0.8
nt.links.new(t_col.outputs["Color"], bsdf.inputs["Base Color"])
nt.links.new(t_nrm.outputs["Color"], nmap.inputs["Color"])
nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
bsdf.inputs["Roughness"].default_value = 0.88
obj.data.materials.append(mat)

# versión ligera para la app (se aplica al exportar)
dec = obj.modifiers.new("Decimar_para_movil", "DECIMATE")
dec.ratio = 0.22

# ---------- luz, cámara y render de evidencia ----------
sun_data = bpy.data.lights.new("Sol", "SUN"); sun_data.energy = 3.5
sun = bpy.data.objects.new("Sol", sun_data); bpy.context.scene.collection.objects.link(sun)
sun.rotation_euler = (math.radians(55), math.radians(-35), math.radians(-20))
cam_data = bpy.data.cameras.new("Camara"); cam_data.lens = 50
cam = bpy.data.objects.new("Camara", cam_data); bpy.context.scene.collection.objects.link(cam)
cam.location = (2.2, -7.2, RAD + 0.4)
cam.rotation_euler = (math.radians(88), 0, math.radians(17))
scn = bpy.context.scene
scn.camera = cam
if scn.world is None:
    scn.world = bpy.data.worlds.new("Mundo")
try:
    scn.world.use_nodes = True
except Exception:
    pass
bg = next((n for n in scn.world.node_tree.nodes if n.type == "BACKGROUND"), None)
if bg:
    bg.inputs["Color"].default_value = (0.08, 0.08, 0.09, 1); bg.inputs["Strength"].default_value = 0.6

bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj

# guardar .blend
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE, "02_Blender", "PiedraSol.blend"))

# exportar FBX para Unity (con el decimado aplicado)
bpy.ops.export_scene.fbx(
    filepath=os.path.join(EXPORT, "PiedraSol.fbx"),
    use_selection=True, use_mesh_modifiers=True,
    apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z", axis_up="Y",
    bake_space_transform=True, path_mode="COPY", embed_textures=True, mesh_smooth_type="FACE")

ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
print("Piedra del Sol lista. Triángulos (alta):", sum(len(p.vertices) - 2 for p in me.polygons),
      "| triángulos exportados aprox:", sum(len(p.vertices) - 2 for p in ev.data.polygons))
