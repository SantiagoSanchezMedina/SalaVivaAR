"""Genera el mapa de altura, el color y el mapa de normales de la Piedra del Sol.

Es una versión estilizada (no una réplica fotogramétrica) basada en la composición real:
rostro central, Nahui Ollin con los cuatro soles, anillo de los 20 días, banda de quincunces,
8 rayos solares, banda de estrellas, dos Xiuhcóatl con el glifo 13 Ácatl arriba y el borde.
Uso: python gen_piedra_sol.py <carpeta_salida>
"""
import sys, os, math
import numpy as np
from PIL import Image
from scipy import ndimage

N = 2048
out = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(out, exist_ok=True)
rng = np.random.default_rng(1479)

# Coordenadas: x a la derecha, y hacia arriba, radio 1 = borde de la piedra
lin = (np.arange(N) + 0.5) / N * 2 - 1
X, Y = np.meshgrid(lin / 0.985, -lin / 0.985)
R = np.hypot(X, Y)
T = np.degrees(np.arctan2(Y, X))          # -180..180, 0 = derecha, 90 = arriba
DISC = R <= 1.0

H = np.full((N, N), 0.0)
H[DISC] = 0.38

def ring(r0, r1):
    return (R >= r0) & (R < r1)

def angdiff(a, b):
    return (a - b + 180) % 360 - 180

def raise_to(mask, h):
    np.maximum(H, np.where(mask, h, 0), out=H)

def set_to(mask, h):
    H[mask] = h

def circle(cx, cy, rad):
    return np.hypot(X - cx, Y - cy) < rad

def ellipse(cx, cy, ax, ay):
    return ((X - cx) / ax) ** 2 + ((Y - cy) / ay) ** 2 < 1

def rot_rect(cx, cy, w, h, ang_deg):
    a = math.radians(ang_deg)
    dx, dy = X - cx, Y - cy
    u = dx * math.cos(a) + dy * math.sin(a)
    v = -dx * math.sin(a) + dy * math.cos(a)
    return (np.abs(u) < w / 2) & (np.abs(v) < h / 2)

def polar_cell(r0, r1, a_center, half_width_deg):
    return ring(r0, r1) & (np.abs(angdiff(T, a_center)) < half_width_deg)

def lines_between_cells(r0, r1, n, offset=0.0, width_deg=0.9):
    m = np.zeros_like(DISC)
    for k in range(n):
        m |= ring(r0, r1) & (np.abs(angdiff(T, offset + k * 360 / n)) < width_deg)
    return m

# ---------- 8. Borde exterior ----------
raise_to(ring(0.945, 1.0), 0.55)
for k in range(48):
    a = math.radians(k * 7.5 + 3.75)
    set_to(circle(0.972 * math.cos(a), 0.972 * math.sin(a), 0.010), 0.45)

# ---------- 7. Dos Xiuhcóatl (serpientes de fuego) ----------
raise_to(ring(0.665, 0.875), 0.5)
for side in (1, -1):
    for k in range(15):
        base_a = 80 - k * 11.0
        a_c = base_a if side == 1 else 180 - base_a
        a_c = ((a_c + 180) % 360) - 180
        hw = 4.6 * (1 - 0.25 * k / 14)                           # el cuerpo se adelgaza hacia la cola
        raise_to(polar_cell(0.675, 0.865, a_c, hw), 0.72)
        set_to(polar_cell(0.70, 0.84, a_c, hw * 0.55), 0.6)
        raise_to(polar_cell(0.72, 0.82, a_c, 0.8), 0.75)
        raise_to(polar_cell(0.745, 0.795, a_c, hw * 0.35), 0.74)
        for f in (-0.45, 0.45):                                  # dos llamas por segmento
            fa = a_c + f * hw
            tri = ring(0.865, 0.94) & (np.abs(angdiff(T, fa)) < 2.6 * (0.94 - R) / 0.075)
            raise_to(tri, 0.7)
# cabezas de las serpientes abajo, de perfil, con las fauces abiertas mirándose
for side in (1, -1):
    hx = side * 0.13
    raise_to(ellipse(hx, -0.79, 0.07, 0.075), 0.78)                         # cráneo
    raise_to(rot_rect(hx - side * 0.07, -0.755, 0.09, 0.035, side * -10), 0.8)  # mandíbula superior
    raise_to(rot_rect(hx - side * 0.065, -0.845, 0.08, 0.03, side * 12), 0.8)   # mandíbula inferior
    set_to(circle(hx + side * 0.01, -0.765, 0.016), 0.56)                   # ojo
    raise_to(circle(hx + side * 0.01, -0.765, 0.006), 0.82)
    raise_to(rot_rect(hx - side * 0.105, -0.775, 0.008, 0.03, 0), 0.82)     # colmillo
    for c in range(3):                                                      # ceja de llamas
        raise_to(rot_rect(hx + side * (0.02 - c * 0.025), -0.715, 0.018, 0.03, side * 20), 0.76)
# rostros humanos que salen de las fauces
for side in (1, -1):
    raise_to(ellipse(side * 0.032, -0.80, 0.028, 0.04), 0.84)
    set_to(circle(side * 0.032, -0.79, 0.006), 0.62)
    raise_to(rot_rect(side * 0.032, -0.83, 0.02, 0.006, 0), 0.86)
# glifo 13 Ácatl arriba, entre las colas
raise_to(rot_rect(0, 0.79, 0.19, 0.16, 0), 0.76)
set_to(rot_rect(0, 0.79, 0.16, 0.13, 0), 0.56)
raise_to(rot_rect(0, 0.805, 0.03, 0.08, 0), 0.76)              # caña (ácatl)
for i in range(13):
    px = -0.055 + (i % 7) * 0.0183
    py = 0.84 if i < 7 else 0.765
    if i >= 7:
        px = -0.046 + (i - 7) * 0.0183
    raise_to(circle(px, py, 0.0065), 0.78)

# ---------- 6. Banda de estrellas ----------
raise_to(ring(0.625, 0.66), 0.68)
for k in range(64):
    a = math.radians(k * 360 / 64)
    set_to(circle(0.6425 * math.cos(a), 0.6425 * math.sin(a), 0.0075), 0.5)

# ---------- 5. Rayos solares ----------
for k in range(8):
    a_c = k * 45
    tri = ring(0.415, 0.62) & (np.abs(angdiff(T, a_c)) < 10.5 * (0.62 - R) / 0.205)
    raise_to(tri, 0.76)
    inner = ring(0.44, 0.59) & (np.abs(angdiff(T, a_c)) < 6.0 * (0.59 - R) / 0.15)
    set_to(inner, 0.6)
    raise_to(ring(0.46, 0.57) & (np.abs(angdiff(T, a_c)) < 1.0), 0.74)
    # espinas pequeñas entre rayos
    small = ring(0.415, 0.52) & (np.abs(angdiff(T, a_c + 22.5)) < 5.0 * (0.52 - R) / 0.105)
    raise_to(small, 0.7)
# plumas en la base de los rayos
feathers = ring(0.415, 0.455)
raise_to(feathers & (np.cos(np.radians(T) * 64) > 0.2), 0.62)

# ---------- 4. Banda de quincunces ----------
raise_to(ring(0.365, 0.41), 0.66)
set_to(lines_between_cells(0.365, 0.41, 40, 4.5, 0.5), 0.5)
for k in range(40):
    a_c = math.radians(k * 9)
    cx, cy = 0.3875 * math.cos(a_c), 0.3875 * math.sin(a_c)
    for ox, oy in ((0, 0), (0.009, 0.009), (-0.009, 0.009), (0.009, -0.009), (-0.009, -0.009)):
        set_to(circle(cx + ox, cy + oy, 0.0045), 0.52)

# ---------- 3. Anillo de los 20 días ----------
raise_to(ring(0.285, 0.36), 0.5)
raise_to(lines_between_cells(0.285, 0.36, 20, 0, 0.8), 0.7)
raise_to(ring(0.285, 0.292) | ring(0.353, 0.36), 0.7)
for k in range(20):
    a_c = k * 18 + 9
    ar = math.radians(a_c)
    cx, cy = 0.3225 * math.cos(ar), 0.3225 * math.sin(ar)
    # glifo pseudoaleatorio pero fijo: cabeza/círculo + detalles
    raise_to(circle(cx, cy, 0.018 + 0.006 * rng.random()), 0.72)
    for j in range(3):
        ox, oy = rng.uniform(-0.018, 0.018, 2)
        if rng.random() < 0.5:
            set_to(circle(cx + ox, cy + oy, 0.006), 0.56)
        else:
            raise_to(rot_rect(cx + ox, cy + oy, 0.02, 0.006, rng.uniform(0, 180)), 0.76)

# ---------- 2. Nahui Ollin y los cuatro soles ----------
raise_to(ring(0.265, 0.285), 0.7)
raise_to(R < 0.265, 0.45)
for k, a_c in enumerate((45, 135, 225, 315)):
    ar = math.radians(a_c)
    cx, cy = 0.185 * math.cos(ar), 0.185 * math.sin(ar)
    raise_to(rot_rect(cx, cy, 0.11, 0.11, 0), 0.74)
    set_to(rot_rect(cx, cy, 0.088, 0.088, 0), 0.55)
    raise_to(circle(cx, cy, 0.022), 0.76)                        # glifo de cada sol
    set_to(circle(cx, cy, 0.01), 0.6)
    for d in range(4):                                           # puntos numerales
        ox = -0.03 + d * 0.02
        raise_to(circle(cx + ox, cy - 0.034, 0.005), 0.76)
# garras a los lados
for side in (1, -1):
    raise_to(ellipse(side * 0.185, 0.0, 0.05, 0.035), 0.74)
    for c in range(4):
        raise_to(rot_rect(side * (0.165 + c * 0.012), -0.04, 0.008, 0.04, 0), 0.76)
    set_to(circle(side * 0.185, 0.0, 0.012), 0.58)
# glifos pequeños arriba/abajo del rostro
raise_to(rot_rect(0, 0.185, 0.05, 0.05, 45), 0.7)
raise_to(rot_rect(0, -0.205, 0.035, 0.035, 45), 0.7)

# ---------- 1. Rostro central (Tonatiuh / Tlaltecuhtli) ----------
face = R < 0.115
H[face] = 0.74 + 0.16 * (1 - (R[face] / 0.115) ** 2)
raise_to(rot_rect(0, 0.085, 0.13, 0.03, 0), 0.86)                # diadema
for side in (1, -1):
    set_to(ellipse(side * 0.037, 0.028, 0.017, 0.010), 0.6)       # ojos
    raise_to(circle(side * 0.037, 0.028, 0.0045), 0.82)
    raise_to(ellipse(side * 0.037, 0.047, 0.022, 0.005), 0.92)   # cejas
    raise_to(circle(side * 0.105, -0.01, 0.022), 0.86)            # orejeras
    set_to(circle(side * 0.105, -0.01, 0.009), 0.66)
raise_to(rot_rect(0, 0.005, 0.016, 0.04, 0), 0.95)                # nariz
set_to(ellipse(0, -0.045, 0.035, 0.012), 0.6)                     # boca
for t in range(-2, 3):
    raise_to(rot_rect(t * 0.012, -0.041, 0.006, 0.008, 0), 0.8)   # dientes
tongue = (Y < -0.045) & (Y > -0.15) & (np.abs(X) < 0.014 * (Y + 0.15) / 0.105)
raise_to(tongue, 0.93)                                            # lengua-cuchillo

# ---------- Desgaste de la piedra ----------
H = ndimage.gaussian_filter(H, 1.6)
noise_big = ndimage.gaussian_filter(rng.standard_normal((N, N)), 40)
noise_big /= np.abs(noise_big).max()
noise_small = ndimage.gaussian_filter(rng.standard_normal((N, N)), 1.2)
noise_small /= np.abs(noise_small).max()
pits = ndimage.gaussian_filter((rng.random((N, N)) > 0.9985).astype(float), 2.5)
pits /= pits.max()
H = H + 0.025 * noise_big + 0.018 * noise_small - 0.12 * pits
H[~DISC] = 0.0
H = np.clip(H, 0, 1)

# ---------- Exportar ----------
Image.fromarray((H * 65535).astype(np.uint16)).save(os.path.join(out, "PiedraSol_altura.png"))

# Color: basalto gris con huecos más oscuros (oclusión falsa) y vetas
cavity = H - ndimage.gaussian_filter(H, 6)
shade = np.clip(0.78 + 2.2 * cavity + 0.35 * (H - 0.5), 0.35, 1.15)
base = np.array([0.43, 0.42, 0.40])
tone = 1 + 0.10 * noise_big[..., None] + 0.06 * noise_small[..., None]
col = np.clip(base * shade[..., None] * tone, 0, 1)
col[~DISC] = [0.25, 0.25, 0.25]
Image.fromarray((col * 255).astype(np.uint8)).save(os.path.join(out, "PiedraSol_color.png"))

# Normal (formato OpenGL, el que usa Unity)
strength = 18.0
gy, gx = np.gradient(H)
nx, ny, nz = -gx * strength, gy * strength, np.ones_like(H)
ln = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
nrm = np.stack([nx / ln, ny / ln, nz / ln], -1) * 0.5 + 0.5
Image.fromarray((nrm * 255).astype(np.uint8)).save(os.path.join(out, "PiedraSol_normal.png"))

# Vista previa con luz rasante para revisar
light = np.array([-0.6, 0.6, 0.55]); light /= np.linalg.norm(light)
lam = np.clip((nrm * 2 - 1) @ light, 0, 1)
prev = np.clip(col * (0.35 + 0.9 * lam[..., None]), 0, 1)
Image.fromarray((prev * 255).astype(np.uint8)).resize((1024, 1024)).save(os.path.join(out, "PiedraSol_preview.png"))
print("ok")
