"""Kit gráfico de la interfaz de Sala Viva AR (temática mesoamericana).
Paleta: obsidiana, piedra, jade, terracota, ocre/oro y hueso. Todo se dibuja al doble y se reduce (antialias).
Uso: python gen_ui.py <carpeta_renders> <carpeta_salida>
"""
import sys, os, math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RENDERS, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
OBS = (20, 17, 15); PIEDRA = (42, 36, 32); JADE = (31, 122, 92); JADE_C = (63, 181, 138)
TERRA = (181, 72, 43); OCRE = (224, 169, 59); OCRE_O = (168, 112, 26); HUESO = (243, 233, 215)
SS = 2  # superm muestreo

def lienzo(w, h): return Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
def bajar(im, w, h): return im.resize((w, h), Image.LANCZOS)
def guardar(im, nombre): im.save(os.path.join(OUT, nombre))

def greca_esquina(d, x, y, s, col, w, sx=1, sy=1):
    """Pequeño escalón de greca en una esquina (orientado con sx/sy)."""
    p = [(x, y + sy * s), (x, y), (x + sx * s, y), (x + sx * s, y + sy * s * 0.45),
         (x + sx * s * 0.45, y + sy * s * 0.45)]
    d.line(p, fill=col, width=w, joint="curve")

# ---------- panel obsidiana con marco ocre (9-slice) ----------
def panel(nombre, fondo, borde, alpha=238):
    W = H = 256; im = lienzo(W, H); d = ImageDraw.Draw(im); s = SS
    d.rounded_rectangle([4 * s, 4 * s, (W - 4) * s, (H - 4) * s], radius=34 * s, fill=fondo + (alpha,))
    d.rounded_rectangle([16 * s, 16 * s, (W - 16) * s, (H - 16) * s], radius=24 * s, outline=borde + (255,), width=3 * s)
    for (x, y, sx, sy) in [(26, 26, 1, 1), (W - 26, 26, -1, 1), (26, H - 26, 1, -1), (W - 26, H - 26, -1, -1)]:
        greca_esquina(d, x * s, y * s, 26 * s, borde + (255,), 4 * s, sx, sy)
    guardar(bajar(im, W, H), nombre)

panel("panel_obsidiana.png", OBS, OCRE)
panel("panel_jade.png", (14, 46, 37), JADE_C)

# ---------- botones (9-slice) ----------
def boton(nombre, c1, c2, borde, contorno=False):
    W, H = 256, 128; im = lienzo(W, H); d = ImageDraw.Draw(im); s = SS
    if contorno:
        d.rounded_rectangle([3 * s, 3 * s, (W - 3) * s, (H - 3) * s], radius=40 * s, fill=OBS + (170,), outline=borde + (255,), width=4 * s)
    else:
        grad = Image.new("RGBA", (W * s, H * s))
        a = np.linspace(0, 1, H * s)[:, None, None]
        g = (np.array(c1)[None, None, :] * (1 - a) + np.array(c2)[None, None, :] * a)
        g = np.concatenate([g.repeat(W * s, 1), np.full((H * s, W * s, 1), 255)], -1).astype(np.uint8)
        grad = Image.fromarray(g, "RGBA")
        m = Image.new("L", (W * s, H * s), 0); ImageDraw.Draw(m).rounded_rectangle([3 * s, 3 * s, (W - 3) * s, (H - 3) * s], radius=40 * s, fill=255)
        im.paste(grad, (0, 0), m)
        d.rounded_rectangle([3 * s, 3 * s, (W - 3) * s, (H - 3) * s], radius=40 * s, outline=borde + (255,), width=3 * s)
        brillo = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(brillo).rounded_rectangle([14 * s, 9 * s, (W - 14) * s, 44 * s], radius=20 * s, fill=(255, 255, 255, 46))
        im.alpha_composite(brillo)
    guardar(bajar(im, W, H), nombre)

boton("boton_ocre.png", (240, 190, 85), (200, 135, 35), OCRE_O)
boton("boton_jade.png", (70, 170, 125), (25, 100, 75), (14, 70, 52))
boton("boton_terracota.png", (205, 100, 65), (150, 55, 30), (110, 40, 22))
boton("boton_contorno.png", None, None, OCRE, contorno=True)

# chip/píldora blanca (para teñir) y círculo para botones de ícono
im = lienzo(128, 64); ImageDraw.Draw(im).rounded_rectangle([0, 0, 128 * SS - 1, 64 * SS - 1], radius=32 * SS, fill=(255, 255, 255, 255))
guardar(bajar(im, 128, 64), "chip.png")
im = lienzo(160, 160); d = ImageDraw.Draw(im); s = SS
d.ellipse([4 * s, 4 * s, 156 * s, 156 * s], fill=OBS + (225,), outline=OCRE + (255,), width=5 * s)
d.ellipse([16 * s, 16 * s, 144 * s, 144 * s], outline=OCRE + (90,), width=2 * s)
guardar(bajar(im, 160, 160), "circulo_boton.png")
im = Image.new("RGBA", (16, 16), (255, 255, 255, 255)); guardar(im, "blanco.png")

# ---------- íconos (blancos, 128 px) ----------
def icono(nombre, dibujar):
    W = 128; im = lienzo(W, W); d = ImageDraw.Draw(im); dibujar(d, SS); guardar(bajar(im, W, W), "ico_" + nombre + ".png")
B = (255, 255, 255, 255)
def flecha_arco(d, s, inv):
    box = [24 * s, 24 * s, 104 * s, 104 * s]
    if not inv:
        d.arc(box, 200, 470, fill=B, width=11 * s); x, y = 64 + 40 * math.cos(math.radians(110)), 64 + 40 * math.sin(math.radians(110))
        d.polygon([(18 * s, 70 * s), (44 * s, 70 * s), (28 * s, 96 * s)], fill=B)
    else:
        d.arc(box, 70, 340, fill=B, width=11 * s)
        d.polygon([(110 * s, 70 * s), (84 * s, 70 * s), (100 * s, 96 * s)], fill=B)
icono("rotar_izq", lambda d, s: flecha_arco(d, s, False))
icono("rotar_der", lambda d, s: flecha_arco(d, s, True))
def ico_reiniciar(d, s):
    d.arc([22 * s, 22 * s, 106 * s, 106 * s], 30, 330, fill=B, width=11 * s)
    d.polygon([(96 * s, 14 * s), (112 * s, 46 * s), (80 * s, 44 * s)], fill=B)
    d.ellipse([54 * s, 54 * s, 74 * s, 74 * s], fill=B)
icono("reiniciar", ico_reiniciar)
def ico_autogiro(d, s):
    d.ellipse([18 * s, 38 * s, 110 * s, 90 * s], outline=B, width=9 * s)
    d.polygon([(100 * s, 50 * s), (122 * s, 62 * s), (100 * s, 76 * s)], fill=B)
    d.polygon([(52 * s, 50 * s), (78 * s, 64 * s), (52 * s, 78 * s)], fill=B)
icono("autogiro", ico_autogiro)
def ico_info(d, s):
    d.ellipse([10 * s, 10 * s, 118 * s, 118 * s], outline=B, width=9 * s)
    d.ellipse([56 * s, 30 * s, 72 * s, 46 * s], fill=B); d.rounded_rectangle([56 * s, 54 * s, 72 * s, 98 * s], radius=4 * s, fill=B)
icono("info", ico_info)
def ico_cerrar(d, s):
    d.line([(32 * s, 32 * s), (96 * s, 96 * s)], fill=B, width=13 * s); d.line([(96 * s, 32 * s), (32 * s, 96 * s)], fill=B, width=13 * s)
icono("cerrar", ico_cerrar)
def ico_ayuda(d, s):
    d.ellipse([10 * s, 10 * s, 118 * s, 118 * s], outline=B, width=9 * s)
    d.arc([42 * s, 26 * s, 86 * s, 70 * s], 180, 30, fill=B, width=10 * s)
    d.line([(80 * s, 62 * s), (64 * s, 74 * s), (64 * s, 84 * s)], fill=B, width=10 * s)
    d.ellipse([57 * s, 92 * s, 71 * s, 106 * s], fill=B)
icono("ayuda", ico_ayuda)
def ico_metricas(d, s):
    for i, h in enumerate([40, 70, 54, 92]):
        x = 18 + i * 26; d.rounded_rectangle([x * s, (110 - h) * s, (x + 18) * s, 110 * s], radius=3 * s, fill=B)
icono("metricas", ico_metricas)
def ico_flecha(d, s, izq):
    p = [(84, 20), (40, 64), (84, 108)] if izq else [(44, 20), (88, 64), (44, 108)]
    d.line([(x * s, y * s) for x, y in p], fill=B, width=14 * s, joint="curve")
icono("anterior", lambda d, s: ico_flecha(d, s, True))
icono("siguiente", lambda d, s: ico_flecha(d, s, False))
def ico_mapa(d, s):
    d.polygon([(14 * s, 30 * s), (46 * s, 18 * s), (82 * s, 30 * s), (114 * s, 18 * s), (114 * s, 98 * s), (82 * s, 110 * s), (46 * s, 98 * s), (14 * s, 110 * s)], outline=B, width=8 * s)
    d.line([(46 * s, 18 * s), (46 * s, 98 * s)], fill=B, width=6 * s); d.line([(82 * s, 30 * s), (82 * s, 110 * s)], fill=B, width=6 * s)
icono("mapa", ico_mapa)
def ico_check(d, s):
    d.line([(24 * s, 66 * s), (52 * s, 94 * s), (106 * s, 36 * s)], fill=B, width=15 * s, joint="curve")
icono("check", ico_check)
def ico_mano(d, s):  # gesto deslizar: mano + flechas
    d.rounded_rectangle([50 * s, 30 * s, 72 * s, 92 * s], radius=11 * s, fill=B)
    d.rounded_rectangle([40 * s, 70 * s, 92 * s, 116 * s], radius=16 * s, fill=B)
    d.polygon([(8 * s, 40 * s), (28 * s, 26 * s), (28 * s, 54 * s)], fill=B); d.polygon([(120 * s, 40 * s), (100 * s, 26 * s), (100 * s, 54 * s)], fill=B)
icono("deslizar", ico_mano)
def ico_pellizco(d, s):
    for a in (45, 225):
        r = math.radians(a); cx, cy = 64 + 34 * math.cos(r), 64 + 34 * math.sin(r)
        d.ellipse([(cx - 13) * s, (cy - 13) * s, (cx + 13) * s, (cy + 13) * s], fill=B)
    d.line([(36 * s, 36 * s), (92 * s, 92 * s)], fill=B, width=6 * s)
    for (x, y, dx, dy) in [(20, 20, 1, 1), (108, 108, -1, -1)]:
        d.polygon([(x * s, y * s), ((x + dx * 22) * s, y * s), (x * s, (y + dy * 22) * s)], fill=B)
icono("pellizco", ico_pellizco)
def ico_estrella(d, s):
    pts = []
    for k in range(10):
        r = 54 if k % 2 == 0 else 22; a = math.radians(-90 + k * 36); pts.append(((64 + r * math.cos(a)) * s, (66 + r * math.sin(a)) * s))
    d.polygon(pts, fill=B)
icono("estrella", ico_estrella)
def ico_ubicacion(d, s):
    d.ellipse([30 * s, 12 * s, 98 * s, 80 * s], fill=B); d.polygon([(36 * s, 62 * s), (92 * s, 62 * s), (64 * s, 118 * s)], fill=B)
    d.ellipse([50 * s, 32 * s, 78 * s, 60 * s], fill=(0, 0, 0, 0))
icono("ubicacion", ico_ubicacion)
def ico_camara(d, s):
    d.rounded_rectangle([10 * s, 36 * s, 118 * s, 106 * s], radius=14 * s, outline=B, width=9 * s)
    d.rectangle([40 * s, 22 * s, 76 * s, 40 * s], fill=B)
    d.ellipse([42 * s, 48 * s, 86 * s, 92 * s], outline=B, width=9 * s)
icono("camara", ico_camara)

# ---------- greca (franja repetible) ----------
W, H = 160, 48; im = lienzo(W, H); d = ImageDraw.Draw(im); s = SS
d.rectangle([0, 0, W * s, 5 * s], fill=OCRE + (255,)); d.rectangle([0, (H - 5) * s, W * s, H * s], fill=OCRE + (255,))
for k in range(2):
    x0 = k * 80
    p = [(x0 + 6, 38), (x0 + 6, 14), (x0 + 40, 14), (x0 + 40, 30), (x0 + 24, 30), (x0 + 24, 22)]
    d.line([(x * s, y * s) for x, y in p], fill=OCRE + (255,), width=5 * s)
    p = [(x0 + 46, 10), (x0 + 46, 34), (x0 + 74, 34), (x0 + 74, 18), (x0 + 60, 18), (x0 + 60, 26)]
    d.line([(x * s, y * s) for x, y in p], fill=OCRE + (255,), width=5 * s)
guardar(bajar(im, W, H), "greca.png")

# ---------- esquina del marco de escaneo ----------
W = 160; im = lienzo(W, W); d = ImageDraw.Draw(im); s = SS
d.line([(10 * s, 150 * s), (10 * s, 10 * s), (150 * s, 10 * s)], fill=(255, 255, 255, 255), width=12 * s, joint="curve")
d.line([(34 * s, 80 * s), (34 * s, 34 * s), (80 * s, 34 * s)], fill=OCRE + (255,), width=7 * s)
d.rectangle([46 * s, 46 * s, 60 * s, 60 * s], fill=OCRE + (255,))
guardar(bajar(im, W, W), "esquina_escaneo.png")

# ---------- emblema (sol estilizado) ----------
def emblema(tam, nombre):
    im = lienzo(tam, tam); d = ImageDraw.Draw(im); s = SS * tam / 256; c = 128
    for k in range(8):
        a = math.radians(k * 45 - 90)
        p = [(c + 120 * math.cos(a), c + 120 * math.sin(a)), (c + 78 * math.cos(a + 0.22), c + 78 * math.sin(a + 0.22)), (c + 78 * math.cos(a - 0.22), c + 78 * math.sin(a - 0.22))]
        d.polygon([(x * s, y * s) for x, y in p], fill=OCRE + (255,))
    d.ellipse([(c - 82) * s, (c - 82) * s, (c + 82) * s, (c + 82) * s], fill=OBS + (255,), outline=OCRE + (255,), width=int(8 * s))
    d.ellipse([(c - 62) * s, (c - 62) * s, (c + 62) * s, (c + 62) * s], outline=JADE_C + (255,), width=int(5 * s))
    for k in range(20):
        a = math.radians(k * 18)
        d.line([((c + 64 * math.cos(a)) * s, (c + 64 * math.sin(a)) * s), ((c + 76 * math.cos(a)) * s, (c + 76 * math.sin(a)) * s)], fill=OCRE + (255,), width=int(4 * s))
    # rostro esquemático
    d.rounded_rectangle([(c - 30) * s, (c - 36) * s, (c + 30) * s, (c + 34) * s], radius=int(12 * s), fill=OCRE + (255,))
    d.rectangle([(c - 22) * s, (c - 14) * s, (c - 8) * s, (c - 6) * s], fill=OBS + (255,)); d.rectangle([(c + 8) * s, (c - 14) * s, (c + 22) * s, (c - 6) * s], fill=OBS + (255,))
    d.rectangle([(c - 4) * s, (c - 6) * s, (c + 4) * s, (c + 10) * s], fill=OBS + (255,))
    d.polygon([((c - 8) * s, (c + 16) * s), ((c + 8) * s, (c + 16) * s), (c * s, (c + 46) * s)], fill=TERRA + (255,))
    guardar(bajar(im, tam, tam), nombre)
emblema(256, "emblema.png")

# ---------- fondo de la pantalla de inicio ----------
W, H = 1080, 1920
yy = np.linspace(0, 1, H)[:, None, None]
fondo = np.array(PIEDRA)[None, None, :] * (1 - yy) * 0.9 + np.array(OBS)[None, None, :] * (0.4 + 0.6 * yy)
rng = np.random.default_rng(3)
fondo = fondo * (1 + 0.05 * cv2.GaussianBlur(rng.standard_normal((H, W)), (0, 0), 2)[..., None])
fondo = Image.fromarray(np.clip(fondo, 0, 255).astype(np.uint8)).convert("RGBA")
ren = Image.open(os.path.join(RENDERS, "render_piedra_sol.png")).convert("RGBA"); ren = ren.crop(ren.getbbox()).resize((1500, 1500), Image.LANCZOS)
g = cv2.cvtColor(np.asarray(ren)[..., :3], cv2.COLOR_RGB2GRAY)
bordes = cv2.Canny(cv2.GaussianBlur(g, (0, 0), 2), 30, 80)
bordes = cv2.dilate(bordes, np.ones((2, 2), np.uint8))
capa = np.zeros((1500, 1500, 4), np.uint8); capa[..., :3] = OCRE; capa[..., 3] = (bordes > 0) * 34
capa = Image.fromarray(capa, "RGBA")
fondo.alpha_composite(capa, (W // 2 - 750, 120))
# viñeta
v = np.zeros((H, W, 4), np.uint8); yv, xv = np.mgrid[0:H, 0:W]
r = np.sqrt(((xv - W / 2) / (W * 0.7)) ** 2 + ((yv - H * 0.45) / (H * 0.65)) ** 2)
v[..., 3] = np.clip((r - 0.6) * 300, 0, 200).astype(np.uint8)
fondo.alpha_composite(Image.fromarray(v, "RGBA"))
fondo.convert("RGB").save(os.path.join(OUT, "fondo_inicio.jpg"), quality=90)

# ---------- insignias de piezas (circulares) y versión bloqueada ----------
for archivo, nombre in [("render_piedra_sol.png", "piedra_sol"), ("render_cabeza_olmeca.png", "cabeza_olmeca"),
                        ("render_pakal.png", "pakal"), ("render_chac_mool.png", "chac_mool")]:
    T = 256; ren = Image.open(os.path.join(RENDERS, archivo)).convert("RGBA"); ren = ren.crop(ren.getbbox()); ren.thumbnail((190, 190), Image.LANCZOS)
    for bloqueada in (False, True):
        im = lienzo(T, T); d = ImageDraw.Draw(im); s = SS
        d.ellipse([6 * s, 6 * s, (T - 6) * s, (T - 6) * s], fill=(PIEDRA if not bloqueada else OBS) + (255,), outline=(OCRE if not bloqueada else (90, 80, 70)) + (255,), width=8 * s)
        r2 = ren.resize((ren.width * s, ren.height * s), Image.LANCZOS)
        if bloqueada:
            a = np.asarray(r2).copy(); a[..., :3] = 70; r2 = Image.fromarray(a, "RGBA")
        im.alpha_composite(r2, ((T * s - r2.width) // 2, (T * s - r2.height) // 2))
        guardar(bajar(im, T, T), f"insignia_{nombre}{'_bloq' if bloqueada else ''}.png")
print("ok", len(os.listdir(OUT)), "archivos")
