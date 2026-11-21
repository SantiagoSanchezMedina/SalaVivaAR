# Sala Viva AR — renders de los 4 modelos para las cédulas (fondo transparente).
# Reconstruye cada pieza con su script y la renderiza con EEVEE en 04_Cedulas\renders.
# Uso (consola de Python de Blender):
#   exec(open(r"C:\Users\joses\OneDrive\Escritorio\RA\SalaVivaAR\02_Blender\scripts\render_cedulas_blender.py", encoding="utf-8").read())
import bpy, math, os
from mathutils import Vector

BASE = r"C:\Users\joses\OneDrive\Escritorio\RA\SalaVivaAR"
SCRIPTS = os.path.join(BASE, "02_Blender", "scripts")
SALIDA = os.path.join(BASE, "04_Cedulas", "renders")
os.makedirs(SALIDA, exist_ok=True)

PIEZAS = [
    # script, objeto, dirección de la cámara (desde el objeto hacia la cámara), nombre de salida
    ("piedra_sol_blender.py", "PiedraSol", (0.0, -1.0, 0.04), "render_piedra_sol.png"),
    ("pakal_blender.py", "MascaraPakal", (0.30, -1.0, 0.10), "render_pakal.png"),
    ("olmeca_blender.py", "CabezaOlmeca", (0.55, -1.0, 0.18), "render_cabeza_olmeca.png"),
    ("chacmool_blender.py", "ChacMool", (0.35, -1.0, 0.40), "render_chac_mool.png"),
]

def preparar_render(obj, direccion, archivo):
    scn = bpy.context.scene
    try:
        scn.render.engine = "BLENDER_EEVEE"
    except Exception:
        scn.render.engine = "BLENDER_EEVEE_NEXT"
    scn.render.resolution_x = 1400; scn.render.resolution_y = 1400
    scn.render.film_transparent = True
    scn.render.image_settings.file_format = "PNG"
    scn.render.image_settings.color_mode = "RGBA"
    try:
        scn.view_settings.view_transform = "Standard"
    except Exception:
        pass
    # mundo: luz ambiental suave
    w = scn.world
    bg = next((n for n in w.node_tree.nodes if n.type == "BACKGROUND"), None)
    if bg:
        bg.inputs["Color"].default_value = (0.55, 0.55, 0.57, 1); bg.inputs["Strength"].default_value = 0.9
    # caja envolvente en coordenadas del mundo (malla evaluada)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    pts = [obj.matrix_world @ v.co for v in ev.data.vertices]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    centro = (mn + mx) / 2
    tam = max((mx - mn).x, (mx - mn).y, (mx - mn).z)
    cam = scn.camera
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = tam * 1.12
    d = Vector(direccion).normalized()
    cam.location = centro + d * tam * 4
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    cam.data.clip_end = tam * 20
    # luces: principal desde arriba-izquierda y relleno
    sol = bpy.data.objects.get("Sol")
    if sol:
        sol.data.energy = 3.2
        sol.rotation_euler = (math.radians(50), math.radians(-28), math.radians(-35))
    rel_d = bpy.data.lights.new("Relleno", "SUN"); rel_d.energy = 1.0
    rel = bpy.data.objects.new("Relleno", rel_d); scn.collection.objects.link(rel)
    rel.rotation_euler = (math.radians(70), math.radians(30), math.radians(140))
    scn.render.filepath = os.path.join(SALIDA, archivo)
    bpy.ops.render.render(write_still=True)
    print("Render listo:", archivo)

for script, nombre, direccion, archivo in PIEZAS:
    exec(open(os.path.join(SCRIPTS, script), encoding="utf-8").read(), {"__name__": "__main__"})
    obj = bpy.data.objects[nombre]
    preparar_render(obj, direccion, archivo)
print("Todos los renders terminados en", SALIDA)
