"""Targets geométricos abstractos (tipo logotipo) para Sala Viva AR.
Cada pieza se construye con formas planas y escalonadas sobre una retícula (estética de grecas
mesoamericanas): muchas esquinas limpias que le sirven a Vuforia sin verse "sucio".
Tipografía serif clásica (GFS Baskerville + TeX Gyre Pagella).
Uso: python gen_geometricos.py <carpeta_salida>
"""
import sys, os, math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1] if len(sys.argv) > 1 else "geo"
os.makedirs(OUT, exist_ok=True)
K = 3
W, H = 1000, 1250
N, B = 0, 255
BASK = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrepagella-regular.otf"
PAG = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrepagella-regular.otf"
PAG_I = "/usr/share/texmf/fonts/opentype/public/tex-gyre/texgyrepagella-italic.otf"

class Lienzo:
    def __init__(self):
        self.im = Image.new("L", (W * K, H * K), B); self.d = ImageDraw.Draw(self.im)
    def poli(self, pts, col=N):
        self.d.polygon([(x * K, y * K) for x, y in pts], fill=col)
    def rect(self, x0, y0, x1, y1, col=N):
        self.d.rectangle([x0 * K, y0 * K, x1 * K, y1 * K], fill=col)
    def linea(self, pts, ancho, col=N):
        self.d.line([(x * K, y * K) for x, y in pts], fill=col, width=int(ancho * K), joint="curve")
    def texto(self, xy, s, ruta, tam, anchor="mm", espaciado=0):
        f = ImageFont.truetype(ruta, int(tam * K))
        if not espaciado:
            self.d.text((xy[0] * K, xy[1] * K), s, font=f, fill=N, anchor=anchor); return
        anchos = [f.getlength(c) for c in s]; total = sum(anchos) + espaciado * K * (len(s) - 1)
        x = xy[0] * K - total / 2
        for c, a in zip(s, anchos):
            self.d.text((x, xy[1] * K), c, font=f, fill=N, anchor="lm"); x += a + espaciado * K
    def final(self): return self.im.resize((W, H), Image.LANCZOS)

def reticula(L, x0, y0, u):
    """Devuelve funciones para dibujar en una retícula de celdas de tamaño u (y su espejo)."""
    P = lambda pts: [(x0 + x * u, y0 + y * u) for x, y in pts]
    E = lambda pts: [(24 - x, y) for x, y in pts]          # espejo horizontal (retícula de 24)
    return P, E

# ---------------- cabeza olmeca geométrica ----------------
def olmeca(L, x0, y0, u):
    P, E = reticula(L, x0, y0, u)
    # casco escalonado
    L.poli(P([(4, 9), (4, 5), (5, 5), (5, 3.5), (7, 3.5), (7, 2.5), (9.5, 2.5), (9.5, 1.5), (14.5, 1.5), (14.5, 2.5),
              (17, 2.5), (17, 3.5), (19, 3.5), (19, 5), (20, 5), (20, 9)]))
    L.poli(P([(4, 7.4), (20, 7.4), (20, 8.0), (4, 8.0)]), B)                       # banda del casco
    for x in (8.2, 15.0):                                                          # correas frontales
        L.poli(P([(x, 3.6), (x + .8, 3.6), (x + .8, 7.4), (x, 7.4)]), B)
    L.poli(P([(12, 3.2), (13.3, 4.8), (12, 6.4), (10.7, 4.8)]), B)                  # rombo central
    L.poli(P([(12, 4.1), (12.6, 4.8), (12, 5.5), (11.4, 4.8)]))
    for f in (lambda p: p, E):
        # orejeras escalonadas
        L.poli(P(f([(2.5, 9), (5.2, 9), (5.2, 15), (4.2, 15), (4.2, 16), (2.5, 16)])))
        L.poli(P(f([(3.2, 10.6), (4.5, 10.6), (4.5, 12.4), (3.2, 12.4)])), B)
        L.poli(P(f([(3.6, 11.1), (4.1, 11.1), (4.1, 11.9), (3.6, 11.9)])))
        # contorno de la mandíbula (banda gruesa escalonada)
        L.poli(P(f([(5.8, 9), (6.6, 9), (6.6, 16.2), (8, 18), (10, 19.4), (12, 19.4), (12, 20.4), (9.6, 20.4), (7.2, 18.8), (5.8, 16.6)])))
        # párpado pesado + ojo almendrado con ranura
        L.poli(P(f([(7.4, 10.4), (10.8, 10.0), (11.2, 10.6), (7.6, 11.0)])))
        L.poli(P(f([(7.6, 12.0), (8.6, 11.3), (10.4, 11.3), (11.2, 12.0), (10.4, 12.7), (8.6, 12.7)])))
        L.poli(P(f([(8.4, 11.85), (10.5, 11.85), (10.5, 12.15), (8.4, 12.15)])), B)
        # mejilla: surco diagonal
        L.poli(P(f([(8.9, 13.6), (9.5, 13.6), (8.4, 16.4), (7.8, 16.4)])))
        # comisura caída
        L.poli(P(f([(8.3, 16.6), (9.1, 16.5), (8.4, 17.7), (7.9, 17.6)])))
    # nariz ancha escalonada con fosas
    L.poli(P([(11, 11), (13, 11), (13, 12.8), (14.8, 13.8), (14.8, 15.2), (9.2, 15.2), (9.2, 13.8), (11, 12.8)]))
    for x in (10.2, 13.0):
        L.poli(P([(x, 14.1), (x + .8, 14.1), (x + .8, 14.7), (x, 14.7)]), B)
    # labios gruesos
    L.poli(P([(8.8, 16.6), (10.4, 15.9), (12, 16.2), (13.6, 15.9), (15.2, 16.6), (14.6, 17.0), (9.4, 17.0)]))
    L.poli(P([(9.4, 17.4), (14.6, 17.4), (13.6, 18.4), (10.4, 18.4)]))

def greca(L, x0, x1, y, alto, seed):
    """Franja de greca escalonada; cada módulo varía un poco para no repetirse igual."""
    rng = np.random.default_rng(seed)
    x = x0; g = alto * 0.16
    L.rect(x0, y, x1, y + g); L.rect(x0, y + alto - g, x1, y + alto)
    while x < x1 - alto * 0.6:
        m = alto * rng.uniform(1.0, 1.35)
        if x + m > x1: m = x1 - x
        h = alto - 2 * g
        tipo = rng.integers(0, 3)
        if tipo == 0:   # escalón
            L.linea([(x, y + alto - g), (x, y + g + h * .45), (x + m * .45, y + g + h * .45), (x + m * .45, y + g + h * .1),
                     (x + m * .8, y + g + h * .1)], g)
        elif tipo == 1: # espiral cuadrada
            L.linea([(x + m * .1, y + alto - g), (x + m * .1, y + g + h * .15), (x + m * .75, y + g + h * .15), (x + m * .75, y + g + h * .7),
                     (x + m * .38, y + g + h * .7), (x + m * .38, y + g + h * .42)], g)
        else:           # triángulo y punto
            L.poli([(x + m * .1, y + alto - g), (x + m * .5, y + g + h * .2), (x + m * .9, y + alto - g)])
            r = h * .12; L.d.ellipse([(x + m * .5 - r) * K, (y + g + h * .62 - r) * K, (x + m * .5 + r) * K, (y + g + h * .62 + r) * K], fill=B)
        x += m

def target_olmeca(seed=6):
    L = Lienzo()
    u = 34; tam = 24 * u
    olmeca(L, (W - tam) / 2, 70, u)
    greca(L, 90, W - 90, 815, 70, seed)
    L.texto((W / 2, 975), "Cabeza Colosal", BASK, 118)
    L.texto((W / 2, 1085), "OLMECA", PAG, 46, espaciado=22)
    L.texto((W / 2, 1160), "Sala Viva AR · Museo Nacional de Antropología", PAG_I, 30)
    return L.final()

def evaluar(g):
    g = cv2.resize(g, (g.shape[1] // 2, g.shape[0] // 2), interpolation=cv2.INTER_AREA)
    kp = cv2.FastFeatureDetector_create(threshold=40, nonmaxSuppression=True).detect(g, None)
    h, w = g.shape; n = 10; c = np.zeros((n, n), int)
    for k in kp: c[min(n - 1, int(k.pt[1] * n / h)), min(n - 1, int(k.pt[0] * n / w))] += 1
    return len(kp), int((c >= 8).sum()), round(float(g.std()), 1)


# ---------------- Piedra del Sol geométrica ----------------
def piedra_sol(L, x0, y0, u):
    P, E = reticula(L, x0, y0, u)
    c = lambda x, y: (x0 + x * u, y0 + y * u)
    def circ(r, col, cx=12, cy=11):
        X, Y = c(cx, cy); L.d.ellipse([(X - r * u) * K, (Y - r * u) * K, (X + r * u) * K, (Y + r * u) * K], fill=col)
    def anillo_rayos(n, r0, r1, ancho_ang, fase=0):
        for k in range(n):
            a = fase + k * 2 * math.pi / n
            pts = [(12 + r0 * math.cos(a - ancho_ang), 11 + r0 * math.sin(a - ancho_ang)), (12 + r1 * math.cos(a), 11 + r1 * math.sin(a)),
                   (12 + r0 * math.cos(a + ancho_ang), 11 + r0 * math.sin(a + ancho_ang))]
            L.poli(P(pts))
    circ(10.2, N); circ(9.3, B)
    anillo_rayos(8, 7.6, 10.0, 0.16, -math.pi / 2)                  # rayos grandes
    anillo_rayos(8, 7.6, 8.9, 0.09, -math.pi / 2 + math.pi / 8)     # rayos chicos
    circ(7.6, N); circ(6.9, B)
    for k in range(20):                                             # anillo de los 20 días (bloques)
        a = k * 2 * math.pi / 20; a1 = a + 2 * math.pi / 20 * 0.62
        L.poli(P([(12 + 6.6 * math.cos(a), 11 + 6.6 * math.sin(a)), (12 + 6.6 * math.cos(a1), 11 + 6.6 * math.sin(a1)),
                  (12 + 5.6 * math.cos(a1), 11 + 5.6 * math.sin(a1)), (12 + 5.6 * math.cos(a), 11 + 5.6 * math.sin(a))]))
    circ(5.2, N); circ(4.5, B)
    # Nahui Ollin: cuatro recuadros en diagonal
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        cx, cy = 12 + sx * 2.55, 11 + sy * 2.55
        L.poli(P([(cx - 1.05, cy - 1.05), (cx + 1.05, cy - 1.05), (cx + 1.05, cy + 1.05), (cx - 1.05, cy + 1.05)]))
        L.poli(P([(cx - .45, cy - .45), (cx + .45, cy - .45), (cx + .45, cy + .45), (cx - .45, cy + .45)]), B)
    # rostro central
    circ(2.05, N)
    for sx in (-1, 1):
        L.poli(P([(12 + sx * .55 - .35, 10.35), (12 + sx * .55 + .35, 10.35), (12 + sx * .55 + .35, 10.75), (12 + sx * .55 - .35, 10.75)]), B)
    L.poli(P([(11.45, 11.6), (12.55, 11.6), (12, 12.9)]), B)            # lengua-cuchillo
    L.poli(P([(11.75, 9.2), (12.25, 9.2), (12.25, 9.8), (11.75, 9.8)]), B)

# ---------------- Máscara de Pakal geométrica (mosaico) ----------------
def pakal(L, x0, y0, u, seed=3):
    P, E = reticula(L, x0, y0, u)
    rng = np.random.default_rng(seed)
    cara = [(5.2, 6.4), (6.4, 3.4), (9.2, 1.8), (12, 1.4), (14.8, 1.8), (17.6, 3.4), (18.8, 6.4), (19.0, 10), (18.2, 14),
            (16.4, 17.6), (14, 19.8), (12, 20.4), (10, 19.8), (7.6, 17.6), (5.8, 14), (5.0, 10)]
    L.poli(P(cara))
    # juntas del mosaico de jade: rejilla irregular de teselas grandes, en blanco
    nx, ny = 6, 8; gx = np.linspace(4.6, 19.4, nx + 1); gy = np.linspace(1.2, 20.6, ny + 1)
    V = np.array([[(x + rng.uniform(-.7, .7), y + rng.uniform(-.55, .55)) for x in gx] for y in gy])
    capa = Image.new("L", L.im.size, 0); dc = ImageDraw.Draw(capa)
    w = int(.24 * u * K)
    for j in range(ny + 1):
        for i in range(nx):
            if j in (0, ny) or rng.random() < .9: dc.line([(x * K, y * K) for x, y in P([V[j, i], V[j, i + 1]])], fill=255, width=w)
    for j in range(ny):
        for i in range(nx + 1):
            dc.line([(x * K, y * K) for x, y in P([V[j, i], V[j + 1, i]])], fill=255, width=w)
    m = Image.new("L", L.im.size, 0); ImageDraw.Draw(m).polygon([(x * K, y * K) for x, y in P(cara)], fill=255)
    from PIL import ImageChops
    L.im.paste(B, (0, 0), ImageChops.multiply(capa, m))
    # rasgos encima del mosaico: placas negras sólidas con ojos de concha
    for f in (lambda p: p, E):
        L.poli(P(f([(5.8, 7.2), (11.2, 6.6), (11.2, 11.4), (5.8, 11.2)])))                       # zona del ojo
        L.poli(P(f([(6.4, 9.3), (8.0, 8.0), (10.2, 8.1), (10.8, 9.3), (9.8, 10.4), (7.6, 10.4)])), B)  # ojo de concha
        pts = P(f([(8.7, 9.25)])); X, Y = pts[0]; r = .78 * u
        L.d.ellipse([(X - r) * K, (Y - r) * K, (X + r) * K, (Y + r) * K], fill=N)                 # iris de obsidiana
        L.poli(P(f([(6.0, 7.0), (11.0, 6.5), (11.0, 5.8), (6.2, 6.2)])))                        # ceja
    L.poli(P([(11.0, 6.6), (13.0, 6.6), (13.4, 13.4), (14.6, 14.6), (9.4, 14.6), (10.6, 13.4)]))    # nariz
    for x in (10.6, 12.8):
        L.poli(P([(x, 13.8), (x + .6, 13.8), (x + .6, 14.2), (x, 14.2)]), B)
    L.poli(P([(8.4, 15.6), (15.6, 15.6), (14.6, 18.2), (9.4, 18.2)]))                            # zona de la boca
    L.poli(P([(9.4, 16.6), (10.8, 16.0), (12, 16.3), (13.2, 16.0), (14.6, 16.6), (13.4, 17.3), (12, 17.4), (10.6, 17.3)]), B)
    L.poli(P([(10.4, 16.6), (13.6, 16.6), (13.0, 16.9), (11.0, 16.9)]))

# ---------------- Chac Mool geométrico ----------------
def chac_mool(L, x0, y0, u):
    P, E = reticula(L, x0, y0, u)
    sep = int(.32 * u * K)
    def parte(pts):          # pieza negra con contorno blanco para que se separen las partes del cuerpo
        L.d.polygon([(x * K, y * K) for x, y in P(pts)], fill=N, outline=B, width=sep)
    L.poli(P([(1, 18.6), (23, 18.6), (23, 20.0), (1, 20.0)]))                                   # base
    parte([(2.6, 18.9), (2.6, 16.6), (9.6, 16.6), (9.6, 18.9)])                                  # antebrazo
    parte([(2.6, 18.9), (2.6, 10.6), (5.0, 9.4), (5.0, 18.9)])                                   # brazo
    parte([(4.6, 10.0), (7.2, 8.8), (12.6, 14.6), (12.6, 18.9), (9.0, 18.9)])                    # torso
    parte([(15.6, 8.4), (18.2, 8.4), (17.4, 17.2), (15.0, 17.2)])                                # pantorrilla
    parte([(11.8, 16.0), (11.8, 13.4), (15.6, 8.2), (18.2, 8.2), (18.2, 10.0), (13.8, 16.0)])    # muslo
    parte([(13.6, 18.9), (13.6, 16.8), (18.4, 16.8), (18.4, 18.9)])                              # pie
    L.poli(P([(16.1, 13.0), (17.8, 12.8), (17.7, 13.5), (16.0, 13.7)]), B)                       # ajorca
    parte([(7.8, 11.0), (13.8, 11.0), (13.0, 12.6), (8.6, 12.6)])                                # recipiente
    L.poli(P([(8.8, 11.5), (12.9, 11.5), (12.6, 12.0), (9.2, 12.0)]), B)
    parte([(5.6, 8.4), (7.8, 8.4), (7.8, 10.0), (5.6, 10.0)])                                    # cuello
    parte([(3.6, 3.0), (9.6, 3.0), (9.6, 8.8), (3.6, 8.8)])                                      # cara
    parte([(2.6, 1.4), (10.6, 1.4), (10.6, 3.2), (2.6, 3.2)])                                    # tocado
    for x in (4.0, 5.6, 7.2, 8.8):
        L.poli(P([(x - .4, 2.0), (x + .4, 2.0), (x + .4, 2.6), (x - .4, 2.6)]), B)
    for x in (2.5, 10.7):
        L.d.ellipse([(x0 + (x - .85) * u) * K, (y0 + 4.5 * u) * K, (x0 + (x + .85) * u) * K, (y0 + 6.2 * u) * K], fill=N, outline=B, width=sep)
        L.d.ellipse([(x0 + (x - .3) * u) * K, (y0 + 5.05 * u) * K, (x0 + (x + .3) * u) * K, (y0 + 5.65 * u) * K], fill=B)
    for x in (5.2, 8.0):
        L.poli(P([(x - .7, 4.9), (x + .7, 4.9), (x + .7, 5.5), (x - .7, 5.5)]), B)
    L.poli(P([(6.3, 5.4), (6.9, 5.4), (6.9, 6.9), (6.3, 6.9)]), B)
    L.poli(P([(5.3, 7.4), (7.9, 7.4), (7.9, 7.9), (5.3, 7.9)]), B)

FICHAS = {
    "piedra_sol":    (piedra_sol, "Piedra del Sol", "MEXICA", 11),
    "cabeza_olmeca": (olmeca, "Cabeza Colosal", "OLMECA", 6),
    "pakal":         (pakal, "Máscara de Pakal", "MAYA", 23),
    "chac_mool":     (chac_mool, "Chac Mool", "MAYA · CHICHÉN ITZÁ", 41),
}

def target_pieza(pid):
    f, titulo, cultura, seed = FICHAS[pid]
    L = Lienzo()
    u = 34; tam = 24 * u
    f(L, (W - tam) / 2, 70, u)
    greca(L, 90, W - 90, 815, 70, seed)
    L.texto((W / 2, 975), titulo, BASK, 118 if len(titulo) < 15 else 100)
    L.texto((W / 2, 1085), cultura, PAG, 46 if len(cultura) < 10 else 38, espaciado=22 if len(cultura) < 10 else 12)
    L.texto((W / 2, 1160), "Sala Viva AR · Museo Nacional de Antropología", PAG_I, 30)
    return L.final()

def target_coleccion():
    """Target horizontal con las cuatro piezas: sobre él aparecen los cuatro modelos a la vez."""
    global W, H
    W0, H0 = W, H; W, H = 1600, 1200
    L = Lienzo()
    L.d.rectangle([40 * K, 40 * K, (W - 40) * K, (H - 40) * K], outline=N, width=6 * K)
    L.d.rectangle([58 * K, 58 * K, (W - 58) * K, (H - 58) * K], outline=N, width=2 * K)
    L.texto((W / 2, 150), "Colección Sala Viva AR", BASK, 96)
    L.texto((W / 2, 238), "MUSEO NACIONAL DE ANTROPOLOGÍA", PAG, 34, espaciado=10)
    greca(L, 120, W - 120, 285, 46, 77)
    orden = [("piedra_sol", "I"), ("cabeza_olmeca", "II"), ("pakal", "III"), ("chac_mool", "IV")]
    u = 13.5; tam = 24 * u
    for i, (pid, num) in enumerate(orden):
        cx = 120 + (W - 240) * (i + .5) / 4
        f = FICHAS[pid][0]; f(L, cx - tam / 2, 430, u)
        L.texto((cx, 790), num, PAG, 40)
        L.texto((cx, 850), FICHAS[pid][1], BASK, 40)
        L.texto((cx, 895), FICHAS[pid][2].split(" ·")[0], PAG, 24, espaciado=6)
    greca(L, 120, W - 120, 960, 46, 99)
    L.texto((W / 2, 1090), "Escanea esta tarjeta para ver las cuatro piezas juntas", PAG_I, 34)
    im = L.final(); W, H = W0, H0
    return im

def textil(L, x0, y0, x1, y1, celda, rng, evitar=None):
    """Fondo geométrico tipo textil: celdas con motivos escalonados que giran y cambian (no se repite)."""
    from PIL import ImageChops
    capa = Image.new("L", (W * K, H * K), 0); d = ImageDraw.Draw(capa)
    g = celda * 0.13 * K
    for j, y in enumerate(np.arange(y0, y1 - celda + 1, celda)):
        for i, x in enumerate(np.arange(x0, x1 - celda + 1, celda)):
            t = rng.integers(0, 6); c = celda * K; X, Y = x * K, y * K
            tmp = Image.new("L", (int(c), int(c)), 0); dt = ImageDraw.Draw(tmp)
            if t == 0: dt.line([(c*.15, c*.85), (c*.15, c*.45), (c*.55, c*.45), (c*.55, c*.15), (c*.85, c*.15)], fill=255, width=int(g))
            elif t == 1: dt.polygon([(c*.15, c*.85), (c*.5, c*.2), (c*.85, c*.85)], fill=255)
            elif t == 2: dt.line([(c*.2, c*.8), (c*.2, c*.2), (c*.8, c*.2), (c*.8, c*.65), (c*.45, c*.65), (c*.45, c*.45)], fill=255, width=int(g))
            elif t == 3: dt.ellipse([c*.3, c*.3, c*.7, c*.7], fill=255); dt.ellipse([c*.43, c*.43, c*.57, c*.57], fill=0)
            elif t == 4: dt.rectangle([c*.2, c*.2, c*.5, c*.5], fill=255); dt.rectangle([c*.55, c*.55, c*.8, c*.8], fill=255)
            else: dt.line([(c*.1, c*.7), (c*.35, c*.3), (c*.6, c*.7), (c*.9, c*.3)], fill=255, width=int(g))
            tmp = tmp.rotate(90 * int(rng.integers(0, 4)))
            capa.paste(255, (int(X), int(Y)), tmp)
    if evitar is not None: capa = ImageChops.subtract(capa, evitar)
    L.im.paste(N, (0, 0), capa)

def target_olmeca_textil(seed=6):
    from PIL import ImageFilter, ImageChops
    rng = np.random.default_rng(seed)
    L = Lienzo()
    u = 30; tam = 24 * u; ox, oy = (W - tam) / 2, 105
    # silueta del ícono (para dejarle un halo blanco sobre el textil)
    S = Lienzo(); olmeca(S, ox, oy, u)
    a = (255 - np.asarray(S.im.resize((W, H)))) > 60
    a = cv2.dilate(a.astype(np.uint8) * 255, np.ones((31, 31), np.uint8))
    relleno = a.copy(); msk = np.zeros((H + 2, W + 2), np.uint8)
    cv2.floodFill(relleno, msk, (0, 0), 255); a = a | (255 - relleno)      # rellena el interior de la cara
    sil = Image.fromarray(a).resize((W * K, H * K))
    m = 60
    L.d.rectangle([m * K, m * K, (W - m) * K, 820 * K], outline=N, width=6 * K)
    textil(L, m + 16, m + 16, W - m - 16, 820 - 16, 44, rng, evitar=sil)
    olmeca(L, ox, oy, u)
    L.texto((W / 2, 930), "Cabeza Colosal", BASK, 112)
    L.texto((W / 2, 1050), "OLMECA", PAG, 44, espaciado=22)
    L.texto((W / 2, 1130), "Sala Viva AR · Museo Nacional de Antropología", PAG_I, 30)
    return L.final()

if __name__ == "__main__":
    for pid, nombre in (("piedra_sol", "PiedraDelSol"), ("cabeza_olmeca", "CabezaOlmeca"), ("pakal", "MascaraPakal"), ("chac_mool", "ChacMool")):
        im = target_pieza(pid); im.save(os.path.join(OUT, f"Target_{nombre}.png"))
        im.convert("RGB").save(os.path.join(OUT, f"Target_{nombre}_Vuforia.jpg"), quality=92)
        print(nombre, evaluar(np.asarray(im)))
    im = target_coleccion(); im.save(os.path.join(OUT, "Target_Coleccion.png"))
    im.convert("RGB").save(os.path.join(OUT, "Target_Coleccion_Vuforia.jpg"), quality=92)
    print("Coleccion", evaluar(np.asarray(im)))
    raise SystemExit
    im = target_olmeca(); im.save(os.path.join(OUT, "Target_Olmeca_geo.png"))
    print("Olmeca geo", evaluar(np.asarray(im)))
    im = target_olmeca_textil(); im.save(os.path.join(OUT, "Target_Olmeca_geo_textil.png"))
    print("Olmeca geo textil", evaluar(np.asarray(im)))
