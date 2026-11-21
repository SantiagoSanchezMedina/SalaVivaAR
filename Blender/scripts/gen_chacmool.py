"""Chac Mool (Chichén Itzá, Sala Maya del MNA) a partir de la foto de perfil — v2.

La figura se arma por partes trazadas sobre la foto (base, torso, cuello, cabeza girada al frente
con tocado y orejeras, brazos, plato, piernas). Cada silueta se "infla" en profundidad con un perfil
redondeado según el grosor real de la parte y se coloca a su distancia (brazo/pierna cercanos y lejanos).

Textura (v2): cada parte tiene su propia región en un atlas. La textura se calcula PÍXEL POR PÍXEL:
según hacia dónde mira ese punto de la superficie se mezcla, de forma suave, la foto (donde la
superficie mira de lado, que es lo que la foto ve) con basalto/caliza triplanar (donde mira al
frente, atrás, arriba o abajo). Así no hay cortes, rayas ni rombos.
Medidas de referencia: 1.48 m de largo x 1.10 m de alto (López Luján).
Uso: python gen_chacmool.py <foto> <carpeta_salida>
"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

foto, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
im0 = Image.open(foto).convert("RGB")
W0, H0 = im0.size
K = 2
W, H = W0 * K, H0 * K
S = 1.48 / 500                              # m por px original
DX = S / K                                  # m por px de trabajo
X0, Y0 = 300, 404
rng = np.random.default_rng(7)

def xz(px, py):
    return (px / K - X0) * S, (Y0 - py / K) * S

def poligono(puntos):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(x * K, y * K) for x, y in puntos], fill=255)
    return np.asarray(m) > 0

PIERNA = [(215, 215), (300, 205), (360, 178), (420, 146), (452, 142), (482, 156), (490, 182),
          (490, 300), (516, 318), (516, 333), (205, 338)]
BRAZO = [(148, 192), (212, 186), (226, 240), (300, 236), (304, 288), (232, 322), (205, 332), (150, 322), (138, 255)]
partes = {
    "torso": dict(poly=[(62, 192), (78, 172), (165, 166), (212, 182), (232, 212), (238, 262), (232, 305),
                        (205, 340), (78, 342), (60, 300), (58, 240)], yc=[0.0], hd=0.26),
    "cuello": dict(poly=[(80, 138), (160, 138), (166, 180), (76, 180)], yc=[0.0], hd=0.13),
    "cara": dict(poly=[(60, 74), (160, 74), (160, 132), (132, 150), (88, 150), (61, 132)], yc=[-0.02], hd=0.15, cabeza=True),
    "tocado": dict(poly=[(57, 38), (165, 38), (167, 80), (57, 80)], yc=[-0.02], hd=0.17, cabeza=True),
    "orejera_i": dict(poly=[(30, 60), (62, 58), (62, 122), (32, 118)], yc=[-0.02], hd=0.05, cabeza=True),
    "orejera_d": dict(poly=[(156, 58), (194, 64), (191, 122), (156, 122)], yc=[-0.02], hd=0.05, cabeza=True),
    "piernas": dict(poly=PIERNA, yc=[-0.125, 0.125], hd=0.13),
    "brazos": dict(poly=BRAZO, yc=[-0.25, 0.25], hd=0.075),
}

# ---------- foto corregida ----------
F = np.asarray(im0.resize((W, H), Image.LANCZOS)).astype(float) / 255
azul = ndimage.binary_dilation(F[..., 2] > F[..., 0] + 0.02, iterations=4)
ii_, jj_ = ndimage.distance_transform_edt(azul, return_distances=False, return_indices=True)
F = F[ii_, jj_]
Lm = F.mean(-1, keepdims=True)
F = F / np.maximum(ndimage.gaussian_filter(Lm, (25, 25, 0)), 0.08) * 0.42   # compensa la luz del museo
F = 0.75 * F + 0.25 * F.mean(-1, keepdims=True)
F = np.clip(F * np.array([0.95, 0.92, 0.9]), 0, 1)
Lf = F.mean(-1)
hp_foto = ndimage.gaussian_filter(Lf, 1.0) - ndimage.gaussian_filter(Lf, 8)

# ---------- piedra triplanar (continua en 3D) ----------
TAM = 1024; METROS = 0.8                      # una tesela de ruido cubre 0.8 m
n_big = ndimage.gaussian_filter(rng.standard_normal((TAM, TAM)), 40, mode="wrap"); n_big /= np.abs(n_big).max()
n_sml = ndimage.gaussian_filter(rng.standard_normal((TAM, TAM)), 1.4, mode="wrap"); n_sml /= np.abs(n_sml).max()
poros = ndimage.gaussian_filter((rng.random((TAM, TAM)) > 0.996).astype(float), 1.3, mode="wrap"); poros /= poros.max()
H_PIEDRA = 0.6 * n_sml - 1.0 * poros
tono = np.median(F[F.mean(-1) > 0.25], axis=0)

def muestrea_tesela(T, a, b):
    u = (a / METROS * TAM) % TAM; v = (b / METROS * TAM) % TAM
    u0 = np.floor(u).astype(int); v0 = np.floor(v).astype(int); fu = u - u0; fv = v - v0
    u1 = (u0 + 1) % TAM; v1 = (v0 + 1) % TAM
    return (T[v0, u0] * (1 - fu) * (1 - fv) + T[v0, u1] * fu * (1 - fv) + T[v1, u0] * (1 - fu) * fv + T[v1, u1] * fu * fv)

def triplanar(T, X, Y, Z, ax, ay, az):
    w = np.stack([ax, ay, az]) ** 4; w /= w.sum(0) + 1e-9
    return w[0] * muestrea_tesela(T, Y, Z) + w[1] * muestrea_tesela(T, X, Z) + w[2] * muestrea_tesela(T, X, Y)

def color_piedra(X, Y, Z, ax, ay, az):
    nb = triplanar(n_big, X, Y, Z, ax, ay, az)
    ns = triplanar(n_sml, X, Y, Z, ax, ay, az)
    po = triplanar(poros, X, Y, Z, ax, ay, az)
    return np.clip(tono * (1 + 0.08 * nb + 0.10 * ns)[..., None] * (1 - 0.35 * po)[..., None], 0, 1)

def suave(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

# ---------- calcular cada región de textura ----------
regiones = []          # (nombre, lado, rgb, altura, r0, c0)
info = {}
for nombre, p in partes.items():
    m = poligono(p["poly"])
    d = ndimage.distance_transform_edt(m)
    hd = p["hd"]
    sat = hd / DX * 0.9
    t = np.clip(d / sat, 0, 1)
    prof = np.where(m, hd * np.sqrt(np.clip(1 - (1 - t) ** 2, 0, 1)), 0)
    rows, cols = np.nonzero(m)
    r0, r1 = rows.min() - 6, rows.max() + 7; c0, c1 = cols.min() - 6, cols.max() + 7
    sub_m = m[r0:r1, c0:c1]; sub_p = ndimage.gaussian_filter(prof, 1.0)[r0:r1, c0:c1]
    gz_px, gx_px = np.gradient(sub_p)
    gx, gz = gx_px / DX, -gz_px / DX                    # pendiente en metros por metro
    ny = 1 / np.sqrt(1 + gx ** 2 + gz ** 2)
    ax, az = np.abs(gx) * ny, np.abs(gz) * ny
    jj = np.arange(c0, c1); ii = np.arange(r0, r1)
    JJ, II = np.meshgrid(jj, ii)
    X, Z = xz(JJ, II)
    Ysup = sub_p                                        # distancia al plano central de la parte
    piedra = color_piedra(X, Ysup, Z, ax, ny, az)
    h_piedra = triplanar(H_PIEDRA, X, Ysup, Z, ax, ny, az)
    w = suave(0.55, 0.88, ny)                           # foto solo donde la superficie mira de lado
    lados = ["frente", "atras"] if p.get("cabeza") else ["ambos"]
    for lado in lados:
        wl = w if lado != "atras" else np.zeros_like(w)
        rgb = wl[..., None] * F[r0:r1, c0:c1] + (1 - wl[..., None]) * piedra
        alt = wl * np.clip(hp_foto[r0:r1, c0:c1] * 6, -1, 1) + (1 - wl) * h_piedra
        # rellenar fuera de la silueta con el color del borde (evita sangrado en la textura)
        fuera = ~ndimage.binary_dilation(sub_m, iterations=2)
        idx = ndimage.distance_transform_edt(fuera, return_distances=False, return_indices=True)
        rgb = rgb[idx[0], idx[1]]; alt = alt[idx[0], idx[1]]
        regiones.append([nombre, lado, rgb, alt])
    info[nombre] = dict(prof=prof, m=m, r0=r0, c0=c0)

# región: franja frontal de la base (foto) y una tesela de piedra plana (base y plato)
b_r0, b_r1, b_c0, b_c1 = 345 * K, 404 * K, 58 * K, 557 * K
regiones.append(["base_frente", "ambos", F[b_r0:b_r1, b_c0:b_c1], np.clip(hp_foto[b_r0:b_r1, b_c0:b_c1] * 6, -1, 1)])
PP = 512
Xp, Zp = np.meshgrid(np.linspace(0, 0.8, PP), np.linspace(0, 0.8, PP))
regiones.append(["piedra", "ambos", color_piedra(Xp, np.zeros_like(Xp), Zp, np.zeros_like(Xp), np.ones_like(Xp), np.zeros_like(Xp)),
                 triplanar(H_PIEDRA, Xp, np.zeros_like(Xp), Zp, np.zeros_like(Xp), np.ones_like(Xp), np.zeros_like(Xp))])

# ---------- empaquetar en un atlas 2048x2048 (estantes) ----------
AT = 2048; MARGEN = 4
def empaquetar(escala):
    x = y = alto_fila = 0; pos = []
    for r in sorted(range(len(regiones)), key=lambda k: -regiones[k][2].shape[0]):
        h, w = (np.array(regiones[r][2].shape[:2]) * escala).astype(int) + MARGEN
        if x + w > AT:
            x = 0; y += alto_fila; alto_fila = 0
        pos.append((r, y, x)); x += w; alto_fila = max(alto_fila, h)
    return pos, y + alto_fila
escala = 1.6
while True:
    pos, alto = empaquetar(escala)
    if alto <= AT:
        break
    escala *= 0.95
atlas = np.zeros((AT, AT, 3)); atlas_h = np.zeros((AT, AT))
lugar = {}
for r, y, x in pos:
    nombre, lado, rgb, alt = regiones[r]
    h, w = (np.array(rgb.shape[:2]) * escala).astype(int)
    rgb_s = np.asarray(Image.fromarray((rgb * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS)).astype(float) / 255
    alt_s = np.asarray(Image.fromarray(alt.astype(np.float32)).resize((w, h), Image.BILINEAR))
    atlas[y:y + h, x:x + w] = rgb_s; atlas_h[y:y + h, x:x + w] = alt_s
    lugar[(nombre, lado)] = (y, x, rgb.shape[0], rgb.shape[1], h, w)
print("escala del atlas:", round(escala, 3))

def uv_de(nombre, lado, fila_local, col_local):
    y, x, h0, w0, h, w = lugar[(nombre, lado)]
    u = (x + (col_local + 0.5) * w / w0) / AT
    v = 1 - (y + (fila_local + 0.5) * h / h0) / AT
    return u, v

# ---------- malla ----------
verts, faces, uvs, plano = [], [], [], []
es_borde = []
PASO = 5
for nombre, p in partes.items():
    I = info[nombre]; m, prof, r0, c0 = I["m"], I["prof"], I["r0"], I["c0"]
    ii = np.arange(0, H, PASO); jj = np.arange(0, W, PASO)
    sub = m[np.ix_(ii, jj)]
    borde = ndimage.binary_dilation(sub) & ~sub
    usar = sub | borde
    for yc in p["yc"]:
        for signo in (-1, 1):
            lado = "ambos" if not p.get("cabeza") else ("frente" if signo == -1 else "atras")
            idx = -np.ones(sub.shape, dtype=np.int64)
            for a, b in zip(*np.nonzero(usar)):
                i, j = ii[a], jj[b]
                x, z = xz(j, i)
                dz = 0.0 if borde[a, b] else float(prof[i, j])
                idx[a, b] = len(verts)
                verts.append((x, yc + signo * dz, z))
                uvs.append(uv_de(nombre, lado, i - r0, j - c0))
                es_borde.append((bool(borde[a, b]), yc))
            for a in range(sub.shape[0] - 1):
                for b in range(sub.shape[1] - 1):
                    q = (idx[a, b], idx[a + 1, b], idx[a + 1, b + 1], idx[a, b + 1])
                    bq = (borde[a, b], borde[a + 1, b], borde[a + 1, b + 1], borde[a, b + 1])
                    validos = [k for k in range(4) if q[k] >= 0]
                    if len(validos) < 3 or all(bq[k] for k in validos):
                        continue
                    if len(validos) == 4:
                        tris_q = [(q[0], q[1], q[2]), (q[0], q[2], q[3])]
                    else:                              # esquina de la silueta: un triángulo
                        tris_q = [tuple(q[k] for k in validos)]
                    for t in tris_q:
                        faces.append(t if signo == -1 else (t[0], t[2], t[1])); plano.append(False)

# ---------- suavizado del contorno (quita el escalonado del borde) ----------
V = np.array(verts, dtype=np.float64); Fc = np.array(faces)
nb = len(V)
B = np.array([e[0] for e in es_borde]); YC = np.array([e[1] for e in es_borde])
vecinos = [set() for _ in range(nb)]
for t in Fc:
    for a_, b_ in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
        vecinos[a_].add(b_); vecinos[b_].add(a_)
vec_borde = [[n_ for n_ in vecinos[i] if B[n_]] for i in range(nb)]
vec_todos = [list(vecinos[i]) for i in range(nb)]
for it in range(8):                        # contorno: solo x,z, entre vértices del borde
    Vn = V.copy()
    for i in np.nonzero(B)[0]:
        if len(vec_borde[i]) >= 2:
            Vn[i, [0, 2]] = 0.5 * V[i, [0, 2]] + 0.5 * V[vec_borde[i]][:, [0, 2]].mean(0)
    V = Vn
for it in range(3):                        # interior: suavizado ligero de todo
    Vn = V.copy()
    for i in np.nonzero(~B)[0]:
        Vn[i] = 0.6 * V[i] + 0.4 * V[vec_todos[i]].mean(0)
    V = Vn
V[B, 1] = YC[B]
verts = [tuple(v) for v in V]

def uv_region(nombre, fu, fv):
    y, x, h0, w0, h, w = lugar[(nombre, "ambos")]
    return (x + 2 + fu * (w - 4)) / AT, 1 - (y + 2 + fv * (h - 4)) / AT

# base (caja): frente/atrás con la foto de la base, el resto con piedra
bx0, _ = xz(58 * K, 0); bx1, _ = xz(560 * K, 0); _, bz1 = xz(0, 326 * K)
pts = [(bx0, -0.34, 0), (bx1, -0.34, 0), (bx1, 0.34, 0), (bx0, 0.34, 0),
       (bx0, -0.34, bz1), (bx1, -0.34, bz1), (bx1, 0.34, bz1), (bx0, 0.34, bz1)]
caras = [((0, 1, 5, 4), "base_frente"), ((2, 3, 7, 6), "base_frente"), ((1, 2, 6, 5), "piedra"),
         ((3, 0, 4, 7), "piedra"), ((4, 5, 6, 7), "piedra"), ((3, 2, 1, 0), "piedra")]
for c, reg in caras:
    b0 = len(verts)
    for k, vi in enumerate(c):
        verts.append(pts[vi]); uvs.append(uv_region(reg, (0, 1, 1, 0)[k], (1, 1, 0, 0)[k]))
    faces += [(b0, b0 + 1, b0 + 2), (b0, b0 + 2, b0 + 3)]; plano += [True, True]

# plato sobre el vientre
cx, cz = xz(265 * K, 222 * K)
R_ext, R_int, alto = 0.13, 0.09, 0.07
n = 48; base_i = len(verts)
anillos = [(R_ext, cz - alto), (R_ext, cz), (R_int, cz), (R_int * 0.9, cz - alto * 0.6)]
for s, (r, z) in enumerate(anillos):
    for k in range(n):
        a = 2 * math.pi * k / n
        verts.append((cx + r * math.cos(a), r * math.sin(a), z))
        uvs.append(uv_region("piedra", 0.5 + 0.45 * math.cos(a) * r / R_ext, 0.5 + 0.45 * math.sin(a) * r / R_ext))
for s in range(len(anillos) - 1):
    for k in range(n):
        a0, a1 = base_i + s * n + k, base_i + s * n + (k + 1) % n
        b0, b1 = base_i + (s + 1) * n + k, base_i + (s + 1) * n + (k + 1) % n
        faces += [(a0, a1, b1), (a0, b1, b0)]; plano += [False, False]
centro = len(verts); verts.append((cx, 0.0, cz - alto * 0.6)); uvs.append(uv_region("piedra", 0.5, 0.5))
for k in range(n):
    faces.append((base_i + 3 * n + k, base_i + 3 * n + (k + 1) % n, centro)); plano.append(False)

verts = np.array(verts, dtype=np.float32); faces = np.array(faces, dtype=np.int32)
uvs = np.array(uvs, dtype=np.float32); plano = np.array(plano, dtype=bool)
np.savez_compressed(os.path.join(out, "ChacMool_malla.npz"), verts=verts, faces=faces, uvs=uvs, plano=plano)

# ---------- texturas ----------
Image.fromarray((np.clip(atlas, 0, 1) * 255).astype(np.uint8)).save(os.path.join(out, "ChacMool_color.png"))
gy, gx = np.gradient(ndimage.gaussian_filter(atlas_h, 0.8))
nm = np.stack([-gx * 1.5, gy * 1.5, np.ones_like(gx)], -1); nm /= np.linalg.norm(nm, axis=-1, keepdims=True)
Image.fromarray(((nm * 0.5 + 0.5) * 255).astype(np.uint8)).save(os.path.join(out, "ChacMool_normal.png"))

# ---------- vistas previas (color por vértice interpolado: más fiel que por cara) ----------
TEX = (np.clip(atlas, 0, 1) * 255).astype(np.uint8)
def vista(rot_deg, elev_deg, nombre):
    a, e = math.radians(rot_deg), math.radians(elev_deg)
    x = verts[:, 0] * math.cos(a) - verts[:, 1] * math.sin(a)
    y = verts[:, 0] * math.sin(a) + verts[:, 1] * math.cos(a)
    z = verts[:, 2]
    y2 = y * math.cos(e) + (z - 0.5) * math.sin(e); z2 = -y * math.sin(e) + (z - 0.5) * math.cos(e)
    Sp = 600; esc = Sp / 1.8
    sx = Sp / 2 + x * esc; sy = Sp / 2 - z2 * esc
    p = np.stack([x, y2, z2], -1)
    e1 = p[faces[:, 1]] - p[faces[:, 0]]; e2 = p[faces[:, 2]] - p[faces[:, 0]]
    fn = np.cross(e1, e2); fn /= np.linalg.norm(fn, axis=1, keepdims=True) + 1e-9
    luz = np.array([-0.4, -0.7, 0.6]); luz /= np.linalg.norm(luz)
    lam = np.abs(fn @ luz) * 0.8 + 0.25
    uvc = uvs[faces].mean(1)
    tc = TEX[np.clip(((1 - uvc[:, 1]) * AT).astype(int), 0, AT - 1), np.clip((uvc[:, 0] * AT).astype(int), 0, AT - 1)] / 255
    orden = np.argsort(-p[faces].mean(1)[:, 1])
    img = Image.new("RGB", (Sp, Sp), (40, 40, 44)); d = ImageDraw.Draw(img)
    for k in orden:
        q = faces[k]
        c = tuple(int(v) for v in np.clip(tc[k] * lam[k] * 255, 0, 255))
        d.polygon([(sx[i], sy[i]) for i in q], fill=c)
    img.save(os.path.join(out, nombre))
vista(0, 0, "ChacMool_preview_lado.png")
vista(-35, 15, "ChacMool_preview_34.png")
vista(90, 25, "ChacMool_preview_pies.png")
vista(180, 15, "ChacMool_preview_otro_lado.png")
print("ok", len(verts), "vértices", len(faces), "triángulos")
