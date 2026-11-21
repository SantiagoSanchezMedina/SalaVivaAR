"""Cabeza colosal olmeca: malla 3D completa (360°) + textura, generada desde la foto frontal.

- Volumen: superelipsoide (bloque redondeado) con las proporciones medidas en las fotos de apoyo,
  base plana como la pieza real.
- Rostro: relieve tallado sobre el frente (casco, ceño, párpados, nariz ancha, labios gruesos,
  mejillas, mentón) ubicado sobre los rasgos de la foto + detalle fino de la foto.
- Banda del casco alrededor de toda la cabeza y orejeras a los lados.
- Textura: foto proyectada de frente, mezclada con basalto procedural (poroso) en lados y atrás.
Salida: Olmeca_malla.npz (vértices, caras, UV), Olmeca_color.png, Olmeca_normal.png, vista previa.
Uso: python gen_olmeca.py <foto_frente> <carpeta_salida>
"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

foto, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
rng = np.random.default_rng(6)

ALTO, ANCHO, FONDO = 1.65, 1.50, 1.35          # m (aprox. Cabeza 6 de San Lorenzo, MNA)
A, B = ANCHO / 2, FONDO / 2
C = 0.88; ZC = 0.80                              # semialtura y centro; abajo se aplana en z=0
PH, PV = 2.5, 3.2                                # exponentes de superelipse (horizontal / vertical)

# ---------- foto frontal (coordenadas medidas en el recorte 520x560) ----------
foto_im = Image.open(foto).convert("RGB").crop((165, 110, 425, 390)).resize((520, 560), Image.LANCZOS)
F = np.asarray(foto_im).astype(float) / 255
FX0, FX1, FY0, FY1 = 20, 495, 20, 510            # silueta de la cabeza en el recorte
mx = (FX0 + FX1) / 2
sat = F.max(-1) - F.min(-1)
es_piedra = ndimage.binary_opening((sat < 0.12) & (F.mean(-1) > 0.35), iterations=2)
es_piedra = ndimage.gaussian_filter(es_piedra.astype(float), 3)

def a_foto(x, z):
    """(x, z) en metros del frente -> (px, py) en el recorte."""
    px = mx + x / A * (FX1 - FX0) / 2
    py = FY0 + (ALTO - z) / ALTO * (FY1 - FY0)
    return px, py

def muestrear(img, px, py):
    h, w = img.shape[:2]
    px = np.clip(px, 0, w - 1.001); py = np.clip(py, 0, h - 1.001)
    x0 = px.astype(int); y0 = py.astype(int); fx = px - x0; fy = py - y0
    if img.ndim == 3:
        fx = fx[..., None]; fy = fy[..., None]
    return (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy)
            + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)

# ---------- relieve del rostro en coordenadas de la foto ----------
yy, xx = np.mgrid[0:560, 0:520].astype(float)
def g(cx, cy, sx, sy, amp):
    return amp * np.exp(-(((xx - cx) / sx) ** 2 + ((yy - cy) / sy) ** 2) / 2)
R = np.zeros((560, 520))
banda = np.clip((yy - 115) / 12, 0, 1) * np.clip((234 - yy) / 10, 0, 1)
R += 0.030 * banda                                            # banda frontal del casco
R += g(258, 230, 260, 7, 0.035)                               # borde del casco sobre el ceño
R -= g(175, 275, 50, 26, 0.060) + g(365, 275, 50, 26, 0.060)  # cuencas
R += g(175, 282, 40, 13, 0.050) + g(365, 282, 40, 13, 0.050)  # párpados/ojos
R += g(175, 255, 55, 9, 0.020) + g(365, 255, 55, 9, 0.020)    # pliegue superior
R += g(262, 305, 30, 32, 0.080)                               # puente de la nariz
R += g(262, 352, 52, 34, 0.190)                               # nariz ancha
R -= g(218, 370, 15, 11, 0.060) + g(306, 370, 15, 11, 0.060)  # fosas nasales
R += g(140, 395, 65, 70, 0.070) + g(385, 395, 65, 70, 0.070)  # mejillas
R += g(265, 418, 58, 20, 0.150)                               # labio superior
R += g(265, 463, 48, 20, 0.130)                               # labio inferior
R -= g(265, 441, 58, 5, 0.060)                                # línea de la boca
R += g(265, 500, 60, 26, 0.050)                               # mentón
L = F @ np.array([0.299, 0.587, 0.114])
hp = ndimage.gaussian_filter(L, 1.2) - ndimage.gaussian_filter(L, 12)
R += 0.010 * np.clip(hp / hp.std(), -3, 3) / 3 * es_piedra   # detalle de la foto
R = ndimage.gaussian_filter(R, 1.5)

# ---------- forma base ----------
def forma(theta, phi):
    """theta: 0 = frente (-Y), crece hacia la derecha de la pieza; phi: 0 arriba, pi abajo."""
    dx, dy, dz = np.sin(phi) * np.sin(theta), -np.sin(phi) * np.cos(theta), np.cos(phi)
    # superelipse: primero en el plano horizontal, luego vertical
    rh = (np.abs(np.cos(theta)) ** PH + np.abs(np.sin(theta)) ** PH) ** (-1 / PH)
    rv = (np.abs(np.sin(phi)) ** PV + np.abs(np.cos(phi)) ** PV) ** (-1 / PV)
    x = A * rv * np.sin(phi) * rh * np.sin(theta)
    y = -B * rv * np.sin(phi) * rh * np.cos(theta)
    z = ZC + C * rv * np.cos(phi)
    return x, y, z

NT, NP = 256, 176
th = np.linspace(-math.pi, math.pi, NT + 1)          # costura atrás; columna duplicada para UV
ph = np.linspace(0.0, math.pi, NP + 1)
TH, PHI = np.meshgrid(th, ph)                         # (NP+1, NT+1)
X, Y, Z = forma(TH, PHI)

# normal aproximada por diferencias
def normales(X, Y, Z):
    P = np.stack([X, Y, Z], -1)
    dt = np.roll(P, -1, 1) - np.roll(P, 1, 1)
    dp = np.roll(P, -1, 0) - np.roll(P, 1, 0)
    n = np.cross(dp, dt)
    n /= np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9
    return n
N0 = normales(X, Y, Z)
frente = np.clip((-N0[..., 1] - 0.25) / 0.45, 0, 1) ** 1.3       # cuánto mira al frente

px, py = a_foto(X, Z)
rel = muestrear(R, px, py) * frente
# banda del casco alrededor (atrás y lados) y orejeras
z_band = ZC + 0.36
anillo = np.exp(-((Z - z_band) / 0.06) ** 2 / 2) * (1 - frente)
rel += 0.03 * anillo
lado = np.exp(-((np.abs(TH) - math.pi / 2) / 0.18) ** 2 / 2) * np.exp(-((Z - (ZC - 0.05)) / 0.28) ** 4 / 2)
rel += 0.045 * lado
# poros/irregularidad suave de la piedra en toda la cabeza
ruido = ndimage.gaussian_filter(rng.standard_normal((NP + 1, NT + 1)), 3, mode="wrap")
rel += 0.012 * ruido / np.abs(ruido).max()

X = X + N0[..., 0] * rel; Y = Y + N0[..., 1] * rel; Z = Z + N0[..., 2] * rel
Z = np.maximum(Z, 0.0)                                            # base plana

# ---------- malla ----------
verts = np.stack([X, Y, Z], -1).reshape(-1, 3)
U = (TH + math.pi) / (2 * math.pi); V = 1 - PHI / math.pi
uvs = np.stack([U, V], -1).reshape(-1, 2)
idx = lambda i, j: i * (NT + 1) + j
faces = []
for i in range(NP):
    for j in range(NT):
        faces.append((idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)))
faces = np.array(faces, dtype=np.int32)
np.savez_compressed(os.path.join(out, "Olmeca_malla.npz"), verts=verts.astype(np.float32),
                    faces=faces, uvs=uvs.astype(np.float32))

# ---------- textura (UV cilíndrica) ----------
TW, TH_ = 2048, 1024
tu = (np.arange(TW) + 0.5) / TW; tv = (np.arange(TH_) + 0.5) / TH_
TU, TV = np.meshgrid(tu, tv)
t_theta = TU * 2 * math.pi - math.pi; t_phi = TV * math.pi            # fila 0 = arriba
tx, ty, tz = forma(t_theta, t_phi)
tn = normales(tx, ty, tz)
w_frente = np.clip((-tn[..., 1] - 0.35) / 0.4, 0, 1)
fpx, fpy = a_foto(tx, tz)
col_foto = muestrear(F, fpx, fpy)
w = w_frente * muestrear(es_piedra, fpx, fpy)
w = ndimage.gaussian_filter(w, 4)
# basalto procedural con el tono de la foto
tono = F[es_piedra > 0.8].mean(0)
n1 = ndimage.gaussian_filter(rng.standard_normal((TH_, TW)), 18, mode="wrap"); n1 /= np.abs(n1).max()
n2 = ndimage.gaussian_filter(rng.standard_normal((TH_, TW)), 1.2, mode="wrap"); n2 /= np.abs(n2).max()
poros = ndimage.gaussian_filter((rng.random((TH_, TW)) > 0.994).astype(float), 1.3, mode="wrap")
poros /= poros.max()
piedra = tono * (1 + 0.10 * n1 + 0.12 * n2)[..., None] * (1 - 0.45 * poros)[..., None]
color = w[..., None] * col_foto + (1 - w[..., None]) * piedra
color[t_phi > math.pi * 0.97] = tono * 0.6                             # base
Image.fromarray((np.clip(color, 0, 1) * 255).astype(np.uint8)).save(os.path.join(out, "Olmeca_color.png"))

# normal de detalle (poros + textura de la foto) en espacio tangente
alt = 0.6 * n2 - 1.2 * poros + 0.8 * w * np.clip(
    (muestrear(L, fpx, fpy) - ndimage.gaussian_filter(muestrear(L, fpx, fpy), 6)) * 8, -1, 1)
gy, gx = np.gradient(ndimage.gaussian_filter(alt, 0.8))
s = 1.2
nm = np.stack([-gx * s, gy * s, np.ones_like(gx)], -1); nm /= np.linalg.norm(nm, axis=-1, keepdims=True)
Image.fromarray(((nm * 0.5 + 0.5) * 255).astype(np.uint8)).save(os.path.join(out, "Olmeca_normal.png"))

# ---------- vista previa rápida (raster con orden de pintor) ----------
def vista(rot_deg, nombre):
    a = math.radians(rot_deg)
    vx = verts[:, 0] * math.cos(a) - verts[:, 1] * math.sin(a)
    vy = verts[:, 0] * math.sin(a) + verts[:, 1] * math.cos(a)
    vz = verts[:, 2]
    S = 520; esc = S / 2.0
    sx = S / 2 + vx * esc; sy = S - 20 - vz * esc
    tri_c = color[(np.clip((1 - uvs[faces[:, 0], 1]) * TH_, 0, TH_ - 1)).astype(int),
                  (np.clip(uvs[faces[:, 0], 0] * TW, 0, TW - 1)).astype(int)]
    p0 = np.stack([vx, vy, vz], -1)
    e1 = p0[faces[:, 1]] - p0[faces[:, 0]]; e2 = p0[faces[:, 3]] - p0[faces[:, 0]]
    fn = np.cross(e1, e2); fn /= np.linalg.norm(fn, axis=1, keepdims=True) + 1e-9
    luz = np.array([-0.4, -0.7, 0.55]); luz /= np.linalg.norm(luz)
    lam = np.clip(fn @ luz, 0, 1) * 0.85 + 0.2
    prof = vy[faces].mean(1)
    orden = np.argsort(-prof)
    img = Image.new("RGB", (S, S), (40, 40, 44)); d = ImageDraw.Draw(img)
    for k in orden:
        if fn[k, 1] > 0.05:
            continue
        q = faces[k]
        c = tuple(int(v) for v in np.clip(tri_c[k] * lam[k] * 255, 0, 255))
        d.polygon([(sx[q[0]], sy[q[0]]), (sx[q[1]], sy[q[1]]), (sx[q[2]], sy[q[2]]), (sx[q[3]], sy[q[3]])], fill=c)
    img.save(os.path.join(out, nombre))
vista(0, "Olmeca_preview_frente.png")
vista(40, "Olmeca_preview_34.png")
vista(95, "Olmeca_preview_lado.png")
print("ok", len(verts), "vértices", len(faces), "caras")
